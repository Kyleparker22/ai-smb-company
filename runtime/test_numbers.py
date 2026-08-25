#!/usr/bin/env python3
"""Tests for the one number + the number each agent owns + the nine KPIs.

Same discipline as runtime/test_evidence.py and test_agentops.py: **every assertion guards an
HONESTY rule, not a feature.** These two modules exist because yourco had nine goals (which is
zero) and 27 agents owning no numbers. The temptation they create is obvious and specific — make
the scoreboard look green — and there are exactly three ways to do it:

  1. count activity instead of outcomes ("the loop ran" → a number),
  2. render a missing input as 0 instead of as refused,
  3. extrapolate a date from a rate of zero.

Each is pinned below, so a future edit that makes the board look better has to DELETE an assertion.

Run:  python3 runtime/test_numbers.py
"""
import os, sys, json, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import northstar as ns                  # noqa: E402
import loop_metrics as lm               # noqa: E402
import crm_metrics as cm                # noqa: E402
import client_metrics as cl             # noqa: E402
import uptime as up                     # noqa: E402
import gate_metrics as gm               # noqa: E402
import kpis as kp                       # noqa: E402

import inspect as _inspect

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ok   " if cond else "  FAIL ") + name + (("  — " + detail) if detail and not cond else ""))


# ── the registry block: every agent, every gap named ────────────────────────────────────────
blk = ns._registry_block()
agents = blk.get("agents") or {}
folders = sorted(n for n in os.listdir(os.path.join(ROOT, "agents"))
                 if os.path.isdir(os.path.join(ROOT, "agents", n)) and not n.startswith("_"))

check("every agent folder owns a number", set(folders) <= set(agents),
      str(sorted(set(folders) - set(agents))))
check("no number is owned by an agent that does not exist", set(agents) <= set(folders),
      str(sorted(set(agents) - set(folders))))
check("every unmeasured metric names the ONE thing missing",
      all(a.get("needs") and a.get("blockedBy")
          for a in agents.values() if a.get("source") == "unmeasured"))
check("`ladders` is direct or enabling — there is no third category",
      all(a.get("ladders") in ("direct", "enabling") for a in agents.values()))
check("every declared source is one the module can actually compute",
      all(a.get("source") == "unmeasured" or a.get("owns") in ns.METRICS
          for a in agents.values()))

# The rule that keeps the scoreboard honest. Every agent has a loop artifact that could be counted;
# counting it would produce 27 green numbers and measure nothing anybody would act on.
liveness = [w for w, a in agents.items() if a.get("owns") == "loopLiveness"]
check("did-it-run is not an outcome — only Atlas may own loop liveness", liveness == ["atlas"],
      str(liveness))

# ── the values: a missing source refuses, it does not report zero ───────────────────────────
rows = ns.owners()
# Three states, not two. `awaiting` (a real source declared, nothing readable right now) must stay
# distinct from `unmeasured` (nothing wired at all) — collapsing them hides a broken extractor
# inside the same blank as the metrics nobody has built.
check("a row is exactly `computed`, `awaiting` or `unmeasured`",
      all(r["state"] in ("computed", "awaiting", "unmeasured") for r in rows))
check("a row without a value never claims one",
      all(r["value"] is None for r in rows if r["state"] != "computed"))
check("a row without a value always says what it needs",
      all(r["needs"] for r in rows if r["state"] != "computed"))
check("`awaiting` is only ever used where a real source is declared",
      all(r["source"] != "unmeasured" for r in rows if r["state"] == "awaiting"))
check("`unmeasured` is only ever used where NO source is declared",
      all(r["source"] == "unmeasured" for r in rows if r["state"] == "unmeasured"))

with tempfile.TemporaryDirectory() as td:
    real = ns.ACTUALS
    try:
        ns.ACTUALS = os.path.join(td, "gone.json")       # the file simply is not there
        v, _unit, why = ns._runway_months()
        check("a missing finance ledger refuses — it does not compute a runway of 0",
              v is None and why and "missing" in why.lower(), repr((v, why)))
        json.dump({"cash": {"onHand": 5000}, "burn": {"monthlyFixed": 0}},
                  open(os.path.join(td, "z.json"), "w"))
        ns.ACTUALS = os.path.join(td, "z.json")
        v, _unit, why = ns._runway_months()
        check("zero burn is UNDEFINED runway, never infinite",
              v is None and "undefined" in (why or "").lower(), repr((v, why)))
    finally:
        ns.ACTUALS = real

