#!/usr/bin/env python3
"""Property OS — the agent crew.

Seven agents. Each one owns a decision, executes at an earned autonomy rung,
and writes what it did to the append-only event log with that rung attached.

  triage     intake diagnosis, priority, self-fix deflection, unit memory
  dispatch   vendor selection, the SLA watchdog, spend, quote anomalies
  concierge  tenant comms, scheduling, the 48h check-back, reopen
  steward    component ledger, capital recommendations, seasonal prevention
  retention  renewal risk, lease expiry, offer drafts, silent units
  ledger     owner reporting and the counterfactual
  scout      (Growth module, pipeline.py) referral import, prospect briefs,
             the cadence nag — aimed at the human, never the prospect
  scribe     (Growth module, pipeline.py) outreach + proposal DRAFTS; there
             is no send action at any rung, by construction
  sentinel   fair-housing + habitability screen on everything outbound, and
             the vendor-compliance watch. Sentinel can VETO; nothing that
             reaches a resident bypasses it.

TWO THINGS THIS FILE IS HONEST ABOUT
------------------------------------
1. The deterministic floor always runs. The Claude calls REFINE decisions;
   they never gate them. Pull the API key and every agent still routes an
   emergency correctly — it just stops writing good prose and stops reading
   photos. That is deliberate: a maintenance dispatcher that stops working
   when a model endpoint is slow is not a product, it is a liability.

2. No agent sends anything to a resident on its own judgment. Free-text to a
   resident is R1 (drafted, human approves) and legal notices are R0 (draft
   only, forever). The autonomy matrix in core.py is the authority; this file
   asks it rather than deciding for itself.

Run:  python3 agents.py --all           # one full sweep of every agent
      python3 agents.py --agent triage
      python3 agents.py --explain       # what each agent may do unattended
"""
import argparse, json, os, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import money
from core import (AUTONOMY, CATEGORIES, COMPONENT_LIFE, PRIORITIES, SELF_FIX,
                  by_id, hours_between, iso, load, log_event, nid, now, parse,
                  rung_for, save, upsert)

# --------------------------------------------------------------- model choice
#
# One global model was wrong: these three calls are not the same kind of work.
#
#   triage      short text (+ a photo) -> a fixed JSON schema. A classification
#               task, run on EVERY request, and run SYNCHRONOUSLY inside the
#               HTTP request when the priority is P1 so an emergency routes on
#               intake instead of waiting for the next sweep. Latency here is a
#               product requirement, not a preference.
#   concierge   two or three sentences to a resident. Low stakes, R2.
#   retention   a renewal letter drafted off a real service history. The only
#               call with genuine prose judgment — and it is R1, so a human
#               reads and edits every one before it goes out.
#
# The triage default is claude-sonnet-5, and unlike every other choice in this
# block it is MEASURED, not reasoned (bench_models.py, 2026-08-16, n=19 against
# a real key — full table in _README.md):
#
#     floor    89% pri / 95% cat / ~0s        sonnet-5  84% / 100% / p95 13s
#     haiku    89% / 89% / p95 7.5s           opus-5    84% /  95% / p95 20s
#                                             fable-5   84% / 100% / p95 19s
#
#   - No model beat the floor on priority; the escalate-only rule means a
#     model can only ADD over-escalations, and each model added exactly one.
#   - Sonnet 5 was the cheapest model to reach 100% category — category is
#     what drives the parts list, the one thing a model adds over keywords.
#   - Opus 5 (the old default) paid the worst latency for zero measured gain:
#     the same category accuracy as free keywords at p95 20s.
#   - Fable 5 tied Sonnet on accuracy at 3.3x the price and 1.5x the latency,
#     confirming the pre-benchmark call. One correction to the record: its
#     measured p50 here was ~14s, not the minutes the earlier comment feared —
#     that fear belongs to hard agentic turns, not schema-bound classification.
#     Still disqualifying inside a synchronous P1 request, and the retention /
#     ZDR constraint is unchanged, so the import guard below stands.
#
# Caveat stated rather than hidden: n=19, so every 5% is one case. This ranks
# "clearly not worth it" (opus/fable for triage) confidently; Sonnet-vs-Haiku
# is one case apart and a larger set could flip it.
#
# concierge and retention stay on the session default — their output is prose
# a human reads (R2 notify / R1 approve), nothing measured them, and unmeasured
# defaults do not get changed here.
DEFAULT_MODEL = os.environ.get("PROPERTYOS_MODEL", "claude-opus-5")
MODELS = {
    "triage": os.environ.get("PROPERTYOS_MODEL_TRIAGE", "claude-sonnet-5"),
    "concierge": os.environ.get("PROPERTYOS_MODEL_CONCIERGE", DEFAULT_MODEL),
    "retention": os.environ.get("PROPERTYOS_MODEL_RETENTION", DEFAULT_MODEL),
}

# Models whose latency profile is incompatible with the synchronous P1 path.
# Selecting one for triage is refused loudly at import rather than discovered
# by a resident waiting on an emergency.
SYNCHRONOUS_UNSAFE = {"claude-fable-5", "claude-mythos-5", "claude-mythos-preview"}
if MODELS["triage"] in SYNCHRONOUS_UNSAFE:
    raise SystemExit(
        f"refusing to run triage on {MODELS['triage']}: thinking cannot be disabled "
        "and turns can run for minutes, but triage executes inside the HTTP request "
        "for a P1 emergency. Set PROPERTYOS_MODEL_TRIAGE to a latency-bounded model."
    )

MODEL = DEFAULT_MODEL   # retained for callers that have not been split yet

# --------------------------------------------------------------- model access

def _client():
    """Returns an Anthropic client, or None if unavailable. Never raises —
    every caller has a deterministic path that runs when this returns None.
    """
    try:
        import anthropic
    except ImportError:
        return None
    try:
        return anthropic.Anthropic()
    except Exception:
        return None


