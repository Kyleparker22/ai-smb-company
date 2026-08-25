#!/usr/bin/env python3
"""yourco — the build journal: how long a build actually took, and what it actually consisted of.

the Founder's ask: *"an agent or tool that documents and logs the time and hours and process for when I am
building for a new prospect/client, so when we have future builds we know exactly how long it will
take and the costs/tokens associated with it."*

The cost ledger (`clients/<client>/cost.md`, written via the `log-build-cost` skill) already captures
**dollars, roughly, after the fact**. Three things were missing, and they are what this file adds:

  (a) **time** — wall duration of a build session, measured not guessed;
  (b) **process** — the ordered steps a build was actually made of, so the journal reads as a
      playbook for the next one, not just a number;
  (c) **queryable history** — `--estimate` answers "how long does a build like this take?" from
      what really happened, and *refuses to answer* when the sample is too thin.

Storage is `loops/_build-journal/sessions.jsonl` — append-only, monotonic `seq`, never edited, the
same discipline as `crm/_attribution-log.jsonl` (`crm/connector_ladder.py`). A mistake is corrected
by appending a `session.correction` event citing the session; the wrong line stays. That property is
the audit trail.

Relationship to `log-build-cost`: this tool does NOT replace it. build_journal captures
time + process + steps; log-build-cost captures the dollars into the client ledger. `--stop` bridges
them by emitting the exact markdown ledger row to append (`--append-ledger` writes it for you).

HONESTY RULES BAKED IN (the whole point — a confident wrong number is worse than no number):
  * A Cowork/Claude Code session's tokens are NOT isolable from org-wide spend. Any `--cost` you
    pass is recorded as `est. — session self-report` and is only ever marked `metered` if you
    explicitly pass `--metered` (i.e. you have a console/invoice number for it).
  * The org's metered day spend from `loops/_anthropic/latest.json` is recorded as **context only**,
    labelled org-wide, never allocated to the session.
  * A session left open past the stale threshold will not silently record 14 hours — `--stop`
    refuses and asks for the real number.
  * `--estimate` below the sample floor says so plainly and shows the raw sessions instead.

Usage:
  python3 runtime/build_journal.py --start sample-client --phase discovery --what "Field-to-Quote v1"
  python3 runtime/build_journal.py --step "mapped Aspire export -> quote engine inputs"
  python3 runtime/build_journal.py --stop --tokens 1200000 --cost 22 --notes "verified end to end"
  python3 runtime/build_journal.py --stop --hours 3.5        # session left open overnight
  python3 runtime/build_journal.py --list-open
  python3 runtime/build_journal.py --report [--json]
  python3 runtime/build_journal.py --estimate "quote platform"
  python3 runtime/build_journal.py --backfill yourco --phase build --what "..." --date 2026-08-01 ...
  python3 runtime/build_journal.py --correct <session-id> --set notes="..." --why "typo in client"

Env seam: YOURCO_BUILD_JOURNAL=/path/to/sessions.jsonl (tests + dry runs; keeps the real journal clean).
"""
import os
import sys
import json
import uuid
import argparse
import datetime
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JOURNAL_DIR = os.path.join(ROOT, "loops", "_build-journal")
LOG = os.environ.get("YOURCO_BUILD_JOURNAL") or os.path.join(JOURNAL_DIR, "sessions.jsonl")
ANTHROPIC_DIR = os.path.join(ROOT, "loops", "_anthropic")
CLIENTS = os.path.join(ROOT, "clients")

PHASES = ("discovery", "build", "tools", "run")   # same four phases as the cost ledger — never fork these
STALE_HOURS = 8.0        # past this, an open session is presumed forgotten, not worked
MIN_SESSIONS = 3         # below this an estimate is not an estimate, it's a guess wearing a median


# ---- the append-only journal ---------------------------------------------------------
def read_events(path=None):
    """Every event, oldest first. A corrupt line is skipped, never fatal (the journal must always read)."""
    path = path or LOG
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def append_event(event, **fields):
    """Append one immutable event. Single write() to an O_APPEND handle — concurrent-writer safe.

    NEVER edits or removes a prior line. Corrections are new `session.correction` events.
    """
    evs = read_events()
    rec = {"seq": (evs[-1].get("seq", 0) + 1) if evs else 1,
           "id": uuid.uuid4().hex[:12],
           "ts": now_iso(),
           "event": event}
    rec.update(fields)
    d = os.path.dirname(LOG)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def parse_ts(s):
    try:
        return datetime.datetime.fromisoformat(str(s))
    except ValueError:
        return None


