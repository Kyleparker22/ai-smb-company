#!/usr/bin/env python3
"""PM Growth OS — the owner-prospect pipeline (v1 of GROWTH_MODULE_SPEC.md).

The Sales-pillar sibling of Property OS. It shares the substrate — storage,
the autonomy matrix, the approvals/messages queues, the sentinel, the honest-
numbers rules — and nothing else. The module turns recorded demand (referrals,
inquiries' evidence, the pitch page) into a worked pipeline where **a human
makes every touch** and the software supplies the two things humans reliably
drop: the cadence and the evidence.

THE LINE THIS MODULE NEVER CROSSES
----------------------------------
There is NO SEND RAIL. Not a rung, not a flag — the capability does not exist.
Every message this module produces is a DRAFT a human sends from their own
mailbox and then records. Building a send rail is a counsel-gated v2 decision
(TCPA / CAN-SPAM / DNC), and the test suite pins the absence so it cannot
arrive as a refactor.

HONEST-NUMBERS RULES (carried over, plus two of its own)
--------------------------------------------------------
- A conversion rate refuses below 10 recorded outcomes — "2 of 3 won" is an
  anecdote and is labelled one.
- No weighted forecasts exist. A stage is a fact; a forecast is a model, and
  v1 ships no model.
- Every figure a draft cites must be computable from the pitch one-pager at
  draft time. An unmeasured metric is silently omitted from the draft — the
  scribe never writes around a `_missing`.

THE STAGE MACHINE
-----------------
  recorded -> researched -> first_touch_drafted -> contacted -> meeting
           -> proposal -> won | lost

Agents may advance only the first two edges (scout: recorded->researched,
scribe: researched->first_touch_drafted). Everything from `contacted` on moves
on a human's say-so, because those stages are claims about what a human did.
`lost` is reachable from any non-terminal stage; `won` only from `proposal`.
"""
import re as _re
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import growth
from core import (by_id, iso, load, log_event, nid, now, parse, save,
                  store_lock, upsert)

STAGES = ("recorded", "researched", "first_touch_drafted", "contacted",
          "meeting", "proposal", "won", "lost")
TERMINAL = {"won", "lost"}
HUMAN_ONLY_FROM = "contacted"      # this stage onward, only a human advances

# Days before a prospect in this stage is OVERDUE for a touch. The cadence is
# the module's entire claim to value: nothing sits.
CADENCE_DAYS = {"recorded": 2, "researched": 2, "first_touch_drafted": 3,
                "contacted": 4, "meeting": 5, "proposal": 7}

MIN_OUTCOMES_FOR_RATE = 10

# Cold-outreach discipline. After this many SENT touches with no reply, the
# cadence STOPS and the prospect rests (R2, reversible by a human). Silence is
# an answer; persistence past it is how outreach becomes spam.
MAX_TOUCHES = 3


# ------------------------------------------------------------------ evidence

def evidence_lines():
    """The claims a draft is allowed to make, computed fresh from the pitch
    one-pager. A metric that reads `_missing` is OMITTED — the scribe never
    writes a sentence around a number the system refused to state."""
    p = growth.performance_onepager()
    lines = []
    pf = p["portfolio"]
    if pf.get("occupancy") is not None:
        lines.append(f"{pf['units']} units at {pf['occupancy']:.0%} occupancy")
    ar = p["avg_resolution"]
    if not ar.get("_missing"):
        lines.append(f"median repair resolution {ar['median']:.0f} hours across "
                     f"{ar['n']} jobs in the last 90 days")
    sla = p["sla_hit_rate"]
    if not sla.get("_missing"):
        lines.append(f"{sla['rate']:.0%} of repairs closed inside their deadline")
    mv = p["measured_vacancy"]
    if not mv.get("_missing"):
        lines.append(f"measured turnover vacancy of {mv['days']} days "
                     f"(median of {mv['n']} completed turnovers)")
    d = p["deflection"]
    if d.get("deflected"):
        lines.append(f"{d['deflected']} vendor visits avoided by guided resident "
                     f"fixes in 90 days (${d['avoided_cost']:,} in invoices that "
                     "never happened)")
    if p["trust"]["balanced"]:
        lines.append("client trust account reconciled to the cent")
    return lines


