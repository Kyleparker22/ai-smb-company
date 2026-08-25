#!/usr/bin/env python3
"""Closing OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["CLOSINGOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="closingos-test-")
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


# ---------------------------------------------------------------- triage + eval
for text in ["updated wiring instructions attached, please use these",
             "our account changed for the payoff, new details below",
             "can you resend the wire info? urgent, closing is today",
             "seller's bank routing number is different now",
             "where do we send the earnest money wire"]:
    c = core.read_message(text)
    ok(c["label"] == "wire_signal", f"wire signal caught: {text[:40]}")
    ok(c.get("protocol") == core.WIRE_PROTOCOL, "…and carries the protocol verbatim")

ok(core.read_message("any update on the Hollis file?")["label"] == "status_question",
   "a status ask classifies")
ok(core.read_message("attached is the payoff letter from the credit union")["label"] == "document_inbound",
   "an inbound document classifies")
ok(core.read_message("can we close early on friday instead")["label"] == "date_question",
   "a date ask classifies")
ok(core.read_message("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "wire_signal" and ev["costly_missed"] == 0,
   f"zero missed wire signals in the shipped eval ({ev['costly_missed']})")
ok("AGENCY-ENDING" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- the wire stop
store.wipe()
store.save("config", {"company": "t"})
store.save("messages", [{"id": "m_w", "text": "updated wiring instructions attached, use these"}])
r = agents.handle_message("m_w")
ok(r["steps"][0]["said"] == core.WIRE_PROTOCOL,
   "the wire reply IS the protocol — nothing restated, nothing confirmed")
ok(any(e["detail"].get("action") == "confirm_wire_change"
       for e in store.events(kind="refused", subject="m_w")), "the refusal is logged")

r = agents.request_wire_instructions("fl_x")
ok(r.get("refused") and not r["executed"],
   "asking the system for wire instructions is refused outright")
ok("any channel" in r["reason"], "…with the never-in-any-channel reason")

# ---------------------------------------------------------------- clear to close
store.save("files", [
    {"id": "f_open", "address": "982 Dove Hollow", "curatives": [
        {"kind": "payoff", "requested_at": iso(now() - timedelta(days=10)), "touches": []},
        {"kind": "survey", "requested_at": iso(now() - timedelta(days=10)),
         "received_at": iso(now() - timedelta(days=2)), "touches": []}]},
    {"id": "f_clean", "address": "417 Juniper", "curatives": [
        {"kind": "payoff", "requested_at": iso(now() - timedelta(days=10)),
         "received_at": iso(now() - timedelta(days=2)), "touches": []}]},
])
v = agents.declare_clear("f_open")
ok(not v.get("clear") and "payoff" in v["refused"],
   "clear-to-close is refused over the open payoff, item named")
ok(not any(a for a in store.load("approvals") if a.get("subject") == "f_open"),
   "the refused clear never became an approvable row")
v = agents.declare_clear("f_clean")
ok(v.get("clear") and v["gate"].get("approval"),
   "the clean file drafts clear-to-close at R1 — a human declares")
ok("assert_clear_to_close" in core.matrix.never_promote(), "clear-to-close can never promote")

# ---------------------------------------------------------------- status desk
d = core.status_draft("f_open")
ok("survey" in d["draft"] and "payoff" in d["draft"],
   "the status draft states received and open items from the record")
ok("no date promise" in d["note"], "…and contains no date promise by design")

# ---------------------------------------------------------------- chase bounds
f = store.by_id("files", "f_open")
item = f["curatives"][0]
plan = core.chase_plan(f, item)
ok(plan["action"] == "draft_chase", "an open item past cooldown drafts a chase")
item["touches"] = [{"at": iso(now() - timedelta(days=30))}] * core.CHASE_MAX_TOUCHES
ok(core.chase_plan(f, item)["action"] == "human", "an exhausted ladder goes to a person")
item["touches"] = [{"at": iso(now() - timedelta(days=1))}]
ok(core.chase_plan(f, item)["action"] == "none", "cooldown respected")

store.save("approvals", [])
out = agents.chase_sweep()
ok(out["drafted"] >= 1, "the sweep drafts chases")

# ---------------------------------------------------------------- R0 probes
for action in ("send_wire_instructions", "confirm_wire_change", "legal_opinion"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("send_wire_instructions", "confirm_wire_change", "legal_opinion")
           for a in core.gate.pending()), "no R0 action reached the approval queue")
ok("promise_close_date" in core.matrix.never_promote(), "date promises can never promote")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Status-call and chase time"]["value"] is None,
   "the time line is blank without the operator's hours")
we = labels["Wire-fraud exposure"]
ok(we["kind"] == "scenario" and we["value"] is None,
   "wire exposure is a scenario, the operator's or blank — the average BEC loss is not our number")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("we revised the wire details, disregard the earlier sheet", "wire_signal"),
                   ("eta on clear to close? lender is pushing", "status_question"),
                   ("can we move the closing to monday morning", "date_question")):
    ok(core.read_message(text)["label"] == want, f"triage: {text[:44]} → {want}")

# ---------------------------------------------------------------- drafted copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

f9 = {"id": "fl9", "address": "44 Maple St", "target_close": _iso(_now() + timedelta(days=10)),
      "curatives": [{"kind": "hoa_estoppel", "requested_at": _iso(_now() - timedelta(days=6))}]}
store.upsert("files", f9)
body = agents._chase_copy(f9, f9["curatives"][0], 1)
ok("hoa estoppel" in body and "44 Maple St" in body and "fl9" in body,
   "chase copy carries the item, the address, and the file number")
ok("HOA / management company" in body, "chase copy names the responsible party")
ok("wire" not in body.lower(), "a chase never mentions wiring")
ok(not any(w in body.lower() for w in ("close on", "close by", "will close")),
   "a chase never promises a date")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")
final = agents._chase_copy(f9, f9["curatives"][0], core.CHASE_MAX_TOUCHES)
ok("Final written request" in final and "call" in final,
   "the last touch names itself final and moves to the phone")

# the sweep records the drafted body on the touch
out = agents.chase_sweep()
f9 = store.by_id("files", "fl9")
ok(f9["curatives"][0].get("touches") and f9["curatives"][0]["touches"][0].get("body"),
   "the drafted body is recorded on the item's touch")

# proactive status: one per open file per 7 days, no date promise
out = agents.status_sweep()
ok(out["drafted"] >= 1, "an open file gets a proactive status draft")
ap = [a_ for a_ in store.load("approvals") if a_["action"] == "draft_status_reply"
      and a_["subject"] == "fl9"]
ok(len(ap) == 1, "exactly one status draft for the file")
out = agents.status_sweep()
ok(not any(a_["subject"] == "fl9" for a_ in store.load("approvals")
           if a_["action"] == "draft_status_reply" and a_["id"] not in {x["id"] for x in ap}),
   "the 7-day status cooldown holds")

# ---------------------------------------------------------------- recovered, counted
base = core.recovered_this_week()
f9["curatives"][0]["received_at"] = _iso(_now() - timedelta(days=1))
f9["closed_at"] = _iso(_now())
store.upsert("files", f9)
store.log_event("draft_chase", "fl9", "human:processor", "R1", {"approval": "apc"})
rec = core.recovered_this_week()
ok(rec["curatives_received"] == base["curatives_received"] + 1
   and rec["files_closed"] == base["files_closed"] + 1,
   "received items and closed files are counted from the file records")
ok(rec["chases_sent"] == 1, "human-sent chases are counted; agent drafts are not")
ok(rec["wire_signals_caught"] >= 1, "wire signals caught are counted from the log")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
