#!/usr/bin/env python3
"""Halflife OS — the suite. `python3 test_halflife_os.py`."""
import os, sys, tempfile
from pathlib import Path

os.environ["HALFLIFEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="halflifeos_test_")
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
ok(len(store.load("matters")) >= 70, "matters seeded (~70)")
ok(len(store.load("evidence")) >= 240, "evidence items seeded (~260)")
ok(sum(1 for i in store.load("evidence") if i["state"] == "LOST") >= 3,
   "several LOST with history")

print("== table-driven clock math ==")
ref = now().replace(microsecond=0)  # iso() truncates microseconds; keep the arithmetic exact
for ct, days in core.DEFAULT_RETENTION["days"].items():
    if ct == "witness_memory":
        continue
    item = {"custodian_type": ct, "type": "footage",
            "created_at": iso(ref - timedelta(days=max(1, days - 5)))}
    c = core.clock(item, ref)
    ok(not c["unknown"] and c["days_left"] == min(5, days - 1),
       f"clock math: {ct} ({days}d) → {c['days_left']}")
# witness anchors on last recorded contact, not the incident
w = {"custodian_type": "witness_memory", "type": "witness",
     "created_at": iso(ref - timedelta(days=300)),
     "last_contact": iso(ref - timedelta(days=100))}
cw = core.clock(w, ref)
ok(cw["days_left"] == 20, "witness clock runs from last recorded contact (120d window)")
ok("last recorded contact" in cw["basis"], "witness basis names the freshness window")
w2 = dict(w)
del w2["last_contact"]
ok(core.clock(w2, ref)["days_left"] < 0, "witness with no contact decays from creation")
# a custodian type NOT in the table
cu = core.clock({"custodian_type": "private_warehouse_cam", "type": "footage",
                 "created_at": iso(ref)}, ref)
ok(cu["unknown"] and cu["days_left"] is None, "unrecorded custodian type → UNKNOWN")
ok("UNKNOWN" in cu["basis"] and "scariest" in cu["basis"], "the basis says why it sorts first")

print("== the dies-first queue ==")
q = core.dies_first_queue()
ok(len(q["rows"]) > 0, "queue has rows")
ok(all(q["rows"][i]["unknown"] for i in range(q["unknown_count"])),
   "UNKNOWN clocks sort FIRST")
ok(q["unknown_count"] >= 1 and q["rows"][0]["unknown"], "the scariest row is on top")
known = [r["days_left"] for r in q["rows"] if not r["unknown"]]
ok(known == sorted(known), "known clocks sorted by days-to-expiry ascending")
ok(all(r["state"] != "LOST" for r in q["rows"]), "LOST excluded from the queue")
ok(q["lost_count"] >= 3, "…but counted")
ok(all(r["item"] != "ev_demo_notice" for r in q["rows"]), "demo_tag items skipped")
nine = next((r for r in q["rows"] if r["item"] == "ev_9days"), None)
ok(nine and nine["days_left"] in (8, 9), f"the 9-days-left footage is in the queue")
ok(any(r["item"] == "ev_unknown" for r in q["rows"] if r["unknown"]),
   "the unknown-custodian item rides the top block")
stale = next((r for r in q["rows"] if r["item"] == "ev_witness_stale"), None)
ok(stale and stale["days_left"] in (19, 20), "the stale witness ranks with footage")

print("== secured needs a receipt (R0) ==")
r = agents.secure("ev_demo_notice")  # letter sent, no receipt
ok("refused" in r, "letter-only item cannot be marked secured")
ok("notice, not possession" in r["refused"], "the refusal states the rule")
ok(r.get("rung") == "R0", "refused at R0")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") == "assert_evidence_secured"
       for e in store.events()), "assert_evidence_secured refusal logged")
ok(not any(a["action"] == "assert_evidence_secured" and a["state"] == "pending"
           for a in store.load("approvals")), "R0 never becomes an approvable row")
item = store.by_id("evidence", "ev_demo_notice")
ok(item["state"] == "on_notice", "state unchanged by the refusal")