def ask(system, user, schema=None, max_tokens=2000, images=None, model=None):
    """One Claude call. Returns the parsed dict (with `schema`) or text, or
    None when the model is unreachable — callers MUST handle None.

    `model` is per-task (see MODELS). Callers pass their own so the choice is
    visible at the call site rather than buried in a global.
    """
    client = _client()
    if client is None:
        return None
    model = model or DEFAULT_MODEL
    content = []
    for img in images or []:
        content.append({"type": "image", "source": {"type": "base64",
                                                    "media_type": img["media_type"],
                                                    "data": img["data"]}})
    content.append({"type": "text", "text": user})
    kwargs = dict(model=model, max_tokens=max_tokens, system=system,
                  messages=[{"role": "user", "content": content}])
    if schema:
        kwargs["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
    try:
        resp = client.messages.create(**kwargs)
    except Exception:
        return None
    if resp.stop_reason == "refusal":
        return None
    text = next((b.text for b in resp.content if b.type == "text"), "")
    if not schema:
        return text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# --------------------------------------------------------------- shared helper

def act(agent, action, subject, detail, amount=None, limit=None):
    """Every state change goes through here so the rung is never guessed.

    Returns (allowed, rung_spec). `allowed` is False for R0/R1 — the caller
    must write a draft or an approval request instead of acting.
    """
    spec = rung_for(action, amount, limit)
    allowed = spec["rung"] in ("R2", "R3")
    log_event(kind=detail.pop("_kind", action), subject_id=subject,
              actor=f"agent:{agent}", rung=spec["rung"],
              detail={**detail, "action": action, "autonomous": allowed})
    return allowed, spec


def queue_approval(agent, kind, subject, summary, payload, why):
    rows = load("approvals")
    rows.append({"id": core.nid("apr"), "at": iso(), "agent": agent, "kind": kind,
                 "subject": subject, "summary": summary, "payload": payload,
                 "why_human": why, "status": "pending"})
    save("approvals", rows)


def queue_message(agent, to_kind, to_id, subject, body, request_id=None,
                  status="draft", channel="app", **extra):
    row = {"id": core.nid("msg"), "at": iso(), "agent": agent, "to_kind": to_kind,
           "to_id": to_id, "subject": subject, "body": body, "channel": channel,
           "request_id": request_id, "status": status, **extra}
    with core.store_lock():
        rows = load("messages")
        rows.append(row)
        save("messages", rows)
    return row


# =============================================================== 1. TRIAGE

TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": list(CATEGORIES)},
        "priority": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
        "confidence": {"type": "number"},
        "visible_in_photo": {"type": "string"},
        "likely_cause": {"type": "string"},
        "parts_to_bring": {"type": "array", "items": {"type": "string"}},
        "safe_self_fix": {"type": "boolean"},
        "clarifying_question": {"type": "string"},
        "habitability_risk": {"type": "boolean"},
        "reasoning": {"type": "string"},
    },
    "required": ["category", "priority", "confidence", "likely_cause",
                 "parts_to_bring", "safe_self_fix", "habitability_risk", "reasoning"],
    "additionalProperties": False,
}

TRIAGE_SYSTEM = """You triage residential maintenance requests for a property manager.

You see what a dispatcher sees: the resident's own words, any photo, and the unit's
service history. Your job is to name the failure, set the urgency, and tell the
vendor what to bring — so the job is fixed on the first visit.

Rules that are not negotiable:
- Habitability first. No heat, no water, no power, sewage backup, gas odour, an
  unsecured exterior door, or anything that makes the unit unsafe or unlivable is
  P1 regardless of how calmly the resident described it. Residents routinely
  understate emergencies; read the situation, not the tone.
- Never propose a self-fix involving gas, a pilot light, standing water near
  electricity, the inside of a disposal, or any panel beyond the breaker face.
  If you are not certain a fix is safe for an untrained person, it is not.
- `parts_to_bring` is the whole point. A vendor who arrives without the part
  turns one visit into two. Use the unit's make/model history where you have it.
- If a photo contradicts the text, trust the photo and say so in `reasoning`.
- Do not diagnose beyond the evidence. "Likely cause" may be "insufficient
  evidence — needs eyes on it", and that is a better answer than a guess.

Set `habitability_risk` true whenever the resident cannot safely or reasonably
live in the unit as-is. Ask `clarifying_question` only when the answer would
change the priority or the parts list — never as a stall."""


def unit_memory(unit_id):
    """What this unit already knows about itself. This is the difference
    between 'no hot water in 4B' and 'no hot water in 4B — Rheem XR450, 9 years
    old, Sutter Plumbing replaced the thermocouple in March, shutoff is behind
    the closet panel'. Same ticket; completely different first visit.
    """
    u = by_id("units", unit_id) or {}
    comps = [c for c in load("components") if c["unit_id"] == unit_id]
    hist = [r for r in load("requests") if r.get("unit_id") == unit_id]
    hist.sort(key=lambda r: r["submitted_at"], reverse=True)
    lines = []
    for c in comps:
        age = core.days_until(c.get("installed"))
        age_y = round(abs(age) / 365.25, 1) if age is not None else "?"
        lines.append(f"{c['label']}: {c.get('make','?')} {c.get('model','?')}, {age_y}y old")
    for r in hist[:6]:
        v = by_id("vendors", r.get("vendor_id")) or {}
        lines.append(f"{r['submitted_at'][:10]} {r['category']} — {r.get('resolution_note') or r['status']}"
                     + (f" [{v.get('name')}]" if v else ""))
    return {"unit": u.get("label"), "beds": u.get("beds"),
            "components": comps, "history_lines": lines,
            "repeat_count": sum(1 for r in hist if r.get("reopened"))}


def run_triage(limit=25):
    out = []
    for r in load("requests"):
        if r.get("triage_final") or r.get("status") != "submitted":
            continue
        mem = unit_memory(r["unit_id"])
        ten = by_id("tenants", r.get("tenant_id")) or {}
        base = core.classify(r.get("description"), bool(r.get("photos")),
                             {"vulnerable_occupant": ten.get("vulnerable_occupant")})

        refined = ask(TRIAGE_SYSTEM, f"""RESIDENT REPORTED: "{r['description']}"
PHOTO ATTACHED: {'yes' if r.get('photos') else 'no'}
UNIT: {mem['unit']} · {mem['beds']}bd
OCCUPANT NOTE: {'infant/elderly/medical occupant on file' if ten.get('vulnerable_occupant') else 'none'}

WHAT THIS UNIT KNOWS ABOUT ITSELF:
{chr(10).join(mem['history_lines']) or '(no history on file)'}

Triage it.""", schema=TRIAGE_SCHEMA, model=MODELS["triage"])

        tri = dict(base)
        if refined:
            # The model may only ESCALATE priority above the rules floor, never
            # de-escalate it. A model that talks itself out of an emergency is
            # the one failure mode this product cannot have.
            order = ["P4", "P3", "P2", "P1"]
            if order.index(refined["priority"]) > order.index(base["priority"]):
                tri["priority"] = refined["priority"]
            tri.update({"category": refined["category"], "source": "rules+model",
                        "likely_cause": refined["likely_cause"],
                        "parts_to_bring": refined["parts_to_bring"],
                        "confidence": refined["confidence"],
                        "reasoning": refined["reasoning"],
                        "clarifying_question": refined.get("clarifying_question"),
                        "model_priority": refined["priority"]})
            if refined.get("habitability_risk") and tri["priority"] in ("P3", "P4"):
                tri["priority"] = "P2"
        r["triage"] = tri
        r["priority"] = tri["priority"]
        r["category"] = tri["category"]
        r["triage_final"] = True
        r.update(core.sla_due(r))

        act("triage", "triage_classify", r["id"],
            {"_kind": "triaged", "category": tri["category"], "priority": tri["priority"],
             "confidence": tri["confidence"], "source": tri["source"]})

        spec = CATEGORIES[tri["category"]]
        fix = spec["self_fix"]
        if r.get("self_fix_failed") or r.get("reopened"):
            # Already tried and it didn't work. Straight to a vendor.
            fix = None
        if fix and (not refined or refined.get("safe_self_fix", True)):
            card = SELF_FIX[fix]
            r["self_fix_offered"] = fix
            act("triage", "offer_self_fix", r["id"],
                {"_kind": "deflected", "self_fix": fix, "avoided": card["avoids"]})
            queue_message("concierge", "tenant", r["tenant_id"], card["title"],
                          "\n".join(f"{i+1}. {s}" for i, s in enumerate(card["steps"]))
                          + "\n\nDidn't work? Tap 'Still broken' and we'll send someone today — "
                            "you won't have to explain it again.",
                          request_id=r["id"], status="sent")
        upsert("requests", r)
        out.append({"request": r["id"], "priority": tri["priority"],
                    "category": tri["category"], "self_fix": fix})
        if len(out) >= limit:
            break
    return out


