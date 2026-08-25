#!/usr/bin/env python3
"""Property OS — server.

Serves the three apps out of app/ and a JSON API over the same store the
agents write to. Stdlib only, bound to localhost.

  GET  /api/bootstrap?role=tenant|staff|owner&id=<id>
  GET  /api/requests[?status=&priority=&property=&open=1]
  GET  /api/requests/<id>
  POST /api/requests                     tenant files one (photo optional)
  POST /api/requests/<id>/status         staff moves it along the tracker
  POST /api/requests/<id>/assign         staff picks a vendor
  POST /api/requests/<id>/schedule       tenant picks a window
  POST /api/requests/<id>/feedback       tenant rates / reopens
  GET  /api/requests/<id>/vendors        ranked bench with the reasons
  GET  /api/units/<id>/memory            what the unit knows about itself
  GET  /api/leases?days=60               the expiration tracker
  GET  /api/owner/<id>/report
  GET  /api/vendors                      bench + scorecards
  GET  /api/approvals    POST /api/approvals/<id>/decide
  GET  /api/messages     POST /api/messages/<id>/send
  GET  /api/metrics                      the honest dashboard numbers
  GET  /api/capital                      the replacement forecast
  POST /api/agents/run[?agent=]          run a sweep now
  GET  /photos/<file>

Every read that cannot be computed returns `_missing` naming what it needs
rather than a zero. The UI renders that string; it never renders a fake 0.
"""
import base64, binascii, hashlib, hmac, json, os, re, sys, threading, time, urllib.parse
from datetime import timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core, growth, money, pipeline
from core import by_id, iso, load, log_event, now, parse, save, upsert

# ---- auth (pilot-grade, single-tenant, honest about what it is) -------------
#
# Per-person access codes -> HMAC-signed session cookie. Enforced when
# PROPERTYOS_AUTH=1; off by default so the local demo stays frictionless. This
# is real enough to test role boundaries and is NOT multi-tenant SaaS auth —
# the README says so in the limits section, and that stays true until a real
# pilot forces the upgrade.
AUTH_ON = os.environ.get("PROPERTYOS_AUTH") == "1"
SESSION_HOURS = 24 * 7


def _secret():
    return (load("config") or {}).get("auth", {}).get("secret", "dev-secret")


def _sign(payload_b64):
    return hmac.new(_secret().encode(), payload_b64.encode(), hashlib.sha256).hexdigest()[:32]


def make_session(role, ident):
    payload = base64.urlsafe_b64encode(json.dumps(
        {"role": role, "id": ident, "exp": time.time() + SESSION_HOURS * 3600}
    ).encode()).decode()
    return f"{payload}.{_sign(payload)}"


def read_session(cookie_header):
    for part in (cookie_header or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k != "pos_sess" or "." not in v:
            continue
        payload, _, sig = v.rpartition(".")
        if not hmac.compare_digest(sig, _sign(payload)):
            return None
        try:
            d = json.loads(base64.urlsafe_b64decode(payload))
        except Exception:
            return None
        if d.get("exp", 0) < time.time():
            return None
        return d
    return None


def login(code):
    codes = (load("config") or {}).get("auth", {}).get("codes", {})
    h = hashlib.sha256((code or "").encode()).hexdigest()
    who = codes.get(h)
    if not who:
        return None
    return {"session": make_session(who["role"], who["id"]),
            "role": who["role"], "id": who["id"], "name": who.get("name")}

# Honour PORT so a harness (or the preview launcher) can place this on a free
# port instead of fighting for the default.
PORT = int(os.environ.get("PORT") or os.environ.get("PROPERTYOS_PORT") or 8813)
PHOTOS = core.DATA / "photos"
MAX_PHOTO_BYTES = 8 * 1024 * 1024
ALLOWED_IMAGE = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
                 "image/heic": ".heic"}
# Proof media from the vendor job card. Video gets its own (larger) cap — a
# 20-second walkthrough of a finished repair is the single best dispute-ender
# there is, and 8MB was image-sized thinking.
ALLOWED_VIDEO = {"video/mp4": ".mp4", "video/quicktime": ".mov", "video/webm": ".webm"}
MAX_VIDEO_BYTES = 60 * 1024 * 1024


# ------------------------------------------------------------------ reads

def metrics(days=90):
    reqs, units = load("requests"), load("units")
    open_reqs = core.open_requests(reqs)
    by_status = {s: sum(1 for r in reqs if r.get("status") == s) for s in core.STATUSES}
    open_by_status = {s: sum(1 for r in open_reqs if r.get("status") == s) for s in core.STATUSES}
    sla = {s: sum(1 for r in open_reqs if core.sla_state(r) == s)
           for s in ("on_track", "at_risk", "breached")}
    occupied = [u for u in units if u.get("tenant_id")]
    expiring = [u for u in occupied if (core.lease_window(u, 60) is not None)]
    return {
        "generated": iso(),
        "portfolio": {"properties": len(load("properties")), "units": len(units),
                      "occupied": len(occupied),
                      "occupancy": round(len(occupied) / len(units), 3) if units else None},
        "requests": {"total": len(reqs), "open": len(open_reqs),
                     "by_status": by_status, "open_by_status": open_by_status},
        "sla": sla,
        "avg_resolution": core.avg_resolution_hours(reqs, days),
        "avg_resolution_p1": core.avg_resolution_hours(reqs, days, "P1"),
        "deflection": core.deflection_savings(reqs, days),
        "automation": core.automation_rate(load("events"), days),
        "leases_60d": len(expiring),
        "turnover_exposure_60d": sum(agents.turn_cost(u)["total"] for u in expiring),
        "approvals_pending": sum(1 for a in load("approvals") if a.get("status") == "pending"),
        "silent_units": len(core.silent_units(units, reqs)),
        "reopen_rate": (round(sum(1 for r in reqs if r.get("reopened"))
                              / max(1, sum(1 for r in reqs if r.get("status") == "resolved")), 3)),
    }


def lease_tracker(days=60):
    reqs, surveys = load("requests"), load("surveys")
    rows = []
    for u in load("units"):
        d = core.lease_window(u, days)
        if d is None:
            continue
        t = by_id("tenants", u.get("tenant_id")) or {}
        p = by_id("properties", u["property_id"]) or {}
        risk = core.renewal_risk(u, reqs, surveys)
        rows.append({"unit_id": u["id"], "unit": u["label"], "property": p.get("name"),
                     "tenant": t.get("name"), "tenant_id": t.get("id"),
                     "ends": u["lease"]["end"][:10], "days_left": d,
                     "rent": u["rent"], "term_months": u["lease"].get("term_months"),
                     "renewal_status": u["lease"].get("renewal_status", "not_started"),
                     "risk": risk, "turn_cost": agents.turn_cost(u),
                     "drafted": bool(u.get("renewal_drafted"))})
    rows.sort(key=lambda r: r["days_left"])
    return rows


