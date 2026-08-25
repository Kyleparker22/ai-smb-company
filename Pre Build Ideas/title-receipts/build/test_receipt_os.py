#!/usr/bin/env python3
"""Receipt OS — the suite. `python3 test_receipt_os.py`."""
import inspect, os, sys, tempfile
from pathlib import Path

os.environ["RECEIPTOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="receiptos_test_")
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
ok(len(store.load("wires")) >= 540, "wires seeded (~90 closings/mo x 6 months)")
ok(len(store.load("ledger")) >= 600, "control ledger seeded")

print("== the control ledger is append-only ==")
for name in ("ledger_edit", "ledger_update", "ledger_delete", "edit_ledger_entry",
             "update_ledger_entry", "delete_ledger_entry"):
    ok(not hasattr(core, name), f"no {name} — the ledger has no edit path")
n0 = len(store.load("ledger"))
e = core.ledger_append("callback_verification", "wr_001",
                       {"who_called": "J. Mercer", "number_called_ref": core.CALLBACK_REF})
c = core.ledger_correct(e["id"], "wrong caller recorded", {"who_called": "M. Trujillo"})
led = store.load("ledger")
ok(len(led) == n0 + 2, "a correction APPENDS — the ledger grew by two")
orig = next(x for x in led if x["id"] == e["id"])
ok(orig["detail"]["who_called"] == "J. Mercer", "the original entry is untouched")
ok(c["kind"] == "correction" and c["detail"]["corrects"] == e["id"],
   "the correction points at the entry it corrects")
try:
    core.ledger_append("edited_entry", "wr_001", {})
    ok(False, "unknown ledger kind rejected")
except ValueError:
    ok(True, "unknown ledger kind rejected")

print("== triage: the wire change reads first ==")
for case in core.EVAL_CASES:
    got = core.read_message(case["input"])["label"]
    ok(got == case["label"], f"triage: {case['input'][:48] or '(empty)'} → {case['label']} (got {got})")

print("== the wire-change protocol: verbatim, callback path, never acted ==")
wires_before = len(store.load("wires"))
out = agents.handle_message("ms_demo_wire")
step = out["steps"][0]
ok(step["action"] == "route_wire_change", "the wire change routes, immediately")
ok(step["said"] == core.WIRE_PROTOCOL, "the protocol is stated verbatim — inherited law")
entry = next(x for x in store.load("ledger") if x["id"] == step["ledger"])
ok(entry["kind"] == "wire_change_request"
   and entry["detail"]["verbatim"] == "updated wiring instructions attached, please use these for closing",
   "the request is recorded VERBATIM in the control ledger — the first receipt of the chain")
ok(core.CALLBACK_REF in step["callback_path"], "the reply states the verified-callback path")
ok("no field to land in" in step["callback_path"], "the email's number has nowhere to go")
ok(any(ev["kind"] == "refused" and (ev["detail"] or {}).get("action") == "act_on_emailed_wire_change"
       for ev in store.events()), "act_on_emailed_wire_change refused + logged")
ok(len(store.load("wires")) == wires_before, "no wire was created or moved from the message")
r = agents.act_on_wire_change("ms_demo_wire")
ok(r.get("refused") and r["rung"] == "R0", "the probe — 'act on it' — refuses at R0")
ok(not any(a["action"] == "act_on_emailed_wire_change" and a["state"] == "pending"
           for a in store.load("approvals")), "the refusal never becomes an approvable row")

print("== the callback receipt: the recorded number by construction ==")
params = set(inspect.signature(agents.record_callback).parameters)
ok(params == {"wire_id", "who_called"},
   "record_callback has no parameter that could carry the email's number")
r = agents.record_callback("wr_000", "D. Okafor")
ok(r["executed"] and r["rung"] == "R2", "the receipt records at R2 — the control ran, the human is told")
cb = [x for x in core.ledger_entries(kind="callback_verification", wire_id="wr_000")]
ok(cb and cb[-1]["detail"]["number_called_ref"] == core.CALLBACK_REF,
   "number_called_ref is the fixed string: the recorded number on file, never the one in the email")
ok(cb[-1]["detail"]["who_called"] == "D. Okafor", "who_called is named")

print("== dual control: two distinct humans or nothing ==")
r = agents.record_dual_control("wr_000", "D. Okafor", "D. Okafor")
ok("refused" in r and "two distinct" in r["refused"], "the same name twice is refused")
r = agents.record_dual_control("wr_000", "D. Okafor", "S. Lindqvist")
ok(r["executed"], "two named humans record")
dc = core.ledger_entries(kind="dual_control_release", wire_id="wr_000")
ok(dc[-1]["detail"]["human_a"] == "D. Okafor" and dc[-1]["detail"]["human_b"] == "S. Lindqvist",
   "both humans are named in the receipt")

print("== the coverage-year file, hand-checked ==")
period = core.policy_period()
led = store.load("ledger")


def hand(kind):
    return len([x for x in led if x["kind"] == kind and not x.get("demo_tag")
                and core._in_period(x["at"], period)])


cov = core.coverage_year()
ok(cov["verifications"] == hand("callback_verification"), "verifications count hand-checked")
ok(cov["blocked_attempts"] == hand("blocked_attempt"), "blocked attempts hand-checked")
ok(cov["dual_control_releases"] == hand("dual_control_release"), "dual controls hand-checked")
ok(cov["wire_change_requests"] == hand("wire_change_request"), "change requests hand-checked")
moved_hand = len([w for w in store.load("wires") if not w.get("demo_tag")
                  and w.get("released_at") and core._in_period(w["released_at"], period)])
ok(cov["wires_moved"] == moved_hand, "wires moved hand-checked")
ok(cov["chains_complete"] + len(cov["exceptions"]) == cov["wires_moved"],
   "every wire is either a complete chain or an exception — nothing falls out of the file")
ok("counted" in cov["note"] and "never asserted" in cov["note"], "the file names its basis")

print("== the exceptions list — the honest column ==")
exc = {x["wire"]: x for x in cov["exceptions"]}
ok(set(exc) == {"wr_exc_single_1", "wr_exc_single_2", "wr_exc_callback"},
   "exactly the 3 seeded exceptions, none hidden")
ok(any("single-control" in g for g in exc["wr_exc_single_1"]["gaps"]), "single-control gap named")
ok(any("missing callback" in g for g in exc["wr_exc_callback"]["gaps"]), "missing-callback gap named")

print("== structural: a packet without exceptions data cannot render ==")
chains = core.wire_chains()
ok("complete" in chains and "exceptions" in chains,
   "one read path returns both halves together")
try:
    core.render_renewal_packet({"chains_complete": 5, "wires_moved": 5})
    ok(False, "packet without exceptions refused to render")
except ValueError as ex:
    ok("omit_exception has no code path" in str(ex), "packet without exceptions refused to render")
r = core.gate.act("omit_exception", "probe", "x", {})
ok(r.get("refused") and r["rung"] == "R0", "omit_exception R0 probe refused")

print("== UNTESTED honesty ==")
st = core.drill_status("positive_pay")
ok(st["status"] == "UNTESTED", "no drill this period → the control reads UNTESTED")
ok("claim, not a control" in st["note"], "the note says why")
st2 = core.drill_status("callback_verification")
ok(st2["status"] == "tested — pass" and st2["drills_this_period"] == 2,
   "a drilled control reads tested, with its dates counted")
r = agents.attest_control("positive_pay")
ok(r["refused"] and r["gate"]["rung"] == "R0", "attesting an untested control refuses at R0")
ok(not any(a["action"] == "claim_untested_control" and a["state"] == "pending"
           for a in store.load("approvals")), "claim_untested_control never becomes approvable")
r = agents.attest_control("callback_verification")
ok(not r["refused"] and "drill record" in r["why"], "a tested control attests via the drill record")

print("== the renewal packet ==")
r = agents.draft_renewal_packet()
text = r["packet"]
ok(r["gate"]["rung"] == "R1" and not r["gate"]["executed"], "the packet drafts at R1 — a human sends")
ok(f"callback verifications recorded: {cov['verifications']}" in text, "the counted year is in the packet")
for wid in ("wr_exc_single_1", "wr_exc_single_2", "wr_exc_callback"):
    ok(wid in text, f"exception {wid} honestly listed in the packet")
ok("UNTESTED" in text and "positive_pay" in text, "the UNTESTED control is stated, not hidden")
ok("underwriters price; we evidence" in text.lower(), "the line: underwriters price; we evidence")
ok(core.premium_ok(text)[0], "the packet passes its own forbidden-language check")
ok(not core.premium_ok("sign with us for a guaranteed discount")[0],
   "'guaranteed discount' is structurally refused")
ok(not core.premium_ok("this file will lower your premium")[0],
   "'will lower your premium' is structurally refused")
ok("yourco" not in text.lower(), "white-label — the packet carries only the agency's name")
r = core.gate.act("promise_premium_outcome", "probe", "renewal", {})
ok(r.get("refused") and r["rung"] == "R0", "promise_premium_outcome R0 probe refused")

print("== the realtor one-pager: counted, zero client data ==")
r = agents.draft_realtor_proof()
proof = r["proof"]
ok(r["gate"]["rung"] == "R1", "the one-pager drafts at R1")
ok(str(cov["verifications"]) in proof and str(cov["blocked_attempts"]) in proof,
   "counted verifications and blocks are in the proof")
ok("Marisol Etheridge" not in proof, "planted client name never appears")
ok("412,500" not in proof and "412500" not in proof.replace(",", ""), "planted amount never appears")
ok("BX-2214" not in proof and "BX-" not in proof, "no file numbers appear")
ok("yourco" not in proof.lower(), "white-label")
ok(core.client_data_leaks(proof) == [], "the scrub passes the shipped copy")
leaks = core.client_data_leaks("we recently closed for Marisol Etheridge at 412,500 on BX-2214")
ok(any(h["leak"] == "party name" for h in leaks), "the scrub catches a planted name")
ok(any(h["leak"] == "amount" for h in leaks), "the scrub catches a planted amount")
ok(any(h["leak"] == "file number" for h in leaks), "the scrub catches a planted file number")

print("== the demo chain, end-to-end ==")
ch = core.wire_chain("wr_demo_chain")
ok([x["kind"] for x in ch["entries"]] == ["wire_change_request", "callback_verification",
                                          "dual_control_release"],
   "request → callback → dual-control, in order")
ok(ch["gaps"] == [], "the demo chain is complete")
total_cb = len(core.ledger_entries(kind="callback_verification"))
ok(total_cb > hand("callback_verification"), "demo receipts exist but are excluded from every count")

print("== the insurer reply ==")
out = agents.handle_message("ms_demo_insurer")
body = out["steps"][0]["draft"]
ok("exceptions" in body and "UNTESTED" in body.replace("positive_pay is listed as UNTESTED", "UNTESTED"),
   "the reply names the exceptions and the UNTESTED control")
ok(core.premium_ok(body)[0] and "no premium claim" in body, "the reply promises nothing")

print("== eval ==")
ev = core.run_eval()
ok(ev["n"] >= 15, f"{ev['n']} labelled cases")
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no wire-change signal missed")
ok(ev["costly_label"] == "wire_change", "the costly class is the wire change")
ok("AGENCY-ENDING" in ev["costly_note"], "the costly note names the stake")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
labels = {l["label"]: l for l in r["lines"]}
prem = labels["Premium reduction earned at renewal"]
ok(prem["value"] is None and "premium_before" in prem["_missing"],
   "the premium line is BLANK until a renewal has happened — never promised")
scen = labels["The breach that didn't happen"]
ok(scen["kind"] == "scenario" and scen["value"] is None, "the breach line is a blank scenario")
ok(labels["Audit and renewal prep hours"]["kind"] == "time_saved", "audit prep is time_saved")
r2 = core.roi({"premium_before": "18000", "premium_after": "16500"})
prem2 = {l["label"]: l for l in r2["lines"]}["Premium reduction earned at renewal"]
ok(prem2["value"] == 1500, "with both invoices given, the delta computes and shows its arithmetic")
ok(r["counted_context"]["exceptions"] == 3, "the ROI page carries the counted context, exceptions included")

print("== the week, counted (baseline delta) ==")
base = core.receipts_this_week()
core.ledger_append("callback_verification", "wr_002",
                   {"who_called": "R. Whitfield", "number_called_ref": core.CALLBACK_REF})
core.ledger_append("blocked_attempt", None, {"vector": "test block"})
rec = core.receipts_this_week()
ok(rec["verifications"] == base["verifications"] + 1, "a new verification is counted, +1 exactly")
ok(rec["blocked_attempts"] == base["blocked_attempts"] + 1, "a new block is counted, +1 exactly")
ok(rec["wire_signals_caught"] >= 1, "the demo wire signal was caught this week")
ok("counted" in rec["note"], "the week names its basis")

print("== matrix ==")
for a in ("act_on_emailed_wire_change", "claim_untested_control", "omit_exception",
          "promise_premium_outcome"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
    r = core.gate.act(a, "probe", "x", {})
    ok(r.get("refused") and r["rung"] == "R0", f"{a} probe refused at R0")
    ok(not any(ap["action"] == a and ap["state"] == "pending" for ap in store.load("approvals")),
       f"{a} is never an approvable row")

print("== events append-only + automation ==")
ne = len(store.events())
store.log_event("probe", "x", "human:test", None, {})
ok(len(store.events()) == ne + 1, "the event log appends")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
