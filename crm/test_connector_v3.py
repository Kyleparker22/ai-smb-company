#!/usr/bin/env python3
"""Connector Console v3 — the six builds, and the refusals that make them worth having.

In-memory fixtures throughout (`d=…, commit=False`): the live CRM is pre-launch, no connector holds a
rung, and nothing here can be reached with real data — a test against `crm/data.json` would prove
nothing about any of these gates.

Guards `decisions/2026-08-13_connector-console-v3.md`. What is worth failing a build over is almost
never the happy path — it is the six places this code must REFUSE:

  • ghost      — no dollar figure off too few referrals, off unmeasured stages, or with no history
  • calibration— no score below MIN_RESOLVED, and no revising a prediction after the fact
  • escrow     — a lost deal is not a breach; only yourco's own conduct is
  • approvals  — nobody decides on somebody else's draft; a complaint resets the rung to A0
  • perks      — a grant cannot be started for a book that has not earned it
  • intake     — identity comes from the channel, never the message body; provenance is never invented
"""
import os, sys, json, datetime, tempfile

CRM = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(CRM)
sys.path.insert(0, CRM)
sys.path.insert(0, os.path.join(ROOT, "runtime"))

import connector_ladder as ladder
import connector_statements as stmts
import connector_writes as writes
import connector_training as training
import connector_ghost as cghost
import connector_calibration as ccal
import connector_escrow as cesc
import connector_approvals as capr
import connector_perks as cperk
import connector_intake as intake

OK, FAIL = [], []
NOLOG = lambda *a, **k: None
NOW = datetime.datetime.now(datetime.timezone.utc)
ISO = NOW.isoformat(timespec="seconds")


def check(name, cond, detail=""):
    (OK if cond else FAIL).append(f"{name}{(' — ' + detail) if detail else ''}")


def refuses(name, fn, exc, expect=None):
    try:
        fn()
    except exc as e:
        check(name, (expect is None or expect.lower() in str(e).lower()), str(e)[:80])
        return
    check(name, False, "did NOT refuse")


def ago(days):
    return (NOW - datetime.timedelta(days=days)).isoformat(timespec="seconds")


def fixture(n_live=1, retainer=3000):
    r0 = {L["slug"]: {"at": ISO, "by": "Alice"} for L in training.curriculum().get("R0", [])}
    companies = [{"id": f"c{i}", "name": f"Co{i}", "referrer": "Alice"} for i in range(n_live)]
    deals = [{"id": f"d{i}", "companyId": f"c{i}", "stage": "live", "retainer": retainer,
              "stageSince": ago(200)} for i in range(n_live)]
    return {
        "companies": companies, "deals": deals, "activities": [],
        "contacts": [{"id": "p1", "name": "Alice", "kind": "internal", "teamRole": "connector",
                      "teamStatus": "active", "email": "alice@x.test", "phone": "727-555-1111"},
                     {"id": "p2", "name": "Bob", "kind": "internal", "teamRole": "connector",
                      "teamStatus": "active"}],
        "meta": {"referralTiers": {"rates": [10, 12.5, 15], "override": 1},
                 "connectorTraining": {"Alice": {"R0": {"lessons": r0, "completedAt": ISO}},
                                       "Bob": {"R0": {"lessons": dict(r0), "completedAt": ISO}}},
                 "connectorSubmissions": [], "connectorApprovals": [],
                 "connectorPredictions": [], "connectorIncidents": []},
    }


def sub(i, connector="Alice", status="verified", submitted=None, verified=None, business=None):
    return {"id": f"s{i}", "connector": connector, "mode": "sourcer", "status": status,
            "business": business or f"Biz{i}", "contact": "An Owner", "email": f"o{i}@x.test",
            "phone": "", "provenance": "known them for years", "consent": "yes", "note": "",
            "submittedAt": submitted or ISO, "verifiedAt": verified}