# =============================================================== 2. DISPATCH

def rank_vendors(request):
    """The assignment market. Score, availability, trade, and — the piece most
    software misses — whether this vendor has been in THIS unit before. A
    vendor who replaced the part last time starts the job knowing something.
    """
    spec = CATEGORIES.get(request.get("category"), CATEGORIES["other"])
    reqs = load("requests")
    prior = {r.get("vendor_id") for r in reqs
             if r.get("unit_id") == request.get("unit_id") and r.get("vendor_id")}
    ranked = []
    for v in load("vendors"):
        if not v.get("active") or spec["trade"] not in v["trades"]:
            continue
        sc = core.vendor_scorecard(v, reqs)
        base = sc.get("score")
        reasons = []
        if base is None:
            base, reasons = 55, [f"unrated — {sc.get('_missing')}"]
        else:
            reasons.append(f"score {base}: first-time-fix {sc['first_time_fix']:.0%}, "
                           f"SLA {sc['sla_hit']:.0%}, tenant {sc['tenant_rating']}/5")
        adj = base
        if v["id"] in prior:
            adj += 8
            reasons.append("has worked this unit before (+8)")
        if request.get("priority") == "P1" and not v.get("after_hours"):
            adj -= 25
            reasons.append("no after-hours coverage on a P1 (-25)")
        exp = core.days_until(v.get("insurance_expires"))
        if exp is not None and exp < 0:
            adj -= 100
            reasons.append(f"INSURANCE EXPIRED {abs(exp)}d ago — not dispatchable")
        ranked.append({"vendor": v, "score": round(adj), "scorecard": sc, "why": reasons})
    ranked.sort(key=lambda x: -x["score"])
    return ranked


def redispatch_after_decline(r, reason=""):
    """A decline is an availability answer, answered immediately: the job
    re-ranks with every decliner excluded and moves to the runner-up on a
    fresh job link — the decliner's link dies with the swap. Mutates `r` in
    place; the caller (the job endpoint, already under store_lock) persists.
    If nobody dispatchable remains, the truth goes to a human as a no_vendor
    approval rather than the job silently going nowhere."""
    declined = r.setdefault("declined_vendor_ids", [])
    if r.get("vendor_id") and r["vendor_id"] not in declined:
        declined.append(r["vendor_id"])
    old_name = (by_id("vendors", r.get("vendor_id")) or {}).get("name")
    ranked = [x for x in rank_vendors(r) if x["vendor"]["id"] not in declined]
    if not ranked or ranked[0]["score"] < 0:
        r["vendor_id"] = None
        r["vendor_token"] = None
        r["vendor_accepted"] = None
        r["status"] = "submitted"
        queue_approval("dispatch", "no_vendor", r["id"],
                       f"Declined by {old_name}; no other dispatchable vendor for "
                       f"{r.get('category')} ({r.get('priority')})",
                       {"request": r["id"], "declined_by": declined,
                        "decline_reason": reason},
                       "every remaining qualified vendor is uninsured, inactive, "
                       "out of area, or has already declined this job")
        return {"reassigned": None, "queued_for_human": True}
    pick = ranked[0]
    allowed, spec = act("dispatch", "assign_vendor", r["id"],
                        {"_kind": "assigned", "vendor": pick["vendor"]["name"],
                         "score": pick["score"], "why": pick["why"],
                         "after_decline_by": old_name})
    if not allowed:
        return {"reassigned": None, "queued_for_human": True}
    r["vendor_id"] = pick["vendor"]["id"]
    r["assigned_at"] = iso()
    r["assignment_why"] = pick["why"]
    r["status"] = "assigned"
    r["vendor_accepted"] = None
    r["scheduled_for"] = None
    r["vendor_token"] = nid("vtk")
    log_event("vendor_swapped", r["id"], "agent:dispatch", "R2",
              {"to": pick["vendor"]["name"],
               "reason": f"declined by {old_name}" + (f" — {reason}" if reason else "")})
    return {"reassigned": pick["vendor"]["name"], "queued_for_human": False}