def _numbers_in(text):
    # Links and opaque tokens are not CLAIMS — the pitch URL's hex token is
    # full of digits, and counting those as cited statistics refused every
    # draft that included the link (found on the first live sweep). Strip
    # URL-ish and token-ish spans first; what remains is prose numbers.
    t = _re.sub(r"\S*/pitch\?t=\S+", " ", text or "")
    t = _re.sub(r"\b[a-z]+_[0-9a-f]{8,}\b", " ", t)
    return set(_re.findall(r"\d[\d,.]*", t))


def numbers_ok(draft, allowed_lines):
    """Every number in a draft must appear in the evidence it was built from.
    This is the check that keeps a model-refined draft from inventing a stat."""
    allowed = set()
    for l in allowed_lines:
        allowed |= _numbers_in(l)
    return _numbers_in(draft) <= allowed


# ------------------------------------------------------------------ prospects

def _find(rows, pid):
    return next((x for x in rows if x["id"] == pid), None)


def add_prospect(body, source, actor="human:mgr_1"):
    """Manual add, the scout's referral import, or one sourced target.

    A SOURCED prospect must carry provenance — where the name came from. We do
    not contact people we cannot say how we found; that is both the compliance
    posture and the first line of the eventual cold email. Opt-outs are
    checked here so no path around the do-not-contact ledger exists."""
    name = (body.get("name") or "").strip()
    contact = (body.get("contact") or "").strip()
    if not name or not contact:
        return None, "a name and a way to reach them are both required"
    if source.get("kind") == "sourced" and not (source.get("provenance") or "").strip():
        return None, ("a sourced prospect requires provenance — we don't "
                      "contact people we can't say how we found")
    if _is_dnc(contact):
        return None, "this contact opted out — the do-not-contact ledger is permanent"
    row = {"id": nid("pros"), "at": iso(), "name": name[:80],
           "contact": contact[:120], "note": (body.get("note") or "")[:500],
           "doors": body.get("doors"),
           "source": source, "stage": "recorded",
           "stage_at": iso(), "history": [{"stage": "recorded", "at": iso()}],
           "brief": None, "drafts": [], "nagged_on": None}
    with store_lock():
        rows = load("prospects")
        rows.append(row)
        save("prospects", rows)
    log_event("prospect_recorded", row["id"], actor, None,
              {"name": row["name"], "source": source.get("kind")})
    return row, None


def _is_dnc(contact, prospects=None):
    c = (contact or "").strip().lower()
    return any(p.get("dnc") and p["contact"].strip().lower() == c
               for p in (prospects if prospects is not None else load("prospects")))


def import_targets(body, actor="human:mgr_1"):
    """Bulk intake of a sourced list (a county-records pull, a prospecting
    export, a meetup sheet). R2: recorded with provenance, deduped, and three
    kinds of row are SKIPPED and reported rather than silently added —
    duplicates, opt-outs, and previously-lost prospects (re-approaching a lost
    prospect is a deliberate human decision, never a list-import side effect)."""
    import agents
    provenance = (body.get("provenance") or "").strip()
    targets = body.get("targets") or []
    if not provenance:
        return None, ("provenance is required for every imported list — where "
                      "did these names come from?")
    if not targets:
        return None, "no targets in the import"
    report = {"added": 0, "duplicate": 0, "previously_lost": 0,
              "do_not_contact": 0, "invalid": 0, "provenance": provenance}
    with store_lock():
        rows = load("prospects")
        by_contact = {p["contact"].strip().lower(): p for p in rows}
        for t in targets[:500]:
            name = (t.get("name") or "").strip()
            contact = (t.get("contact") or "").strip()
            if not name or not contact:
                report["invalid"] += 1
                continue
            existing = by_contact.get(contact.lower())
            if existing:
                if existing.get("dnc"):
                    report["do_not_contact"] += 1
                elif existing["stage"] == "lost":
                    report["previously_lost"] += 1
                else:
                    report["duplicate"] += 1
                continue
            row = {"id": nid("pros"), "at": iso(), "name": name[:80],
                   "contact": contact[:120], "note": (t.get("note") or "")[:500],
                   "doors": t.get("doors"),
                   "source": {"kind": "sourced", "provenance": provenance,
                              "by": actor},
                   "stage": "recorded", "stage_at": iso(),
                   "history": [{"stage": "recorded", "at": iso()}],
                   "brief": None, "drafts": [], "nagged_on": None}
            rows.append(row)
            by_contact[contact.lower()] = row
            report["added"] += 1
        save("prospects", rows)
    agents.act("scout", "import_target_list", provenance[:60],
               {"_kind": "targets_imported", **report})
    return report, None