class Lookup:
    """One pass over each table per HTTP request instead of one per row.

    enrich() used to call load() per request, which meant a 400-row board
    re-read the whole 6,600-row event log 400 times and the page never
    finished loading. Build the indexes once and hand them down.
    """

    def __init__(self, want_events=False):
        self.units = {u["id"]: u for u in load("units")}
        self.props = {p["id"]: p for p in load("properties")}
        self.tenants = {t["id"]: t for t in load("tenants")}
        self.vendors = {v["id"]: v for v in load("vendors")}
        self.events = {}
        if want_events:
            for e in load("events"):
                self.events.setdefault(e.get("subject"), []).append(e)
            for evs in self.events.values():
                evs.sort(key=lambda e: e["at"])


def enrich(r, lk=None, timeline=False):
    """`timeline` is opt-in: a list view never needs the per-row event history,
    and attaching it is what made the board slow enough to look broken."""
    lk = lk or Lookup(want_events=timeline)
    u = lk.units.get(r.get("unit_id")) or {}
    p = lk.props.get(r.get("property_id")) or {}
    t = lk.tenants.get(r.get("tenant_id")) or {}
    v = lk.vendors.get(r.get("vendor_id")) or {}
    out = {**r, "unit": u.get("label"), "property": p.get("name"),
           "tenant": t.get("name"), "tenant_phone": t.get("phone"),
           "vendor": v.get("name"), "vendor_phone": v.get("phone"),
           "sla_state": core.sla_state(r),
           "availability_view": core.availability_state(r),
           "priority_label": core.PRIORITIES.get(r.get("priority"), {}).get("label"),
           "age_hours": round(core.hours_between(r["submitted_at"], iso()) or 0, 1)}
    if timeline:
        out["timeline"] = lk.events.get(r["id"], [])
    return out


def bootstrap(role, ident):
    if role == "tenant":
        t = by_id("tenants", ident) or (load("tenants") or [{}])[0]
        if not t:
            return {"error": "no tenants"}
        u = by_id("units", t.get("unit_id")) or {}
        p = by_id("properties", u.get("property_id")) or {}
        lk = Lookup(want_events=False)
        mine = [enrich(r, lk) for r in load("requests") if r.get("tenant_id") == t["id"]]
        mine.sort(key=lambda r: r["submitted_at"], reverse=True)
        msgs = [m for m in load("messages")
                if m.get("to_kind") == "tenant" and m.get("to_id") == t["id"]
                and m.get("status") == "sent"]
        msgs.sort(key=lambda m: m["at"], reverse=True)
        pays = sorted((x for x in load("payments") if x["tenant_id"] == t["id"]),
                      key=lambda x: x["at"], reverse=True)
        return {"role": "tenant", "tenant": t, "unit": u, "property": p,
                "requests": mine, "messages": msgs[:20],
                "rent": {**money.tenant_balance(t["id"]),
                         "recent_payments": pays[:4],
                         "deposit_held": money.deposit_held(t["id"]),
                         "note": "This app records rent, it never charges your account. "
                                 "Pay by ACH or check as usual — what you see here is "
                                 "the office's ledger of what arrived."},
                "lease_days_left": core.days_until(u.get("lease", {}).get("end")),
                "self_fix_catalog": core.SELF_FIX,
                "categories": {k: {"trade": v["trade"], "priority": v["priority"]}
                               for k, v in core.CATEGORIES.items()},
                "emergency_line": (load("config") or {}).get("after_hours_emergency_line")}
    if role == "owner":
        o = by_id("owners", ident) or (load("owners") or [{}])[0]
        tok = growth.share_token()
        return {"role": "owner", "owner": o, "report": agents.owner_report(o["id"]),
                "statement": money.owner_statement(o["id"]),
                "leases": [l for l in lease_tracker(60)
                           if (by_id("properties",
                                     (by_id("units", l["unit_id"]) or {}).get("property_id")) or {}
                               ).get("owner_id") == o["id"]],
                "metrics": metrics(),
                # The referral hook: this owner's own referrals back, plus the
                # shareable performance page — the thing they forward.
                "share_url": f"/pitch?t={tok}" if tok else None,
                "my_referrals": sorted((r for r in load("referrals")
                                        if r.get("source") == f"owner:{o['id']}"),
                                       key=lambda r: r["at"], reverse=True)}
    lk = Lookup(want_events=False)
    # Every open request, always — plus a recent tail of resolved ones for
    # context. A blind [-400:] slice silently dropped open requests off the
    # board, so the header count and the table disagreed.
    allr = load("requests")
    open_r = [r for r in allr if r.get("status") != "resolved"]
    closed = sorted((r for r in allr if r.get("status") == "resolved"),
                    key=lambda r: r.get("resolved_at") or r["submitted_at"], reverse=True)[:300]
    board_rows = sorted(open_r + closed, key=lambda r: r["submitted_at"], reverse=True)
    tok = growth.share_token()
    return {"role": "staff", "config": load("config"), "metrics": metrics(),
            "requests": [enrich(r, lk) for r in board_rows],
            "properties": load("properties"), "vendors": vendor_bench(),
            "approvals": [a for a in load("approvals") if a.get("status") == "pending"],
            "leases": lease_tracker(60), "owners": load("owners"),
            "autonomy": core.AUTONOMY,
            "leads": {"inquiries": growth.inquiry_queue(),
                      "referrals": sorted(load("referrals"),
                                          key=lambda r: r["at"], reverse=True),
                      "share_url": f"/pitch?t={tok}" if tok else None}}


def vendor_bench():
    reqs = load("requests")
    out = []
    for v in load("vendors"):
        sc = core.vendor_scorecard(v, reqs)
        out.append({**v, "scorecard": sc,
                    "insurance_days": core.days_until(v.get("insurance_expires")),
                    "recent_reviews": core.vendor_recent_reviews(v["id"], reqs),
                    "open_jobs": sum(1 for r in reqs if r.get("vendor_id") == v["id"]
                                     and r.get("status") != "resolved")})
    out.sort(key=lambda v: -(v["scorecard"].get("score") or -1))
    return out


# ------------------------------------------------------------------ writes

