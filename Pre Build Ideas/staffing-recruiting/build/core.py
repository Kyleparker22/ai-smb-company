#!/usr/bin/env python3
"""Redeploy OS — domain core (staffing · recruiting agencies).

Everything that is a *rule* lives here: candidate, req, assignment and
credential models; the matching and ranking scorer with its PERMITTED-FACTOR
list enforced in code; commute math; the redeploy trigger calendar; credential
expiry; the submission state machine; the ROI model and the autonomy matrix.

The product thesis: the agency's most valuable asset is the database it already
paid for. Every re-source is money spent twice, and an assignment that ends
without a redeployment conversation is the cheapest revenue in the industry,
lost.

THE LOAD-BEARING GUARDRAIL: the system **never rejects a candidate and never
makes a hiring decision.** It ranks, with explicit inspectable reasons, and a
recruiter decides. Ranking inputs are restricted to job-related factors by
construction — protected characteristics and their obvious proxies are excluded
in code, and the test suite poisons a candidate record with them to prove the
score does not move.

Stdlib only.
"""
import re
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "candidates", "reqs", "assignments", "submissions",
          "credentials", "clients", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="REDEPLOYOS_DATA_ROOT")


# ---------------------------------------------------------------- permitted factors
#
# The scorer reads THESE AND NOTHING ELSE. Everything below the line is excluded
# by construction, not by discipline — `_permitted()` strips the record before
# scoring, so a factor that is not on the list cannot reach the arithmetic even
# if somebody adds it to the data later.

PERMITTED_FACTORS = (
    "skills", "certifications", "verified_experience_months", "geo", "commute_minutes",
    "pay_rate_history", "availability", "prior_client_ids", "performance_notes",
    "short_notice_history", "assignment_history_count", "last_worked_at",
)

# Named so a reader can see what is deliberately kept out. Any of these appearing
# in a candidate record is ignored; several are proxies rather than direct
# attributes, which is the half that gets missed.
EXCLUDED_FACTORS = (
    "name", "age", "date_of_birth", "graduation_year", "gender", "pronouns", "race",
    "ethnicity", "national_origin", "language_at_home", "marital_status", "children",
    "religion", "disability", "veteran_status", "zip_code", "neighborhood", "photo",
    "arrest_record", "credit_score", "employment_gaps", "salary_history_prior_employer",
)


def _permitted(candidate):
    """The only view of a candidate the scorer ever sees."""
    return {k: v for k, v in candidate.items() if k in PERMITTED_FACTORS}


# ---------------------------------------------------------------- the work

SKILLS = ("forklift", "pick_pack", "machine_operate", "welding_mig", "welding_tig",
          "cnc_setup", "assembly", "shipping_receiving", "quality_inspect", "maintenance")

CREDENTIALS = {
    "forklift_cert": dict(label="Forklift certification", valid_days=1095, required_for=["forklift"]),
    "osha_10": dict(label="OSHA 10", valid_days=1825, required_for=[]),
    "welding_cert": dict(label="Welding certification", valid_days=730,
                         required_for=["welding_mig", "welding_tig"]),
    "background": dict(label="Background check", valid_days=365, required_for=[]),
    "drug_screen": dict(label="Drug screen", valid_days=365, required_for=[]),
}
EXPIRY_WARN_DAYS = 30
REDEPLOY_TRIGGER_DAYS = 21


def credential_state(cred, ref=None):
    ref = ref or now()
    spec = CREDENTIALS.get(cred.get("type"))
    if not spec:
        return {"state": "unknown", "_missing": "credential type not on file"}
    if not cred.get("issued_at"):
        return {"state": "unknown", "_missing": "no issue date recorded — expiry is unknowable"}
    expires = (parse(cred["issued_at"]) + timedelta(days=spec["valid_days"]))
    left = (expires - ref).days
    return {"state": "expired" if left < 0 else "expiring" if left <= EXPIRY_WARN_DAYS else "valid",
            "days_left": left, "expires": iso(expires), "label": spec["label"]}


