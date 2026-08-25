#!/usr/bin/env python3
"""The run journal — loop runs that survive their own death, and cost that stops being invisible.

TWO PROBLEMS, ONE STORE.

1. **A dying run loses everything.** `runtime/run-loop.sh` fires `claude -p`, gives it ~15 minutes, and
   either an artifact lands or it does not. `_loop-contract.md` has good *stop* rules (no third
   identical attempt, no flip-flop, land a partial) and no *resume* story — so a run that stops
   correctly at minute 14 starts from zero next firing. LangGraph's answer is checkpointing at
   every super-step; this is the cheap version of the same idea, and reliability is the thing
   yourco sells.

2. **Per-loop cost is thrown away every single run.** `runtime/run-loop.sh` already calls
   `claude -p --output-format json`, whose result carries `total_cost_usd` and `usage` — and
   appends it to `loops/_runtime/<loop>.log`, which is **gitignored and host-local**. The most
   granular cost data in the business is generated ~20 times a day and discarded. `--record`
   catches it on the way past. (`loops/_anthropic/latest.json` only has DAILY TOTALS, so without
   this there is no per-agent cost and none can be honestly invented from a daily number.)

THE TRACE DEFINITION — the observability half, without the platform. Checkpoint kinds are fixed
to the five things the agent-observability literature says a trace must capture, plus a free note:

    tool          a tool was selected, with its arguments
    memory-read   a learning / skill / artifact was read into context
    memory-write  a learning / skill / artifact was written
    state         a state transition inside the run
    decision      a branch was taken, and why
    note          anything else

Fixed on purpose: a free-form checkpoint vocabulary is a trace nobody can query.

FIVE HONESTY RULES (tests in runtime/test_agentops.py):

1. **Missing cost is null and counted as unpriced — never 0.** A zero would read as free, and a
   free loop is the one number nobody would question. Same stance as the trust ledger's
   estimated/unpriced split.
2. **A run with checkpoints and no terminal row is `abandoned` past the window, not "running".**
   Silence has to mean something (the drills rule, applied to runs).
3. **Resume is a HAND-OFF, never a rewind.** An LLM run cannot be forked mid-flight; what this
   returns is the prior run's checkpoints so the next firing does not redo finished work. It is
   labelled that way everywhere, because calling it "resume" would over-claim.
4. **Nothing is deleted.** Append-only via `runtime/ledger.py`; corrections are new events.
5. **Unparseable model output is recorded as unparseable.** A run that produced JSON we could not
   read is a recorded fact, not an absent row.

CLI
  claude -p ... --output-format json | python3 runtime/run_journal.py --record --loop content
  python3 runtime/run_journal.py --checkpoint content --kind state --step "drafts written" --state '{"n":3}'
  python3 runtime/run_journal.py --resume content      # what the last run left behind
  python3 runtime/run_journal.py --status [--days 30]
"""
import os, re, sys, json, argparse, datetime

CODE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(CODE)
sys.path.insert(0, CODE)
from ledger import Ledger  # noqa: E402

STORE = "loops/_agentops/runs.jsonl"
PROMPTS = os.path.join(os.path.dirname(CODE), "runtime", "prompts")

KINDS = ("tool", "memory-read", "memory-write", "state", "decision", "note")
ABANDON_HOURS = 6      # past this with no terminal row, an open run is abandoned, not running


def _ledger():
    return Ledger(STORE)


def agent_for(loop):
    """Loop -> agent, parsed from the prompt's own first line ('You are Kolby, ...').
    Deterministic and single-sourced: no second mapping table to drift against the prompts."""
    p = os.path.join(PROMPTS, f"{loop}.md")
    try:
        first = open(p, encoding="utf-8").readline()
    except OSError:
        return None
    m = re.match(r"\s*You are ([A-Z][a-zA-Z]+)", first)
    return m.group(1).lower() if m else None


def _num(d, *path):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur if isinstance(cur, (int, float)) and not isinstance(cur, bool) else None


