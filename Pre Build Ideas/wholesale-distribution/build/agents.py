#!/usr/bin/env python3
"""Quote Desk OS — the agents: RFQ parser, quote builder, PO ingestion, follow-up.

Nothing here files a low-confidence line into a quote, substitutes a part
silently, or writes an order from a discrepant PO.

Stdlib only.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import days_until, iso, now, parse


# ---------------------------------------------------------------- 1 · RFQ parser

LINE_RE = re.compile(
    r"^\s*(?:(?P<qty>\d+)\s*(?P<uom>ea|each|pc|pcs|pk|pack|bx|box|cs|case|ft|feet|lf|roll|rl)?\s*[-x:]?\s*)?"
    r"(?P<desc>.+?)\s*(?:\((?P<pn>[A-Z0-9\-]{3,})\))?\s*$", re.I)


def parse_rfq(rfq_id):
    """Email body / spreadsheet rows / photo transcription → structured lines.

    The parser is deliberately permissive; the MATCHER is where the caution
    lives. A line that parses but does not match confidently is queued.
    """
    rfq = store.by_id("rfqs", rfq_id)
    if not rfq:
        return {"error": "no such rfq"}
    raw_lines = rfq.get("lines")
    if raw_lines is None:
        raw_lines = []
        for ln in (rfq.get("body") or "").splitlines():
            if not ln.strip() or len(ln.strip()) < 3:
                continue
            m = LINE_RE.match(ln)
            if not m:
                continue
            raw_lines.append({"qty": int(m.group("qty")) if m.group("qty") else None,
                              "uom": m.group("uom"), "description": m.group("desc").strip(),
                              "customer_part": m.group("pn")})
    gate.act("parse_rfq", "parser", rfq_id,
             {"summary": f"{len(raw_lines)} line(s) from {rfq.get('source')}"})
    return {"rfq": rfq_id, "lines": raw_lines}


# ---------------------------------------------------------------- 2 · quote builder

def build_quote(rfq_id, ref=None):
    ref = ref or now()
    rfq = store.by_id("rfqs", rfq_id)
    if not rfq:
        return {"error": "no such rfq"}
    cust = store.by_id("customers", rfq["customer_id"]) or {}
    catalog, xref = store.load("catalog"), store.load("xref")
    parsed = parse_rfq(rfq_id)["lines"]

    priced, queued, subs = [], [], []
    for raw in parsed:
        m = core.match_line(raw, catalog, cust, xref)
        gate.act("match_line", "quoter", rfq_id,
                 {"summary": f"{(raw.get('description') or '')[:40]} → {m['sku'] or 'no match'} "
                             f"({m['confidence']})"})
        if not m["sku"] or m["confidence"] < core.MATCH_THRESHOLD:
            gate.act("queue_low_confidence", "quoter", rfq_id,
                     {"summary": f"queued: {(raw.get('description') or '')[:40]}", "why": m["why"]})
            queued.append({"raw": raw, "confidence": m["confidence"], "why": m["why"]})
            continue
        sub = core.substitution_for(m["row"], catalog)
        if sub:
            res = gate.act("propose_substitution", "quoter", rfq_id,
                           {"summary": f"{m['sku']} discontinued → {sub.get('proposed') or 'no successor'}",
                            "differences": sub.get("differences"), "why": sub["why"]})
            subs.append({**sub, "for_sku": m["sku"], "approval": res.get("approval")})
            if not sub.get("proposed"):
                queued.append({"raw": raw, "confidence": m["confidence"], "why": sub["why"]})
                continue
            m = {**m, "sku": sub["proposed"],
                 "row": next(c for c in catalog if c["sku"] == sub["proposed"])}
        p = core.price_line(m["row"], cust, raw.get("qty") or 1)
        priced.append({**p, "description": m["row"]["description"], "family": m["row"].get("family"),
                       "uom": m["row"].get("uom"), "match_why": m["why"],
                       "confidence": m["confidence"]})

    below = [l for l in priced if l["below_floor"]]
    total = round(sum(l["extended"] for l in priced), 2)
    state = ("queued_for_human" if queued and not priced else
             "awaiting_approval" if (below or subs) else "draft")
    q = {"id": store.nid("q"), "rfq_id": rfq_id, "customer_id": cust.get("id"),
         "customer": cust.get("name"), "created_at": rfq.get("at") or iso(ref),
         "lines": priced, "queued_lines": queued, "substitutions": subs,
         "total": total, "below_floor": bool(below), "state": state,
         "ship_to": cust.get("ship_to"), "terms": cust.get("terms"), "touches": []}

    if below:
        gate.act("price_below_floor", "quoter", q["id"],
                 {"summary": f"{len(below)} line(s) under the {core.MARGIN_FLOOR:.0%} floor",
                  "lines": [l["sku"] for l in below]})
    elif priced:
        def _price():
            q["state"] = "awaiting_approval"
            return q["id"]
        gate.act("price_quote", "quoter", q["id"],
                 {"summary": f"{len(priced)} line(s), ${total:,.2f}"}, execute=_price)
    store.upsert("quotes", q)
    return {"quote": q, "priced": len(priced), "queued": len(queued), "substitutions": len(subs)}


def sweep_rfqs(limit=200, ref=None):
    made = 0
    for r in store.load("rfqs"):
        if r.get("quoted_at") or r.get("demo_tag"):
            continue
        build_quote(r["id"], ref)
        r["quoted_at"] = iso(ref or now())
        store.upsert("rfqs", r)
        made += 1
        if made >= limit:
            break
    return {"quoted": made}


# ---------------------------------------------------------------- 3 · PO ingestion

def ingest_po(po_id, ref=None):
    ref = ref or now()
    po = store.by_id("pos", po_id)
    if not po:
        return {"error": "no such po"}
    quote = store.by_id("quotes", po.get("quote_id"))
    if not quote:
        po.update(verdict="exception", why="no quote on file to reconcile against",
                  processed_at=iso(ref))
        store.upsert("pos", po)
        return {"po": po_id, "verdict": "exception",
                "why": "no quote on file — an order is never written from a PO alone"}
    r = core.reconcile(po, quote)
    po.update(verdict=r["verdict"], discrepancies=r["discrepancies"], why=r["why"],
              processed_at=iso(ref))
    store.upsert("pos", po)
    if r["clean"]:
        def _write():
            o = {"id": store.nid("o"), "po_id": po_id, "quote_id": quote["id"],
                 "customer_id": quote["customer_id"], "lines": quote["lines"],
                 "total": quote["total"], "written_at": iso(ref)}
            store.upsert("orders", o)
            quote["state"] = "won"
            quote["decided_at"] = iso(ref)
            store.upsert("quotes", quote)
            return o["id"]
        res = gate.act("write_order", "orders", po_id,
                       {"summary": f"{po.get('number')} reconciles — order written"}, execute=_write)
        return {"po": po_id, "verdict": "order", "gate": res, "why": r["why"]}
    # deliberately NOT queued as an approvable row: writing a discrepant order is R0
    gate.act("write_discrepant_order", "orders", po_id,
             {"summary": f"{po.get('number')} held — {len(r['discrepancies'])} discrepancy(ies)",
              "discrepancies": r["discrepancies"]})
    return {"po": po_id, "verdict": "exception", "discrepancies": r["discrepancies"],
            "why": r["why"]}


def sweep_pos(ref=None):
    done = 0
    for p in store.load("pos"):
        if p.get("processed_at") or p.get("demo_tag"):
            continue
        ingest_po(p["id"], ref)
        done += 1
    return {"processed": done}


# ---------------------------------------------------------------- 4 · follow-up

def followups(ref=None):
    ref = ref or now()
    drafted, closed = 0, 0
    for q in store.load("quotes"):
        if core.quote_state(q, ref) == "expired" and q.get("state") == "sent":
            def _close(q=q):
                q.update(state="lost", loss_reason="no_decision", decided_at=iso(ref))
                store.upsert("quotes", q)
                return q["id"]
            gate.act("close_quote_lost", "followup", q["id"],
                     {"summary": f"${q.get('total', 0):,.2f} · {core.QUOTE_TTL_DAYS}d with no decision",
                      "loss_reason": "no_decision"}, execute=_close)
            closed += 1
            continue
        for t in core.due_followups(q, ref):
            gate.act("quote_followup", "followup", q["id"],
                     {"summary": f"{t['kind']} · {q.get('customer')} · ${q.get('total', 0):,.2f}",
                      "preview": _copy(q, t)})
            q.setdefault("touches", []).append({"day": t["day"], "kind": t["kind"], "at": iso(ref)})
            store.upsert("quotes", q)
            drafted += 1
    return {"drafted": drafted, "closed": closed}


def _copy(q, t):
    who = (q.get("customer") or "there")
    if t["kind"] == "confirm":
        return (f"Hi — checking the quote for {who} came through cleanly and the specs read right. "
                f"Happy to walk any line back to the drawing.")
    if t["kind"] == "check":
        return (f"Hi — is the {who} quote still live? No pressure either way; I'd rather know it's "
                f"gone than keep holding stock against it.")
    return (f"Hi — last note on this one. I'll close it on our side, and it's easy to refresh if "
            f"the job comes back.")


def run_all():
    return {"rfqs": sweep_rfqs(), "pos": sweep_pos(), "followups": followups()}