def blocking_credentials(candidate, req, ref=None, credentials=None):
    """Which credentials this req requires that this candidate cannot show.

    `credentials` is injectable so the evals can run without store state — a
    scorer that can only be exercised against a live database is a scorer nobody
    audits.
    """
    needed = set()
    for skill in req.get("skills", []):
        for k, spec in CREDENTIALS.items():
            if skill in spec["required_for"]:
                needed.add(k)
    needed |= set(req.get("client_requirements", []))
    if isinstance(credentials, dict):          # pre-indexed by candidate id
        rows = credentials.get(candidate["id"], [])
    else:
        rows = [r for r in (credentials if credentials is not None else store.load("credentials"))
                if r["candidate_id"] == candidate["id"]]
    have = {c["type"]: credential_state(c, ref) for c in rows}
    out = []
    for k in sorted(needed):
        st = have.get(k)
        if st is None:
            out.append({"credential": k, "why": "not on file"})
        elif st.get("_missing"):
            out.append({"credential": k, "why": st["_missing"]})
        elif st["state"] == "expired":
            out.append({"credential": k, "why": f"expired {abs(st['days_left'])} days ago"})
    return out


# ---------------------------------------------------------------- the ranker
#
# Ranks. Never rejects. Every candidate that appears carries a stated reason, and
# a candidate the ranker will not place is still returned with the blocker named
# rather than silently dropped.

MAX_COMMUTE = 45


def rank_candidates(req, candidates=None, ref=None, limit=25, credentials=None):
    ref = ref or now()
    candidates = candidates if candidates is not None else store.load("candidates")
    # Index the credential table ONCE. Loading it per candidate made a sweep
    # O(n²) — 16,500 rows re-read 11,000 times per req, which took the demo from
    # instant to minutes.
    if not isinstance(credentials, dict):
        idx = {}
        for r in (credentials if credentials is not None else store.load("credentials")):
            idx.setdefault(r["candidate_id"], []).append(r)
        credentials = idx
    ranked, blocked = [], []
    for c in candidates:
        p = _permitted(c)
        reasons, score = [], 0.0

        skills = set(p.get("skills") or [])
        need = set(req.get("skills", []))
        hit = need & skills
        if not hit:
            blocked.append({"candidate_id": c["id"], "why": "none of the required skills on file"})
            continue
        # A req can mark skills as MUST-HAVE. Without this, a two-skill req is
        # satisfied by a candidate holding one of them, and the gap statement —
        # the most valuable output this module has — can never fire.
        must = set(req.get("must_have") or [])
        missing = must - skills
        if missing:
            blocked.append({"candidate_id": c["id"],
                            "why": f"missing must-have skill(s): {', '.join(sorted(missing))}"})
            continue
        score += len(hit) / max(1, len(need)) * 3
        reasons.append(f"{len(hit)} of {len(need)} required skills on file: {', '.join(sorted(hit))}")

        exp = p.get("verified_experience_months")
        if exp is None:
            reasons.append("verified experience not recorded")
        else:
            score += min(exp / 24, 1.5)
            reasons.append(f"{exp} months of verified experience")

        cm = p.get("commute_minutes", {}).get(req.get("geo")) if isinstance(p.get("commute_minutes"), dict) else None
        if cm is None:
            reasons.append("commute to this site not recorded")
        elif cm > MAX_COMMUTE:
            blocked.append({"candidate_id": c["id"],
                            "why": f"{cm} minutes from the site, over the {MAX_COMMUTE}-minute line"})
            continue
        else:
            score += (1 - cm / MAX_COMMUTE) * 1.2
            reasons.append(f"{cm} minutes from the site")

        creds = blocking_credentials(c, req, ref, credentials)
        if creds:
            blocked.append({"candidate_id": c["id"],
                            "why": "; ".join(f"{x['credential']} {x['why']}" for x in creds)})
            continue

        if req.get("client_id") in (p.get("prior_client_ids") or []):
            score += 1.0
            reasons.append("has worked this client before")
        notes = p.get("performance_notes") or []
        if notes:
            good = sum(1 for n in notes if n.get("rating", 0) >= 4)
            score += good * 0.3
            reasons.append(f"{good} of {len(notes)} recorded performance notes are strong")
        else:
            reasons.append("no performance notes recorded")

        av = p.get("availability")
        if av == "available":
            score += 1.2
            reasons.append("marked available")
        elif av == "ending_soon":
            score += 0.8
            reasons.append("assignment ending soon — a redeploy rather than a new source")
        else:
            reasons.append(f"availability: {av or 'not recorded'}")

        sn = p.get("short_notice_history")
        if sn is not None:
            score += sn * 0.15
            reasons.append(f"took short notice {sn} of the last 5 times")

        ranked.append({"candidate_id": c["id"], "score": round(score, 2), "reasons": reasons})
    ranked.sort(key=lambda r: -r["score"])
    return {"ranked": ranked[:limit], "blocked": blocked[:30],
            "considered": len(candidates),
            "note": "ranked, never rejected. A blocked row states the blocker — a missing "
                    "certification or a commute over the line — and a recruiter decides whether it "
                    "matters"}