def hours_between(a, b):
    ta, tb = parse_ts(a), parse_ts(b)
    if not ta or not tb:
        return None
    return round((tb - ta).total_seconds() / 3600.0, 2)


def fmt_hours(h):
    if h is None:
        return "unknown"
    if h < 1:
        return f"{int(round(h * 60))}m"
    return f"{h:.2f}h"


# ---- folding events into sessions ----------------------------------------------------
def sessions():
    """Replay the log into session records. Pure read — the log is the truth, this is the view."""
    by_id, order = {}, []
    for e in read_events():
        ev = e.get("event")
        sid = e.get("session")
        if ev == "session.started" and sid:
            by_id[sid] = {"id": sid, "client": e.get("client"), "phase": e.get("phase"),
                          "kind": e.get("kind"), "what": e.get("what"), "started": e.get("ts"),
                          "steps": [], "state": "open", "stopped": None, "hours": None,
                          "hours_precision": None, "tokens": None, "cost_usd": None,
                          "cost_evidence": None, "notes": None, "flags": [], "context": {},
                          "backfill": False, "corrections": []}
            order.append(sid)
        elif ev == "session.step" and sid in by_id:
            by_id[sid]["steps"].append({"ts": e.get("ts"), "step": e.get("step")})
        elif ev == "session.stopped" and sid in by_id:
            s = by_id[sid]
            s.update(state="closed", stopped=e.get("ts"), hours=e.get("hours"),
                     hours_precision=e.get("hours_precision"), tokens=e.get("tokens"),
                     cost_usd=e.get("cost_usd"), cost_evidence=e.get("cost_evidence"),
                     notes=e.get("notes"), context=e.get("context") or {},
                     flags=list(e.get("flags") or []))
        elif ev == "session.backfill" and sid:
            by_id[sid] = {"id": sid, "client": e.get("client"), "phase": e.get("phase"),
                          "kind": e.get("kind"), "what": e.get("what"),
                          "started": e.get("date"), "stopped": e.get("date"),
                          "steps": [{"ts": e.get("date"), "step": s} for s in (e.get("steps") or [])],
                          "state": "closed", "hours": e.get("hours"),
                          "hours_precision": e.get("hours_precision", "unknown"),
                          "tokens": e.get("tokens"), "cost_usd": e.get("cost_usd"),
                          "cost_evidence": e.get("cost_evidence"), "notes": e.get("notes"),
                          "flags": list(e.get("flags") or []), "context": e.get("context") or {},
                          "backfill": True, "corrections": []}
            order.append(sid)
        elif ev == "session.correction" and sid in by_id:
            s = by_id[sid]
            for k, v in (e.get("set") or {}).items():
                if k in s:
                    s[k] = v
            s["corrections"].append({"ts": e.get("ts"), "why": e.get("why"),
                                     "set": e.get("set") or {}})
    return [by_id[s] for s in order]


def open_sessions():
    return [s for s in sessions() if s["state"] == "open"]


def find_session(sid):
    for s in sessions():
        if s["id"] == sid or s["id"].startswith(sid):
            return s
    return None


def resolve_open(sid=None):
    """Which session does a bare --step/--stop apply to? Explicit beats implicit; never guess between two."""
    op = open_sessions()
    if sid:
        s = find_session(sid)
        if not s:
            return None, f"no session matching '{sid}'"
        if s["state"] != "open":
            return None, f"session {s['id']} is already closed ({s['stopped']})"
        return s, None
    if not op:
        return None, "no open session — start one with --start <client> --phase <phase> --what '...'"
    if len(op) > 1:
        listing = ", ".join(f"{s['id']}({s['client']})" for s in op)
        return None, f"{len(op)} sessions are open — name one with --session: {listing}"
    return op[0], None