# ── the north star: declared, singular, and unwilling to forecast from nothing ──────────────
star = ns.north_star()
check("a north star is declared", star.get("declared") is True)
check("the north star is a single metric", isinstance(star.get("metric"), str) and star["metric"])
check("the other goal metrics are named supporting, not deleted",
      len(star.get("supporting") or []) >= 1)
if not star.get("current"):
    p = star.get("projection") or {}
    check("no projection from a rate of zero", p.get("value") is None and bool(p.get("refusal")))
    check("the refusal says WHY, not just that it refused",
          "forecast" in (p.get("refusal") or "").lower())
else:
    check("a projection off real movement is still refused without a trend",
          (star.get("projection") or {}).get("value") is None)

cov = ns.coverage(rows)
check("every agent lands in exactly one state — none is quietly uncounted",
      cov["computed"] + cov["awaiting"] + cov["unmeasured"] == cov["agents"],
      str(cov))
check("blockers account for EVERY row without a value, awaiting included",
      sum(b["count"] for b in ns.blockers(rows))
      == sum(1 for r in rows if r["state"] != "computed"))

# ── nothing here writes ──────────────────────────────────────────────────────────────────────
import re as _re
for mod in ("northstar.py", "kpis.py"):
    src = open(os.path.join(ROOT, "dashboard", mod)).read()
    writes = (_re.findall(r'open\([^)]*["\']["wax]b?\+?["\']', src)
              + _re.findall(r'\bjson\.dump\(', src)
              + _re.findall(r'\bos\.replace\(', src)
              + _re.findall(r'\.write\(', src))
    check(f"{mod} stores no number — every value is computed per call, never persisted",
          not writes, str(writes))

# ── the seven that were prose (2026-08-25) ──────────────────────────────────────────────────
# These read numbers back out of markdown. That is only safe while a structure that does not parse
# reports a PARSE FAILURE rather than a zero — a metric that silently reads 0 when a heading gets
# renamed is worse than one that reads blank, because 0 looks like an answer.
for key, fn in lm.METRICS.items():
    v, unit, note = fn()
    check(f"{key}: always explains itself", bool(note))
    check(f"{key}: a blank is never dressed as a zero", v is None or isinstance(v, (int, float)))

check("every prose-fixed metric declares which mechanism it uses",
      set(lm.MECHANISM) == set(lm.METRICS)
      and all(m in ("derived", "extracted") for m in lm.MECHANISM.values()))

with tempfile.TemporaryDirectory() as td:
    real = lm.REPO
    try:
        # An empty repo: every heading these depend on is gone. Not one may answer 0.
        lm.REPO = td
        os.makedirs(os.path.join(td, "loops/eval-review"))
        open(os.path.join(td, "loops/eval-review/2026-08-25.md"), "w").write(
            "# Eval review\n\n## Scoreboard (this week)\n\nthe table was renamed away\n")
        v, _u, why = lm.eval_pass_rate()
        check("a scoreboard that does not parse REFUSES — it does not report a 0% pass rate",
              v is None and "did not parse" in (why or ""), repr((v, why)))
        os.makedirs(os.path.join(td, "loops/aeo-geo"))
        open(os.path.join(td, "loops/aeo-geo/2026-08-25.md"), "w").write(
            "# AEO\n\n## Citation-presence score\n\nnot a number any more\n")
        v, _u, why = lm.citation_presence()
        check("a missing citation score REFUSES — it does not report 0%",
              v is None and "not inferring" in (why or ""), repr((v, why)))
        os.makedirs(os.path.join(td, "loops/_governance"))
        open(os.path.join(td, "loops/_governance/2026-08-25.md"), "w").write(
            "# drift\n\n**Result:** \u26a0\ufe0f DRIFT\n\nthe finding table was reformatted\n")
        v, _u, why = lm.registry_drift_open()
        check("a DRIFT report whose table will not parse never reports 0 open findings",
              v is None and "contradict" in (why or ""), repr((v, why)))
        open(os.path.join(td, "loops/_governance/2026-08-26.md"), "w").write(
            "# drift\n\n**Result:** \u2705 clean\n\nNo drift.\n")
        v, _u, _w = lm.registry_drift_open()
        check("a genuinely clean governance run DOES report 0 — a refusal everywhere would be "
              "just as dishonest", v == 0, repr(v))
        os.makedirs(os.path.join(td, "loops/brand-audit"))
        open(os.path.join(td, "loops/brand-audit/2026-08.md"), "w").write(
            "# Brand\n\n## Review volume\n**0 reviewed \u00b7 0 cleared first time**\n")
        v, _u, why = lm.brand_first_pass()
        check("a first-pass rate over zero reviews is UNDEFINED, not 100%",
              v is None and "undefined" in (why or "").lower(), repr((v, why)))
        open(os.path.join(td, "loops/brand-audit/2026-08.md"), "w").write(
            "# Brand\n\n## Review volume\n**4 reviewed \u00b7 3 cleared first time**\n")
        v, _u, _w = lm.brand_first_pass()
        check("a real review volume computes the rate", v == 75, repr(v))
    finally:
        lm.REPO = real