def gap_statement(req, result):
    """What the database does NOT contain. More valuable than a padded list."""
    if result["ranked"]:
        return None
    creds = {c for s in req.get("skills", []) for c, spec in CREDENTIALS.items()
             if s in spec["required_for"]}
    wanted = req.get("must_have") or req.get("skills", [])
    return (f"We have nobody on file with {', '.join(wanted)}"
            + (f" and a current {', '.join(sorted(creds))}" if creds else "")
            + f" within {MAX_COMMUTE} minutes of {req.get('geo')}. "
              f"That is a sourcing job, not a search job.")


# ---------------------------------------------------------------- submissions

SUBMISSION_STATES = ("shortlisted", "screened", "submitted", "interviewing", "placed", "closed")


def time_to_submit(req, submissions):
    subs = [s for s in submissions if s["req_id"] == req["id"] and s.get("submitted_at")]
    if not subs:
        return None
    first = min(parse(s["submitted_at"]) for s in subs)
    opened = parse(req.get("opened_at"))
    return round((first - opened).total_seconds() / 3600, 2) if opened and first else None


def submit_speed(reqs=None, submissions=None, floor=10):
    reqs = reqs if reqs is not None else store.load("reqs")
    submissions = submissions if submissions is not None else store.load("submissions")
    vals = [t for t in (time_to_submit(r, submissions) for r in reqs) if t is not None]
    if len(vals) < floor:
        return unmeasured(f"only {len(vals)} reqs with a recorded submission; need {floor}",
                          field="median_hours", n=len(vals))
    return {"median_hours": round(median(vals), 2), "n": len(vals)}


# ---------------------------------------------------------------- redeploy

def redeploy_due(ref=None):
    ref = ref or now()
    out = []
    cands = store.index("candidates")
    for a in store.load("assignments"):
        if a.get("state") != "active" or a.get("redeploy_opened"):
            continue
        d = days_until(a.get("ends_at"), ref)
        if d is None or d > REDEPLOY_TRIGGER_DAYS or d < 0:
            continue
        c = cands.get(a["candidate_id"], {})
        out.append({"assignment": a["id"], "candidate_id": a["candidate_id"],
                    "days_to_end": d, "client": a.get("client"),
                    "skills": c.get("skills"), "gm_per_week": a.get("gm_per_week"),
                    "why": f"ends in {d} days — the cheapest revenue in the building is the person "
                           f"already sourced, screened and proven"})
    out.sort(key=lambda r: r["days_to_end"])
    return out


def redeploy_rate(days=180, floor=10):
    """Counted: of assignments that ENDED in the window, how many were followed
    by a new assignment for the same person inside 30 days."""
    ref = now()
    ended = [a for a in store.load("assignments")
             if a.get("ends_at") and (parse(a["ends_at"]) or ref) < ref
             and (parse(a["ends_at"]) or ref) >= ref - timedelta(days=days)]
    if len(ended) < floor:
        return unmeasured(f"only {len(ended)} assignments ended in {days} days; need {floor}",
                          field="rate", n=len(ended))
    by_cand = {}
    for a in store.load("assignments"):
        by_cand.setdefault(a["candidate_id"], []).append(a)
    redeployed = 0
    for a in ended:
        end = parse(a["ends_at"])
        nxt = [x for x in by_cand.get(a["candidate_id"], [])
               if x["id"] != a["id"] and parse(x.get("starts_at") or "") and
               end <= parse(x["starts_at"]) <= end + timedelta(days=30)]
        redeployed += bool(nxt)
    return {"rate": round(redeployed / len(ended), 3), "redeployed": redeployed,
            "of": len(ended), "window_days": days}