# ═══════════════════════════════════════════════════ 1. tier basis → MRR
t = {"rates": [10, 12.5, 15]}
check("tier: banding is MRR by default", stmts._tier_basis(t) == "mrr")
check("tier: $14,999 is tier 1", stmts._tier(14_999, t)[0] == 1)
check("tier: $15,000 is tier 2", stmts._tier(15_000, t)[0] == 2)
check("tier: $29,999 is still tier 2", stmts._tier(29_999, t)[0] == 2)
check("tier: $30,000 is tier 3", stmts._tier(30_000, t)[0] == 3)
# The pathology the change exists to kill.
big = {"active": [{"mrr": 10_000}] * 3}
small = {"active": [{"mrr": 1_000}] * 6}
check("tier: 3×$10k now out-ranks 6×$1k",
      stmts._tier(stmts.tier_input(big, t), t)[1] > stmts._tier(stmts.tier_input(small, t), t)[1],
      f'{stmts._tier(stmts.tier_input(big, t), t)[1]}% vs {stmts._tier(stmts.tier_input(small, t), t)[1]}%')
# The bands are round Core multiples, and they are ONE CLIENT LOOSER than the old count rule at each
# end. An earlier version of this file asserted "still crosses" as if the move were like-for-like —
# it is not, and the test now pins the actual (deliberate) difference so nobody restates it wrongly.
core = lambda n: {"active": [{"mrr": stmts.CORE_FLOOR}] * n}
check("tier: 5 Core clients reach 12.5% (the count rule needed 6)",
      stmts._tier(stmts.tier_input(core(5), t), t)[1] == 12.5)
check("tier: 4 Core clients do not", stmts._tier(stmts.tier_input(core(4), t), t)[1] == 10)
check("tier: 10 Core clients reach 15% (the count rule needed 11)",
      stmts._tier(stmts.tier_input(core(10), t), t)[1] == 15)
check("tier: 9 Core clients do not", stmts._tier(stmts.tier_input(core(9), t), t)[1] == 12.5)
# The old count rule, for the record — what the bands are being compared AGAINST.
_count = {"rates": [10, 12.5, 15], "basis": "count", "thresholds": [6, 11]}
check("tier: the legacy rule really did need 6 and 11",
      stmts._tier(5, _count)[1] == 10 and stmts._tier(6, _count)[1] == 12.5
      and stmts._tier(10, _count)[1] == 12.5 and stmts._tier(11, _count)[1] == 15)
check("tier: legacy count basis still honoured",
      stmts._tier(6, {"rates": [10, 12.5, 15], "basis": "count"})[0] == 2)
_nx, note = stmts.tier_progress_note({"active": [{"mrr": 3000}] * 2}, t)
check("tier: the gap is quoted in dollars AND clients", "$" in note and "client" in note, note)

# ═══════════════════════════════════════════════════ 2. ghost — grading yourco
d = fixture(n_live=1)
g = cghost.compute("Alice", d, ghost_data={"ghost": [], "measuredRungs": 0, "totalRungs": 5})
check("ghost: no referrals on the board → no figure", g["commissionGap"] is None and not g["enough"])
check("ghost: and it says why", "nothing to compare" in g["why"].lower(), g["why"])

d = fixture(n_live=4)
rows = [{"id": f"d{i}", "company": f"Co{i}", "real": "proposal", "ghost": "live",
         "rungsBehind": 2, "rungsAhead": 0, "daysBehind": 30, "priced": True,
         "evGap": 1000, "unpricedRungs": [], "explain": "x"} for i in range(4)]
g = cghost.compute("Alice", d, ghost_data={"ghost": rows, "measuredRungs": 5, "totalRungs": 5})
check("ghost: gap is the CONNECTOR's commission, not yourco's EV",
      g["commissionGap"] == 4 * 1000 * g["rate"] / 100, str(g["commissionGap"]))
check("ghost: counts what is behind pace", g["behind"] == 4)

two = cghost.compute("Alice", fixture(n_live=2), ghost_data={"ghost": rows[:2], "measuredRungs": 5, "totalRungs": 5})
check("ghost: refuses a book-level figure below the sample floor",
      two["commissionGap"] is None and not two["enough"])
check("ghost: an anecdote is named as one", "anecdote" in two["why"].lower())

unp = [dict(r, priced=False, evGap=None, unpricedRungs=["audit"]) for r in rows]
g = cghost.compute("Alice", fixture(n_live=4), ghost_data={"ghost": unp, "measuredRungs": 1, "totalRungs": 5})
check("ghost: unpriced stays unpriced — no invented number", g["commissionGap"] is None)
check("ghost: unpriced rows still show a POSITION", all(r["ghost"] for r in g["rows"]))
check("ghost: and it blames yourco's missing history, not the connector",
      "measured pace" in g["why"] or "not run enough" in g["why"], g["why"])