def record_do_not_contact(pid, actor="human:mgr_1"):
    """Permanent. Every import and every draft checks it; nothing overrides it.
    R3 because honoring an opt-out is always the safe direction."""
    import agents
    with store_lock():
        rows = load("prospects")
        p = _find(rows, pid)
        if not p:
            return None, "not found"
        p["dnc"] = iso()
        p["dormant"] = p.get("dormant") or iso()
        save("prospects", rows)
    agents.act("scout", "record_do_not_contact", pid,
               {"_kind": "opt_out_recorded", "contact": p["contact"]})
    return p, None


def wake_prospect(pid, actor="human:mgr_1"):
    """A human deliberately puts a rested prospect back on cadence. Refused
    for an opt-out — dnc is permanent and this is not a way around it."""
    with store_lock():
        rows = load("prospects")
        p = _find(rows, pid)
        if not p:
            return None, "not found"
        if p.get("dnc"):
            return None, "they opted out — do-not-contact is permanent"
        p["dormant"] = None
        p["stage_at"] = iso()      # restart the clock; don't instantly re-nag
        save("prospects", rows)
    log_event("prospect_woken", pid, actor, None, {})
    return p, None


def touches_sent(pid, msgs=None):
    """SENT outreach touches for a prospect — drafts don't count; only what a
    human actually sent and recorded."""
    return sum(1 for m in (msgs if msgs is not None else load("messages"))
               if m.get("module") == "pipeline" and m.get("prospect_id") == pid
               and m.get("kind") in ("first_touch", "follow_up")
               and m.get("status") == "sent")


def _advance(rows, p, to, actor):
    p["stage"] = to
    p["stage_at"] = iso()
    p["history"].append({"stage": to, "at": iso(), "by": actor})
    save("prospects", rows)


def advance_prospect(pid, to, actor="human:mgr_1", reason=None):
    """Forward one stage at a time; `lost` from anywhere non-terminal; `won`
    only from `proposal`. A human may drive any legal edge; an agent may only
    drive the two drafting edges — enforced here, not by convention."""
    if to not in STAGES:
        return None, f"stage must be one of {STAGES}"
    with store_lock():
        rows = load("prospects")
        p = _find(rows, pid)
        if not p:
            return None, "not found"
        cur = p["stage"]
        if cur in TERMINAL:
            return None, f"{cur} is terminal"
        if to == "lost":
            pass                                   # reachable from anywhere live
        elif to == "won":
            if cur != "proposal":
                return None, "won is only reachable from proposal — a win that "\
                             "skipped the proposal stage is a record-keeping lie"
        elif STAGES.index(to) != STAGES.index(cur) + 1:
            return None, f"one stage at a time: next is '{STAGES[STAGES.index(cur) + 1]}'"
        if actor.startswith("agent:") and to not in ("researched",
                                                    "first_touch_drafted"):
            return None, "an agent may only advance the two drafting edges — "\
                         "contacted and beyond (and lost) are claims about what "\
                         "a human did, so a human records them"
        if to == "lost" and reason:
            p["lost_reason"] = str(reason)[:200]
        if actor.startswith("human:"):
            p["dormant"] = None      # a human moving the stage IS the revival
        _advance(rows, p, to, actor)
    kind = "prospect_" + ("won" if to == "won" else "lost" if to == "lost" else "advanced")
    log_event(kind, pid, actor,
              "R2" if actor.startswith("agent:") else None, {"to": to})
    return p, None


