#!/usr/bin/env python3
"""Lab OS — the suite. `python3 test_lab_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["LABOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="labos_test_")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import timedelta

import agents, core, seed
from core import store
from _kit.store import iso, now

PASS = FAIL = 0


def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {label}")


def _obs(unit_id, metric, value, n=None, item=None, date=None):
    rows = store.load("observations")
    rows.append({"id": store.nid("ob"), "unit_id": unit_id, "date": date or iso()[:10],
                 "metric": metric, "item": item, "value": value, "n": n})
    store.save("observations", rows)


def _exp(metric, t, c, item=None, need=None, days=10):
    fl = core.sample_floors()[metric]
    e = {"id": store.nid("exp"), "hypothesis": "test fixture", "metric": metric,
         "item": item, "treatment_units": t, "control_units": c, "status": "live",
         "started_at": iso(now() - timedelta(days=days)),
         "min_sample": {"n": need or fl["n"], "unit": fl["unit"], "_source": "test floor"}}
    store.upsert("experiments", e)
    return e


print("== seed ==")
seed.main()
ok(len(store.load("units")) == 5, "5 units seeded")
ok(len(store.load("experiments")) == 3, "3 experiments seeded")
ok(len(store.load("stockouts")) >= 30, "stockouts seeded")
ok(len(store.load("observations")) > 500, "~60 days of observations seeded")

print("== triage: the illness claim reads first ==")
for text, want in (("your tacos made me sick last night", "illness"),
                   ("I got food poisoning from the brisket bowl", "illness"),
                   ("whole office was throwing up after the catering order", "illness"),
                   ("pretty sure the horchata gave me a stomach bug", "illness"),
                   ("we 86'd the brisket at 6pm again", "stockout_report"),
                   ("ran out of tortillas mid-dinner at riverside", "stockout_report"),
                   ("campus sold out of the salsa flight by 7", "stockout_report"),
                   ("who's winning the guac test", "gm_result_ask"),
                   ("how's the bundle experiment doing, can we call it", "gm_result_ask"),
                   ("any results on the menu board test yet", "gm_result_ask"),
                   ("let's test $1 off bowls at elm street", "experiment_proposal"),
                   ("can we try a bigger portion on the campus tacos", "experiment_proposal"),
                   ("we should run a price test on horchata", "experiment_proposal"),
                   ("", "human"),
                   ("do you cater weddings?", "human"),
                   ("what time does depot district close", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44] or '(empty)'} → {want}")

print("== TOO EARLY is structural: the return has no winner in it ==")
v = core.verdict("exp_demo_live")
ok(str(v["verdict"]).startswith("TOO EARLY TO KNOW (n="), "live test reads TOO EARLY")
ok("need 500" in v["verdict"], "the verdict names the floor")
for k in ("lift_pct", "z", "direction", "diff", "winner", "confidence_read"):
    ok(k not in v, f"below the floor the return carries no '{k}'")
ok("by construction" in v["why"], "the why names the construction")
ok(v["floor_source"] and "DEFAULT sample floors" in v["floor_source"],
   "the floor is _source-named")
# even a HUGE fake lift below the floor refuses to conclude anything
eh = _exp("attach_rate", ["tH"], ["cH"], item="x", need=500)
_obs("tH", "attach_rate", 95, n=100, item="x")
_obs("cH", "attach_rate", 5, n=100, item="x")
vh = core.verdict(eh)
ok(str(vh["verdict"]).startswith("TOO EARLY TO KNOW (n=100, need 500)"),
   "a 1800% fake lift on 100 tickets still reads TOO EARLY")
ok("lift_pct" not in vh and "z" not in vh, "no lift leaks around the floor")
r = core.conclude(eh["id"])
ok("refused" in r and "cannot conclude" in r["refused"], "concluding below the floor refused")
ok(any(e["kind"] == "refused"
       and (e.get("detail") or {}).get("action") == "conclude_below_sample_floor"
       for e in store.events()), "conclude_below_sample_floor logged")

print("== concluded stats, hand-checked ==")
# two-proportion fixture: 300/1000 vs 250/1000 → lift 20.0%, z 2.50 → PROBABLE
ea = _exp("attach_rate", ["tA"], ["cA"], item="a")
_obs("tA", "attach_rate", 300, n=1000, item="a")
_obs("cA", "attach_rate", 250, n=1000, item="a")
va = core.verdict(ea)
ok(va["verdict"] == "PROBABLE", f"proportion fixture verdict {va['verdict']} (want PROBABLE)")
ok(va["lift_pct"] == 20.0, f"lift hand-checked: {va['lift_pct']} == 20.0")
ok(va["z"] == 2.5, f"z hand-checked: {va['z']} == 2.5")
ok(va["direction"] == "treatment ahead", "direction reads treatment ahead")
ok("two-proportion z" in va["method"], "the method is stated")
# a clearly separated pair: 400/1000 vs 250/1000 → lift 60.0%, z 7.16 → CLEAR
eb = _exp("attach_rate", ["tB"], ["cB"], item="b")
_obs("tB", "attach_rate", 400, n=1000, item="b")
_obs("cB", "attach_rate", 250, n=1000, item="b")
vb = core.verdict(eb)
ok(vb["verdict"] == "CLEAR" and vb["lift_pct"] == 60.0 and vb["z"] == 7.16,
   f"clear proportion fixture hand-checked (got {vb['verdict']}, {vb['lift_pct']}, {vb['z']})")
# means fixture: 30 unit-days per arm, means 24 vs 20 → diff 4.0, lift 20.0%, z 10.77
ec = _exp("item_units", ["tC"], ["cC"], item="c")
for i in range(30):
    _obs("tC", "item_units", [22, 23, 24, 25, 26][i % 5], item="c")
    _obs("cC", "item_units", [18, 19, 20, 21, 22][i % 5], item="c")
vc = core.verdict(ec)
ok(vc["verdict"] == "CLEAR", "means fixture reads CLEAR")
ok(vc["diff"] == 4.0 and vc["lift_pct"] == 20.0, f"means diff/lift hand-checked ({vc['diff']}, {vc['lift_pct']})")
ok(vc["z"] == 10.77, f"means z hand-checked: {vc['z']} == 10.77")
ok("Welch" in vc["method"], "the means method is stated")
# the seeded conclusions froze honestly
sc = store.by_id("experiments", "exp_demo_clear")["verdict"]
ok(sc["verdict"] == "CLEAR" and sc["direction"] == "treatment ahead",
   "seeded bundle test froze CLEAR, treatment ahead")
ok(sc["diff"] == 1.1 and sc["lift_pct"] == 7.0,
   f"seeded CLEAR lift hand-checked ({sc['diff']}, {sc['lift_pct']})")
ok(sc["z"] is not None and sc["z"] >= 2.6, "seeded CLEAR z at or above the CLEAR line")
sn = store.by_id("experiments", "exp_demo_noise")["verdict"]
ok(sn["verdict"] == "NOISE", "seeded menu-board test froze NOISE")

print("== one lever per dial ==")
r = core.create_experiment("louder guac prompt", "attach_rate", ["u_elm"], ["u_north"],
                           item="guacamole")
ok("refused" in r and "one lever per dial" in r["refused"],
   "same metric + shared unit refused at creation")
ok(r.get("clashes_with") == "exp_demo_live", "the refusal names the clashing experiment")
ok(any(e["kind"] == "refused"
       and (e.get("detail") or {}).get("action") == "overlapping_experiments_same_metric"
       for e in store.events()), "overlap refusal logged")
r1 = core.create_experiment("bowl portion test", "item_units", ["u_elm"], ["u_depot"],
                            item="finch bowl")
ok("experiment" in r1, "different metric, same units — allowed")
r2 = core.create_experiment("bowl portion test B", "item_units", ["u_river"], ["u_campus"],
                            item="finch bowl")
ok("refused" not in r2 or "experiment" in r2, "same metric, disjoint units — allowed")
r3 = core.create_experiment("bowl portion test C", "item_units", ["u_river"], ["u_north"],
                            item="finch bowl")
ok("refused" in r3 and "one lever per dial" in r3["refused"],
   "same metric, shared unit with a live test — refused")
ok("refused" in core.create_experiment("no control", "item_units", ["u_elm"], []),
   "an experiment with no control arm refused")
ok("refused" in core.create_experiment("both arms", "item_units", ["u_elm"], ["u_elm"]),
   "a unit in both arms refused")
ok(r1["experiment"]["min_sample"]["n"] == 28
   and "_source" in r1["experiment"]["min_sample"], "the floor is recorded ON the experiment")

print("== the rollout gate, both ways ==")
r = core.rollout("exp_demo_live")
ok("refused" in r and "no path" in r["refused"], "rolling out a live experiment has no path")
ok("TOO EARLY" in r["refused"], "the refusal quotes the current read")
r = core.rollout("exp_demo_noise")
ok("refused" in r and "no path" in r["refused"], "rolling out concluded NOISE has no path")
ok("institutionalizes luck" in r["refused"], "the refusal says why")
ok(sum(1 for e in store.events()
       if e["kind"] == "refused"
       and (e.get("detail") or {}).get("action") == "rollout_unconcluded_experiment") >= 2,
   "rollout refusals logged")
r = core.rollout("exp_demo_clear")
ok(r.get("drafted") and r["gate"]["rung"] == "R1", "concluded CLEAR drafts a rollout at R1")
ok(r["stats_attached"]["verdict"] == "CLEAR" and r["stats_attached"]["lift_pct"] == 7.0,
   "the full stats ride with the draft")
ap = [a for a in store.load("approvals")
      if a["action"] == "draft_rollout_recommendation" and a["state"] == "pending"]
ok(len(ap) == 1 and (ap[0]["detail"].get("stats") or {}).get("verdict") == "CLEAR",
   "the approval row carries the stats")

print("== the 86 ledger, priced from own pace ==")
so = store.by_id("stockouts", "so_demo_friday")
p = core.price_stockout(so)
ok(p["cost"] == 280.0, f"hand-checked: median 8 × 2.5h × $14 = 280 (got {p['cost']})")
ok(p["pace_units_per_hour"] == 8 and p["pace_n"] == 5, "the pace is the recorded median of 5 readings")
ok("own" in p["basis"] and "never an industry average" in p["basis"], "the basis names its source")
paceless = {"id": "so_test_pl", "unit_id": "u_elm", "item": "street corn esquites",
            "daypart": "dinner", "duration_hours": 2.0, "at": iso()}
pp = core.price_stockout(paceless)
ok(pp["cost"] is None and "no recorded sales pace" in pp["_missing"],
   "no pace history → unmeasured, never estimated")
ok("counted, not dollared" in pp["_missing"], "the refusal states the rule")
base = core.eightysix_counted(7)
rows = store.load("stockouts")
rows.append({"id": "so_test_add", "unit_id": "u_river", "item": "brisket plate",
             "daypart": "dinner", "duration_hours": 1.0, "at": iso()})
store.save("stockouts", rows)
after = core.eightysix_counted(7)
ok(round(after["dollared"] - base["dollared"], 2) == 112.0,
   f"a new 1h brisket 86 adds exactly 8×1×14=112 to the counted week "
   f"(delta {round(after['dollared'] - base['dollared'], 2)})")
ok(after["priced"] == base["priced"] + 1, "priced count moves by one")
rows = store.load("stockouts")
rows.append({"id": "so_test_pl2", "unit_id": "u_elm", "item": "street corn esquites",
             "daypart": "lunch", "duration_hours": 4.0, "at": iso()})
store.save("stockouts", rows)
after2 = core.eightysix_counted(7)
ok(after2["dollared"] == after["dollared"] and after2["unmeasured"] == after["unmeasured"] + 1,
   "a paceless 86 moves the unmeasured count, never the dollars")
rows = store.load("stockouts")
rows.append({"id": "so_test_demo", "unit_id": "u_river", "item": "brisket plate",
             "daypart": "dinner", "duration_hours": 5.0, "at": iso(), "demo_tag": "demo"})
store.save("stockouts", rows)
ok(core.eightysix_counted(7)["dollared"] == after2["dollared"],
   "demo fixtures never enter the counted 86 board")
lb = core.ledger_board()
ok(any(r.get("_missing") for r in lb["rows"]), "the ledger renders unmeasured rows as such")
ok("note" in lb["week"] and "counted" in lb["week"]["note"], "the week total names its basis")

print("== the illness protocol: verbatim, never answered ==")
out = agents.handle_message("ms_demo_illness")
step = out["steps"][0]
ok(step["action"] == "escalate_illness", "the illness claim escalates")
ok("draft" not in step, "NO written reply is drafted — ever")
ok(all("draft" not in s for s in out["steps"]), "no step around it drafts either")
ok("counsel" in step["refused"], "the human + counsel path is named")
inc = store.by_id("incidents", step["incident"])
ok(inc["verbatim"] == "your tacos made me sick last night and I want to talk to someone",
   "the claim is logged verbatim")
ok(any(e["kind"] == "refused"
       and (e.get("detail") or {}).get("action") == "answer_illness_claim"
       for e in store.events()), "answer_illness_claim refused + logged")
ok(any(e["kind"] == "escalate_illness" and e.get("rung") == "R2"
       for e in store.events()), "the escalation ran at R2 — it never queued")
m = store.by_id("messages", "ms_demo_illness")
ok(not m.get("draft_reply"), "no draft_reply lands on the illness message")

print("== the GM ask: the verdict quoted, TOO EARLY included ==")
out = agents.handle_message("ms_demo_gm")
body = out["steps"][0]["draft"]
ok("TOO EARLY TO KNOW" in body, "the draft quotes the TOO EARLY verdict verbatim")
ok("no winner to report" in body, "the draft explains the floor honestly")
ok("CLEAR" in body and "7.0%" in body, "the concluded CLEAR result is cited with its lift")
ok("yourco" not in body.lower(), "white-label")
out = agents.handle_message("ms_demo_proposal")
ok("one lever per dial" in out["steps"][0]["draft"], "the proposal ack names the overlap rule")
out = agents.handle_message("ms_demo_86")
ok(out["steps"][0]["action"] == "log_stockout", "the 86 report logs to the ledger")
ok(any(e["kind"] == "log_stockout" and e.get("rung") == "R2" for e in store.events()),
   "log_stockout ran at R2")

print("== sweeps skip demo fixtures ==")
msgs = store.load("messages")
msgs.append({"id": "ms_test_demo", "from": "guest-x", "demo_tag": "demo",
             "text": "who's winning the guac test", "at": iso()})
store.save("messages", msgs)
r = agents.run_all()
ok(r["messages"]["handled"] >= 10, "routine messages handled by the sweep")
ok(not store.by_id("messages", "ms_test_demo").get("handled_at"),
   "a demo_tag message is skipped by the sweep — it exists for the hand walk-through")
ok(agents.handle_message("ms_test_demo")["steps"][0]["action"] == "draft_gm_result_reply",
   "the same demo row still handles by hand")

print("== matrix: the R0s never promote, never approve ==")
for a in ("conclude_below_sample_floor", "rollout_unconcluded_experiment",
          "overlapping_experiments_same_metric", "answer_illness_claim",
          "estimate_counterfactual_without_pace"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
    pr = core.gate.act(a, "probe", "x", {})
    ok(pr.get("refused") and not pr.get("executed"), f"R0 probe {a} refused")
    ok(not any(row["action"] == a and row["state"] == "pending"
               for row in store.load("approvals")),
       f"{a} never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no illness claim missed")
ok(ev["costly_label"] == "illness", "the costly label is the illness claim")
ok("ADMISSION IN A FUTURE LAWSUIT" in ev["costly_note"], "the costly note names the stake")
ok(ev["n"] >= 15, "15+ labelled cases")

print("== roi, typed ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(r["recorded"]["clear_lift_per_ticket"] == 1.1,
   "the CLEAR lift $/ticket is counted from the frozen verdict")
ok("eightysix_cost_28d" in r["recorded"], "the 86 cost is counted from the ledger")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["Winning-experiment lift"]["kind"] == "revenue", "the lift line is revenue")
ok(labels["The bad rollout avoided"]["kind"] == "scenario", "the avoided rollout is a scenario")
ok(labels["The bad rollout avoided"]["value"] is None
   and labels["The bad rollout avoided"].get("_missing"),
   "the scenario line renders blank until the operator decides it")
ok(labels["Owner analysis hours"]["kind"] == "time_saved", "analysis hours are time_saved")
ok(r["totals"]["scenario"]["total"] is None, "no scenario subtotal is invented")

print("== the counted week, by delta ==")
base = core.week_counted()
store.log_event("draft_gm_result_reply", "ms_demo_gm", "human:owner", "R1", {})
store.log_event("escalate_illness", "inc_x", "agent:intake", "R2", {})
after = core.week_counted()
ok(after["gm_replies_sent"] == base["gm_replies_sent"] + 1, "human GM replies counted")
ok(after["illness_escalated"] == base["illness_escalated"] + 1, "illness escalations counted")
ok(after["experiments_concluded"] >= 1, "this week's conclusions counted")
ok("counted" in after["note"], "the week names its basis")

print("== the log is append-only ==")
evs = store.events()
first_id = evs[0]["id"]
n0 = len(evs)
store.log_event("note", "x", "human:test", None, {})
evs2 = store.events()
ok(len(evs2) == n0 + 1, "an event appends")
ok(evs2[0]["id"] == first_id, "history does not move")

print("== automation, counted or refused ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted from the log or refused with a reason")

print("== white-label ==")
html = (Path(__file__).parent / "app" / "index.html").read_text()
ok("yourco" not in html.lower(), "no yourco on the client surface")
ok("Blue Finch" not in html, "the UI takes the company name from config, not hardcode")
ok("yourco" not in agents._desk_ack({}).lower(), "desk ack white-label")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