def run_dispatch():
    reqs = load("requests")
    out = []

    # --- (a) assign anything triaged and unassigned
    for r in reqs:
        if r.get("status") != "submitted" or not r.get("triage_final") or r.get("self_fix_offered"):
            continue
        ranked = rank_vendors(r)
        if not ranked or ranked[0]["score"] < 0:
            queue_approval("dispatch", "no_vendor", r["id"],
                           f"No dispatchable vendor for {r['category']} ({r['priority']})",
                           {"request": r["id"]},
                           "every qualified vendor is uninsured, inactive, or out of area")
            continue
        pick = ranked[0]
        allowed, spec = act("dispatch", "assign_vendor", r["id"],
                            {"_kind": "assigned", "vendor": pick["vendor"]["name"],
                             "score": pick["score"], "why": pick["why"],
                             "runner_up": ranked[1]["vendor"]["name"] if len(ranked) > 1 else None})
        if allowed:
            r["status"] = "assigned"
            r["vendor_id"] = pick["vendor"]["id"]
            r["assigned_at"] = iso()
            r["assignment_why"] = pick["why"]
            # the job card IS the outreach artifact — minted at assignment, or
            # the "system reaches out to the vendor" step has nothing to send
            r["vendor_token"] = nid("vtk")
            upsert("requests", r)
            out.append({"request": r["id"], "assigned": pick["vendor"]["name"],
                        "rung": spec["rung"]})

    # --- (b) the SLA watchdog: escalate BEFORE the tenant complains
    for r in load("requests"):
        if r.get("status") == "resolved" or r.get("escalated"):
            continue
        state = core.sla_state(r)
        if state not in ("at_risk", "breached"):
            continue
        ranked = [x for x in rank_vendors(r) if x["vendor"]["id"] != r.get("vendor_id")]
        allowed, spec = act("dispatch", "escalate_backup_vendor", r["id"],
                            {"_kind": "escalated", "sla_state": state,
                             "current": (by_id("vendors", r.get("vendor_id")) or {}).get("name"),
                             "backup": ranked[0]["vendor"]["name"] if ranked else None,
                             "resolve_by": r.get("resolve_by")})
        r["escalated"] = True
        r["escalation_reason"] = f"SLA {state} against a {r.get('priority')} clock"
        if allowed and ranked and state == "breached":
            r["vendor_id"] = ranked[0]["vendor"]["id"]
            r["assigned_at"] = iso()
            # rotate the job link on a swap — the replaced vendor's link must
            # die with the swap, or two vendors hold live keys to one job
            r["vendor_token"] = nid("vtk")
            r["vendor_accepted"] = None
            log_event("vendor_swapped", r["id"], "agent:dispatch", "R2",
                      {"to": ranked[0]["vendor"]["name"], "reason": "SLA breached"})
        upsert("requests", r)
        out.append({"request": r["id"], "escalated": state})

    # --- (b2) declines are re-dispatched by redispatch_after_decline(), called
    #     synchronously from the job endpoint — a decline is an availability
    #     answer and it is answered immediately, not on the next sweep.

    # --- (c) money. Two instruments, deliberately distinct:
    #
    #   routine    the owner's STANDING limit. Under it and clean: R2. Over it
    #              or price-anomalous: R1, a human decides first.
    #   emergency  a P1 is a habitability failure, and its clock outranks the
    #              approval queue. The owner's EMERGENCY authority applies:
    #              commit the spend up to that cap, send the owner notice the
    #              same moment, and turn a suspicious price into a post-hoc
    #              invoice review instead of a reason to leave a resident
    #              without heat. Fix first, argue about the price afterwards.
    #              Above even the emergency cap: R1 — "emergency" is a reason
    #              to move fast, not a blank cheque.
    for r in load("requests"):
        q = r.get("quote")
        if not q or r.get("spend_decided"):
            continue
        prop = by_id("properties", r.get("property_id")) or {}
        owner = by_id("owners", prop.get("owner_id")) or {}
        standing = owner.get("spend_approval_limit", 400)
        emergency = r.get("priority") == "P1"
        cap = owner.get("emergency_spend_limit", 2500) if emergency else standing
        action = "approve_spend_emergency" if emergency else "approve_spend_under"
        anomaly = core.price_anomaly(r, load("requests"))
        allowed, spec = act("dispatch", action, r["id"],
                            {"_kind": "spend_approved", "amount": q, "limit": cap,
                             "emergency": emergency, "anomaly": anomaly},
                            amount=q, limit=cap)
        r["spend_decided"] = True
        r["price_anomaly"] = anomaly
        if allowed and emergency:
            r["spend_approved"] = True
            if r.get("stall_reason") == "awaiting_owner_approval":
                r["stall_reason"] = None
                r["stall_since"] = None
            # The notice is what makes this R2 rather than R3 — it goes out
            # the moment the spend is committed, not in the monthly report.
            n_ok, _ = act("dispatch", "message_owner", r["id"],
                          {"_kind": "message_sent", "template": "emergency spend notice",
                           "amount": q})
            v = by_id("vendors", r.get("vendor_id")) or {}
            queue_message("dispatch", "owner", owner.get("id"),
                          f"Emergency spend committed — {r.get('title', 'P1 repair')[:48]}",
                          f"A P1 habitability repair at {prop.get('name', '')} "
                          f"{(by_id('units', r.get('unit_id')) or {}).get('label', '')} was "
                          f"authorized under your ${cap} emergency authority.\n\n"
                          f"Quote: ${q} · Vendor: {v.get('name', 'unassigned')}\n"
                          f"Issue: {r.get('description', '')[:140]}\n\n"
                          f"Your standing per-job limit (${standing}) was not the applicable "
                          f"instrument: a P1 habitability clock does not wait on an approval "
                          f"queue. This notice is the control.",
                          request_id=r["id"], status="sent" if n_ok else "draft")
            if (anomaly or {}).get("flag"):
                queue_approval("dispatch", "emergency_review", r["id"],
                               f"${q} committed on a P1 — invoice is "
                               f"{anomaly['ratio']}x the median. Review after the fact.",
                               {"request": r["id"], "amount": q, "owner": owner.get("name"),
                                "property": prop.get("name"), "emergency": True,
                                "anomaly": anomaly},
                               "the money is already committed under the emergency authority "
                               "— habitability outranked the price argument. This is the "
                               "post-hoc review of that invoice, not a gate on the repair")
        elif allowed and not (anomaly or {}).get("flag"):
            r["spend_approved"] = True
        else:
            r["spend_approved"] = False
            # `anomaly` carries no `ratio` when there were too few comparable
            # jobs to compute one — it returns {"flag": False, "_missing": ...}.
            # Reading it unconditionally crashed the whole dispatch sweep.
            if emergency and q > cap:
                why = (f"${q} exceeds even {owner.get('name', 'the owner')}'s "
                       f"${cap} emergency authority — the one approval a human "
                       f"must make at P1 speed")
            elif q > cap:
                why = (f"${q} exceeds {owner.get('name', 'the owner')}'s "
                       f"${cap} standing limit")
            elif (anomaly or {}).get("ratio"):
                why = (f"quote is {anomaly['ratio']}x the portfolio median "
                       f"for {r['category']}")
            else:
                why = "flagged for review before this spend is committed"
            queue_approval("dispatch", "spend", r["id"],
                           f"${q} — {r.get('title', 'repair')}",
                           {"request": r["id"], "amount": q, "owner": owner.get("name"),
                            "emergency": emergency, "anomaly": anomaly}, why)
        upsert("requests", r)
        out.append({"request": r["id"], "spend": q, "auto": r["spend_approved"],
                    "emergency": emergency})
    return out


# =============================================================== 3. CONCIERGE

CONCIERGE_SYSTEM = """You write to residents on behalf of their property manager.

Write like a competent human who respects the reader's time. Short. Specific.
No corporate throat-clearing, no "we value your tenancy", no exclamation marks.

Every message answers the three things a resident actually wants to know:
what is happening, when someone will be there, and what they need to do.

If we are late or we got it wrong, say so plainly in the first sentence. Do not
explain our internal reasons — a resident with no hot water does not care that
the part was backordered, they care when they can shower. Give them the date.

Never promise a time we have not scheduled. Never speculate about cost or who
pays. Never discuss the lease, the deposit, or anything legal — that is not
your call. If the resident raised one of those, say a person will follow up."""


def run_concierge():
    out = []

    # --- (a) the 48-hour check-back. This is what makes "resolved" mean fixed.
    for r in load("requests"):
        if r.get("status") != "resolved" or r.get("checkback_sent"):
            continue
        done = parse(r.get("resolved_at"))
        if not done or (now() - done) < timedelta(hours=48):
            continue
        allowed, spec = act("concierge", "message_tenant", r["id"],
                            {"_kind": "message_sent", "template": "48h check-back"})
        queue_message("concierge", "tenant", r["tenant_id"],
                      "Is it actually fixed?",
                      f"We closed out \"{r.get('title')}\" two days ago. Is it working?\n\n"
                      "Tap 'Still broken' and we'll reopen it — no new request, no "
                      "re-explaining. You'll get the same vendor if they're available.\n\n"
                      "If it's fixed, leave the crew a quick star rating — thirty seconds, "
                      "and it genuinely decides who we send next time.",
                      request_id=r["id"], status="sent" if allowed else "draft")
        r["checkback_sent"] = True
        upsert("requests", r)
        out.append({"request": r["id"], "sent": "48h check-back"})

    # --- (b) proactive status on anything stalled, before they chase us
    for r in core.open_requests():
        if r.get("status_note_sent") or not r.get("stall_reason"):
            continue
        stall = r["stall_reason"]
        human = {
            "parts_backorder": "the part is on order",
            "awaiting_owner_approval": "we're waiting on an approval",
            "no_access": "we haven't been able to get in",
            "scheduled_out": "it's scheduled",
            "vendor_unresponsive": "our vendor went quiet and we're reassigning",
        }[stall]
        body = ask(CONCIERGE_SYSTEM, f"""Write a short status update to the resident.

REQUEST: "{r.get('title')}" — opened {r['submitted_at'][:10]}, priority {r.get('priority')}
STATUS: {human}
DAYS OPEN: {int((hours_between(r['submitted_at'], iso()) or 0) / 24)}

They have not chased us. We are telling them first. Two or three sentences.""",
                   model=MODELS["concierge"])
        if body is None:
            body = (f"Quick update on \"{r.get('title')}\": {human}. "
                    "We'll message you the moment there's a date. Nothing you need to do.")
        allowed, spec = act("concierge", "message_tenant_custom", r["id"],
                            {"_kind": "message_sent", "stall": stall, "drafted": True})
        queue_message("concierge", "tenant", r["tenant_id"], "Update on your request",
                      body, request_id=r["id"], status="sent" if allowed else "draft")
        r["status_note_sent"] = True
        upsert("requests", r)
        out.append({"request": r["id"], "drafted": stall, "auto_sent": allowed})
    return out


