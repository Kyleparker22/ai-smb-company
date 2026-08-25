#!/usr/bin/env python3
"""Remit OS — the suite. `python3 test_remit_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["REMITOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="remitos_test_")
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
ok(sum(len(r["lines"]) for r in store.load("remits")) >= 400, "400+ remittance lines seeded")
cs = core.contracts()
ok("CareMax Rx" in cs and "OptiScript" in cs, "two PBM contracts recorded")
ok("Pinnacle Health Rx" not in cs, "one PBM deliberately unrecorded")
ok(core.unauditable_pbms() == ["Pinnacle Health Rx"], "the unrecorded PBM is named")
acq = store.load("config")["acquisition"]["costs"]
ok("Velotrix 25mg" not in acq and "Duloxetine 30mg" not in acq,
   "some acquisition costs deliberately unrecorded")

print("== triage: the wrong-pills message reads first ==")
for text, want in (("i think i got the wrong pills", "wrong_med"),
                   ("these pills don't look like my usual ones", "wrong_med"),
                   ("the bottle has someone else's name on it", "wrong_med"),
                   ("the label says a medication i have never taken", "wrong_med"),
                   ("i think these are someone else's pills", "wrong_med"),
                   ("grandma got a capsule that looks wrong", "wrong_med"),
                   ("my insurance rejected the refill and says prior authorization is needed",
                    "pbm_question"),
                   ("the pbm says this drug is not covered anymore", "pbm_question"),
                   ("insurance says you billed the wrong plan", "pbm_question"),
                   ("why did my copay double this month", "price_complaint"),
                   ("you charged me more than last time", "price_complaint"),
                   ("this prescription got way more expensive", "price_complaint"),
                   ("can i get a refill on my lisinopril", "refill"),
                   ("is my refill ready for pickup", "refill"),
                   ("", "human"),
                   ("what time do you close on sunday", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44] or '(empty)'} → {want}")

print("== the wrong-pills protocol ==")
out = agents.handle_message("ms_demo_wrongmed")
step = out["steps"][0]
ok(step["action"] == "pharmacist_now", "the wrong-pills message goes to the pharmacist NOW")
ok(step["draft"] == core.PHARMACIST_NOW, "the fixed script is the whole reply, verbatim")
ok("do NOT take anything" in step["draft"] and "interrupted right now" in step["draft"],
   "the script stops the patient and interrupts the pharmacist")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "wrong_med_message_queued"
       for e in store.events()), "wrong_med_message_queued refused + logged")
ok(step["gate"]["executed"] and step["gate"]["rung"] == "R2",
   "the reply executes at R2 — safety never waits for a click")
ok(not any(a["action"] == "pharmacist_now_reply" and a["state"] == "pending"
           for a in store.load("approvals")), "the reply never sat in a queue")
ok("yourco" not in step["draft"].lower(), "white-label — no yourco in the reply")

print("== the contract arithmetic, hand-checked ==")
rm = store.by_id("remits", "rm_cm_01")
c = core.contracts()["CareMax Rx"]
big = next(l for l in rm["lines"] if l["script_ref"] == "RX-88214")
al = core.autopsy_line(big, c)
ok(al["expected"] == 378.65, f"expected 14.80×30×0.85 + 1.25 = 378.65 (got {al['expected']})")
ok(al["delta"] == 212.47, f"delta to the cent: 212.47 (got {al['delta']})")
ok(al["class"] == "underpaid", "the big line classes underpaid")
ok("§3.1" in al["clause"], "the clause is cited")
ok("to the cent" in al["why"], "the why states the delta to the cent")

print("== DIR drift ==")
dirl = next(l for l in rm["lines"] if l["script_ref"] == "RX-77103")
al2 = core.autopsy_line(dirl, c)
ok(al2["class"] == "dir_drift", "over-withheld DIR classes dir_drift")
ok(al2["delta"] == 5.25, f"DIR drift to the cent: 5.25 (got {al2['delta']})")
ok("§5.4" in al2["why"], "the DIR clause is cited")

print("== correct lines and the MAC basis ==")
corr = next(l for l in rm["lines"]
            if l["script_ref"] not in ("RX-88214", "RX-77103")
            and core.autopsy_line(l, c)["class"] == "correct")
ok(core.autopsy_line(corr, c)["delta"] == 0.0, "a correct line shows zero delta")
osrm = store.by_id("remits", "rm_os_01")
osc = core.contracts()["OptiScript"]
met = next(l for l in osrm["lines"] if l["drug"] == "Metformin 500mg")
alm = core.autopsy_line(met, osc)
ok("Exhibit B" in alm["clause"], "a MAC-list generic prices from the MAC clause")

print("== the ambiguous clause — both readings to a human ==")
amb = next(l for l in osrm["lines"] if l["script_ref"] == "RX-90455")
ala = core.autopsy_line(amb, osc)
ok(ala["class"] == "ambiguous", "brand-on-MAC classes ambiguous")
ok(len(ala["readings"]) == 2, "BOTH readings are output")
ok("§4.1" in ala["readings"][0]["clause"] and "Exhibit B" in ala["readings"][1]["clause"],
   "each reading cites its own clause")
ok(ala["readings"][0]["expected"] == 315.73 and ala["readings"][1]["expected"] == 126.85,
   "both readings computed to the cent")
ok("human" in ala["why"].lower() and ala["route"] == "human",
   "an ambiguous line routes to a human, never auto-resolved")

print("== the UNAUDITABLE refusal ==")
r = core.autopsy("rm_px_01")
ok(r.get("unauditable") and "UNAUDITABLE" in r["refused"], "no recorded contract → UNAUDITABLE")
ok("Pinnacle Health Rx" in r["refused"], "the gap names the PBM")
ok("rate basis" in r["refused"] and "appeal window" in r["refused"],
   "the refusal names what to record")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "audit_without_recorded_contract"
       for e in store.events()), "audit_without_recorded_contract logged at R0")

print("== the autopsy sweep + recoverable ledger ==")
sw = agents.autopsy_sweep()
ok(sw["audited"] == 3 and "Pinnacle Health Rx" in sw["unauditable"],
   "sweep audits the recorded PBMs and refuses the unrecorded one")
ok(sw["flagged"] >= 40, f"variances land in the ledger ({sw['flagged']} flagged)")
ok(not any(f["pbm"] == "Pinnacle Health Rx" for f in store.load("findings")),
   "no findings ever invented for the unauditable PBM")
lg = core.ledger()
ok(lg["open_recoverable"] > 200, "open recoverable is counted in dollars")
row = next(x for x in lg["rows"] if x["id"] == "fd_rm_cm_01_RX-88214")
ok(row["days_left"] == 78, "aged against the contract's own 90-day window")
ok("DATE ALERT" in row["label"], "the window is a DATE ALERT, not legal advice")
exp_row = next(x for x in lg["rows"] if x["id"] == "fd_rm_demo_expired_RX-99001")
ok(exp_row["expired"] and exp_row["days_left"] < 0, "the lapsed demo window reads expired")
ok(all(x.get("delta") is None for x in lg["rows"] if x["class"] == "ambiguous"),
   "an ambiguous row carries no delta until a human resolves it")

print("== the appeal draft — clause + delta, R1, PHI-scrubbed ==")
r = agents.draft_appeal("fd_rm_cm_01_RX-88214")
ok("§3.1" in r["draft"] and "$212.47" in r["draft"], "the appeal cites the clause and the delta")
ok("$378.65" in r["draft"] and "$166.18" in r["draft"], "expected and paid both quoted")
ok(r["gate"]["rung"] == "R1" and r["gate"].get("approval"),
   "the appeal queues at R1 — a human sends")
ok(core.phi_scrub_ok(r["draft"], big)[0], "the draft passes the scrub against its source line")
ok("Marisol" not in r["draft"] and "Vance" not in r["draft"],
   "the patient's name never reaches the PBM")
ok("(555)" not in r["draft"], "the patient's phone never reaches the PBM")
ok("yourco" not in r["draft"].lower(), "white-label — no yourco in the appeal")
f88 = store.by_id("findings", "fd_rm_cm_01_RX-88214")
ok("patient" not in f88 and "patient_phone" not in f88,
   "the finding itself is built from the whitelist — identifiers never enter it")
r = agents.draft_appeal("fd_rm_os_01_RX-90455")
ok("refused" in r and "readings" in r, "an ambiguous line cannot be appealed — both readings shown")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "auto_resolve_ambiguous_clause"
       for e in store.events()), "auto_resolve_ambiguous_clause logged")

print("== PHI scrub, planted ==")
ok(not core.phi_scrub_ok("patient SSN 123-45-6789 attached")[0], "a planted SSN fails")
ok(not core.phi_scrub_ok("patient DOB 4/12/1961, script RX-60001")[0], "a planted DOB fails")
ok(not core.phi_scrub_ok("call her at (555) 014-7212")[0], "a planted phone fails")
ok(not core.phi_scrub_ok("regarding Marisol Vance's fill", {"patient": "Marisol Vance"})[0],
   "a planted patient name fails against the source line")
ok(core.phi_scrub_ok("Re: remittance rm_cm_01, script RX-88214, short $212.47")[0],
   "a clean script reference passes")

print("== resolving the ambiguity — a human act ==")
r = agents.resolve_ambiguous("fd_rm_os_01_RX-90456")
ok("refused" in r and len(r["readings"]) == 2,
   "no human → refused, with both readings shown again")
r = agents.resolve_ambiguous("fd_rm_os_01_RX-90456", reading=0, human="owner")
ok(r.get("resolved") and r["finding"]["class"] == "underpaid",
   "a human picks the §4.1 reading — the line reclasses underpaid")
ok(r["finding"]["delta"] == 188.88, f"the resolved delta is exact (got {r['finding']['delta']})")
ok(any(e["kind"] == "ambiguous_resolved" and e["actor"] == "human:owner"
       for e in store.events()), "the resolution is logged to the human")

print("== recovered = counted corrections only ==")
base = core.recovered()
ok(base["recovered"] == 0 and "counted" in base["note"], "nothing recovered until it is counted")
r = core.estimate_recovered()
ok("refused" in r and r["gate"].get("refused"), "the estimate probe is refused at R0")
ok(not any(a["action"] == "estimate_recovered_dollars" and a["state"] == "pending"
           for a in store.load("approvals")), "the estimate never becomes an approvable row")
r = agents.record_correction("fd_rm_cm_01_RX-88214", amount=212.47)
ok("refused" in r, "no human → no correction; it is never assumed")
r = agents.record_correction("fd_rm_cm_01_RX-88214", amount=212.47, human="owner")
ok(r.get("corrected"), "a human posts the PBM's corrected remittance")
rec = core.recovered()
ok(rec["recovered"] == 212.47 and rec["corrections"] == 1,
   "recovered is the counted correction, to the cent")

print("== the margin truth board ==")
mb = core.margin_board()
ok(mb["loss_count"] > 0 and mb["loss_dollars"] < 0, "the dispensed-at-a-loss list is counted")
ok(any(r["drug"] == "Metformin 500mg" for r in mb["loss_rows"]),
   "MAC below acquisition shows as a counted loss")
ok(mb["unmeasured"]["lines"] > 0 and "Velotrix 25mg" in mb["unmeasured"]["drugs"],
   "no recorded acquisition cost → unmeasured, drug named")
ok("_missing" in mb["unmeasured"] and "never assumed" in mb["unmeasured"]["_missing"],
   "unmeasured states its reason")
ok(not any(r["script_ref"] == "RX-99001" for r in mb["loss_rows"]),
   "demo-tagged remits stay out of the counted board")

print("== the appeal-window sweep ==")
ws = agents.window_sweep()
ok(ws["alerts"] >= 1, "the lapsed window raises a DATE ALERT")
ok(any(e["kind"] == "appeal_window_alert" and "CLOSED" in (e["detail"] or {}).get("summary", "")
       for e in store.events()), "the alert names the closed window")

print("== matrix ==")
for a in ("wrong_med_message_queued", "audit_without_recorded_contract",
          "auto_resolve_ambiguous_clause", "estimate_recovered_dollars", "phi_in_outbound"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("phi_in_outbound", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
r = core.gate.act("audit_without_recorded_contract", "probe", "x", {})
ok(r.get("refused"), "R0 audit probe refused")
ok(not any(a["action"] in ("phi_in_outbound", "audit_without_recorded_contract")
           and a["state"] == "pending" for a in store.load("approvals")),
   "an R0 never becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no wrong-medication message missed")
ok("WRONG DRUG" in ev["costly_note"], "costly note names the stake")
ok(ev["n"] >= 15, "15+ labelled cases, empty message included")

print("== roi ==")
r = core.roi({})
ok("recovered_counted" in r["recorded"] and "open_recoverable" in r["recorded"],
   "the counted inputs are recorded, not asked for")
ok(r["recorded"]["recovered_counted"] == 212.47, "the ROI reads the counted correction")
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["The dispensed-at-a-loss list"]["kind"] == "scenario"
   and labels["The dispensed-at-a-loss list"]["value"] is None,
   "the loss list is a scenario line, blank until the owner values it")
ok(labels["Owner audit hours"]["kind"] == "time_saved", "hours stay typed as time, never revenue")
ok(labels["Open recoverable inside the window"]["value"] is None
   and "appeal_win_rate" in labels["Open recoverable inside the window"]["_missing"],
   "a line missing your input is blank, never estimated")

print("== the counted week ==")
basew = core.week_counts()
store.log_event("draft_appeal", "fd_rm_cm_01_RX-88214", "human:owner", "R1", {})
w = core.week_counts()
ok(w["appeals_sent"] == basew["appeals_sent"] + 1,
   "human-sent appeals counted; agent drafts are not")
ok(w["corrections_recorded"] == 1 and w["corrected_dollars"] == 212.47,
   "the week counts the recorded correction with its dollars")
ok(w["autopsies_run"] >= 3 and "counted" in w["note"], "autopsies counted; basis named")

print("== append-only ==")
n0 = len(store.events())
store.log_event("correction_recorded", "fd_x", "human:owner", "R1", {"amount": 1.00})
evs = store.events()
ok(len(evs) == n0 + 1, "a correction is a NEW event")
ok(any(e["subject"] == "fd_rm_cm_01_RX-88214" and e["kind"] == "correction_recorded"
       for e in evs), "the earlier state is still in the log — nothing rewritten")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted from the log, or refused below the floor")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
