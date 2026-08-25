#!/usr/bin/env python3
"""Property OS — the growth surfaces.

Three things, deliberately intake-shaped. Working these leads — sequences,
pipelines, outreach — belongs to the separate Growth module (see
GROWTH_MODULE_SPEC.md); this file only ever RECORDS demand and shows evidence.

  one-pager   the white-label portfolio-performance page. The best door-growth
              asset a manager has is proof the operation runs well, and this
              product manufactures that proof as a byproduct. Shared by an
              unguessable token link; rotating the token revokes every copy.
  referrals   an owner (or staff) hands us a name. Recording it is R3
              bookkeeping. CONTACTING that person is R1 forever — a referral
              is a name, not consent to be cold-called by software.
  inquiries   leasing-inquiry intake on vacant units. Recorded FIFO, worked
              FIFO, acknowledged with the identical template. There is no
              scoring, ranking, or screening of applicants anywhere in this
              codebase, permanently — prospect_score() below refuses by
              construction and the test suite pins the refusal.

WHITE-LABEL RULES FOR THE ONE-PAGER (enforced, then pinned by test)
-------------------------------------------------------------------
The page is read by a stranger the manager wants to impress. It carries the
manager's org name and portfolio-level arithmetic — and nothing else:
  - no owner names, no resident names, no vendor names, no street addresses
  - no dollar balances (trust reads "balanced to the cent" or "OUT OF
    BALANCE", never an amount — a prospect has no business seeing balances)
  - every honesty rule from the rest of the product: a figure that cannot be
    computed renders its reason, never a zero and never an estimate.
"""
import sys
import uuid
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
import money
from core import by_id, iso, load, log_event, nid, now, parse, save, store_lock

INQUIRY_STATUSES = ("new", "toured", "applied", "closed")
REFERRAL_STATUSES = ("new", "contacted", "won", "closed")
INQUIRY_DEDUPE_DAYS = 21

ACK_TEMPLATE = ("Thanks — we received your inquiry{unit_bit}. Inquiries are "
                "handled in the order they arrive, and a person will reach out "
                "to schedule a tour. If your plans change, just reply here.")


# ------------------------------------------------------------- the one-pager

def performance_onepager():
    """The portfolio's operating record, computed live, safe for a stranger.

    Every number is the same arithmetic the internal dashboards run — this is
    not a marketing rewrite of the metrics, it is the metrics with the private
    columns removed. Anything unmeasured says what it needs.
    """
    cfg = load("config") or {}
    reqs = load("requests")
    units = load("units")
    events = load("events")
    props = load("properties")
    occupied = [u for u in units if u.get("tenant_id")]

    cutoff = now() - timedelta(days=90)
    done = [r for r in reqs if r.get("status") == "resolved" and r.get("resolved_at")
            and (parse(r["resolved_at"]) or now()) >= cutoff]
    if len(done) >= 5:
        sla_hit = {"rate": round(sum(1 for r in done if not r.get("sla_breached"))
                                 / len(done), 3), "n": len(done)}
    else:
        sla_hit = {"rate": None,
                   "_missing": f"only {len(done)} resolved requests in 90 days; "
                               "need 5 to state a hit rate"}

    resolved_all = [r for r in reqs if r.get("status") == "resolved"]
    if len(resolved_all) >= 20:
        reopen = {"rate": round(sum(1 for r in resolved_all if r.get("reopened"))
                                / len(resolved_all), 3), "n": len(resolved_all)}
    else:
        reopen = {"rate": None,
                  "_missing": f"only {len(resolved_all)} resolved requests on file; "
                              "need 20 to state a reopen rate"}

    pm_cut = now() - timedelta(days=180)
    preventive = [r for r in reqs if r.get("preventive")
                  and (parse(r["submitted_at"]) or now()) >= pm_cut]

    rec = money.reconcile()

    return {
        "org": cfg.get("org", "This portfolio"),
        "generated": iso(),
        "portfolio": {
            "units": len(units), "properties": len(props),
            "occupancy": round(len(occupied) / len(units), 3) if units else None,
            "cities": sorted({p.get("city") for p in props if p.get("city")}),
        },
        "avg_resolution": core.avg_resolution_hours(reqs, 90),
        "p1_resolution": core.avg_resolution_hours(reqs, 90, "P1"),
        "sla_hit_rate": sla_hit,
        "deflection": core.deflection_savings(reqs, 90),
        "measured_vacancy": core.measured_vacancy(),
        "automation": core.automation_rate(events, 90),
        "reopen_rate": reopen,
        "preventive_orders_180d": len(preventive),
        # A prospect sees the STATE of the trust discipline, never a balance.
        "trust": {"balanced": bool(rec.get("ok")),
                  "statement": ("client trust account reconciled to the cent — "
                                "cash equals every dollar owed out of it"
                                if rec.get("ok") else
                                "trust account is OUT OF BALANCE — shown here "
                                "because hiding it would make every other number "
                                "on this page worthless")},
        "basis": "Every figure on this page is computed from recorded events at "
                 "the moment it is opened — nothing is asserted, estimated, or "
                 "hand-typed. Anything unmeasured names what it needs instead "
                 "of pretending.",
    }