def create_request(body):
    tid = body.get("tenant_id")
    t = by_id("tenants", tid)
    if not t:
        return {"error": "unknown tenant"}, 400
    u = by_id("units", t["unit_id"]) or {}
    text = (body.get("description") or "").strip()
    if not text:
        return {"error": "description is required"}, 400

    photos = []
    for ph in (body.get("photos") or [])[:4]:
        saved = save_photo(ph)
        if saved:
            photos.append(saved)

    tri = core.classify(text, bool(photos), body.get("answers"))
    if t.get("vulnerable_occupant") and tri["priority"] == "P2":
        tri["priority"] = "P1"
        tri["reasons"].append("infant / elderly / medical occupant on file")

    r = {"id": core.nid("req"), "unit_id": u.get("id"), "property_id": u.get("property_id"),
         "tenant_id": t["id"], "title": text[:70], "description": text,
         "category": tri["category"], "priority": tri["priority"], "status": "submitted",
         "submitted_at": iso(), "channel": body.get("channel", "app"),
         "photos": photos, "triage": tri, "triage_final": False,
         "entry_permission": body.get("entry_permission", "appointment"),
         "entry_notes": body.get("entry_notes", ""), "pets": bool(body.get("pets")),
         "preferred_windows": body.get("preferred_windows") or [],
         "answers": body.get("answers") or {}}
    # Availability: the resident's stated windows, TIMESTAMPED — a statement,
    # never a standing consent (core.availability_state ages it out at 14d).
    # The UI only asks when it can matter (not "anytime", not a P1) — but if
    # windows arrive anyway, the truth is kept.
    ws = [str(w).strip().replace('"', '').replace("'", "")[:60]
          for w in (body.get("availability_windows") or body.get("preferred_windows") or [])[:4]
          if str(w).strip()]
    r["availability"] = {"windows": ws, "stated_at": iso()} if ws else None
    comp = next((c for c in load("components")
                 if c["unit_id"] == u.get("id")
                 and c["kind"] == core.CATEGORIES[tri["category"]]["component"]), None)
    r["component_id"] = comp["id"] if comp else None
    r.update(core.sla_due(r))
    upsert("requests", r)
    log_event("submitted", r["id"], f"tenant:{t['id']}", None,
              {"channel": r["channel"], "photos": len(photos),
               "provisional_priority": tri["priority"]})

    # Deterministic triage has already run — a P1 is routed on the way in, not
    # on the next agent sweep. An emergency must never wait for a batch job.
    if tri["priority"] == "P1":
        agents.run_triage(limit=3)
        agents.run_dispatch()
        r = by_id("requests", r["id"])
    fix = core.CATEGORIES[tri["category"]]["self_fix"]
    return {"request": enrich(r, timeline=True), "self_fix": core.SELF_FIX.get(fix) if fix else None,
            "sla": core.PRIORITIES[tri["priority"]]}, 200


def save_photo(ph):
    """Accepts {media_type, data(base64)} or a data: URL. Rejects anything that
    is not a recognised image type or is over the cap — an intake form is an
    unauthenticated write path and gets treated like one.
    """
    if isinstance(ph, str) and ph.startswith("data:"):
        head, _, b64 = ph.partition(",")
        media = head[5:].split(";")[0]
        ph = {"media_type": media, "data": b64}
    if not isinstance(ph, dict):
        return None
    media = ph.get("media_type")
    if media not in ALLOWED_IMAGE:
        return None
    try:
        raw = base64.b64decode(ph.get("data", ""), validate=True)
    except (binascii.Error, ValueError):
        return None
    if not raw or len(raw) > MAX_PHOTO_BYTES:
        return None
    PHOTOS.mkdir(parents=True, exist_ok=True)
    name = core.nid("img") + ALLOWED_IMAGE[media]
    (PHOTOS / name).write_bytes(raw)
    return {"file": name, "media_type": media, "bytes": len(raw)}


def save_media(ph):
    """save_photo, widened for vendor proof: images OR video, each against its
    own cap. Same treatment of the input as an unauthenticated write path."""
    if isinstance(ph, str) and ph.startswith("data:"):
        head, _, b64 = ph.partition(",")
        ph = {"media_type": head[5:].split(";")[0], "data": b64}
    if not isinstance(ph, dict):
        return None
    media = ph.get("media_type")
    if media in ALLOWED_IMAGE:
        ext, cap, kind, prefix = ALLOWED_IMAGE[media], MAX_PHOTO_BYTES, "photo", "img"
    elif media in ALLOWED_VIDEO:
        ext, cap, kind, prefix = ALLOWED_VIDEO[media], MAX_VIDEO_BYTES, "video", "vid"
    else:
        return None
    try:
        raw = base64.b64decode(ph.get("data", ""), validate=True)
    except (binascii.Error, ValueError):
        return None
    if not raw or len(raw) > cap:
        return None
    PHOTOS.mkdir(parents=True, exist_ok=True)
    name = core.nid(prefix) + ext
    (PHOTOS / name).write_bytes(raw)
    return {"file": name, "media_type": media, "bytes": len(raw), "kind": kind}


def set_status(rid, body):
    r = by_id("requests", rid)
    if not r:
        return {"error": "not found"}, 404
    new = body.get("status")
    if new not in core.STATUSES:
        return {"error": f"status must be one of {core.STATUSES}"}, 400
    actor = body.get("actor", "human:mgr_1")
    prev = r.get("status")
    r["status"] = new
    stamp = {"assigned": "assigned_at", "in_progress": "started_at", "resolved": "resolved_at"}
    if new in stamp:
        r[stamp[new]] = iso()
    if new == "resolved":
        r["resolution_kind"] = body.get("resolution_kind", "fixed")
        r["resolution_note"] = body.get("note", "")
        r["actual_cost"] = body.get("cost", r.get("actual_cost"))
        r["sla_breached"] = bool(r.get("resolve_by")) and parse(r["resolved_at"]) > parse(r["resolve_by"])
        r["checkback_sent"] = False   # arm the 48h check-back
        r["stall_reason"] = None
    if body.get("quote") is not None:
        # Staff recording the vendor's quote. The next dispatch sweep runs the
        # spend decision against it — standing limit for routine, emergency
        # authority for a P1.
        r["quote"] = int(body["quote"]) or None
        r["spend_decided"] = False
    if body.get("stall_reason") is not None:
        r["stall_reason"] = body["stall_reason"] or None
        r["stall_since"] = iso() if body["stall_reason"] else None
        r["status_note_sent"] = False
    upsert("requests", r)
    log_event(new if new != "in_progress" else "started", rid, actor, None,
              {"from": prev, "to": new, "note": body.get("note", "")})
    return {"request": enrich(r, timeline=True)}, 200