print("== a letter is notice, not possession ==")
d10 = iso(now() - timedelta(days=10))
r = agents.intake({"client": "Renata Holloway", "case_type": "trucking",
                   "opposing": "Bluff Road Logistics", "incident_date": d10,
                   "evidence": [
                       {"type": "footage", "source": "loading-dock camera",
                        "custodian": "Bluff Road Logistics", "custodian_type": "retail_cctv"},
                       {"type": "edr", "source": "tractor EDR",
                        "custodian": "Ridgeline Towing", "custodian_type": "vehicle_edr"},
                       {"type": "witness", "source": "bystander Gus Ferreira",
                        "custodian": "witness (synthetic)", "custodian_type": "witness_memory"},
                       {"type": "footage", "source": "yard camera",
                        "custodian": "Kestrel Storage LLC",
                        "custodian_type": "private_warehouse_cam"}]})
ok("matter" in r and len(r["items"]) == 4, "intake spawns the inventory from typed facts")
ok(all(x["item"]["created_at"] == d10 for x in r["items"]),
   "the incident date starts every clock")
ok(len(r["letters"]) == 4, "a draft per item in the same call")
lg = [x["gate"] for x in r["letters"]]
ok(all(g.get("rung") == "R1" and not g.get("executed") for g in lg),
   "every letter queues at R1 — drafted, not sent")
ok(not store.events(kind="preservation_letter_sent"), "nothing has been sent")
unk = next(x for x in r["items"] if x["item"]["custodian_type"] == "private_warehouse_cam")
ok(unk["clock"]["unknown"], "the unstated-policy item reads UNKNOWN at intake")
ok("NOT sent" in r["note"], "the intake note says so out loud")
# now a human approves one letter — that IS the send
letter_item = r["letters"][0]["item"]
before = core.clock(store.by_id("evidence", letter_item))
ap_id = r["letters"][0]["gate"]["approval"]
dec = core.gate.decide(ap_id, "amerrick", True,
                       execute=lambda: agents.letter_sent(letter_item, "amerrick"))
ok(dec["ok"] and dec["result"]["state"] == "on_notice", "human approval sends → on_notice")
after = core.clock(store.by_id("evidence", letter_item))
ok(after["expiry"] == before["expiry"], "the clock KEPT RUNNING — expiry unchanged")
ok(store.by_id("evidence", letter_item)["state"] != "secured",
   "on notice is never secured")
ok(any(e["kind"] == "preservation_letter_sent" and e["actor"] == "human:amerrick"
       for e in store.events()), "the send is a recorded human act")
# the letter copy itself
body = r["letters"][0]["draft"]
ok("PRESERVATION OF EVIDENCE" in body and "notice is not possession" in body,
   "the letter cites the rule")
ok("DRAFT FOR ATTORNEY REVIEW" in body, "the letter is a draft for attorney review")
ok("Merrick & Vance" in body and "yourco" not in body.lower(), "white-label")

print("== secured with a receipt is a human act ==")
r = agents.secure(letter_item, receipt_ref="RCPT-7001 — native files on locker drive")
ok("refused" in r and "HUMAN" in r["refused"], "receipt without a named human → refused")
r = agents.secure(letter_item, receipt_ref="RCPT-7001 — native files on locker drive",
                  human="kvance")
ok(r.get("secured") and r["receipt"].startswith("RCPT-7001"), "receipt + human → secured")
ok(store.by_id("evidence", letter_item)["state"] == "secured", "state is secured")
ok(any(e["kind"] == "evidence_secured" and e["actor"] == "human:kvance"
       for e in store.events()), "the receipt is a recorded human event")

print("== LOST is permanent ==")
# an item whose clock has already run out (municipal 14d, created 18d ago → died 4d ago)
dead = {"id": "ev_test_dead", "matter_id": "mat_000", "type": "footage",
        "source": "intersection cam test", "custodian": "City of Fairview DOT",
        "custodian_type": "municipal_camera",
        "created_at": iso(now() - timedelta(days=18)), "state": "on_notice",
        "notice": {"sent_at": iso(now() - timedelta(days=16)), "by": "amerrick"}}