g = cghost.compute("Alice", fixture(n_live=4), ghost_data={"ghost": [], "unavailable": "no git"})
check("ghost: unreadable history → refusal, never zero", g["commissionGap"] is None)
check("ghost: never another connector's book",
      cghost.compute("Bob", fixture(n_live=4),
                     ghost_data={"ghost": rows, "measuredRungs": 5, "totalRungs": 5}) is None
      or cghost.compute("Bob", fixture(n_live=4),
                        ghost_data={"ghost": rows, "measuredRungs": 5, "totalRungs": 5})["rows"] == [])

# ═══════════════════════════════════════════════════ 3. calibration
d = fixture()
c = ccal.compute("Alice", d)
check("calibration: no predictions → no score", c["brier"] is None and not c["enough"])
for i in range(4):
    ccal.predict("Alice", f"c{i}x", 80, d=d, commit=False, log=NOLOG)
    ccal.resolve(f"c{i}x", "client", d=d, commit=False, log=NOLOG)
c = ccal.compute("Alice", d)
check("calibration: still refuses below the floor", c["brier"] is None, str(c["resolved"]))
check("calibration: and says how many more are needed", "1 more" in c["why"] or "more to go" in c["why"], c["why"])
ccal.predict("Alice", "c9x", 80, d=d, commit=False, log=NOLOG)
ccal.resolve("c9x", "client", d=d, commit=False, log=NOLOG)
c = ccal.compute("Alice", d)
check("calibration: scores at the floor", c["brier"] is not None and c["enough"])
check("calibration: 5×80% all correct is well calibrated but optimistic",
      c["brier"] < 0.05 and c["bias"] < 0, f"brier {c['brier']} bias {c['bias']}")
check("calibration: priority never drops below 1.0", c["priority"] >= 1.0)
check("calibration: priority is capped", c["priority"] <= ccal.PRIORITY_MAX)
refuses("calibration: cannot revise a call after the fact",
        lambda: ccal.predict("Alice", "c0x", 10, d=d, commit=False, log=NOLOG),
        ccal.PredictionError, "already called")
refuses("calibration: confidence must be a probability",
        lambda: ccal.predict("Alice", "zz", 140, d=d, commit=False, log=NOLOG),
        ccal.PredictionError, "between 0 and 100")
refuses("calibration: a non-connector cannot predict",
        lambda: ccal.predict("Nobody", "zz", 50, d=d, commit=False, log=NOLOG),
        ccal.PredictionError, "not a connector")

# ═══════════════════════════════════════════════════ 4. escrow
d = fixture()
d["meta"]["connectorSubmissions"] = [sub(1, submitted=ISO, verified=ISO)]
e = cesc.compute(None, d).get("Alice", {"breaches": []})
check("escrow: a submission handled on time is no breach", not e["breaches"])
d["meta"]["connectorSubmissions"] = [sub(1, submitted=ago(9), verified=ago(6))]
e = cesc.compute(None, d)["Alice"]
kinds = {b["kind"] for b in e["breaches"]}
check("escrow: late verification is caught from the record's own timestamps", "verify_late" in kinds)
check("escrow: verified-then-abandoned is caught", "never_contacted" in kinds)
check("escrow: both are computed, not asserted", e["computedCount"] == 2 and e["loggedCount"] == 0)
check("escrow: accrues but is never payable while staged", e["payable"] is False and e["owed"] > 0)
# The distinction the whole instrument rests on.
d2 = fixture()
d2["meta"]["connectorSubmissions"] = [sub(1, status="rejected", submitted=ISO, verified=ISO)]
e2 = cesc.compute(None, d2).get("Alice", {"breaches": []})
check("escrow: a referral that simply didn't work out is NOT a breach", not e2["breaches"])
d3 = fixture()
d3["meta"]["connectorSubmissions"] = [sub(1, status="booked", submitted=ago(30), verified=ago(29))]
e3 = cesc.compute(None, d3)["Alice"]
check("escrow: a booked contact can't be 'never contacted'",
      "never_contacted" not in {b["kind"] for b in e3["breaches"]})
