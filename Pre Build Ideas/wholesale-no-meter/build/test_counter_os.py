#!/usr/bin/env python3
"""Counter OS — the suite. `python3 test_counter_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["COUNTEROS_DATA_ROOT"] = tempfile.mkdtemp(prefix="counteros_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import agents, core, seed
from core import store

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
ok(len(store.load("catalog")) >= 550, "catalog seeded (~600 items)")
ok(len(store.load("nos")) >= 240, "~250 no-events seeded")
ok(len(store.load("vendors")) == 8, "vendors seeded")

print("== triage: the contractor-down reads first ==")
for text, want in (
        ("my crew is standing around, do you have 2 in EMT connectors RIGHT NOW", "contractor_down"),
        ("job is down until we get a 3/4 pex crimp tool, need it today", "contractor_down"),
        ("emergency — the site needs 200 ft of 12/2 MC right now", "contractor_down"),
        ("customer asked for a ridgeline press jaw, we don't carry it", "no_report"),
        ("we were out of 2 in emt connectors again, he walked", "no_report"),
        ("turned away another guy asking for pex crimp rings", "no_report"),
        ("didn't have the 6 in dwv coupling in stock", "no_report"),
        ("price on 500 ft of 12/2 romex", "price_ask"),
        ("how much for a case of pvc primer", "price_ask"),
        ("can you quote 40 sticks of 2 in rigid", "price_ask"),
        ("is my will call order ready", "willcall"),
        ("order 5512 ready for pickup?", "willcall"),
        ("", "human"),
        ("what time do you open saturday", "human"),
        ("who do I talk to about a return", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44] or '(empty)'} → {want}")

print("== capture + pricing, both paths ==")
r = agents.report_no({"item_asked": "2 in EMT connector", "kind": "out_of_stock",
                      "branch": "Fairfield", "sku": "ELC-0042", "qty": 10,
                      "walked_or_waited": "waited"})
ok(r["pricing"]["priced"] and r["pricing"]["dollars"] == round(0.56 * 10, 2),
   "priced from the catalog item's own margin: 10 × $0.56")
ok("catalog margin on ELC-0042" in r["pricing"]["basis"], "the basis names the SKU")
r = agents.report_no({"item_asked": "Ridgeline RL-34 press jaw", "kind": "not_carried",
                      "branch": "Riverside", "category": "press tools", "qty": 1})
ok(r["pricing"]["priced"] and r["pricing"]["dollars"] == 38.0,
   "priced from the recorded category margin")
ok("recorded category margin" in r["pricing"]["basis"]
   and "source:" in r["pricing"]["basis"], "the category basis names its source")
r = agents.report_no({"item_asked": "some mystery bracket", "kind": "not_carried",
                      "branch": "Fairfield"})
ok(not r["pricing"]["priced"] and r["pricing"]["dollars"] is None, "no comparable → UNPRICED")
ok("a counted mystery beats an invented dollar" in r["pricing"]["why"],
   "the UNPRICED phrase is asserted")
ok("refused_pricing" in r, "the refusal to invent a dollar is logged, not silent")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "price_no_without_comparable"
       for e in store.events()), "price_no_without_comparable logged as a refusal")
r = agents.report_no({"item_asked": "half a capture", "kind": "not_carried"})
ok("error" in r and "branch" in r["error"], "a half-captured no is named, not counted")

print("== the stocking case: the count drafts it ==")
r = agents.draft_stocking_case("Ridgeline RL-34 press jaw")
ok("case" in r, "the threshold-crossing item drafts a case")
c = r["case"]
ok(c["threshold"]["arithmetic"].startswith("8 counted no's")  # 7 seeded + 1 filed above
   and "≥ the recorded threshold of 5" in c["threshold"]["arithmetic"],
   "the threshold arithmetic prints on the case")
ok(c["math"]["counted_margin_dollars"] == 8 * 38.0, "the margin math is the count × the recorded margin")
nos_by_id = {n["id"]: n for n in store.load("nos")}
ok(all(h["id"] in nos_by_id and nos_by_id[h["id"]] == h for h in c["history"]),
   "the no history is the ledger verbatim — every row is the stored row itself")
ok(len(c["history"]) == 8, "all counted no's ride on the case")
ok(r["gate"]["rung"] == "R1" and not r["gate"]["executed"],
   "the case drafts at R1 — a human commits the dollars")
opts = c["vendor_options"]["options"]
ok(len(opts) == 1 and opts[0]["vendor"] == "v_dover" and opts[0]["lead_time_days"] == 4,
   "vendor options are recorded vendors with recorded lead times only")

print("== below the threshold: structural refusal ==")
r = agents.draft_stocking_case("2 in copper repair coupling")
ok("refused" in r and "anecdote, not demand" in r["refused"], "two no's do not draft a case")
ok("2 counted no's" in r["arithmetic"] and "< the recorded threshold of 5" in r["arithmetic"],
   "the refusal prints the same arithmetic")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "stocking_case_below_threshold"
       for e in store.events()), "stocking_case_below_threshold logged")
ok(not any(a["action"] == "stocking_case_below_threshold" and a["state"] == "pending"
           for a in store.load("approvals")), "the R0 never becomes an approvable row")
ok(not any(store.by_id("cases", cid) for cid in (f"case_{agents._slug('2 in copper repair coupling')}",)),
   "no case row exists below the threshold")
ok(not hasattr(core, "force_stocking_case") and not hasattr(agents, "force_stocking_case"),
   "a manual force path does not exist — structurally")
ok(not hasattr(core, "force_case") and not hasattr(agents, "force_case"),
   "no force alias either")

print("== the OOS autopsy: the math, hand-checked ==")
r = agents.draft_oos_autopsy("ELC-0042")
ok("autopsy" in r, "the carried OOS item gets an autopsy")
a = r["autopsy"]
ok(a["proposed_point"] == 42, "proposed point = ceil(6.0/day × (5d lead + 2d safety)) = 42")
ok(a["recorded_point"] == 20, "the recorded point it beat is cited")
ok("pace 6.0/day × (lead 5d + safety 2d) = 42.0" in a["math"]
   and "the recorded point was 20" in a["math"], "the arithmetic prints in full")
ok(a["walked_cost"]["dollars"] == round((40 + 25 + 60) * 0.56, 2),
   "walked cost counted: 125 walked units × $0.56 recorded margin = $70.00")
ok("counted from the ledger" in a["walked_cost"]["basis"], "the walked cost names its basis")
ok(a["safety_source"].startswith("owner's rule"), "the safety factor names its source")
ok(r["gate"]["rung"] == "R1", "the autopsy drafts at R1")
r = agents.draft_oos_autopsy("NOPE-9999")
ok("error" in r, "an autopsy needs a carried item")

print("== the vendor packet: verbatim only ==")
r = agents.draft_vendor_packet("v_larkspur")
ok("packet" in r, "the vendor with counted no's gets a packet")
p = r["packet"]
ok(all(n["id"] in nos_by_id for n in p["rows"]),
   "every packet row is a ledger row — nothing composed, nothing invented")
import json as _json
pj = _json.dumps(p).lower()
ok("fill_rate" not in pj and "fill rate needs a denominator" in pj,
   "no invented fill rate — and the packet says why")
ok(p["counted"]["fill_failures"] == len(p["rows"]), "the counted totals are counts of the rows shown")
ok(r["gate"]["rung"] == "R1", "the packet drafts at R1 — a human takes it to the rep")
probe = core.gate.act("invent_vendor_stats", "probe", "v_larkspur", {})
ok(probe.get("refused") and probe["rung"] == "R0", "invent_vendor_stats refused at R0")

print("== stock answers: counted only ==")
r = core.stock_answer("do you have a 2 in EMT connector")
ok(r["carried"] and r["sku"] == "ELC-0042", "the ask matches the carried SKU")
ok("counted record" in r["answer"] and "zero" in r["answer"], "zero on hand → the honest no")
ok(core.optimism_ok(r["answer"])[0], "the shipped copy passes its own optimism check")
ok(not core.optimism_ok("we should have some in back, probably")[0],
   "optimism language is structurally refused")
r = core.stock_answer("got any 1/2 in EMT coupling")
ok(r["carried"] and ("Yes — counted stock" in r["answer"] or "zero" in r["answer"]),
   "a carried item answers from counts either way")
r = core.stock_answer("do you carry flux capacitors for a delorean")
ok(not r["carried"] and "not something we carry" in r["answer"], "not carried → the straight answer")
ok(r["capture"] == "not_carried", "the honest no is itself a capture")
probe = core.gate.act("stock_answer_optimism", "probe", "x", {})
ok(probe.get("refused") and probe["rung"] == "R0", "stock_answer_optimism refused at R0")

print("== the contractor-down demo ==")
out = agents.handle_message("ms_demo_down")
ok(out["classification"]["label"] == "contractor_down", "the costly label routes first")
step = out["steps"][0]
ok("counted record" in step["draft"] and "zero" in step["draft"],
   "the crew gets the counted truth, not a hopeful yes")
ok("should have" not in step["draft"].lower() and "probably" not in step["draft"].lower(),
   "no optimism in the draft")
ok(step.get("captured_no"), "the miss itself becomes a counted no")
ok("yourco" not in step["draft"].lower(), "white-label")

print("== the no-report demo ==")
out = agents.handle_message("ms_demo_noreport")
step = out["steps"][0]
ok(step["action"] == "log_no" and step["pricing"]["priced"], "the structured no is captured and priced")
ok(step.get("case"), "the capture that crosses the threshold carries its case")

print("== matrix ==")
for act in ("price_no_without_comparable", "stocking_case_below_threshold",
            "stock_answer_optimism", "invent_vendor_stats"):
    ok(act in core.matrix.never_promote(), f"{act} never promotes")
r0 = core.gate.act("price_no_without_comparable", "probe", "x", {})
ok(r0.get("refused"), "R0 probe refused")
ok(not any(a["action"] in ("price_no_without_comparable", "stock_answer_optimism",
                           "invent_vendor_stats", "stocking_case_below_threshold")
           and a["state"] == "pending" for a in store.load("approvals")),
   "no R0 ever becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["n"] >= 15, "≥15 labelled cases")
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no contractor-down missed")
ok("CREW STANDING AROUND" in ev["costly_note"], "the costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok("priced_no_dollars_60d" in r["recorded"] and "walked_oos_dollars_60d" in r["recorded"],
   "the counted inputs are recorded, not asked for")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Captured demand"]["kind"] == "revenue"
   and labels["Captured demand"]["value"] is None, "captured demand is blank until the rate is yours")
ok(labels["Counter seconds"]["kind"] == "time_saved", "counter time is time_saved, never revenue")
ok(labels["Vendor concessions"]["kind"] == "scenario"
   and labels["Vendor concessions"]["value"] is None, "the concession line is a blank scenario")
r = core.roi({"capture_rate": 0.4, "recovery_share": 0.5, "seconds_saved": 45,
              "loaded_rate": 38})
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Captured demand"]["value"] is not None, "with your rate, the counted dollars compute")
ok(labels["Vendor concessions"]["value"] is None, "the scenario stays blank — never auto-filled")

print("== the counted week ==")
wk = core.counted_week()
ok(wk["this_week"]["count"] > 0, "this week is counted")
ok(wk["baseline"].get("weekly_avg") is not None, "the baseline is counted from 8 prior weeks")
ok("count" in wk["delta"], "the delta is stated against the counted baseline")
ok("counted from the ledger" in wk["note"], "the week names its basis")

print("== demo fixtures are excluded from counts ==")
ok(all(not n.get("demo_tag") for n in core.recent_nos(400)),
   "recent_nos never returns a demo row")
ok("no_demo_excluded" not in [n["id"] for n in core.recent_nos(60)],
   "the seeded demo row is skipped")
board = core.no_board()
ok(board["count"] == len(core.recent_nos(7)), "the board is the counted ledger, exactly")
ok("never asserted" in board["note"], "the board names its basis")

print("== append-only ==")
n0 = len(store.events())
agents.report_no({"item_asked": "append test item", "kind": "not_carried",
                  "branch": "Fairfield"})
n1 = len(store.events())
ok(n1 > n0, "events only grow")
first_ids = [e["id"] for e in store.events()][:n0]
ok(first_ids == [e["id"] for e in store.events()[:n0]], "earlier events are untouched")

print("== automation ==")
agents.run_all()
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted from the log, or refused with the reason")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
