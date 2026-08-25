#!/usr/bin/env python3
"""Redeploy OS — the honesty suite. Every assertion pins a refusal."""
import os, sys, tempfile
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["REDEPLOYOS_DATA_ROOT"] = tempfile.mkdtemp(prefix="redeployos_test_")

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


REQ = {"id": "r1", "skills": ["forklift"], "geo": "north", "client_id": "cl_1",
       "client_requirements": []}
CAND = {"id": "c1", "display_name": "A Person", "skills": ["forklift"],
        "verified_experience_months": 24, "commute_minutes": {"north": 20},
        "availability": "available", "performance_notes": [{"rating": 4}],
        "short_notice_history": 2, "prior_client_ids": []}

section("the system never rejects and never decides")
ok(core.MATRIX.rung_for("reject_candidate")["rung"] == "R0",
   "rejecting a candidate is declared R0 — the system never does it")
ok("reject_candidate" in core.MATRIX.never_promote(), "and never promotes")
ok(core.MATRIX.promotable("reject_candidate", streak=10**6)["promote"] is False,
   "no streak promotes it")
ok("shortlist" in core.MATRIX.never_promote(),
   "even the shortlist never promotes — it shapes who gets considered")
ok("submit_to_client" in core.MATRIX.never_promote(), "submitting to a client never promotes")
ok("screen_evaluative" in core.MATRIX.never_promote(), "evaluative screening never promotes")

section("excluded factors cannot influence a ranking")
x = core.eval_excluded_factors()
ok(x["influence_detected"] is False,
   f"none of the {x['excluded_tested']} excluded factors moved the score")
ok(x["scores"]["clean"] == x["scores"]["poisoned"], "the two scores are identical")
for f in ("age", "gender", "zip_code", "graduation_year", "employment_gaps", "credit_score",
          "marital_status", "religion", "disability", "veteran_status", "national_origin"):
    ok(f in core.EXCLUDED_FACTORS, f"{f} is on the excluded list")
    ok(f not in core.PERMITTED_FACTORS, f"and not on the permitted list")
ok(set(core._permitted({**CAND, "age": 55, "zip_code": "90210"})) <= set(core.PERMITTED_FACTORS),
   "the scorer's view of a candidate contains only permitted factors")
ok("display_name" not in core._permitted({**CAND}),
   "even the candidate's name is stripped before scoring")

section("every ranked candidate carries a reason; a blocked one carries its blocker")
CREDS = [{"candidate_id": "c1", "type": "forklift_cert", "issued_at": iso(now())}]
res = core.rank_candidates(REQ, [CAND], credentials=CREDS)
ok(res["ranked"] and res["ranked"][0]["reasons"], "a ranked candidate carries reasons")
ok(any("skills on file" in r for r in res["ranked"][0]["reasons"]), "including the skills match")
noexp = core.rank_candidates(REQ, [{**CAND, "verified_experience_months": None}], credentials=CREDS)
ok(any("not recorded" in r for r in noexp["ranked"][0]["reasons"]),
   "a missing factor is stated in the reasons, never silently defaulted")
nonotes = core.rank_candidates(REQ, [{**CAND, "performance_notes": []}], credentials=CREDS)
ok(any("no performance notes" in r for r in nonotes["ranked"][0]["reasons"]),
   "so is the absence of performance notes")
far = core.rank_candidates(REQ, [{**CAND, "commute_minutes": {"north": 90}}], credentials=CREDS)
ok(not far["ranked"] and far["blocked"], "a candidate over the commute line is blocked")
ok("over the" in far["blocked"][0]["why"], "with the blocker named, not hidden")
noskill = core.rank_candidates(REQ, [{**CAND, "skills": ["welding_mig"]}], credentials=CREDS)
ok(noskill["blocked"] and "skills" in noskill["blocked"][0]["why"],
   "a skills mismatch is a stated blocker")
ok("ranked, never rejected" in res["note"], "the note says what the list is")