def assign(rid, body):
    r = by_id("requests", rid)
    v = by_id("vendors", body.get("vendor_id"))
    if not r or not v:
        return {"error": "not found"}, 404
    prev = r.get("vendor_id")
    r["vendor_id"] = v["id"]
    r["assigned_at"] = iso()
    if r["status"] == "submitted":
        r["status"] = "assigned"
    upsert("requests", r)
    log_event("reassigned" if prev else "assigned", rid,
              body.get("actor", "human:mgr_1"), None,
              {"vendor": v["name"], "manual_override": True,
               "previous": (by_id("vendors", prev) or {}).get("name")})
    return {"request": enrich(r, timeline=True)}, 200


def feedback(rid, body):
    r = by_id("requests", rid)
    if not r:
        return {"error": "not found"}, 404
    if body.get("rating"):
        r["tenant_rating"] = max(1, min(5, int(body["rating"])))
        r["rated_at"] = iso()
    if body.get("comment"):
        r["tenant_comment"] = body["comment"][:1000]
    if body.get("still_broken"):
        # The single most important write in the product. "Resolved" that the
        # resident disputes is not resolved, and reopening the ORIGINAL ticket
        # (rather than making them file a new one) is what keeps the vendor
        # scorecard and the resolution-time average honest.
        r["reopened"] = True
        # Back to the vendor who was on it — but a request that was never
        # dispatched (a self-fix the resident tried and it didn't work) has no
        # vendor to return to. Marking THAT 'assigned' strands it: dispatch only
        # picks up 'submitted', so the row would sit with no vendor forever.
        r["status"] = "assigned" if r.get("vendor_id") else "submitted"
        r["triage_final"] = bool(r.get("vendor_id"))   # re-triage a never-dispatched job
        if r.get("self_fix_offered"):
            # The resident tried the guided fix and it did not work. Record that
            # and clear the flag: leaving it set makes dispatch skip the request
            # forever, and re-offering the same card is the worst thing the
            # product could do to someone who just told us it failed.
            r["self_fix_failed"] = r.pop("self_fix_offered")
        r["resolution_kind"] = None
        r["resolved_at"] = None
        r["reopened_at"] = iso()
        r.update(core.sla_due({**r, "submitted_at": iso()}))
        log_event("reopened", rid, f"tenant:{r.get('tenant_id')}", None,
                  {"reason": body.get("comment", "tenant says it is not fixed"),
                   "vendor": (by_id("vendors", r.get("vendor_id")) or {}).get("name")})
    else:
        log_event("feedback", rid, f"tenant:{r.get('tenant_id')}", None,
                  {"rating": r.get("tenant_rating")})
    upsert("requests", r)
    return {"request": enrich(r, timeline=True)}, 200


def schedule(rid, body):
    r = by_id("requests", rid)
    if not r:
        return {"error": "not found"}, 404
    if body.get("accept_proposed") is not None:
        # the resident answering a vendor's outside-window proposal
        pw = (r.get("proposed_window") or {}).get("window")
        if body["accept_proposed"] and pw:
            r["scheduled_for"] = pw
            log_event("scheduled", rid, f"tenant:{r.get('tenant_id')}", None,
                      {"window": pw, "chosen_by": "tenant", "accepted_proposal": True})
        else:
            log_event("schedule_declined", rid, f"tenant:{r.get('tenant_id')}", None,
                      {"window": pw, "note": "the resident said no — nothing was booked"})
        r["proposed_window"] = None
        upsert("requests", r)
        return {"request": enrich(r, timeline=True)}, 200
    if body.get("availability_windows") is not None:
        # restating availability re-stamps the clock — a fresh statement
        ws = [str(w).strip().replace('"', '').replace("'", "")[:60]
              for w in (body.get("availability_windows") or [])[:4] if str(w).strip()]
        r["availability"] = {"windows": ws, "stated_at": iso()} if ws else None
        log_event("availability_stated", rid, f"tenant:{r.get('tenant_id')}", None,
                  {"windows": ws})
    if body.get("window"):
        r["scheduled_for"] = body.get("window")
        log_event("scheduled", rid, f"tenant:{r.get('tenant_id')}", None,
                  {"window": body.get("window"), "chosen_by": "tenant"})
    r["entry_permission"] = body.get("entry_permission", r.get("entry_permission"))
    upsert("requests", r)
    return {"request": enrich(r, timeline=True)}, 200


def decide_approval(aid, body):
    rows = load("approvals")
    for a in rows:
        if a["id"] != aid:
            continue
        a["status"] = "approved" if body.get("approve") else "declined"
        a["decided_at"] = iso()
        a["decided_by"] = body.get("actor", "human:mgr_1")
        a["note"] = body.get("note", "")
        save("approvals", rows)
        log_event("approval_" + a["status"], a["subject"], a["decided_by"], None,
                  {"kind": a["kind"], "agent": a["agent"]})
        if a["kind"] == "spend" and a["status"] == "approved":
            r = by_id("requests", a["subject"])
            if r:
                r["spend_approved"] = True
                if r.get("stall_reason") == "awaiting_owner_approval":
                    # The thing it was waiting on just happened. Leaving the
                    # stall flag set kept "awaiting owner approval" on the
                    # board after the owner had approved it.
                    r["stall_reason"] = None
                    r["stall_since"] = None
                upsert("requests", r)
        return {"approval": a}, 200
    return {"error": "not found"}, 404


def send_message(mid, body):
    rows = load("messages")
    for m in rows:
        if m["id"] != mid:
            continue
        if m.get("status") == "blocked":
            return {"error": "blocked by compliance screen — rewrite it first",
                    "flags": m.get("screen", {}).get("flags")}, 409
        if body.get("body"):
            m["body"] = body["body"]
            res = agents.screen(m["body"], m.get("to_kind", "tenant"))
            m["screen"] = res
            if not res["clean"]:
                m["status"] = "blocked"
                save("messages", rows)
                return {"error": "edit reintroduced a compliance flag",
                        "flags": res["flags"]}, 409
        m["status"] = "sent"
        m["sent_at"] = iso()
        m["sent_by"] = body.get("actor", "human:mgr_1")
        save("messages", rows)
        log_event("message_sent", m.get("request_id") or m["id"],
                  m["sent_by"], None, {"to": m["to_kind"], "agent_drafted": m["agent"]})
        return {"message": m}, 200
    return {"error": "not found"}, 404