# =============================================================== 4. STEWARD

def run_steward():
    """Component economics + prevention. Recommends; never spends.

    Two very different outputs, deliberately kept apart. `replace_now` is a
    decision the owner needs this month and gets an approval row.
    `plan_replacement` is a budget line for next year — routing it to the same
    queue is how an approvals inbox becomes noise nobody reads, and a noisy
    inbox is how the one urgent item gets missed.
    """
    reqs = load("requests")
    out, budget = [], []
    for c in load("components"):
        v = core.component_verdict(c, reqs)
        if not v:
            continue
        if v["verdict"] == "plan_replacement":
            u = by_id("units", c["unit_id"]) or {}
            budget.append({"component": c["id"], "unit": u.get("label"),
                           "label": v["label"], "age_years": v["age_years"],
                           "life_years": v["life_years"], "replace_cost": v["replace_cost"],
                           "why": v["why"]})
            continue
        if v["verdict"] != "replace_now" or c.get("capital_flagged"):
            continue
        u = by_id("units", c["unit_id"]) or {}
        prop = by_id("properties", c.get("property_id")) or {}
        owner = by_id("owners", prop.get("owner_id")) or {}
        act("steward", "capital_recommendation", c["id"],
            {"_kind": "capital_recommended", "verdict": v["verdict"],
             "unit": u.get("label"), "spend": v["repair_spend"],
             "replace": v["replace_cost"]})
        queue_approval("steward", "capital", c["id"],
                       f"{v['label']} · {prop.get('name')} {u.get('label')} — {v['verdict'].replace('_',' ')}",
                       # `property` / `unit_label` are carried so the approvals queue
                       # can sort and filter on them instead of parsing the summary
                       # string, which is display copy and will change.
                       {"component": c["id"], "owner": owner.get("name"),
                        "property": prop.get("name"), "unit_label": u.get("label"), **v},
                       "owner capital is the owner's decision — this is arithmetic, not an instruction")
        c["capital_flagged"] = iso()
        upsert("components", c)
        out.append({"component": c["id"], "verdict": v["verdict"],
                    "why": v["why"], "unit": u.get("label")})

    # --- preventive maintenance. The component ledger knows every furnace's
    # age; this is the part that acts on it BEFORE the 2am failure. Idempotent:
    # a component gets one open PM order at a time, and never before its
    # interval has elapsed since the last one (or install).
    reqs_all = load("requests")
    pm_done = {}
    for r in reqs_all:
        if r.get("preventive") and r.get("component_id"):
            prev = pm_done.get(r["component_id"])
            if not prev or r["submitted_at"] > prev:
                pm_done[r["component_id"]] = r["submitted_at"]
    open_pm = {r.get("component_id") for r in reqs_all
               if r.get("preventive") and r.get("status") != "resolved"}
    created = 0
    for c in load("components"):
        spec = core.PM_SCHEDULE.get(c.get("kind"))
        if not spec or c["id"] in open_pm:
            continue
        u = by_id("units", c["unit_id"]) or {}
        if not u.get("tenant_id"):
            continue
        last = pm_done.get(c["id"]) or c.get("installed")
        if last and (now() - parse(last)).days < spec["every_days"]:
            continue
        allowed, _ = act("steward", "schedule_preventive", c["id"],
                         {"_kind": "pm_scheduled", "task": spec["task"],
                          "unit": u.get("label"), "interval_days": spec["every_days"]})
        if not allowed:
            continue
        r = {"id": core.nid("req"), "unit_id": u["id"], "property_id": u["property_id"],
             "tenant_id": u["tenant_id"], "title": spec["task"][:70],
             "description": f"Preventive maintenance ({spec['every_days']}d interval): {spec['task']}",
             "category": spec["category"], "priority": spec["priority"],
             "status": "submitted", "submitted_at": iso(), "channel": "preventive",
             "photos": [], "triage_final": True, "preventive": True,
             "component_id": c["id"], "entry_permission": "appointment",
             "triage": {"category": spec["category"], "priority": spec["priority"],
                        "confidence": 1.0, "source": "pm-schedule",
                        "reasons": [f"interval PM: {spec['task']}"],
                        "est_cost": spec["est"]}}
        r.update(core.sla_due(r))
        upsert("requests", r)
        created += 1
        if created >= 12:
            break   # spread a backlog across sweeps instead of flooding dispatch
    budget.sort(key=lambda b: -b["replace_cost"])
    save("capital_forecast", {"generated": iso(), "replace_now_queued": len(out),
                              "plan_replacement": budget,
                              "next_5y_exposure": sum(b["replace_cost"] for b in budget),
                              "note": "a budget forecast, not an approval request — "
                                      "nothing here needs a decision this month"})
    return out


# =============================================================== 5. RETENTION

RENEWAL_SYSTEM = """You draft renewal outreach for a property manager.

You are given a resident's real service history — every request, every delay,
every time we were late. Use it. A renewal letter that ignores three months of
a broken dishwasher is worse than no letter.

Structure: acknowledge specifically what went wrong (name it), say what changed
or will change, then make the offer. If nothing went wrong, skip the apology —
manufactured contrition reads as insincere and residents can tell.

Hard limits. You are drafting for a human to send, and these carry legal weight:
- Never reference or imply anything about familial status, race, national origin,
  religion, disability, sex, or source of income. Not as a compliment, not as
  small talk, not inferred from a name. This is fair-housing exposure.
- Never state a price the manager did not give you.
- Never threaten non-renewal or imply the resident has no alternative.
- Never make a repair promise with a date unless the date is in the record."""


