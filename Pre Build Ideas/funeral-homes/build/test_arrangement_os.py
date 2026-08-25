#!/usr/bin/env python3
"""Arrangement OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["ARRANGEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="arrangeos-test-")
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
ok(core.read_call("my father just passed at the hospice")["label"] == "first_call",
   "a death notification is a first call")
ok(core.read_call("we need to make arrangements for my sister")["label"] == "first_call",
   "arrangement language is a first call")
ok(core.read_call("I'd like to plan ahead for myself")["label"] == "preneed", "pre-need classifies")
ok(core.read_call("how much is cremation with a small service")["label"] == "price_question",
   "a price question classifies")
ok(core.read_call("are the death certificates ready?")["label"] == "document_status",
   "a document ask classifies")
ok(core.read_call("")["label"] == "human", "empty — a person answers, always")

ev = core.run_eval()
ok(ev["costly_label"] == "first_call" and ev["costly_missed"] == 0,
   f"zero missed first calls in the shipped eval ({ev['costly_missed']})")
ok("FAMILY FAILED" in ev["costly_note"], "the eval names the stake")

# first call pages the director; nothing templated beyond logistics
store.wipe()
store.save("config", {"company": "t"})
store.save("calls", [{"id": "c1", "text": "mom died this morning at the hospital"}])
r = agents.handle_call("c1")
ok(r["steps"][0]["action"] == "page_director", "the director is paged")
ok("director is being reached" in r["steps"][0]["said"], "the reply is logistics and compassion routing only")
ok(any(e["detail"].get("action") == "automate_grief_support"
       for e in store.events(kind="refused", subject="c1")),
   "the no-templated-grief refusal is logged")

# ---------------------------------------------------------------- GPL quotes
q = core.quote(["direct_cremation"])
ok(q.get("refused") and "no General Price List on file" in q["refused"],
   "no GPL on file → no numbers, period")
store.save("gpl", [{"key": "direct_cremation", "label": "Direct cremation", "price": 2395},
                   {"key": "urn_standard", "label": "Standard urn", "price": 295}])
q = core.quote(["direct_cremation", "urn_standard"])
ok(q["total"] == 2690 and len(q["lines"]) == 2, "a quote itemizes from the GPL")
ok("never bundle-only" in q["note"], "…and says it is always itemized")
q = core.quote(["direct_cremation", "premium_package_x"])
ok(q.get("refused") and "not on the recorded GPL" in q["refused"],
   "an off-list item refuses the whole quote")
q = core.quote([])
ok(q.get("refused"), "an empty quote refuses")

# ---------------------------------------------------------------- documents
case = {"id": "cs1", "documents": [
    {"kind": "death_certificate", "requested_at": iso(now() - timedelta(days=5)), "touches": []},
    {"kind": "burial_permit", "requested_at": iso(now() - timedelta(days=5)),
     "needed_by": iso(now() + timedelta(days=3)), "touches": []},
    {"kind": "insurance_assignment", "requested_at": iso(now() - timedelta(days=5)),
     "received_at": iso(now() - timedelta(days=1)), "touches": []},
]}
docs = core.case_documents(case)
ok(sum(1 for d in docs if d["state"] == "open") == 2, "open documents are counted")
permit = next(d for d in docs if d["kind"] == "burial_permit")
ok(permit.get("days_left") in (2, 3) and "service date depends" in permit["label"],
   "a dated permit carries its date alert")

plan = core.chase_plan(case["documents"][0])
ok(plan["action"] == "draft_chase", "an open item past cooldown drafts a chase")
item = dict(case["documents"][0], touches=[{"at": iso(now() - timedelta(days=30))}] * core.CHASE_MAX_TOUCHES)
ok(core.chase_plan(item)["action"] == "human", "an exhausted ladder → the director calls")

# ---------------------------------------------------------------- preneed ledger
store.save("preneed", [{"id": "p1", "funding_recorded": True},
                       {"id": "p2", "funding_recorded": False}])
pl = core.preneed_ledger()
ok(pl["contracts"] == 2 and pl["funded_recorded"] == 1, "the ledger counts")
ok("unmeasured, not assumed" in pl["funding_note"], "unfunded contracts are unmeasured, not assumed")

# ---------------------------------------------------------------- R0 probes
for action in ("automate_grief_support", "quote_off_gpl", "handle_remains_decision",
               "pressure_sale_at_need"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("automate_grief_support", "quote_off_gpl",
                           "handle_remains_decision", "pressure_sale_at_need")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Pre-need follow-ups converted"]["value"] is None,
   "the pre-need line is blank without the operator's conversion")
fc = labels["First calls that reached you"]
ok(fc["kind"] == "scenario" and fc["value"] is None,
   "an answered 2am call is never framed as revenue — yours or blank")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("the coroner's office gave us your number this morning", "first_call"),
                   ("what does a graveside burial service cost", "price_question"),
                   ("we want to pre-arrange for my wife and me together", "preneed")):
    ok(core.read_call(text)["label"] == want, f"triage: {text[:44]} → {want}")

# ---------------------------------------------------------------- the brief + copy
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

brief = agents.first_call_brief({"text": "my father just passed at the hospice",
                                 "at": _iso(_now())})
ok("every human word comes from a human" in brief["rule"], "the brief restates the rule")
ok(any("callback" in c for c in brief["capture"]), "the capture list is logistics only")
ok(not any(w in " ".join(brief["capture"]).lower() for w in ("condolence", "comfort", "sorry")),
   "the desk captures facts — it offers no words of its own")

case9 = {"id": "cs9", "documents": [{"kind": "death_certificate",
                                     "requested_at": _iso(_now() - timedelta(days=5)),
                                     "needed_by": _iso(_now() + timedelta(days=4))}]}
store.upsert("cases", case9)
body = agents._chase_copy(case9, case9["documents"][0], 1)
ok("death certificate" in body and "cs9" in body, "chase copy carries the item and case number")
ok("vital records" in body, "chase copy names the institution")
ok("so the family doesn't have to" in body, "the chase names who it shields")
ok(not any(w in body.lower() for w in ("grief", "loss", "condolence")),
   "institution-facing copy never touches the family's grief")
final = agents._chase_copy(case9, case9["documents"][0], core.CHASE_MAX_TOUCHES)
ok("Final written follow-up" in final and "director" in final,
   "the last touch names itself final and moves to the director's call")

pn = agents._preneed_copy({"from": "Miriam"})
ok("Miriam" in pn and "no decisions required" in pn, "preneed copy is unhurried, no pressure")
ok("itemized price list" in pn, "the GPL rides along either way")
ok("yourco" not in (body + pn).lower(), "white-label: no yourco name in outward copy")

# ---------------------------------------------------------------- recovered, counted
base = core.recovered_this_week()
case9["documents"][0]["received_at"] = _iso(_now() - timedelta(days=1))
store.upsert("cases", case9)
store.log_event("draft_document_chase", "cs9", "human:caredesk", "R1", {})
rec = core.recovered_this_week()
ok(rec["documents_received"] == base["documents_received"] + 1,
   "a received document is counted from the case record")
ok(rec["chases_sent"] == base["chases_sent"] + 1,
   "human-sent chases are counted; agent drafts are not")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