# ------------------------------------------------------------------ turnover

def open_turnover(body):
    u = by_id("units", body.get("unit_id"))
    if not u:
        return {"error": "unknown unit"}, 404
    rows = load("turnovers")
    if any(t["unit_id"] == u["id"] and t["state"] != "leased" for t in rows):
        return {"error": "a turnover is already open for this unit"}, 409
    t = {"id": core.nid("trn"), "unit_id": u["id"], "property_id": u["property_id"],
         "tenant_id": u.get("tenant_id"), "state": "notice", "opened_at": iso(),
         "moveout_date": body.get("moveout_date"), "tasks": [], "history": [
             {"state": "notice", "at": iso()}]}
    rows.append(t)
    save("turnovers", rows)
    agents.act("staff-api", "open_turnover", t["id"],
               {"_kind": "turnover_advanced", "to": "notice", "unit": u["label"]})
    return {"turnover": t}, 200


def advance_turnover(tid, body):
    rows = load("turnovers")
    t = next((x for x in rows if x["id"] == tid), None)
    if not t:
        return {"error": "not found"}, 404
    states = list(core.TURNOVER_STATES)
    cur, to = states.index(t["state"]), body.get("state")
    if to not in states or states.index(to) != cur + 1:
        return {"error": f"turnover moves one state at a time: next is "
                         f"'{states[cur + 1] if cur + 1 < len(states) else 'done'}'"}, 400
    u = by_id("units", t["unit_id"]) or {}

    if to == "inspected":
        t["moved_out"] = body.get("moved_out") or iso()
        t["inspection_note"] = body.get("note", "")
        # The deposit itemization is a legal document on a statutory clock —
        # R0: drafted with the evidence attached, a human sends it.
        held = money.deposit_held(t.get("tenant_id"))
        agents.act("staff-api", "deposit_disposition", t["id"],
                   {"_kind": "deposit_disposition_drafted", "held": held})
        agents.queue_approval("retention", "deposit_disposition", t["id"],
            f"Deposit disposition · {u.get('label')} — ${held:,.0f} held (R0, statutory clock)",
            {"turnover": t["id"], "unit_label": u.get("label"), "amount": held,
             "property": (by_id("properties", t.get("property_id")) or {}).get("name"),
             "inspection_note": t.get("inspection_note", ""),
             "draft": "Itemization draft: deposit held vs. documented damages beyond "
                      "normal wear (see inspection note + unit photo history). "
                      "STATE TIMELINES APPLY — counsel-reviewed template required "
                      "before any real send."},
            "a deposit itemization is a legal document with a statutory deadline — "
            "drafted with the evidence, sent by a human, forever")
    elif to == "make_ready":
        made = []
        for title, cat, est in core.MAKEREADY_TEMPLATE:
            r = {"id": core.nid("req"), "unit_id": u["id"], "property_id": u.get("property_id"),
                 "tenant_id": None, "title": f"Make-ready: {title}",
                 "description": f"Turnover {t['id']} make-ready task: {title}",
                 "category": cat, "priority": "P3", "status": "submitted",
                 "submitted_at": iso(), "channel": "turnover", "photos": [],
                 "triage_final": True, "turnover_id": t["id"],
                 "triage": {"category": cat, "priority": "P3", "confidence": 1.0,
                            "source": "make-ready-template", "est_cost": est,
                            "reasons": ["make-ready checklist"]}}
            r.update(core.sla_due(r))
            upsert("requests", r)
            made.append(r["id"])
        t["tasks"] = made
        agents.act("staff-api", "create_makeready_tasks", t["id"],
                   {"_kind": "turnover_advanced", "to": to, "tasks": len(made)})
    elif to == "leased":
        t["new_lease_start"] = body.get("new_lease_start") or iso()
        if t.get("moved_out"):
            t["vacancy_days"] = max(0, (parse(t["new_lease_start"]) - parse(t["moved_out"])).days)

    t["state"] = to
    t["history"].append({"state": to, "at": iso()})
    save("turnovers", rows)
    if to not in ("inspected", "make_ready"):
        log_event("turnover_advanced", t["id"], body.get("actor", "human:mgr_1"), None,
                  {"to": to, "unit": u.get("label")})
    return {"turnover": t}, 200


# ------------------------------------------------------------------ money api

def money_summary():
    rec = money.reconcile()
    b = money.balances()
    return {"reconcile": rec,
            "trust_cash": b.get("trust_cash", 0),
            "operating_cash": b.get("operating_cash", 0),
            "delinquency": money.delinquency(),
            "batches": load("batches")[-5:],
            "measured_vacancy": core.measured_vacancy(),
            "note": "This system accounts for money and drafts movement. It cannot "
                    "execute a transfer — a human does that at the bank and records it."}


def record_payment_api(body):
    p = money.record_payment(body.get("tenant_id"), body.get("amount", 0),
                             body.get("method", "ach"),
                             actor=body.get("actor", "human:mgr_1"))
    return ({"payment": p}, 200) if p else ({"error": "unknown tenant or bad amount"}, 400)


# ------------------------------------------------------------------ vendor job

def job_payload(token):
    r = next((x for x in load("requests") if x.get("vendor_token") == token), None)
    if not r:
        return None
    v = by_id("vendors", r.get("vendor_id")) or {}
    u = by_id("units", r.get("unit_id")) or {}
    prop = by_id("properties", r.get("property_id")) or {}
    mem = agents.unit_memory(u.get("id")) if u else {}
    return {"request": {k: r.get(k) for k in
                        ("id", "title", "description", "priority", "status", "category",
                         "entry_permission", "entry_notes", "pets", "scheduled_for",
                         "quote", "invoice_amount", "vendor_accepted", "photos")},
            "availability": core.availability_state(r),
            "proposed_window": (r.get("proposed_window") or {}).get("window"),
            "triage": {k: (r.get("triage") or {}).get(k)
                       for k in ("likely_cause", "parts_to_bring")},
            "unit": u.get("label"), "property": prop.get("name"),
            "address": prop.get("address"),
            "vendor": v.get("name"),
            "history": (mem or {}).get("history_lines", [])[:6],
            "note": "This link is your job card. No login — the link itself is the key; "
                    "don't forward it."}


