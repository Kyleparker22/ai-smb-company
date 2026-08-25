#!/usr/bin/env python3
"""Ember OS — the suite. `python3 test_ember_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["EMBEROS_DATA_ROOT"] = tempfile.mkdtemp(prefix="emberos_test_")
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
ok(len(store.load("pets")) >= 300, "pets seeded across the chain")
ok(len(store.load("clinics")) == 40, "40 clinics")
ok(len(store.load("loads")) >= 2, "chamber loads seeded")

print("== triage: the identity worry reads first ==")
for text, want in (("how do I know these are really Max's ashes", "identity_worry"),
                   ("are you sure these are actually Bella's remains and not another dog's",
                    "identity_worry"),
                   ("I read about crematories mixing up pets, how do I know you didn't",
                    "identity_worry"),
                   ("did we get the right ashes back? the bag seems small", "identity_worry"),
                   ("these ashes seem like they are really someone else's", "identity_worry"),
                   ("riverbend animal hospital has three patients ready for pickup",
                    "clinic_pickup_request"),
                   ("can your driver collect two pets from our clinic tomorrow",
                    "clinic_pickup_request"),
                   ("when will Luna's ashes be ready to come home", "status_ask"),
                   ("any update on Cooper? we miss him", "status_ask"),
                   ("we'd like to add a paw print keepsake for Daisy", "addon_order"),
                   ("can we order the engraved cedar urn instead of the standard one",
                    "addon_order"),
                   ("can you deliver Milo's ashes to our house on saturday",
                    "return_arrangement"),
                   ("we'd rather come to you to bring Rosie home, what are your hours",
                    "return_arrangement"),
                   ("", "human"),
                   ("thank you for taking such good care of our girl", "human"),
                   ("do you also do horses", "human")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:46]} → {want}")

print("== the identity protocol: the chain, cited verbatim ==")
out = agents.handle_message("ms_demo_worry")
step = out["steps"][0]
ok(step["action"] == "draft_identity_answer", "the identity worry gets the record")
draft = step["draft"]
ok("never answer with comfort alone" in draft, "the answer refuses bare reassurance")
ok("WC-0417" in draft, "the tag is cited")
ok("read and matched by" in draft, "the verbatim tag-check language is cited")
for a, b in (("clinic", "van"), ("van", "facility"), ("facility", "chamber"),
             ("chamber", "urn")):
    ok(f"{a} → {b}" in draft, f"the {a} → {b} transfer is cited verbatim")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "reassure_without_record"
       for e in store.events()), "reassure_without_record refused + logged")
ok("yourco" not in draft.lower(), "white-label — no yourco on a family surface")
ok(core.tone_ok(draft)[0], "the identity answer passes its own tone check")

print("== chain of custody: no path without the tag check ==")
ok(not hasattr(core, "record_transfer_unchecked"), "no unchecked-transfer code path exists")
ok(not hasattr(core, "force_transfer"), "no force-transfer code path exists")
r = core.record_transfer("pt_demo_transfer", by="operator K. Alvarez")
ok("refused" in r and "tag verification" in r["refused"], "transfer without tag → refused")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "transfer_without_tag_check"
       for e in store.events()), "transfer_without_tag_check logged as a refusal")
r = core.record_transfer("pt_demo_transfer", tag_read="WC-9999", by="operator K. Alvarez")
ok("refused" in r and "does not match" in r["refused"], "wrong tag → refused, HOLDs")
pet = store.by_id("pets", "pt_demo_transfer")
ok(len(pet["custody"]) == 2, "nothing was written by the refused transfers")
r = core.record_transfer("pt_demo_transfer", to="urn", tag_read="WC-0902", by="operator K. Alvarez")
ok("refused" in r and "skipped" in r["refused"], "steps cannot be skipped")
r = core.record_transfer("pt_demo_transfer", tag_read="WC-0902", by="operator K. Alvarez")
ok(r.get("recorded") and r["to"] == "chamber", "with the tag check, the transfer records")
pet = store.by_id("pets", "pt_demo_transfer")
ok(pet["custody"][-1]["tag_check"]["by"] == "operator K. Alvarez",
   "the tag check rides in the record")
st = core.chain_status(store.by_id("pets", "pt_demo_gap"))
ok(st["state"] == "HOLD", "the deliberate gap reads HOLD")
ok("never assumed" in st["why"], "a gap is never assumed")
r = core.record_transfer("pt_demo_gap", tag_read="WC-0771", by="operator D. Whitmore")
ok("refused" in r and "HOLD" in r["refused"], "nothing moves over a hold")
ok(core.chain_status(store.by_id("pets", "pt_demo_max"))["state"] == "intact",
   "Max's chain is intact")

print("== the service-level wall ==")
r = core.change_service_level("pt_demo_private", "communal")
ok("refused" in r and "consent" in r["refused"], "software probe → refused")
ok(not any(a["action"] == "change_service_level" and a["state"] == "pending"
           for a in store.load("approvals")), "R0 never becomes an approvable row")
ok(store.by_id("pets", "pt_demo_private")["service_level"] == "private",
   "the recorded level did not move")
r = core.change_service_level("pt_demo_status", "private", human="owner", consent_ref="CR-2201")
ok(r.get("changed") and r["consent_ref"] == "CR-2201",
   "a human with the family's consent ref changes it")
ok(store.by_id("pets", "pt_demo_status")["consent_refs"][0]["ref"] == "CR-2201",
   "the consent ref is recorded on the pet")
core.change_service_level("pt_demo_status", "individual", human="owner", consent_ref="CR-2202")
r = core.add_to_load("ld_demo_communal", "pt_demo_private")
ok("refused" in r and "do not mix" in r["refused"], "private pet into a communal load → refused")
ok("EL-0655" in r["refused"], "the refusal cites the signed election ref")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "mix_private_chamber_load"
       for e in store.events()), "mix_private_chamber_load logged as a refusal")
r = core.add_to_load("ld_demo_private", "pt_demo_max")
ok("refused" in r and "exactly one pet" in r["refused"], "a private load holds one pet")
ok("pt_demo_private" not in (store.by_id("loads", "ld_demo_communal")["pets"]),
   "the load record did not move")

print("== the family tone check ==")
for w in ("processed", "shipment", "unit", "disposal", "inventory"):
    ok(not core.tone_ok(f"your pet has been {w}")[0], f"'{w}' is forbidden to a family")
ok(core.tone_ok("Max is ready to come home whenever you are")[0], "family language passes")
r = agents.try_family_draft("Your unit has been processed and the shipment is ready.")
ok("refused" in r, "the planted logistics draft → refused")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "logistics_language_to_family"
       for e in store.events()), "logistics_language_to_family logged as a refusal")
ok(agents.try_family_draft("Rosie is safe with us and ready whenever you are.").get("ok"),
   "an honest family draft passes the door")
for n in (1, 2, 3):
    body = agents._return_reminder_copy(store.by_id("pets", "pt_demo_aged"), n)
    ok(core.tone_ok(body)[0], f"return-reminder touch {n} passes its own tone check")

print("== the proof rule: the family's recorded act ==")
r = core.approve_proof("pt_demo_proof")
ok("refused" in r and "family's recorded act" in r["refused"], "software approval → refused")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "approve_engraving_proof"
       for e in store.events()), "approve_engraving_proof logged as a refusal")
r = core.approve_proof("pt_demo_proof", family="Dana Nakamura", ref="FA-1187")
ok(r.get("approved") and r["by"] == "Dana Nakamura", "the family's approval records")
ok(any(e["kind"] == "proof_approved" and e["actor"] == "family:Dana Nakamura"
       for e in store.events()), "the approval is the family's act in the log")

print("== the aged-remains clock ==")
r = core.final_disposition("pt_demo_proof")
ok("refused" in r and "policy clock" in r["refused"], "before the clock → refused")
ok(any(e["kind"] == "refused"
       and (e["detail"] or {}).get("action") == "final_disposition_before_clock"
       for e in store.events()), "final_disposition_before_clock logged")
r = core.final_disposition("pt_demo_aged")
ok("refused" in r and "human act" in r["refused"], "even at the clock, no human → no decision")
r = core.final_disposition("pt_demo_aged", human="owner")
ok(r.get("done") and "only now" in r["why"], "a human decides after the clock, and only then")
plan = core.return_plan(store.by_id("pets", "pt_demo_proof"))
ok(plan["action"] == "none" and "cooldown" in plan["why"], "grief is not chased — the cooldown holds")
plan = core.return_plan({"ashes_ready_at": iso(now() - timedelta(days=40))})
ok(plan["action"] == "draft_reminder", "past the cooldown, the gentle ladder drafts")
plan = core.return_plan({"ashes_ready_at": iso(now() - timedelta(days=170)),
                         "return_touches": [{"at": iso(now() - timedelta(days=30))}] * 3})
ok(plan["action"] == "none" and "human act" in plan["why"],
   "the ladder is bounded — after it, the clock runs and a human decides")

print("== the add-on, offered once ==")
out = agents.handle_message("ms_demo_status")
d1 = out["steps"][0]["draft"]
ok(out["steps"][0]["offered_addon"] and "paw print" in d1, "the first update carries the offer")
ok(core.tone_ok(d1)[0], "the update passes its own tone check")
ok(store.by_id("pets", "pt_demo_status").get("addon_offered_at"), "the offer is recorded")
out = agents.handle_message("ms_demo_status2")
d2 = out["steps"][0]["draft"]
ok(not out["steps"][0]["offered_addon"] and "paw print" not in d2,
   "the second update never re-pitches")
ok(sum(1 for e in store.events(kind="draft_addon_offer")) +
   sum(1 for e in store.events(kind="queued_for_approval")
       if (e["detail"] or {}).get("action") == "draft_addon_offer") == 1,
   "draft_addon_offer fired exactly once")

print("== the clinic desk + the return arrangement ==")
out = agents.handle_message("ms_demo_clinic")
d = out["steps"][0]["draft"]
ok(out["steps"][0]["action"] == "draft_pickup_confirmation", "the pickup routes from the request")
ok("Riverbend Animal Hospital" in d and "recorded preferences" in d,
   "the clinic's recorded preferences are cited — never memory")
ok("tag-verified at" in d, "the handoff tag check is named to the clinic")
out = agents.handle_message("ms_demo_return")
ok(store.by_id("pets", "pt_demo_return").get("return_method_requested"),
   "the return method is recorded")
ok(core.tone_ok(out["steps"][0]["draft"])[0], "the return draft passes the tone check")
out = agents.handle_message("ms_demo_addon")
ok("approve the exact spelling" in out["steps"][0]["draft"],
   "the engraving waits on the family's proof")

print("== sweeps skip demo fixtures ==")
before = {p["id"]: len(p.get("return_touches") or []) for p in store.load("pets")
          if p.get("demo_tag")}
agents.return_sweep()
after = {p["id"]: len(p.get("return_touches") or []) for p in store.load("pets")
         if p.get("demo_tag")}
ok(before == after, "the return sweep never touches a demo pet")

print("== matrix ==")
for a in ("transfer_without_tag_check", "reassure_without_record", "change_service_level",
          "mix_private_chamber_load", "logistics_language_to_family",
          "final_disposition_before_clock", "approve_engraving_proof"):
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
r = core.gate.act("transfer_without_tag_check", "probe", "x", {})
ok(r.get("refused"), "R0 probe refused")
ok(not any(a["action"] in core.matrix.never_promote() and a["state"] == "pending"
           for a in store.load("approvals")), "no R0 ever becomes an approvable row")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no identity worry missed")
ok("END THE BUSINESS" in ev["costly_note"], "the costly note names the stake")
ok(ev["n"] >= 15, "at least 15 labelled cases")

print("== roi ==")
r = core.roi({})
ok("active_clinics" in r["recorded"], "active clinics are counted")
ok("addon_attach_rate" in r["recorded"], "the attach rate is counted")
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["The wrong-ashes file"]["kind"] == "scenario", "the wrong-ashes file is a scenario")
ok(labels["The wrong-ashes file"]["value"] is None, "the wrong-ashes file is blank, never our number")
ok(labels["Route & office hours"]["kind"] == "time_saved", "hours are time_saved, never revenue")

print("== recovered, counted ==")
base = core.recovered_this_week()
p9 = store.by_id("pets", "pt_demo_max")
p9["returned_at"] = iso(now() - timedelta(days=1))
store.upsert("pets", p9)
store.log_event("draft_return_reminder", "pt_demo_proof", "human:caredesk", "R1", {})
rec = core.recovered_this_week()
ok(rec["pets_home"] == base["pets_home"] + 1, "a pet home this week is counted")
ok(rec["reminders_sent"] == base["reminders_sent"] + 1,
   "human reminders counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a), "automation counted or refused")

print("== append-only events ==")
n0 = len(store.load("events"))
first = store.load("events")[0]
store.log_event("probe", "x", "human:test", None, {})
evs = store.load("events")
ok(len(evs) == n0 + 1, "the log only grows")
ok(evs[0] == first and evs[0]["kind"] == "seeded", "history is never rewritten")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