# ---- cost context --------------------------------------------------------------------
def org_spend_context():
    """The org's metered model spend for today, from the HQ Anthropic pull. CONTEXT ONLY.

    This number is org-wide (every loop, every agent, every session on every machine). It is
    recorded next to the session so a future reader can sanity-check a self-report against the day's
    real bill — it is NOT an allocation, and this function never divides it by anything.
    """
    ctx = {"org_spend_source": None, "org_spend_note":
           "org-wide metered spend for the day; a single session cannot be isolated from it"}
    path = os.path.join(ANTHROPIC_DIR, "latest.json")
    if not os.path.exists(path):
        ctx["org_spend_source"] = "unavailable — loops/_anthropic/latest.json not found"
        return ctx
    try:
        with open(path, encoding="utf-8") as f:
            blob = json.load(f)
    except (ValueError, OSError) as e:
        ctx["org_spend_source"] = f"unreadable — {e}"
        return ctx
    if blob.get("error") or not blob.get("connected"):
        ctx["org_spend_source"] = "Anthropic Admin API not connected at last pull"
        return ctx
    today = datetime.date.today().isoformat()
    day = next((d for d in (blob.get("days") or []) if d.get("date") == today), None)
    ctx["org_spend_source"] = f"loops/_anthropic/latest.json (fetched {blob.get('fetched')})"
    ctx["org_spend_day"] = today
    # These come straight from the Admin cost_report, which the dashboard already converted from
    # CENTS to dollars (dashboard/server.py anthropic_cost(), the /100.0 with the verified comment).
    # Do not divide or multiply again here.
    ctx["org_spend_today_usd"] = (day or {}).get("usd")
    ctx["org_spend_7d_usd"] = blob.get("cost7d")
    days = [d.get("date") for d in (blob.get("days") or []) if d.get("date")]
    ctx["org_spend_last_day_in_pull"] = max(days) if days else None
    if day is None:
        ctx["org_spend_note"] += ("; today's bucket is NOT in the last pull (the Admin cost report "
                                  "lags ~a day) — today's org spend is unknown, not zero")
    return ctx


# ---- the ledger row ------------------------------------------------------------------
def _cell(s):
    """Markdown table cells can't contain a raw pipe."""
    return str(s or "").replace("|", "/").replace("\n", " ").strip()


def ledger_row(s):
    """The exact `clients/<client>/cost.md` Ledger row for this session.

    Format is dictated by the existing table (see clients/sample-client/cost.md):
    | Date | Phase | What | Tokens | $ | Evidence |
    """
    date = (s.get("stopped") or s.get("started") or now_iso())[:10]
    what = _cell(s.get("what") or "(unspecified)")
    steps = [st.get("step") for st in s.get("steps") or [] if st.get("step")]
    if steps:
        what += " — " + _cell("; ".join(steps))
    if s.get("notes"):
        what += " — " + _cell(s["notes"])
    dur = fmt_hours(s.get("hours"))
    prec = s.get("hours_precision")
    if prec == "wall":
        what += f" (build journal: {dur} measured, {len(steps)} steps)"
    elif prec == "stated":
        what += f" (build journal: ~{dur} stated, {len(steps)} steps)"
    else:
        what += f" (build journal: duration {dur}, {len(steps)} steps)"

    if s.get("tokens"):
        try:
            t = int(s["tokens"])
            tokens = f"~{t/1_000_000:.2f}M" if t >= 1_000_000 else f"~{t:,}"
        except (TypeError, ValueError):
            tokens = _cell(s["tokens"])
    else:
        tokens = "not isolable — see $"

    ev = s.get("cost_evidence") or "est."
    if s.get("cost_usd") is None:
        dollars = "unknown"
        ev = "est. — not self-reported at stop"
    else:
        dollars = (f"${s['cost_usd']:,.2f}" if ev == "metered" else f"~${s['cost_usd']:,.2f}")
    return f"| {date} | {s.get('phase')} | {what} | {tokens} | {dollars} | {_cell(ev)} |"