def scaffold_won_client(pid, actor="human:mgr_1"):
    """The won -> onboarding handoff: create the ops-module owner + property
    shell so the sale flows into Property OS without re-keying. Every default
    is FLAGGED for onboarding — a scaffold is not a configuration."""
    with store_lock():
        pros = load("prospects")
        p = _find(pros, pid)
        if not p:
            return None, "not found"
        if p["stage"] != "won":
            return None, "only a won prospect is scaffolded — the signature comes first"
        if p.get("scaffolded_owner_id"):
            return {"owner_id": p["scaffolded_owner_id"], "already": True}, None
        oid = nid("own")
        prop_id = nid("prop")
        owners = load("owners")
        owners.append({
            "id": oid, "name": p["name"],
            "email": p["contact"] if "@" in p["contact"] else "",
            "phone": p["contact"] if "@" not in p["contact"] else "",
            "properties": [prop_id],
            "spend_approval_limit": 400, "emergency_spend_limit": 2500,
            "mgmt_fee_pct": 0.08, "reserve_floor": 300,
            "onboarding": True,
            "onboarding_note": "SCAFFOLD DEFAULTS — spend limits, emergency "
                               "authority, fee %, and reserve floor are the "
                               "system defaults, not this owner's terms. Set "
                               "each with the owner before go-live.",
        })
        save("owners", owners)
        props = load("properties")
        props.append({"id": prop_id, "name": f"{p['name']} portfolio",
                      "address": None, "city": None, "state": None,
                      "year_built": None, "owner_id": oid,
                      "onboarding": True})
        save("properties", props)
        p["scaffolded_owner_id"] = oid
        save("prospects", pros)
    import agents
    agents.act("scout", "scaffold_won_client", pid,
               {"_kind": "client_scaffolded", "owner_id": oid,
                "requested_by": actor})
    return {"owner_id": oid, "property_id": prop_id}, None


# ------------------------------------------------------------------ metrics

def conversion(prospects=None):
    """Won / (won + lost). Refuses below MIN_OUTCOMES_FOR_RATE recorded
    outcomes — a rate on three data points is an anecdote wearing a suit."""
    rows = prospects if prospects is not None else load("prospects")
    outcomes = [p for p in rows if p["stage"] in TERMINAL]
    won = [p for p in outcomes if p["stage"] == "won"]
    if len(outcomes) < MIN_OUTCOMES_FOR_RATE:
        return {"rate": None, "won": len(won), "lost": len(outcomes) - len(won),
                "_missing": f"only {len(outcomes)} recorded outcomes — need "
                            f"{MIN_OUTCOMES_FOR_RATE} to state a rate; until then "
                            "the counts are the whole story"}
    return {"rate": round(len(won) / len(outcomes), 3),
            "won": len(won), "lost": len(outcomes) - len(won), "n": len(outcomes)}


def source_read(prospects=None):
    """Which sources produce pipeline. Counts are facts and always shown;
    per-source rates obey the same outcome floor."""
    rows = prospects if prospects is not None else load("prospects")
    out = {}
    for p in rows:
        k = p["source"].get("kind", "unknown")
        s = out.setdefault(k, {"recorded": 0, "won": 0, "lost": 0})
        s["recorded"] += 1
        if p["stage"] in TERMINAL:
            s[p["stage"]] += 1
    return out


def overdue(p, at=None):
    days = CADENCE_DAYS.get(p["stage"])
    if days is None:
        return None
    since = parse(p["stage_at"]) or now()
    late = ((at or now()) - since).days - days
    return late if late > 0 else None


