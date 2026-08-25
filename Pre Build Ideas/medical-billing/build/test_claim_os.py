#!/usr/bin/env python3
"""Claim OS — the suite. `python3 test_claim_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["CLAIMOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="claimos_test_")
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
ok(len(store.load("claims")) >= 600, "claims seeded")
ok(len(store.load("denials")) >= 80, "denials seeded")

print("== denial triage by reason code ==")
for carc, want in (("CO-50", "needs_provider_doc"), ("CO-29", "untimely"),
                   ("CO-16", "needs_info"), ("CO-11", "miscoded"),
                   ("CO-97", "bundled"), ("PR-1", "patient_resp"),
                   ("XX-99", "unknown"), (None, "unknown")):
    ok(core.triage_denial({"carc": carc})["kind"] == want, f"triage {carc} → {want}")

print("== the upcoding refusal ==")
okr, why = core.can_recode(store.by_id("claims", "cm_demo_upcode"), "99214")
ok(not okr and "upcoding is fraud" in why, "up without documentation refused, stake named")
r = agents.recode("cm_demo_upcode", "99214")
ok("refused" in r, "the recode path refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "upcode_without_documentation"
       for e in store.events()), "upcode_without_documentation logged")
okr, why = core.can_recode(store.by_id("claims", "cm_demo_docd"), "99214")
ok(okr and "DOC-2214" in why and "still drafts at R1" in why,
   "documented upcode permitted — and still gated at R1")
r = agents.recode("cm_demo_docd", "99214")
ok(r.get("rung") == "R1" and r.get("approval"), "documented upcode queues, never executes")
okr, why = core.can_recode(store.by_id("claims", "cm_demo_upcode"), "99211")
ok(okr and "downcode" in why, "downcoding is mechanical")
r = agents.recode("cm_demo_upcode", "99211")
ok(r.get("executed") and r.get("rung") == "R2", "downcode executes at R2")
ok(store.by_id("claims", "cm_demo_upcode")["cpt"] == "99211", "the downcode landed")

print("== the clean-claim gate ==")
oks, why = core.can_submit(store.by_id("claims", "cm_demo_dirty"))
ok(not oks and "payer" in why and "icd10" in why and "rendering_npi" in why,
   "incomplete claim refused with each field named")
r = agents.submit("cm_demo_dirty")
ok("refused" in r, "submit path refuses")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "submit_incomplete_claim"
       for e in store.events()), "submit_incomplete_claim logged")
r = agents.submit("cm_demo_docd")
ok(r.get("rung") == "R1", "a clean claim queues at R1 — an 837 is a legal statement")

print("== the filing clock ==")
c = core.filing_clock({"payer": "BlueCap", "date_of_service": iso(now() - timedelta(days=80))})
ok(c["days_left"] in (9, 10), "BlueCap 90-day window computes")
ok("DATE ALERT" in c["label"], "the clock is a date alert, not advice")
c = core.filing_clock({"payer": "Medicare", "date_of_service": iso(now() - timedelta(days=80))})
ok(c["days_left"] > 200, "Medicare's own window applies")
ok("_missing" in core.filing_clock({"payer": "BlueCap"}), "no DOS → unknowable, never guessed")
ar = core.at_risk_board()
ok(ar["at_risk_value"] >= 210, "the demo at-risk claim is counted with its dollars")

print("== PHI discipline ==")
okp, why = core.phi_scrub_ok("claim cm_001, DOS 2026-07-01, denied CO-50")
ok(okp, "a claim reference passes")
okp, why = core.phi_scrub_ok("patient DOB 4/12/1961, claim cm_001")
ok(not okp and "DOB" in why, "a DOB fails the draft")
okp, why = core.phi_scrub_ok("SSN 123-45-6789 attached")
ok(not okp, "an SSN pattern fails the draft")
claim = store.by_id("claims", "cm_demo_docd")
body = agents._appeal_copy({"carc": "CO-50"}, claim, 1)
ok("cm_demo_docd" in body and "CO-50" in body and "DOC-2214" in body,
   "the appeal cites claim, code, and documentation")
ok(core.phi_scrub_ok(body)[0], "the appeal draft passes the scrub structurally")

print("== the appeal ladder ==")
d9 = {"id": "dn_x", "claim_id": "cm_demo_docd", "carc": "CO-50",
      "denied_at": iso(now() - timedelta(days=20))}
store.upsert("denials", d9)
ok(core.appeal_plan(d9)["action"] == "draft_appeal", "an appealable denial is due a draft")
d9["touches"] = [{"at": iso(now() - timedelta(days=3))}]
ok(core.appeal_plan(d9)["action"] == "none", "14-day cooldown holds")
d9["touches"] = [{"at": iso(now() - timedelta(days=40))}, {"at": iso(now() - timedelta(days=20))}]
ok("a human calls the payer" in core.appeal_plan(d9)["why"], "past the ladder, a human calls")
ok(core.appeal_plan({"id": "d", "carc": "CO-29", "denied_at": iso(now())})["action"] == "human",
   "an untimely denial goes to a human — a write-off is never automated")

print("== matrix ==")
for a in ("upcode_without_documentation", "submit_incomplete_claim", "send_phi_in_draft",
          "write_off_claim"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("send_phi_in_draft", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no medical-necessity denial missed")
ok("FOREVER" in ev["costly_note"], "costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("at_risk_value" in r["recorded"], "at-risk dollars recorded")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The audit file"]["kind"] == "scenario", "the audit file is a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
c9 = store.by_id("claims", "cm_demo_atrisk")
c9["paid_at"] = iso(now() - timedelta(days=1))
store.upsert("claims", c9)
store.log_event("draft_appeal", "dn_x", "human:denials", "R1", {})
d9["resolved_at"] = iso(now())
store.upsert("denials", d9)
rec = core.recovered_this_week()
ok(rec["claims_paid"] == base["claims_paid"] + 1 and rec["paid_value"] >= 210,
   "a paid claim is counted with its dollars")
ok(rec["appeals_sent"] == 1, "human-sent appeals counted; agent drafts are not")
ok(rec["denials_resolved"] == base["denials_resolved"] + 1, "resolutions counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