# Melanie's count is a floor by construction; saying so is the only thing that makes a 0 fair.
_v, _u, note = lm.initiatives_adopted()
check("the initiative count is labelled a FLOOR, because adoption without a decision is invisible",
      "FLOOR" in (note or ""))

# Staleness is shown, never silently trusted.
_v, _u, note = lm.eval_pass_rate()
check("a reading past twice its loop's cadence carries a STALE warning in the note it travels with",
      ("STALE" in (note or "")) or ("d ago" in (note or "")))

# ── the five that needed a CRM field (2026-08-25) ───────────────────────────────────────────
# The temptation here is different from the extractors': these read a schema that STARTS EMPTY, so
# every one of them could report a confident 0 on day one and look finished.
_crm = cm._crm()
_meta = _crm.get("meta") or {}
check("the channel vocabulary is declared in the CRM, not in the reader",
      len(_meta.get("sourceChannels") or []) >= 5)
check("'Audit delivered' exists as an activity type — the Audit is the front door and nothing "
      "counted one", "Audit delivered" in (_meta.get("activityTypes") or []))
check("'collateral' exists as an artifact type — otherwise a one-pager looks like a build",
      "collateral" in (_meta.get("artifactTypes") or []))

_cos = [c for c in (_crm.get("companies") or []) if not c.get("archived")]
check("every channel on a company is in the declared vocabulary",
      all((c.get("channel") or "") in set(_meta.get("sourceChannels") or []) | {""} for c in _cos))
check("no company's channel was INFERRED — the backfill restated `source`, it did not judge",
      all((c.get("channelSource") or "") in ("", "recorded", "restated") for c in _cos),
      str(sorted({c.get("channelSource") or "" for c in _cos})))
check("`founder-sourced` stayed distinct from `warm-network` — who typed the row is not a claim "
      "about how well we know them",
      "founder-sourced" in (_meta.get("sourceChannels") or [])
      and "warm-network" in (_meta.get("sourceChannels") or []))

for key, fn in cm.METRICS.items():
    v, unit, note = fn()
    check(f"{key}: always explains itself", bool(note))
    check(f"{key}: a blank is never dressed as a zero", v is None or isinstance(v, (int, float)))

# The two that must NOT report a confident zero, and the reasons are different.
v, _u, why = cm.audits_to_engagement()
check("no audit conversion rate before any audit exists — and not a 0% either",
      v is None and "no 'Audit delivered'" in (why or ""), repr((v, why)))
v, _u, why = cm.collateral_reached_buyer()
check("0% collateral reach would claim a linking habit that does not exist yet — so it refuses",
      v is None and "does not exist yet" in (why or ""), repr((v, why)))
v, _u, why = cm.inbound_from_content()
check("content refuses while nothing is published — a 0 would read as a verdict on the content "
      "rather than on the gate",
      v is None and "OtherVenture" in (why or ""), repr((v, why)))

# The one that SHOULD report zero, because the path has been live and nothing came through it.
v, _u, why = cm.signals_promoted()
check("the intent sweep DOES report a real zero — refusing everywhere would be its own dishonesty",
      v == 0 and "since July" in (why or ""), repr((v, why)))

