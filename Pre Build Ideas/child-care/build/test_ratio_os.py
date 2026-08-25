#!/usr/bin/env python3
"""Ratio OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["RATIOOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="ratioos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core
from core import store
from _kit.store import iso, now

PASS = FAIL = 0


def ok(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {msg}")


# ---------------------------------------------------------------- the pickup rule
store.wipe()
store.save("config", {"company": "t", "ratio_rules": core.DEFAULT_RATIO_RULES})
store.save("children", [{"id": "c1", "name": "Emma", "status": "active",
                         "authorized_pickups": ["Alex Osei", "Harper Osei"]}])
v = core.release_check("c1", "Alex Osei")
ok(v["listed"] and "not an authorization" in v["note"],
   "a listed person passes the lookup — and it is only a lookup")
v = core.release_check("c1", "alex osei")
ok(v["listed"], "the lookup is case-insensitive")
v = core.release_check("c1", "Uncle Ray")
ok(not v["listed"] and "never authorizes a release" in v["refused"],
   "an unlisted person is refused with the rule stated")

r = agents.check_release("c1", "Uncle Ray")
ok("refused" in r, "the agent path refuses too")
ok(any(e["detail"].get("action") == "confirm_unlisted_pickup"
       for e in store.events(kind="refused", subject="c1")), "the refusal is logged")
ok(any(e["kind"] == "open_verification" for e in store.events(subject="c1")),
   "a human verification task opened (R2, logged)")

# ---------------------------------------------------------------- triage + eval
ok(core.read_message("my brother will pick her up today instead of me")["label"] == "pickup_change",
   "a pickup change classifies")
ok(core.read_message("he fell off the slide and hit his head")["label"] == "incident",
   "an injury classifies")
ok(core.read_message("she had a fever, when can she come back")["label"] == "illness_question",
   "an illness question classifies")
ok(core.read_message("do you have any infant room openings")["label"] == "enrollment",
   "enrollment classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "critical" and ev["costly_missed"] == 0,
   f"zero missed critical messages in the shipped eval ({ev['costly_missed']})")
ok("NIGHTMARE SCENARIO" in ev["costly_note"], "the eval names the stake")

# handling: pickup change never auto-approves
store.save("messages", [{"id": "m1", "child_id": "c1",
                         "text": "grandma is getting him this afternoon"}])
store.save("approvals", [])
r = agents.handle_message("m1")
ok(r["steps"][0]["action"] == "open_verification", "a pickup change opens verification")
ok("confirms nothing" in r["steps"][0]["refused"], "…and software confirms nothing")
# incident: nothing drafted
store.save("messages", [{"id": "m2", "child_id": "c1",
                         "text": "another kid bit Emma, she has a bruise"}])
r = agents.handle_message("m2")
ok("nothing drafted" in r["steps"][0]["refused"], "an incident gets nothing in writing")

# ---------------------------------------------------------------- ratios
store.save("rooms", [
    {"id": "r_ok", "name": "toddler A", "age_group": "toddler", "state_code": "TX",
     "capacity": 18, "attendance_recorded": True},
    {"id": "r_over", "name": "infant A", "age_group": "infant", "state_code": "TX",
     "capacity": 12, "attendance_recorded": True},
    {"id": "r_norec", "name": "annex", "age_group": "preschool", "state_code": "TX",
     "capacity": 20, "attendance_recorded": False},
])
att = [{"id": f"a{i}", "room_id": "r_ok", "child_id": f"k{i}", "checked_in": iso(),
        "checked_out": None} for i in range(9)]
att += [{"id": f"b{i}", "room_id": "r_over", "child_id": f"j{i}", "checked_in": iso(),
         "checked_out": None} for i in range(9)]
store.save("attendance", att)
store.save("clockins", [
    {"id": "s1", "room_id": "r_ok", "staff": "x", "clocked_out": None},
    {"id": "s2", "room_id": "r_over", "staff": "y", "clocked_out": None},
])
v = core.room_ratio(store.by_id("rooms", "r_ok"))
ok(v["status"] == "inside" and v["ratio"] == 9.0, "9 toddlers : 1 staff is inside the TX rule (9)")
v = core.room_ratio(store.by_id("rooms", "r_over"))
ok(v["status"] == "over", "9 infants : 1 staff is over the TX rule (4)")
v = core.room_ratio(store.by_id("rooms", "r_norec"))
ok(v.get("_missing") and "never assumed compliant" in v["_missing"],
   "a room with no records is unmeasured, never assumed compliant")
v = core.room_ratio({"id": "x", "age_group": "infant", "state_code": "ZZ"})
ok(v.get("_missing"), "a state with no rules is refused")

# staff zero
store.save("clockins", [{"id": "s1", "room_id": "r_ok", "staff": "x", "clocked_out": None}])
v = core.room_ratio(store.by_id("rooms", "r_over"))
ok(v["status"] == "over" and "no staff" in v["why"], "children with zero staff is over by definition")

# ---------------------------------------------------------------- funnel floor
store.save("waitlist", [])
f = core.funnel()
ok(f.get("_missing") and "need 10" in f["_missing"], "the funnel refuses below its floor")

# ---------------------------------------------------------------- R0 probes
for action in ("confirm_unlisted_pickup", "add_authorized_pickup", "respond_to_incident",
               "answer_medical_exclusion", "estimate_ratio"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("confirm_unlisted_pickup", "add_authorized_pickup",
                           "respond_to_incident", "answer_medical_exclusion", "estimate_ratio")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Seats filled from the waitlist"]["value"] is None,
   "the seats line is blank without the operator's tuition")
ok(labels["The pickup discipline"]["kind"] == "scenario",
   "the release rule is never monetized — it cannot be priced")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("my coworker Dana will be getting him today, dark green suv", "pickup_change"),
                   ("there was blood on his sock after outside time", "incident"),
                   ("pink eye is going around her class, can she attend tomorrow", "illness_question")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

# ---------------------------------------------------------------- the checklist + copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

cl = agents.verification_checklist({"text": "my brother will get her"})
ok(len(cl) == 4 and any("ON FILE" in s for s in cl),
   "the checklist calls the number on file, never the message's")
ok(any("the child stays" in s for s in cl), "when anything is off, the child stays")

tour = agents._tour_copy({"from": "Priya"})
ok("Priya" in tour and "full swing" in tour, "tour copy offers the honest view")
ok("$" not in tour, "no rates in the message — rates come on paper at the visit")
wl = agents._waitlist_copy({"family": "Okafor family", "age_group": "infant"})
ok("haven't forgotten" in wl and "first call" in wl, "waitlist copy is honest about the wait")
ok("Nothing has opened yet" in wl, "no false hope — the copy says nothing has opened")
ok("yourco" not in (tour + wl).lower(), "white-label: no yourco name in outward copy")

# ---------------------------------------------------------------- recovered, counted
base = core.recovered_this_week()
store.log_event("draft_tour_offer", "mq1", "human:director", "R1", {})
store.upsert("waitlist", {"id": "wl9", "family": "Nkemdi", "age_group": "twos",
                          "at": _iso(_now() - timedelta(days=30)),
                          "enrolled_at": _iso(_now() - timedelta(days=1))})
rec = core.recovered_this_week()
ok(rec["tour_offers_sent"] == base["tour_offers_sent"] + 1,
   "human-sent tour offers are counted; agent drafts are not")
ok(rec["enrollments"] == base["enrollments"] + 1, "enrollments are counted from the waitlist")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
