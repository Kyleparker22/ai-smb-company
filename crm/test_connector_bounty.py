#!/usr/bin/env python3
"""Connector Program v2 — submission bounty, Sourcer scope, and the recruit-at-R1 move.

Everything here runs against IN-MEMORY fixtures (`d=…, commit=False`), never `crm/data.json` and
never the attribution log. The live CRM cannot reach these states yet — the program is pre-launch and
no connector holds a rung — so a test that used real data would prove nothing about the gates.

Guards `decisions/2026-08-11_connector-program-v2.md`. The properties worth failing a build over:
  • bounty arithmetic matches the constants, and is never reported as payable while staged
  • provenance/consent are enforced, because yourco is the caller on a Sourcer contact
  • a duplicate contact cannot be sold twice — the gaming surface of a per-contact bounty
  • nobody verifies their own submission — the bounty pays on that transition
  • recruiting is at R1, and its training still needs an operator's confirmation
"""
import os, sys, json, copy, datetime

CRM = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CRM)
import connector_ladder as ladder
import connector_statements as stmts
import connector_writes as writes
import connector_training as training

OK, FAIL = [], []


def check(name, cond, detail=""):
    (OK if cond else FAIL).append(f"{name}{(' — ' + detail) if detail else ''}")


def refuses(name, fn, expect=None):
    """A refusal must raise ScopeError AND write nothing. Returns the message for inspection."""
    try:
        fn()
    except writes.ScopeError as e:
        msg = str(e)
        check(name, (expect is None or expect.lower() in msg.lower()), msg[:90])
        return msg
    check(name, False, "did NOT refuse")
    return ""


NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
MONTH = datetime.date.today().strftime("%Y-%m")


def fixture():
    """Two connectors, both joined (R0 evidence + R0 training complete), one a downline of the other."""
    r0 = {rec["slug"]: {"at": NOW, "by": "Alice"}
          for rec in training.curriculum().get("R0", [])}
    return {
        "companies": [{"id": "c1", "name": "Northside Dental", "referrer": "Alice"}],
        "deals": [{"id": "d1", "companyId": "c1", "stage": "prospect"}],
        # `kind: internal` + `teamRole: connector` is what `ladder.compute()` looks for; `teamStatus:
        # active` is the signed-agreement evidence that makes R0 real.
        "contacts": [
            {"id": "p1", "name": "Alice", "kind": "internal", "teamRole": "connector",
             "teamStatus": "active"},
            {"id": "p2", "name": "Bob", "kind": "internal", "teamRole": "connector",
             "teamStatus": "active"},
        ],
        "activities": [],
        "meta": {
            "referralTiers": {"rates": [10, 12.5, 15], "thresholds": [6, 11], "override": 1},
            "repRecruiters": {"Bob": "Alice"},
            "connectorTraining": {"Alice": {"R0": {"lessons": r0, "completedAt": NOW}},
                                  "Bob": {"R0": {"lessons": dict(r0), "completedAt": NOW}}},
            "connectorSubmissions": [],
        },
    }


def submission(**over):
    base = {"business": "Northside Dental", "contact": "Dana Reyes", "email": "dana@northside.test",
            "provenance": "my dentist for six years", "consent": "yes"}
    base.update(over)
    return base


# ------------------------------------------------------------------ 1. the ladder move
check("ladder: recruiting unlocks at R1", "recruit_connectors" in ladder.UNLOCKS["R1"])
check("ladder: recruiting no longer at R2", "recruit_connectors" not in ladder.UNLOCKS["R2"])
check("ladder: submitting contacts unlocks at R0", "submit_contacts" in ladder.UNLOCKS["R0"])
check("ladder: an R1 holder may recruit", ladder.can(1, "recruit_connectors"))
check("ladder: an R0 holder may NOT recruit", not ladder.can(0, "recruit_connectors"))
check("ladder: an R0 holder may submit", ladder.can(0, "submit_contacts"))
check("ladder: a non-connector (-1) may not submit", not ladder.can(-1, "submit_contacts"))

# The capability moved rungs; its training must have followed, and must still be operator-confirmed.
team = next((L for L in training.load_lessons()
             if (L.get("unlocks") or "").strip() == "recruit_connectors"), None)
