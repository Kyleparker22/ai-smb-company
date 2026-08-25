#!/usr/bin/env python3
"""Append-only event ledger — the shared write substrate for yourco's evidence stores.

Same discipline as `crm/_attribution-log.jsonl` and `loops/_build-journal/sessions.jsonl`,
extracted once so the four newer stores can't each invent their own half-correct version:

    loops/_trust/actions.jsonl      agent actions, by autonomy rung   (trust ledger)
    loops/_trust/forecasts.jsonl    calibration bets + resolutions    (calibration market)
    loops/_trust/drills.jsonl       immune drills + detection         (immune system)
    loops/_twin/predictions.jsonl   the DRI twin's calls + outcomes   (twin scoreboard)

THE FOUR PROPERTIES (this file exists to make them impossible to violate):

1. **Append-only.** Nothing is ever edited or deleted. `append()` is the only writer.
2. **Monotonic seq.** Every event carries an integer `seq`, one greater than the highest
   already on disk. Gaps and reordering are therefore detectable.
3. **Corrections are new events.** Got it wrong? Append an event with `corrects: <seq>`.
   The original stays on disk forever — that property IS the audit trail. `project()`
   applies corrections for reading; the file itself never loses the mistake.
4. **Corruption is reported, not swallowed.** A malformed line is counted and surfaced
   in `read().bad`, never silently skipped. A store that quietly drops rows is worse
   than one that admits it lost them.

Concurrency: the runtime is multi-process (systemd timers + Cowork sessions + the
listener all share one clone), so every append takes an exclusive `flock` on the
ledger file and re-reads the tail for the next seq INSIDE the lock. Two loops writing
the same ledger in the same second cannot collide or duplicate a seq.

Read-side helpers never lock — an append is a single atomic O_APPEND line write, so a
concurrent reader sees either the whole line or none of it.
"""
import os, json, fcntl, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAX_FIELD = 4000       # per-string-field cap: a runaway prompt can't bloat the ledger
MAX_EVENT_BYTES = 64000  # one line ceiling; refused rather than truncated (silent truncation lies)


def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def _clip(v, depth=0):
    """Recursively bound what can enter the ledger. Strings clipped, containers capped,
    unknown types stringified — a ledger row must always be JSON-round-trippable."""
    if depth > 6:
        return "…"
    if isinstance(v, str):
        return v[:MAX_FIELD]
    if isinstance(v, bool) or v is None or isinstance(v, (int, float)):
        return v
    if isinstance(v, dict):
        return {str(k)[:200]: _clip(x, depth + 1) for k, x in list(v.items())[:60]}
    if isinstance(v, (list, tuple)):
        return [_clip(x, depth + 1) for x in list(v)[:200]]
    return str(v)[:MAX_FIELD]