def run_retention(window_days=90):
    units, reqs, surveys = load("units"), load("requests"), load("surveys")
    out = []
    for u in units:
        d = core.days_until(u.get("lease", {}).get("end"))
        if d is None or d > window_days or d < -30:
            continue
        risk = core.renewal_risk(u, reqs, surveys)
        ten = by_id("tenants", u.get("tenant_id"))
        if not ten:
            continue
        prop = by_id("properties", u["property_id"]) or {}
        if u.get("renewal_drafted"):
            continue

        hist = [r for r in reqs if r.get("unit_id") == u["id"]]
        hist.sort(key=lambda r: r["submitted_at"], reverse=True)
        summary = "\n".join(
            f"- {r['submitted_at'][:10]} {r.get('title','')[:50]} — "
            f"{r['status']}{' (BREACHED SLA)' if r.get('sla_breached') else ''}"
            f"{' (came back after we closed it)' if r.get('reopened') else ''}"
            for r in hist[:8]) or "- no maintenance requests on file"

        body = ask(RENEWAL_SYSTEM, f"""Draft a renewal message.

RESIDENT: {ten['name']} · {prop.get('name')} {u['label']} · resident since {ten['move_in'][:10]}
LEASE ENDS: {u['lease']['end'][:10]} ({d} days)
CURRENT RENT: ${u['rent']}/mo
NON-RENEWAL RISK: {risk.get('score')} ({risk.get('band')})
WHAT DROVE THAT: {json.dumps(risk.get('drivers', []), indent=1)}

THEIR SERVICE HISTORY:
{summary}

The manager has NOT set a renewal price. Leave it as [RENEWAL TERMS] for them
to fill. Draft the message.""", model=MODELS["retention"])
        if body is None:
            body = (f"Hi {ten['name'].split()[0]} — your lease is up on "
                    f"{u['lease']['end'][:10]} and we'd like you to stay. "
                    "[RENEWAL TERMS]\n\n(Model unavailable — this is the fallback "
                    "template, not a drafted message. Rewrite before sending.)")

        allowed, spec = act("retention", "renewal_offer", u["id"],
                            {"_kind": "renewal_drafted", "days_out": d,
                             "risk": risk.get("score"), "band": risk.get("band")})
        queue_approval("retention", "renewal", u["id"],
                       f"{prop.get('name')} {u['label']} — {ten['name']}, "
                       f"{d}d out, risk {risk.get('score')} ({risk.get('band')})",
                       {"unit": u["id"], "tenant": ten["id"], "draft": body,
                        "property": prop.get("name"), "unit_label": u["label"],
                        "days_left": d,
                        "risk": risk, "current_rent": u["rent"],
                        # Key must match the lease tracker's (`turn_cost`) — the UI
                        # reads one name for both, and the mismatch rendered the
                        # turnover figure as an em-dash on every renewal card.
                        "turn_cost": turn_cost(u)},
                       "a price commitment to a resident — the manager sends this, never an agent")
        u["renewal_drafted"] = iso()
        u["renewal_risk"] = risk
        upsert("units", u)
        out.append({"unit": u["id"], "days_out": d, "risk": risk.get("score")})
    return out


def turn_cost(unit):
    """What losing this resident costs. Make-ready + vacancy + leasing.

    Vacancy days upgrade from assumption to MEASUREMENT once the turnover
    pipeline has 3 completed turns — the basis line always says which one you
    are looking at.
    """
    rent = unit.get("rent", 0)
    mv = core.measured_vacancy()
    vac_days = mv["days"] if mv.get("days") is not None else 32
    basis = (mv["basis"] if mv.get("days") is not None else
             "32-day vacancy ASSUMPTION (" + mv["_missing"] + ")")
    make_ready = 1400 + unit.get("beds", 2) * 350
    total = round(make_ready + rent / 30 * vac_days + rent * 0.75 + 250)
    return {"make_ready": make_ready,
            "vacancy_days": vac_days, "vacancy_cost": round(rent / 30 * vac_days),
            "leasing_fee": round(rent * 0.75), "turnover_admin": 250,
            "total": total,
            "assumptions": basis + " · 75%-of-one-month leasing fee · make-ready "
                           "scaled by bedroom count."}


# =============================================================== 5b. COLLECTIONS

def run_collections():
    """Rent charges and the delinquency ladder.

    The ladder only ever ASKS, in escalating formality — and the escalation
    itself de-automates: reminder R2, firm notice R1 (draft), payment plan R1
    (proposal), legal referral R0 (drafted for counsel, never sent). The
    further behind a resident is, the LESS this software does alone. Money
    movement never happens here at all.
    """
    out = {"charges_posted": 0, "reminders": 0, "notices_drafted": 0,
           "plans_proposed": 0, "referrals_drafted": 0}
    out["charges_posted"] = len(money.post_rent_charges())

    for d in money.delinquency():
        r_id = f"{d['tenant_id']}:{d['oldest_due'][:10]}"
        t = by_id("tenants", d["tenant_id"]) or {}
        if d["stage"] == "remind":
            if any(m.get("thread") == r_id and m.get("kind") == "rent_reminder"
                   for m in load("messages")):
                continue
            allowed, _ = act("collections", "rent_reminder", d["tenant_id"],
                             {"_kind": "message_sent", "template": "rent reminder",
                              "days_late": d["days_late"], "balance": d["balance"]})
            m = queue_message("collections", "tenant", d["tenant_id"],
                          "A reminder about this month's rent",
                          f"Hi {t.get('name', '').split(' ')[0]} — our records show a balance of "
                          f"${d['balance']:,.0f}, due {d['oldest_due'][:10]}. If you've already "
                          f"paid, thank you — records can lag a day or two and you can ignore "
                          f"this. If something's making this month hard, reply here and a person "
                          f"will work with you on it. No fees have been added.",
                          status="sent" if allowed else "draft",
                          kind="rent_reminder", thread=r_id)
            out["reminders"] += 1
        elif d["stage"] in ("notice", "plan"):
            kind = "delinquency_notice" if d["stage"] == "notice" else "payment_plan_proposal"
            if any(a.get("kind") == "delinquency" and a["payload"].get("thread") == r_id
                   and a["payload"].get("step") == d["stage"]
                   for a in load("approvals")):
                continue
            act("collections", kind, d["tenant_id"],
                {"_kind": "delinquency_step", "step": d["stage"],
                 "days_late": d["days_late"], "balance": d["balance"]})
            body = (f"[FIRM NOTICE DRAFT — human sends] {t.get('name')}: balance "
                    f"${d['balance']:,.0f}, {d['days_late']} days past due."
                    if d["stage"] == "notice" else
                    f"[PAYMENT PLAN PROPOSAL — human approves terms] {t.get('name')}: "
                    f"${d['balance']:,.0f} over 3 months alongside current rent.")
            queue_approval("collections", "delinquency", d["tenant_id"],
                           f"{t.get('name')} · {d['unit']} — ${d['balance']:,.0f}, "
                           f"{d['days_late']}d late — {d['stage']}",
                           {"tenant": d["tenant_id"], "thread": r_id, "step": d["stage"],
                            "balance": d["balance"], "days_late": d["days_late"],
                            "draft": body, "property": (by_id("properties", d.get("property_id")) or {}).get("name"),
                            "amount": d["balance"]},
                           "escalating a resident's delinquency changes the relationship — "
                           "a human decides tone, timing, and terms")
            out["notices_drafted" if d["stage"] == "notice" else "plans_proposed"] += 1
        elif d["stage"] == "referral":
            if any(a.get("kind") == "legal_referral" and a["payload"].get("tenant") == d["tenant_id"]
                   for a in load("approvals")):
                continue
            act("collections", "legal_referral", d["tenant_id"],
                {"_kind": "delinquency_step", "step": "referral",
                 "days_late": d["days_late"], "balance": d["balance"]})
            queue_approval("collections", "legal_referral", d["tenant_id"],
                           f"{t.get('name')} · {d['unit']} — ${d['balance']:,.0f}, "
                           f"{d['days_late']}d — REFERRAL PACKET (R0)",
                           {"tenant": d["tenant_id"], "amount": d["balance"],
                            "days_late": d["days_late"],
                            "property": (by_id("properties", d.get("property_id")) or {}).get("name"),
                            "packet": "ledger history + notice trail assembled for counsel"},
                           "referring a resident for collection or eviction is NEVER "
                           "automated — this packet goes to a human, then to counsel")
            out["referrals_drafted"] += 1
    return out


# =============================================================== 6. LEDGER

