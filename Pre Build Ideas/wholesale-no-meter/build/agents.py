#!/usr/bin/env python3
"""Counter OS — the agents. Everything routes through `core.gate`. Stdlib only.

Deliberately absent: any force path for a stocking case. `draft_stocking_case`
recounts the counted ledger itself and there is no function in this build that
drafts a case from anything else.
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


# ---------------------------------------------------------------- capture

def report_no(payload, source="counter"):
    """The capture path — a no goes from sentence to counted row in seconds.
    Priced from a recorded comparable or counted UNPRICED; if the counted
    ledger crosses the recorded threshold, the stocking case drafts at R1."""
    missing = [f for f in ("item_asked", "kind", "branch") if not payload.get(f)]
    if missing:
        return {"error": f"a no needs: {', '.join(missing)} — the capture is the product, "
                         f"and a half-captured no counts nothing"}
    if payload["kind"] not in core.NO_KINDS:
        return {"error": f"kind must be one of {core.NO_KINDS}"}
    no = {"id": store.nid("no"), "at": payload.get("at") or iso(),
          "item_asked": payload["item_asked"], "kind": payload["kind"],
          "asked_by": payload.get("asked_by"), "branch": payload["branch"],
          "walked_or_waited": payload.get("walked_or_waited") or "unknown",
          "category": payload.get("category"), "sku": payload.get("sku"),
          "qty": payload.get("qty")}
    store.upsert("nos", no)
    gate.act("log_no", source, no["id"],
             {"item": no["item_asked"], "kind": no["kind"], "branch": no["branch"]})
    pricing = core.price_no(no)
    out = {"no": no, "pricing": pricing}
    if not pricing["priced"]:
        # The refusal to invent a dollar is logged every time it happens —
        # UNPRICED is a first-class result, not a silent gap.
        r = gate.act("price_no_without_comparable", source, no["id"],
                     {"item": no["item_asked"], "why": pricing["why"]})
        out["refused_pricing"] = {"why": pricing["why"], "event": r.get("event")}
    if no["kind"] in ("not_carried", "wrong_size"):
        ok, _rows, arithmetic, _th = core.stocking_case_check(no["item_asked"])
        out["threshold"] = arithmetic
        if ok:
            out["case"] = draft_stocking_case(no["item_asked"])
    return out


# ---------------------------------------------------------------- the stocking case

def _slug(s):
    return re.sub(r"[^a-z0-9]+", "_", core._norm(s)).strip("_")[:48]


def draft_stocking_case(item):
    """The case drafts only from the counted ledger's own arithmetic. Below the
    recorded threshold there is NO case — structurally: this function recounts
    the ledger itself, and no force path exists anywhere in this build."""
    ok, rows, arithmetic, th = core.stocking_case_check(item)
    if not ok:
        r = gate.act("stocking_case_below_threshold", "stocking", item,
                     {"arithmetic": arithmetic})
        return {"refused": (f"no case — {arithmetic}. One loud contractor asking twice is "
                            f"an anecdote, not demand; the case waits for the count."),
                "arithmetic": arithmetic, "event": r.get("event")}
    ix = store.index("catalog", "sku")
    dollars, priced_n, unpriced_n, bases = 0.0, 0, 0, []
    for n in rows:
        p = core.price_no(n, ix)
        if p["priced"]:
            priced_n += 1
            dollars += p["dollars"]
            bases.append(p["basis"])
        else:
            unpriced_n += 1
    cats = [n.get("category") for n in rows if n.get("category")]
    category = max(set(cats), key=cats.count) if cats else None
    case = {"id": f"case_{_slug(item)}", "item": item, "at": iso(), "state": "drafted",
            "threshold": {"arithmetic": arithmetic, "count": th["count"],
                          "window_days": th["window_days"], "source": th["_source"]},
            "history": rows,  # the no history, verbatim ledger rows
            "math": {"counted_margin_dollars": round(dollars, 2), "priced": priced_n,
                     "unpriced": unpriced_n,
                     "unpriced_note": (f"{unpriced_n} no's counted but not dollared — "
                                       f"{core.UNPRICED_PHRASE}") if unpriced_n else None,
                     "bases": sorted(set(bases))},
            "category": category,
            "vendor_options": core.vendor_options(category)}
    store.upsert("cases", case)
    g = gate.act("draft_stocking_case", "stocking", case["id"],
                 {"summary": (f"stock '{item}'? {len(rows)} counted no's; counted "
                              f"margin ${dollars:,.0f} in {th['window_days']}d"),
                  "arithmetic": arithmetic})
    case["approval"] = g.get("approval")
    store.upsert("cases", case)
    return {"case": case, "gate": g}


def case_sweep(limit=6):
    """Draft cases for every item the counted ledger has pushed over the
    recorded threshold. Below-threshold items are left alone by construction."""
    out = {"drafted": 0, "already": 0}
    pending = {a["subject"] for a in gate.pending() if a["action"] == "draft_stocking_case"}
    for cand in core.stocking_candidates()["rows"]:
        if out["drafted"] >= limit or not cand["crossed"]:
            continue
        cid = f"case_{_slug(cand['item'])}"
        if cid in pending or (store.by_id("cases", cid) or {}).get("state") == "approved_to_stock":
            out["already"] += 1
            continue
        draft_stocking_case(cand["item"])
        out["drafted"] += 1
    return out


# ---------------------------------------------------------------- the OOS autopsy

def draft_oos_autopsy(sku):
    a = core.oos_autopsy(sku)
    if "error" in a or "refused" in a:
        return a
    g = gate.act("draft_reorder_autopsy", "purchasing", sku,
                 {"summary": (f"{sku}: point {a['recorded_point']} → {a['proposed_point']}; "
                              f"walked cost {a['walked_cost']['dollars']:,.2f} counted"),
                  "math": a["math"]})
    return {"autopsy": a, "gate": g}


def autopsy_sweep(limit=4, window_days=60):
    seen, out = set(), {"drafted": 0}
    pending = {a["subject"] for a in gate.pending() if a["action"] == "draft_reorder_autopsy"}
    for n in core.recent_nos(window_days, kinds=("out_of_stock",)):
        sku = n.get("sku")
        if not sku or sku in seen or sku in pending or out["drafted"] >= limit:
            continue
        seen.add(sku)
        r = draft_oos_autopsy(sku)
        if "autopsy" in r:
            out["drafted"] += 1
    return out


# ---------------------------------------------------------------- the vendor packet

def draft_vendor_packet(vendor_id):
    p = core.vendor_packet(vendor_id)
    if "error" in p:
        return p
    if not p["rows"]:
        return {"refused": (f"no counted no's on {p['name']}'s line in {p['window_days']} days "
                            f"— a packet with nothing counted in it is not drafted, and "
                            f"nothing gets invented to fill one"), **{"vendor": vendor_id}}
    g = gate.act("draft_vendor_packet", "purchasing", vendor_id,
                 {"summary": (f"{p['name']}: {p['counted']['fill_failures']} counted fill "
                              f"failures, {p['counted']['walked']} walked, "
                              f"${p['counted']['walked_margin_dollars']:,.2f} counted margin")})
    return {"packet": p, "gate": g}


# ---------------------------------------------------------------- messages

def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "counter", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "contractor_down":
        ans = core.stock_answer(m.get("text", ""))
        okp, why = core.optimism_ok(ans["answer"])
        assert okp, why  # structural: the shipped copy passes its own check
        gate.act("draft_counter_reply", "counter", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": ans["answer"][:110]})
        m["draft_reply"] = ans["answer"]
        step = {"action": "draft_counter_reply", "draft": ans["answer"],
                "why": "answered from counted stock only — never optimism"}
        if ans.get("capture"):
            item = ans.get("sku") or m.get("text", "")[:80]
            cap = report_no({"item_asked": item, "kind": ans["capture"],
                             "asked_by": m.get("from"), "branch": m.get("branch") or "Fairfield",
                             "walked_or_waited": "unknown", "sku": ans.get("sku")},
                            source="counter")
            step["captured_no"] = cap["no"]["id"]
            step["why"] += " — and the miss itself is now a counted no"
        out["steps"].append(step)
    elif c["label"] == "no_report":
        if m.get("no"):
            r = report_no(dict(m["no"]), source="counter")
            step = {"action": "log_no", "no": r.get("no", {}).get("id"),
                    "pricing": r.get("pricing"), "threshold": r.get("threshold"),
                    "why": "captured verbatim into the counted ledger"}
            if r.get("case"):
                step["case"] = ("refused" if "refused" in r["case"]
                                else r["case"]["case"]["id"])
            out["steps"].append(step)
        else:
            out["steps"].append({"action": "route_human",
                                 "why": "a no report needs the item and the kind — a person "
                                        "fills the two fields; a half-captured no counts nothing"})
    elif c["label"] == "price_ask":
        row = core.find_item(m.get("text", ""))
        if row:
            body = (f"Recorded list on {row['sku']} ({row['description']}): "
                    f"${row['list']:.2f}/{row.get('uom', 'ea')} — counted stock "
                    f"{sum((row.get('on_hand') or {}).values())} across branches. A person "
                    f"confirms quantity breaks before anything is promised.")
            gate.act("draft_counter_reply", "counter", msg_id,
                     {"summary": m.get("text", "")[:60], "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_counter_reply", "draft": body,
                                 "why": "recorded list and counted stock only"})
        else:
            out["steps"].append({"action": "route_human",
                                 "why": "no confident catalog match — a person quotes; a loose "
                                        "match prices the wrong part, confidently"})
    elif c["label"] == "willcall":
        out["steps"].append({"action": "route_human",
                             "why": "will-call status lives in the order record — a person "
                                    "checks it; no invented status"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "cases": case_sweep(),
            "autopsies": autopsy_sweep()}