# ---------------------------------------------------------------- the Present module
#
# Branded submittal rendering: take the candidate's SOURCE résumé and re-render
# it into the agency's own template, presentation-grade, in seconds. The market
# insight (what the HireAra category proved): agencies win on how a candidate is
# PRESENTED, and the reformat is the single most repeated document task on a
# staffing desk.
#
# The honesty contract that separates this from the "AI resume enhancer" junk:
# a render is a REFORMAT, never an enhancement. Three guarantees, each
# structural:
#   1. NOTHING IS INVENTED. The renderer reads only RENDER_FIELDS from the
#      recorded source — there is no code path that adds a skill, an employer or
#      a date the source does not carry, and `provenance_check` re-derives that
#      from the output. A date the source doesn't have renders as "not
#      recorded", never as a plausible guess.
#   2. CONTACT ROUTES ARE STRIPPED BY CONSTRUCTION. Candidate contact fields are
#      not on the render whitelist, and a second regex pass redacts anything
#      email- or phone-shaped that was pasted into free text — a submittal that
#      leaks the candidate's number is how a client goes direct.
#   3. WORDING IS A HUMAN'S. Polish suggestions are drafted and queued R1 —
#      rewording somebody's professional history is a claim about them, and a
#      recruiter approves every line. The render ships the source's own words
#      until then.

RENDER_FIELDS = ("summary", "employment", "skills", "certifications", "education")
CONTACT_FIELDS = ("email", "phone", "address", "linkedin", "personal_site")

_CONTACT_RE = re.compile(
    r"[\w.+-]+@[\w-]+\.[\w.]+"                                   # email
    r"|\(?\b\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"                  # phone
    r"|\blinkedin\.com/\S+", re.I)


def _scrub_text(text):
    """Redact contact-shaped strings from free text. Layer two of the scrub —
    layer one is the field whitelist."""
    return _CONTACT_RE.sub("[withheld by the agency]", text or "")


def render_submittal(candidate, source=None, agency=None, ref=None):
    """Re-render the recorded source résumé into the agency's brand. Returns the
    rendered document plus what was withheld — the scrub is reported, never
    silent."""
    ref = ref or now()
    source = source if source is not None else candidate.get("resume_source")
    if not source:
        return {"refused": "no source résumé on file — a render with nothing behind it would be "
                           "an invention, and inventing a person's history is the one thing this "
                           "module exists to never do"}
    brand = agency or store.load("config").get("brand") or {}
    scrubbed = sorted(k for k in CONTACT_FIELDS if source.get(k))

    def line(x):
        return esc_html(_scrub_text(x))

    jobs = []
    for j in source.get("employment", []):
        start = j.get("start") or "not recorded"
        end = j.get("end") or "not recorded"
        jobs.append({"employer": j.get("employer"), "title": j.get("title"),
                     "start": start, "end": end,
                     "html": f"<div class='job'><b>{line(j.get('title'))}</b> — "
                             f"{line(j.get('employer'))} <span class='dates'>{line(start)} → "
                             f"{line(end)}</span></div>"})
    skills = [s for s in source.get("skills", [])]
    certs = [c for c in source.get("certifications", [])]
    edu = [e for e in source.get("education", [])]
    html = (
        f"<div class='submittal' style='border-top:6px solid {brand.get('color', '#333')}'>"
        f"<div class='brandbar'><b>{line(brand.get('name', 'the agency'))}</b> · candidate submittal</div>"
        f"<h2>{line(candidate.get('display_name'))}</h2>"
        + (f"<p class='sum'>{line(source.get('summary'))}</p>" if source.get("summary") else "")
        + "<h3>Experience</h3>" + "".join(j["html"] for j in jobs)
        + ("<h3>Skills</h3><p>" + ", ".join(line(s) for s in skills) + "</p>" if skills else "")
        + ("<h3>Certifications</h3><p>" + ", ".join(line(c) for c in certs) + "</p>" if certs else "")
        + ("<h3>Education</h3><p>" + ", ".join(line(e) for e in edu) + "</p>" if edu else "")
        + f"<div class='foot'>{line(brand.get('footer', 'Candidate contact is available through the agency.'))}</div>"
        + "</div>")
    return {"html": html, "brand": brand.get("name"),
            "employment": jobs, "skills": skills, "certifications": certs, "education": edu,
            "scrubbed_fields": scrubbed,
            "note": "a reformat of the recorded source, not an enhancement. Contact routes are "
                    "withheld by construction; wording changes wait for a recruiter"}