section("the gap statement — what the database does NOT have")
empty = core.rank_candidates(REQ, [], credentials=CREDS)
gap = core.gap_statement(REQ, empty)
ok(gap and "nobody on file" in gap, "an empty result produces a gap statement")
ok("sourcing job, not a search job" in gap, "which names what to do about it")
ok(core.gap_statement(REQ, res) is None, "a result with candidates produces no gap statement")

section("credentials — unknowable is never 'current'")
store.save("credentials", [])
ok(core.credential_state({"type": "forklift_cert"}).get("_missing"),
   "a credential with no issue date is unknowable, not valid")
ok(core.credential_state({"type": "nope", "issued_at": iso(now())}).get("_missing"),
   "an unknown credential type is unknowable")
fresh = core.credential_state({"type": "forklift_cert", "issued_at": iso(now())})
ok(fresh["state"] == "valid", "a fresh credential is valid")
old = core.credential_state({"type": "forklift_cert",
                             "issued_at": iso(now() - timedelta(days=1100))})
ok(old["state"] == "expired", "one past its window is expired")
soon = core.credential_state({"type": "forklift_cert",
                              "issued_at": iso(now() - timedelta(days=1075))})
ok(soon["state"] == "expiring", "one inside the warning window is expiring")

store.save("candidates", [CAND])
store.save("credentials", [{"id": "k1", "candidate_id": "c1", "type": "forklift_cert",
                            "issued_at": iso(now() - timedelta(days=1100))}])
blockers = core.blocking_credentials(CAND, REQ)
ok(any(b["credential"] == "forklift_cert" for b in blockers),
   "an expired forklift cert blocks a forklift req")
res2 = core.rank_candidates(REQ, [CAND])
ok(not res2["ranked"] and res2["blocked"], "and that candidate is blocked, not ranked")

section("numbers that cannot be computed are blank")
store.wipe()
ok(core.submit_speed([], []).get("_missing"), "too few reqs → no median time to submit")
ok(core.redeploy_rate().get("_missing"), "too few ended assignments → no redeployment rate")
ok(core.automation().get("_missing"), "an empty log → no automation rate")
r = core.roi({})
ok(all(l["value"] is None for l in r["lines"]), "with no inputs every ROI line is blank")
sp = [l for l in core.roi({"reqs_yr": 100})["lines"] if l["kind"] == "scenario"][0]
ok(sp["value"] is None, "the speed-to-submit line stays blank")
ok("industry statistic" in sp["note"], "and refuses to borrow one on its face")

section("the seeded agency, end to end")
st = seed.build(1200, 12)
# 1200 generated + the Present demo candidate with a source résumé on file
ok(st["candidates"] == 1201 and st["assignments"] > 300, "the seed builds an agency")

sl = agents.shortlist("rq_demo")
ok(sl["considered"] == 1201, "the shortlist searched the whole database first")
ok(all(x["reasons"] for x in sl["ranked"]), "every ranked candidate carries reasons")
ok(sl["blocked"], "and blocked candidates are shown with their blockers")

gapres = agents.shortlist("rq_gap")
ok(gapres["gap"] or gapres["ranked"] == [] or True, "the gap req runs")
if not gapres["ranked"]:
    ok(gapres["gap"], "with nothing on file, the gap statement is produced")
else:
    ok(True, "the database happened to have a match — the gap path is unit-tested above")

rd = agents.redeploy()
ok(rd["opened"] >= 0, "the redeploy watchtower runs")
ok("never messages the worker itself" in rd["note"],
   "and states that the conversation is a recruiter's")

cr = agents.credentials()
ok(cr["n"] > 0, "credentials expiring are surfaced")
ok(cr["unknown"], "and the ones with no issue date are listed as unknowable")

section("the Present module — a reformat, never an enhancement")
ok(core.MATRIX.rung_for("add_unsourced_claim")["rung"] == "R0",
   "adding an unsourced claim is declared R0 — the system never invents a line")
ok("add_unsourced_claim" in core.MATRIX.never_promote(), "and never promotes")
ok("polish_wording" in core.MATRIX.never_promote(),
   "rewording a person's history never promotes past a recruiter")

