#!/usr/bin/env python3
"""Protocol OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["PROTOOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="protoos-test-")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agents, core, seed
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


seed.build(n=200)

# ---------------------------------------------------------------- triage
for text, kind in [("my face and lips are swelling up", "anaphylaxis"),
                   ("I can't breathe properly", "breathing"),
                   ("chest pain and my heart is racing", "cardiac"),
                   ("the site is hot and swollen with pus", "injection_site"),
                   ("I fainted this morning", "neuro"),
                   ("vomiting nonstop since yesterday", "severe_gi")]:
    c = core.read_message(text)
    ok(c["label"] == "urgent", f"'{text[:28]}…' is urgent")
    ok(c["kind"] == kind, f"'{text[:28]}…' is typed as {kind}")

for text in ["should I increase my dose", "is it normal to feel tired",
             "can I combine this with my other medication", "any side effects to expect"]:
    ok(core.read_message(text)["label"] == "clinical", f"'{text[:28]}…' is clinical")
for text in ["I need a receipt", "can I reschedule to Friday", "when is my next shipment"]:
    ok(core.read_message(text)["label"] == "admin", f"'{text[:28]}…' is admin")
ok(core.read_message("hello")["label"] == "unclear", "an unmatched message is unclear, not guessed")
ok("rather than the system guessing" in core.read_message("hello")["why"],
   "unclear says a human reads it")

# urgency beats everything: a refill word plus a symptom is still urgent
c = core.read_message("I need a refill but my face is swelling")
ok(c["label"] == "urgent", "a symptom inside an admin message is still urgent")

# ---------------------------------------------------------------- the exclusion
allp = store.load("patients")
excluded = [p for p in allp if p["status"] in core.NEVER_CONTACT]
ok(len(excluded) > 0, "the seed contains permanently un-contactable patients")
reach = {p["id"] for p in core.contactable()}
ok(not (reach & {p["id"] for p in excluded}), "contactable() cannot see an excluded patient")
ok(all(r["patient"] in reach for r in core.due_and_lapsing()),
   "the due/lapsing list only ever contains contactable patients")
ok(all(r["patient"] in reach for r in core.silent_after_change()),
   "the quiet-after-change list only ever contains contactable patients")

for st in core.NEVER_CONTACT:
    p = next((x for x in excluded if x["status"] == st), None)
    if not p:
        continue
    r = agents.draft_refill_nudge(p["id"])
    ok(r.get("refused") is not None, f"a {st} patient can never be nudged")
    ok(r["status"] == st, f"the refusal names the {st} status")

ok(core.matrix.rung_for("contact_excluded")["rung"] == "R0", "contacting an excluded patient is R0")
ok("contact_excluded" in core.matrix.never_promote(), "it can never be promoted")

# ---------------------------------------------------------------- the clinical refusals
for a in ("clinical_advice", "adjust_dose", "interpret_labs", "contact_excluded"):
    ok(core.matrix.rung_for(a)["rung"] == "R0", f"{a} is R0")
    ok(a in core.matrix.never_promote(), f"{a} is never promotable")
    ok(core.matrix.promotable(a, streak=50000)["promote"] is False, f"no streak promotes {a}")

r = agents.answer_clinical("should I double my dose?")
ok(r["refused"] is True, "a clinical question is refused")
ok("can't advise" in r["reply"], "the refusal is said to the patient")
ok(core.URGENT_INSTRUCTION in r["reply"], "the refusal still carries the emergency instruction")

r = agents.adjust_dose("pt0001", "+1 step")
ok(r["refused"] is True, "a dose change is refused")
ok("prescriber" in r["why"], "the refusal names whose decision it is")

before = len(core.gate.pending())
res = core.gate.act("interpret_labs", "inbox", "lab1", {})
ok(res.get("refused") is True, "interpreting a lab is refused outright")
ok(len(core.gate.pending()) == before, "an R0 never becomes a clickable approval")

# ---------------------------------------------------------------- the cycle computes from their own data
rows = core.due_and_lapsing()
ok(len(rows) > 0, "the cycle produces rows")
unknown = [r for r in rows if r.get("state") == "unknown"]
for u in unknown:
    ok("_missing" in u, "a patient with no interval or fill is 'unknown' with a reason, never assumed")

p = {"id": "ptTEST", "name": "Test Patient", "status": "active", "since": iso(now())}
store.upsert("patients", p)
store.upsert("protocols", {"patient": "ptTEST", "name": "P", "interval_days": 28,
                           "last_fill": iso(now() - timedelta(days=50)),
                           "started_at": iso(now() - timedelta(days=200)),
                           "cycles_filled": 5, "last_change": None})
row = next(r for r in core.due_and_lapsing() if r["patient"] == "ptTEST")
ok(row["state"] == "lapsing", "50 days on a 28-day interval is lapsing")
store.upsert("protocols", {"patient": "ptTEST", "name": "P", "interval_days": 28,
                           "last_fill": iso(now() - timedelta(days=25)),
                           "started_at": iso(now() - timedelta(days=200)),
                           "cycles_filled": 5, "last_change": None})
row = next(r for r in core.due_and_lapsing() if r["patient"] == "ptTEST")
ok(row["state"] == "due", "25 days on a 28-day interval is due, not overdue")

# ---------------------------------------------------------------- quiet after a change
store.upsert("protocols", {"patient": "ptTEST", "name": "P", "interval_days": 28,
                           "last_fill": iso(now() - timedelta(days=10)),
                           "started_at": iso(now() - timedelta(days=200)),
                           "cycles_filled": 5,
                           "last_change": iso(now() - timedelta(days=40))})
sil = [s for s in core.silent_after_change() if s["patient"] == "ptTEST"]
ok(len(sil) == 1, "a patient quiet 40 days after a change is surfaced")
ok("a person calls" in sil[0]["action"], "the quiet list prescribes a human call")
ok("draft" not in sil[0], "the quiet list deliberately carries no message draft")

store.upsert("messages", {"id": "mTEST", "patient": "ptTEST", "at": iso(now()),
                          "text": "hi", "handled_at": None, "label": None})
ok(not [s for s in core.silent_after_change() if s["patient"] == "ptTEST"],
   "once they message, they leave the quiet list")

# ---------------------------------------------------------------- nudges are drafts
r = agents.draft_refill_nudge("ptTEST")
ok("draft" in r, "a nudge produces a draft")
ok(r.get("approval"), "the draft sits at the approval gate")
ok(r["rung"] == "R1", "patient outreach is R1")
for word in ("dose", "mg", "increase"):
    ok(word not in r["draft"].lower(), f"the draft contains no '{word}'")

# ---------------------------------------------------------------- the sweep
out = agents.run_all()
ok(out["excluded_unreachable"] == len(excluded), "the sweep reports who it could never reach")
ok("never loads one" in out["note"], "the sweep states the exclusion is structural")
nudged = {a["subject"] for a in store.load("approvals")}
ok(not (nudged & {p["id"] for p in excluded}), "the sweep never drafted to an excluded patient")

# ---------------------------------------------------------------- eval
ev = core.run_eval()
ok(ev["costly_label"] == "urgent", "the costly class is an urgent message")
ok(ev["costly_missed"] == 0, "no urgent message is misfiled")
ok(ev["costly_recall"] == 1.0, "every urgent message is caught")
ok("filed as a refill request" in ev["costly_note"].lower(), "the eval names the failure it guards")

# ---------------------------------------------------------------- numbers refuse
store.save("protocols", [])
cr = core.continuation_rate()
ok("_missing" in cr and cr["rate"] is None, "continuation refuses with nothing started, never 0")

seed.build(n=200)
cr = core.continuation_rate()
ok("_missing" not in cr and 0.0 <= cr["rate"] <= 1.0, "continuation computes on a real book")

r = core.roi({})
ok(any(l.get("value") is None for l in r["lines"]), "ROI blanks without operator inputs")
scen = [l for l in r["lines"] if l["kind"] == "scenario"]
ok(scen and "never monetized by us" in (scen[0].get("assumption") or ""),
   "safety routing is never monetized")
r2 = core.roi({"urgent_value": "9000"})
ok(r2["totals"]["scenario"]["total"] == 9000, "the scenario totals separately")
ok(r2["totals"]["revenue"]["total"] != 9000, "a scenario is never revenue")
ts = [l for l in r2["lines"] if l["kind"] == "time_saved"]
ok(ts and "never summed into revenue" in (ts[0].get("note") or ""), "time saved stays out of revenue")

au = core.automation()
ok("rate" in au or "_missing" in au, "automation is counted or refused")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