class Ledger:
    """One append-only JSONL file. Construct with a repo-relative path."""

    def __init__(self, rel_path):
        self.rel = rel_path
        self.path = os.path.join(ROOT, rel_path)

    # ---- write -------------------------------------------------------------
    def append(self, kind, **fields):
        """Append one event. Returns the event as written (incl. its assigned seq).

        `corrects=<seq>` marks this event as superseding an earlier one — the only
        way to change recorded history. Raises ValueError on an oversized event
        rather than writing a truncated (and therefore false) row."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        # Open r+ so the same descriptor can read the tail and append under one lock.
        # a+ would leave the read offset at EOF on some platforms; r+ is explicit.
        if not os.path.exists(self.path):
            open(self.path, "a").close()
        with open(self.path, "r+", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                seq = 0
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        s = json.loads(line).get("seq")
                    except ValueError:
                        continue  # a corrupt line must not stop seq allocation
                    if isinstance(s, int) and s > seq:
                        seq = s
                ev = {"seq": seq + 1, "ts": _now(), "kind": str(kind)[:80]}
                for k, v in fields.items():
                    if k in ("seq", "ts", "kind"):
                        continue  # reserved — a caller can't forge these
                    ev[str(k)[:80]] = _clip(v)
                blob = json.dumps(ev, ensure_ascii=False)
                if len(blob.encode()) > MAX_EVENT_BYTES:
                    raise ValueError(f"event too large ({len(blob)}B) — refusing to write a truncated row")
                f.seek(0, os.SEEK_END)
                if f.tell():  # a prior crash could have left a newline-less tail
                    f.seek(f.tell() - 1)
                    if f.read(1) != "\n":
                        f.write("\n")
                f.write(blob + "\n")
                f.flush()
                os.fsync(f.fileno())
                return ev
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # ---- read --------------------------------------------------------------
    def read(self):
        """-> {"events": [...], "bad": <int>, "exists": bool}.

        `bad` is the count of unparseable lines. Callers should surface it: a store
        that silently drops rows would let evidence disappear without anyone noticing."""
        if not os.path.exists(self.path):
            return {"events": [], "bad": 0, "exists": False}
        events, bad = [], 0
        try:
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        bad += 1
                        continue
                    if isinstance(ev, dict) and isinstance(ev.get("seq"), int):
                        events.append(ev)
                    else:
                        bad += 1
        except OSError:
            return {"events": [], "bad": 0, "exists": False}
        events.sort(key=lambda e: e["seq"])
        return {"events": events, "bad": bad, "exists": True}

    def project(self):
        """Read with corrections applied: an event carrying `corrects: N` replaces
        event N (and inherits its seq for ordering). The superseded event stays on
        disk — this is a read-time view, never a rewrite.

        -> {"events": [...], "bad": int, "exists": bool, "corrected": int}"""
        raw = self.read()
        by_seq = {e["seq"]: e for e in raw["events"]}
        corrected = 0
        for e in raw["events"]:
            tgt = e.get("corrects")
            if isinstance(tgt, int) and tgt in by_seq and tgt != e["seq"]:
                merged = dict(by_seq[tgt])
                merged.update({k: v for k, v in e.items() if k not in ("seq",)})
                merged["_correctedBy"] = e["seq"]
                by_seq[tgt] = merged
                by_seq.pop(e["seq"], None)  # the correction is folded in, not listed twice
                corrected += 1
        out = sorted(by_seq.values(), key=lambda e: e["seq"])
        return {"events": out, "bad": raw["bad"], "exists": raw["exists"], "corrected": corrected}


# ---- shared scoring: calibration ------------------------------------------
# Used by BOTH the calibration market (trust) and the twin scoreboard, so the two
# can never drift into different definitions of "how well-calibrated is this?".

MIN_FORECASTS = 5  # below this, no score is reported — see refuse_reason()


def brier(pairs):
    """Brier score over [(p, outcome_bool), ...]. 0 = perfect, 0.25 = a coin flip
    stated at 50%, 1 = confidently wrong every time. Lower is better.
    Returns None on an empty set — never 0, which would read as perfection."""
    pairs = [(float(p), 1.0 if o else 0.0) for p, o in pairs
             if isinstance(p, (int, float)) and not isinstance(p, bool) and 0.0 <= p <= 1.0]
    if not pairs:
        return None
    return round(sum((p - o) ** 2 for p, o in pairs) / len(pairs), 4)


def calibration_bins(pairs, edges=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0001)):
    """Reliability table: for each confidence band, what actually happened.
    This is the honest picture a single Brier number hides — "80% confident" should
    come true about 80% of the time, and the bin shows whether it does."""
    out = []
    for i in range(len(edges) - 1) if pairs else []:
        lo, hi = edges[i], edges[i + 1]
        sel = [(p, o) for p, o in pairs if lo <= p < hi]
        if not sel:
            continue
        out.append({
            "band": f"{int(lo * 100)}–{int(min(hi, 1.0) * 100)}%",
            "n": len(sel),
            "claimed": round(sum(p for p, _ in sel) / len(sel), 3),
            "actual": round(sum(1 for _, o in sel if o) / len(sel), 3),
        })
    return out


def refuse_reason(n, minimum=MIN_FORECASTS):
    """The house honesty rule, shared: below the sample floor we state the sample,
    we do not state a rate. (Same stance as build_journal's --estimate refusal.)"""
    if n >= minimum:
        return None
    return (f"Not scoring from {n} resolved item{'' if n == 1 else 's'} "
            f"— {minimum} is the floor. Here is the raw record instead.")


if __name__ == "__main__":  # smoke test: python3 runtime/ledger.py
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    try:
        l = Ledger(os.path.relpath(os.path.join(tmp, "t.jsonl"), ROOT))
        a = l.append("test", who="atlas", n=1)
        b = l.append("test", who="david", n=2)
        assert (a["seq"], b["seq"]) == (1, 2), "seq must be monotonic"
        l.append("test", corrects=1, who="atlas", n=99)
        proj = l.project()
        assert len(proj["events"]) == 2, "correction folds in, does not duplicate"
        assert proj["events"][0]["n"] == 99, "correction wins at read time"
        assert len(l.read()["events"]) == 3, "the original stays on disk forever"
        with open(l.path, "a") as f:
            f.write("{not json\n")
        assert l.read()["bad"] == 1, "corruption is counted, not swallowed"
        assert brier([(1.0, True), (1.0, True)]) == 0.0
        assert brier([(0.5, True), (0.5, False)]) == 0.25
        assert brier([]) is None, "empty must be None, never 0"
        assert refuse_reason(2) and not refuse_reason(9)
        print("ledger.py — all assertions pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