refuses("escrow: a computed breach cannot be entered by hand",
        lambda: cesc.log_incident("the Founder", "s1", "verify_late", d=d3, commit=False, log=NOLOG),
        writes.ScopeError, "computed")
refuses("escrow: an incident must name the operator",
        lambda: cesc.log_incident("", "s1", "complaint", d=d3, commit=False, log=NOLOG),
        writes.ScopeError)

# ═══════════════════════════════════════════════════ 5. approvals
d = fixture()
d["meta"]["connectorSubmissions"] = [sub(i) for i in range(25)]
check("approvals: everyone starts on the gate", capr.rung_for("Alice", d)["key"] == "A0")
refuses("approvals: nothing is drafted to an unverified contact",
        lambda: capr.draft_for("the Founder", "s99", "hi", d=d, commit=False, log=NOLOG),
        capr.ApprovalError, "no such submission")
d["meta"]["connectorSubmissions"].append(sub(50, status="pending"))
refuses("approvals: a pending submission gets no draft",
        lambda: capr.draft_for("the Founder", "s50", "hi", d=d, commit=False, log=NOLOG),
        capr.ApprovalError, "not been verified")
r = capr.draft_for("the Founder", "s0", "Hi — Alice suggested we speak.", d=d, commit=False, log=NOLOG)
refuses("approvals: nobody decides on someone else's draft",
        lambda: capr.decide("Bob", r["id"], "approved", d=d, commit=False, log=NOLOG),
        capr.ApprovalError, "someone else's")
capr.decide("Alice", r["id"], "approved", d=d, commit=False, log=NOLOG)
for i in range(1, 5):
    x = capr.draft_for("the Founder", f"s{i}", "hi", d=d, commit=False, log=NOLOG)
    capr.decide("Alice", x["id"], "approved", d=d, commit=False, log=NOLOG)
check("approvals: A1 is earned on 5 clean approvals", capr.rung_for("Alice", d)["key"] == "A1")
x = capr.draft_for("the Founder", "s5", "hi", d=d, commit=False, log=NOLOG)
check("approvals: an A1 draft carries a release deadline stamped at draft time", bool(x["releaseAfter"]))
capr.decide("Alice", x["id"], "edited", edited="my own words", d=d, commit=False, log=NOLOG)
check("approvals: an edit means the draft was wrong, so the streak resets",
      capr.rung_for("Alice", d)["key"] == "A0")
for i in range(6, 21):
    x = capr.draft_for("the Founder", f"s{i}", "hi", d=d, commit=False, log=NOLOG)
    capr.decide("Alice", x["id"], "approved", d=d, commit=False, log=NOLOG)
check("approvals: A2 is earned on 15 clean", capr.rung_for("Alice", d)["key"] == "A2")
x = capr.draft_for("the Founder", "s21", "hi", d=d, commit=False, log=NOLOG)
check("approvals: at A2 yourco proceeds and it is still on the record",
      x["status"] == "released" or any(rr.get("status") == "released"
                                       for rr in d["meta"]["connectorApprovals"]))
d["meta"]["connectorIncidents"].append({"connector": "Alice", "kind": "complaint", "at": ISO})
check("approvals: one complaint puts them back on the gate", capr.rung_for("Alice", d)["key"] == "A0")
d["meta"]["connectorApprovalHold"] = {"Alice": True}
check("approvals: asking to go back on the gate is always honoured",
      capr.rung_for("Alice", d)["key"] == "A0" and capr.rung_for("Alice", d)["held"])

# ═══════════════════════════════════════════════════ 6. own-OS grant
p = cperk.compute("Alice", fixture(n_live=4))
check("perk: 4 live clients has not earned it", p["status"] == "not_yet" and p["short"] == 1)
p = cperk.compute("Alice", fixture(n_live=5))
check("perk: 5 live clients earns it", p["status"] == "earned")
check("perk: staged until launch", p["active"] is False)
check("perk: the arithmetic is stated, not asserted", p["bookAtThreshold"] == 5 * stmts.CORE_FLOOR)
d = fixture(n_live=5)
d["meta"]["connectorOSGrants"] = {"Alice": {"status": "earned"}}
d["deals"][0]["stage"] = "prospect"
check("perk: earned once, kept while active", cperk.compute("Alice", d)["status"] == "earned")
refuses("perk: a grant cannot be started for a book that hasn't earned it",
        lambda: cperk.set_status("the Founder", "Alice", "scoped", d=fixture(n_live=1), commit=False, log=NOLOG),
        writes.ScopeError, "earned at")