# Coverage is a refusal condition, not a footnote.
import copy as _copy
_saved = cm._crm
try:
    _blank = _copy.deepcopy(_crm)
    for _c in _blank.get("companies") or []:
        _c.pop("channel", None)
    cm._crm = lambda: _blank
    v, _u, why = cm.inbound_from_content()
    check("with no channels recorded, a channel metric refuses on COVERAGE and says how many rows "
          "it could see", v is None and "of" in (why or "") and "%" in (why or ""), repr(why))
finally:
    cm._crm = _saved

# Jim's is the oldest, not the average — an average hides the item that has been rotting.
check("the open-loops metric takes the MAX, because an average hides the worst item",
      "max(ages)" in _inspect.getsource(cm.oldest_open_loop))

# ── the six waiting on client #1 (2026-08-25) ───────────────────────────────────────────────
# No amount of building produces a customer. What CAN be got wrong is whether these compute when one
# lands — and the sharpest failure here would be a metric that reads green off a misparse.
_bands = cl.locked_bands()
check("the locked band table parses out of pricing/README.md", len(_bands) >= 4, str(_bands))
check("no band starts below a plausible retainer — the first version read '$3' out of "
      "'cap 3, then graduate' and passed a $1,000 quote as in-band",
      all(lo >= cl.MIN_PLAUSIBLE_RETAINER for _n, lo, _hi in _bands), str(_bands))
check("every band's floor is at or below its ceiling", all(lo <= hi for _n, lo, hi in _bands))
check("the $1,000 brotherhood rate sits inside NO locked band — the fact the metric exists to catch",
      not any(lo <= 1000 <= hi for _n, lo, hi in _bands), str(_bands))
check("bands are parsed from pricing/README.md, never copied into code — a second copy of a price "
      "is a drift surface", "pricing/README.md" in _inspect.getsource(cl.locked_bands))

_v, _u, _note = cl.proposals_at_locked_price()
check("the price metric is a COUNT, not a rate — a percentage off one quote is theatre",
      _u == "in band")

for key, fn in cl.METRICS.items():
    v, unit, note = fn()
    check(f"{key}: always explains itself", bool(note))
    check(f"{key}: a blank is never dressed as a zero", v is None or isinstance(v, (int, float)))

# stageHistory is the whole point of this cluster: the ONLY record that could not have been
# reconstructed later, because stageSince is overwritten on every move.
_crm2 = cl._crm()
_deals = _crm2.get("deals") or []
_stages = {s.get("key") for s in (_crm2.get("stages") or [])}
check("every deal carries a stageHistory — the clock that used to be overwritten on every move",
      all(d.get("stageHistory") for d in _deals),
      str([d.get("id") for d in _deals if not d.get("stageHistory")][:5]))
check("every stageHistory entry names a real stage",
      all(h.get("stage") in _stages for d in _deals for h in (d.get("stageHistory") or [])))
check("every stageHistory entry says whether it was recorded at the move or restated later",
      all((h.get("source") in ("recorded", "restated"))
          for d in _deals for h in (d.get("stageHistory") or [])))
import ast as _ast
_body = _ast.parse(_inspect.getsource(cl._entered)).body[0]
_stmts = _body.body[1:] if _ast.get_docstring(_body) else _body.body
_names = {n.value for st in _stmts for n in _ast.walk(st)
          if isinstance(n, _ast.Constant) and isinstance(n.value, str)}
check("the duration metrics read stageHistory ONLY — stageSince answers a different question and "
      "would silently return the wrong date for any stage already left",
      not any("stageSince" in v for v in _names), str(sorted(_names)))

# Two refusals that are easy to get wrong in the flattering direction.
check("an unscored live client is not counted as healthy — 'nobody looked' and 'it's fine' are "
      "different facts", "unscored is not healthy" in _inspect.getsource(cl.clients_healthy))
check("an invoice still inside its terms is neither on-time nor late",
      "still inside their terms" in _inspect.getsource(cl.invoices_paid_on_time))

# The re-scope is recorded where a future reader will see it, not just in a commit message.
import json as _json
_reg = _json.load(open(os.path.join(ROOT, "runtime/agent-registry.json")))
_kl = _reg["agent_metrics"]["agents"]["Reed"]
check("Reed's re-scope is written down — a production agent is not graded on whether the "
      "founder closes", "RE-SCOPED" in _kl["why"] and _kl["owns"] == "videosReachedProspect")