def esc_html(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if s is not None else "")


def provenance_check(rendered, source):
    """Every claim in the rendered document must exist in the source. Re-derived
    from the OUTPUT, so a renderer bug that invents a line is caught here rather
    than shipped."""
    unsourced = []
    src_emp = {(j.get("employer"), j.get("title")) for j in source.get("employment", [])}
    for j in rendered.get("employment", []):
        if (j.get("employer"), j.get("title")) not in src_emp:
            unsourced.append({"section": "employment",
                              "claim": f"{j.get('title')} at {j.get('employer')}"})
    for section in ("skills", "certifications", "education"):
        have = set(source.get(section, []))
        for item in rendered.get(section, []):
            if item not in have:
                unsourced.append({"section": section, "claim": item})
    leaks = _CONTACT_RE.findall(rendered.get("html", ""))
    return {"clean": not unsourced and not leaks, "unsourced": unsourced,
            "contact_leaks": len(leaks),
            "note": "any unsourced claim is a fabrication with the agency's name on it"}


WEAK_PHRASES = {"responsible for": "led", "helped with": "contributed to",
                "worked on": "operated", "did": "performed"}


def polish_suggestions(source):
    """Wording suggestions, drafted only. Each keeps the original beside it —
    nothing is applied until a recruiter approves the line."""
    out = []
    for j in source.get("employment", []):
        for weak, better in WEAK_PHRASES.items():
            if weak in (j.get("title") or "").lower():
                out.append({"section": "employment", "original": j.get("title"),
                            "suggested": (j.get("title") or "").lower().replace(weak, better),
                            "note": "wording only — the facts are untouched"})
    summary = (source.get("summary") or "").lower()
    for weak, better in WEAK_PHRASES.items():
        if weak in summary:
            out.append({"section": "summary", "original": source.get("summary"),
                        "suggested": summary.replace(weak, better),
                        "note": "wording only — the facts are untouched"})
    return out


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "shortlist":         dict(rung="R1", reason="a ranked list with reasons, handed to a recruiter. It stays R1 because a shortlist shapes who gets considered, and that is a human's call", never_promote=True),
    "reject_candidate":  dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. It ranks with reasons and names blockers; it does not reject anyone and does not make a hiring decision", never_promote=True),
    "screen_logistics":  dict(rung="R2", reason="capturing availability, rate expectation and interest is data collection, not evaluation"),
    "screen_evaluative": dict(rung="R1", reason="anything that judges a person against a bar is a recruiter's judgement", never_promote=True),
    "schedule_interview": dict(rung="R2", reason="finding a slot on two calendars commits nobody to anything"),
    "reminder":          dict(rung="R2", reason="a templated reminder against a booked interview"),
    "assemble_packet":   dict(rung="R2", reason="formatting a résumé and screening notes into the client's template"),
    "submit_to_client":  dict(rung="R1", reason="putting a person in front of a client is the agency's reputation", never_promote=True),
    "open_redeploy":     dict(rung="R2", reason="opening a redeploy record 21 days before an assignment ends"),
    "redeploy_outreach": dict(rung="R1", reason="the conversation with someone about their next assignment is a recruiter's"),
    "credential_warn":   dict(rung="R2", reason="warning that a certification expires soon is always the safe direction"),
    "notify_client_credential": dict(rung="R1", reason="telling a client about a compliance gap is the agency's word"),
    "render_submittal":  dict(rung="R2", reason="re-rendering the recorded source résumé into the agency's template adds no claim and removes the contact routes — a reformat of facts already on file"),
    "polish_wording":    dict(rung="R1", reason="rewording a person's professional history is a claim about them — a recruiter approves every suggested line, with the original beside it", never_promote=True),
    "add_unsourced_claim": dict(rung="R0", reason="THE SYSTEM NEVER INVENTS A LINE. A skill, employer or date that is not in the recorded source cannot be added to a submittal by software — that is fabrication with the agency's name on it", never_promote=True),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"shortlist", "screen_logistics", "screen_evaluative", "schedule_interview",
                "reminder", "assemble_packet", "submit_to_client", "submitted",
                "open_redeploy", "redeploy_outreach", "credential_warn",
                "notify_client_credential", "render_submittal", "polish_wording"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("candidate:",))


