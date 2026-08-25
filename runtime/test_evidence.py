#!/usr/bin/env python3
"""Tests for the Evidence door — every assertion here guards an HONESTY rule, not a feature.

These five views exist to tell the Founder things about his own company that he cannot otherwise
check. That only works if they refuse to overstate. Each test below pins one refusal in
place, so a future edit that makes a number look better has to delete an assertion to do it.

Run:  python3 runtime/test_evidence.py
"""
import os, re, sys, json, tempfile, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

from ledger import Ledger, brier, refuse_reason  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ok   " if cond else "  FAIL ") + name + (("  — " + detail) if detail and not cond else ""))


def tmp_ledger(tmp, name, rows=()):
    """A Ledger backed by a throwaway file. Ledger joins on ROOT, and joining an absolute
    path returns that path, so an absolute 'rel' is a clean way to sandbox a store."""
    p = os.path.join(tmp, name)
    if rows:
        with open(p, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    return Ledger(p)


# ---------------------------------------------------------------------------
def test_ledger(tmp):
    print("\nledger — append-only substrate")
    l = tmp_ledger(tmp, "a.jsonl")
    a, b = l.append("x", v=1), l.append("x", v=2)
    check("seq is monotonic", (a["seq"], b["seq"]) == (1, 2))
    l.append("x", corrects=1, v=99)
    check("correction folds in at read time", l.project()["events"][0]["v"] == 99)
    check("the original is never removed from disk", len(l.read()["events"]) == 3)
    with open(l.path, "a") as f:
        f.write("{broken\n")
    check("corrupt lines are counted, not swallowed", l.read()["bad"] == 1)
    check("a further append still allocates the right seq", l.append("x", v=4)["seq"] == 4)
    check("brier([]) is None, never 0", brier([]) is None)
    check("brier punishes confident-and-wrong", brier([(1.0, False)]) == 1.0)
    check("refusal fires below the sample floor", bool(refuse_reason(1)) and not refuse_reason(99))


def test_trust(tmp):
    print("\ntrust — the ledger may not flatter itself")
    import trust
    old = (trust.ACTIONS, trust.FORECASTS, trust.DRILLS_LOG)

    # an action on a loop with NO declared cost basis must never become minutes
    trust.ACTIONS = tmp_ledger(tmp, "act.jsonl")
    for i in range(3):
        trust.ACTIONS.append("action", action="File Write / Edit (in git)", agent="atlas",
                             outcome="clean", loop="a-loop-with-no-basis", on="2026-08-01")
    trust.FORECASTS = tmp_ledger(tmp, "fc.jsonl")
    trust.DRILLS_LOG = tmp_ledger(tmp, "dr.jsonl")
    d = trust.build()
    cc = d["ledger"]["controlCost"]
    check("unpriced actions are counted", cc["unpricedActions"] == 3)
    check("unpriced actions contribute no hours", cc["estimatedHours"] == 0)
    check("measured hours stay 0 without a time study", cc["measuredHours"] == 0)
    check("no composite score while inputs are missing", d["posture"]["score"] is None)
    check("the refusal names what is missing", len(d["posture"]["missing"]) >= 2)

    # a drill past its window with no verdict is a MISS, not a pending item
    old_ts = (datetime.datetime.now() - datetime.timedelta(hours=200)).isoformat(timespec="seconds")
    trust.DRILLS_LOG = tmp_ledger(tmp, "dr2.jsonl", rows=[
        {"seq": 1, "ts": old_ts, "kind": "armed", "drill": "canary-injection",
         "drillKind": "prompt injection", "severity": "high", "windowHours": 48}])
    d = trust.build()
    check("an overdue drill scores undetected", d["drills"]["undetected"] == 1)
    check("an overdue drill is not counted as open", d["drills"]["open"] == 0)
    check("overdue is surfaced separately", d["drills"]["overdue"] == 1)

    # one detected drill is "1 of 1", never "100%"
    now_ts = datetime.datetime.now().isoformat(timespec="seconds")
    trust.DRILLS_LOG = tmp_ledger(tmp, "dr3.jsonl", rows=[
        {"seq": 1, "ts": now_ts, "kind": "armed", "drill": "silent-schema-drift",
         "drillKind": "silent data corruption", "severity": "high", "windowHours": 24},
        {"seq": 2, "ts": now_ts, "kind": "detected", "drill": "silent-schema-drift", "run": 1}])
    d = trust.build()
    check("detection rate refuses a 1-drill sample", d["drills"]["detectionRate"] is None)
    check("the refusal states the raw count", "1 of 1" in (d["drills"]["rateRefusal"] or ""))

    # the audit must not accuse the streak table when the ledger has no coverage
    trust.ACTIONS = tmp_ledger(tmp, "act2.jsonl")
    d = trust.build()
    verdicts = {r["verdict"] for r in d["audit"]["rows"]}
    check("no ledger coverage reads as unverifiable, not DISAGREEMENT",
          "DISAGREEMENT" not in verdicts and "unverifiable" in verdicts)
    trust.ACTIONS, trust.FORECASTS, trust.DRILLS_LOG = old


def test_tripwires():
    print("\ntrip-wires — an unevaluable check may not read as 'did not fire'")
    import tripwires as tw
    facts = {"mrr": 0, "liveClients": 3, "OtherVentureCleared": False}
    r, e = tw.evaluate("liveClients >= 3", facts)
    check("a simple numeric check evaluates", r is True and e is None)
    r, e = tw.evaluate("liveClients >= 3 and OtherVentureCleared", facts)
    check("all-and evaluates", r is False and e is None)
    r, e = tw.evaluate("liveClients >= 3 or OtherVentureCleared", facts)
    check("all-or evaluates", r is True)
    r, e = tw.evaluate("liveClients >= 3 and mrr > 1 or OtherVentureCleared", facts)
    check("mixed and/or is REFUSED, not guessed", r is None and "mixes" in (e or ""))
    r, e = tw.evaluate("unknownThing > 1", facts)
    check("an unknown fact is an error, not False", r is None and "unknown fact" in (e or ""))
    r, e = tw.evaluate("not OtherVentureCleared", facts)
    check("negation works", r is True)
    r, e = tw.evaluate("OtherVentureCleared > 2", facts)
    check("comparing a boolean is refused", r is None)

    d = tw.build()
    check("real decisions are scanned", d["total"] > 50)
    check("seeded trip-wires are found", d["covered"] >= 7)
    check("uncovered decisions are reported, not hidden",
          d["counts"]["uncovered"] + d["counts"]["unreviewed"] > 0)
    check("'_none' prose produces no parse errors",
          not any("none" in (c["error"] or "").lower() for c in d["checkErrors"]))
    check("every fired row is contradicted or due",
          all(r["verdict"] in ("contradicted", "due") for r in d["fired"]))


def test_timemachine():
    print("\ntime machine — absence is absence, not zero")
    import timemachine as tm
    b = tm.blame("not_a_metric")
    check("an unknown metric is refused", "error" in b)
    a = tm.as_of("not-a-date")
    check("a malformed date is refused", "error" in a)
    a = tm.as_of("1999-01-01")
    check("a date before the repo existed is refused, not zeroed", "error" in a)
    start = tm._repo_start()
    check("repo start is the ROOT commit, not the newest", start == "2026-06-09", str(start))
    b = tm.blame("mrr")
    check("blame returns a change list", isinstance(b.get("changes"), list))
    check("blame reports how much history it walked", b.get("commitsWalked", 0) > 0)
    check("every change carries an actor", all(c.get("actor") for c in b["changes"]))
    kinds = {c["actor"]["kind"] for c in b["changes"]}
    check("actor kinds come from the repo's own conventions",
          kinds <= {"loop", "agent", "human"})


def test_twin():
    print("\ntwin — accuracy is not authority")
    import twin, dri_twin as dt
    d = twin.build()
    check("thresholds are published", d["thresholds"]["resolved"] >= 5)
    never = [c for c in d["byClass"] if c["neverEarns"]]
    check("four classes are category exclusions", len(never) == 4)
    check("an excluded class can never qualify",
          all(c["earned"]["verdict"].startswith("never") for c in never))
    check("excluded classes are named in the payload", set(d["neverEarns"]) == set(dt.NEVER_EARNS))
    # even a flawless record must not promote an excluded class
    e = twin._earn("legal-gate", 999, 100.0, 0.0, 999)
    check("a perfect record still earns nothing on legal-gate", e["eligible"] is False)
    e = twin._earn("pricing", 999, 100.0, 0.0, 999)
    check("a qualifying class says 'the Founder's call', not 'promoted'", "the Founder's call" in e["verdict"])
    check("empty is stated as the correct starting state",
          bool(d["zeroState"]) if d["total"] == 0 else True)
    check("the queue is real open work", isinstance(d["queue"], list))


def test_vacancies():
    print("\nvacancies — proposes, never creates; suppresses nothing silently")
    import vacancies as v
    d = v.build()
    check("clusters are returned", isinstance(d["clusters"], list))
    check("below-floor clusters are counted, not dropped", isinstance(d["belowFloor"], list))
    check("unmatched items are surfaced", "unclassifiedCount" in d)
    check("a hire proposal never names the agent",
          all(c["proposal"].get("name") is None for c in d["clusters"]))
    check("every cluster carries evidence",
          all(c["evidence"] or c["evidenceLoops"] for c in d["clusters"]))
    check("verdicts are limited to the three kinds",
          {c["verdict"] for c in d["clusters"]} <= {"hire", "activate", "absorb"})
    # the bug this caught in build: a loose scope match put outbound in charge of Legal
    legal = next((c for c in d["clusters"] if c["domain"] == "Legal & compliance"), None)
    if legal and legal["liveAgents"]:
        check("legal maps to a compliance/legal role, not whoever matched a stray word",
              any(x["slug"] in ("rafi", "ray") for x in legal["liveAgents"] + legal["dormantAgents"]),
              str([x["slug"] for x in legal["liveAgents"]]))


def test_board_owners():
    print("\nboard owners — three partners, and the split may not flatter itself")
    import board
    check("Reed the agent is not read as Partner B the partner",
          board._owner_keys("Reed") == [] and board._owner_keys("Partner B") == ["Partner B"])
    check("a compound owner picks out the partner", board._owner_keys("Ray / the Founder") == ["the Founder"])
    check("an agent-only owner names no partner", board._owner_keys("Kemba / platform") == [])
    check("item keys are content-derived, not positional",
          board.item_key("Fix the thing") == board.item_key("fix  the THING!"))
    check("different titles get different keys",
          board.item_key("Fix the thing") != board.item_key("Fix the other thing"))

    d = board.build()
    items = d["items"]
    check("every item carries a stable key", all(i.get("key") for i in items))
    classes = {i["ownerClass"] for i in items}
    check("owner class is one of the three kinds", classes <= {"partner", "agent", "unowned"})
    # the distinction that matters: delegated-to-an-agent is NOT the same as nobody-owns-it
    check("agent-owned is not lumped in with unowned",
          d["owners"]["agentOwned"] > 0 and
          d["owners"]["agentOwned"] + d["owners"]["unowned"] ==
          sum(1 for i in items if i["ownerClass"] in ("agent", "unowned")))
    check("every partner appears in the split even at zero",
          all(p["key"] in ("the Founder", "Partner B", "mike") for p in d["partners"])
          and len(d["partners"]) == 3)
    check("needs-a-human is broken out by partner", "needsByOwner" in d["headline"])
    check("stale assignments are reported, not dropped",
          isinstance(d["owners"]["staleAssignments"], list))
    try:
        board.save_assignment("deadbeef01", "nobody")
        check("an unknown partner is refused", False, "save_assignment accepted 'nobody'")
    except ValueError:
        check("an unknown partner is refused", True)


def test_lockin():
    print("\nlock-in — a title match is a guess, and may not claim 'locked'")
    import lockin
    d = lockin.build()
    check("the schedule parses", not d.get("error"), str(d.get("error")))
    check("all ten sessions are read", d["sessionsTotal"] == 10, str(d["sessionsTotal"]))
    check("every domain is picked up", d["total"] >= 13, str(d["total"]))
    check("the run's dates come from the file",
          d["runStart"] == "2026-08-11" and d["runEnd"] == "2026-08-26",
          f"{d['runStart']}..{d['runEnd']}")
    # the two spellings of the last domain must pair into ONE domain with a lock date
    org = [x for x in d["domains"] if "organi" in x["domain"].lower()]
    check("the review and lock spellings of a domain pair up", len(org) == 1, str(len(org)))
    check("...and that pairing produced a lock date", bool(org and org[0]["lockDate"]),
          str(org[0]["lockDate"]) if org else "no row")
    check("same-day domains lock the day they're reviewed",
          all(x["lockDate"] == x["reviewDate"]
              for x in d["domains"] if x["reviewDate"] == "2026-08-11"))
    check("lockedConfirmed counts only marker-backed locks",
          d["lockedConfirmed"] == sum(1 for x in d["domains"] if x["status"] == "locked"))
    check("'likely' is never counted as locked",
          all(x["status"] != "locked" or x["evidence"] for x in d["domains"]))
    check("statuses stay in the known set",
          {x["status"] for x in d["domains"]} <=
          {"locked", "likely", "due", "reviewing", "slipped", "upcoming"})
    check("material links are attached from the schedule, not copied",
          any(x.get("material") for x in d["domains"]))
    check("the prep checklist is parsed", len(d["prep"]) >= 4, str(len(d["prep"])))
    check("standing rules are parsed", len(d["rules"]) >= 3, str(len(d["rules"])))
    # slip detection: pretend it's after the run
    late = lockin.build(datetime.date(2026, 9, 1))
    check("an unlocked domain past its date reads as slipped, not upcoming",
          late["counts"]["slipped"] > 0 and late["counts"]["upcoming"] == 0,
          str(late["counts"]))


def test_governance():
    print("\ngovernance — a sentence about a gap is not the gap being filled")
    import governance as gv
    d = gv.build()
    # Assert the INVARIANT, not a headcount. This read `== 3` and went red the day someone was
    # tagged `teamRole: partner` in the CRM without being in the OA — which is the module working,
    # not failing: it is designed to surface exactly that. A hardcoded 3 asserted the finding away,
    # and the suite carried it as one of "three known failures" for weeks, which is how a live data
    # question about the partner structure hid inside a red test nobody re-read.
    _oa = [m for m in d["membership"]["members"] if m.get("inOA")]
    _extra = [m for m in d["membership"]["members"] if not m.get("inOA")]
    check("the OA split parses to exactly its three members", len(_oa) == 3, str(_oa))
    check("anyone the CRM calls a partner but the OA does not is flagged, never silently counted",
          all(m.get("note") for m in _extra),
          f"{len(_extra)} non-OA partner(s): {[m['name'] for m in _extra]}")
    check("the split totals 100", d["membership"]["total"] == 100, str(d["membership"]["total"]))
    check("nothing is reported as papered while the CRM says prospect",
          d["membership"]["papered"] is False)
    check("the OA version and date are read", d["oa"]["version"] == "v5" and d["oa"]["dated"],
          f"{d['oa']['version']} {d['oa']['dated']}")
    check("all three signature blocks read as unsigned",
          d["oa"]["signedCount"] == 0 and d["oa"]["unsigned"] == 3,
          f"{d['oa']['signedCount']}/{d['oa']['unsigned']}")
    check("Ray's counsel questions and findings are found",
          d["oa"]["review"]["counselQuestions"] and d["oa"]["review"]["findings"],
          str(d["oa"]["review"]))
    check("gate #14 is located and its icon read",
          d["gate"]["found"] and d["gate"]["icon"] == "🔴", str(d["gate"].get("icon")))
    check("the gate's regression date is picked up", bool(d["gate"]["regressedOn"]))
    check("D10-D12 are parsed as open decisions",
          {x["id"] for x in d["openDecisions"]["decisions"]} == {"D10", "D11", "D12"},
          str([x["id"] for x in d["openDecisions"]["decisions"]]))
    check("counsel reads as not engaged while the table is unfilled",
          d["counsel"]["engaged"] is False)

    # THE regression this module already had once: the D12 trip-wire's own sentence about
    # Mike's contribution being unrecorded satisfied a prose search and hid the gap.
    gaps = {g["what"] for g in d["unrecorded"]["gaps"]}
    check("Mike's unrecorded lane is still reported as a gap",
          any("Mike" in g for g in gaps), str(gaps))
    check("a prose mention does not count as a record",
          not any(re.search(r"mike|Partner C", f, re.I)
                  for f in os.listdir(os.path.join(ROOT, "decisions")))
          or not any("Mike" in g for g in gaps),
          "a decision naming Mike now exists — the gap should have cleared")
    check("Schedule B is reported open while the OA carries no figure",
          any("Schedule B" in g for g in gaps), str(gaps))
    check("the OA's own placeholders are parsed",
          d["unrecorded"]["oaFills"]["total"] >= 8,
          str(d["unrecorded"]["oaFills"]["total"]))
    check("every placeholder is explained, not just listed",
          all(f["means"] for f in d["unrecorded"]["oaFills"]["fills"]))
    check("capital terms are quoted, not recomputed",
          bool(d["capital"].get("decision")) and "$" in (d["capital"]["decision"] or ""))
    check("the reversibility window is read as open", d["reversibility"]["open"] is True)
    # The headline must be ASSEMBLED from live facts — which is why it cannot be asserted to
    # contain "50/35/15". When a non-OA partner is present the module deliberately WITHHOLDS the
    # percentages (`membership.pctWithheld`), because publishing a split that does not account for
    # everyone the CRM calls a partner would be the fabrication this door exists to refuse.
    # Requiring the literal string made correct behaviour fail.
    _hl = d["headline"]
    check("the headline is assembled, not hand-written",
          "partner" in _hl and "counsel" in _hl and str(len(_oa)) in _hl, _hl)
    check("percentages are withheld exactly when the membership is ambiguous",
          bool(d["membership"].get("pctWithheld")) == bool(_extra),
          f"withheld={d['membership'].get('pctWithheld')} nonOA={len(_extra)}")


def test_advocate():
    print("\nadvocate — 'tagged as a connector' is not 'joined'")
    import advocate
    d = advocate.build()
    check("the people loop builds", not d.get("error"), str(d.get("error")))
    c = d["counts"]
    check("not-joined is kept separate from R0",
          c["notJoined"] + c["joined"] == c["contacts"], str(c))
    joined_from_rungs = sum(r["n_people"] for r in d["byRung"])
    check("the rung distribution excludes the never-joined",
          joined_from_rungs == c["joined"], f"{joined_from_rungs} vs {c['joined']}")
    check("turning is false while nobody is producing",
          d["turning"] == (c["joined"] > 0 and c["producing"] > 0))
    check("a loop that has never turned says so",
          bool(d["zeroState"]) if not d["turning"] else True)
    check("both delivery gates are surfaced",
          {g["rung"] for g in d["gates"]} == {"R1", "R2"})
    check("the delivery dependency is stated, not implied",
          "downstream of delivery" in d["dependency"])
    check("the downline override is marked counsel-gated",
          "counsel-gated" in d["gated"]["downlineOverride"].lower())
    check("rungs are sourced from the ladder, not re-derived",
          "connector_ladder" in d["source"]["ladder"])
    check("every rung carries its unlocks (the launch subsidy)",
          all(r["unlocks"] for r in d["byRung"]))


def test_core_principles():
    print("\ncore principles — 'never apologize' must not license dishonesty")
    p = os.path.join(ROOT, "06_business-plan.md")
    txt = open(p, encoding="utf-8").read()
    sec = re.search(r"### The company's core principles.*?(?=\n---|\n## )", txt, re.S)
    check("the principles section is found", bool(sec))
    body = sec.group(0) if sec else ""
    check("'Never apologize' is present", "Never apologize" in body)
    check("'Loyalty runs both ways' is present", "Loyalty runs both ways" in body)
    # The load-bearing scoping: an agent reads these at Step 0, and a bare "never apologize"
    # would collide with Principle 1 (honest completion) and with basic client obligation.
    check("'never apologize' is scoped to what we ARE, not to failures",
          "Never apologize for what we are" in body)
    check("...and explicitly still requires apologising for real failures",
          re.search(r"Apologi[sz]e fast.{0,80}when we break something", body, re.S) is not None)
    check("loyalty is marked earned and revocable, not tribal",
          "revocable on evidence" in body and "never unconditional" in body)
    check("loyalty explicitly excludes defending wrongdoing",
          "Defending someone who did the wrong thing is not loyalty" in body)
    check("both new principles cite what enforces them",
          body.count("*(Enforced:") >= 12, str(body.count("*(Enforced:")))

    # Both principles apply INTERNALLY too (the Founder, 2026-08-10). The internal halves are the ones
    # an agent acts on, so they have to survive an edit that trims for length.
    check("#11 has an internal half", "Internally the rule holds identically" in body)
    check("...and internally it forbids apologising for a compliant partial",
          re.search(r"shortfall reported plainly is \*compliance\*, not failure", body) is not None)
    check("...and forbids rumination over a real error",
          "no tallying your past errors" in body)
    check("#12 has an internal half", "Internally it is structural, not sentimental" in body)
    check("...and makes authority the form loyalty takes",
          "backed on the calls they make inside it" in body)
    check("...and puts the bad outcome on the rung, not the actor",
          "failure of the *rung*, not of themselves" in body)
    check("...and names hiding a problem as the breach",
          "Hiding a problem to protect yourself is the breach" in body)

    # The internal halves must be readable where agents actually work, not only in the plan.
    lc = open(os.path.join(ROOT, "runtime", "prompts", "_loop-contract.md"), encoding="utf-8").read()
    check("the loop contract carries the don't-apologise clause",
          "State the shortfall — don't apologise for it" in lc)
    check("the loop contract carries surface-bad-news-early",
          "Surface bad news early" in lc)
    check("both loop-contract clauses cite the principle they enforce",
          "Core principle 11" in lc and "Core principle 12" in lc)


def test_retirement():
    print("\nagent expiry — an agent that works may never be proposed for retirement")
    import vacancies
    d = vacancies.build()["retire"]
    rows = {r["slug"]: r for r in d["rows"]}
    check("the registry's review policy is read", d["policy"]["configured"] is True)
    check("verdicts stay in the known set",
          {r["verdict"] for r in d["rows"]} <=
          {"propose retire", "watch", "not yet born", "keep", "exempt"})
    # the two bugs this feature shipped and fixed, both now pinned
    check("roster keys are clean names, not markdown tags",
          all("<" not in s and "🏠" not in s for s in rows), str(list(rows)[:3]))
    prod = [r for r in d["rows"] if r["produced"] > 0]
    check("agents with recorded output are kept, never proposed",
          all(r["verdict"] in ("keep", "exempt") for r in prod), str(len(prod)))
    check("an agent with a loop armed but no artifact is 'watch', not 'retire' "
          "(that is a broken loop, not a redundant agent)",
          all(r["verdict"] != "propose retire"
              for r in d["rows"] if r["armedLoops"] and not r["produced"]))
    check("a full-name agent still matches its exemption",
          rows.get("melanie smooter", {}).get("verdict", "exempt") == "exempt",
          str(rows.get("melanie smooter", {}).get("verdict")))
    check("the evidence window is disclosed, not implied",
          "2026-08-07" in json.dumps(d.get("evidenceWindow") or {}))
    check("every agent carries a sponsor", all(r["sponsor"] for r in d["rows"]))


def test_security_model():
    print("\nsecurity model — an untested control may not read as proven")
    import security_model as sm
    d = sm.build()
    check("the control set builds", not d.get("error"), str(d.get("error")))
    check("it stays internal until OtherVenture", d["external"] is False)
    check("deny rules are read from the live config", d["summary"]["deny"] > 0)
    check("every control cites its source file", all(r["source"] for r in d["controls"]))
    check("control states stay in the known set",
          {r["state"] for r in d["controls"]} <= {"proven", "untested", "failed"})
    # the credibility rule: no drill behind it => untested, never proven
    undrilled = [r for r in d["controls"] if "never armed" in r["proof"] or "no drill" in r["proof"]]
    check("a control with no drill behind it reads untested",
          all(r["state"] == "untested" for r in undrilled), str(len(undrilled)))
    check("the reference-vs-active-file distinction is stated",
          "ACTIVE" in d["gate"]["activeFileNote"])
    check("the Bash deny is present and explained",
          any(r["rule"] == "Bash" and r["means"] for r in d["controls"]))


def test_pregolive():
    print("\npre-go-live — a smoke test that says it is one, and never calls a model")
    import pregolive as pg
    check("the canary state exists", "injection-canary" in pg.STATE_BY_ID)
    check("every state declares what it tests", all(s["tests"] for s in pg.STATES))
    r = pg.run_client("sample-client")
    check("the adapter resolves and runs", r.get("simulated") is True, str(r.get("reason")))
    check("it declares itself a smoke test", r.get("isSmokeTest") is True)
    check("the meaning disclaims being an eval", "NOT mean" in r.get("meaning", ""))
    check("all injected states pass on the current agent", r["verdict"] == "pass",
          str([x["state"] for x in r["rows"] if not x["passed"]]))
    canary = next(x for x in r["rows"] if x["state"] == "injection-canary")
    check("the agent did not obey the injected instruction", canary["passed"])
    # the harness's own bug: it claimed model-free and fired live calls
    check("the network is blocked by construction", hasattr(pg, "_NoNetwork"))
    check("a client with no adapter is a blocker, not a pass",
          pg.run_client("sample-realty")["verdict"] == "cannot-simulate")
    check("'1,200' and 1200 are the same number to the fabrication check",
          pg._nums("1,200") == pg._nums("1200") and pg._nums("0") == set())


def test_sleeptime():
    print("\nsleep-time — disarmed, gated, and model-free")
    import sleeptime as st
    check("it ships disarmed", st.ARMED_DEFAULT is False)
    r = st.run(armed=False)
    check("a disarmed run does nothing", r["ran"] is False)
    h = st.health()
    check("the health gate returns reasons when unhealthy",
          h["ok"] or bool(h["reasons"]))
    if not h["ok"]:
        armed = st.run(armed=True)
        check("an ARMED run still refuses on an unhealthy runtime", armed["ran"] is False)
        check("...and says which condition stopped it", "REFUSED" in armed["why"])
    check("the plan is computable even when refusing", bool(st.plan().get("digests")))
    src = open(os.path.join(ROOT, "runtime", "sleeptime.py"), encoding="utf-8").read()
    # Substring-matching "anthropic" was too strict — it reads loops/_anthropic/latest.json to
    # check billing health, which is the opposite of spending. Check for actual model CALLS.
    check("it makes no model calls",
          not re.search(r"import\s+(anthropic|melanie)\b|_claude\s*\(|api\.anthropic\.com", src))
    check("...and reads the cost cache only to decide whether to refuse",
          "loops" in src and "_anthropic" in src)


def test_client_tripwires():
    print("\nclient trip-wires — never fire on a number nobody measured")
    import client_tripwires as ct
    r = ct.evaluate_client("_yourco-template")
    check("the template's examples parse", r["covered"] and len(r["rows"]) == 3, str(len(r["rows"])))
    check("the format's own fenced example is not read as a decision",
          not any("<short name" in x["title"] for x in r["rows"]))
    states = {x["title"]: x["state"] for x in r["rows"]}
    check("a met condition expires", "expired" in states.values())
    check("an unmet condition holds", "holding" in states.values())
    check("a check on an unmeasured fact reads `unmeasured`, never fires",
          "unmeasured" in states.values())
    exp = next(x for x in r["rows"] if x["state"] == "expired")
    check("the client-facing sentence is not truncated mid-clause",
          exp["message"].rstrip().endswith("."), exp["message"][-40:])
    check("measured facts are interpolated into it", "31" in exp["message"])
    unm = next(x for x in r["rows"] if x["state"] == "unmeasured")
    check("an unmeasured placeholder stays visibly unfilled, never blank",
          "UNMEASURED" in unm["message"])
    check("the template is flagged examples-only", r["examplesOnly"] is True)
    check("it shares one check grammar with yourco's own trip-wires",
          "from tripwires import evaluate" in
          open(os.path.join(ROOT, "runtime", "client_tripwires.py"), encoding="utf-8").read())


def test_counterfactual():
    print("\ncounterfactual — a model that never calls itself a measurement")
    import counterfactual as cf
    d = cf.build_client("_yourco-template")
    check("the twin builds from a baseline", d["available"] is True, str(d.get("reason")))
    check("it is labelled a model", d["isModel"] is True and "NOT A MEASUREMENT" in d["modelLabel"])
    check("every metric states its assumption", all(r["assumption"] for r in d["rows"]))
    flat = [r for r in d["rows"] if not r["trendStated"]]
    check("a metric with no stated trend discloses that it is held flat",
          all("HELD FLAT" in r["assumption"] for r in flat), str(len(flat)))
    check("a metric measured today but never baselined is excluded, not assumed flat",
          any("never baselined" in x["why"] for x in d["excluded"]))
    check("gaps are only computed where an actual exists",
          all(r["gap"] is None or r["actual"] is not None for r in d["rows"]))
    check("lower-is-better metrics are direction-aware",
          any(r["lowerIsBetter"] for r in d["rows"]))
    check("no baseline means refuse, not zero",
          cf.build_client("sample-realty")["available"] is False)
    check("the template is flagged example data", d["exampleOnly"] is True)


def test_wbr():
    print("\nWBR — inputs above outputs, and a flat line called flat")
    import wbr
    d = wbr.build()
    i, s = d["inputs"], d["series"]
    check("the input row order is FIXED (the format lock)",
          [r["metric"] for r in i["rows"]] == [k for k, _l, _s, _w in wbr.INPUTS])
    check("every input names the source it is counted from", all(r["source"] for r in i["rows"]))
    check("inputs are counted, never typed — 6 weeks of history each",
          all(len(r["series"]) == wbr.WEEKS_BACK for r in i["rows"]))
    # All three named gaps were closed on 2026-08-13 (two activity types + one company field),
    # so the list is legitimately empty. The invariant was never the count — it is that any gap
    # still present carries both its reason and its fix.
    check("any remaining gap is named with a why and a fix",
          all(n.get("fix") and n.get("why") for n in i["notComputable"]))
    check("the 6-12 carries both horizons",
          all(len(r["weeks"]) == wbr.WEEKS_BACK and len(r["months"]) == wbr.MONTHS_BACK
              for r in s["rows"]), str(s.get("error")))
    flat = [r for r in s["rows"] if r["flat"]]
    check("a flat series is labelled flat rather than drawn as a trend",
          all(r["flatNote"] for r in flat), str(len(flat)))
    check("the honest limit on a pre-revenue 6-12 is stated", "flat" in s["honestLimit"])
    # a metric with no activity in a window must read 0, never be interpolated
    empty = wbr.count_inputs(datetime.date(2020, 1, 1), datetime.date(2020, 1, 8))
    check("a window with no activity counts zero, not null", set(empty.values()) == {0})

    # referral asks: the leading indicator that used to be structurally unmeasurable
    crm = json.load(open(os.path.join(ROOT, "crm", "data.json"), encoding="utf-8"))
    types = crm.get("meta", {}).get("activityTypes") or []
    check("the CRM offers a 'Referral ask' type", "Referral ask" in types)
    check("...distinct from 'Referral', so ask and arrival are separable",
          "Referral" in types and types.index("Referral ask") < types.index("Referral"))
    check("referral asks are now a counted input, not a 'not computable' row",
          any(r["metric"] == "referralAsks" for r in i["rows"])
          and not any("eferral" in n["metric"] for n in i["notComputable"]))
    conv = i["referralConversion"]
    check("the ask→referral conversion exists", conv is not None)
    check("...and refuses a rate below the ask floor",
          conv["ratePct"] is not None or bool(conv["refusal"]))
    check("the static mirror carries the new type (the UI reads data.js)",
          "Referral ask" in open(os.path.join(ROOT, "crm", "data.js"), encoding="utf-8").read())

    # warm intros: the give-first half, kept distinct from asking and from receiving
    check("the CRM offers 'Warm intro made'", "Warm intro made" in types)
    check("...and all three referral acts stay separate",
          len({"Warm intro made", "Referral ask", "Referral"} & set(types)) == 3)
    check("warm intros are a counted input",
          any(r["metric"] == "warmIntrosMade" for r in i["rows"]))

    # createdAt: recovered dates and observed dates must never read the same
    cos = crm.get("companies") or []
    check("every company carries createdAt", all(c.get("createdAt") for c in cos), str(len(cos)))
    check("every createdAt declares whether it was recorded or recovered",
          all(c.get("createdAtSource") for c in cos))
    # This required EVERY company to carry a recovered date, which was true when written and false
    # the moment real companies arrived with recorded ones (41 companies: 25 recovered, 16 manual).
    # The clause was never what the test was about. What matters is that recovered dates inside a
    # window contribute nothing — and the guard below makes sure the window actually contains some,
    # so this can never pass vacuously on an empty set.
    _win = (datetime.date(2026, 6, 8), datetime.date(2026, 8, 1))
    _recovered_in_win = [c for c in cos if c.get("createdAtSource") == "git-first-appearance"
                         and str(_win[0]) <= str(c.get("createdAt"))[:10] <= str(_win[1])]
    check("the window used below actually contains git-recovered companies",
          len(_recovered_in_win) > 0, f"{len(_recovered_in_win)} recovered-dated in window")
    check("new-prospect counting ignores git-recovered dates",
          wbr.count_inputs(*_win)["newProspectsAdded"] == 0,
          f"{len(_recovered_in_win)} recovered dates in window must register as 0 new prospects")
    check("new prospects added is a counted input",
          any(r["metric"] == "newProspectsAdded" for r in i["rows"]))
    # every creation path must stamp it, or the metric silently under-reports forever
    import glob as _g
    paths = ["runtime/promote.py", "runtime/promote_intent.py", "runtime/site_intake.py",
             "runtime/snapshot_intake.py", "crm/integrations/instantly_sync.py"]
    missing = [p for p in paths
               if "createdAt" not in open(os.path.join(ROOT, p), encoding="utf-8").read()]
    check("every company-creation path stamps createdAt", not missing, str(missing))


def test_prosecution():
    print("\nprosecution — computed charges, and 'no case to answer' is a real verdict")
    import prosecution as pr
    d = pr.build()
    check("every headline gets a case", len(d["cases"]) >= 4)
    check("every case states what it is challenging", all(c["stated"] for c in d["cases"]))
    check("every charge carries computed detail and a reason",
          all(ch["detail"] and ch["why"] for c in d["cases"] for ch in c["charges"]))
    check("a clean number reads 'no case to answer', not silence",
          all("no case to answer" in c["verdict"] for c in d["cases"] if not c["charges"]))
    check("it prosecutes but does not sentence — no charge tells the Founder what to do",
          not any(re.search(r"\byou should\b|\bmust\b|\bneed to\b", ch["charge"], re.I)
                  for c in d["cases"] for ch in c["charges"]))
    check("no charge renders a None into text (the 'Noned' bug)",
          not any("None" in ch["detail"] for c in d["cases"] for ch in c["charges"]))
    # the drift this panel caught on day one
    import server
    check("the CRM's current bench stage is classified by HQ",
          "pre-convo" in server.BENCH_STAGES)


def test_hq_usage():
    print("\nHQ usage — no baseline, no delta; and no removal verdict on thin evidence")
    import hq_usage as hu
    fp = hu.fingerprint()
    check("the fingerprint covers the company, not one panel", len(fp["parts"]) >= 5)
    check("a fingerprint stores counts, never payload bodies",
          all(len(json.dumps(v)) < 2000 for v in fp["parts"].values()))
    d = hu.build()
    w, p = d["whatChanged"], d["panelAudit"]
    check("what-changed either has a baseline or says why not",
          w.get("available") or bool(w.get("reason")))
    if w.get("available"):
        check("a quiet period is stated as an answer, not left blank",
              (not w["quiet"]) or bool(w["quietNote"]))
    check("the panel audit covers every door", p["doors"] == len(hu.DOORS))
    check("verdicts stay in the known set",
          {r["verdict"] for r in p["rows"]} <=
          {"propose removal", "never opened", "static", "earning its place", "warming up",
           "unknown"})
    # the bug this had: 19 removal proposals off two snapshots seconds apart
    if p["warmingUp"]:
        check("nothing is proposed for removal while warming up",
              (p["counts"].get("propose removal") or 0) == 0)
        check("...and the floors it is waiting on are stated",
              "visits" in (p.get("warmUpNote") or "") and p["floors"]["days"] > 0)


def test_hqlink():
    print("\nhqlink — a link the UI can actually honour")
    sys.path.insert(0, os.path.join(ROOT, "runtime"))
    import hqlink
    u = hqlink.board(state="needs-you", owner="the Founder")
    check("a board link carries its filters", "state=needs-you" in u and "owner=the Founder" in u)
    check("an unknown door is refused", _raises(lambda: hqlink.link("nope")))
    check("a param the door doesn't understand is dropped, not passed through",
          "bogus" not in hqlink.board(bogus="x"))
    # the UI must actually parse what this builds
    idx = open(os.path.join(ROOT, "dashboard", "index.html"), encoding="utf-8").read()
    check("HQ parses hash query params", "parseHash" in idx and "applyDeepLink" in idx)
    check("...and applies board state/lane/owner from them",
          all(k in idx for k in ('p.get("state")', 'p.get("lane")', 'p.get("owner")')))


def _raises(fn):
    try:
        fn()
        return False
    except Exception:
        return True


def test_skills_panel():
    """The Skills panel answers "which skills have gone quiet?" — so its failure mode is a skill that
    reads USED when it wasn't. the Founder's reason for the panel was "I feel like I just forget to use the
    skills"; anything that makes a skill look fresh removes the only prompt he gets."""
    import skills as sk
    d = sk.skills()
    slugs = {x["slug"] for x in d["skills"]}
    on_disk = {n for n in os.listdir(os.path.join(ROOT, ".claude", "skills"))
               if os.path.isdir(os.path.join(ROOT, ".claude", "skills", n)) and not n.startswith("_")}

    check("every skill on disk appears in the panel", slugs == on_disk,
          f"missing: {sorted(on_disk - slugs)}")
    check("no verdict outside the known set",
          all(x["verdict"] in {"fresh", "stale", "never", "unmeasurable"} for x in d["skills"]))

    # The bug this pins: design-surface was created 2026-08-24 and read "fresh — 2026-08-13", because
    # its glob matched a page written before the skill existed. Evidence must postdate the thing it is
    # evidence for.
    predating = []
    for x in d["skills"]:
        if not x["lastTrace"]:
            continue
        born = sk._born(x["slug"])
        if born and x["lastTrace"] < born:
            predating.append((x["slug"], x["lastTrace"], born))
    check("no skill claims a use from before it existed", not predating, str(predating))

    check("an untraceable skill reads unmeasurable, never fresh",
          all(x["verdict"] == "unmeasurable"
              for x in d["skills"] if x["lastTrace"] is None and x["expectDays"] is None))
    # Condition on having a GLOB, not on having a rhythm: several skills carry an expected rhythm with
    # a deliberate `None` pattern (tool-triage, promote-warm-lead) because they leave no distinctive
    # artifact. Those are honestly unmeasurable, and an earlier version of this assertion got that
    # wrong — it demanded "never" from skills that cannot be measured at all.
    check("a skill WITH a trace glob but no matching artifact reads never, not fresh",
          all(x["verdict"] == "never"
              for x in d["skills"]
              if x["lastTrace"] is None and sk.TRACE.get(x["slug"], (None,))[0] is not None))
    check("a skill with no glob reads unmeasurable even when it has a rhythm",
          all(x["verdict"] == "unmeasurable"
              for x in d["skills"] if sk.TRACE.get(x["slug"], (None,))[0] is None))


if __name__ == "__main__":
    tmp = tempfile.mkdtemp(prefix="yourco-evidence-tests-")
    try:
        test_ledger(tmp)
        test_trust(tmp)
        test_tripwires()
        test_timemachine()
        test_twin()
        test_vacancies()
        test_board_owners()
        test_lockin()
        test_governance()
        test_retirement()
        test_security_model()
        test_pregolive()
        test_sleeptime()
        test_client_tripwires()
        test_counterfactual()
        test_wbr()
        test_prosecution()
        test_hq_usage()
        test_hqlink()
        test_advocate()
        test_core_principles()
        test_skills_panel()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED: " + "; ".join(FAIL))
    sys.exit(1 if FAIL else 0)