def append_ledger_row(client, row):
    """Insert the row as the last line of the Ledger table in clients/<client>/cost.md.

    Deliberately minimal: one line inserted, every other byte of the file untouched — no
    reformatting, no rewriting of history rows (the ledger is append-only too). If the table can't
    be located the row is NOT written; we print it and say so rather than corrupting the file.
    """
    path = os.path.join(CLIENTS, client, "cost.md")
    if not os.path.exists(path):
        return False, (f"{path} does not exist — create it from clients/_yourco-template/cost.md "
                       "first (see the log-build-cost skill), then paste the row above")
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    header = next((i for i, l in enumerate(lines)
                   if l.startswith("| Date ") and "Phase" in l and "Evidence" in l), None)
    if header is None:
        return False, "could not find the Ledger table header in cost.md — paste the row by hand"
    i = header + 2  # skip the |---| separator
    last = i
    while i < len(lines) and lines[i].startswith("|"):
        last = i
        i += 1
    lines.insert(last + 1, row)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return True, path


# ---- commands ------------------------------------------------------------------------
def cmd_start(a):
    if a.phase not in PHASES:
        print(f"phase must be one of {', '.join(PHASES)}")
        return 2
    already = [s for s in open_sessions() if s["client"] == a.start]
    if already:
        print(f"NOTE: {len(already)} session already open for {a.start} "
              f"({', '.join(s['id'] for s in already)}). Opening another — "
              f"--step/--stop will now require --session.")
    sid = uuid.uuid4().hex[:8]
    rec = append_event("session.started", session=sid, client=a.start, phase=a.phase,
                       kind=(a.kind or a.phase), what=a.what)
    print(f"started {sid} · {a.start} · {a.phase} · kind={a.kind or a.phase}")
    print(f"  what: {a.what or '(none given — pass --what next time; it is what --estimate matches on)'}")
    print(f"  at:   {rec['ts']}")
    print(f"  log:  {LOG}")
    print("  next: --step \"<what you just did>\" as you go, then --stop when done.")
    return 0


def cmd_step(a):
    s, err = resolve_open(a.session)
    if err:
        print(err)
        return 2
    prev = s["steps"][-1]["ts"] if s["steps"] else s["started"]
    append_event("session.step", session=s["id"], step=a.step)
    since = hours_between(prev, now_iso())
    print(f"step {len(s['steps']) + 1} logged on {s['id']} ({s['client']}) "
          f"· +{fmt_hours(since)} since the last mark")
    return 0


def cmd_stop(a):
    s, err = resolve_open(a.session)
    if err:
        print(err)
        return 2
    stopped = now_iso()
    wall = hours_between(s["started"], stopped)
    flags = []
    stale = wall is not None and wall > STALE_HOURS

    if stale and a.hours is None and not a.accept_stale:
        # The failure this guard exists to prevent: a forgotten session silently becoming
        # "14 hours of build work" and poisoning every future estimate.
        print(f"STALE SESSION — {s['id']} ({s['client']}) has been open {fmt_hours(wall)}, "
              f"past the {STALE_HOURS:g}h threshold.")
        print("  Wall-clock elapsed is almost certainly NOT time worked (forgotten/crashed session).")
        print("  Re-run with ONE of:")
        print(f"    --stop --session {s['id']} --hours <real hours worked>   (recorded as 'stated')")
        print(f"    --stop --session {s['id']} --accept-stale               (records elapsed, flagged unreliable)")
        return 3

    if a.hours is not None:
        hours, precision = round(float(a.hours), 2), "stated"
        if wall is not None:
            flags.append(f"wall-clock elapsed was {fmt_hours(wall)}; hours stated by operator")
    else:
        hours, precision = wall, "wall"
        if stale:
            precision = "wall-unreliable"
            flags.append(f"session left open {fmt_hours(wall)} (> {STALE_HOURS:g}h) — "
                         "elapsed recorded on operator's say-so, treat as an upper bound")

    if a.cost is not None and a.metered:
        evidence = "metered"
    elif a.cost is not None:
        evidence = "est. — session self-report"
    else:
        evidence = None

    ctx = org_spend_context()
    rec = append_event("session.stopped", session=s["id"], hours=hours,
                       hours_precision=precision, wall_hours=wall,
                       tokens=a.tokens, cost_usd=(round(float(a.cost), 2) if a.cost is not None else None),
                       cost_evidence=evidence, notes=a.notes, flags=flags, context=ctx)
    s = find_session(s["id"])

    print(f"stopped {s['id']} · {s['client']} · {s['phase']}")
    print(f"  duration: {fmt_hours(hours)}  [{precision}]")
    for f in flags:
        print(f"  FLAG: {f}")
    print(f"  steps:    {len(s['steps'])}")
    for i, st in enumerate(s["steps"], 1):
        prev = s["steps"][i - 2]["ts"] if i > 1 else s["started"]
        print(f"    {i}. (+{fmt_hours(hours_between(prev, st['ts']))}) {st['step']}")
    if a.cost is not None:
        print(f"  cost:     ${float(a.cost):,.2f}  [{evidence}]")
    else:
        print("  cost:     not self-reported — the ledger row will say so "
              "(pass --cost next time; the self-report IS the mechanism)")
    today_org = ctx.get("org_spend_today_usd")
    print("  org context (NOT an allocation): org-wide metered spend on "
          f"{ctx.get('org_spend_day')} = "
          f"{('$%.2f' % today_org) if today_org is not None else 'unknown — not in the last pull (lags ~1d)'}"
          f"; 7d ${ctx.get('org_spend_7d_usd')}")
    print(f"    source: {ctx.get('org_spend_source')}")
    print(f"  seq:      {rec['seq']}")

    row = ledger_row(s)
    print("\n  --- cost ledger row for clients/%s/cost.md (log-build-cost skill) ---" % s["client"])
    print("  " + row)
    if a.append_ledger:
        ok, info = append_ledger_row(s["client"], row)
        print(f"  {'APPENDED to ' + info if ok else 'NOT appended: ' + info}")
    else:
        print("  (not written — re-run with --append-ledger, or paste it into the Ledger table)")
    return 0