check("training: a lesson unlocks recruiting", team is not None)
if team:
    check("training: the recruiting lesson re-bucketed to R1", team["rung"] == "R1", team["rung"])
    check("training: recruiting still needs an operator's confirmation",
          training.needs_confirmation(team, team["rung"]))
    check("training: ordinary R1 lessons stay self-marked",
          not training.needs_confirmation({"rung": "R1", "unlocks": ""}, "R1"))

# ------------------------------------------------------------------ 2. the fixture holds R0
d = fixture()
state = ladder.compute(d)
check("fixture: Alice holds R0", (state.get("Alice") or {}).get("rungN") == 0,
      str((state.get("Alice") or {}).get("rungN")))

# ------------------------------------------------------------------ 3. submission validation
d = fixture()
ok, why = writes.can_write("Alice", {"kind": "submission", "fields": submission()}, d)
check("submit: a complete submission is allowed", ok, why)

refuses("submit: provenance is required",
        lambda: writes.submit_contact("Alice", submission(provenance=""), d=fixture(), commit=False),
        "how you know them")
refuses("submit: unreachable contact is refused",
        lambda: writes.submit_contact("Alice", submission(email="", phone=""), d=fixture(), commit=False),
        "email or a phone")
refuses("submit: business name is required",
        lambda: writes.submit_contact("Alice", submission(business=""), d=fixture(), commit=False),
        "Business name")
refuses("submit: a bad consent value is refused",
        lambda: writes.submit_contact("Alice", submission(consent="maybe"), d=fixture(), commit=False),
        "consent")
refuses("submit: an yourco-internal field is refused",
        lambda: writes.submit_contact("Alice", submission(retainer="9000"), d=fixture(), commit=False),
        "not a submission field")
refuses("submit: a non-connector is refused",
        lambda: writes.submit_contact("Nobody", submission(), d=fixture(), commit=False),
        "not a connector")

# "unknown" consent is a legitimate answer and must be recordable as itself.
d = fixture()
rec = writes.submit_contact("Alice", submission(consent="unknown"), d=d, commit=False, log=lambda *a, **k: None)
check("submit: unknown consent is recorded, not coerced", rec["consent"] == "unknown", rec["consent"])
check("submit: lands as pending", rec["status"] == "pending", rec["status"])
check("submit: tagged sourcer mode", rec["mode"] == "sourcer")
check("submit: does NOT create a CRM company",
      len(d["companies"]) == 1, f'{len(d["companies"])} companies')

# ------------------------------------------------------------------ 4. duplicates (the gaming surface)
d = fixture()
writes.submit_contact("Alice", submission(), d=d, commit=False, log=lambda *a, **k: None)
refuses("dupe: the same connector cannot resubmit the same contact",
        lambda: writes.submit_contact("Alice", submission(), d=d, commit=False),
        "already submitted")
refuses("dupe: a second connector cannot sell the same business",
        lambda: writes.submit_contact("Bob", submission(contact="Someone Else"), d=d, commit=False),
        "one referrer per company")
refuses("dupe: matched on email even when the business is renamed",
        lambda: writes.submit_contact("Bob", submission(business="Northside Dental Care"), d=d, commit=False))
# A rejected submission must not block a later, legitimate one for the same business.
d["meta"]["connectorSubmissions"][0]["status"] = "rejected"
ok, why = writes.can_write("Bob", {"kind": "submission", "fields": submission()}, d)
check("dupe: a rejected submission stops blocking", ok, why)

# ------------------------------------------------------------------ 5. verification
d = fixture()
rec = writes.submit_contact("Alice", submission(), d=d, commit=False, log=lambda *a, **k: None)
refuses("verify: a connector cannot verify their own submission",
        lambda: writes.verify_submission("Alice", rec["id"], "verified", d=d, commit=False),
        "cannot verify their own")
refuses("verify: an unknown submission is refused",
        lambda: writes.verify_submission("the Founder", "sub-nope", "verified", d=d, commit=False))
refuses("verify: an invented status is refused",
        lambda: writes.verify_submission("the Founder", rec["id"], "paid", d=d, commit=False), "Status must be")
check("verify: the queue holds it before verification",
      [r["id"] for r in writes.pending_submissions(d)] == [rec["id"]])
