#!/usr/bin/env python3
"""Plat OS — the suite. `python3 test_plat_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["PLATOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="platos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import timedelta

import agents, core, seed
from core import store
from _kit.store import is_missing, iso, now

PASS = FAIL = 0


def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {label}")


print("== seed ==")
seed.main()
open_jobs = [j for j in store.load("jobs") if j["stage"] != "sealed"]
sealed = [j for j in store.load("jobs") if j["stage"] == "sealed"]
ok(len(open_jobs) >= 60, "open jobs seeded")
ok(len(sealed) >= 200, "historical sealed jobs seeded (the comparables)")
ok(len(store.load("day_sheets")) >= 20, "day sheets seeded")

print("== triage: the boundary question reads first ==")
for c in core.EVAL_CASES:
    got = core.read_message(c["input"])["label"]
    ok(got == c["label"], f"triage: {c['input'][:44] or '(empty)'} → {c['label']} (got {got})")

print("== the boundary refusal ==")
out = agents.handle_message("ms_demo_boundary")
step = out["steps"][0]
ok(step["action"] == "route_to_pls", "the question routes to the PLS")
row = store.by_id("boundary_log", step["recorded"])
ok(row and "the buyer says the shed encroaches" in row["verbatim"],
   "the question is preserved VERBATIM in the append-only log")
ok(row["routed_to"]["name"] == "Rosa Whitcomb", "routed to the RECORDED PLS by name")
ev = next(e for e in store.events()
          if e["kind"] == "refused" and (e["detail"] or {}).get("action") == "state_boundary_conclusion")
ok("shed encroaches" in ev["detail"]["verbatim"], "the refusal event carries the verbatim ask")
body = step["draft"]
ok("Rosa Whitcomb" in body and "PLS 5521" in body, "the draft names the licensed surveyor")
ok("sealed" in body, "the draft points at the sealed record, not an opinion")
okb, why = core.boundary_reply_ok(body)
ok(okb, f"the shipped copy passes its own conclusion check ({why})")
ok(not core.boundary_reply_ok("the fence encroaches on your property")[0],
   "conclusion language is structurally refused")
ok(not core.boundary_reply_ok("don't worry, the line is well clear of the shed")[0],
   "'the line is' from software is structurally refused")
ok("yourco" not in body.lower(), "white-label")

print("== append-only boundary log ==")
n0 = len(store.load("boundary_log"))
core.record_boundary_question("is the pin by the oak the corner, can you confirm", "Kovac")
core.record_boundary_question("is the pin by the oak the corner, can you confirm", "Kovac")
ok(len(store.load("boundary_log")) == n0 + 2,
   "a repeated question is a NEW entry — nothing overwritten")
ok(not hasattr(core, "delete_boundary_question") and not hasattr(core, "edit_boundary_question"),
   "no delete and no edit exist anywhere in the module — the absence is the rule")

print("== the seal gate ==")
r = agents.seal_plat("jb_demo_unsealed")
ok("refused" in r and "no path" in r["refused"], "sealing without a reference is refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "seal_without_reference"
       for e in store.events()), "seal_without_reference logged")
ok(store.by_id("jobs", "jb_demo_unsealed")["stage"] == "pls_review",
   "the job did NOT move to sealed")
ok(not any(a["action"] in ("mark_plat_sealed", "seal_without_reference")
           and a["state"] == "pending" for a in store.load("approvals")),
   "no approvable row — there is structurally no path, not a slow yes")
r = agents.seal_plat("jb_demo_unsealed", seal_number="S-2026-0901", seal_date=iso(now()))
ok("refused" in r and "PLS's act" in r["refused"], "even with a reference, no PLS → no seal")
r = agents.seal_plat("jb_demo_unsealed", seal_number="S-2026-0901", seal_date=iso(now()),
                     pls="whitcomb")
ok(r.get("sealed") and r["seal"]["number"] == "S-2026-0901",
   "with the recorded reference and the PLS, it seals")
j = store.by_id("jobs", "jb_demo_unsealed")
ok(j["stage"] == "sealed" and j["seal"]["number"] == "S-2026-0901",
   "the seal reference is on the job record")
ok(any(e["kind"] == "mark_plat_sealed" and e["actor"] == "human:whitcomb"
       for e in store.events()), "the seal event is the PLS's, a human's")

print("== the research chain ==")
r = agents.begin_draft("jb_demo_nochain")
ok("refused" in r and "a boundary without its chain is an opinion" in r["refused"],
   "a draft citing nothing is refused, with the rule named")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "draft_without_research_chain"
       for e in store.events()), "draft_without_research_chain logged")
ok(store.by_id("jobs", "jb_demo_nochain")["stage"] == "field", "the job did not advance")
chained = next(j for j in open_jobs if j["stage"] == "field" and j.get("research_chain"))
r = agents.begin_draft(chained["id"])
ok(r.get("stage") == "draft" and r["chain"]["cited"] >= 1, "a cited job advances to draft")
ok(any("deed book" in i for i in r["chain"]["instruments"]),
   "the chain cites instruments — deed book/page")

print("== crew day sheets ==")
ds = core.day_sheet_status(store.by_id("jobs", "jb_demo_nosheet"))
ok(is_missing(ds), "fieldwork with no same-day sheet reads INCOMPLETE via unmeasured")
ok("never assumed" in ds["_missing"], "the reason says never assumed")
ds = core.day_sheet_status(store.by_id("jobs", "jb_demo_friday"))
ok(ds.get("complete") and ds.get("points") == 212, "a same-day sheet reads complete, counted")
ok(core.day_sheet_status({"id": "x"}).get("applies") is False, "no fieldwork → the rule is n/a")

print("== the deadline board ==")
db = core.deadline_board()
dated = [r["days_to_closing"] for r in db["rows"] if r["days_to_closing"] is not None]
ok(dated == sorted(dated), "ranked by days-to-closing — the master clock")
undated = [r for r in db["rows"] if r["days_to_closing"] is None]
ok(all(db["rows"].index(u) >= len(dated) for u in undated),
   "jobs with no closing date rank last, never guessed into the queue")
ok(undated and "never guessed" in undated[0]["note"], "the missing clock is named")
ok(any("no research chain cited" in b for r in db["rows"] for b in r["blockers"]),
   "the chain blocker is named on the board")
ok(any("no same-day crew sheet" in b for r in db["rows"] for b in r["blockers"]),
   "the missing day sheet is named on the board")
ok(any("CLOSING WEEK" in b for r in db["rows"] for b in r["blockers"]),
   "closing week is flagged to a human")

print("== the closing promise, from recorded clocks only ==")
clocks = core.stage_medians()
ok("medians" in clocks and clocks["n"] >= 200, "stage clocks counted from sealed history")
p = core.closing_projection(store.by_id("jobs", "jb_demo_friday"))
ok(p.get("days_to_closing") is not None and p.get("projected_days_to_seal") is not None,
   "the projection computes both clocks")
ok("sealed jobs" in p["basis"] and "never a gut answer" in p["basis"],
   "the basis names its evidence")
ok(is_missing(core.closing_projection({"id": "x", "stage": "draft"})),
   "no closing date → unmeasured, never guessed")
ok(is_missing(core.stage_medians([])), "no recorded history → no clocks, stated")
r = core.promise_closing_reply({"id": "x", "stage": "draft"})
ok("refused" in r and "guess" in r["refused"], "a promise without recorded clocks is refused")
out = agents.handle_message("ms_demo_closing")
step = out["steps"][0]
ok(step["action"] == "draft_deadline_reply", "the title company gets a drafted answer")
ok("stage clocks" in step["draft"] and "A person confirms" in step["draft"],
   "the draft cites the clocks and holds for a human")
ok("yourco" not in step["draft"].lower(), "white-label")
ok(any(a["action"] == "draft_deadline_reply" and a["state"] == "pending"
       for a in store.load("approvals")), "the deadline reply queues at R1 — a human sends")

print("== status from the record ==")
out = agents.handle_message("ms_000")
step = out["steps"][0]
ok(step["action"] == "draft_status_reply" and "record" in step["draft"],
   "status is answered from the pipeline record")

print("== quotes: comparables or refusal ==")
q = core.quote_math("boundary", 3)
ok(q.get("comparables", 0) >= 3, "the 3-acre boundary quote has recorded comparables")
ok("median" in q["basis"] and "our own book" in q["basis"], "the basis is the recorded median")
q = core.quote_math("alta", 300)
ok("refused" in q and "we don't guess" in q["refused"], "no comparables → refused, not guessed")
ok("refused" in core.quote_math("boundary", None), "no acreage → refused, inputs named")
out = agents.handle_message("ms_demo_quote_ok")
ok(out["steps"][0]["action"] == "draft_quote" and "$" in out["steps"][0]["draft"],
   "a comparable-backed quote drafts for a human")
out = agents.handle_message("ms_demo_quote_none")
ok("refused" in out["steps"][0], "the 300-acre ALTA ask is refused on the agent path")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "quote_without_comparables"
       for e in store.events()), "quote_without_comparables logged")

print("== deadline sweep ==")
sw = agents.deadline_sweep()
ok(sw["drafted"] >= 1, "closing-week jobs get drafted alerts")
ok(not any(j.get("demo_tag") and j.get("deadline_alerted_at")
           for j in store.load("jobs")), "the sweep skips demo fixtures")

print("== matrix ==")
for a in ("state_boundary_conclusion", "seal_without_reference",
          "draft_without_research_chain", "quote_without_comparables"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
ok(core.matrix.actions["promise_closing_date"]["rung"] == "R1", "promise_closing_date sits at R1")
ok(core.matrix.actions["mark_plat_sealed"]["rung"] == "R1", "mark_plat_sealed sits at R1")
r = core.gate.act("state_boundary_conclusion", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] == "state_boundary_conclusion" and a_["state"] == "pending"
           for a_ in store.load("approvals")), "R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no boundary question missed")
ok("WITHOUT A LICENSE" in ev["costly_note"], "the costly note names the licensure stake")

print("== roi ==")
r = core.roi({})
ok(r["recorded"]["crews"] == 2 and r["recorded"]["jobs_mo"] >= 1,
   "crews and jobs/mo are counted, not asked for")
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Crew-week throughput"]["kind"] == "revenue", "throughput is typed revenue")
ok(labels["Research hours returned"]["kind"] == "time_saved", "research hours are typed time")
sc = labels["The lost title company"]
ok(sc["kind"] == "scenario" and sc["value"] is None and "_missing" in sc,
   "the lost-title-company line is a scenario and renders BLANK until the operator prices it")
ok("never a saving" in (sc["assumption"] or ""), "the scenario refuses to be a saving")

print("== recovered, counted ==")
base = core.recovered_this_week()
ok(base["plats_sealed"] >= 2, "seals this week counted (incl. the demo seal)")
agents.seal_plat("jb_demo_friday", seal_number="S-2026-0902", seal_date=iso(now()),
                 pls="whitcomb")
store.log_event("draft_deadline_reply", "jb_demo_friday", "human:owner", "R1", {})
rec = core.recovered_this_week()
ok(rec["plats_sealed"] == base["plats_sealed"] + 1, "a new seal moves the count by exactly one")
ok(rec["closings_kept"] == base["closings_kept"] + 1,
   "sealed before its closing → a closing KEPT, counted")
ok(rec["deadline_alerts_sent"] == base["deadline_alerts_sent"] + 1,
   "human-sent alerts counted; agent drafts are not")
ok(rec["boundary_questions_routed"] >= 1, "routed boundary questions counted from refusals")
ok("counted" in rec["note"], "recovered names its basis")

print("== append-only events ==")
n = len(store.events())
store.log_event("note", "x", "human:test", "R1", {})
ok(len(store.events()) == n + 1, "the event log only grows — corrections are new events")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