def share_token():
    return ((load("config") or {}).get("share") or {}).get("performance_token")


def rotate_share_token(actor="human:mgr_1"):
    """New token, old links dead. R2: reversible by rotating again."""
    tok = "shr_" + uuid.uuid4().hex
    with store_lock():
        cfg = load("config") or {}
        cfg["share"] = {"performance_token": tok, "created": iso(),
                        "rotated_by": actor}
        save("config", cfg)
    log_event("share_link_rotated", "onepager", actor,
              "R2" if actor.startswith("agent:") else None, {})
    return tok


# --------------------------------------------------------------- referrals

def record_referral(body, source):
    """`source` is who handed us the name: 'owner:<id>' or 'human:<id>'.
    Recording is R3. Everything after recording is a human's move."""
    name = (body.get("name") or "").strip()
    contact = (body.get("contact") or "").strip()
    if not name or not contact:
        return None, "a name and a way to reach them are both required"
    row = {"id": nid("ref"), "at": iso(), "name": name[:80],
           "contact": contact[:120], "note": (body.get("note") or "")[:500],
           "source": source, "status": "new"}
    with store_lock():
        rows = load("referrals")
        rows.append(row)
        save("referrals", rows)
    log_event("referral_recorded", row["id"], source,
              "R3" if source.startswith("agent:") else None,
              {"name": row["name"], "source": source})
    return row, None


def set_referral_status(rid, status, actor="human:mgr_1"):
    if status not in REFERRAL_STATUSES:
        return None, f"status must be one of {REFERRAL_STATUSES}"
    with store_lock():
        rows = load("referrals")
        row = next((x for x in rows if x["id"] == rid), None)
        if not row:
            return None, "not found"
        row["status"] = status
        row["status_at"] = iso()
        save("referrals", rows)
    log_event("referral_status", rid, actor,
              "R2" if actor.startswith("agent:") else None, {"to": status})
    return row, None


# --------------------------------------------------------------- inquiries

def listings():
    """Vacant units in a form a stranger may see. No tenant data exists on a
    vacant unit by construction; nothing else is included."""
    out = []
    for u in load("units"):
        if u.get("tenant_id"):
            continue
        p = by_id("properties", u["property_id"]) or {}
        out.append({"unit_id": u["id"], "label": u["label"], "beds": u.get("beds"),
                    "baths": u.get("baths"), "sqft": u.get("sqft"),
                    "rent": u.get("rent"), "property": p.get("name"),
                    "city": p.get("city")})
    out.sort(key=lambda x: (x.get("rent") or 0))
    return out