# ---------------------------------------------------------------- evals
#
# Two. One scores shortlist quality. The other is the one that matters: it proves
# no excluded factor can influence a ranking, and its expected value is ZERO.

SHORTLIST_EVAL = Eval(
    "shortlist quality", "should_shortlist",
    "a candidate who genuinely fits and never surfaces is a placement lost silently — recall is "
    "reported alone")


def eval_shortlist():
    req = {"id": "r_eval", "skills": ["forklift"], "geo": "north", "client_id": "cl_1",
           "client_requirements": []}
    base = dict(skills=["forklift"], verified_experience_months=30,
                commute_minutes={"north": 15}, availability="available",
                prior_client_ids=["cl_1"], performance_notes=[{"rating": 5}],
                short_notice_history=3)
    cases, pool = [], []
    for i, (mut, label) in enumerate([
            ({}, "should_shortlist"),
            (dict(verified_experience_months=None), "should_shortlist"),
            (dict(performance_notes=[]), "should_shortlist"),
            (dict(skills=["welding_mig"]), "should_not"),
            (dict(commute_minutes={"north": 90}), "should_not"),
            (dict(skills=[]), "should_not")]):
        cid = f"ev_{i}"
        pool.append({"id": cid, **base, **mut})
        cases.append({"input": cid, "label": label})
    creds = [{"candidate_id": c["id"], "type": "forklift_cert", "issued_at": iso(now())}
             for c in pool]
    res = rank_candidates(req, pool, credentials=creds)
    shortlisted = {r["candidate_id"] for r in res["ranked"]}
    return SHORTLIST_EVAL.run(
        cases, lambda cid: "should_shortlist" if cid in shortlisted else "should_not")


def eval_excluded_factors():
    """The one that must be zero. Poison a record with every excluded factor and
    assert the score does not move."""
    req = {"id": "r_x", "skills": ["forklift"], "geo": "north", "client_id": "cl_1",
           "client_requirements": []}
    clean = {"id": "x1", "skills": ["forklift"], "verified_experience_months": 24,
             "commute_minutes": {"north": 20}, "availability": "available",
             "performance_notes": [{"rating": 4}], "short_notice_history": 2}
    poison = {**clean, "id": "x2"}
    for k in EXCLUDED_FACTORS:
        poison[k] = "POISON"
    creds = [{"candidate_id": "x1", "type": "forklift_cert", "issued_at": iso(now())},
             {"candidate_id": "x2", "type": "forklift_cert", "issued_at": iso(now())}]
    a = rank_candidates(req, [clean], credentials=creds)["ranked"]
    b = rank_candidates(req, [poison], credentials=creds)["ranked"]
    same = bool(a) and bool(b) and abs(a[0]["score"] - b[0]["score"]) < 1e-9
    return {"name": "excluded-factor influence", "excluded_tested": len(EXCLUDED_FACTORS),
            "scores": {"clean": a[0]["score"] if a else None, "poisoned": b[0]["score"] if b else None},
            "influence_detected": not same,
            "must_be": False,
            "note": "every excluded factor is written into a candidate record and the score is "
                    "recomputed. Any difference at all is a failure — this is the number that has "
                    "to be zero, and it is the audit trail a plaintiff's lawyer would ask for"}