def pipeline_read():
    rows = load("prospects")
    msgs = load("messages")
    unsent = [m for m in msgs if m.get("module") == "pipeline"
              and m.get("status") == "draft"]
    board = {s: [] for s in STAGES}
    nags = []
    msgs_all = load("messages")
    for p in sorted(rows, key=lambda x: x["at"]):
        late = overdue(p)
        entry = {**p, "age_days": (now() - (parse(p["at"]) or now())).days,
                 "stage_age_days": (now() - (parse(p["stage_at"]) or now())).days,
                 "overdue_days": late,
                 "touches_sent": touches_sent(p["id"], msgs_all),
                 "drafts_waiting": sum(1 for m in unsent
                                       if m.get("prospect_id") == p["id"])}
        board[p["stage"]].append(entry)
        if late and not p.get("dormant") and not p.get("dnc"):
            nags.append({"prospect_id": p["id"], "name": p["name"],
                         "stage": p["stage"], "overdue_days": late})
    live = [p for p in rows if p["stage"] not in TERMINAL]
    resting = [p for p in live if p.get("dormant") and not p.get("dnc")]
    return {"stages": board, "nags": nags,
            "drafts_waiting": len(unsent),
            "metrics": {"open": len(live), "resting": len(resting),
                        "dnc": sum(1 for p in rows if p.get("dnc")),
                        "total": len(rows),
                        "conversion": conversion(rows),
                        "sources": source_read(rows)},
            "note": "No send rail exists in this module. Drafts wait for a "
                    "human to send from their own mailbox and record it; the "
                    "cadence nags the human, never the prospect."}


# ------------------------------------------------------------------ scout

def _brief(p):
    """Everything the operator's own records know that helps the first call.
    Recorded facts only — the scout does not speculate about a stranger."""
    lines = []
    src = p["source"]
    if src.get("kind") == "referral":
        ref = by_id("referrals", src.get("referral_id")) or {}
        by = src.get("by", "")
        if by.startswith("owner:"):
            o = by_id("owners", by.split(":", 1)[1]) or {}
            if o:
                units = [u for u in load("units") if u.get("property_id")
                         in (o.get("properties") or [])]
                lines.append(f"Referred by {o.get('name')} — a current client "
                             f"with {len(units)} units under management. "
                             "Name-drop with their permission, not before.")
        else:
            lines.append("Referred by staff — check the referral note for how "
                         "you know them.")
        if ref.get("note"):
            lines.append(f"Referrer's note: {ref['note']}")
    if p.get("note"):
        lines.append(f"Recorded note: {p['note']}")
    ev = evidence_lines()
    if ev:
        lines.append("Evidence available for the conversation: " +
                     "; ".join(ev[:3]) + ".")
    lines.append("Not researched beyond our own records — anything else, "
                 "verify before repeating it.")
    return lines


def run_scout():
    """Imports referrals, writes briefs, advances recorded->researched, nags
    the human on cadence, and closes the loop back onto referral rows."""
    import agents
    out = {"imported": 0, "briefed": 0, "nags": 0, "referrals_closed": 0}

    # --- import referrals not yet mirrored into the pipeline (idempotent)
    with store_lock():
        pros = load("prospects")
        have = {p["source"].get("referral_id") for p in pros
                if p["source"].get("kind") == "referral"}
        for r in load("referrals"):
            if r["id"] in have or r.get("status") == "closed":
                continue
            row = {"id": nid("pros"), "at": iso(), "name": r["name"],
                   "contact": r["contact"], "note": r.get("note", ""),
                   "source": {"kind": "referral", "referral_id": r["id"],
                              "by": r.get("source")},
                   "stage": "recorded", "stage_at": iso(),
                   "history": [{"stage": "recorded", "at": iso()}],
                   "brief": None, "drafts": [], "nagged_on": None}
            pros.append(row)
            out["imported"] += 1
        save("prospects", pros)
    for p in load("prospects"):
        if p["source"].get("kind") == "referral" and not p.get("import_logged"):
            agents.act("scout", "import_referral", p["id"],
                       {"_kind": "prospect_recorded", "name": p["name"],
                        "referral": p["source"].get("referral_id")})
            p["import_logged"] = iso()
            upsert("prospects", p)

    # --- brief + advance recorded -> researched (the one edge scout owns)
    for p in load("prospects"):
        if p["stage"] != "recorded":
            continue
        p["brief"] = _brief(p)
        upsert("prospects", p)
        allowed, _ = agents.act("scout", "research_prospect", p["id"],
                                {"_kind": "prospect_briefed",
                                 "lines": len(p["brief"])})
        if allowed:
            with store_lock():
                rows = load("prospects")
                q = _find(rows, p["id"])
                if q and q["stage"] == "recorded":
                    _advance(rows, q, "researched", "agent:scout")
            out["briefed"] += 1

    # --- the cadence nag: R2, aimed at the HUMAN, at most once a day.
    # Rested and opted-out prospects are off the cadence by definition.
    today = iso()[:10]
    for p in load("prospects"):
        late = overdue(p)
        if not late or p.get("nagged_on") == today or p.get("dormant") or p.get("dnc"):
            continue
        agents.act("scout", "nag_human_on_cadence", p["id"],
                   {"_kind": "cadence_nag", "stage": p["stage"],
                    "overdue_days": late})
        p["nagged_on"] = today
        upsert("prospects", p)
        out["nags"] += 1

    # --- close the loop on the ops-side referral row (R2 bookkeeping)
    for p in load("prospects"):
        if p["source"].get("kind") != "referral" or p["stage"] not in TERMINAL:
            continue
        r = by_id("referrals", p["source"].get("referral_id"))
        want = "won" if p["stage"] == "won" else "closed"
        if r and r.get("status") not in ("won", "closed"):
            growth.set_referral_status(r["id"], want, actor="agent:scout")
            out["referrals_closed"] += 1
    return out