def job_action(token, action, body):
    with core.store_lock():
        reqs = load("requests")
        r = next((x for x in reqs if x.get("vendor_token") == token), None)
        if not r:
            return {"error": "unknown job link"}, 404
        vid = r.get("vendor_id", "unknown")
        actor = f"vendor:{vid}"
        decline_out = None
        if action == "accept":
            r["vendor_accepted"] = iso()
            log_event("job_accepted", r["id"], actor, None,
                      {"eta": body.get("eta", "")})
        elif action == "decline":
            if r.get("status") in ("in_progress", "resolved"):
                return {"error": "work already started — call the office instead"}, 400
            reason = (body.get("reason") or "")[:200]
            log_event("job_declined", r["id"], actor, None, {"reason": reason})
            # instant re-dispatch to the runner-up; rotates the job link, so
            # this token is dead the moment the decline lands
            decline_out = agents.redispatch_after_decline(r, reason)
        elif action == "schedule":
            w = (body.get("window") or "").strip()
            if not w:
                return {"error": "a time window is required"}, 400
            if core.window_match(w, r):
                # both parties already said yes: the resident stated this
                # window, the vendor picked it verbatim — confirm instantly
                r["scheduled_for"] = w
                r["proposed_window"] = None
                log_event("scheduled", r["id"], actor, None,
                          {"window": w, "chosen_by": "vendor", "in_resident_window": True,
                           "auto_confirmed": True,
                           "why": core.AUTONOMY["confirm_schedule_in_window"]["reason"]})
            else:
                # a window the resident never offered (or one gone stale) is a
                # QUESTION — nothing is scheduled until they answer it
                r["proposed_window"] = {"window": w, "by": actor, "at": iso()}
                log_event("schedule_proposed", r["id"], actor, None,
                          {"window": w, "in_resident_window": False,
                           "availability_state": core.availability_state(r)["state"],
                           "why": core.AUTONOMY["propose_schedule_outside_window"]["reason"]})
        elif action == "start":
            r["status"] = "in_progress"
            r["started_at"] = r.get("started_at") or iso()
            log_event("started", r["id"], actor, None, {})
        elif action == "complete":
            photos = []
            for ph in (body.get("photos") or [])[:6]:
                sp = save_media(ph)
                if sp:
                    sp["proof"] = True
                    photos.append(sp)
            # No proof, no close — from the vendor card. (Staff can still
            # resolve manually via /status; that override carries their name.)
            if not photos:
                return {"error": "proof closes the job — attach at least one photo or "
                                 "video of the finished work. It protects you when the "
                                 "48-hour check-back asks the resident if it's fixed."}, 400
            r["proof_photos"] = (r.get("proof_photos") or []) + photos
            r["status"] = "resolved"
            r["resolved_at"] = iso()
            r["resolution_kind"] = "fixed"
            r["resolution_note"] = body.get("note", "")[:500]
            r["sla_breached"] = bool(r.get("resolve_by")) and                 parse(r["resolved_at"]) > parse(r["resolve_by"])
            r["checkback_sent"] = False
            r["stall_reason"] = None
            log_event("job_completed", r["id"], actor, None,
                      {"proof_photos": len(photos), "note": body.get("note", "")[:80]})
        elif action == "invoice":
            try:
                amt = round(float(body.get("amount", 0)), 2)
            except (TypeError, ValueError):
                return {"error": "a numeric invoice amount is required"}, 400
            if amt <= 0:
                return {"error": "a numeric invoice amount is required"}, 400
            r["invoice_amount"] = amt
            m = money.match_invoice(r, amt)
            r["invoice_match"] = m
            if m["match"]:
                r["actual_cost"] = amt
                log_event("invoice_matched", r["id"], "agent:dispatch", "R2",
                          {"invoice": amt, "quote": m["quote"], "drift_pct": m.get("drift_pct")})
            else:
                log_event("invoice_review_queued", r["id"], "agent:dispatch", "R1",
                          {"invoice": amt, "reason": m["reason"]})
                agents.queue_approval("dispatch", "invoice_review", r["id"],
                    f"${amt} invoiced — {m['reason']}",
                    {"request": r["id"], "amount": amt, "invoice": amt,
                     "quote": m.get("quote"), "drift_pct": m.get("drift_pct"),
                     "property": (by_id("properties", r.get("property_id")) or {}).get("name"),
                     "anomaly": r.get("price_anomaly")},
                    "the invoice does not match the approved quote — a human settles "
                    "the difference before it is paid")
        else:
            return {"error": "unknown action"}, 400
        for i, x in enumerate(reqs):
            if x["id"] == r["id"]:
                reqs[i] = r
        save("requests", reqs)
    if action == "decline":
        return {"job": None, "closed": True,
                "note": "No problem — this job has been passed along and this link is now "
                        "closed. Thanks for the quick answer; a fast no keeps you high on "
                        "the bench."}, 200
    return {"job": job_payload(token)}, 200