def cmd_backfill(a):
    """Record a build that happened before the journal existed. Precision is explicitly 'unknown'."""
    if a.phase not in PHASES:
        print(f"phase must be one of {', '.join(PHASES)}")
        return 2
    sid = uuid.uuid4().hex[:8]
    steps = [s.strip() for s in (a.steps or "").split("|") if s.strip()]
    evidence = None
    if a.cost is not None:
        evidence = "metered" if a.metered else "est. — backfilled self-report"
    rec = append_event("session.backfill", session=sid, client=a.backfill, phase=a.phase,
                       kind=(a.kind or a.phase), what=a.what, date=a.date, steps=steps,
                       hours=(round(float(a.hours), 2) if a.hours is not None else None),
                       hours_precision=("stated" if a.hours is not None else "unknown"),
                       tokens=a.tokens,
                       cost_usd=(round(float(a.cost), 2) if a.cost is not None else None),
                       cost_evidence=evidence, notes=a.notes,
                       flags=["BACKFILL — reconstructed after the fact from the cost ledger; "
                              "duration was never measured" if a.hours is None else
                              "BACKFILL — reconstructed after the fact; hours stated, not measured"])
    print(f"backfilled {sid} · {a.backfill} · {a.phase} · {a.date} · seq {rec['seq']}")
    print(f"  hours: {'unknown (excluded from every estimate)' if a.hours is None else fmt_hours(a.hours) + ' [stated]'}")
    print(f"  steps: {len(steps)}")
    return 0


def cmd_correct(a):
    s = find_session(a.correct)
    if not s:
        print(f"no session matching '{a.correct}'")
        return 2
    fields = {}
    for pair in a.set or []:
        if "=" not in pair:
            print(f"--set expects key=value, got '{pair}'")
            return 2
        k, v = pair.split("=", 1)
        if k not in s:
            print(f"unknown field '{k}' — one of: {', '.join(sorted(s))}")
            return 2
        try:
            fields[k] = json.loads(v)
        except ValueError:
            fields[k] = v
    if not fields:
        print("nothing to correct — pass --set key=value")
        return 2
    rec = append_event("session.correction", session=s["id"], set=fields, why=a.why)
    print(f"correction appended (seq {rec['seq']}) on {s['id']}: {fields}")
    print("  the original line is untouched — that is what makes this a log and not a database")
    return 0