def eval_render_honesty():
    """The Present module's audit: poison a source résumé with contact routes in
    every field AND pasted into free text, render it, and assert nothing leaks
    and nothing is invented. Expected leak count: zero, always."""
    source = {
        "summary": "Forklift operator. Reach me at test@example.com or (555) 014-2299.",
        "email": "test@example.com", "phone": "555-014-2299",
        "address": "12 Elm St", "linkedin": "linkedin.com/in/testperson",
        "employment": [{"employer": "Everline Packaging", "title": "Forklift Operator",
                        "start": "2023-01", "end": None}],
        "skills": ["forklift"], "certifications": [], "education": [],
    }
    cand = {"id": "rx", "display_name": "A Person", "resume_source": source}
    r = render_submittal(cand, source, agency={"name": "Ironline Staffing", "color": "#1a3c5e"})
    p = provenance_check(r, source)
    missing_dates_honest = any(j["end"] == "not recorded" for j in r["employment"])
    return {"name": "render honesty",
            "contact_leaks": p["contact_leaks"],
            "scrubbed_fields": r["scrubbed_fields"],
            "unsourced_claims": len(p["unsourced"]),
            "missing_date_rendered_as": "not recorded" if missing_dates_honest else "INVENTED",
            "clean": p["clean"] and missing_dates_honest,
            "note": "contact routes in five fields plus two pasted into free text; every one must "
                    "be withheld. A date the source doesn't carry must render as 'not recorded' — "
                    "a plausible guess here is a fabrication"}


# ---------------------------------------------------------------- the desk board

def desk_board(ref=None):
    ref = ref or now()
    reqs = [r for r in store.load("reqs") if r.get("state") == "open"]
    creds = []
    cands = store.index("candidates")
    for c in store.load("credentials"):
        st = credential_state(c, ref)
        if st.get("state") in ("expiring", "expired"):
            creds.append({"candidate_id": c["candidate_id"], "type": c["type"], **st})
    creds.sort(key=lambda x: x.get("days_left", 0))
    return {
        "generated": iso(ref),
        "open_reqs": len(reqs),
        "submit_speed": submit_speed(),
        "redeploy_due": len(redeploy_due(ref)),
        "redeploy_rate": redeploy_rate(),
        "credentials_expiring": creds[:40],
        "credential_count": len(creds),
        "automation": automation(),
    }


# ---------------------------------------------------------------- ROI

ROI = (Roi("What the database is worth here")
       .line("Redeploy value", "revenue",
             "assignments ending/mo × redeploy points gained × GM per placement × avg duration wks",
             ["assignments_ending_month", "redeploy_points_gained", "gm_per_week", "avg_duration_weeks"],
             lambda g: g["assignments_ending_month"] * 12 * g["redeploy_points_gained"]
             * g["gm_per_week"] * g["avg_duration_weeks"],
             note="assignments ending is counted from your own board. This is the honest headline: "
                  "the candidate is already sourced, already screened and already proven, so the "
                  "margin is the cleanest in the business",
             assumption="points gained is the lift over the redeployment rate you run today, which "
                        "this system measures")
       .line("Sourcing avoided", "revenue",
             "reqs/yr × database-fill% × external sourcing cost avoided",
             ["reqs_yr", "database_fill_rate", "sourcing_cost_per_req"],
             lambda g: g["reqs_yr"] * g["database_fill_rate"] * g["sourcing_cost_per_req"],
             note="every re-source is money you already spent, spent again")
       .line("Compliance", "revenue",
             "lapses avoided/yr × cost per lapse",
             ["lapses_per_year", "cost_per_lapse"],
             lambda g: g["lapses_per_year"] * g["cost_per_lapse"],
             assumption="cost per lapse is the billing gap plus the client remediation, yours to set")
       .line("Speed to submit", "scenario",
             "your own submission history, once it has 90 days of outcomes",
             ["speed_win_evidence"],
             lambda g: g["speed_win_evidence"],
             note="A SCENARIO WITH NO NUMBER YET. Whether being first actually wins you more is "
                  "answerable from YOUR submission history and nobody else's — we will not put an "
                  "industry statistic here"))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    ending = [a for a in store.load("assignments")
              if a.get("state") == "active" and (days_until(a.get("ends_at")) or 999) <= 30]
    if ending:
        recorded["assignments_ending_month"] = len(ending)
        gms = [a["gm_per_week"] for a in ending if a.get("gm_per_week")]
        if gms:
            recorded["gm_per_week"] = round(median(gms), 2)
    reqs = store.load("reqs")
    if reqs:
        recorded["reqs_yr"] = len(reqs)
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    merged.pop("speed_win_evidence", None)
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