# ------------------------------------------------------------------ http

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT / "app"), **k)

    def send_api(self, obj, code=200):
        raw = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def body_json(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return {}

    @property
    def q(self):
        return {k: v[0] for k, v in
                urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).items()}

    def gate(self, path, method="GET"):
        """Role gate, enforced when PROPERTYOS_AUTH=1.

        Job links (/api/job/*) and pitch links (/api/pitch/*) pass — the token
        IS the credential, scoped to one work order / one read-only page.
        Listings and inquiry SUBMISSION are public by design: they are the
        storefront, and a prospect has no account. Login passes. Everything
        else needs a session; staff sees all, tenant and owner get their
        identity FORCED to their session (the ?id= parameter stops being
        trusted the moment auth is on).
        """
        if not AUTH_ON:
            return None
        if path.startswith(("/api/auth/", "/api/job/", "/api/pitch/")):
            return None
        if path == "/api/listings":
            return None
        if path == "/api/inquiries" and method == "POST":
            return None                      # the public intake; reads stay gated
        if not path.startswith("/api/"):
            return None                      # static shell is public; data is not
        sess = read_session(self.headers.get("Cookie"))
        if not sess:
            return {"error": "login required"}, 401
        self.session = sess
        if sess["role"] == "staff":
            return None
        # an owner may hand us a referral; they may not read the referral book
        if sess["role"] == "owner" and path == "/api/referrals" and method == "POST":
            return None
        # tenants and owners: reads of their own bootstrap + tenant actions only
        allowed_prefixes = {"tenant": ("/api/bootstrap", "/api/requests"),
                            "owner": ("/api/bootstrap", "/api/owner/")}
        if not path.startswith(allowed_prefixes.get(sess["role"], ())):
            return {"error": f"forbidden for role {sess['role']}"}, 403
        return None

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        self.session = None
        denied = self.gate(path, "GET")
        if denied:
            return self.send_api(*denied)
        if path == "/job" or path == "/job/":
            self.path = "/job.html"
            return super().do_GET()
        if path in ("/pitch", "/pitch/"):
            self.path = "/pitch.html"
            return super().do_GET()
        if path in ("/inquire", "/inquire/"):
            self.path = "/inquire.html"
            return super().do_GET()
        if path in ("/growth", "/growth/"):
            self.path = "/growth.html"
            return super().do_GET()
        if path.startswith("/photos/"):
            name = Path(path).name
            f = PHOTOS / name
            if not f.is_file() or f.parent != PHOTOS:
                return self.send_error(404)
            raw = f.read_bytes()
            mime = {".jpg": "image/jpeg", ".png": "image/png",
                    ".webp": "image/webp", ".heic": "image/heic",
                    ".mp4": "video/mp4", ".mov": "video/quicktime",
                    ".webm": "video/webm"}.get(f.suffix, "application/octet-stream")
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            return self.wfile.write(raw)

        if not path.startswith("/api/"):
            if path == "/":
                self.path = "/index.html"
            return super().do_GET()

        q = self.q
        if path == "/api/bootstrap":
            role, ident = q.get("role", "staff"), q.get("id")
            if AUTH_ON and self.session and self.session["role"] != "staff":
                # A logged-in resident or owner is themselves, whatever the URL says.
                role, ident = self.session["role"], self.session["id"]
            return self.send_api(bootstrap(role, ident))
        if path == "/api/notice":
            # A dataset can carry a banner about itself — set by an importer when
            # some of the portfolio is illustrative rather than the operator's own.
            return self.send_api({"notice": (load("config", {}) or {}).get("notice")})
        if path == "/api/metrics":
            return self.send_api(metrics(int(q.get("days", 90))))
        if path == "/api/leases":
            return self.send_api(lease_tracker(int(q.get("days", 60))))
        if path == "/api/vendors":
            return self.send_api(vendor_bench())
        if path == "/api/approvals":
            return self.send_api([a for a in load("approvals")
                                  if q.get("all") or a.get("status") == "pending"])
        if path == "/api/messages":
            rows = load("messages")
            if q.get("status"):
                rows = [m for m in rows if m.get("status") == q["status"]]
            return self.send_api(rows[-200:])
        if path == "/api/capital":
            return self.send_api(load("capital_forecast", {}))
        if path == "/api/auth/me":
            return self.send_api(read_session(self.headers.get("Cookie"))
                                 or {"role": None, "auth_enforced": AUTH_ON})
        if path == "/api/money/summary":
            return self.send_api(money_summary())
        if path == "/api/turnovers":
            return self.send_api(load("turnovers"))
        if path == "/api/listings":
            return self.send_api(growth.listings())
        if path == "/api/pipeline":
            return self.send_api(pipeline.pipeline_read())
        if path == "/api/inquiries":
            return self.send_api(growth.inquiry_queue())
        if path == "/api/referrals":
            return self.send_api(sorted(load("referrals"),
                                        key=lambda r: r["at"], reverse=True))
        m = re.match(r"^/api/pitch/([A-Za-z0-9_]+)$", path)
        if m:
            tok = growth.share_token()
            if not tok or not hmac.compare_digest(m.group(1), tok):
                return self.send_api({"error": "unknown or revoked link"}, 404)
            return self.send_api(growth.performance_onepager())
        m = re.match(r"^/api/job/([A-Za-z0-9_]+)$", path)
        if m:
            j = job_payload(m.group(1))
            return self.send_api(j or {"error": "unknown job link"}, 200 if j else 404)
        m = re.match(r"^/api/owner/([a-z0-9_]+)/statement$", path)
        if m:
            st = money.owner_statement(m.group(1), self.q.get("month"))
            return self.send_api(st or {"error": "not found"}, 200 if st else 404)
        if path == "/api/requests":
            rows = load("requests")
            if q.get("open"):
                rows = core.open_requests(rows)
            for k in ("status", "priority", "category"):
                if q.get(k):
                    rows = [r for r in rows if r.get(k) == q[k]]
            if q.get("property"):
                rows = [r for r in rows if r.get("property_id") == q["property"]]
            rows.sort(key=lambda r: r["submitted_at"], reverse=True)
            rows = rows[:int(q.get("limit", 300))]
            lk = Lookup(want_events=False)
            return self.send_api([enrich(r, lk) for r in rows])
        m = re.match(r"^/api/requests/([a-z0-9_]+)$", path)
        if m:
            r = by_id("requests", m.group(1))
            return self.send_api(enrich(r, timeline=True) if r else {"error": "not found"},
                                 200 if r else 404)
        m = re.match(r"^/api/requests/([a-z0-9_]+)/vendors$", path)
        if m:
            r = by_id("requests", m.group(1))
            if not r:
                return self.send_api({"error": "not found"}, 404)
            return self.send_api([{"vendor_id": x["vendor"]["id"], "name": x["vendor"]["name"],
                                   "score": x["score"], "why": x["why"],
                                   "scorecard": x["scorecard"]}
                                  for x in agents.rank_vendors(r)])
        m = re.match(r"^/api/units/([a-z0-9_]+)/memory$", path)
        if m:
            return self.send_api(agents.unit_memory(m.group(1)))
        m = re.match(r"^/api/owner/([a-z0-9_]+)/report$", path)
        if m:
            rep = agents.owner_report(m.group(1))
            return self.send_api(rep or {"error": "not found"}, 200 if rep else 404)
        return self.send_api({"error": "no route"}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        self.session = None
        denied = self.gate(path, "POST")
        if denied:
            return self.send_api(*denied)
        body = self.body_json()
        if path == "/api/auth/login":
            out = login(body.get("code"))
            if not out:
                return self.send_api({"error": "unknown access code"}, 401)
            raw = json.dumps({k: out[k] for k in ("role", "id", "name")}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie",
                             f"pos_sess={out['session']}; Path=/; HttpOnly; SameSite=Lax")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            return self.wfile.write(raw)
        if AUTH_ON and self.session and self.session["role"] == "tenant"                 and path == "/api/requests":
            body["tenant_id"] = self.session["id"]   # a resident files as themselves
        m = re.match(r"^/api/job/([A-Za-z0-9_]+)/([a-z_]+)$", path)
        if m:
            return self.send_api(*job_action(m.group(1), m.group(2), body))
        if path == "/api/turnovers":
            return self.send_api(*open_turnover(body))
        m = re.match(r"^/api/turnovers/([a-z0-9_]+)/advance$", path)
        if m:
            return self.send_api(*advance_turnover(m.group(1), body))
        if path == "/api/inquiries":
            return self.send_api(*growth.record_inquiry(body))
        if path == "/api/referrals":
            source = body.get("source") or "human:mgr_1"
            if AUTH_ON and self.session and self.session["role"] == "owner":
                source = f"owner:{self.session['id']}"   # an owner refers as themselves
            row, err = growth.record_referral(body, source)
            return self.send_api({"referral": row} if row else {"error": err},
                                 200 if row else 400)
        m = re.match(r"^/api/referrals/([a-z0-9_]+)/status$", path)
        if m:
            row, err = growth.set_referral_status(m.group(1), body.get("status"),
                                                  body.get("actor", "human:mgr_1"))
            return self.send_api({"referral": row} if row else {"error": err},
                                 200 if row else 400)
        m = re.match(r"^/api/inquiries/([a-z0-9_]+)/status$", path)
        if m:
            row, err = growth.set_inquiry_status(m.group(1), body.get("status"),
                                                 body.get("actor", "human:mgr_1"))
            return self.send_api({"inquiry": row} if row else {"error": err},
                                 200 if row else 400)
        if path == "/api/prospects":
            src = {"kind": "manual", "by": body.get("actor", "human:mgr_1")}
            if (body.get("provenance") or "").strip():
                src = {"kind": "sourced", "provenance": body["provenance"].strip(),
                       "by": body.get("actor", "human:mgr_1")}
            row, err = pipeline.add_prospect(
                body, src, actor=body.get("actor", "human:mgr_1"))
            return self.send_api({"prospect": row} if row else {"error": err},
                                 200 if row else 400)
        if path == "/api/prospects/import":
            report, err = pipeline.import_targets(
                body, actor=body.get("actor", "human:mgr_1"))
            return self.send_api({"report": report} if report else {"error": err},
                                 200 if report else 400)
        m = re.match(r"^/api/prospects/([a-z0-9_]+)/dnc$", path)
        if m:
            row, err = pipeline.record_do_not_contact(
                m.group(1), actor=body.get("actor", "human:mgr_1"))
            return self.send_api({"prospect": row} if row else {"error": err},
                                 200 if row else 400)
        m = re.match(r"^/api/prospects/([a-z0-9_]+)/wake$", path)
        if m:
            row, err = pipeline.wake_prospect(
                m.group(1), actor=body.get("actor", "human:mgr_1"))
            return self.send_api({"prospect": row} if row else {"error": err},
                                 200 if row else 400)
        m = re.match(r"^/api/prospects/([a-z0-9_]+)/advance$", path)
        if m:
            row, err = pipeline.advance_prospect(
                m.group(1), body.get("stage"),
                actor=body.get("actor", "human:mgr_1"),
                reason=body.get("reason"))
            return self.send_api({"prospect": row} if row else {"error": err},
                                 200 if row else 400)
        m = re.match(r"^/api/prospects/([a-z0-9_]+)/scaffold$", path)
        if m:
            out, err = pipeline.scaffold_won_client(
                m.group(1), actor=body.get("actor", "human:mgr_1"))
            return self.send_api(out if out else {"error": err},
                                 200 if out else 400)
        if path == "/api/growth/rotate_share":
            tok = growth.rotate_share_token(body.get("actor", "human:mgr_1"))
            return self.send_api({"share_url": f"/pitch?t={tok}"})
        if path == "/api/money/payments":
            return self.send_api(*record_payment_api(body))
        m = re.match(r"^/api/money/batches/([a-z0-9_]+)/execute$", path)
        if m:
            out = money.execute_batch(m.group(1), body.get("actor", "human:mgr_1"),
                                      body.get("reference", ""))
            return self.send_api(out, 200 if "batch" in out else 400)
        if path == "/api/requests":
            return self.send_api(*create_request(body))
        if path == "/api/agents/run":
            name = self.q.get("agent")
            if name and name not in agents.AGENTS:
                return self.send_api({"error": f"unknown agent {name}"}, 400)
            res = {name: agents.AGENTS[name]()} if name else agents.run_all()
            return self.send_api({"ran": res, "metrics": metrics()})
        for pat, fn in ((r"^/api/requests/([a-z0-9_]+)/status$", set_status),
                        (r"^/api/requests/([a-z0-9_]+)/assign$", assign),
                        (r"^/api/requests/([a-z0-9_]+)/feedback$", feedback),
                        (r"^/api/requests/([a-z0-9_]+)/schedule$", schedule),
                        (r"^/api/approvals/([a-z0-9_]+)/decide$", decide_approval),
                        (r"^/api/messages/([a-z0-9_]+)/send$", send_message)):
            m = re.match(pat, path)
            if m:
                return self.send_api(*fn(m.group(1), body))
        return self.send_api({"error": "no route"}, 404)

    def end_headers(self):
        """Static assets must revalidate.

        The service worker deliberately caches the shell so a resident can open
        the app on a bad connection — that is the point of it. But the BROWSER's
        own HTTP cache sits in front of that, so an edited stylesheet keeps
        serving stale bytes until someone clears storage by hand. `no-cache`
        means "you may keep a copy, but ask before using it", which preserves
        the offline story and kills the stale-asset trap.

        API responses set their own `no-store` in send_api and are skipped here
        so the header is never sent twice.
        """
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def _scheduler(minutes):
    """The agents on a clock — the app runs itself instead of waiting for the
    'Run agents' button. Sweeps are proven idempotent (the journey suite pins
    it), which is exactly what makes the interval a free choice."""
    while True:
        time.sleep(minutes * 60)
        try:
            agents.run_all()
            log_event("sweep_completed", "scheduler", "agent:scheduler", "R3",
                      {"interval_minutes": minutes})
        except Exception as e:
            log_event("sweep_failed", "scheduler", "agent:scheduler", "R3",
                      {"error": f"{type(e).__name__}: {e}"})


if __name__ == "__main__":
    if not (core.DATA / "requests.json").exists():
        print("No data yet — run:  python3 seed.py")
        sys.exit(1)
    sweep_min = int(os.environ.get("PROPERTYOS_SWEEP_MINUTES", "15"))
    if sweep_min > 0:
        threading.Thread(target=_scheduler, args=(sweep_min,), daemon=True).start()
    print(f"Property OS on http://127.0.0.1:{PORT}  "
          f"(auth {'ON' if AUTH_ON else 'off'} · sweep every {sweep_min}m)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
