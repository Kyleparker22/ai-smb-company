#!/usr/bin/env python3
"""Quote Desk OS — domain core (distributors · job shops · custom manufacturing).

Everything that is a *rule* lives here: the catalog and cross-reference models,
the line-matching scorer and its confidence thresholds, pricing/tier/margin-floor
logic, substitution rules, PO reconciliation and discrepancy typing, the quote
state machine and follow-up cadence, the ROI model and the autonomy matrix.

The product thesis: two clocks. Quote turnaround (a competitor answers in four
hours) and order entry (a PO keyed by hand is where the wrong quantity, the
wrong revision and the discontinued part get in).

Three prohibitions are rules here:
  1. A low-confidence line NEVER enters a quote. It goes to a human queue with
     the ambiguity named.
  2. A substitution is NEVER silent — it is a proposal with the spec difference
     stated, and it drops the quote to the approval gate.
  3. A discrepant PO NEVER becomes an order. The whole order holds.
Plus: one customer's pricing agreement can never price another customer, and
that is enforced structurally rather than by discipline.

Stdlib only.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "catalog", "customers", "xref", "rfqs", "quotes", "pos",
          "orders", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="QUOTEDESK_DATA_ROOT")


# ---------------------------------------------------------------- pricing
#
# Tiers are a DISCOUNT OFF LIST, and the margin floor is computed against cost.
# The floor is the rule that keeps a desk from buying business by accident.

TIERS = {"contract": 0.32, "preferred": 0.22, "standard": 0.12, "spot": 0.0}
MARGIN_FLOOR = 0.18          # below this, a human approves — always


def price_line(sku_row, customer, qty):
    """List → tier discount → the customer's own agreement, if any.

    A customer's agreement is read from THEIR record only. There is no argument
    to this function that could make one customer's pricing available to
    another, which is the structural half of the confidentiality rule.
    """
    if not sku_row:
        return None
    tier = customer.get("tier", "spot")
    disc = TIERS.get(tier, 0.0)
    agreed = (customer.get("agreement") or {}).get(sku_row["sku"])
    unit = agreed if agreed is not None else round(sku_row["list"] * (1 - disc), 2)
    cost = sku_row["cost"]
    margin = round((unit - cost) / unit, 4) if unit else None
    return {"sku": sku_row["sku"], "unit": unit, "cost": cost, "qty": qty,
            "extended": round(unit * qty, 2),
            "margin": margin, "below_floor": margin is not None and margin < MARGIN_FLOOR,
            "basis": ("customer agreement" if agreed is not None else f"{tier} tier ({disc:.0%} off list)")}


# ---------------------------------------------------------------- line matching
#
# Confidence per line. Below threshold the line does not enter a quote — it goes
# to a human with the ambiguity named. A wrongly matched part ships, returns,
# and costs freight both ways, which is why the false-match rate is the eval.

MATCH_THRESHOLD = 0.72

_UOM = {"ea": "ea", "each": "ea", "pc": "ea", "pcs": "ea", "pk": "pk", "pack": "pk",
        "bx": "bx", "box": "bx", "cs": "cs", "case": "cs", "ft": "ft", "feet": "ft",
        "lf": "ft", "roll": "rl", "rl": "rl"}


def normalize_uom(u):
    return _UOM.get((u or "").strip().lower(), (u or "").strip().lower() or None)


def _tokens(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def match_line(raw, catalog, customer, xref):
    """One RFQ line → a match with a confidence and a stated reason.

    Four signals, in order of how much they deserve to be trusted:
      1. the customer's own cross-reference (their part number → our SKU)
      2. an exact SKU hit
      3. this customer's purchase history
      4. description token overlap  ← the weakest, and never enough alone
    """
    desc, cust_pn = raw.get("description", ""), raw.get("customer_part")
    qty = raw.get("qty")
    reasons = []

    if cust_pn:
        hit = next((x for x in xref if x["customer_id"] == customer["id"]
                    and x["customer_part"].lower() == cust_pn.lower()), None)
        if hit:
            row = next((c for c in catalog if c["sku"] == hit["sku"]), None)
            if row:
                return {"sku": row["sku"], "confidence": 0.98, "row": row,
                        "why": f"customer cross-reference: their {cust_pn} is our {row['sku']}",
                        "qty": qty, "uom": normalize_uom(raw.get("uom"))}
        reasons.append(f"their part number {cust_pn} is not in our cross-reference")

    exact = next((c for c in catalog if c["sku"].lower() == (desc or "").strip().lower()), None)
    if exact:
        return {"sku": exact["sku"], "confidence": 0.95, "row": exact,
                "why": "the line is our SKU verbatim", "qty": qty,
                "uom": normalize_uom(raw.get("uom"))}

    bought = [c for c in catalog if c["sku"] in (customer.get("bought") or [])]
    toks = _tokens(desc)
    scored = []
    for row in catalog:
        overlap = len(toks & _tokens(row["description"]))
        if not overlap:
            continue
        base = overlap / max(1, len(toks | _tokens(row["description"])))
        if row in bought:
            score = base + 0.18
            why = f"description overlap, and this customer has bought {row['sku']} before"
        else:
            score = base
            why = "description overlap only"
        scored.append((score, base, row, why))
    if not scored:
        return {"sku": None, "confidence": 0.0, "row": None, "qty": qty,
                "uom": normalize_uom(raw.get("uom")),
                "why": "; ".join(reasons + ["nothing in the catalog matched this description"])}
    scored.sort(key=lambda t: -t[0])
    top, base_top, row, why = scored[0]
    # Ambiguity is judged on the BASE overlap, before the purchase-history boost.
    # Two sizes of the same part are ambiguous whatever this customer bought last
    # time — letting history break a size tie is how you confidently ship the
    # wrong diameter.
    base_runner = max((b for _, b, r, _w in scored[1:]), default=0.0)
    if base_runner and abs(base_top - base_runner) < 0.08:
        other = next(r for _s, b, r, _w in scored[1:] if abs(b - base_runner) < 1e-9)
        return {"sku": None, "confidence": round(min(base_top, 0.6), 2), "row": None, "qty": qty,
                "uom": normalize_uom(raw.get("uom")),
                "why": f"two catalog items score almost the same ({row['sku']} and "
                       f"{other['sku']}) — a human picks, we do not guess"}
    # Description overlap is the weakest signal and is NEVER enough on its own.
    # A near-verbatim description (most of the catalog text present) can clear
    # the bar; a loose word match is capped BELOW the threshold on purpose, so it
    # goes to a human however tempting the top candidate looks. Without this cap
    # a one-word line like "valve" matched a specific SKU because the customer
    # had bought it once — which is precisely the wrong part, confidently.
    NEAR_VERBATIM = 0.6
    if top >= NEAR_VERBATIM:
        conf = round(min(0.94, 0.45 + top), 2)
    else:
        conf = round(min(MATCH_THRESHOLD - 0.02, 0.45 + top), 2)
        why += " — description overlap alone is never enough to price a line"
    return {"sku": row["sku"] if conf >= MATCH_THRESHOLD else None,
            "confidence": conf, "row": row if conf >= MATCH_THRESHOLD else None, "qty": qty,
            "uom": normalize_uom(raw.get("uom")),
            "why": "; ".join(reasons + [why])}


# ---------------------------------------------------------------- substitutions

def substitution_for(row, catalog):
    """A discontinued part gets a PROPOSAL with the spec difference named."""
    if not row or row.get("status") != "discontinued":
        return None
    sup = next((c for c in catalog if c["sku"] == row.get("superseded_by")), None)
    if not sup:
        return {"proposed": None,
                "why": f"{row['sku']} is discontinued and we have no successor on file — "
                       f"a human sources this"}
    diffs = []
    for k in ("spec", "material", "rating", "uom"):
        if row.get(k) != sup.get(k):
            diffs.append({"field": k, "was": row.get(k), "now": sup.get(k)})
    return {"proposed": sup["sku"], "differences": diffs,
            "why": (f"{row['sku']} is discontinued; {sup['sku']} supersedes it"
                    + (f" with {len(diffs)} spec difference(s)" if diffs else " with no spec change")),
            "silent_ok": False}


# ---------------------------------------------------------------- the quote machine

QUOTE_STATES = ("draft", "queued_for_human", "awaiting_approval", "sent", "won", "lost", "expired")
LOSS_REASONS = ("price", "lead_time", "stock", "competitor", "no_decision", "spec_mismatch",
                "customer_cancelled")
QUOTE_TTL_DAYS = 30
FOLLOWUP = [dict(day=2, kind="confirm", note="did it arrive, any questions on the spec"),
            dict(day=7, kind="check", note="still live, or has it gone another way"),
            dict(day=16, kind="last", note="says it is the last note before we close it")]


def quote_state(q, ref=None):
    if q.get("state") in ("won", "lost"):
        return q["state"]
    if q.get("state") in ("queued_for_human", "awaiting_approval", "draft"):
        return q["state"]
    age = -(days_until(q.get("sent_at") or q.get("created_at"), ref) or 0)
    return "expired" if age > QUOTE_TTL_DAYS else "sent"


def due_followups(q, ref=None):
    if quote_state(q, ref) != "sent":
        return []
    age = -(days_until(q.get("sent_at"), ref) or 0)
    sent = {t.get("day") for t in q.get("touches", [])}
    return [t for t in FOLLOWUP if t["day"] <= age and t["day"] not in sent]


# ---------------------------------------------------------------- PO reconciliation

DISCREPANCY_TYPES = ("price", "quantity", "sku", "ship_to", "terms", "date", "uom")


def reconcile(po, quote):
    """Line by line. ANY discrepancy holds the WHOLE order — a partially-correct
    order shipped is worse than an order that waited ten minutes for a human."""
    diffs = []
    qlines = {l["sku"]: l for l in quote.get("lines", [])}
    plines = {l.get("sku"): l for l in po.get("lines", [])}
    for sku, pl in plines.items():
        ql = qlines.get(sku)
        if not ql:
            diffs.append({"type": "sku", "sku": sku,
                          "detail": f"{sku} is on the PO but not on the quote"})
            continue
        if pl.get("qty") != ql.get("qty"):
            diffs.append({"type": "quantity", "sku": sku,
                          "detail": f"PO says {pl.get('qty')}, quote says {ql.get('qty')}"})
        if pl.get("unit") is not None and abs(pl["unit"] - ql["unit"]) > 0.004:
            diffs.append({"type": "price", "sku": sku,
                          "detail": f"PO unit ${pl['unit']}, quoted ${ql['unit']}"})
        if pl.get("uom") and ql.get("uom") and normalize_uom(pl["uom"]) != normalize_uom(ql["uom"]):
            diffs.append({"type": "uom", "sku": sku,
                          "detail": f"PO in {pl['uom']}, quoted in {ql['uom']}"})
    for sku in qlines:
        if sku not in plines:
            diffs.append({"type": "sku", "sku": sku,
                          "detail": f"{sku} was quoted but is not on the PO"})
    if po.get("ship_to") and quote.get("ship_to") and po["ship_to"] != quote["ship_to"]:
        diffs.append({"type": "ship_to", "sku": None,
                      "detail": f"PO ships to '{po['ship_to']}', quote said '{quote['ship_to']}'"})
    if po.get("terms") and quote.get("terms") and po["terms"] != quote["terms"]:
        diffs.append({"type": "terms", "sku": None,
                      "detail": f"PO terms '{po['terms']}', quoted '{quote['terms']}'"})
    return {"clean": not diffs, "discrepancies": diffs,
            "verdict": "order" if not diffs else "exception",
            "why": "matches the quote line for line" if not diffs
                   else f"{len(diffs)} discrepancy(ies) — the WHOLE order holds, not just the line"}


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "parse_rfq":          dict(rung="R3", reason="reading an inbound document and extracting lines commits nobody"),
    "match_line":         dict(rung="R3", reason="proposing a SKU for a line, with its confidence, is a suggestion the desk sees before anything prices"),
    "queue_low_confidence": dict(rung="R3", reason="handing an ambiguous line to a human is always the safe direction"),
    "price_quote":        dict(rung="R2", reason="pricing from the cost file and the customer's own tier, above the margin floor, with no substitutions"),
    "price_below_floor":  dict(rung="R1", reason="a quote under the margin floor is the desk buying business — an owner decides", never_promote=True),
    "propose_substitution": dict(rung="R1", reason="a different part than the one they asked for, with the spec difference named. Never silent, never automatic", never_promote=True),
    "send_quote":         dict(rung="R1", reason="a quote in a customer's hands is a price commitment"),
    "quote_followup":     dict(rung="R2", reason="asking whether a quote we already sent is still live"),
    "close_quote_lost":   dict(rung="R2", reason="recording a loss with a structured reason; reopening is one click"),
    "write_order":        dict(rung="R2", reason="only from a PO that reconciles to the quote line for line"),
    "write_discrepant_order": dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. A PO that does not match the quote holds as an exception — the whole order, not just the line", never_promote=True),
    "cross_customer_price": dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. One customer's agreement cannot price another, and the code has no path that would allow it", never_promote=True),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"parse_rfq", "match_line", "queue_low_confidence", "price_quote",
                "price_below_floor", "propose_substitution", "send_quote", "quote_sent",
                "quote_followup", "close_quote_lost", "write_order"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("customer:",))


# ---------------------------------------------------------------- evals

MATCH_EVAL = Eval(
    "line matching", "queue",
    "a wrongly matched part ships, comes back, and costs freight both ways — the false-match rate "
    "is what this measures, so lines that should have gone to a human are counted alone")


def eval_matching():
    catalog = store.load("catalog") or _demo_catalog()
    cust = {"id": "c_eval", "tier": "standard", "bought": ["SKU-1001"], "agreement": {}}
    xref = [{"customer_id": "c_eval", "customer_part": "YOURCO-77", "sku": "SKU-1001"}]
    cases = [
        ({"description": "YOURCO-77", "customer_part": "YOURCO-77", "qty": 10}, "match"),
        ({"description": "SKU-1001", "qty": 5}, "match"),
        ({"description": "1/2 in brass ball valve threaded", "qty": 4}, "match"),
        ({"description": "widget", "qty": 1}, "queue"),
        ({"description": "", "qty": 1}, "queue"),
        ({"description": "part per drawing", "qty": 2}, "queue"),
        ({"description": "valve", "qty": 3}, "queue"),
        ({"description": "misc hardware as discussed", "qty": 9}, "queue"),
    ]
    keyed = {i: c for i, (c, _) in enumerate(cases)}

    def predict(i):
        m = match_line(keyed[i], catalog, cust, xref)
        return "match" if (m["sku"] and m["confidence"] >= MATCH_THRESHOLD) else "queue"

    return MATCH_EVAL.run([{"input": i, "label": l} for i, (_, l) in enumerate(cases)], predict)


def _demo_catalog():
    return [
        {"sku": "SKU-1001", "description": "1/2 in brass ball valve threaded", "list": 18.4,
         "cost": 11.2, "status": "active", "uom": "ea"},
        {"sku": "SKU-1002", "description": "3/4 in brass ball valve threaded", "list": 24.1,
         "cost": 15.0, "status": "active", "uom": "ea"},
    ]


# ---------------------------------------------------------------- the desk board

def desk_board(ref=None):
    ref = ref or now()
    quotes = store.load("quotes")
    today = [q for q in quotes if (parse(q.get("created_at")) or ref).date() == ref.date()]
    return {
        "generated": iso(ref),
        "today": {"rfqs": len(today),
                  "auto_drafted": sum(1 for q in today if q.get("state") in ("awaiting_approval", "sent")),
                  "human_queue": sum(1 for q in today if q.get("state") == "queued_for_human"),
                  "needs_margin_approval": sum(1 for q in today if q.get("below_floor"))},
        "turnaround": turnaround(quotes, ref),
        "open_value": open_quote_value(quotes, ref),
        "exceptions": len([p for p in store.load("pos") if p.get("verdict") == "exception"]),
        "automation": automation(),
    }


def turnaround(quotes=None, ref=None, floor=10):
    quotes = quotes if quotes is not None else store.load("quotes")
    hrs = []
    for q in quotes:
        a, b = parse(q.get("created_at")), parse(q.get("sent_at"))
        if a and b:
            hrs.append(round((b - a).total_seconds() / 3600, 2))
    if len(hrs) < floor:
        return unmeasured(f"only {len(hrs)} quotes with both a receipt and a send time; need {floor}",
                          field="median_hours", n=len(hrs))
    return {"median_hours": round(median(hrs), 2), "n": len(hrs)}


def open_quote_value(quotes=None, ref=None):
    quotes = quotes if quotes is not None else store.load("quotes")
    live = [q for q in quotes if quote_state(q, ref) == "sent"]
    if not live:
        return unmeasured("no quotes in a sent state", field="amount", n=0)
    return {"amount": round(sum(q.get("total", 0) for q in live), 2), "n": len(live)}


# ---------------------------------------------------------------- the margin ledger

def margin_ledger(min_sample=8):
    """Did faster quoting or deeper discounting win more? From recorded outcomes
    only — a thin cell is blank, never computed."""
    quotes = [q for q in store.load("quotes") if q.get("state") in ("won", "lost")]
    by_depth, by_speed, by_family = {}, {}, {}
    for q in quotes:
        d = q.get("discount_depth")
        if d is not None:
            bucket = "0-5%" if d < 0.05 else "5-10%" if d < 0.10 else "10-20%" if d < 0.20 else "20%+"
            by_depth.setdefault(bucket, []).append(q["state"] == "won")
        t = q.get("turnaround_hours")
        if t is not None:
            bucket = "<4h" if t < 4 else "4-24h" if t < 24 else "1-3d" if t < 72 else "3d+"
            by_speed.setdefault(bucket, []).append(q["state"] == "won")
        for f in {l.get("family") for l in q.get("lines", []) if l.get("family")}:
            by_family.setdefault(f, []).append(q["state"] == "won")

    def summarize(d):
        return {k: ({"win_rate": round(sum(v) / len(v), 3), "n": len(v)} if len(v) >= min_sample
                    else unmeasured(f"only {len(v)} decided quotes in this bucket; need {min_sample}",
                                    field="win_rate", n=len(v)))
                for k, v in sorted(d.items())}

    return {"by_discount_depth": summarize(by_depth), "by_turnaround": summarize(by_speed),
            "by_family": summarize(by_family), "decided_quotes": len(quotes),
            "loss_reasons": {r: sum(1 for q in quotes if q.get("loss_reason") == r)
                             for r in LOSS_REASONS}}


# ---------------------------------------------------------------- ROI

ROI = (Roi("What the two clocks are worth here")
       .line("Quote capacity", "time_saved",
             "RFQs/wk × hours saved each × 48 × loaded desk rate",
             ["rfqs_wk", "hours_saved_per_quote", "loaded_rate"],
             lambda g: g["rfqs_wk"] * g["hours_saved_per_quote"] * 48 * g["loaded_rate"],
             note="RFQ volume is counted from your own inbox")
       .line("Order-entry time", "time_saved",
             "POs/wk × minutes each × 48 × loaded rate",
             ["pos_wk", "minutes_per_po", "loaded_rate"],
             lambda g: g["pos_wk"] * (g["minutes_per_po"] / 60) * 48 * g["loaded_rate"])
       .line("Error avoidance", "revenue",
             "order errors/mo × cost per error × 12",
             ["order_errors_month", "cost_per_error"],
             lambda g: g["order_errors_month"] * g["cost_per_error"] * 12,
             assumption="cost per error is yours: rework plus freight both ways plus the credit")
       .line("Win-rate lift from faster quoting", "revenue",
             "needs 90 days of recorded quote outcomes",
             ["win_rate_lift_evidence"],
             lambda g: g["win_rate_lift_evidence"],
             note="WE WILL NOT PUT A NUMBER HERE FROM AN INDUSTRY STATISTIC. This line stays blank "
                  "until your own margin ledger can answer whether faster quoting won you more — "
                  "which takes about 90 days of recorded outcomes"))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    rfqs = store.load("rfqs")
    wk = [r for r in rfqs if (parse(r.get("at")) or now()) >= now() - timedelta(days=7)]
    if wk:
        recorded["rfqs_wk"] = len(wk)
    pos = [p for p in store.load("pos") if (parse(p.get("at")) or now()) >= now() - timedelta(days=7)]
    if pos:
        recorded["pos_wk"] = len(pos)
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    # The win-rate line is never satisfiable from config — only from a real ledger.
    merged.pop("win_rate_lift_evidence", None)
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