def cmd_list_open(a):
    op = open_sessions()
    if not op:
        print("no open sessions.")
        return 0
    print(f"{len(op)} open session(s):")
    for s in op:
        el = hours_between(s["started"], now_iso())
        stale = el is not None and el > STALE_HOURS
        print(f"  {s['id']}  {s['client']:<16} {s['phase']:<10} open {fmt_hours(el)}"
              f"{'   <-- STALE (> %g h): --stop will ask for real hours' % STALE_HOURS if stale else ''}")
        print(f"           what: {s['what']}  · steps so far: {len(s['steps'])}")
    return 0


def _fmt_money(v):
    return "—" if v is None else f"${v:,.2f}"


def report_payload():
    ss = sessions()
    by_client, by_phase = {}, {}
    for s in ss:
        for bucket, key in ((by_client, s["client"]), (by_phase, s["phase"])):
            b = bucket.setdefault(key, {"sessions": 0, "hours": 0.0, "hours_known": 0,
                                        "cost": 0.0, "cost_known": 0, "steps": 0})
            b["sessions"] += 1
            b["steps"] += len(s["steps"])
            if s.get("hours") is not None:
                b["hours"] += s["hours"]
                b["hours_known"] += 1
            if s.get("cost_usd") is not None:
                b["cost"] += s["cost_usd"]
                b["cost_known"] += 1
    return {"journal": LOG, "sessions": ss, "open": len(open_sessions()),
            "by_client": by_client, "by_phase": by_phase,
            "generated": now_iso()}


def cmd_report(a):
    p = report_payload()
    if a.json:
        print(json.dumps(p, indent=1))
        return 0
    ss = p["sessions"]
    print(f"BUILD JOURNAL — {len(ss)} session(s) · {p['open']} open")
    print(f"  {LOG}")
    if not ss:
        print("\n  Empty. Nothing has been journaled yet — that is a true statement, not a bug.")
        return 0
    print("\nRECENT")
    for s in ss[-15:]:
        state = s["state"].upper()
        cost = _fmt_money(s.get("cost_usd"))
        marks = []
        if s.get("backfill"):
            marks.append("BACKFILL")
        if s.get("hours_precision") and s["hours_precision"] != "wall":
            marks.append(s["hours_precision"])
        if s.get("corrections"):
            marks.append(f"{len(s['corrections'])} correction(s)")
        print(f"  {(s.get('started') or '')[:10]}  {s['id']}  {str(s['client']):<16} "
              f"{str(s['phase']):<10} {fmt_hours(s.get('hours')):>8}  {cost:>9}  "
              f"{len(s['steps'])} step{'' if len(s['steps']) == 1 else 's'}"
              f"  [{state}{(' · ' + ' · '.join(marks)) if marks else ''}]")
        print(f"      {s.get('what')}")
        for f in s.get("flags") or []:
            print(f"      ! {f}")
    for title, bucket in (("BY CLIENT", p["by_client"]), ("BY PHASE", p["by_phase"])):
        print(f"\n{title}")
        print(f"  {'key':<20} {'sessions':>8} {'hours':>10} {'$':>10} {'steps':>7}")
        for k, b in sorted(bucket.items(), key=lambda kv: -kv[1]["sessions"]):
            hrs = ("none" if b["hours_known"] == 0 else
                   f"{b['hours']:.2f}" + ("" if b["hours_known"] == b["sessions"]
                                          else f" ({b['hours_known']}/{b['sessions']})"))
            dollars = ("none" if b["cost_known"] == 0 else
                       f"{b['cost']:,.2f}" + ("" if b["cost_known"] == b["sessions"]
                                              else f" ({b['cost_known']}/{b['sessions']})"))
            print(f"  {str(k):<20} {b['sessions']:>8} {hrs:>10} {dollars:>10} {b['steps']:>7}")
    print("\n  Totals in parentheses = how many of those sessions actually carry the number.")
    print("  Hours/$ are summed only over sessions that have them — never imputed.")
    return 0


