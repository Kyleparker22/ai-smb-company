#!/usr/bin/env python3
"""Consign OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "counter", msg_id, {"label": c["label"], "why": c["why"]})
    item = store.by_id("items", m.get("item_id")) if m.get("item_id") else None

    if c["label"] == "claim":
        gate.act("log_claim", "counter", msg_id,
                 {"verbatim": m.get("text", ""), "from": m.get("from"),
                  "item": (item or {}).get("id")})
        ev = store.log_event("refused", msg_id, "agent:counter", "R0",
                             {"action": "deny_claim",
                              "why": "software assembles the record; a human rules"})
        store.log_event("refused", msg_id, "agent:counter", "R0",
                        {"action": "certify_authenticity",
                         "why": "software never calls an item genuine — and never calls it "
                                "fake either; the record is pulled and a human decides"})
        body = _claim_ack(m, item)
        out["steps"].append({"action": "log_claim", "draft": body,
                             "refused": "nothing ruled by this message — no denial, and no "
                                        "verdict either way on authenticity; the intake record "
                                        "and any cert are pulled for a human",
                             "record": core.brand_line(item) if item else
                                       {"state": "no item linked — the record pull is manual"},
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "auth_ask":
        body = _auth_copy(m, item)
        okc, why = core.listing_ok(body, item)
        assert okc, why  # structural: the shipped copy passes its own claim check
        gate.act("draft_auth_reply", "counter", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_auth_reply", "draft": body,
                             "why": "the record speaks — the consignor tag or a cited cert; "
                                    "software never adds its own judgment"})
    elif c["label"] == "offer":
        out["steps"].append(_offer_step(m, item))
    elif c["label"] == "pickup":
        slots = _pickup_slots()
        gate.act("propose_pickup", "counter", msg_id, {"slots": slots})
        body = _pickup_copy(m, slots)
        m["draft_reply"] = body
        out["steps"].append({"action": "propose_pickup", "draft": body,
                             "why": "slots propose at R2 — nothing is booked until the buyer "
                                    "confirms one"})
    elif c["label"] == "payout":
        out["steps"].append(_payout_step(m))
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _claim_ack(m, item):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — taking this seriously, and here's exactly what happens: we pull the "
            f"intake record for the item (condition notes, the consignor's tag, and any "
            f"third-party authentication on file) and the owner reviews it with you directly. "
            f"Nothing about your claim is decided by this message — no denial, and no verdict "
            f"either way on authenticity. You'll hear from a person within one business day.")


def _auth_copy(m, item):
    who = (m.get("from") or "there").split()[0]
    bl = core.brand_line(item) if item else None
    if bl and bl["line"]:
        return (f"Hi {who} — the honest answer is exactly what's on the record: {bl['line']} "
                f"Happy to show you the tag and paperwork in person before you decide.")
    return (f"Hi {who} — honest answer: we sell items as tagged by the consignor, and we only "
            f"say 'authenticated' when a third-party certificate is on file — for this one I'd "
            f"want to pull the record before saying anything. Come see the tag and decide with "
            f"it in your hands.")


def _offer_step(m, item):
    if not item:
        return {"action": "route_human",
                "why": "an offer with no item linked — a person matches it up"}
    chk = core.offer_check(item, m.get("offer_amount"))
    if "refused" in chk:
        ev = store.log_event("refused", item["id"], "agent:counter", "R0",
                             {"action": "accept_below_floor", "why": chk["refused"]})
        return {"action": "route_consignor", "refused": chk["refused"], "event": ev["id"],
                "why": "no recorded floor — the consignor decides, not software"}
    who = (m.get("from") or "there").split()[0]
    if chk["action"] == "counter":
        store.log_event("refused", item["id"], "agent:counter", "R0",
                        {"action": "accept_below_floor", "why": chk["why"]})
        body = (f"Hi {who} — we can't do ${float(m.get('offer_amount') or 0):,.0f} on that one: "
                f"it's consigned, and the owner's floor is ${item['floor_price']:,.0f}. That "
                f"number we can do today, and it comes with the full intake record.")
    else:
        body = (f"Hi {who} — ${float(m.get('offer_amount') or 0):,.0f} works; that clears the "
                f"owner's floor. Reply to confirm and we'll set a pickup window.")
    gate.act("draft_offer_reply", "counter", m["id"],
             {"summary": f"{chk['action']} at floor ${item['floor_price']:,.0f}",
              "preview": body[:110]})
    m["draft_reply"] = body
    return {"action": "draft_offer_reply", "draft": body, "check": chk,
            "why": chk["why"]}


def _pickup_slots():
    base = now()
    return [iso(base.replace(hour=h, minute=0, second=0, microsecond=0)
                + __import__("datetime").timedelta(days=d))
            for d, h in ((1, 10), (1, 16), (2, 12))]


def _pickup_copy(m, slots):
    who = (m.get("from") or "there").split()[0]
    days = ", ".join(s[:16].replace("T", " ") for s in slots)
    return (f"Hi {who} — any of these work? {days}. Reply with one and it's held for you; "
            f"nothing is booked until you confirm.")


def _payout_step(m):
    who = (m.get("from") or "there").split()[0]
    cons = next((c for c in store.load("consignors")
                 if (c.get("name") or "").split()[0].lower() == who.lower()), None)
    sold = [i for i in store.load("items")
            if cons and i.get("consignor_id") == cons["id"] and i.get("status") == "sold"]
    unpaid = [i for i in sold if not i.get("paid_out_at")]
    lines, unpayable = [], []
    for i in unpaid:
        math = core.payout_math(i, cons)
        if "refused" in math:
            unpayable.append({"item": i["id"], "why": math["refused"]})
        else:
            lines.append({"item": i["id"], "title": i.get("title"), **math})
    total = round(sum(x["amount"] for x in lines), 2)
    body = (f"Hi {who} — from the ledger: {len(sold)} of your items have sold; "
            f"{len(lines)} payout(s) totalling ${total:,.2f} are drafted from your recorded "
            f"split and awaiting the owner's pay run"
            + (f", and {len(unpayable)} sale(s) can't be computed yet — we'll confirm the "
               f"missing agreement detail with you rather than guess" if unpayable else "")
            + ". Every number is the agreement's arithmetic, not memory.")
    gate.act("draft_payout", "ledger", m["id"],
             {"summary": f"{len(lines)} payout(s) ${total:,.2f} for {who}",
              "preview": body[:110]})
    m["draft_reply"] = body
    return {"action": "draft_payout", "draft": body, "payouts": lines,
            "unpayable": unpayable,
            "why": "answered from the ledger — the agreement's arithmetic cited, missing "
                   "inputs named rather than guessed"}


# ---------------------------------------------------------------- listings

def list_item(item_id):
    it = store.by_id("items", item_id)
    if not it:
        return {"error": "no such item"}
    okl, why = core.can_list(it)
    if not okl:
        action = ("list_prohibited_item" if "prohibited" in why or "recall" in why
                  else "publish_listing_blocked")
        ev = store.log_event("refused", item_id, "agent:listings", "R0" if
                             action == "list_prohibited_item" else None,
                             {"action": action, "why": why})
        return {"refused": why, "event": ev["id"]}
    d = core.describe(it)
    assert d["listing_ok"], d["why"]  # structural: the listing passes its own claim check
    gate.act("draft_listing", "listings", item_id,
             {"summary": (it.get("title") or "")[:60], "preview": d["body"][:110]})
    r = gate.act("publish_listing", "listings", item_id,
                 {"summary": f"publish to {', '.join(d['channels'])}",
                  "preview": d["body"][:110]})
    it["listing_draft"] = d["body"]
    store.upsert("items", it)
    return {"listing": d, "gate": r,
            "note": "drafted for the shop's business channels — a human publishes"}


def listing_sweep(limit=15):
    out = {"drafted": 0, "refused": 0, "skipped": 0}
    for it in store.load("items"):
        if out["drafted"] >= limit:
            break
        if it.get("status") != "intake" or it.get("demo_tag") or it.get("listing_draft"):
            out["skipped"] += 1
            continue
        r = list_item(it["id"])
        out["drafted" if "listing" in r else "refused"] += 1
    return out


def markdown_sweep(ref=None):
    """Reprice per the recorded schedule. R2 — the agreement already decided
    this number; anything off-schedule has no path."""
    ref = ref or now()
    out = {"repriced": 0, "unchanged": 0}
    for it in store.load("items"):
        if it.get("status") != "listed" or it.get("demo_tag"):
            continue
        md = core.markdown_price(it, ref)
        if "refused" in md:
            continue
        if it.get("current_price") == md["price"]:
            out["unchanged"] += 1
            continue
        gate.act("markdown_on_schedule", "pricing", it["id"],
                 {"summary": f"{it.get('title')} → ${md['price']:,.2f} ({md['basis']})"})
        it["current_price"] = md["price"]
        store.upsert("items", it)
        out["repriced"] += 1
    return out


# ---------------------------------------------------------------- the clock

def reclaim_sweep(limit=15, ref=None):
    ref = ref or now()
    out = {"drafted": 0, "skipped": 0}
    consignors = store.index("consignors")
    for it in store.load("items"):
        if out["drafted"] >= limit or it.get("status") != "listed" or it.get("demo_tag"):
            continue
        plan = core.reclaim_plan(it, ref)
        if plan["action"] != "draft_notice":
            out["skipped"] += 1
            continue
        touch_n = len(it.get("reclaim_touches") or []) + 1
        who = (consignors.get(it.get("consignor_id"), {}).get("name") or "there").split()[0]
        st = core.clock_state(it, ref)
        body = {
            1: (f"Hi {who} — your {it.get('title')} finished its listing term. You have "
                f"{st.get('reclaim_ends_in')} days to pick it up, or we can keep trying at the "
                f"marked-down price — your call, just reply."),
            2: (f"Hi {who} — second note on the {it.get('title')}: {st.get('reclaim_ends_in')} "
                f"days left on your reclaim window. Reply and we'll hold it for you."),
            3: (f"Hi {who} — last note from us on the {it.get('title')}. After the window the "
                f"agreement lets it go to donation — we'd genuinely rather hand it back. One "
                f"reply holds it."),
        }.get(touch_n, f"Hi {who} — your item's reclaim window is running.")
        gate.act("draft_reclaim_notice", "clock", it["id"],
                 {"summary": f"{who} · {it.get('title')} · touch {touch_n}",
                  "preview": body[:110]})
        it.setdefault("reclaim_touches", []).append({"at": iso(ref), "kind": "drafted"})
        store.upsert("items", it)
        out["drafted"] += 1
    return out


def donate(item_id, human=None):
    it = store.by_id("items", item_id)
    if not it:
        return {"error": "no such item"}
    okd, why = core.can_donate(it)
    if not okd:
        ev = store.log_event("refused", item_id, "agent:clock", "R0",
                             {"action": "donate_before_clock", "why": why})
        return {"refused": why, "event": ev["id"]}
    if not human:
        return {"refused": "the clock is complete but donation is a human act — a person "
                           "confirms", "why": why}
    it["status"] = "donated"
    store.upsert("items", it)
    store.log_event("donated", item_id, f"human:{human}", "R1", {"why": why})
    return {"donated": True, "why": why}


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at") and not m.get("demo_tag"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "listings": listing_sweep(),
            "markdowns": markdown_sweep(), "reclaim": reclaim_sweep()}