store.upsert("evidence", dead)
sw = agents.sweep_expiry()
ok(sw["marked_lost"] >= 1, "the expiry sweep marks the dead")
dead = store.by_id("evidence", "ev_test_dead")
ok(dead["state"] == "LOST" and dead.get("died_at"), "LOST with died_at recorded")
ok(dead.get("was_on_notice") is True, "…and whether we were on notice")
ok(any(e["kind"] == "mark_lost" and e["subject"] == "ev_test_dead"
       for e in store.events()), "mark_lost logged at R2")
ok(not hasattr(core, "resurrect") and not hasattr(agents, "resurrect"),
   "no resurrect path exists")
r = agents.secure("ev_test_dead", receipt_ref="RCPT-9999", human="kvance")
ok("refused" in r and "does not forgive" in r["refused"],
   "a LOST item cannot be secured — the ledger does not forgive")
n_lost = sum(1 for i in store.load("evidence") if i["state"] == "LOST")
agents.sweep_expiry()
ok(sum(1 for i in store.load("evidence") if i["state"] == "LOST") == n_lost,
   "a second sweep changes nothing — LOST is stable")
ok(store.by_id("evidence", "ev_demo_notice")["state"] == "on_notice",
   "demo_tag items are skipped by the sweep — the fixture is untouched")

print("== triage: the tip reads first ==")
for c in core.EVAL_CASES:
    ok(core.read_message(c["input"])["label"] == c["label"],
       f"triage: {c['input'][:46] or '(empty)'} → {c['label']}")

print("== the tip spawns the item + letter NOW ==")
n_items = len(store.load("evidence"))
n_pend = len(core.gate.pending())
out = agents.handle_message("ms_demo_tip")
step = out["steps"][0]
ok(step["action"] == "inventory_evidence", "the tip is inventoried, not filed")
ok(len(store.load("evidence")) == n_items + 1, "an inventory item spawned")
spawned = store.by_id("evidence", step["item"])
ok(spawned["custodian_type"] == "gas_station_cctv", "the tip typed its custodian")
ok(spawned["created_at"] == store.by_id("matters", "mat_000")["incident_date"],
   "the clock runs from the incident, not the message")
ok(step["letter_gate"]["rung"] == "R1" and len(core.gate.pending()) == n_pend + 1,
   "the preservation letter drafted in the same pass, queued at R1")
ok("NEVER routed casually" in step["why"], "the why states the stake")
ok("PRESERVATION OF EVIDENCE" in step["draft"], "the draft is a real letter")

print("== eval ==")
ev = core.run_eval()
ok(ev["accuracy"] == 1.0, f"eval accuracy {ev['accuracy']}")
ok(ev["costly_missed"] == 0, "no evidence tip missed")
ok(ev["n"] >= 15, "15+ labelled cases")
ok(any(c["input"] == "" and c["label"] == "human" for c in core.EVAL_CASES),
   "the empty message routes to a human")
ok("OVERWRITES ITSELF" in ev["costly_note"], "the costly note names the stake")

print("== the R0 probes ==")
for a in ("assert_evidence_secured", "extend_clock_without_policy",
          "legal_advice_to_nonclient"):
    r = core.gate.act(a, "probe", "x", {})
    ok(r.get("refused") and r.get("rung") == "R0", f"{a} probe refused at R0")
    ok(a in core.matrix.never_promote(), f"{a} never promotes")
ok(not any(a["state"] == "pending" and a["action"] in
           ("assert_evidence_secured", "extend_clock_without_policy",
            "legal_advice_to_nonclient") for a in store.load("approvals")),
   "no R0 ever became an approvable row")
ok(not hasattr(core, "extend_clock"), "there is no clock-extension function")

print("== the legal-advice line holds ==")
out = agents.handle_message([m for m in store.load("messages")
                             if m["text"].startswith("how long do i have")][0]["id"])