# ------------------------------------------------------------------ scribe

FIRST_TOUCH_TEMPLATE = """Hi {first},

{referrer_line}I run {org}, and I'd value 20 minutes to hear how your rentals
are going and show you how we run ours. A few things about our operation,
computed from our own records this morning, not marketing copy:

{evidence}

If it's useful, here's the live page those numbers come from: {pitch_link}
No pitch deck, no obligation — if the numbers aren't interesting, that's a
complete answer.

[YOUR SIGN-OFF]"""

COLD_FIRST_TOUCH_TEMPLATE = """Hi {first},

[HOW WE FOUND THEM — recorded provenance, review before sending: {provenance}]

I run {org}, a property-management operation, and I write to rental owners who
look like they might be carrying the day-to-day themselves. If that's you and
you ever weigh handing it off, I'd value 20 minutes. A few things about our
operation, computed from our own records this morning, not marketing copy:

{evidence}

The live page those numbers come from: {pitch_link}

If this isn't relevant, reply "no thanks" and I won't write again — we record
opt-outs permanently and honor them by construction.

[YOUR SIGN-OFF]
[YOUR FIRM'S PHYSICAL MAILING ADDRESS — required on commercial email]"""

FOLLOW_UP_TEMPLATE = """Hi {first},

Following up on my note — no rush, and one data point since I wrote:
{evidence_one}

Happy to talk whenever suits, or to close the file if the timing's wrong.

[YOUR SIGN-OFF]"""

THANK_YOU_TEMPLATE = """Hi {first},

Thank you for introducing {prospect} — that kind of trust is the only
marketing we ever want. I'll reach out personally and I'll keep you posted
on what comes of it.

[YOUR SIGN-OFF]"""

REFERRER_UPDATE_TEMPLATE = """Hi {first},

An update on {prospect}, who you introduced: {outcome_line}
Either way — thank you again for the introduction.

[YOUR SIGN-OFF]"""

PROPOSAL_TEMPLATE = """MANAGEMENT PROPOSAL DRAFT — {prospect}
(assembled by the scribe agent at R0: the principal reviews every line and
fills every bracket; software never sets a price)

1. Scope: full-service management of {prospect}'s portfolio
   ([UNITS] units — confirm count and addresses at signing).
2. Our operation, measured from our own records as of {date}:
{evidence}
3. Management fee: [PRINCIPAL SETS — % of collected rent]
4. Spend authority: routine per-job limit [OWNER SETS], emergency habitability
   authority [OWNER SETS] with same-moment notice.
5. Trust accounting: client funds in trust, reconciled continuously,
   statements monthly, disbursements on your schedule.
6. Term and exit: [PRINCIPAL SETS — recommend month-to-month after year one]

[STATE-SPECIFIC TERMS — counsel-reviewed template required before any real
prospect receives this]"""


def _first(name):
    return (name or "").split()[0] or "there"