def record(loop, blob, run_id=None):
    """Ingest a `claude -p --output-format json` result. Absent fields stay None and are
    reported as unpriced/unknown — never defaulted to a number that would read as measured."""
    parsed, parse_error = None, None
    if isinstance(blob, dict):
        parsed = blob
    else:
        text = (blob or "").strip()
        try:
            parsed = json.loads(text)
        except ValueError:
            # runtime/run-loop.sh appends JSON to a log, so the tail may carry extra lines.
            m = re.search(r"\{.*\}", text, re.S)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except ValueError as e:
                    parse_error = f"{type(e).__name__}: {e}"
            else:
                parse_error = "no JSON object found in input"
    if parsed is None:
        return _ledger().append("run", loop=loop, agent=agent_for(loop), status="unparseable",
                                parse_error=parse_error, cost_usd=None,
                                note="model output could not be parsed — recorded as a run that "
                                     "happened with unknown cost, not as an absent run")
    usage = parsed.get("usage") if isinstance(parsed.get("usage"), dict) else {}
    is_err = bool(parsed.get("is_error")) or parsed.get("subtype") not in (None, "success")
    return _ledger().append(
        "run", loop=loop, agent=agent_for(loop),
        status="error" if is_err else "ok",
        run_id=run_id or parsed.get("session_id"),
        cost_usd=_num(parsed, "total_cost_usd"),
        duration_ms=_num(parsed, "duration_ms"),
        num_turns=_num(parsed, "num_turns"),
        tokens_in=_num(usage, "input_tokens"),
        tokens_out=_num(usage, "output_tokens"),
        cache_read=_num(usage, "cache_read_input_tokens"),
        cache_write=_num(usage, "cache_creation_input_tokens"),
        subtype=parsed.get("subtype"),
    )


def checkpoint(loop, kind, step, state=None, run_id=None):
    if kind not in KINDS:
        raise ValueError(f"unknown checkpoint kind '{kind}' — one of {', '.join(KINDS)}")
    return _ledger().append("checkpoint", loop=loop, agent=agent_for(loop), ckind=kind,
                            step=step, state=state, run_id=run_id)


def _by_run(events):
    """Group checkpoints under the terminal run row that closed them. A checkpoint stream with
    no terminal row is an OPEN run — the case rule 2 exists for."""
    open_ck, closed, seen_open = {}, [], []
    for e in events:
        loop = e.get("loop")
        if e.get("kind") == "checkpoint":
            open_ck.setdefault(loop, []).append(e)
        elif e.get("kind") == "run":
            closed.append({**e, "checkpoints": open_ck.pop(loop, [])})
    for loop, cks in open_ck.items():
        seen_open.append({"loop": loop, "agent": cks[0].get("agent"), "checkpoints": cks,
                          "last_ts": cks[-1].get("ts")})
    return closed, seen_open


def _age_hours(ts, now):
    try:
        return (now - datetime.datetime.fromisoformat(ts)).total_seconds() / 3600.0
    except (TypeError, ValueError):
        return None


def status(days=30, now=None):
    now = now or datetime.datetime.now()
    raw = _ledger().project()
    cutoff = now - datetime.timedelta(days=days)
    events = [e for e in raw["events"]
              if (_age_hours(e.get("ts"), now) or 0) <= days * 24]
    closed, still_open = _by_run(events)
    for o in still_open:
        age = _age_hours(o["last_ts"], now)
        o["age_hours"] = round(age, 1) if age is not None else None
        o["state"] = "abandoned" if (age is not None and age > ABANDON_HOURS) else "in-flight"

    priced = [r for r in closed if isinstance(r.get("cost_usd"), (int, float))]
    unpriced = [r for r in closed if not isinstance(r.get("cost_usd"), (int, float))]
    by_loop = {}
    for r in closed:
        b = by_loop.setdefault(r.get("loop") or "(unknown)",
                               {"loop": r.get("loop"), "agent": r.get("agent"), "runs": 0,
                                "errors": 0, "cost_usd": 0.0, "priced_runs": 0, "unpriced_runs": 0})
        b["runs"] += 1
        b["errors"] += 1 if r.get("status") != "ok" else 0
        if isinstance(r.get("cost_usd"), (int, float)):
            b["cost_usd"] += r["cost_usd"]; b["priced_runs"] += 1
        else:
            b["unpriced_runs"] += 1
    for b in by_loop.values():
        b["cost_usd"] = round(b["cost_usd"], 4)
    return {
        "window_days": days, "since": cutoff.date().isoformat(),
        "runs": len(closed), "errors": sum(1 for r in closed if r.get("status") != "ok"),
        "unparseable": sum(1 for r in closed if r.get("status") == "unparseable"),
        "priced_runs": len(priced), "unpriced_runs": len(unpriced),
        "cost_usd": round(sum(r["cost_usd"] for r in priced), 4) if priced else None,
        "by_loop": sorted(by_loop.values(), key=lambda b: -b["cost_usd"]),
        "open_runs": still_open,
        "bad_lines": raw["bad"], "store_exists": raw["exists"],
        "cost_caveat": (f"{len(unpriced)} of {len(closed)} runs carry no cost field and are "
                        f"EXCLUDED from the total rather than counted as $0."
                        if unpriced else None),
    }


