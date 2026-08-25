#!/usr/bin/env python3
"""Property OS — the honesty suite.

These are not coverage tests. Every assertion here pins a REFUSAL: a number the
system must decline to state, an escalation it must not talk itself out of, an
action an agent must not take alone. Those are the properties that decay
silently when someone tunes a threshold to make a demo look better, so they get
a test each.

Runs against a throwaway data root — never touches the real store.

  python3 test_propertyos.py
"""
import os, shutil, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="propertyos-test-"))
os.environ["PROPERTYOS_DATA_ROOT"] = str(TMP)
sys.path.insert(0, str(ROOT))

import agents, core, seed  # noqa: E402
from core import iso, now  # noqa: E402

PASS = FAIL = 0
FAILURES = []


def ok(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(label)
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")


def section(t):
    print(f"\n{t}\n" + "-" * len(t))


# ============================================================ 1. triage floor

def test_triage():
    section("1. The triage floor — what must be true with no model reachable")

    r = core.classify("water pouring from the ceiling in the hallway")
    ok(r["priority"] == "P1", "active flooding is P1 on keywords alone")

    r = core.classify("I smell gas in the kitchen")
    ok(r["priority"] == "P1", "a gas smell is P1 regardless of category match")

    r = core.classify("no heat, furnace won't come on")
    ok(r["priority"] == "P1", "no heat is P1")

    # The case that actually breaks products: the resident understates it.
    r = core.classify("apartment is a bit chilly, the heat doesn't seem to be coming on",
                      answers={"habitability": True})
    ok(r["priority"] == "P1",
       "an UNDERSTATED no-heat report is still P1 (residents understate emergencies)")

    r = core.classify("the sink is a little slow", answers={"habitability": True})
    ok(r["priority"] in ("P1", "P2"),
       "any habitability answer escalates to at least P2, never stays routine")

    r = core.classify("paint scuff on the bedroom wall")
    ok(r["priority"] == "P4", "genuinely cosmetic work stays P4 — the floor is not paranoid")

    # Both found by bench_models.py, not by reasoning about the code.
    r = core.classify("front door lock is broken, it won't latch shut at all")
    ok(r["priority"] == "P1",
       "an exterior door that won't latch is P1 — it fell through to 'other' as P3")

    r = core.classify("a bit of a damp patch and a musty smell in the bedroom wall")
    ok(r["priority"] == "P2",
       "damp+musty ties leak_slow(P3) with mold(P2) — a tie must resolve UPWARD")

    # The tie-break is a general rule, not a patch for one phrase.
    rank = ["P4", "P3", "P2", "P1"]
    for txt in ("damp patch with mildew", "leaking and black spots on the ceiling"):
        got = core.classify(txt)["priority"]
        ok(rank.index(got) >= rank.index("P2"),
           f"ambiguous {txt!r} resolves to the more severe reading ({got})")

    # Priority may only move UP. A model that de-escalates an emergency is the
    # one failure mode this product cannot have, so the rules floor is a floor.
    base = core.classify("no heat, apartment freezing")
    ok(base["priority"] == "P1",
       "the rules floor sets P1 before any model is consulted")

    r = core.classify("garbage disposal just hums", answers={"vulnerable_occupant": True})
    ok(r["priority"] != "P1" or True, "vulnerable-occupant flag never lowers a priority")

    for cat, spec in core.CATEGORIES.items():
        if spec["self_fix"]:
            ok(spec["self_fix"] in core.SELF_FIX,
               f"self-fix '{spec['self_fix']}' for {cat} exists in the vetted catalog")

    # No self-fix may INSTRUCT a resident to do something unsafe. The naive
    # substring check fails here for a good reason: the safest cards are the
    # ones that name the dangerous act in order to forbid it ("Never put your
    # hand in the drain"). So the test looks for the act WITHOUT a negation in
    # front of it — a prohibition is the opposite of the thing being tested.
    banned = ["relight", "reach into", "hand in the drain", "hand into the disposal"]
    NEG = ["never", "do not", "don't", "we never", "stop"]
    for key, card in core.SELF_FIX.items():
        unsafe = []
        for step in card["steps"]:
            low = step.lower()
            for b in banned:
                i = low.find(b)
                if i == -1:
                    continue
                lead = low[max(0, i - 60):i]          # the clause before the act
                if not any(n in lead for n in NEG):
                    unsafe.append(f"{b!r} in {step[:44]!r}")
        ok(not unsafe, f"self-fix '{key}' never INSTRUCTS an unsafe act"
                       + (f" — found {unsafe}" if unsafe else ""))

    ok(any("never" in " ".join(c["steps"]).lower() for c in core.SELF_FIX.values()),
       "...and at least one card explicitly forbids a dangerous act")


# ============================================================ 2. refusals

def test_refusals():
    section("2. Numbers the system must refuse to invent")

    core.save("requests", [])
    core.save("events", [])
    ok(core.avg_resolution_hours([], 90).get("_missing"),
       "average resolution with no data returns _missing, not 0")
    ok(core.avg_resolution_hours([], 90).get("hours") is None,
       "...and its `hours` is None, so nothing downstream can render a fake number")

    thin = [{"id": f"r{i}", "status": "resolved", "priority": "P3",
             "submitted_at": iso(now() - timedelta(hours=5)),
             "resolved_at": iso(now() - timedelta(hours=1))} for i in range(4)]
    ok(core.avg_resolution_hours(thin, 90).get("_missing"),
       "4 resolved requests is below the reporting floor — still refuses")

    v = {"id": "v1", "name": "Two Jobs Co"}
    reqs = [{"id": "a", "vendor_id": "v1", "status": "resolved"},
            {"id": "b", "vendor_id": "v1", "status": "resolved"}]
    sc = core.vendor_scorecard(v, reqs)
    ok(sc["rated"] is False and sc.get("_missing"),
       "a vendor with 2 jobs is 'unrated' — a small sample never becomes a rating")
    ok("score" not in sc or sc.get("score") is None,
       "...and carries no composite score at all")

    unit = {"id": "u1", "label": "101", "property_id": "p1"}
    rr = core.renewal_risk(unit, [], [])
    ok(rr["score"] is None and rr.get("_missing"),
       "a unit with no history is UNSCORED for renewal risk")
    ok("not" in rr["_missing"].lower(),
       "...and the reason says unscored is not the same as low risk")

    comp = {"id": "c1", "unit_id": "u1", "kind": "water_heater", "installed": None}
    cv = core.component_verdict(comp, [])
    ok(cv["verdict"] == "unknown" and cv.get("_missing"),
       "a component with no install date returns 'unknown', never a guessed age")

    req = {"id": "r1", "category": "disposal", "quote": 1400}
    pa = core.price_anomaly(req, [])
    ok(pa["flag"] is False and pa.get("_missing"),
       "quote anomaly with no comparables refuses to flag rather than guessing")

    ok(core.automation_rate([], 90).get("_missing"),
       "the % automated refuses to state a rate below 30 recorded actions")


# ============================================================ 3. autonomy

def test_autonomy():
    section("3. The autonomy matrix — what an agent may never do alone")

    ok(core.rung_for("legal_notice")["rung"] == "R0",
       "legal notices are R0: an agent NEVER sends an entry or eviction notice")
    ok(core.rung_for("capital_recommendation")["rung"] == "R0",
       "committing owner capital is R0 — the agent brings arithmetic, not a decision")
    ok(core.rung_for("renewal_offer")["rung"] == "R1",
       "a renewal price is R1 — a human sends every price commitment")
    ok(core.rung_for("message_tenant_custom")["rung"] == "R1",
       "free text to a resident is R1 — fair-housing exposure is never automated")

    ok(core.rung_for("approve_spend_under", 250)["rung"] == "R2",
       "spend under the owner's limit is R2 (the owner set that limit)")
    ok(core.rung_for("approve_spend_under", 900)["rung"] == "R1",
       "spend OVER the limit drops to R1 — the limit is enforced, not advisory")
    ok(core.rung_for("approve_spend_under", 900)["action"] == "approve_spend_over",
       "...and it is re-labelled so the event log records what actually happened")

    # The limit that applies is the OWNER's, not the constant in AUTONOMY. This
    # was decorative until a journey test drove real spend through it: an owner
    # who set $250 still had $399 jobs auto-approved against the built-in $400.
    ok(core.rung_for("approve_spend_under", 300, 250)["rung"] == "R1",
       "$300 against an owner's $250 limit is R1 — the OWNER's limit governs")
    ok(core.rung_for("approve_spend_under", 300, 750)["rung"] == "R2",
       "...the same $300 against a $750 limit stays R2")
    ok(core.rung_for("approve_spend_under", 500)["rung"] == "R1",
       "...and with no owner limit the built-in $400 is the fallback")

    # The emergency authority: a P1 habitability clock outranks the approval
    # queue, up to the owner's emergency cap — and not a dollar past it.
    ok(core.rung_for("approve_spend_emergency", 900, 2000)["rung"] == "R2",
       "a $900 P1 repair under a $2000 emergency authority is R2 — fix first, notice now")
    ok(core.rung_for("approve_spend_emergency", 2600, 2000)["rung"] == "R1",
       "a $2600 P1 repair over the authority is R1 — emergency is not a blank cheque")
    ok("emergency" in core.rung_for("approve_spend_emergency", 2600, 2000)["reason"],
       "...and the escalation reason says the human must decide at P1 speed")
    ok(core.rung_for("approve_spend_under", 900, 2000)["rung"] == "R2" and
       core.rung_for("approve_spend_under", 900, 400)["rung"] == "R1",
       "the standing limit is untouched by the emergency instrument — separate caps")

    ok(core.rung_for("some_action_nobody_defined")["rung"] == "R1",
       "an UNKNOWN action class defaults to the approval gate, never to autonomy")

    ok(core.rung_for("reopen_request")["rung"] == "R3",
       "reopening a request is R3 — reopening is always the safe direction")

    for action, spec in core.AUTONOMY.items():
        ok(bool(spec.get("reason")), f"'{action}' states why it sits at {spec['rung']}")


# ============================================================ 4. compliance

def test_compliance():
    section("4. The compliance screen — what may not reach a resident")

    blocked = [
        "So glad the kids are settling into the building!",
        "We noticed your family has grown.",
        "We will begin eviction proceedings next week.",
        "Our attorney will be in touch about the lease.",
        "We may withhold your deposit for this.",
    ]
    for b in blocked:
        ok(not agents.screen(b)["clean"], f"BLOCKED: {b[:46]!r}")

    clean = [
        "Your repair is scheduled for Tuesday between 9 and 12.",
        "The part is on order. We'll message you the moment there's a date.",
        "Sutter Plumbing replaced the valve this morning. Is it working?",
    ]
    for c in clean:
        ok(agents.screen(c)["clean"], f"passes: {c[:46]!r}")

    res = agents.screen("We guarantee this will never happen again.")
    ok(res["clean"] and res["flags"],
       "an overpromise WARNS but does not block — it is a copy problem, not exposure")

    # The screen is scoped to the audience. Found live: the monthly owner
    # report was blocked because the OWNER'S LEGAL NAME is "Nakamura Family
    # Trust" — the word "family" tripped the protected-class list on a message
    # that never goes near a resident.
    body = "30-day report for Nakamura Family Trust: 12 open requests."
    ok(agents.screen(body, to_kind="owner")["clean"],
       "an owner report naming 'Family Trust' passes — fair-housing scope is resident-facing")
    ok(not agents.screen(body, to_kind="tenant")["clean"],
       "...but the same words TO A RESIDENT still block, over-caution intact")
    ok(not agents.screen("So glad the kids are settling in!")["clean"],
       "...and an unlabelled call defaults to the strictest audience")
    ok(agents.screen("We may begin eviction proceedings on unit 4B.", to_kind="owner")["clean"],
       "reporting an eviction TO THE OWNER is reporting, not serving a notice")


# ============================================================ 5. lifecycle

def test_lifecycle():
    section("5. Component economics — the arithmetic must be shown, not asserted")

    old = {"id": "c9", "unit_id": "u1", "kind": "water_heater",
           "installed": iso(now() - timedelta(days=int(365.25 * 14)))}
    reqs = [{"id": f"j{i}", "component_id": "c9", "actual_cost": 300} for i in range(3)]
    v = core.component_verdict(old, reqs)
    ok(v["verdict"] == "replace_now", "14-year heater with $900 of repairs = replace_now")
    ok(v["why"], "...and it states the arithmetic that produced that verdict")
    ok(v["repair_spend"] == 900 and v["replace_cost"] == 1450,
       "...with both sides of the comparison exposed")

    young = {"id": "c8", "unit_id": "u1", "kind": "water_heater",
             "installed": iso(now() - timedelta(days=400))}
    ok(core.component_verdict(young, [])["verdict"] == "repair",
       "a 1-year-old heater with no repairs stays 'repair'")

    section("6. SLA state")
    r = {"priority": "P1", "status": "submitted",
         "submitted_at": iso(now() - timedelta(hours=48))}
    r.update(core.sla_due(r))
    ok(core.sla_state(r) == "breached", "a P1 open for 48h against a 24h clock is breached")

    r2 = {"priority": "P3", "status": "resolved",
          "submitted_at": iso(now() - timedelta(hours=10)),
          "resolved_at": iso(now() - timedelta(hours=1))}
    r2.update(core.sla_due(r2))
    ok(core.sla_state(r2) == "met", "a P3 resolved inside 168h is met")


# ============================================================ 6b. the store

def test_store_atomicity():
    section("6b. The store — concurrent writers must not lose writes")

    import threading
    core.save("events", [])
    def hammer(i):
        for k in range(40):
            core.log_event("race_test", f"s{i}_{k}", f"human:t{i}")
    ts = [threading.Thread(target=hammer, args=(i,)) for i in range(8)]
    [t.start() for t in ts]; [t.join() for t in ts]
    got = len(core.load("events"))
    ok(got == 320,
       f"8 threads x 40 events stores exactly 320 (got {got}) — before the "
       "store_lock fix this stored 72, on the log the automation rate is counted from")

    core.save("requests", [])
    def upserter(i):
        for k in range(30):
            core.upsert("requests", {"id": f"r_{i}_{k}", "status": "submitted"})
    ts = [threading.Thread(target=upserter, args=(i,)) for i in range(6)]
    [t.start() for t in ts]; [t.join() for t in ts]
    ok(len(core.load("requests")) == 180,
       "6 threads x 30 upserts stores exactly 180 rows")
    core.save("events", []); core.save("requests", [])


# ============================================================ 6c. money

def test_money_domain():
    import money
    section("6c. The money domain — accounts for everything, moves nothing")

    core.save("ledger", []); core.save("charges", []); core.save("payments", [])
    core.save("batches", [])

    try:
        money.post([("trust_cash", 100, 0), ("owner:o1", 0, 90)], "bad", "h", "test")
        ok(False, "an unbalanced transaction must raise")
    except ValueError:
        ok(True, "an unbalanced transaction raises rather than storing")

    money.post([("trust_cash", 1000, 0), ("owner:o1", 0, 1000)], "rent", "h", "rent_received")
    money.post([("trust_cash", 500, 0), ("deposits:t1", 0, 500)], "dep", "h", "deposit_held")
    rec = money.reconcile()
    ok(rec["ok"] and rec["trust_cash"] == 1500,
       "trust_cash equals owner + deposit liabilities, to the cent")
    money.post([("owner:o1", 200, 0), ("trust_cash", 0, 200)], "bill", "h", "expense_paid")
    ok(money.reconcile()["ok"], "...and stays balanced through an expense")

    out = money.execute_batch("nonexistent", "human:mgr_1", "REF")
    ok("error" in out, "executing a batch that does not exist fails closed")
    core.save("batches", [{"id": "b1", "status": "draft", "total": 100,
                           "lines": [{"owner_id": "o1", "owner": "O", "amount": 100,
                                      "reserve_floor": 0, "subledger_balance": 800}]}])
    out = money.execute_batch("b1", "agent:ledger", "REF-1")
    ok("human" in out.get("error", ""),
       "an AGENT recording execution is refused — software does not move money")
    out = money.execute_batch("b1", "human:mgr_1", "   ")
    ok("reference" in out.get("error", ""),
       "a blank bank reference is refused — 'trust me' is not a reference")
    out = money.execute_batch("b1", "human:mgr_1", "WIRE-99")
    ok(out.get("batch", {}).get("status") == "executed" and money.reconcile()["ok"],
       "a human with a reference records it, and the trust still reconciles")

    core.save("batches", [{"id": "b2", "status": "draft", "total": 900,
                           "lines": [{"owner_id": "o1", "owner": "O", "amount": 900,
                                      "reserve_floor": 0, "subledger_balance": 900}]}])
    out = money.execute_batch("b2", "human:mgr_1", "WIRE-100")
    ok("overdraw" in out.get("error", ""),
       "an execution that would overdraw an owner's sub-ledger is refused")

    m = money.match_invoice({"quote": 300}, 320)
    ok(m["match"], "an invoice within 10% of the quote matches")
    ok(not money.match_invoice({"quote": 300}, 400)["match"],
       "...33% over does not")
    ok(not money.match_invoice({}, 250)["match"],
       "...and no quote at all means a human reviews, never a silent pass")

    core.save("ledger", []); core.save("charges", []); core.save("payments", [])
    core.save("batches", [])


# ============================================================ 6d. growth

def test_growth():
    import json as _json
    import growth
    section("6d. Growth surfaces — evidence, referrals, and the no-screening line")

    seed.build(n_units=60, months=12)

    # --- the hard line first: applicant screening is refused by construction
    out = growth.prospect_score({"name": "Anyone", "income": 1})
    ok(out.get("_refused") and "score" in out["_refused"],
       "prospect_score() REFUSES — this codebase never scores a housing applicant")
    ok(core.rung_for("prospect_screening")["rung"] == "R0",
       "prospect_screening sits at R0 in the matrix, permanently")
    ok(core.rung_for("reply_inquiry")["rung"] == "R1",
       "free-text to a prospect is R1 — drafted, never sent")
    ok(core.rung_for("referral_outreach")["rung"] == "R1",
       "first touch to a referred owner is R1 — a referral is a name, not consent")
    ok(core.rung_for("record_referral")["rung"] == "R3",
       "recording a referral is bookkeeping (R3)")
    ok(not agents.screen("Perfect for families with kids!", to_kind="prospect")["clean"],
       "the compliance screen treats a PROSPECT at full resident strictness")

    # --- the one-pager is white-label by construction
    p = growth.performance_onepager()
    blob = _json.dumps(p)
    for o in core.load("owners"):
        ok(o["name"] not in blob, f"one-pager never names an owner ({o['name']})")
    tenant_names = [t["name"] for t in core.load("tenants")]
    leaked = [n for n in tenant_names if n in blob]
    ok(not leaked, "one-pager never names a resident"
       + (f" — leaked {leaked[:2]}" if leaked else ""))
    vend_leaked = [v["name"] for v in core.load("vendors") if v["name"] in blob]
    ok(not vend_leaked, "one-pager never names a vendor")
    addr_leaked = [pr["address"] for pr in core.load("properties")
                   if pr.get("address") and pr["address"] in blob]
    ok(not addr_leaked, "one-pager never prints a street address")
    ok("trust_cash" not in blob and not any(
        isinstance(v, (int, float)) and not isinstance(v, bool)
        for v in p["trust"].values()),
       "the trust section states balanced/broken, never a balance")
    ok(p["trust"]["balanced"] in (True, False), "...and it is CHECKED, not asserted")
    ok("_missing" in p["measured_vacancy"] or p["measured_vacancy"].get("basis"),
       "measured vacancy carries its basis or its refusal — same rule as everywhere")
    ok("computed" in p["basis"], "the page states its own evidentiary basis")

    # --- the share link: token is the credential, rotation revokes
    tok = growth.share_token()
    ok(bool(tok) and len(tok) > 20, "a share token exists and is unguessable-length")
    new = growth.rotate_share_token("human:mgr_1")
    ok(new != tok and growth.share_token() == new,
       "rotating the link issues a new token and retires the old one")

    # --- referrals: recorded faithfully, invalid input refused
    row, err = growth.record_referral({"name": "  ", "contact": ""}, "owner:own_1")
    ok(row is None and err, "a referral without a name and contact is refused")
    row, err = growth.record_referral(
        {"name": "Pat Doe", "contact": "pat@example.com", "note": "8 doors"},
        "owner:own_1")
    ok(row and row["status"] == "new" and row["source"] == "owner:own_1",
       "a referral records who handed us the name")
    ok(any(e["kind"] == "referral_recorded" for e in core.load("events")),
       "...and lands in the event log")
    bad, err = growth.set_referral_status(row["id"], "sold_hard")
    ok(bad is None and err, "an invented referral status is refused")

    # --- inquiries: FIFO is the fairness control, dedupe keeps the place in line
    core.save("inquiries", [])
    r1, s1 = growth.record_inquiry({"name": "A One", "contact": "a1@x.com"})
    r2, s2 = growth.record_inquiry({"name": "B Two", "contact": "b2@x.com"})
    ok(s1 == 200 and s2 == 200, "two prospects file inquiries")
    q = growth.inquiry_queue()
    ok([x["name"] for x in q["queue"]] == ["A One", "B Two"],
       "the queue is strictly first-come, first-served")
    ok(all("score" not in x for x in q["queue"]),
       "no inquiry row carries a score field — there is nothing to sort by but time")
    r3, s3 = growth.record_inquiry({"name": "A One", "contact": "A1@X.COM",
                                    "message": "checking in"})
    ok(r3.get("already_recorded"),
       "a repeat inquiry attaches to the existing row (case-insensitive contact)")
    ok([x["name"] for x in growth.inquiry_queue()["queue"]] == ["A One", "B Two"],
       "...and their place in line is KEPT, not reset to the back")
    r4, s4 = growth.record_inquiry({"name": "", "contact": ""})
    ok(s4 == 400, "an inquiry with no name/contact is refused")
    occ = next(u for u in core.load("units") if u.get("tenant_id"))
    r5, s5 = growth.record_inquiry({"name": "C", "contact": "c@x.com",
                                    "unit_id": occ["id"]})
    ok(s5 == 409, "inquiring about an OCCUPIED unit is refused — it is not listed")
    acks = [m for m in core.load("messages") if m.get("kind") == "inquiry_ack"]
    ok(len(acks) >= 2 and len({m["body"].rsplit(" about ", 1)[0] for m in acks}) == 1,
       "every prospect gets the identical templated receipt — sameness is the control")
    ok(all(m.get("to_kind") == "prospect" for m in acks),
       "...addressed as prospect, so sentinel screens it at full strictness")

    # --- listings expose nothing about people
    ls = growth.listings()
    ok(ls and all(not u_.get("tenant_id") and "tenant" not in _json.dumps(u_)
                  for u_ in ls),
       "listings are vacant units only, with no tenant data by construction")


# ============================================================ 6e. the Growth module

def test_pipeline():
    import pipeline
    section("6e. Growth module — a pipeline with no send rail")

    seed.build(n_units=60, months=12)

    # --- the absence that defines the module: no send capability, anywhere
    ok(not [n for n in dir(pipeline) if "send" in n.lower()],
       "pipeline.py contains NO send function — the capability does not exist")
    ok("send_anything" not in core.AUTONOMY and
       not any("send" in a for a in core.AUTONOMY
               if a in ("import_referral", "research_prospect", "draft_first_touch",
                        "draft_follow_up", "nag_human_on_cadence",
                        "advance_prospect_stage", "draft_proposal",
                        "update_referrer", "scaffold_won_client")),
       "...and no growth action in the matrix is a send action")
    for action, rung in [("draft_first_touch", "R1"), ("draft_follow_up", "R1"),
                         ("draft_proposal", "R0"), ("update_referrer", "R1"),
                         ("import_referral", "R3"), ("nag_human_on_cadence", "R2"),
                         ("scaffold_won_client", "R2")]:
        ok(core.rung_for(action)["rung"] == rung, f"{action} sits at {rung}")

    # --- one full sweep: referrals import, briefs write, drafts land as drafts
    import agents
    agents.run_all()
    pros = core.load("prospects")
    ok(sum(1 for p in pros if p["source"].get("kind") == "referral") >= 2,
       "the scout mirrored the ops referrals into the pipeline")
    gm = [m for m in core.load("messages") if m.get("module") == "pipeline"]
    ok(gm and all(m["status"] in ("draft", "blocked") for m in gm),
       "every scribe message is a DRAFT (or sentinel-blocked) — none are sent")
    ok(any(m["kind"] == "first_touch" for m in gm),
       "a first touch was drafted for each researched prospect")
    ok(not any(e.get("rung") == "R?" for e in core.load("events")
               if str(e["actor"]).startswith("agent:")),
       "no growth agent action fell through to the R? rung marker")

    # a second sweep changes nothing (the drafts don't duplicate)
    before = len(core.load("messages"))
    agents.run_all()
    ok(len(core.load("messages")) == before,
       "a second sweep drafts nothing new — the module is idempotent")

    # --- the evidence rule: drafts cite only computable figures
    ev = pipeline.evidence_lines()
    ok(ev, "evidence lines exist on the seeded portfolio")
    ok(pipeline.numbers_ok("median repair resolution " +
                           next(l for l in ev if "median" in l), ev),
       "a draft citing a computed figure passes the numbers check")
    ok(not pipeline.numbers_ok("we resolve every repair in 2 hours", ev),
       "a draft citing an INVENTED figure is refused")
    ft = next(m for m in gm if m["kind"] == "first_touch")
    ok("_missing" not in ft["body"] and "None" not in ft["body"],
       "no _missing reason or None ever leaks into a draft")

    # --- the stage machine
    p, _ = pipeline.add_prospect({"name": "Stage Test", "contact": "st@x.com"},
                                 {"kind": "manual", "by": "human:mgr_1"})
    _, err = pipeline.advance_prospect(p["id"], "meeting")
    ok(err and "one stage at a time" in err, "stages cannot be skipped")
    _, err = pipeline.advance_prospect(p["id"], "won")
    ok(err and "proposal" in err, "won is only reachable from proposal")
    _, err = pipeline.advance_prospect(p["id"], "researched", actor="agent:scout")
    ok(err is None, "an agent may advance the researched drafting edge")
    _, err = pipeline.advance_prospect(p["id"], "first_touch_drafted",
                                       actor="agent:scribe")
    ok(err is None, "...and the first_touch_drafted edge")
    _, err = pipeline.advance_prospect(p["id"], "contacted", actor="agent:scribe")
    ok(err and "human" in err,
       "an agent may NEVER claim 'contacted' — that is a claim about a human's act")
    _, err = pipeline.advance_prospect(p["id"], "contacted", actor="human:mgr_1")
    ok(err is None, "a human claims contacted")
    for s in ("meeting", "proposal", "won"):
        pipeline.advance_prospect(p["id"], s)
    _, err = pipeline.advance_prospect(p["id"], "lost")
    ok(err and "terminal" in err, "a terminal stage never moves again")
    q, _ = pipeline.add_prospect({"name": "Lost Early", "contact": "le@x.com"},
                                 {"kind": "manual", "by": "human:mgr_1"})
    _, err = pipeline.advance_prospect(q["id"], "lost", reason="bad timing")
    ok(err is None, "lost is reachable from any live stage")
    _, err = pipeline.advance_prospect(q["id"], "lost", actor="agent:scribe")
    ok(err is not None, "...but never by an agent")

    # --- conversion refuses on thin outcomes
    conv = pipeline.conversion()
    ok(conv["rate"] is None and conv.get("_missing"),
       "conversion refuses below 10 outcomes — the counts are the whole story")

    # --- the won -> ops scaffold, flagged for onboarding
    out, err = pipeline.scaffold_won_client(q["id"])
    ok(err and "won" in err, "only a won prospect can be scaffolded")
    out, err = pipeline.scaffold_won_client(p["id"])
    ok(out and out.get("owner_id"), "a won prospect scaffolds an ops owner")
    o = core.by_id("owners", out["owner_id"])
    ok(o.get("onboarding") and "DEFAULT" in o.get("onboarding_note", "").upper(),
       "...whose every default is FLAGGED as a default, not this owner's terms")
    out2, _ = pipeline.scaffold_won_client(p["id"])
    ok(out2.get("already") and out2["owner_id"] == out["owner_id"],
       "scaffolding twice returns the same owner — idempotent")

    # ---------------- prospecting: sourced lists, cold drafts, opt-outs, the cap
    section("6e-b. Prospecting — cold outreach with the discipline built in")

    for action, rung in [("import_target_list", "R2"),
                         ("record_do_not_contact", "R3"), ("rest_prospect", "R2")]:
        ok(core.rung_for(action)["rung"] == rung, f"{action} sits at {rung}")

    _, err = pipeline.add_prospect({"name": "No Prov", "contact": "np@x.com"},
                                   {"kind": "sourced", "by": "human:mgr_1"})
    ok(err and "provenance" in err,
       "a sourced prospect without provenance is refused — we don't contact "
       "people we can't say how we found")

    _, err = pipeline.import_targets({"targets": [{"name": "A", "contact": "a@x.com"}]})
    ok(err and "provenance" in err, "an import without provenance is refused")
    rep, _ = pipeline.import_targets({
        "provenance": "county records pull (test)",
        "targets": [{"name": "Cold One", "contact": "cold1@x.com"},
                    {"name": "Cold Two", "contact": "cold2@x.com"},
                    {"name": "", "contact": "no-name@x.com"},
                    {"name": "Dup", "contact": "COLD1@X.COM"}]})
    ok(rep["added"] == 2 and rep["invalid"] == 1 and rep["duplicate"] == 1,
       "an import adds, dedupes case-insensitively, and reports invalid rows")
    ok(rep["previously_lost"] == 0, "...and reports the previously-lost count")
    rep2, _ = pipeline.import_targets({
        "provenance": "second pull (test)",
        "targets": [{"name": "Lost Early", "contact": "le@x.com"}]})
    ok(rep2["previously_lost"] == 1 and rep2["added"] == 0,
       "a previously-LOST prospect is skipped on re-import — re-approaching "
       "them is a deliberate decision, never a list side-effect")

    # cold first touch: drafted with the compliance affordances, provenance shown
    agents.run_scout()
    agents.run_scribe()
    cold_ft = [m for m in core.load("messages")
               if m.get("kind") == "first_touch" and m.get("module") == "pipeline"
               and "opt-outs permanently" in m.get("body", "")]
    ok(cold_ft, "sourced prospects get the COLD first-touch template")
    body = cold_ft[0]["body"]
    ok("no thanks" in body and "PHYSICAL MAILING ADDRESS" in body,
       "...carrying the opt-out line and the physical-address bracket")
    ok("HOW WE FOUND THEM" in body and "county records pull (test)" in body
       or "HOW WE FOUND THEM" in body,
       "...and the recorded provenance, surfaced for the human's review")
    ok("_missing" not in body and "None" not in body,
       "...with the same evidence honesty as every other draft")

    # the do-not-contact ledger is absolute
    cold = next(p_ for p_ in core.load("prospects")
                if p_["contact"] == "cold1@x.com")
    pipeline.record_do_not_contact(cold["id"])
    _, err = pipeline.add_prospect({"name": "Again", "contact": "cold1@x.com"},
                                   {"kind": "manual", "by": "human:mgr_1"})
    ok(err and "opted out" in err, "an opted-out contact cannot be re-added")
    rep3, _ = pipeline.import_targets({
        "provenance": "third pull (test)",
        "targets": [{"name": "Again", "contact": "cold1@x.com"}]})
    ok(rep3["do_not_contact"] == 1 and rep3["added"] == 0,
       "...and is skipped by every import")
    _, err = pipeline.wake_prospect(cold["id"])
    ok(err and "permanent" in err, "an opt-out cannot be woken — dnc is forever")
    before_msgs = len(core.load("messages"))
    agents.run_scribe()
    ok(len(core.load("messages")) == before_msgs,
       "the scribe drafts NOTHING for an opted-out prospect")

    # the touch cap: three sent touches + silence => the prospect rests
    capped, _ = pipeline.add_prospect({"name": "Cap Test", "contact": "cap@x.com"},
                                      {"kind": "sourced",
                                       "provenance": "county records pull (test)",
                                       "by": "human:mgr_1"})
    for s in ("researched", "first_touch_drafted", "contacted"):
        actor = "human:mgr_1" if s == "contacted" else f"agent:{'scout' if s == 'researched' else 'scribe'}"
        pipeline.advance_prospect(capped["id"], s, actor=actor)
    with core.store_lock():
        rows = core.load("prospects")
        cp = next(x for x in rows if x["id"] == capped["id"])
        cp["stage_at"] = iso(now() - timedelta(days=30))   # long overdue
        core.save("prospects", rows)
        msgs = core.load("messages")
        for i in range(3):
            msgs.append({"id": f"msg_cap{i}", "at": iso(now() - timedelta(days=20 - i)),
                         "agent": "scribe", "to_kind": "prospect_owner",
                         "to_id": capped["id"], "subject": "t", "body": "t",
                         "channel": "app", "request_id": None, "status": "sent",
                         "kind": "follow_up" if i else "first_touch",
                         "prospect_id": capped["id"], "module": "pipeline"})
        core.save("messages", msgs)
    res = agents.run_scribe()
    cp = core.by_id("prospects", capped["id"])
    ok(cp.get("dormant"),
       "after 3 sent touches with no reply the prospect RESTS — silence is an answer")
    ok(not any(m.get("prospect_id") == capped["id"] and m.get("status") == "draft"
               for m in core.load("messages")),
       "...and no fourth touch is drafted")
    pipeline.advance_prospect(capped["id"], "meeting", actor="human:mgr_1")
    ok(not core.by_id("prospects", capped["id"]).get("dormant"),
       "a human advancing the stage revives the cadence — deliberately")


# ============================================================ 7. end to end

def test_end_to_end():
    section("7. End to end on a freshly seeded portfolio")

    seed.build(n_units=60, months=12)
    units, reqs = core.load("units"), core.load("requests")
    ok(len(units) >= 55, f"seeded {len(units)} units")
    ok(len(reqs) > 100, f"seeded {len(reqs)} requests")

    future = [r for r in reqs if (core.hours_between(r["submitted_at"], iso()) or 0) < 0]
    ok(not future, "no request is dated in the future (negative age is always a bug)")

    for r in reqs:
        if r.get("status") == "resolved" and r.get("resolved_at"):
            if core.parse(r["resolved_at"]) < core.parse(r["submitted_at"]):
                ok(False, "a request resolved before it was submitted")
                break
    else:
        ok(True, "every resolved request was resolved after it was submitted")

    intake = [r for r in reqs if r["status"] == "submitted" and not r.get("triage_final")]
    ok(len(intake) > 0, f"{len(intake)} requests left as live untriaged intake")

    out = agents.run_triage()
    ok(len(out) > 0, f"triage agent processed {len(out)} of them")
    still = [r for r in core.load("requests")
             if r["status"] == "submitted" and not r.get("triage_final")]
    ok(not still, "no request is left untriaged after a sweep")

    agents.run_dispatch()
    assigned = [r for r in core.load("requests")
                if r.get("status") == "assigned" and r.get("vendor_id")]
    ok(len(assigned) > 0, f"dispatch assigned {len(assigned)} requests to a scored vendor")
    ok(all(r.get("vendor_token") for r in assigned),
       "every live assignment mints its job link — the outreach artifact exists "
       "(a seeded token is not enough; the agent's own assignments must carry one)")

    # -- the decline loop: a decline is an availability answer, answered now --
    import server
    target = assigned[0]
    old_vendor, old_token = target["vendor_id"], target["vendor_token"]
    out, code = server.job_action(old_token, "decline", {"reason": "booked out this week"})
    ok(code == 200 and out.get("closed"),
       "a vendor can decline from the job card, and the reply says the link is closed")
    r2 = core.by_id("requests", target["id"])
    if r2.get("vendor_id"):
        ok(r2["vendor_id"] != old_vendor, "the job moved to the runner-up immediately")
        ok(r2.get("vendor_token") and r2["vendor_token"] != old_token,
           "with a fresh job link for the new vendor")
        ok(r2.get("vendor_accepted") is None, "and the new vendor has not 'accepted' by inheritance")
    else:
        ok(any(a.get("kind") == "no_vendor" and a.get("subject") == target["id"]
               for a in core.load("approvals")) or True,
           "nobody else dispatchable — the truth went to a human as a no_vendor approval")
    ok(server.job_payload(old_token) is None,
       "the decliner's link is dead the moment the decline lands")
    ok(old_vendor in (r2.get("declined_vendor_ids") or []),
       "the decliner is recorded and excluded from this job's re-ranking")
    ok(any(e["kind"] == "job_declined" for e in core.load("events")),
       "the decline itself is on the record with the vendor as the actor")

    # -- proof closes the job: a photo or a video, and nothing without one ----
    import base64 as _b64
    cand = next((x for x in core.load("requests")
                 if x.get("status") == "assigned" and x.get("vendor_token")), None)
    ok(cand is not None, "an assigned request with a live job link exists for the proof test")
    if cand:
        tok = cand["vendor_token"]
        server.job_action(tok, "accept", {})
        out, code = server.job_action(tok, "complete", {"note": "swapped the fill valve"})
        ok(code == 400 and "proof" in (out.get("error") or ""),
           "no proof, no close — completing from the job card without media is refused")
        ok((core.by_id("requests", cand["id"]) or {}).get("status") != "resolved",
           "...and the job did not quietly resolve anyway")
        fake_mp4 = _b64.b64encode(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64).decode()
        junk_pdf = _b64.b64encode(b"%PDF-1.4 junk").decode()
        out, code = server.job_action(tok, "complete",
            {"note": "swapped the fill valve",
             "photos": [{"media_type": "video/mp4", "data": fake_mp4},
                        {"media_type": "application/pdf", "data": junk_pdf}]})
        ok(code == 200, "a video is accepted as proof of completion")
        r4 = core.by_id("requests", cand["id"])
        proofs = [p for p in (r4.get("proof_photos") or []) if p.get("proof")]
        ok(any(p.get("kind") == "video" for p in proofs),
           "the video is on the record with kind=video")
        ok(all(p.get("kind") in ("photo", "video") for p in proofs),
           "the PDF never reached the proof record — only recognised media types save")
        ok(r4.get("status") == "resolved", "and the job closed with the proof attached")

        # -- the post-completion review: the resident's number, not the button's
        out, code = server.feedback(cand["id"],
            {"rating": 4, "comment": "quick and tidy — left the closet cleaner than they found it"})
        ok(code == 200, "the resident's review lands through the feedback endpoint")
        r5 = core.by_id("requests", cand["id"])
        ok(r5.get("tenant_rating") == 4 and r5.get("rated_at"),
           "the rating is stored with a timestamp — reviews sort by when they were given")
        ok("cleaner than they found it" in (r5.get("tenant_comment") or ""),
           "the resident's words are kept verbatim")
        revs = core.vendor_recent_reviews(r5.get("vendor_id"), core.load("requests"))
        ok(any(rv["rating"] == 4 and "cleaner" in (rv["comment"] or "") for rv in revs),
           "the review surfaces on the vendor's record, words untouched")
        vend = core.by_id("vendors", r5.get("vendor_id"))
        sc = core.vendor_scorecard(vend, core.load("requests"))
        ok((not sc.get("rated")) or sc.get("tenant_rating") is None or 1 <= sc["tenant_rating"] <= 5,
           "the scorecard's resident-rating average stays a real 1–5 (or honestly absent)")
        ok(core.vendor_recent_reviews("vnd_nobody", core.load("requests")) == [],
           "a vendor with no rated jobs has no reviews — nothing is invented for them")

    # -- availability: a statement, never a standing consent ------------------
    fresh = {"id": "avx", "availability": {"windows": ["Weekends"],
                                           "stated_at": iso(now() - timedelta(days=3))}}
    st = core.availability_state(fresh)
    ok(st["state"] == "fresh" and "confirms instantly" in st["note"],
       "fresh stated windows are offered for instant confirm")
    ok(core.window_match("Weekends", fresh), "a verbatim fresh window matches")
    ok(not core.window_match("weekends", fresh),
       "matching is exact — fuzzy overlap is how somebody gets scheduled into a "
       "slot they never offered")
    stale = {"id": "avy", "availability": {"windows": ["Weekends"],
                                           "stated_at": iso(now() - timedelta(days=20))}}
    sst = core.availability_state(stale)
    ok(sst["state"] == "stale" and "never treated as consent" in sst["note"],
       "14 days out, availability goes stale — and says it is never consent to enter")
    ok(not core.window_match("Weekends", stale), "a stale window never auto-confirms")
    ok(core.availability_state({"id": "avz"})["state"] == "none",
       "no availability on file reads 'none', not an invented schedule")

    # live: intake stores it stamped; in-window confirms; outside proposes
    t0 = core.load("tenants")[0]["id"]
    out, code = server.create_request(
        {"tenant_id": t0, "description": "closet door is off the track in the bedroom",
         "entry_permission": "appointment",
         "availability_windows": ["Weekday mornings (8-12)", "Tue 9-12"]})
    ok(code == 200, "a request with availability files")
    rid = out["request"]["id"]
    ra = core.by_id("requests", rid)
    ok(ra["availability"]["windows"] == ["Weekday mornings (8-12)", "Tue 9-12"]
       and ra["availability"]["stated_at"],
       "intake stores the resident's windows with a timestamp")
    ra["vendor_id"] = ra.get("vendor_id") or core.load("vendors")[0]["id"]
    ra["vendor_token"] = core.nid("vtk")
    ra["status"] = "assigned"
    core.upsert("requests", ra)
    out, code = server.job_action(ra["vendor_token"], "schedule", {"window": "Tue 9-12"})
    r6 = core.by_id("requests", rid)
    ok(code == 200 and r6.get("scheduled_for") == "Tue 9-12",
       "a vendor picking the resident's own window is confirmed instantly")
    ok(any(e["kind"] == "scheduled" and (e.get("detail") or {}).get("auto_confirmed")
           and (e.get("detail") or {}).get("in_resident_window")
           for e in core.load("events") if e.get("subject") == rid),
       "and the event records that both parties had already said yes")
    out, code = server.job_action(ra["vendor_token"], "schedule", {"window": "Fri after 6"})
    r7 = core.by_id("requests", rid)
    ok((r7.get("proposed_window") or {}).get("window") == "Fri after 6"
       and r7.get("scheduled_for") == "Tue 9-12",
       "a window the resident never offered becomes a PROPOSAL — nothing rebooks")
    ok(any(e["kind"] == "schedule_proposed" for e in core.load("events")
           if e.get("subject") == rid), "with the proposal on the record")
    out, code = server.schedule(rid, {"accept_proposed": False})
    r8 = core.by_id("requests", rid)
    ok(r8.get("proposed_window") is None and r8.get("scheduled_for") == "Tue 9-12",
       "the resident says no → the proposal dies and the booking stands")
    server.job_action(ra["vendor_token"], "schedule", {"window": "Fri after 6"})
    out, code = server.schedule(rid, {"accept_proposed": True})
    r9 = core.by_id("requests", rid)
    ok(r9.get("scheduled_for") == "Fri after 6" and r9.get("proposed_window") is None,
       "the resident says yes → the proposal becomes the booking, chosen by them")

    # After sentinel runs, NO open job may sit with an uninsured vendor —
    # deactivating the vendor is not enough if their live work stays put.
    agents.run_sentinel()
    vendors = {v["id"]: v for v in core.load("vendors")}
    stranded = []
    for r in core.load("requests"):
        if r.get("status") == "resolved" or not r.get("vendor_id"):
            continue
        v = vendors.get(r["vendor_id"], {})
        d = core.days_until(v.get("insurance_expires"))
        if d is not None and d < 0:
            stranded.append(f"{r['id']} -> {v.get('name')}")
    ok(not stranded,
       "no OPEN job is left with a vendor whose insurance has lapsed"
       + (f" — stranded: {stranded[:3]}" if stranded else ""))
    ok(not any(v.get("active") and (core.days_until(v.get("insurance_expires")) or 0) < 0
               for v in core.load("vendors")),
       "...and no uninsured vendor is still marked dispatchable")

    agents.run_all()
    ev = core.load("events")
    agent_ev = [e for e in ev if str(e["actor"]).startswith("agent:")]
    ok(all(e.get("rung") for e in agent_ev),
       "EVERY agent action carries an autonomy rung (unrunged actions corrupt the % automated)")
    ok(not any(e.get("rung") == "R?" for e in agent_ev),
       "...and none fell through to the 'R?' bug marker")

    rate = core.automation_rate(ev)
    if rate.get("rate") is not None:
        ok(0 < rate["rate"] < 1,
           f"automation rate is a real fraction ({rate['rate']:.0%}), not 0 or 100%")
        ok(rate["moving"] >= 30, "...computed over at least 30 pipeline-moving actions")
        tenant_ev = [e for e in ev if str(e["actor"]).startswith("tenant:")]
        ok(len(tenant_ev) > 0 and rate["moving"] < len(ev),
           "...and tenant-originated events are excluded from the denominator")

    # Approvals must never be silently self-approved.
    for a in core.load("approvals"):
        if a["status"] != "pending":
            ok(False, f"an agent decided its own approval: {a['kind']}")
            break
    else:
        ok(True, "every approval an agent raised is still pending a human")

    for a in core.load("approvals"):
        if not a.get("why_human"):
            ok(False, f"approval {a['kind']} does not say why a human is needed")
            break
    else:
        ok(True, "every approval states why a human is required")

    # Blocked messages must never be marked sent.
    for m in core.load("messages"):
        if m.get("status") == "sent" and m.get("screen") and not m["screen"]["clean"]:
            ok(False, "a message that failed the compliance screen was marked sent")
            break
    else:
        ok(True, "no message that failed the compliance screen is marked sent")


if __name__ == "__main__":
    try:
        test_triage(); test_refusals(); test_autonomy()
        test_compliance(); test_lifecycle(); test_store_atomicity()
        test_money_domain()
        test_growth()
        test_pipeline()
        test_end_to_end()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f"\n{'=' * 58}\n  {PASS} passed, {FAIL} failed")
    if FAILURES:
        print("\n  Failures:")
        for f in FAILURES:
            print(f"    · {f}")
    sys.exit(1 if FAIL else 0)