def _pitch_link():
    tok = growth.share_token()
    return f"/pitch?t={tok}" if tok else "[PITCH LINK — generate in console]"


def _has_msg(msgs, kind, **match):
    return any(m.get("kind") == kind and
               all(m.get(k) == v for k, v in match.items()) for m in msgs)


def _draft(agent_action, kind, to_kind, to_id, subject, body, prospect_id,
           allowed_extra=None):
    """All scribe output funnels here: R1 logged, queued as a DRAFT, tagged
    with the module so the ops surfaces can tell whose message it is. The
    numbers check runs on every draft — a draft that cites a figure outside
    its evidence is refused and logged, not quietly stored. `allowed_extra`
    carries recorded facts a specific draft legitimately quotes (a referrer's
    note, an import's provenance) so their digits don't read as invented."""
    import agents
    ev = evidence_lines()
    if not numbers_ok(body, ev + [subject or ""] + ["20"] + (allowed_extra or [])):
        log_event("draft_refused", prospect_id, "agent:scribe", "R1",
                  {"kind": kind, "why": "cites a number outside the computed evidence"})
        return None
    agents.act("scribe", agent_action, prospect_id,
               {"_kind": "draft_written", "draft_kind": kind})
    return agents.queue_message("scribe", to_kind, to_id, subject, body,
                                status="draft", kind=kind,
                                prospect_id=prospect_id, module="pipeline")


