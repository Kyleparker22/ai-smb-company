#!/usr/bin/env python3
"""Close OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["CLOSEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="closeos_test_")

import agents, core, seed                    # noqa: E402
from core import gate, store                 # noqa: E402
from _kit.store import iso, now              # noqa: E402

P = F = 0


def ok(c, l):
    global P, F
    if c:
        P += 1
    else:
        F += 1
        print(f"  FAIL: {l}")


def section(t):
    print(f"\n{t}")


section("an engagement may not sit in a vague 'in progress'")
e = {"id": "e1"}
try:
    core.advance(e, "waiting_on_client")
    ok(False, "a live state without a blocker must raise")
except ValueError as ex:
    ok("blocker" in str(ex), "a live state without a named blocker is refused, with a reason")
ok(core.advance(dict(e), "waiting_on_client", "client")["blocker"] == "client",
   "with a blocker it advances")
ok(core.advance(dict(e), "complete")["blocker"] is None, "complete needs no blocker")
try:
    core.advance(dict(e), "in progress", "client")
    ok(False, "'in progress' must not be a state")
except ValueError:
    ok(True, "'in progress' is not a state this system has")
ok("in progress" not in core.STATES, "and it is not in the state list")

section("the chaser never chases what it should not")
items = [{"id": "a", "type": "bank_statement", "state": "received", "requested_at": iso(now() - timedelta(days=20))},
         {"id": "b", "type": "k1", "state": "open", "requested_at": iso(now() - timedelta(days=20))},
         {"id": "c", "type": "draft_return", "state": "open", "requested_at": iso(now() - timedelta(days=20))},
         {"id": "d", "type": "signed_8879", "state": "open", "requested_at": iso(now() - timedelta(days=20))}]
due, why = core.due_chase(items[0], items)
ok(due == [] and "already received" in why, "a received item is never chased again")
due, why = core.due_chase(items[3], items)
ok(due == [] and "not chaseable" in why,
   "an 8879 is not chased before the draft return exists")
due, why = core.due_chase(items[2], items)
ok(due == [] and "outstanding" in (why or ""),
   "a draft return is not chased while client items are outstanding")
due, why = core.due_chase(items[1], items)
ok(len(due) == 5 and why is None, "a genuinely chaseable item has its ladder")
items[1]["touches"] = [{"day": 0}, {"day": 3}]
ok([t["day"] for t in core.due_chase(items[1], items)[0]] == [7, 12, 18],
   "a sent touch is never re-sent")
ok(core.LADDER[-1]["kind"] == "escalate",
   "the ladder ends at a partner task, not a fifth email")

section("document matching — a wrong-year or wrong-entity file is flagged, never filed")
eng = {"id": "e", "period_year": 2025, "entity": "YourCo LLC"}
open_items = [{"id": "i1", "type": "bank_statement", "state": "open", "period_month": 3},
              {"id": "i2", "type": "k1", "state": "open"}]
m = core.match_document({"filename": "YourCo 2024 Mar bank stmt.pdf"}, open_items, eng)
ok(m["action"] == "flag" and "wrong period" in m["why"], "a 2024 document on a 2025 engagement is flagged")
ok(m["matched"] is None, "and matched to nothing")
m2 = core.match_document({"filename": "2025 Mar bank stmt.pdf", "entity_hint": "Beta Inc"},
                         open_items, eng)
ok(m2["action"] == "flag" and "entity" in m2["why"], "a wrong-entity document is flagged")
m3 = core.match_document({"filename": "IMG_4471.jpg"}, open_items, eng)
ok(m3["action"] == "human_queue", "an unreadable filename goes to a human, not into a folder")
ok(m3["read"]["confidence"] < core.MATCH_THRESHOLD, "because its confidence is below threshold")
m4 = core.match_document({"filename": "1099-NEC 2025.pdf"}, open_items, eng)
ok(m4["action"] == "flag" and "no open request" in m4["why"],
   "a document nobody asked for is flagged rather than filed blindly")
m5 = core.match_document({"filename": "YourCo 2025 Mar bank stmt.pdf"}, open_items, eng)
ok(m5["action"] == "file" and m5["matched"] == "i1", "a clean match files")
ev = core.eval_documents()
ok(ev["costly_missed"] == 0, "zero mismatches slipped through as files")
ok(ev["costly_recall"] == 1.0, "recall on 'flag' is reported alone and is 1.0")

section("no tax position, ever; nothing is ever deleted")
ok(core.MATRIX.rung_for("answer_tax_question")["rung"] == "R0",
   "answering a tax question is declared R0")
ok("answer_tax_question" in core.MATRIX.never_promote(), "and never promotes")
ok(core.MATRIX.rung_for("delete_document")["rung"] == "R0", "deleting a document is declared R0")
ok("delete_document" in core.MATRIX.never_promote(), "and never promotes")
ok("propose_billing" in core.MATRIX.never_promote(),
   "asking a client for more money stays a partner's conversation")

section("a scope event cannot exist without a citation")
letter = {"clauses": [{"text": "Prior-year amendments are outside this engagement.",
                       "applies_to": ["prior-year amendment"], "covers": False},
                      {"text": "Routine questions arising from the work above are included.",
                       "applies_to": ["advisory question"], "covers": True}]}
d = core.detect_scope("Can you go back and amend 2023?", letter)
ok(d and d[0]["label"] == "prior-year amendment", "an amendment request is detected")
ok(d[0]["citation"], "and it carries the clause it falls outside")
eng2 = {"id": "e2", "client_id": "c1"}
r = core.log_scope_event(eng2, d[0], "evidence text")
ok(r["logged"] is True, "a cited out-of-scope event logs")
covered = core.detect_scope("Should I elect S-corp for next year?", letter)
r2 = core.log_scope_event(eng2, covered[0], "x")
ok(r2["logged"] is False and "covers this" in r2["why"],
   "something the letter DOES cover is not logged as scope creep")
bare = core.detect_scope("The books are a mess since our bookkeeper left, can you catch us up?", letter)
r3 = core.log_scope_event(eng2, bare[0], "x")
ok(r3["logged"] is False and "no clause" in r3["why"],
   "with no clause speaking to it, a partner decides — the system does not assert it is out of scope")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.blocker_ages().get("_missing"), "too few blocked engagements → no median")
ok(core.automation().get("_missing"), "an empty log → no automation rate")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs every ROI line is blank")
r2 = core.roi({"engagements": 30, "blocker_days_removed": 5, "daily_wip_value": 40,
               "scope_events_per_year": 50, "capture_rate": 0.6, "avg_scope_value": 1200})
cash = [l for l in r2["lines"] if l["kind"] == "cash_timing"][0]
ok("CASH CONVERSION, NOT REVENUE" in cash["note"],
   "the cycle-time line labels itself cash conversion on its face")
ok(r2["totals"]["cash_timing"]["total"] != r2["totals"]["revenue"]["total"],
   "and it is subtotalled separately from revenue")

section("the seeded firm, end to end")
st = seed.build(60, 12)
ok(st["engagements"] > 60 and st["documents"] > 300, "the seed builds a firm mid-season")

board = core.partner_board()
ok(all(r["blocker"] for r in board["rows"]), "every live engagement on the board names its blocker")
ok(board["at_risk"] is not None, "the board sorts by what blows a deadline first")

c = agents.chaser()
ok(c["bundles"] > 0, "the chaser drafts")
ok(c["held"], "and holds back items that are not chaseable yet, with reasons")
nudges = [d for d in c["drafts"] if d["step"] == "nudge"]
ok(nudges and all("still open" in d["body"] for d in nudges),
   "a nudge tells the client the list is only what is still open")
ok(all(len(set(d["body"].split("; "))) == len(d["body"].split("; ")) for d in nudges),
   "and it never repeats the same item twice in one message")

i = agents.intake()
ok(i["counts"]["flag"] > 0, "the intake flags real mismatches")
ok(i["counts"]["human_queue"] > 0, "and queues the unreadable ones")
demo_flags = [f for f in i["flagged"] if "2024" in f["filename"] or "Beta" in str(f.get("why"))]
ok(demo_flags, "the deliberate wrong-year / wrong-entity demo documents are caught")

msg = agents.client_message("en_demo", "Can I deduct the truck I bought in November? "
                                       "Also we just formed a new LLC for the rental.")
ok(msg["steps"][0]["action"] == "route_to_cpa", "the deductibility question is routed")
ok("refused" in msg["steps"][0], "and it records what it refused to do")
ok(not any("deduct" in (s.get("said") or "").lower() and "yes" in (s.get("said") or "").lower()
           for s in msg["steps"]), "no step answers the question")
ok(any(s["action"] == "log_scope_event" for s in msg["steps"]),
   "and the new entity is logged against the letter in the same pass")

evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")
ok(not any(e["kind"] == "delete_document" for e in evs), "nothing was ever deleted")
ids = [e["id"] for e in evs]
agents.chaser()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("answer_tax_question", "intake", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before,
   "and it adds nothing to the approval queue — a human must not be offered a button "
   "that clicks past a prohibition")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "answer_tax_question"
       for e in store.load("events")),
   "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