writes.verify_submission("the Founder", rec["id"], "verified", d=d, commit=False, log=lambda *a, **k: None)
check("verify: status moved", d["meta"]["connectorSubmissions"][0]["status"] == "verified")
check("verify: the operator is on the record",
      d["meta"]["connectorSubmissions"][0]["verifiedBy"] == "the Founder")
check("verify: the queue empties", writes.pending_submissions(d) == [])

# ------------------------------------------------------------------ 6. bounty arithmetic
b = stmts.bounties(d)["Alice"]
check("bounty: verified pays exactly BOUNTY_VERIFIED", b["earned"] == stmts.BOUNTY_VERIFIED, str(b["earned"]))
check("bounty: booked step not yet earned", b["booked"] == 0)
writes.verify_submission("the Founder", rec["id"], "booked", d=d, commit=False, log=lambda *a, **k: None)
b = stmts.bounties(d)["Alice"]
check("bounty: a booked call pays both steps",
      b["earned"] == stmts.BOUNTY_VERIFIED + stmts.BOUNTY_BOOKED, str(b["earned"]))
check("bounty: counted once per step", (b["verified"], b["booked"]) == (1, 1), str((b["verified"], b["booked"])))
writes.verify_submission("the Founder", rec["id"], "client", d=d, commit=False, log=lambda *a, **k: None)
b = stmts.bounties(d)["Alice"]
check("bounty: becoming a client does not pay a third bounty step",
      b["earned"] == stmts.BOUNTY_VERIFIED + stmts.BOUNTY_BOOKED, str(b["earned"]))

d2 = fixture()
writes.submit_contact("Alice", submission(), d=d2, commit=False, log=lambda *a, **k: None)
b2 = stmts.bounties(d2)["Alice"]
check("bounty: a pending submission earns nothing", b2["earned"] == 0, str(b2["earned"]))
check("bounty: pending is counted as pending", b2["pending"] == 1)
writes.verify_submission("the Founder", d2["meta"]["connectorSubmissions"][0]["id"], "rejected",
                         d=d2, commit=False, log=lambda *a, **k: None)
b2 = stmts.bounties(d2)["Alice"]
check("bounty: a rejected submission earns nothing", b2["earned"] == 0, str(b2["earned"]))

# THE honesty rule: accrued is not payable while the program is staged.
check("bounty: not payable while staged", stmts.BOUNTY_PAYABLE is False)
check("bounty: every ledger says so", all(v["payable"] is False for v in stmts.bounties(d).values()))

# ------------------------------------------------------------------ 7. the cap mechanism
d = fixture()
cap, used, left = writes.cap_state("Alice", d)
check("cap: unset by default (the Founder's open number)", cap is None, str(cap))
d["meta"]["connectorSubmissionCap"] = 1
writes.submit_contact("Alice", submission(), d=d, commit=False, log=lambda *a, **k: None)
cap, used, left = writes.cap_state("Alice", d)
check("cap: counts this month's submissions", (cap, used, left) == (1, 1, 0), str((cap, used, left)))
refuses("cap: refuses past the cap",
        lambda: writes.submit_contact("Alice", submission(business="Other Co", email="o@x.test",
                                                         provenance="neighbour"), d=d, commit=False),
        "cap")
# A cap is per connector, not global — Bob is unaffected by Alice's.
ok, why = writes.can_write("Bob", {"kind": "submission", "fields": submission(
    business="Bob's Barber", email="bob@barber.test", provenance="my barber")}, d)
check("cap: is per connector, not global", ok, why)

# ------------------------------------------------------------------ 8. statements include the bounty
d = fixture()
r = writes.submit_contact("Alice", submission(), d=d, commit=False, log=lambda *a, **k: None)
writes.verify_submission("the Founder", r["id"], "booked", d=d, commit=False, log=lambda *a, **k: None)
book = stmts.bounties(d)
check("statement: a connector with no live book still has a bounty ledger",
      "Alice" in book and book["Alice"]["earned"] > 0)

print(f"\n{len(OK)} passed, {len(FAIL)} failed\n")
for f in FAIL:
    print("  FAIL " + f)
if not FAIL:
    for o in OK:
        print("  ok   " + o)
sys.exit(1 if FAIL else 0)