def run_scribe():
    """Drafts: first touch, follow-ups, referrer thank-yous and updates, and
    the proposal shell. Everything lands as a draft or an R0 document; the
    stage the scribe may advance is researched -> first_touch_drafted only."""
    import agents
    out = {"first_touch": 0, "follow_ups": 0, "thank_yous": 0,
           "referrer_updates": 0, "proposals": 0, "rested": 0}
    msgs = load("messages")
    ev = evidence_lines()

    for p in load("prospects"):
        pid = p["id"]
        src = p["source"]

        # -- thank the referrer once, at import
        if src.get("kind") == "referral" and str(src.get("by", "")).startswith("owner:"):
            ref_owner = src["by"].split(":", 1)[1]
            o = by_id("owners", ref_owner) or {}
            if o and not _has_msg(msgs, "referrer_thank_you", prospect_id=pid):
                m = _draft("update_referrer", "referrer_thank_you", "owner",
                           ref_owner, "Thank you for the introduction",
                           THANK_YOU_TEMPLATE.format(first=_first(o.get("name")),
                                                     prospect=p["name"]), pid)
                if m:
                    msgs.append(m)
                    out["thank_yous"] += 1

        # An opt-out or a rested prospect gets NOTHING drafted — the dnc check
        # is absolute, and dormancy is the point of dormancy.
        if p.get("dnc") or p.get("dormant"):
            continue

        # -- first touch: drafted once, advances researched -> first_touch_drafted.
        #    Source-aware: a referral opens with the (permission-gated) name-drop;
        #    a sourced prospect gets the COLD template — provenance stated for
        #    review, an opt-out line, and the physical-address bracket the law
        #    expects on commercial email.
        if p["stage"] == "researched" and not _has_msg(msgs, "first_touch",
                                                       prospect_id=pid):
            org = (load("config") or {}).get("org", "our firm")
            evidence = "\n".join(f"  - {l}" for l in ev[:4]) or \
                       "  - [evidence unavailable — portfolio too new to cite]"
            allowed_extra = []
            if src.get("kind") == "sourced":
                prov = src.get("provenance", "")
                allowed_extra.append(prov)
                body = COLD_FIRST_TOUCH_TEMPLATE.format(
                    first=_first(p["name"]), provenance=prov, org=org,
                    evidence=evidence, pitch_link=_pitch_link())
            else:
                referrer_line = ""
                if src.get("kind") == "referral" and str(src.get("by", "")).startswith("owner:"):
                    o = by_id("owners", src["by"].split(":", 1)[1]) or {}
                    if o:
                        # The brief says "name-drop with their permission, not
                        # before" — so the draft carries the same condition
                        # rather than contradicting it.
                        referrer_line = (f"[CONFIRM {o.get('name')} is happy to be "
                                         f"named before sending] {o.get('name')} "
                                         "suggested I reach out — they mentioned "
                                         "you first, so you'd know why I'm writing. ")
                body = FIRST_TOUCH_TEMPLATE.format(
                    first=_first(p["name"]), referrer_line=referrer_line,
                    org=org, evidence=evidence, pitch_link=_pitch_link())
            m = _draft("draft_first_touch", "first_touch", "prospect_owner",
                       pid, f"An introduction — {p['name']}", body, pid,
                       allowed_extra=allowed_extra)
            if m:
                msgs.append(m)
                out["first_touch"] += 1
                with store_lock():
                    rows = load("prospects")
                    q = _find(rows, pid)
                    if q and q["stage"] == "researched":
                        _advance(rows, q, "first_touch_drafted", "agent:scribe")

        # -- follow-up: only when overdue, only if nothing is already waiting —
        #    and only under the touch cap. At the cap the prospect RESTS (R2)
        #    instead of receiving touch four: silence is an answer.
        if p["stage"] in ("contacted", "meeting", "proposal") and overdue(p):
            sent_touches = touches_sent(pid, msgs)
            if sent_touches >= MAX_TOUCHES and p["stage"] == "contacted":
                agents.act("scribe", "rest_prospect", pid,
                           {"_kind": "prospect_rested", "touches": sent_touches,
                            "why": f"{MAX_TOUCHES} touches sent, no reply"})
                with store_lock():
                    rows = load("prospects")
                    q = _find(rows, pid)
                    if q and not q.get("dormant"):
                        q["dormant"] = iso()
                        save("prospects", rows)
                out["rested"] = out.get("rested", 0) + 1
                continue
            waiting = any(m.get("prospect_id") == pid and m.get("status") == "draft"
                          for m in msgs)
            recent = any(m.get("kind") == "follow_up" and m.get("prospect_id") == pid
                         and (parse(m.get("at")) or now()) >
                         now() - timedelta(days=CADENCE_DAYS[p["stage"]])
                         for m in msgs)
            if not waiting and not recent:
                body = FOLLOW_UP_TEMPLATE.format(
                    first=_first(p["name"]),
                    evidence_one=(ev[0] if ev else
                                  "[no new figure to cite — say so plainly]"))
                m = _draft("draft_follow_up", "follow_up", "prospect_owner",
                           pid, "Following up", body, pid)
                if m:
                    msgs.append(m)
                    out["follow_ups"] += 1

        # -- the proposal shell: R0, assembled when a meeting happened
        if p["stage"] == "meeting" and not any(
                d.get("kind") == "proposal" for d in p.get("drafts", [])):
            agents.act("scribe", "draft_proposal", pid,
                       {"_kind": "proposal_assembled"})
            p.setdefault("drafts", []).append({
                "kind": "proposal", "at": iso(),
                "body": PROPOSAL_TEMPLATE.format(
                    prospect=p["name"], date=iso()[:10],
                    evidence="\n".join(f"   - {l}" for l in ev[:4]) or
                             "   - [portfolio too new to cite figures]")})
            upsert("prospects", p)
            out["proposals"] += 1

        # -- referrer update on an outcome, once
        if (p["stage"] in TERMINAL and src.get("kind") == "referral"
                and str(src.get("by", "")).startswith("owner:")
                and not _has_msg(msgs, "referrer_update", prospect_id=pid)):
            ref_owner = src["by"].split(":", 1)[1]
            o = by_id("owners", ref_owner) or {}
            if o:
                outcome_line = ("we're delighted to say they've come on board."
                                if p["stage"] == "won" else
                                "the timing wasn't right, and we've closed the "
                                "file respectfully.")
                m = _draft("update_referrer", "referrer_update", "owner",
                           ref_owner, f"About {p['name']}",
                           REFERRER_UPDATE_TEMPLATE.format(
                               first=_first(o.get("name")), prospect=p["name"],
                               outcome_line=outcome_line), pid)
                if m:
                    msgs.append(m)
                    out["referrer_updates"] += 1
    return out