def owner_report(owner_id, days=30):
    owner = by_id("owners", owner_id)
    if not owner:
        return None
    props = [p for p in load("properties") if p["id"] in owner["properties"]]
    pids = {p["id"] for p in props}
    units = [u for u in load("units") if u["property_id"] in pids]
    reqs = [r for r in load("requests") if r.get("property_id") in pids]
    cutoff = now() - timedelta(days=days)
    window = [r for r in reqs if (parse(r["submitted_at"]) or now()) >= cutoff]
    done = [r for r in window if r.get("status") == "resolved"]
    spend = sum(r.get("actual_cost") or 0 for r in window)
    defl = [r for r in window if r.get("resolution_kind") == "deflected"]
    avoided = sum(CATEGORIES.get(r.get("category"), CATEGORIES["other"])["median_cost"] for r in defl)
    occupied = [u for u in units if u.get("tenant_id")]

    return {
        "owner": owner["name"], "properties": [p["name"] for p in props],
        "units": len(units), "occupied": len(occupied),
        "occupancy": round(len(occupied) / len(units), 3) if units else None,
        "window_days": days,
        "requests_received": len(window), "resolved": len(done),
        "open_now": len([r for r in reqs if r.get("status") != "resolved"]),
        "avg_resolution": core.avg_resolution_hours(reqs, days),
        "p1_resolution": core.avg_resolution_hours(reqs, days, "P1"),
        "maintenance_spend": spend,
        "spend_per_unit": round(spend / len(units), 2) if units else None,
        # The line owners never see anywhere else: what we stopped from happening.
        "avoided_cost": {"deflected_dispatches": len(defl), "value": avoided,
                         "basis": "portfolio median cost for each job class that a "
                                  "guided self-fix resolved without a truck roll"},
        "sla_hit_rate": (round(sum(1 for r in done if not r.get("sla_breached")) / len(done), 3)
                         if done else None),
        "capital_flagged": [
            {"unit": (by_id("units", c["unit_id"]) or {}).get("label"), **v}
            for c in load("components") if c["property_id"] in pids
            for v in [core.component_verdict(c, reqs)]
            if v and v["verdict"] == "replace_now"][:8],
        "leases_expiring_60d": [
            {"unit": u["label"], "ends": u["lease"]["end"][:10],
             "days": core.days_until(u["lease"]["end"]),
             "risk": core.renewal_risk(u, reqs, load("surveys")).get("score"),
             "exposure": turn_cost(u)["total"]}
            for u in occupied if (core.lease_window(u) or 999) <= 60],
    }


LEDGER_CADENCE_DAYS = 6

def run_money_cycle():
    """The ledger agent's money half: fee, statement, disbursement DRAFT.

    Everything here is accounting or drafting at R2. The one thing this
    function will never contain is a call that moves money — executing the
    batch is a human at a bank, recorded afterwards (money.execute_batch
    enforces the human actor and the bank reference).
    """
    out = {"fees": 0, "statements": 0, "batch": None, "reconcile": None}
    mk = money.month_key(now())
    for o in load("owners"):
        if money.take_mgmt_fee(o["id"], mk):
            act("ledger", "take_mgmt_fee", o["id"],
                {"_kind": "mgmt_fee_taken", "month": mk})
            out["fees"] += 1
        already = any(m.get("kind") == "statement" and m.get("to_id") == o["id"]
                      and m.get("month") == mk for m in load("messages"))
        if not already:
            st = money.owner_statement(o["id"], mk)
            if st and (st["rent_collected"] or st["maintenance_paid"]):
                allowed, _ = act("ledger", "issue_statement", o["id"],
                                 {"_kind": "statement_issued", "month": mk,
                                  "net": st["net"]})
                queue_message("ledger", "owner", o["id"],
                              f"Statement · {mk}", json.dumps(st, indent=1),
                              status="sent" if allowed else "draft",
                              kind="statement", month=mk)
                out["statements"] += 1
    rec = money.reconcile()
    out["reconcile"] = rec
    if rec["ok"]:
        allowed, _ = act("ledger", "draft_payment_batch", "trust",
                         {"_kind": "batch_drafted"})
        if allowed:
            b = money.draft_disbursement_batch()
            out["batch"] = b["id"] if b else None
    else:
        # A broken trust invariant freezes drafting. Silently drafting draws
        # from an unreconciled trust account is how bookkeeping software helps
        # people lose their license.
        queue_approval("ledger", "trust_alert", "trust",
                       f"TRUST OUT OF BALANCE by ${abs(rec['difference']):,.2f} — "
                       "disbursement drafting frozen",
                       {"reconcile": rec, "amount": abs(rec["difference"])},
                       "no draw is drafted from an unreconciled trust account — a human "
                       "finds the difference first")
    return out


def run_ledger():
    """The owner report fires at most once per LEDGER_CADENCE_DAYS per owner.

    It used to fire on every sweep: three sweeps meant three identical
    "30-day reports" in each owner's inbox, and an hourly runtime schedule
    would have meant twenty-four a day. The sweep being idempotent is what
    makes its schedule a free choice.
    """
    out = []
    recent_cut = now() - timedelta(days=LEDGER_CADENCE_DAYS)
    already = {m.get("to_id") for m in load("messages")
               if m.get("agent") == "ledger" and m.get("to_kind") == "owner"
               and (parse(m.get("at")) or now()) > recent_cut}
    for o in load("owners"):
        if o["id"] in already:
            continue
        rep = owner_report(o["id"])
        allowed, spec = act("ledger", "message_owner", o["id"],
                            {"_kind": "message_sent", "template": "monthly owner report",
                             "spend": rep["maintenance_spend"]})
        exposure = sum(l["exposure"] for l in rep["leases_expiring_60d"])
        queue_message("ledger", "owner", o["id"],
                      f"{rep['window_days']}-day report · {len(rep['properties'])} properties",
                      json.dumps(rep, indent=1), status="sent" if allowed else "draft")
        out.append({"owner": o["name"], "spend": rep["maintenance_spend"],
                    "avoided": rep["avoided_cost"]["value"],
                    "expiring_60d": len(rep["leases_expiring_60d"]),
                    "turnover_exposure": exposure})
    return out


# =============================================================== 7. SENTINEL

# Screened on every outbound draft. Each pattern is a real exposure, not a
# style preference — this is the layer that lets the rest of the crew run fast.
PROTECTED = ["kids", "children", "child", "family", "families", "baby", "pregnant",
             "religion", "church", "mosque", "synagogue", "race", "nationality",
             "disability", "handicap", "wheelchair", "elderly", "single mother",
             "section 8", "voucher", "immigrant", "english is", "your people"]
LEGAL_TERMS = ["evict", "eviction", "terminate your lease", "notice to quit",
               "legal action", "attorney", "court", "lien", "collections",
               "security deposit will", "withhold your deposit"]
PROMISES = ["guarantee", "guaranteed", "we promise", "will never", "always be"]