step = out["steps"][0]
ok(step["action"] == "route_attorney", "a deadline ask routes to an attorney")
ok("Nothing in this message is a date, an opinion, or advice." in step["draft"],
   "the reply states, verbatim, that it contains no date and no opinion")
ok("licensed attorney" in step["draft"] or "attorneys will call" in step["draft"]
   or "attorneys" in step["draft"], "the reply hands the question to an attorney")
ok(any(e["kind"] == "refused" and (e["detail"] or {}).get("action") ==
       "legal_advice_to_nonclient" for e in store.events()),
   "legal_advice_to_nonclient refusal logged")

print("== roi: scenario lines stay blank ==")
r = core.roi({})
ok("items_preserved" in r["recorded"], "preserved count is recorded, counted")
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
scen = [l for l in r["lines"] if l["kind"] == "scenario"]
ok(len(scen) == 3, "three scenario lines")
ok(all(l.get("value") is None and l.get("_missing") for l in scen),
   "every scenario line stays BLANK — never a promised win")
foot = next(l for l in r["lines"] if l["label"] == "Footage that made liability")
ok("never a promised win" in (foot.get("assumption") or ""),
   "the liability line says why it is blank")
r2 = core.roi({"chase_hours_wk": 6, "loaded_rate": 40})
ts = next(l for l in r2["lines"] if l["kind"] == "time_saved")
ok(ts["value"] == 6 * 48 * 40, "time_saved computes from the operator's own inputs")
ok(all(l.get("value") is None for l in r2["lines"] if l["kind"] == "scenario"),
   "scenario lines blank even when other inputs arrive")

print("== counted this week, baseline-delta ==")
base = core.ledger_this_week()
agents.secure("ev_demo_notice", receipt_ref="RCPT-2214 — USB copy", human="kvance")
agents.letter_sent("ev_9days", "amerrick")
rec = core.ledger_this_week()
ok(rec["secured"] == base["secured"] + 1, "a new receipt moves the counted stat by one")
ok(rec["letters_sent"] == base["letters_sent"] + 1, "a human send counts; drafts do not")
ok(rec["lost"] >= 1, "this week's losses counted (the test's own dead item)")
ok("counted" in rec["note"], "the stat names its basis")
c9 = core.clock(store.by_id("evidence", "ev_9days"))
ok(store.by_id("evidence", "ev_9days")["state"] == "on_notice"
   and c9["days_left"] in (8, 9), "the 9-day item is on notice and STILL dying")

print("== witness freshness resets only on recorded contact ==")
before = core.clock(store.by_id("evidence", "ev_witness_stale"))
r = agents.witness_contact("ev_witness_stale", "amerrick")
ok(r["clock"]["days_left"] in (119, 120), "a recorded contact resets the window")
ok(r["clock"]["days_left"] > before["days_left"], "…which moved the clock")
ok(any(e["kind"] == "witness_contact" and e["actor"] == "human:amerrick"
       for e in store.events()), "the contact is a recorded human event")
r = agents.witness_contact("ev_9days", "amerrick")
ok("refused" in r, "only a witness item carries a freshness clock")

print("== append-only events ==")
n = len(store.events())
store.log_event("test_probe", "x", "human:test", "R1", {})
store.log_event("test_probe", "x", "human:test", "R1", {"correction": True})
evs = store.events(kind="test_probe")
ok(len(store.events()) == n + 2 and len(evs) == 2,
   "a correction is a NEW event — both rows stay")
ok(all(e.get("id") and e.get("at") for e in evs), "every event carries id + timestamp")

print("== white-label ==")
for text in (agents._status_copy({"from": "Bea Okonkwo", "matter_id": "mat_000"}),
             agents._deadline_copy({"from": "Bea Okonkwo"})):
    ok("yourco" not in text.lower() and "Merrick & Vance" in text,
       "outward copy carries the firm's name only")

print("== automation ==")
a = core.automation()
ok("rate" in a and (a.get("rate") is not None or "_missing" in a),
   "automation counted from the log, or refused with the reason")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