def resume(loop, now=None):
    """What the last run left behind. A HAND-OFF, not a rewind — see honesty rule 3."""
    now = now or datetime.datetime.now()
    _closed, still_open = _by_run(_ledger().project()["events"])
    mine = [o for o in still_open if o["loop"] == loop]
    if not mine:
        return {"loop": loop, "resumable": False,
                "note": "No unfinished run for this loop. Start from the SOP's step 1."}
    o = mine[-1]
    age = _age_hours(o["last_ts"], now)
    return {
        "loop": loop, "resumable": True, "age_hours": round(age, 1) if age is not None else None,
        "abandoned": bool(age is not None and age > ABANDON_HOURS),
        "checkpoints": [{"kind": c.get("ckind"), "step": c.get("step"), "state": c.get("state"),
                         "ts": c.get("ts")} for c in o["checkpoints"]],
        "note": ("This is a HAND-OFF, not a rewind: the previous run's context is gone and cannot "
                 "be restored. These are the steps it recorded as finished — do not redo them, "
                 "and verify each one's artifact still exists before trusting it."),
    }


def main():
    ap = argparse.ArgumentParser(description="Run journal — durability + per-loop cost.")
    ap.add_argument("--record", action="store_true", help="ingest claude -p JSON from stdin/--file")
    ap.add_argument("--file", help="read the JSON blob from a file instead of stdin")
    ap.add_argument("--loop")
    ap.add_argument("--run-id")
    ap.add_argument("--checkpoint", metavar="LOOP")
    ap.add_argument("--kind", default="note", choices=KINDS)
    ap.add_argument("--step", default="")
    ap.add_argument("--state", help="JSON string of state to carry forward")
    ap.add_argument("--resume", metavar="LOOP")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.record:
        if not a.loop:
            ap.error("--record needs --loop")
        blob = open(a.file, encoding="utf-8", errors="replace").read() if a.file else sys.stdin.read()
        ev = record(a.loop, blob, run_id=a.run_id)
        print(json.dumps(ev) if a.json else
              f"recorded run {a.loop} seq={ev['seq']} status={ev.get('status')} "
              f"cost={'$%.4f' % ev['cost_usd'] if isinstance(ev.get('cost_usd'), (int, float)) else 'UNPRICED'}")
        return

    if a.checkpoint:
        st = json.loads(a.state) if a.state else None
        ev = checkpoint(a.checkpoint, a.kind, a.step, st, run_id=a.run_id)
        print(f"checkpoint seq={ev['seq']} {a.checkpoint} [{a.kind}] {a.step}")
        return

    if a.resume:
        r = resume(a.resume)
        print(json.dumps(r, indent=2) if a.json else
              (f"{a.resume}: nothing to hand off" if not r["resumable"] else
               f"{a.resume}: {len(r['checkpoints'])} checkpoint(s) from "
               f"{r['age_hours']}h ago{' [ABANDONED]' if r['abandoned'] else ''}\n  "
               + "\n  ".join(f"[{c['kind']}] {c['step']}" for c in r["checkpoints"])
               + f"\n\n  {r['note']}"))
        return

    s = status(a.days)
    if a.json:
        print(json.dumps(s, indent=2)); return
    if not s["store_exists"]:
        print("  Run journal is empty — no run has been recorded yet.\n"
              "  Wire it in runtime/run-loop.sh (see runtime/README.md) and it fills from the next firing.\n"
              "  Nothing can be backfilled: the historical JSON went to gitignored host-local logs.")
        return
    print(f"Run journal — last {s['window_days']}d: {s['runs']} runs, {s['errors']} errors")
    print(f"  cost: {('$%.2f' % s['cost_usd']) if s['cost_usd'] is not None else 'no priced runs'}")
    if s["cost_caveat"]:
        print(f"  ⚠ {s['cost_caveat']}")
    for b in s["by_loop"][:20]:
        # A loop with no priced run renders as "—", never $0.0000. Honesty rule 1 has to hold in
        # the renderer too: a fabricated zero in the cost column is the one number nobody queries.
        cost = f"${b['cost_usd']:>7.4f}" if b["priced_runs"] else f"{'—':>8}"
        print(f"   {b['loop']:<24} {b['agent'] or '—':<10} {b['runs']:>3} runs  " + cost
              + (f"  ({b['unpriced_runs']} unpriced)" if b["unpriced_runs"] else ""))
    for o in s["open_runs"]:
        print(f"  {o['state'].upper():<10} {o['loop']} — {len(o['checkpoints'])} checkpoints, "
              f"{o['age_hours']}h old")
    if s["bad_lines"]:
        print(f"  ⚠ {s['bad_lines']} unparseable line(s) in the store — counted, not skipped")


if __name__ == "__main__":
    main()