def screen(text, to_kind="tenant"):
    """Compliance screen, scoped to the AUDIENCE of the message.

    Fair-housing exposure is about statements to or about residents regarding
    protected classes; a legal notice is something served on a resident. Those
    blocks apply to resident-directed messages. Applied to everything, the
    screen blocked the monthly owner report because the owner's own legal name
    is "Nakamura Family Trust" — the substring "family" tripped the protected-
    class list, and an agent flagged a landlord's name to compliance. Business
    reporting to an owner may legitimately say "family", "eviction filed", or
    "attorney engaged"; the same words in a message to a resident are exactly
    what the screen exists to stop.

    Defaults to the strictest audience, so an unlabelled call is over-blocked
    rather than under-blocked. Overpromise stays a warning for everyone.

    A PROSPECT gets the same strictness as a resident — stricter in spirit:
    pre-tenancy is where steering and screening liability is at its maximum,
    so anything drafted to a leasing inquiry passes the full resident screen.
    """
    t = (text or "").lower()
    flags = []
    if to_kind in ("tenant", "prospect"):
        for w in PROTECTED:
            if w in t:
                flags.append({"kind": "fair_housing", "term": w, "severity": "block",
                              "why": "references or implies a protected class — "
                                     "fair-housing exposure regardless of intent"})
        for w in LEGAL_TERMS:
            if w in t:
                flags.append({"kind": "legal_notice", "term": w, "severity": "block",
                              "why": "legal notices are R0: an agent never sends these, "
                                     "and phrasing them wrong creates liability"})
    for w in PROMISES:
        if w in t:
            flags.append({"kind": "overpromise", "term": w, "severity": "warn",
                          "why": "an unconditional promise a vendor schedule cannot keep"})
    return {"clean": not any(f["severity"] == "block" for f in flags), "flags": flags}


def run_sentinel():
    out = {"messages_screened": 0, "blocked": 0, "warned": 0, "vendor_issues": []}
    msgs = load("messages")
    changed = False
    for m in msgs:
        if m.get("screened"):
            continue
        res = screen(m.get("body"), m.get("to_kind", "tenant"))
        m["screened"] = iso()
        m["screen"] = res
        out["messages_screened"] += 1
        if not res["clean"]:
            m["status"] = "blocked"
            out["blocked"] += 1
            log_event("message_blocked", m["id"], "agent:sentinel", "R3",
                      {"flags": res["flags"], "to": m["to_kind"]})
            queue_approval("sentinel", "blocked_message", m["id"],
                           f"Blocked a message to {m['to_kind']}: {m.get('subject')}",
                           {"message": m["id"], "flags": res["flags"], "body": m.get("body")},
                           "compliance block — a human decides whether to rewrite or discard")
        elif res["flags"]:
            out["warned"] += 1
        changed = True
    if changed:
        save("messages", msgs)

    for v in load("vendors"):
        exp = core.days_until(v.get("insurance_expires"))
        issues = []
        if exp is not None and exp < 0:
            issues.append(f"insurance EXPIRED {abs(exp)} days ago")
        elif exp is not None and exp < 30:
            issues.append(f"insurance expires in {exp} days")
        if not v.get("w9_on_file"):
            issues.append("no W-9 on file (1099 exposure at year end)")
        if issues:
            out["vendor_issues"].append({"vendor": v["name"], "issues": issues})
            if exp is not None and exp < 0 and v.get("active"):
                v["active"] = False
                upsert("vendors", v)
                log_event("vendor_deactivated", v["id"], "agent:sentinel", "R2",
                          {"reason": "insurance lapsed — cannot be dispatched"})
                out["reassigned"] = out.get("reassigned", 0) + _rehome(v)
    return out


def _rehome(vendor):
    """Deactivating a vendor is not enough — their OPEN jobs are still sitting
    with them. An uninsured contractor working a unit is the liability this
    whole check exists to prevent, so the open work moves with the deactivation.

    Re-routing is R2 (reversible, manager notified). If there is no insured
    alternative the job is unassigned and raised to a human rather than left
    quietly in place, because "no vendor" is a visible problem and "uninsured
    vendor" is an invisible one.
    """
    moved = 0
    for r in load("requests"):
        if r.get("vendor_id") != vendor["id"] or r.get("status") == "resolved":
            continue
        alts = [x for x in rank_vendors(r)
                if x["vendor"]["id"] != vendor["id"] and x["score"] >= 0]
        if alts:
            r["vendor_id"] = alts[0]["vendor"]["id"]
            r["assigned_at"] = iso()
            r["assignment_why"] = [f"re-routed off {vendor['name']} — insurance lapsed"] \
                + alts[0]["why"]
            log_event("vendor_swapped", r["id"], "agent:sentinel", "R2",
                      {"from": vendor["name"], "to": alts[0]["vendor"]["name"],
                       "reason": "prior vendor uninsured"})
        else:
            r["vendor_id"] = None
            r["status"] = "submitted"
            log_event("reassigned", r["id"], "agent:sentinel", "R2",
                      {"from": vendor["name"], "to": None,
                       "reason": "prior vendor uninsured and no insured alternative"})
            queue_approval("sentinel", "no_vendor", r["id"],
                           f"{r.get('title','repair')} — no insured vendor available",
                           {"request": r["id"], "dropped": vendor["name"]},
                           "the only qualified vendors are uninsured; a human must "
                           "decide whether to wait, waive, or source a new contractor")
        upsert("requests", r)
        moved += 1
    return moved


# =============================================================== driver

def run_ledger_full():
    return {"reports": run_ledger(), "money": run_money_cycle()}


# The Growth module's two agents live in pipeline.py (module boundary — see
# GROWTH_MODULE_SPEC.md); imported lazily here to avoid a circular import.
def run_scout():
    import pipeline
    return pipeline.run_scout()


def run_scribe():
    import pipeline
    return pipeline.run_scribe()


AGENTS = {"triage": run_triage, "dispatch": run_dispatch, "concierge": run_concierge,
          "steward": run_steward, "collections": run_collections,
          "retention": run_retention, "ledger": run_ledger_full,
          "scout": run_scout, "scribe": run_scribe,
          "sentinel": run_sentinel}

# Order matters: triage feeds dispatch, everything feeds sentinel, scout feeds
# scribe, and sentinel runs last so nothing this sweep produced escapes the
# screen — the growth drafts included.
ORDER = ["triage", "dispatch", "concierge", "steward", "collections",
         "retention", "ledger", "scout", "scribe", "sentinel"]


def run_all():
    return {name: AGENTS[name]() for name in ORDER}


def explain():
    print("AUTONOMY MATRIX — what runs without a human, and why\n")
    for action, spec in AUTONOMY.items():
        mark = {"R0": "propose only ", "R1": "human approves",
                "R2": "acts + tells ", "R3": "acts silently "}[spec["rung"]]
        lim = f" (limit ${spec['limit']})" if "limit" in spec else ""
        print(f"  {spec['rung']}  {mark}  {action}{lim}\n        {spec['reason']}\n")
    print("The two that never move: legal_notice and capital_recommendation stay at R0")
    print("permanently. Not because the model can't draft them — because sending an")
    print("entry notice or committing an owner's capital is not an agent's decision.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", choices=list(AGENTS))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--explain", action="store_true")
    a = ap.parse_args()
    if a.explain:
        explain()
    elif a.agent:
        print(json.dumps(AGENTS[a.agent](), indent=1)[:4000])
    elif a.all:
        res = run_all()
        if _client():
            print("Model path: " + " · ".join(f"{k}={v}" for k, v in MODELS.items()) + "\n")
        else:
            print("Model path: RULES ONLY — no API key/SDK (the deterministic floor)\n")
        for k, v in res.items():
            n = len(v) if isinstance(v, list) else v
            print(f"  {k:<10} {n if not isinstance(n, dict) else json.dumps(n)[:110]}")
        print(f"\n  automation  {core.automation_rate(load('events'))}")
    else:
        ap.print_help()