check("perk: earned-but-not-started is a visible backlog",
      [x["connector"] for x in cperk.owed(fixture(n_live=5))] == ["Alice"])

# ═══════════════════════════════════════════════════ 6b. promotion — the missing join
# `referralMode` was read by the console and written by NOTHING, so every real referral rendered as
# "Your introduction" even when yourco made the approach. A submission becomes a company only here,
# so this is the one place that can know the mode.
d = fixture()
d["meta"]["connectorSubmissions"] = [sub(1, business="Northside Dental")]
refuses("promote: an unverified submission cannot become a company",
        lambda: writes.promote_submission("the Founder", "s1",
                                          d={**fixture(), "meta": {**fixture()["meta"],
                                             "connectorSubmissions": [sub(1, status="pending")]}},
                                          commit=False, log=NOLOG),
        writes.ScopeError, "verify it first")
refuses("promote: must name the operator",
        lambda: writes.promote_submission("", "s1", d=d, commit=False, log=NOLOG),
        writes.ScopeError)
before = len(d["companies"])
writes.promote_submission("the Founder", "s1", d=d, commit=False, log=NOLOG)
new = [c for c in d["companies"] if c["name"] == "Northside Dental"]
check("promote: a company is created", len(d["companies"]) == before + 1 and new)
check("promote: tagged to the connector so commission computes",
      new and new[0].get("referrer") == "Alice", str(new and new[0].get("referrer")))
check("promote: the referral is stamped SOURCER — the whole point",
      d["meta"]["referralMode"].get(new[0]["id"]) == "sourcer",
      str(d["meta"].get("referralMode")))
check("promote: the owner becomes a contact",
      any(p.get("companyId") == new[0]["id"] and p.get("name") == "An Owner" for p in d["contacts"]))
check("promote: provenance is carried onto the contact's relationship",
      any(p.get("relationship") for p in d["contacts"] if p.get("companyId") == new[0]["id"]))
refuses("promote: cannot be promoted twice",
        lambda: writes.promote_submission("the Founder", "s1", d=d, commit=False, log=NOLOG),
        writes.ScopeError, "already promoted")
# An Introducer referral must NOT be stamped — default is introducer, and mislabelling a warm intro
# as a cold call would be the same failure in the other direction.
check("promote: only sourced referrals are stamped",
      set(d["meta"]["referralMode"]) == {new[0]["id"]})
# The activity type the console writes must be the one the CRM registers, or the Activity tab's
# data-built filter offers a stray one-off instead of the type.
d2 = fixture()
writes.set_referral_fields("Alice", "c0", {"note": "spoke Friday"}, d=d2, commit=False, log=NOLOG)
act = [a for a in d2["activities"] if a.get("type", "").lower().startswith("connector")]
check("note: writes a CRM activity row", len(act) == 1)
check("note: uses the registered type spelling", act and act[0]["type"] == "Connector note",
      str(act and act[0]["type"]))

# ═══════════════════════════════════════════════════ 7. intake
d = fixture()
r = intake.handle("nobody@nowhere.test", "Some Biz, A Person, a@b.test, my dentist", d=d, commit=False)
check("intake: an unknown sender is refused", not r["ok"] and r["reason"] == "unknown-sender")
check("intake: and is told nothing at all", r["reply"] is None)
r = intake.handle("alice@x.test", "I am Bob. Some Biz, A Person, a@b.test, my dentist",
                  d=d, commit=False, log=NOLOG)
check("intake: identity comes from the channel, never the body", r["connector"] == "Alice")
r = intake.handle("727-555-1111", "Cedar Auto, A Person, c@d.test, my mechanic for years",
                  d=fixture(), commit=False, log=NOLOG)
