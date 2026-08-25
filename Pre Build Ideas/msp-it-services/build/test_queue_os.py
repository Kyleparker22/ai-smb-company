#!/usr/bin/env python3
"""Queue OS — the honesty suite."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

os.environ["QUEUEOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="queueos-test-")
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


# ---------------------------------------------------------------- triage
for text, kind in [("got a weird email asking me to approve a payment, I clicked the link", "phishing"),
                   ("all our files changed to .locked and there's a note", "ransomware"),
                   ("MFA prompts keep flooding my phone", "mfa_bombing"),
                   ("sign-in from Russia on the CFO account", "account_compromise")]:
    c = core.triage(text)
    ok(c["label"] == "security" and c["kind"] == kind, f"security typed as {kind}")

ok(core.triage("email is down for the whole office")["label"] == "outage", "an office-wide outage ranks")
ok(core.triage("forgot my password again")["label"] == "routine", "a password reset is routine")
ok(core.triage("")["label"] == "human", "empty goes to a person")

ev = core.run_eval()
ok(ev["costly_label"] == "security" and ev["costly_missed"] == 0,
   f"zero missed security signals in the shipped eval ({ev['costly_missed']})")
ok("INCIDENT REPORT" in ev["costly_note"], "the eval names the stake")

# ---------------------------------------------------------------- the close refusal
store.wipe()
store.save("config", {"company": "t"})
store.save("tickets", [
    {"id": "t_sec", "client_id": "c1", "text": "files encrypted", "label": "security",
     "opened_at": iso(now() - timedelta(hours=2))},
    {"id": "t_rt", "client_id": "c1", "text": "printer jam", "label": "routine",
     "opened_at": iso(now() - timedelta(hours=2))},
])
r = agents.close_ticket("t_sec")            # software tries to close
ok("refused" in r, "software cannot close a security ticket")
ok("security engineer" in r["refused"], "…and the refusal names who can")
ok(not store.by_id("tickets", "t_sec").get("resolved_at"), "the ticket stayed open")
ok(any(e["kind"] == "refused" for e in store.events(subject="t_sec")), "the refusal is logged")
r = agents.close_ticket("t_sec", human="sec_engineer")
ok(r.get("closed") and r["by"] == "human:sec_engineer", "a human security engineer can close it")
r = agents.close_ticket("t_rt")
ok(r.get("closed"), "software can close a routine ticket (R2, logged)")

# ---------------------------------------------------------------- sla
store.save("clients", [
    {"id": "c_gold", "name": "GoldCo", "tier": "gold"},
    {"id": "c_none", "name": "NoTierCo", "tier": None},
])
t_breach = {"id": "t1", "client_id": "c_gold", "text": "x",
            "opened_at": iso(now() - timedelta(hours=10))}
s = core.sla_state(t_breach)
ok(s["state"] == "breached", "a gold ticket open 10h is breached (8h resolve)")
t_ok = {"id": "t2", "client_id": "c_gold", "text": "x",
        "opened_at": iso(now() - timedelta(minutes=10))}
ok(core.sla_state(t_ok)["state"] == "inside", "a fresh ticket is inside")
s = core.sla_state({"id": "t3", "client_id": "c_none", "text": "x",
                    "opened_at": iso(now() - timedelta(hours=1))})
ok(s.get("_missing") and "unknowable" in s["_missing"],
   "no tier on the agreement → the clock refuses, never defaults")

store.save("tickets", [t_breach, t_ok,
                       {"id": "t3", "client_id": "c_none", "text": "x",
                        "opened_at": iso(now() - timedelta(hours=1))}])
b = core.sla_board()
ok(b["breached"] == 1 and len(b["unknowable"]) == 1,
   "the board counts breaches and names the unknowable clock")
ok(b["rows"][0]["ticket"] == "t1", "breached sorts first")

# ---------------------------------------------------------------- scope
agreement = {"includes": [{"id": "S-3", "text": "Managed backup and restore", "covers": ["backup"]}],
             "excludes": [{"id": "X-1", "text": "Projects and cabling billed separately", "covers": ["project"]}]}
store.save("clients", [{"id": "c1", "name": "TestCo", "tier": "silver", "agreement": agreement}])
v = core.scope_check({"client_id": "c1", "text": "restore the accounting share from backup"})
ok(v["verdict"] == "in_scope" and v["clause"] == "S-3", "in-scope cites the clause")
v = core.scope_check({"client_id": "c1", "text": "new office cabling for 20 desks"})
ok(v["verdict"] == "out_of_scope" and v["clause"] == "X-1", "out-of-scope cites the exclusion")
v = core.scope_check({"client_id": "c1", "text": "set up the lobby TVs to show dashboards"})
ok(v["verdict"] == "ambiguous", "a category the agreement never mentions is ambiguous")
v = core.scope_check({"client_id": "c1", "text": "please install security updates on the server"})
ok(v["verdict"] == "ambiguous" and "never asserts billable off silence" in v["why"],
   "silence in the agreement is never billable")

# ---------------------------------------------------------------- scope sweep
store.save("tickets", [
    {"id": "s1", "client_id": "c1", "text": "new office cabling for 20 desks", "label": "human",
     "opened_at": iso()},
    {"id": "s2", "client_id": "c1", "text": "set up the lobby TVs", "label": "human",
     "opened_at": iso()},
    {"id": "s3", "client_id": "c1", "text": "printer", "label": "routine", "opened_at": iso()},
])
store.save("approvals", [])
store.save("scope_findings", [])
out = agents.scope_sweep()
ok(out["out_of_scope"] == 1 and out["ambiguous"] == 1, "the sweep files one billable draft, one ambiguous")
ok(len([a for a in store.load("approvals") if a["action"] == "draft_billable"]) == 1,
   "only the cited exclusion produced a billable draft")

# ---------------------------------------------------------------- R0 probes
for action in ("close_security_ticket", "downgrade_security", "auto_remediate_production",
               "send_credentials"):
    r = core.gate.act(action, "probe", "x")
    ok(r.get("refused") and not r["executed"], f"{action} is refused outright")
ok(not any(a["action"] in ("close_security_ticket", "downgrade_security",
                           "auto_remediate_production", "send_credentials")
           for a in core.gate.pending()), "no R0 action reached the approval queue")
ok("bill_client" in core.matrix.never_promote(), "billing can never promote")

# ---------------------------------------------------------------- roi
r = core.roi({})
labels = {l["label"]: l for l in r["lines"]}
ok("THIS IS A MODEL" in r["label"], "the panel labels itself a model")
ok(labels["Out-of-scope work captured"]["value"] is None,
   "revenue line blank without the operator's rate card")
ok(labels["SLA credits avoided"]["kind"] == "scenario", "avoided breaches are a scenario, never a saving")
ok(labels["Security response exposure"]["value"] is None,
   "security head start is never monetized by us")

a = core.automation()
ok(a.get("_missing") or a.get("rate") is not None, "automation counted or refused")

# ---------------------------------------------------------------- new eval phrasings hold
for text, want in (("got an email from the ceo asking for gift cards, seems suspicious", "security"),
                   ("accounting says a large transfer of files left the shared drive overnight", "security"),
                   ("whole office is down, nobody can connect since the storm", "outage")):
    ok(core.triage(text)["label"] == want, f"triage: {text[:44]} → {want}")

# ---------------------------------------------------------------- drafted copy + the brief
store.save("clients", [{"id": "cl9", "name": "Harbor Dental", "tier": "gold",
                        "agreement": {"includes": [], "excludes": [
                            {"id": "X-4", "covers": ["project"],
                             "text": "office moves, cabling and migrations are quoted separately"}]}}])
t9 = {"id": "tk9", "client_id": "cl9", "from": "Rosa M", "opened_at": iso(now()),
      "text": "forgot my password again, sorry"}
store.upsert("tickets", t9)
body = agents._routine_reply_copy(t9)
ok("Rosa" in body and "reset link" in body, "password reply routes through the portal")
ok("We never send passwords in email" in body, "the credential rule is stated in the copy itself")
ok("yourco" not in body.lower(), "white-label: no yourco name in outward copy")

brief = agents.security_brief({"id": "tk10", "client_id": "cl9", "opened_at": iso(now()),
                               "text": "all our files changed to .locked"}, "ransomware")
ok(brief["client"] == "Harbor Dental" and brief["tier"] == "gold", "brief carries the account facts")
ok("isolate the host" in brief["first_moves"], "brief gives the kind-specific first move")
ok(any("never closes" in r for r in brief["rules"]), "brief restates the close rule")
ok("hands touch production" in brief["note"], "the brief is a head start, not a runbook")

v = core.scope_check({"client_id": "cl9", "text": "planning the office move to the new building"})
ok(v["verdict"] == "out_of_scope" and v["clause"] == "X-4", "move is excluded by clause X-4")
bill = agents._billable_copy(v, {"client_id": "cl9", "text": "planning the office move"})
ok("X-4" in bill and "quoted separately" in bill, "billable copy quotes the clause verbatim")
ok("quote first" in bill or "quote" in bill, "a quote path, never an invoice")
ok("invoice" not in bill.lower(), "the word invoice never appears in the scope conversation")

# ---------------------------------------------------------------- recovered, counted
rec = core.recovered_this_week()
ok(rec["replies_sent"] == 0 and rec["billables_approved"] == 0,
   "nothing approved yet → zeros, honestly")
store.log_event("draft_routine_reply", "tk9", "human:dispatcher", "R1", {"approval": "ap1"})
store.log_event("draft_billable", "tk10", "human:owner", "R1", {"approval": "ap2"})
store.log_event("escalate_security", "tk10", "agent:dispatcher", "R2", {"kind": "ransomware"})
rec = core.recovered_this_week()
ok(rec["replies_sent"] == 1 and rec["billables_approved"] == 1 and rec["security_escalations"] == 1,
   "human-approved sends and escalations are counted from the log")
ok("counted" in rec["note"], "recovered names its basis")

# an agent-actor draft event is NOT counted as a send
store.log_event("draft_routine_reply", "tk11", "agent:dispatcher", "R1", {})
ok(core.recovered_this_week()["replies_sent"] == 1,
   "a drafted-but-unsent reply never counts as sent")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
