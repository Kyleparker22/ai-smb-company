#!/usr/bin/env python3
"""Key OS — the suite. `python3 test_key_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["KEYOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="keyos_test_")
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
ok(len(store.load("systems")) >= 30, "master systems seeded")
ok(len(store.load("jobs")) >= 250, "jobs seeded")
ok(len(store.load("authorizations")) >= 50, "authorization records seeded")
ok("_source" in core.rate_card(), "the rate card names its source")
ok(core.authority_for("14 Alder Ct") is None, "14 Alder Ct deliberately has no authority record")

print("== triage: the emergency reads first ==")
for case in core.EVAL_CASES:
    got = core.read_message(case["input"])["label"]
    ok(got == case["label"], f"triage: {case['input'][:44]!r} → {case['label']} (got {got})")

print("== the emergency protocol ==")
out = agents.handle_message("ms_demo_hotcar")
step = out["steps"][0]
ok(out["classification"]["label"] == "emergency_lockout", "hot car classified emergency")
ok(step["draft"].startswith(agents.EMERGENCY_SCRIPT), "the reply LEADS with the 911 script verbatim")
ok("call 911 now" in step["draft"], "911 named in the reply")
ok(any(e["kind"] == "record_emergency" and e["rung"] == "R2" for e in store.events()),
   "the emergency record lands at R2 without waiting")
ok("yourco" not in step["draft"].lower(), "white-label: emergency draft")

print("== the authorization gate ==")
out = agents.handle_message("ms_demo_rekey_noauth")
step = out["steps"][0]
ok(step.get("unverifiable"), "no authority → drafted as unverifiable")
ok("14 Alder Ct" in step["gap"], "the gap names the address")
ok("ID seen" in step["gap"] or "deed" in step["gap"], "the gap names the missing acts")
ok("break-in with an invoice" in step["gap"], "the gap names the stake")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "perform_without_authorization"
       for e in store.events()), "perform_without_authorization refused + logged")
ok(not any(j.get("address") == "14 Alder Ct" for j in store.load("jobs")),
   "structural: no job row exists for the unverified address — there is no dispatch path")
ok("yourco" not in step["draft"].lower(), "white-label: unverifiable draft")

out = agents.handle_message("ms_demo_rekey_auth")
step = out["steps"][0]
ok(step["action"] == "draft_dispatch", "recorded authority → the job path")
ok(step.get("authorization_ref") == "au_demo", "the dispatch carries the authorization ref")
ok("Dana Whitcomb" in step["draft"] or "verified on our records" in step["draft"],
   "the draft names the verification")
job = store.by_id("jobs", step["job"])
ok(job and job.get("authorization_ref") == "au_demo", "the job row records the auth ref")
ok(any(a["action"] == "draft_dispatch" and a["state"] == "pending"
       for a in store.load("approvals")), "the dispatch queues at R1 — a human rolls the truck")
ok("yourco" not in step["draft"].lower(), "white-label: dispatch draft")

print("== the phone claim ==")
before = core.authority_for("14 Alder Ct")
core.record_phone_claim("14 Alder Ct", "Grant Hyland", "says he just bought it")
ok(before is None and core.authority_for("14 Alder Ct") is None,
   "a recorded phone claim is never authority")
ok(any(a.get("role") == "phone_claim" and a.get("address") == "14 Alder Ct"
       for a in store.load("authorizations")), "the claim IS recorded — as a claim")
ok(any(e["kind"] == "phone_claim_recorded" for e in store.events()), "the claim event logged")
r = core.gate.act("authorize_by_phone_claim", "probe", "x", {})
ok(r.get("refused"), "authorize_by_phone_claim R0 probe refused")

print("== the key-code scrub ==")
okc, why = core.key_scrub_ok("your code is SC4-84921")
ok(not okc, "keyway-code pattern fails the scrub")
okc, why = core.key_scrub_ok("bitting is 3-5-2-4-6")
ok(not okc, "bitting cut sequence fails the scrub")
ok(core.key_scrub_ok("van 2 arriving at 14 Alder Ct around 3pm")[0], "clean copy passes")
planted = store.load("registry")[0]["key_code"]
ok(not core.key_scrub_ok(f"the code you asked about is {planted}")[0],
   "a RECORDED code fails the scrub even beyond the regex — the field half")
m = store.by_id("messages", "ms_demo_quote")
m["text"] = f"how much to rekey a 3 bedroom house with 5 locks, my old code was {planted}"
store.upsert("messages", m)
out = agents.handle_message("ms_demo_quote")
drafts = [s.get("draft", "") for s in out["steps"]] + [store.by_id("messages", "ms_demo_quote").get("draft_reply", "")]
ok(all(planted not in (d or "") for d in drafts),
   "structural: a code planted in a message never appears in any draft")
r = core.gate.act("disclose_key_code", "probe", "x", {})
ok(r.get("refused"), "disclose_key_code R0 probe refused")

print("== the master-key registry, append-only ==")
ok(not hasattr(core, "edit_system"), "edit_system does not exist")
ok(not hasattr(core, "registry_edit"), "registry_edit does not exist")
sys_id = store.load("systems")[0]["id"]
recs0 = core.system_records(sys_id)
n_all0 = len(store.load("registry"))
new = core.registry_append(sys_id, "key issued to new tenant", "test authorizer")
recs1 = core.system_records(sys_id)
ok(len(recs1) == len(recs0) + 1, "a change is a NEW record")
ok(len(store.load("registry")) == n_all0 + 1, "nothing else was touched")
ok(recs1[0] == recs0[0], "the oldest record is intact — history is never rewritten")
r = core.gate.act("edit_registry_record", "probe", sys_id, {})
ok(r.get("refused"), "edit_registry_record R0 probe refused")

out = agents.handle_message("ms_demo_master")
step = out["steps"][0]
ok(step["action"] == "registry_append", "a named authorizer's change appends")
ok(step.get("record"), "the append produced a new record id")
ok("new registry entry" in step["draft"], "the ack names the append-only rule")
ok(core.key_scrub_ok(step["draft"])[0] and not any(
   rec["key_code"] in step["draft"] for rec in store.load("registry") if rec.get("key_code")),
   "no code in the master-system reply")
m = store.by_id("messages", "ms_demo_master")
m2 = dict(m, id="ms_probe_master", handled_at=None, **{"from": "Nobody Inparticular"})
store.upsert("messages", m2)
out = agents.handle_message("ms_probe_master")
ok(out["steps"][0].get("unverifiable"), "a non-authorizer's master change is unverifiable")
ok("not a named authorizer" in out["steps"][0]["gap"], "the gap names the missing authority")

print("== the rate-card clamp ==")
card = core.rate_card()
q = core.quote_for("rekey", cylinders=5)
ok(q["total"] == card["rekey_base"] + 5 * card["rekey_per_cylinder"],
   "the rekey quote is the card's arithmetic exactly")
q2 = core.quote_for("lockout_auto", after_hours=True)
ok(q2["total"] == round(card["lockout_auto"] * card["after_hours_multiplier"], 2),
   "the after-hours multiplier comes from the card")
ok("no other number exists" in q2["basis"], "the basis names the clamp")
q3 = core.quote_for("whatever_i_feel_like")
ok(q3.get("total") is None and "_missing" in q3, "an off-card kind cannot be priced")
q4 = core.quote_for("rekey")
ok(q4.get("total") is None, "a rekey with no cylinder count refuses rather than guessing")
r = core.gate.act("quote_off_rate_card", "probe", "x", {})
ok(r.get("refused"), "quote_off_rate_card R0 probe refused")

print("== jobs close with their references ==")
r = agents.close_job("jb_demo_norefs", human="owner")
ok("refused" in r and "authorization_ref" in r["refused"], "no auth ref → close refused, gap named")
j = dict(store.by_id("jobs", "jb_demo_norefs"), authorization_ref="au_demo", card_item="rekey_base")
store.upsert("jobs", j)
r = agents.close_job("jb_demo_norefs")
ok("refused" in r and "human act" in r["refused"], "references on file but no human → no close")
r = agents.close_job("jb_demo_norefs", human="owner")
ok(r.get("closed") and "au_demo" in r["why"] and "rekey_base" in r["why"],
   "a human closes citing the authorization ref and the card line")

print("== service clocks: the bounded ladder ==")
c_due = store.by_id("clocks", "ck_demo_due")
ok(core.service_plan(c_due)["action"] == "draft_service_reminder", "an overdue clock is due a touch")
c_ex = store.by_id("clocks", "ck_demo_exhausted")
plan = core.service_plan(c_ex)
ok(plan["action"] == "none" and "silence exit" in plan["why"],
   "3 touches → ladder exhausted, silence exit")
c_skip = store.by_id("clocks", "ck_demo_skip")
ok("demo" in core.service_plan(c_skip)["why"], "sweeps skip demo_tag")
out = agents.service_sweep()
ok(out["drafted"] >= 1, "due clocks get drafted reminders")
c_due = store.by_id("clocks", "ck_demo_due")
ok(core.service_plan(c_due)["action"] == "none", "a fresh touch starts the cooldown")

print("== matrix ==")
for a in ("perform_without_authorization", "disclose_key_code", "authorize_by_phone_claim",
          "quote_off_rate_card", "edit_registry_record"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("perform_without_authorization", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a_["action"] in ("perform_without_authorization", "disclose_key_code",
                            "authorize_by_phone_claim", "quote_off_rate_card")
           and a_["state"] == "pending" for a_ in store.load("approvals")),
   "no R0 ever becomes an approvable row")

print("== the append-only log ==")
n = len(store.events())
first = store.events()[0]
store.log_event("probe", "x", "human:test", None, {})
ok(len(store.events()) == n + 1 and store.events()[0] == first,
   "the event log only ever grows; the first event is intact")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no emergency missed")
ok("LIFE-SAFETY" in ev["costly_note"] and "911" in ev["costly_note"],
   "the costly note names the life-safety stake and 911")
ok(ev["n"] >= 15, "eval set is at least 15 cases")

print("== roi ==")
r = core.roi({})
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok("after_hours_jobs_90d" in r["recorded"], "after-hours jobs counted")
labels = {l["label"]: l for l in r["lines"]}
ok(labels["After-hours capture"]["kind"] == "revenue", "after-hours capture is revenue")
ok(labels["Dispatch hours"]["kind"] == "time_saved", "dispatch hours is time_saved")
lw = labels["The lawsuit file"]
ok(lw["kind"] == "scenario", "the lawsuit file is a scenario")
ok(lw["value"] is None and "_missing" in lw, "the lawsuit file renders blank, never estimated")
r2 = core.roi({"lawsuit_value": 50000})
ok({l["label"]: l for l in r2["lines"]}["The lawsuit file"]["value"] == 50000,
   "the operator's own lawsuit number renders as a scenario")

print("== recovered, counted ==")
base = core.recovered_this_week()
store.upsert("jobs", {"id": "jb_test_rec", "kind": "lockout_auto", "card_item": "lockout_auto",
                      "opened_at": iso(now() - timedelta(days=2)),
                      "closed_at": iso(now() - timedelta(days=1))})
store.log_event("draft_dispatch", "jb_test_rec", "human:dispatcher", "R1", {})
rec = core.recovered_this_week()
ok(rec["jobs_closed"] == base["jobs_closed"] + 1, "closed jobs counted, baseline-delta")
ok(rec["dispatches_sent"] == base["dispatches_sent"] + 1,
   "human dispatches counted; agent drafts are not")
ok(rec["emergencies_recorded"] >= 1, "the emergency was counted")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print("== white-label sweep ==")
for mid in ("ms_demo_hotcar", "ms_demo_rekey_auth", "ms_demo_rekey_noauth", "ms_demo_master"):
    d = (store.by_id("messages", mid) or {}).get("draft_reply") or ""
    ok("yourco" not in d.lower(), f"white-label: {mid}")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