# ---- the payoff: estimate ------------------------------------------------------------
def match_sessions(kind):
    """Which past sessions count as 'a build like this'? Returns (matches, basis) — basis is printed
    so the reader can judge the match, instead of trusting a black box."""
    k = (kind or "").strip().lower()
    ss = [s for s in sessions() if s["state"] == "closed"]
    exact = [s for s in ss if (s.get("kind") or "").lower() == k]
    if exact:
        return exact, f"kind == '{kind}'"
    if k in PHASES:
        ph = [s for s in ss if (s.get("phase") or "").lower() == k]
        if ph:
            return ph, f"phase == '{kind}'"
    text = [s for s in ss if k and (k in (s.get("what") or "").lower()
                                    or k in (s.get("kind") or "").lower()
                                    or k in (s.get("client") or "").lower())]
    if text:
        return text, f"text match on '{kind}' (kind/what/client) — loose, judge the sessions yourself"
    return [], f"nothing matched '{kind}'"


def estimate_payload(kind):
    matches, basis = match_sessions(kind)
    timed = [s for s in matches if s.get("hours") is not None
             and s.get("hours_precision") in ("wall", "stated")]
    costed = [s for s in matches if s.get("cost_usd") is not None]
    out = {"kind": kind, "basis": basis, "matched": len(matches), "timed": len(timed),
           "costed": len(costed), "min_sessions": MIN_SESSIONS, "estimable": False,
           "sessions": [{"id": s["id"], "date": (s.get("started") or "")[:10], "client": s["client"],
                         "phase": s["phase"], "what": s["what"], "hours": s.get("hours"),
                         "hours_precision": s.get("hours_precision"), "cost_usd": s.get("cost_usd"),
                         "cost_evidence": s.get("cost_evidence"), "notes": s.get("notes"),
                         "steps": [st["step"] for st in s["steps"]],
                         "flags": s.get("flags") or []} for s in matches]}
    if len(timed) >= MIN_SESSIONS:
        hrs = sorted(s["hours"] for s in timed)
        out["estimable"] = True
        out["hours"] = {"median": round(statistics.median(hrs), 2), "min": hrs[0], "max": hrs[-1],
                        "n": len(hrs)}
    if len(costed) >= MIN_SESSIONS:
        c = sorted(s["cost_usd"] for s in costed)
        out["cost"] = {"median": round(statistics.median(c), 2), "min": c[0], "max": c[-1],
                       "n": len(c),
                       "all_estimates": all((s.get("cost_evidence") or "").startswith("est")
                                            for s in costed)}
    steps = Counter()
    for s in matches:
        for st in s["steps"]:
            steps[(st["step"] or "").strip().lower()] += 1
    out["common_steps"] = steps.most_common(12)
    if timed:
        rep = sorted(timed, key=lambda s: s["hours"])[len(timed) // 2]
        out["representative"] = {"id": rep["id"], "hours": rep["hours"],
                                 "steps": [st["step"] for st in rep["steps"]]}
    return out


def cmd_estimate(a):
    p = estimate_payload(a.estimate)
    if a.json:
        print(json.dumps(p, indent=1))
        return 0
    print(f"ESTIMATE — \"{p['kind']}\"")
    print(f"  matching basis: {p['basis']}")
    if p["matched"] == 0:
        print(f"\n  NO SESSIONS ON RECORD for '{p['kind']}'. No estimate — there is nothing to estimate from.")
        print("  Journal the next build of this kind (--start/--step/--stop) and this becomes answerable.")
        return 0

    if not p["estimable"]:
        n = p["timed"]
        print(f"\n  {p['matched']} session(s) matched, {n} with a usable duration — "
              f"TOO FEW TO ESTIMATE (floor is {p['min_sessions']}).")
        print("  Not producing a number from this sample. Here is what those sessions actually were:")
    else:
        h = p["hours"]
        print(f"\n  HOURS   median {fmt_hours(h['median'])}   range {fmt_hours(h['min'])}–{fmt_hours(h['max'])}"
              f"   (n={h['n']})")
        if "cost" in p:
            c = p["cost"]
            note = "  ALL SELF-REPORTED ESTIMATES — not metered" if c["all_estimates"] else ""
            print(f"  COST    median ${c['median']:,.2f}   range ${c['min']:,.2f}–${c['max']:,.2f}"
                  f"   (n={c['n']}){note}")
        else:
            print(f"  COST    only {p['costed']} of {p['matched']} sessions carry a $ figure — "
                  f"below the floor of {p['min_sessions']}; no median offered.")
        if p.get("representative"):
            r = p["representative"]
            print(f"\n  TYPICAL STEP SEQUENCE (session {r['id']}, {fmt_hours(r['hours'])} — the median run)")
            for i, st in enumerate(r["steps"], 1):
                print(f"    {i}. {st}")
        if p["common_steps"]:
            print("\n  STEPS THAT RECUR ACROSS THESE BUILDS")
            for step, n in p["common_steps"]:
                if n > 1:
                    print(f"    {n}x  {step}")
        print("\n  SAMPLE")

    for s in p["sessions"]:
        print(f"    {s['date']}  {s['id']}  {s['client']} · {s['phase']} · "
              f"{fmt_hours(s['hours'])} [{s['hours_precision']}] · "
              f"{_fmt_money(s['cost_usd'])} [{s['cost_evidence'] or 'no $ reported'}]")
        print(f"        {s['what']}")
        for st in s["steps"]:
            print(f"          - {st}")
        if s.get("notes"):
            print(f"        notes: {s['notes']}")
        for f in s["flags"]:
            print(f"        ! {f}")
    if not p["estimable"]:
        print(f"\n  Read them and judge for yourself — that is more honest than a median of {p['timed']}.")
    return 0


# ---- cli -----------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="build_journal.py",
        description="yourco build journal — time + process + cost per build session, "
                    "so the next build is estimable from evidence instead of vibes.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--start", metavar="CLIENT", help="open a build session for a client")
    g.add_argument("--step", metavar="TEXT", help="record one step in the open session")
    g.add_argument("--stop", action="store_true", help="close the open session")
    g.add_argument("--backfill", metavar="CLIENT", help="record a past build (precision: unknown)")
    g.add_argument("--correct", metavar="SESSION", help="append a correction to a session")
    g.add_argument("--list-open", action="store_true", dest="list_open")
    g.add_argument("--report", action="store_true")
    g.add_argument("--estimate", metavar="KIND", help="what has a build of this kind actually taken?")

    ap.add_argument("--phase", choices=PHASES, help="cost-ledger phase (same four, never forked)")
    ap.add_argument("--what", help="one line: what this session is building")
    ap.add_argument("--kind", help="estimation bucket, e.g. 'quote platform', 'demo kit' "
                                   "(defaults to the phase)")
    ap.add_argument("--session", help="target a specific session id (needed when >1 is open)")
    ap.add_argument("--notes", help="closing notes")
    ap.add_argument("--tokens", type=int, help="self-reported token count, if you have one")
    ap.add_argument("--cost", type=float, help="self-reported $ for this session")
    ap.add_argument("--metered", action="store_true",
                    help="ONLY if the --cost came from a console/invoice, not an estimate")
    ap.add_argument("--hours", type=float, help="state the real hours worked (overrides wall clock)")
    ap.add_argument("--accept-stale", action="store_true", dest="accept_stale",
                    help="record a stale session's raw elapsed time anyway (flagged unreliable)")
    ap.add_argument("--append-ledger", action="store_true", dest="append_ledger",
                    help="also insert the emitted row into clients/<client>/cost.md")
    ap.add_argument("--date", help="backfill: the date it happened (YYYY-MM-DD)")
    ap.add_argument("--steps", help="backfill: steps separated by | ")
    ap.add_argument("--set", action="append", help="correction: key=value (repeatable)")
    ap.add_argument("--why", help="correction: why")
    ap.add_argument("--json", action="store_true", help="machine output")
    a = ap.parse_args(argv)

    if a.start:
        if not a.phase:
            ap.error("--start requires --phase")
        return cmd_start(a)
    if a.step:
        return cmd_step(a)
    if a.stop:
        return cmd_stop(a)
    if a.backfill:
        if not a.phase or not a.date:
            ap.error("--backfill requires --phase and --date")
        return cmd_backfill(a)
    if a.correct:
        return cmd_correct(a)
    if a.list_open:
        return cmd_list_open(a)
    if a.report:
        return cmd_report(a)
    if a.estimate:
        return cmd_estimate(a)
    ap.error("nothing to do")


if __name__ == "__main__":
    sys.exit(main())
