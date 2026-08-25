#!/usr/bin/env python3
"""Crew OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["CREWOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="crewos-test-")
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
ok(core.classify_report("found the back door unlocked when we arrived")["label"] == "security",
   "an unlocked door is a security incident")
ok(core.classify_report("alarm was going off at suite 400")["label"] == "security",
   "an alarm is a security incident")
ok(core.classify_report("what's the alarm code for the medical building?")["label"] == "access_request",
   "an alarm-code ask is an access request")
ok(core.classify_report("restrooms on 3 weren't done last night")["label"] == "complaint",
   "a quality complaint classifies")
ok(core.classify_report("we're out of liners at the bank")["label"] == "supply", "supply classifies")
ok(core.classify_report("")["label"] == "human", "empty routes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "security" and ev["costly_missed"] == 0,
   f"zero missed security incidents in the shipped eval ({ev['costly_missed']})")
ok("MEETS ITS INSURER" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- the access refusal
store.wipe()
store.save("config", {"company": "t"})
store.save("reports", [
    {"id": "r_acc", "contract_id": "c1", "text": "can you text me the lockbox combo for suite 200"},
    {"id": "r_sec", "contract_id": "c1", "text": "window by the loading dock is smashed"},
])
r = agents.handle_report("r_acc")
ok(r["steps"][0].get("refused") and "moves through this system" in r["steps"][0]["refused"],
   "an access ask is refused with the rule stated")
ok(any(e["detail"].get("action") == "share_access_info"
       for e in store.events(kind="refused", subject="r_acc")), "the access refusal is logged")

# security close discipline
r = agents.handle_report("r_sec")
ok(r["steps"][0]["action"] == "escalate_security", "a security report escalates")
r = agents.close_incident("r_sec")
ok("refused" in r, "software cannot close a security incident")
ok(not store.by_id("reports", "r_sec").get("closed_at"), "…and it stayed open")
r = agents.close_incident("r_sec", human="supervisor")
ok(r.get("closed"), "a human can close it after follow-up")

# ---------------------------------------------------------------- inspection evidence
store.save("inspections", [
    {"id": "i_fresh", "contract_id": "c_ok", "at": iso(now() - timedelta(days=3)), "score": 4.6},
    {"id": "i_stale", "contract_id": "c_stale", "at": iso(now() - timedelta(days=45)), "score": 4.8},
])
v = core.clean_claim("c_ok")
ok(v["assertable"] and v["inspection"] == "i_fresh", "a fresh inspection makes the claim assertable")
v = core.clean_claim("c_stale")
ok(not v["assertable"] and "no inspection record inside" in v["refused"],
   "a stale inspection does not back a claim")
v = core.clean_claim("c_none")
ok(not v["assertable"], "no inspection at all → cannot assert")

# a complaint on an uninspected contract gets the HONEST draft
store.save("reports", [{"id": "r_cmp", "contract_id": "c_none",
                        "text": "trash was missed in the corner offices again"}])
store.save("approvals", [])
r = agents.handle_report("r_cmp")
ok(r["steps"][0]["action"] == "draft_honest_reply", "the reply admits the missing inspection")
ok(any(e["detail"].get("action") == "assert_cleaned_without_inspection"
       for e in store.events(kind="refused", subject="r_cmp")), "the evidence refusal is logged")

# ---------------------------------------------------------------- coverage access rule
store.save("contracts", [{"id": "b1", "name": "Bank", "value_month": 3000}])
store.save("crew", [
    {"id": "w1", "name": "Keyed", "access": ["b1"], "assigned": [], "out_tonight": False},
    {"id": "w2", "name": "NoKey", "access": [], "assigned": [], "out_tonight": False},
    {"id": "w3", "name": "Out", "access": ["b1"], "assigned": [], "out_tonight": True},
])
cb = core.coverage_board()
ok(len(cb["uncovered"]) == 1, "the unassigned contract shows uncovered")
u = cb["uncovered"][0]
ok([c["who"] for c in u["candidates"]] == ["Keyed"], "only the keyed, present crew member is proposed")
ok(any("never improvised" in b["why"] for b in u["blocked"]),
   "the keyless member is blocked with the reason named")

# ---------------------------------------------------------------- R0 probes
for action in ("share_access_info", "close_security_incident", "assert_cleaned_without_inspection"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("share_access_info", "close_security_incident",
                           "assert_cleaned_without_inspection")
           for a in core.gate.pending()), "no R0 action reached the approval queue")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Uncovered nights caught"]["value"] is None,
   "the coverage line is blank without the operator's churn share")
ok(labels["The access discipline"]["kind"] == "scenario",
   "access discipline is never monetized by us")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("loading dock door was propped open with a brick", "security"),
                   ("need the door code for the annex tonight", "access_request"),
                   ("floors on 2 still dirty according to the property manager", "complaint")):
    ok(core.classify_report(text)["label"] == want, f"triage: {text[:42]} → {want}")

# ---------------------------------------------------------------- drafted copy + the brief
from datetime import timedelta
from _kit.store import iso as _iso, now as _now

store.upsert("contracts", {"id": "ct9", "name": "Meridian Medical Plaza",
                           "client": "Meridian"})
store.upsert("inspections", {"id": "in9", "contract_id": "ct9", "score": 94,
                             "at": _iso(_now() - timedelta(days=5))})
m9 = {"id": "rp9", "contract_id": "ct9", "at": _iso(_now()),
      "text": "restrooms on 3 weren't done last night per the client"}
store.upsert("reports", m9)
claim = core.clean_claim("ct9")
body = agents._complaint_reply_copy(m9, claim)
ok("Meridian Medical Plaza" in body and "94" in body and "in9" in body,
   "with an inspection the reply cites site, score, and record id")
ok("re-do" in body and "photo-confirm" in body, "the make-right is a re-do, not a debate")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")

store.save("inspections", [])
claim = core.clean_claim("ct9")
body2 = agents._complaint_reply_copy(m9, claim)
ok("we won't" in body2 and "booking an inspection" in body2,
   "without an inspection the reply admits the gap instead of arguing")
ok("re-does the" in body2, "the gap reply still leads with the re-do")

brief = agents.security_brief({"contract_id": "ct9", "at": _iso(_now()),
                               "text": "back door unlocked"})
ok(brief["site"] == "Meridian Medical Plaza", "brief carries the site")
ok("before they find it themselves" in brief["first_move"],
   "the first move is the client call, in order")
ok(any("never closes" in r for r in brief["rules"]), "brief restates the close rule")

# ---------------------------------------------------------------- recovered, counted
base = core.recovered_this_week()
ok(base["replies_sent"] == 0, "no human sends yet → zero, honestly")
store.log_event("draft_complaint_reply", "rp9", "human:supervisor", "R1", {})
agents.close_incident("rp9", human="supervisor")
rec = core.recovered_this_week()
ok(rec["replies_sent"] == base["replies_sent"] + 1
   and rec["incidents_closed"] == base["incidents_closed"] + 1,
   "human sends and human closes are counted from the log")
ok("counted" in rec["note"], "recovered names its basis")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