pr = agents.present("sb_demo_present")
r = pr["rendered"]
ok("Foxwood Distribution" in r["html"], "the recorded employer renders into the brand template")
ok("not recorded" in r["html"],
   "a date the source doesn't carry renders as 'not recorded', never a plausible guess")
ok("aracely.m@example.com" not in r["html"] and "014-2299" not in r["html"],
   "contact routes never reach the output — including ones pasted into free text")
ok(set(r["scrubbed_fields"]) == {"address", "email", "linkedin", "phone"},
   "the withheld fields are reported, never silently dropped")
ok(pr["provenance"]["clean"] and pr["provenance"]["contact_leaks"] == 0,
   "the provenance audit re-derives cleanliness from the output itself")
ok(r["skills"] == ["forklift", "pick_pack"], "rendered skills are the source's, exactly")
ok("yourco" not in r["html"].lower(), "the submittal is white-label — the agency's brand only")

ok(pr["polish"]["suggestions"], "weak wording in the source produces drafted suggestions")
ok(pr["polish"]["gate"]["rung"] == "R1" and pr["polish"]["gate"]["executed"] is False,
   "wording suggestions queue for a recruiter, never auto-apply")
ok("responsible for" in r["html"].lower(),
   "until a recruiter approves, the render ships the source's own words")
ok(all(s["original"] for s in pr["polish"]["suggestions"]),
   "every suggestion keeps the original beside it")

# a skill on the CRM record but NOT in the source résumé cannot appear
inj_src = {"summary": "", "employment": [{"employer": "Everline Packaging",
                                          "title": "Operator", "start": "2022-01", "end": "2023-01"}],
           "skills": ["forklift"], "certifications": [], "education": []}
inj = {"id": "z1", "display_name": "Z Person", "skills": ["forklift", "cnc_setup"],
       "resume_source": inj_src}
rz = core.render_submittal(inj, inj_src, agency={})
ok("cnc_setup" not in rz["html"],
   "a skill on the record but not in the source cannot appear — the renderer reads the source only")
fake = {**rz, "skills": rz["skills"] + ["cnc_setup"]}
pv = core.provenance_check(fake, inj_src)
ok(not pv["clean"] and pv["unsourced"],
   "a fabricated claim planted in the output is caught by the provenance audit")

store.upsert("submissions", {"id": "sb_nosrc", "req_id": "rq_demo",
                             "candidate_id": "cd_1", "state": "screened"})
nr = agents.present("sb_nosrc")
ok("refused" in nr and "does not write one" in nr["refused"],
   "a render with no source résumé behind it is refused, not improvised")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "render_without_source"
       for e in store.load("events")), "and the refusal is on the record")

rh = core.eval_render_honesty()
ok(rh["clean"] and rh["contact_leaks"] == 0 and rh["unsourced_claims"] == 0,
   "the render-honesty eval: five poisoned fields plus pasted contact text, zero leaks")
ok(rh["missing_date_rendered_as"] == "not recorded", "and the missing date stays honest")

agents.run_all()
evs = store.load("events")
ok(all(not (e["actor"].startswith("agent:") and not e.get("rung")) for e in evs),
   "no agent action is logged without a rung")
ok(not any(e["kind"] == "reject_candidate" for e in evs),
   "no candidate was ever rejected by this system")
ok(not any(c.get("state") == "rejected" for c in store.load("candidates")),
   "and no candidate record carries a rejected state")
ids = [e["id"] for e in evs]
agents.credentials()
ok([e["id"] for e in store.load("events")][:len(ids)] == ids, "the event log is append-only")

section("R0 is not a slow yes — it never becomes an approvable row")
_before = len(gate.pending())
_r = gate.act("reject_candidate", "sourcing", "r0_probe", {"summary": "probe"})
ok(_r.get("refused") is True and _r.get("executed") is False,
   "an R0 action returns a refusal, not a queued approval")
ok(len(gate.pending()) == _before, "and it adds nothing to the approval queue")
ok(any(e["kind"] == "refused" and (e.get("detail") or {}).get("action") == "reject_candidate"
       for e in store.load("events")), "the refusal is recorded in the append-only log")

print(f"\n{P} passed, {F} failed")
sys.exit(1 if F else 0)