# ── runtime availability (2026-08-25) ───────────────────────────────────────────────────────
# The whole design is that a MISSING line is the measurement. The three ways to get that wrong are
# to claim uptime for time before monitoring existed, to compute a percentage off a handful of
# beats, and to read a deliberate pause as an outage. All three are pinned.
import tempfile as _tf, datetime as _dt, json as _js

_now = _dt.datetime(2026, 8, 25, 12, 0, tzinfo=_dt.timezone.utc)


def _write(path, spec):
    open(path, "w").write("\n".join(
        _js.dumps({"ts": (_now - _dt.timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "paused": p, "failed_units": 0}) for m, p in spec) + "\n")


_real_store = up.STORE
try:
    with _tf.TemporaryDirectory() as _td:
        _p = os.path.join(_td, "hb.jsonl")
        up.STORE = _p

        up.STORE = os.path.join(_td, "nothing.jsonl")
        _r = up.compute(7, _now)
        check("with no heartbeat at all it reads UNMEASURED, never 100%",
              _r["state"] == "unmeasured" and _r["value"] is None)
        check("and it names the host install as the thing that is missing",
              "host" in (_r["refusal"] or "").lower() and "unmeasured month" in (_r["refusal"] or ""))
        up.STORE = _p

        _write(_p, [(m, False) for m in range(0, 3 * 24 * 60, up.INTERVAL_MIN)])
        _r = up.compute(7, _now)
        check("a clean run computes 100%", _r["value"] == 100.0)
        check("but the window is CLIPPED to the first beat — no claim about time when nothing "
              "was watching", _r["expected"] < 7 * 24 * 60 // up.INTERVAL_MIN,
              f"expected={_r['expected']}")
        check("and it says the window was clipped", any("clipped" in n for n in _r["notes"]))

        _hole = [(m, False) for m in range(0, 3 * 24 * 60, up.INTERVAL_MIN) if not (600 <= m < 840)]
        _write(_p, _hole)
        _r = up.compute(7, _now)
        check("a 4-hour hole shows up as lost availability", _r["value"] < 96.0, str(_r["value"]))
        check("the longest gap is reported in minutes, not inferred", _r["longestGapMinutes"] == 240,
              str(_r["longestGapMinutes"]))
        check("and it fails the SLA reference rather than rounding up to it",
              _r["meetsSlaTarget"] is False)

        _write(_p, [(m, 600 <= m < 840) for m in range(0, 3 * 24 * 60, up.INTERVAL_MIN)])
        _r = up.compute(7, _now)
        check("a deliberate pause is UP, not DOWN — available and idle", _r["value"] == 100.0)
        check("but it is not counted as SERVING either, so a stand-down cannot hide as uptime",
              _r["servingPct"] < 96.0 and _r["paused"] > 0)

        _write(_p, [(m, False) for m in range(0, 60, up.INTERVAL_MIN)])
        _r = up.compute(7, _now)
        check("a handful of beats gets no percentage at all", _r["state"] == "unmeasured")

        open(_p, "a").write("not json at all\n")
        _b, _bad = up.read_beats()
        check("a corrupt line is COUNTED, never silently dropped — a store that loses rows looks "
              "like an outage", _bad == 1)
finally:
    up.STORE = _real_store

check("the beat interval matches between the writer, the timer and the reader",
      f"INTERVAL_MIN={up.INTERVAL_MIN}" in open(os.path.join(ROOT, "runtime/heartbeat.sh")).read()
      and f"*:0/{up.INTERVAL_MIN}" in open(os.path.join(ROOT, "runtime/systemd/yourco-heartbeat.timer")).read())
check("the heartbeat timer is NOT persistent — a catch-up run would back-fill the gap it exists "
      "to expose",
      "Persistent=false" in open(os.path.join(ROOT, "runtime/systemd/yourco-heartbeat.timer")).read())
check("the heartbeat makes no model call — the one thing that must work during an outage cannot "
      "depend on the thing that is out",
      "claude" not in open(os.path.join(ROOT, "runtime/heartbeat.sh")).read().split("set -uo")[1])
check("the beat store is committed, not written into the gitignored loops/_runtime/",
      "loops/_health" in open(os.path.join(ROOT, "runtime/heartbeat.sh")).read()
      and "loops/_health/heartbeat.jsonl" not in open(os.path.join(ROOT, ".gitignore")).read())

# ── the two behind the launch-gate (2026-08-25) ────────────────────────────────────────────
# A gate is not something a metric can fix. What CAN be got wrong is reporting 0 as though it were a
# verdict on the work, and letting the first campaign and the first bookings arrive unattributed.
for key, fn in gm.METRICS.items():
    v, unit, note = fn()
    check(f"{key}: always explains itself", bool(note))
    check(f"{key}: refuses rather than reporting a flattering zero while the gate holds",
          v is None or isinstance(v, (int, float)))

_v, _u, _why = gm.positive_reply_rate()
check("the reply rate names the GATE, not the copy — a 0% would read as a verdict on the copy",
      _v is None and "verdict on the copy" in (_why or ""), repr(_why))
_v, _u, _why = gm.bookings_from_site()
check("bookings name the gate too, and state that the instrument is complete",
      _v is None and "instrument is complete" in (_why or ""), repr(_why))

check("the legacy undifferentiated `replied` counts as CONTACTED and never as POSITIVE — a "
      "vocabulary change must not promote old rows into wins",
      "replied" in gm.CONTACTED and "replied" not in gm.POSITIVE)
check("there is a floor on the reply rate — one reply in eight is not a 12.5%% rate",
      gm.MIN_CONTACTED >= 30)
check("an unreadable OtherVenture tracker is treated as CLOSED — never assume permission",
      "never assume permission" in _inspect.getsource(gm._OtherVenture_open))

# The five intake writers, and the bug class that would have fired the day the gate opened.
_live_stages = {s.get("key") for s in (cl._crm().get("stages") or [])}
_meta2 = cl._crm().get("meta") or {}
for _w in ("runtime/promote.py", "runtime/promote_intent.py", "runtime/intent_server.py",
           "runtime/site_intake.py", "runtime/snapshot_intake.py"):
    _src = open(os.path.join(ROOT, _w)).read()
    _stages_written = set(_re_stage.findall(_src)) if False else set(
        __import__("re").findall(r'"stage":\s*"([a-z\-]+)"', _src))
    check(f"{os.path.basename(_w)} creates deals only on live rungs",
          _stages_written <= _live_stages, str(sorted(_stages_written - _live_stages)))
    check(f"{os.path.basename(_w)} starts the go-live clock on the rows it creates",
          '"stageHistory"' in _src)

_pm = "\n".join(l for l in open(os.path.join(ROOT, "runtime/promote.py")).read().splitlines()
                if not l.lstrip().startswith("#"))
check("promote.py writes seqStatus as the flat schema field, not a nested seq object nothing reads",
      '"seqStatus"' in _pm and '"seq":' not in _pm)
check("promote.py records the reply as POSITIVE, which is what _is_warm already determined",
      '"replied-positive"' in open(os.path.join(ROOT, "runtime/promote.py")).read())
check("`Booking` is a distinct activity type from `Meeting` — nextMeeting holds only the next one",
      "Booking" in (_meta2.get("activityTypes") or []) and "Meeting" in (_meta2.get("activityTypes") or []))
check("`Audit requested` and `Audit delivered` are separate — a request that never became an audit "
      "is a different failure from an audit that never became an engagement",
      {"Audit requested", "Audit delivered"} <= set(_meta2.get("activityTypes") or []))

# Webb's attribution has to survive to launch, which is the moment nobody re-reads this file.
import glob as _glob
_bare = [os.path.basename(p) for p in _glob.glob(os.path.join(ROOT, "agents/webb/pages/yourco-site-v2/*.html"))
         for m in __import__("re").findall(r"calendly\.com/[^\"\'\s]*", open(p, encoding="utf-8").read())
         if "utm_source=" not in m]
check("every Calendly link on the staged site carries where it came from", not _bare, str(sorted(set(_bare))[:4]))

# ── the three waiting on a first business event (2026-08-25) ────────────────────────────────
# These cannot be closed by building — an audit has to be delivered and an asset has to be shown.
# What CAN be fixed is the reason they would stay uncounted AFTER it happens, and the reason nobody
# would notice they were still blank.
_sop = open(os.path.join(ROOT, "processes/audit-sop.md"), encoding="utf-8").read()
check("the audit SOP tells the human to log the delivery — the front door of the whole motion, "
      "uncounted until 2026-08-25", "Audit delivered" in _sop)
check("and it says to log an honest NO as a delivered audit — a conversion rate that drops the "
      "ones that didn't sell is not a conversion rate",
      "honest no is still an audit delivered" in _sop.lower())
check("Reed's definition of done is registering the asset on the deal, not publishing it",
      "type: video" in open(os.path.join(ROOT, "agents/Reed/02_build.md"), encoding="utf-8").read())
check("pickle's definition of done is the same act",
      "type: collateral" in open(os.path.join(ROOT, "agents/pickle/_README.md"), encoding="utf-8").read())

import board as _bd
_rows = _bd.unshown_assets()
check("the Board can state that produced assets have never been shown — a blank metric is "
      "invisible, and this is the one surface that says it out loud",
      len(_rows) == 1 and "never been shown" in _rows[0]["title"], str(_rows))
check("it names BOTH agents' habit as one habit, not two problems",
      not _rows or ("Reed" in _rows[0]["detail"] and "Pickle" in _rows[0]["detail"]))
check("it offers 'these assets are not fit for these conversations' as a real answer — silence and "
      "a decision are different states",
      not _rows or "that is also an answer" in _rows[0]["next"])
check("the unshown-assets row is suppressed when there is nobody to show anything to — producing "
      "before there is an audience is a sequencing choice, not a defect",
      "if not in_motion" in _inspect.getsource(_bd.unshown_assets))
check("and it counts only deals past Pre Convo — you cannot show collateral to someone you have "
      "not spoken to", "pre-convo" in _inspect.getsource(_bd._in_motion_board))

# ── the nine KPIs ────────────────────────────────────────────────────────────────────────────
ks = kp.compute()
check("exactly nine KPIs", len(ks) == 9, str(len(ks)))
check("a KPI is exactly `computed` or `refused`",
      all(k["state"] in ("computed", "refused") for k in ks))
check("a refused KPI carries no value", all(k["value"] is None for k in ks if k["state"] == "refused"))
check("a refused KPI always says what is missing",
      all(k["refusal"] for k in ks if k["state"] == "refused"))
check("EVERY KPI names the precondition that clears it",
      all(k["firstComputableWhen"] for k in ks))
check("every KPI names an owner", all(k["owner"] for k in ks))
check("every KPI carries its formula, so nobody re-derives one under pressure",
      all(k["formula"] for k in ks))

bm = next(k for k in ks if k["key"] == "burnMultiple")
check("burn multiple with no new ARR is UNDEFINED, not infinite and not bad",
      bm["state"] == "refused" and "undefined" in (bm["refusal"] or "").lower())

cac = next(k for k in ks if k["key"] == "cac")
check("CAC is labelled a FLOOR — the founder's time is not in any ledger",
      any("floor" in c.lower() for c in cac["caveats"]))

eb = next(k for k in ks if k["key"] == "ebitda")
check("a computed KPI still carries the caveats that undercut it",
      eb["state"] != "computed" or len(eb["caveats"]) >= 2)

with tempfile.TemporaryDirectory() as td:
    real = kp.ACTUALS
    try:
        kp.ACTUALS = os.path.join(td, "gone.json")
        empty = kp.compute()
        check("with no actuals at all, NOTHING computes — no KPI falls back to zero",
              all(k["value"] is None for k in empty),
              str([k["key"] for k in empty if k["value"] is not None]))
    finally:
        kp.ACTUALS = real

# The doc and the engine are one fact in two places; the watchdog compares them, and so does this.
doc = open(os.path.join(ROOT, "finance/kpi-definitions.md")).read().lower()
missing = [k["name"] for k in ks
           if k["name"].split(" (")[0].lower() not in doc]
check("every computed KPI is defined in finance/kpi-definitions.md", not missing, str(missing))
check("the definitions page refuses to set targets it has no readings for",
      "does not do" in doc and "wish" in doc)

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