def record_inquiry(body):
    """Public intake. Validated and capped like the maintenance form — an
    unauthenticated write path gets treated like one. Duplicate contact inside
    the dedupe window attaches to the existing row instead of re-queueing,
    because re-queueing would move them to the back of a FIFO line."""
    name = (body.get("name") or "").strip()
    contact = (body.get("contact") or "").strip()
    if not name or not contact:
        return {"error": "a name and a way to reach you are both required"}, 400
    unit_id = body.get("unit_id")
    unit = by_id("units", unit_id) if unit_id else None
    if unit_id and (not unit or unit.get("tenant_id")):
        return {"error": "that home is no longer available"}, 409

    with store_lock():
        rows = load("inquiries")
        cut = now() - timedelta(days=INQUIRY_DEDUPE_DAYS)
        dup = next((x for x in rows
                    if x["contact"].lower() == contact.lower()
                    and x.get("status") != "closed"
                    and (parse(x["at"]) or now()) >= cut), None)
        if dup:
            dup["messages"] = (dup.get("messages") or []) + \
                [{"at": iso(), "text": (body.get("message") or "")[:500]}]
            save("inquiries", rows)
            return {"inquiry": dup, "already_recorded": True,
                    "note": "you're already in line — your place in the queue "
                            "is kept, not reset"}, 200
        row = {"id": nid("inq"), "at": iso(), "name": name[:80],
               "contact": contact[:120], "unit_id": unit["id"] if unit else None,
               "unit": unit.get("label") if unit else None,
               "property": (by_id("properties", unit["property_id"]) or {}).get("name")
                           if unit else None,
               "move_in": (body.get("move_in") or "")[:20],
               "message": (body.get("message") or "")[:500],
               "status": "new", "messages": []}
        rows.append(row)
        save("inquiries", rows)
    log_event("inquiry_received", row["id"], f"prospect:{row['id']}", None,
              {"unit": row.get("unit"), "channel": "web"})

    # The identical templated receipt, R2. The routing goes through the same
    # act() gate and sentinel screen as every other outbound message.
    import agents
    unit_bit = f" about {row['unit']}" if row.get("unit") else ""
    allowed, _ = agents.act("concierge", "acknowledge_inquiry", row["id"],
                            {"_kind": "message_sent", "template": "inquiry ack"})
    agents.queue_message("concierge", "prospect", row["id"],
                         "We got your inquiry",
                         ACK_TEMPLATE.format(unit_bit=unit_bit),
                         status="sent" if allowed else "draft",
                         kind="inquiry_ack")
    return {"inquiry": row,
            "note": "Inquiries are handled strictly in the order received."}, 200


def inquiry_queue():
    """FIFO with the position shown. The ORDER is the fairness control: there
    is no score column because there is no score, and the position number is
    what a staff member works from."""
    rows = sorted(load("inquiries"), key=lambda x: x["at"])
    open_rows = [x for x in rows if x.get("status") != "closed"]
    for i, x in enumerate(open_rows):
        x["position"] = i + 1
    return {"queue": open_rows,
            "closed": [x for x in rows if x.get("status") == "closed"][-20:],
            "note": "worked in the order received — this product never scores, "
                    "ranks, or screens an applicant, so the position number is "
                    "the whole of the prioritisation"}


def set_inquiry_status(iid, status, actor="human:mgr_1"):
    if status not in INQUIRY_STATUSES:
        return None, f"status must be one of {INQUIRY_STATUSES}"
    with store_lock():
        rows = load("inquiries")
        row = next((x for x in rows if x["id"] == iid), None)
        if not row:
            return None, "not found"
        row["status"] = status
        row["status_at"] = iso()
        save("inquiries", rows)
    log_event("inquiry_status", iid, actor, None, {"to": status})
    return row, None


def prospect_score(*_args, **_kwargs):
    """Deliberately not implemented, permanently.

    This is a tombstone, not a stub. Scoring a housing applicant — by any
    signal this system holds or could infer — is steering/screening exposure
    the software must never carry, and 'we'll add it carefully later' is how
    it gets added. The test suite pins this refusal; removing it is a
    counsel-level decision, not a refactor.
    """
    return {"_refused": "this software does not score, rank, or screen housing "
                        "applicants. Inquiries are worked in the order received "
                        "(AUTONOMY['prospect_screening'], R0 permanently)."}
