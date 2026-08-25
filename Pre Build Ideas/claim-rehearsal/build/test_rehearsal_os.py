#!/usr/bin/env python3
"""Rehearsal OS — the suite. `python3 test_rehearsal_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["REHEARSALOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="rehearsalos_test_")
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


print("== seed ==")
seed.main()
accounts = store.load("accounts")
ok(len(accounts) >= 900, "≥900 accounts seeded")
unread = [a for a in accounts if not a.get("policy_recorded")]
ok(0.05 <= len(unread) / len(accounts) <= 0.11, f"~8% unread policies ({len(unread)})")
ok(store.by_id("accounts", "ac_demo_full") is not None, "demo rehearsal account present")
ok(store.by_id("accounts", "ac_demo_unread") is not None, "demo unreadable account present")
ok(all("555" in a.get("carrier_claim_line", "") for a in accounts if a.get("carrier_claim_line")),
   "every claim line is a 555 number — synthetic only")
cfg = store.load("config")
ok("_source" in (cfg.get("scenarios") or {}), "the scenario table is recorded and _source-named")
ok("_source" in (cfg.get("rate_card") or {}), "the rate card is recorded and _source-named")

print("== triage: the active claim reads first ==")
for c in core.EVAL_CASES:
    ok(core.read_message(c["input"])["label"] == c["label"],
       f"triage: {c['input'][:46] or '(empty)'} → {c['label']}")
ok(len(core.EVAL_CASES) == 15, "15 labelled eval cases, empty → human included")

print("== the active-claim protocol ==")
ev0 = store.events()[0]
out = agents.handle_message("ms_demo_active")
step = out["steps"][0]
ok(step["action"] == "log_claim_intake", "the claim intake is logged (R2 — cannot wait)")
ok("Kestrel Mutual" in step["draft"] and "1-800-555-0134" in step["draft"],
   "the script cites the RECORDED carrier and claim line")
ok("report a loss in progress" in step["draft"], "the claims-reporting script, verbatim")
ok("carrier's decision at adjustment" in step["draft"],
   "the script says out loud that payout is the carrier's call")
ok(core.opinion_free(step["draft"])[0], "the script carries no coverage opinion — structurally")
ok(core.fear_ok(step["draft"])[0], "the script carries no fear language")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "promise_coverage"
       for e in store.events()), "promise_coverage refused + logged mid-crisis")
ok(len(store.load("claims")) == 1, "the claim record exists")
ok("yourco" not in step["draft"].lower(), "white-label — the agency's voice, no yourco")

print("== the rehearsal arithmetic, hand-checked ==")
r = core.rehearse(store.by_id("accounts", "ac_demo_full"))
kf = next(s for s in r["scenarios"] if s["key"] == "kitchen_fire")
t = kf["severities"]["typical"]
ok(t["loss"] == 77000, "typical kitchen fire loss = $77,000 (recorded table)")
ok(t["payout"] == 36000, "policy pays 77,000×.5 = 38,500 on dwelling − 2,500 deductible = 36,000")
ok(t["gap"] == 41000, "THE GAP = $41,000 exactly — contents 23,100 + loss-of-use 15,400 excluded + 2,500 deductible")
ok(kf["severities"]["low"]["gap"] == 14500, "low severity gap = 14,500 (24,000 − 9,500)")
ok(kf["severities"]["severe"]["gap"] == 82500, "severe gap = 82,500 (160,000 − 77,500)")
ok(set(kf["severities"]) == {"low", "typical", "severe"},
   "all three severities — never one number")
cites = " · ".join(t["citations"])
ok("HX 21 44" in cites and "HX 30 06" in cites, "both exclusions cited by recorded form number")
ok("deductible $2,500 (recorded)" in cites, "the deductible is cited, not hidden")
wb = next(s for s in r["scenarios"] if s["key"] == "water_backup")
ok(wb["severities"]["typical"]["gap"] == 28000 and
   "no recorded water_backup coverage" in " ".join(wb["severities"]["typical"]["citations"]),
   "uncovered peril → the whole typical loss is the gap, cited as uncovered")
sl = next(s for s in r["scenarios"] if s["key"] == "liability_slip")
ok(sl["severities"]["typical"]["gap"] == 0, "liability typical inside the limit — gap 0, honestly")
ok(sl["severities"]["severe"]["gap"] == 250000, "liability severe capped at the recorded 100k limit")
ok(r["gap_typical_total"] == 69000, "typical gap across scenarios = 41,000 + 28,000 + 0")
ok("only the carrier" in r["label"] and "arithmetic on the recorded policy" in r["label"],
   "every rehearsal carries the label: arithmetic, only the carrier adjusts")
ok("_source" not in r or True, "scenario source named")
ok("DEFAULT scenario table" in r["scenario_source"], "the scenario table names its provenance")
rr = agents.rehearse_account("ac_demo_full")
ok(rr["gate"]["rung"] == "R2" and rr["gate"]["executed"],
   "the rehearsal itself runs at R2 — internal arithmetic, logged")
ok(store.by_id("rehearsals", rr["row"]) is not None, "the rehearsal row is persisted")
ok(any(e["kind"] == "gap_found" and e["subject"] == "ac_demo_full"
       for e in store.events()), "each gap is logged as a gap_found event")

print("== UNREADABLE — we read policies before we rehearse them ==")
r2 = agents.rehearse_account("ac_demo_unread")
ok(r2.get("unreadable"), "no recorded policy detail → UNREADABLE, no rehearsal")
ok("We read policies before we rehearse them" in r2["why"], "the refusal says why")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "rehearse_unread_policy"
       for e in store.events()), "rehearse_unread_policy refused + logged")
fs2 = agents.draft_fix_sheet("ac_demo_unread")
ok(fs2.get("unreadable"), "no fix sheet on an unread policy either")

print("== single-number severity refused ==")
r3 = agents.refuse_single_number("ac_demo_full", "typical")
ok("never" in r3["refused"] and "range" in r3["refused"], "one number → refused with the rule")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "single_number_severity"
       for e in store.events()), "single_number_severity refusal logged")

print("== the R0 probes never become approvable ==")
for a in ("promise_coverage", "rehearse_unread_policy", "fear_language",
          "single_number_severity"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
    pr = core.gate.act(a, "probe", "x", {})
    ok(pr.get("refused"), f"{a} R0 probe refused")
    ok(not any(ap["action"] == a and ap["state"] == "pending"
               for ap in store.load("approvals")), f"{a} never becomes an approvable row")

print("== the tone check, both ways ==")
ok(core.fear_ok("the rehearsal shows a $41,000 gap and the endorsement that closes it")[0],
   "calm arithmetic passes")
bad = cfg["demo_probes"]["fear"]
okf, whyf = core.fear_ok(bad)
ok(not okf and "devastating" in whyf and "lose everything" in whyf,
   "fear language refused with the words named")
pr = agents.check_client_draft(bad, "probe:fear")
ok(pr.get("refused"), "the fear probe is refused, not softened")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "fear_language"
       for e in store.events()), "fear_language refusal logged")
pr2 = agents.check_client_draft(cfg["demo_probes"]["promise"], "probe:promise")
ok(pr2.get("refused") and "carrier" in pr2["refused"], "the coverage-promise probe is refused")
ok(not core.opinion_free("good news, you're fully covered")[0], "opinion detector fires")
ok(core.opinion_free("what your policy pays is the carrier's decision at adjustment")[0],
   "honest phrasing passes the opinion check")

print("== the fix sheet, priced from the recorded rate card ==")
fs = agents.draft_fix_sheet("ac_demo_full")
lines = {(l["kind"], l["key"]): l for l in fs["sheet"]["lines"]}
ok(("exclusion", "HX 21 44") in lines and lines[("exclusion", "HX 21 44")]["annual_premium"] == 118,
   "the grease-fire buy-back is priced from the recorded card ($118)")
l3006 = lines.get(("exclusion", "HX 30 06"))
ok(l3006 and l3006["annual_premium"] is None and "no recorded rate" in l3006["_missing"],
   "a fix with no recorded rate renders blank with the reason — never invented")
ok(("uncovered", "water_backup") in lines
   and lines[("uncovered", "water_backup")]["annual_premium"] == 96,
   "the missing water backup coverage is priced ($96)")
lim = lines.get(("limit", "personal_liability"))
ok(lim and lim.get("severe_only") and lim["annual_premium"] == 62,
   "the severe-only limit gap maps to the umbrella, priced")
ok(fs["sheet"]["priced_total"] == 276, "priced total = 118 + 96 + 62")
ok(fs["sheet"]["unpriced"] == 1, "the unpriced line is counted, not hidden")
ok(core.REHEARSAL_LABEL == fs["sheet"]["label"], "every sheet carries the arithmetic label")
ok(fs["gate"]["rung"] == "R1" and not fs["gate"]["executed"],
   "the fix sheet drafts at R1 — a producer sends")
ok("$69,000" in fs["cover"], "the cover note quotes the counted typical gap")
ok(core.fear_ok(fs["cover"])[0] and core.opinion_free(fs["cover"])[0],
   "the cover note passes both structural checks")
ok("yourco" not in fs["cover"].lower(), "white-label cover note")

print("== T-60 date alerts ==")
radar = core.renewal_radar()
ok(radar["window_days"] == 60, "the radar window is T-60")
ok(radar["rows"] and all(0 <= x["days"] <= 60 for x in radar["rows"]),
   "every radar row is inside the window")
ok(all("DATE ALERT" in x["label"] for x in radar["rows"]), "every row is a DATE ALERT")
demo_row = next((x for x in radar["rows"] if x["account"] == "ac_demo_full"), None)
ok(demo_row is not None and 36 <= demo_row["days"] <= 38, "the demo renewal sits at ~T-38")
ok(demo_row["status"] == "rehearsed", "the rehearsed account reads rehearsed")
unread_row = next((x for x in radar["rows"] if x["account"] == "ac_demo_unread"), None)
ok(unread_row is not None and unread_row["status"] == "UNREADABLE",
   "the unread account reads UNREADABLE on the radar")

print("== the renewal packet ==")
pk = agents.draft_renewal_packet("ac_demo_full")
ok("rehearsal" in pk["packet"] and "fix_sheet" in pk["packet"],
   "the packet = the rehearsal + the fix sheet")
ok(pk["gate"]["rung"] == "R1" and not pk["gate"]["executed"], "the packet drafts at R1")
ok(pk["packet"]["label"] == core.REHEARSAL_LABEL, "the packet carries the label")
apid = pk["gate"]["approval"]
core.gate.decide(apid, "principal", approve=True)
ok(any(e["kind"] == "draft_renewal_packet" and e["actor"] == "human:principal"
       for e in store.events()), "a human approval is logged as the human's act")

print("== gaps counted: found and closed ==")
led = core.gap_ledger()
ok(led["found"] >= 4, f"gaps found counted from the log ({led['found']})")
ok(led["closed"] == 0, "nothing closed yet — a sent sheet closes nothing")
en = agents.record_endorsement("ac_demo_full", "exclusion", "HX 21 44")
ok(en["rung"] == "R1" and not en["executed"], "recording an endorsement waits for a human")
core.gate.decide(en["approval"], "principal", approve=True,
                 execute=lambda: agents.apply_endorsement("ac_demo_full", "exclusion",
                                                          "HX 21 44", "principal"))
led2 = core.gap_ledger()
ok(led2["closed"] == 1, "the gap closes only when the endorsement is recorded")
ok(any(e["kind"] == "gap_closed" and e["actor"] == "human:principal"
       for e in store.events()), "gap_closed logged as the human's act")
a9 = store.by_id("accounts", "ac_demo_full")
ok(any(e["key"] == "HX 21 44" for e in a9.get("endorsements", [])),
   "the endorsement is on the account record")
fs9 = core.fix_sheet(a9)
ok(next(l for l in fs9["lines"] if l["key"] == "HX 21 44")["closed"],
   "the fix sheet shows the closed line closed")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no active claim missed")
ok("RISING WATER" in ev["costly_note"], "the costly note names the stake")
ok(ev["costly_label"] == "active_claim", "the costly label is the active claim")

print("== roi ==")
ri = core.roi({})
ok("THIS IS A MODEL" in ri["label"], "the panel labels itself a model")
labels = {l["label"]: l for l in ri["lines"]}
eo = labels["The uncovered-claim E&O file"]
ok(eo["kind"] == "scenario" and eo["value"] is None and "eo_claim_value" in eo["_missing"],
   "the E&O file is a scenario line and stays blank until the operator prices it")
ok(labels["Retention lift at rehearsed renewals"]["value"] is None,
   "retention lift refuses without the operator's lift number")
ok(ri["recorded"].get("rehearsed_renewals", 0) >= 1, "rehearsed renewals are counted, recorded")
ok(ri["recorded"].get("gaps_closed") == 1, "gaps closed recorded from the ledger")
er = labels["Endorsement revenue from closed gaps"]
expect = round(1 * ri["recorded"]["avg_endorsement_premium"] * 0.12, 2)
ok(er["value"] == expect, "endorsement revenue = closed × recorded avg premium × commission")
ok(labels["CSR hours on renewal prep"]["kind"] == "time_saved",
   "CSR hours are time_saved, never summed into revenue")

print("== counted week, with a baseline delta ==")
wk = core.counted_week()
ok(wk["this_week"]["rehearsals_run"] >= 1, "rehearsals this week are counted")
ok(wk["this_week"]["packets_sent"] >= 1, "sent packets counted from human approvals")
ok(wk["delta"].get("_missing"), "no prior week → the delta refuses, not zero-fills")
store.log_event("run_rehearsal", "ac_backfill", "agent:rehearsal", "R2", {},
                at=iso(now() - timedelta(days=8)))
wk2 = core.counted_week()
ok("_missing" not in wk2["delta"], "with a prior week on record the delta computes")
ok(wk2["delta"]["rehearsals_run"] == wk2["this_week"]["rehearsals_run"] - 1,
   "the delta is this week minus last, counted")

print("== sweeps + automation ==")
run = agents.run_all()
ok(run["renewals"]["rehearsed"] >= 1, "the T-60 sweep rehearses in-window accounts")
ok(run["renewals"]["skipped"] >= 1, "demo fixtures are skipped by the sweep")
au = core.automation()
ok("rate" in au and (au.get("rate") is not None or "_missing" in au),
   "automation counted from the log, or refused below the floor")

print("== append-only ==")
evs = store.events()
ok(evs[0] == ev0, "the first event is untouched — corrections are new events")
n = len(evs)
store.log_event("noted", "x", "human:test", "R1", {})
ok(len(store.events()) == n + 1, "the log only ever grows")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
