#!/usr/bin/env python3
"""Haul OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["HAULOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="haulos-test-")
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


# ---------------------------------------------------------------- classifier + eval
for text, kind in [("can I toss a few cans of old paint in there", "paint_solvents"),
                   ("got some car batteries", "batteries"),
                   ("we're tearing out a popcorn ceiling from the 70s", "asbestos"),
                   ("old fridge and a window AC unit", "appliances_freon"),
                   ("half a propane tank from the grill", "propane_fuel"),
                   ("needles from my dad's insulin", "medical")]:
    c = core.classify_item(text)
    ok(c["label"] == "hazardous" and c["kind"] == kind, f"hazardous typed as {kind}")

ok(core.classify_item("drywall from the garage remodel")["label"] == "allowed", "drywall is allowed")
ok(core.classify_item("old couch and a dresser")["label"] == "allowed", "furniture is allowed")
c = core.classify_item("some stuff from my uncle's shed")
ok(c["label"] == "unknown" and "contaminated" in c["why"],
   "vague contents are unknown — 'probably fine' is how loads get contaminated")
ok(core.classify_item("")["label"] == "unknown", "empty is unknown")

ev = core.run_eval()
ok(ev["costly_label"] == "hazardous" and ev["costly_missed"] == 0,
   f"zero hazardous items missed in the shipped eval ({ev['costly_missed']})")
ok("CONTAMINATED LOAD" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- the never-yes rule
store.wipe()
store.save("config", {"company": "t"})
store.save("messages", [
    {"id": "m_haz", "text": "can I toss a few cans of old paint in there"},
    {"id": "m_ok", "text": "drywall from the garage remodel"},
])
r = agents.answer_item("m_haz")
ok(r["steps"][0]["action"] == "refuse_and_route", "a hazardous item is refused and routed")
ok("can't go in the container" in r["steps"][0]["said"], "the answer says no, with help coming")
ok(any(e["detail"].get("action") == "approve_hazardous_item"
       for e in store.events(kind="refused", subject="m_haz")), "the refusal is logged")
r = agents.answer_item("m_ok")
ok("Yes, that's fine" in r["steps"][0]["said"], "an allowed item gets a yes")
ok("scale ticket decides" in r["steps"][0]["said"], "…with the weight caveat riding along")

# ---------------------------------------------------------------- charge evidence
store.save("charges", [
    {"id": "c_t", "kind": "overweight", "amount": 340, "scale_ticket_id": "tkt_1"},
    {"id": "c_n", "kind": "overweight", "amount": 340},
    {"id": "c_p", "kind": "contamination", "amount": 150, "photo_record_id": "ph_1"},
    {"id": "c_np", "kind": "contamination", "amount": 150},
])
ok(core.charge_check(store.by_id("charges", "c_t"))["assertable"], "a ticketed overage asserts")
v = core.charge_check(store.by_id("charges", "c_n"))
ok(not v["assertable"] and "no scale ticket" in v["refused"], "no ticket → cannot assert")
ok(core.charge_check(store.by_id("charges", "c_p"))["assertable"], "a photographed contamination asserts")
ok(not core.charge_check(store.by_id("charges", "c_np"))["assertable"], "no photo → cannot assert")

r = agents.try_charge("c_n")
ok("refused" in r, "the ticketless charge is refused at the agent layer too")
ok(not any(a for a in store.load("approvals") if a.get("subject") == "c_n"),
   "the refused charge never became an approvable row")
r = agents.try_charge("c_t")
ok(r.get("gate", {}).get("approval"), "the evidenced charge drafts at R1")

# ---------------------------------------------------------------- containers
store.save("containers", [
    {"id": "k1", "status": "on_site", "site": "A", "size": 20,
     "delivered_at": iso(now() - timedelta(days=12))},
    {"id": "k2", "status": "on_site", "site": "B", "size": 20,
     "delivered_at": iso(now() - timedelta(days=2))},
    {"id": "k3", "status": "on_site", "site": "C", "size": 20},  # no delivery date
    {"id": "k4", "status": "in_yard", "size": 20},
])
store.save("orders", [
    {"id": "o1", "kind": "pickup", "container_id": "k2", "promised_at": iso(now() + timedelta(days=1))},
    {"id": "o2", "kind": "pickup", "container_id": "k9", "promised_at": iso(now() - timedelta(days=3))},
])
idle = {r["container"]: r for r in core.idle_containers()}
ok("k1" in idle and idle["k1"]["flagged"], "12 idle days flags")
ok("k2" not in idle, "a container with an open pull is not idle")
ok(idle["k3"].get("_missing"), "no delivery date → idle age unknowable, said")
ok("k4" not in idle, "a yard container is not idle-on-site")
missed = core.missed_pickups()
ok(len(missed) == 1 and missed[0]["order"] == "o2" and missed[0]["days_late"] == 3,
   "a promised pickup past due is counted missed")

# ---------------------------------------------------------------- R0 probes
for action in ("approve_hazardous_item", "assert_charge_without_ticket"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("approve_hazardous_item", "assert_charge_without_ticket")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Idle container-days turned"]["value"] is None,
   "the idle line is blank without the operator's margin")
ok(labels["Contaminated-load exposure"]["kind"] == "scenario",
   "contamination exposure is a scenario, never a saving")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("a couple gallons of leftover deck stain", "hazardous"),
                   ("old queen mattress and box spring", "hazardous"),
                   ("concrete chunks from the patio demo", "allowed")):
    ok(core.classify_item(text)["label"] == want, f"triage: {text[:40]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

store.upsert("charges", {"id": "ch9", "kind": "overweight", "amount": 340,
                         "scale_ticket_id": "ST-2214"})
r = agents.try_charge("ch9")
ok(r["assertable"] and "ST-2214" in r["draft"] and "$340" in r["draft"],
   "overweight copy leads with the ticket and the number")
ok("call and we'll walk it" in r["draft"].lower() or "call" in r["draft"].lower(),
   "the copy invites the walk-through, not the fight")
store.upsert("charges", {"id": "ch10", "kind": "contamination", "amount": 150,
                         "photo_record_id": "PH-88"})
r = agents.try_charge("ch10")
ok("PH-88" in r["draft"] and "before this bills" in r["draft"],
   "contamination copy cites the photos and offers the out")
ok("yourco" not in r["draft"].lower(), "white-label: no yourco name in outward copy")

# ---------------------------------------------------------------- the make-right sweep
store.upsert("orders", {"id": "or9", "kind": "pickup", "container_id": "cn9",
                        "promised_at": _iso(_now() - timedelta(days=2))})
out = agents.missed_pickup_sweep()
ok(out["drafted"] >= 1, "a late pull gets a drafted make-right")
ap = next(a_ for a_ in store.load("approvals") if a_["action"] == "draft_pickup_makeright")
ok("that's on" in ap["detail"]["preview"] or "on \nus" in ap["detail"]["preview"]
   or "on us" in ap["detail"]["preview"], "the make-right owns the miss plainly")
out = agents.missed_pickup_sweep()
ok(out["drafted"] == 0, "one make-right per order per 3 days")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["charges_sent"] == 0 and rec["charge_value"] == 0, "nothing sent → zeros, honestly")
store.log_event("draft_charge", "ch9", "human:owner", "R1", {"approval": "aph"})
store.upsert("orders", {"id": "or10", "kind": "swap", "container_id": "cn2",
                        "completed_at": _iso(_now() - timedelta(days=1))})
rec = core.recovered_this_week()
ok(rec["charges_sent"] == 1 and rec["charge_value"] == 340,
   "a human-sent charge is counted with its ledger amount")
ok(rec["pulls_completed"] >= 1, "completed pulls are counted from the order book")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