check("intake: a phone sender resolves to the same connector", r["connector"] == "Alice" and r["ok"])
r = intake.handle("alice@x.test", "Lakeside Physio, tom@lakeside.test", d=fixture(), commit=False)
check("intake: provenance is never invented", not r["ok"] and "provenance" in r["missing"])
check("intake: it asks the question instead", "how you know them" in (r["reply"] or ""))
f, m = intake.parse("Hey yourco — Cedar Auto Body 727-555-0142, my mechanic, fixed my truck twice.")
check("intake: a greeting is not the business name", f.get("business") == "Cedar Auto Body", str(f.get("business")))
check("intake: the business is not filed as the owner", f.get("contact") != f.get("business"))
check("intake: provenance is the clause, not the whole message",
      f.get("provenance") and "Cedar Auto Body" not in f["provenance"], str(f.get("provenance")))
f2, _ = intake.parse("Biz, A Person, a@b.test — my dentist. They don't know yet.")
check("intake: 'they don't know' is recorded as no", f2.get("consent") == "no", str(f2.get("consent")))
f3, _ = intake.parse("Biz, A Person, a@b.test — my dentist, I told her to expect a call.")
check("intake: 'I told them' is recorded as yes", f3.get("consent") == "yes", str(f3.get("consent")))
f4, _ = intake.parse("Biz, A Person, a@b.test — my dentist.")
check("intake: silence on consent stays unknown", f4.get("consent") == "unknown")
# The scoped write path is not bypassed just because the channel changed.
d = fixture()
intake.handle("alice@x.test", "Dup Co, A Person, dup@x.test, my dentist", d=d, commit=False, log=NOLOG)
r = intake.handle("alice@x.test", "Dup Co, A Person, dup@x.test, my dentist", d=d, commit=False, log=NOLOG)
check("intake: duplicate detection still applies over text", not r["ok"] and r["reason"] == "refused")


# ── Practice drills (2026-08-24): three refusals worth failing a build over ───────────────────────
import coach as _coach
# Load the console by PATH, not by name: `crm/server.py` is already on sys.path and would shadow
# `connector-console/server.py`, so a plain `import server` silently gets the CRM's server instead.
import importlib.util as _ilu
_console_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "processes", "partnerships", "connector-console", "server.py")
_spec = _ilu.spec_from_file_location("_console_server", _console_path)
_console = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_console)

_LESSONS_DONE = [{"slug": "01-the-intro-play", "done": True},
                 {"slug": "02-who-to-flag", "done": False}]

_dr = _console.drills_for("__nobody__", {}, _LESSONS_DONE)
_ids = {i["id"] for i in _dr["items"]}

check("a drill is hidden until its lesson is complete",
      not any(i["lesson"] == "02-who-to-flag" for i in _dr["items"]),
      "an incomplete lesson's drill is a quiz on unseen material")
check("drills for a completed lesson are offered",
      any(i["lesson"] == "01-the-intro-play" for i in _dr["items"]))

# The rubric is the answer key. If it reaches the browser with the prompt, the page can reveal it
# early and practice becomes recitation — so it must be absent until an attempt exists.
check("the rubric never ships before an attempt",
      all("reveal" not in i for i in _dr["items"]),
      "looks_like/fails_if travelled to the page with the prompt")

# A self-mark records that the person read the rubric and formed a view. It is NOT an outside
# judgement, and merging the two would make both meaningless.
_tmp = os.path.join(tempfile.mkdtemp(prefix="coach-"), "connector.jsonl")
_real_store = _coach.STORE
_coach.STORE = os.path.dirname(_tmp)
try:
    _coach.record("connector", "Z", "01-the-intro-play#1", "missed", note="quoted a price")
    _coach.record("connector", "Z", "01-the-intro-play#1", "solid", by="self", note="felt fine")
    _g = _coach.growth("connector", "Z")
    check("a self-mark cannot clear a judged miss",
          [w["drill"] for w in _g["workOn"]] == ["01-the-intro-play#1"],
          "the whole point of an outside judgement is that it survives the person's own view")
    check("judged and self-marked are counted apart",
          (_g["judgedCount"], _g["selfMarkedCount"]) == (1, 1))
    check("growth still states what it cannot see", bool(_g["cannotSee"]))
finally:
    _coach.STORE = _real_store

print(f"\n{len(OK)} passed, {len(FAIL)} failed\n")
for f in FAIL:
    print("  FAIL " + f)
if not FAIL:
    for o in OK:
        print("  ok   " + o)
sys.exit(1 if FAIL else 0)
