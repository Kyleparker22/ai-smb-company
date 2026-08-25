#!/usr/bin/env python3
"""Counter OS — domain core (wholesale distribution · the "No" meter).

The thesis: a distributor's biggest leak is a sentence, not a transaction.
"We don't carry that" and "we're out" leave no record, so stocking and vendor
decisions run on gut. This core captures every no, prices it from a RECORDED
comparable or refuses to, and lets the counted ledger — never an anecdote —
draft the stocking case, the reorder-point autopsy, and the vendor packet.

Four prohibitions are rules here, not discipline:
  1. A no with no recorded comparable is COUNTED, never dollared. UNPRICED is
     a first-class result — a counted mystery beats an invented dollar.
  2. A stocking case drafts only when the counted ledger crosses the recorded
     threshold. The case creator recounts the ledger itself; there is no
     argument, and no other function, that can force a case from an anecdote.
  3. "Do you have X" is answered from the counted stock record or with an
     honest no. Optimism ("should have some in back") cannot be produced.
  4. The vendor packet is the counted ledger verbatim. No invented fill
     rates, no industry stats — what we cannot count is not in the packet.

Stdlib only. Honesty rules come from `_kit`.
"""
import math as _math
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, now,           # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "catalog", "vendors", "nos", "cases", "messages",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="COUNTEROS_DATA_ROOT")

NO_KINDS = ("not_carried", "out_of_stock", "wrong_size")
UNPRICED_PHRASE = "a counted mystery beats an invented dollar"


# ---------------------------------------------------------------- recorded config

DEFAULT_THRESHOLD = {
    "_source": ("DEFAULT stocking threshold — replace with the number the owner actually "
                "adopts before go-live. The point is that it is RECORDED, so the case "
                "creator can print its arithmetic instead of arguing taste."),
    "count": 5, "window_days": 60,
}

DEFAULT_SAFETY = {
    "_source": ("DEFAULT safety stock — days of pace held back for variance. Replace with "
                "the operator's own number before go-live; the autopsy prints it either way."),
    "days": 2,
}

DEFAULT_CATEGORY_MARGINS = {
    "_source": ("recorded average margin dollars per counter sale, by category, from the "
                "operator's own sales export (synthetic here) — never an industry stat"),
    "margins": {},
}


def stocking_threshold():
    return store.load("config").get("stocking_threshold") or DEFAULT_THRESHOLD


def safety_stock():
    return store.load("config").get("safety_days") or DEFAULT_SAFETY


def category_margins():
    return store.load("config").get("category_margins") or DEFAULT_CATEGORY_MARGINS


# ---------------------------------------------------------------- the ledger

def _norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def recent_nos(window_days, kinds=None, ref=None):
    """The counted ledger, demo fixtures excluded. Every read in this file that
    claims to be counted goes through here."""
    ref = ref or now()
    cutoff = ref - timedelta(days=window_days)
    rows = []
    for n in store.load("nos"):
        if n.get("demo_tag"):
            continue
        if kinds and n.get("kind") not in kinds:
            continue
        at = parse(n.get("at"))
        if at and cutoff <= at <= ref:
            rows.append(n)
    return rows


def price_no(no, catalog_ix=None):
    """Dollars only from a RECORDED comparable: the catalog item's own margin,
    or a recorded category margin. Anything else is UNPRICED — counted, not
    dollared; a counted mystery beats an invented dollar."""
    qty = no.get("qty") or 1
    ix = catalog_ix if catalog_ix is not None else store.index("catalog", "sku")
    row = ix.get(no.get("sku")) if no.get("sku") else None
    if row and row.get("list") is not None and row.get("cost") is not None:
        unit = round(row["list"] - row["cost"], 2)
        return {"priced": True, "dollars": round(unit * qty, 2),
                "basis": (f"catalog margin on {row['sku']}: (${row['list']:.2f} list − "
                          f"${row['cost']:.2f} cost) × {qty} = ${unit * qty:.2f}")}
    cm = category_margins()
    cat = no.get("category")
    if cat and cat in (cm.get("margins") or {}):
        m = cm["margins"][cat]
        return {"priced": True, "dollars": round(m * qty, 2),
                "basis": (f"recorded category margin for '{cat}': ${m:.2f} × {qty} — "
                          f"source: {cm['_source']}")}
    return {"priced": False, "dollars": None,
            "why": (f"no recorded comparable (no catalog SKU, no recorded category margin) — "
                    f"counted, not dollared; {UNPRICED_PHRASE}")}


def no_board(window_days=7, ref=None):
    """This week's no's, counted. Priced from recorded comparables only; the
    rest read UNPRICED, loudly."""
    ref = ref or now()
    rows = recent_nos(window_days, ref=ref)
    ix = store.index("catalog", "sku")
    priced_d, priced_n, unpriced_n = 0.0, 0, 0
    by_kind = {k: 0 for k in NO_KINDS}
    by_branch, walked = {}, 0
    groups = {}
    for n in rows:
        p = price_no(n, ix)
        if p["priced"]:
            priced_n += 1
            priced_d += p["dollars"]
        else:
            unpriced_n += 1
        by_kind[n["kind"]] = by_kind.get(n["kind"], 0) + 1
        by_branch[n.get("branch") or "?"] = by_branch.get(n.get("branch") or "?", 0) + 1
        walked += n.get("walked_or_waited") == "walked"
        g = groups.setdefault(_norm(n.get("item_asked")), {"item": n.get("item_asked"),
                                                           "count": 0, "dollars": 0.0,
                                                           "unpriced": 0})
        g["count"] += 1
        if p["priced"]:
            g["dollars"] = round(g["dollars"] + p["dollars"], 2)
        else:
            g["unpriced"] += 1
    top = sorted(groups.values(), key=lambda g: -g["count"])[:8]
    return {"window_days": window_days, "count": len(rows), "walked": walked,
            "priced": {"n": priced_n, "dollars": round(priced_d, 2),
                       "basis": "recorded comparables only — catalog or category margin"},
            "unpriced": {"n": unpriced_n,
                         "note": f"counted, not dollared — {UNPRICED_PHRASE}"},
            "by_kind": by_kind, "by_branch": by_branch, "top_items": top,
            "note": "counted from the ledger — never asserted"}


# ---------------------------------------------------------------- the stocking case
#
# The threshold check is STRUCTURAL: this function recounts the ledger itself.
# There is no count argument a caller could inflate and no force path anywhere
# in this build — an anecdote cannot draft a case because no code accepts one.

def counted_nos_for(item, window_days, ref=None):
    key = _norm(item)
    return [n for n in recent_nos(window_days, kinds=("not_carried", "wrong_size"), ref=ref)
            if _norm(n.get("item_asked")) == key]


def stocking_case_check(item, ref=None):
    th = stocking_threshold()
    rows = counted_nos_for(item, th["window_days"], ref=ref)
    ok = len(rows) >= th["count"]
    arithmetic = (f"{len(rows)} counted no's for '{item}' in the last {th['window_days']} days "
                  f"{'≥' if ok else '<'} the recorded threshold of {th['count']} in "
                  f"{th['window_days']} — source: {th['_source']}")
    return ok, rows, arithmetic, th


def stocking_candidates(ref=None):
    """Every distinct asked-for item in the window, with its count against the
    recorded threshold. The board's threshold watch."""
    th = stocking_threshold()
    groups = {}
    for n in recent_nos(th["window_days"], kinds=("not_carried", "wrong_size"), ref=ref):
        g = groups.setdefault(_norm(n.get("item_asked")),
                              {"item": n.get("item_asked"), "count": 0})
        g["count"] += 1
    out = sorted(groups.values(), key=lambda g: -g["count"])
    for g in out:
        g["crossed"] = g["count"] >= th["count"]
        g["arithmetic"] = (f"{g['count']} {'≥' if g['crossed'] else '<'} {th['count']} "
                           f"in {th['window_days']}d")
    return {"threshold": th, "rows": out}


def vendor_options(category):
    """Recorded vendors that carry the category, with their recorded lead times.
    No recorded vendor → an empty list and a human sources; nothing is invented."""
    if not category:
        return {"options": [], "note": "no recorded category on these no's — a human sources"}
    opts = [{"vendor": v["id"], "name": v["name"], "lead_time_days": v.get("lead_time_days"),
             "rep": v.get("rep")}
            for v in store.load("vendors") if category in (v.get("lines") or [])]
    if not opts:
        return {"options": [], "note": f"no recorded vendor carries '{category}' — a human sources"}
    return {"options": opts, "note": "recorded vendors and recorded lead times only"}


# ---------------------------------------------------------------- the OOS autopsy
#
# An out-of-stock no on an item we DO carry is not bad luck — it is the counted
# cost of a reorder point the recorded pace beat. The autopsy proposes the new
# point WITH the arithmetic, and refuses when an input is not recorded.

def oos_autopsy(sku, window_days=60, ref=None):
    row = next((c for c in store.load("catalog") if c.get("sku") == sku), None)
    if not row:
        return {"error": f"{sku} is not in the catalog — an autopsy needs a carried item"}
    oos = [n for n in recent_nos(window_days, kinds=("out_of_stock",), ref=ref)
           if n.get("sku") == sku]
    if not oos:
        return {"refused": (f"no counted out-of-stock no's for {sku} in {window_days} days — "
                            f"an autopsy without counted no's is a guess")}
    missing = [k for k, v in (("pace_per_day", row.get("pace_per_day")),
                              ("reorder_point", row.get("reorder_point"))) if v is None]
    vendor = next((v for v in store.load("vendors") if v["id"] == row.get("vendor")), None)
    lead = (vendor or {}).get("lead_time_days")
    if lead is None:
        missing.append("vendor lead time")
    if missing:
        return {"refused": (f"cannot propose a reorder point for {sku} — not recorded: "
                            f"{', '.join(missing)}. The math needs its inputs; a proposed "
                            f"point without them is the optimism this build exists to kill")}
    safety = safety_stock()
    pace, rp = row["pace_per_day"], row["reorder_point"]
    proposed = _math.ceil(pace * (lead + safety["days"]))
    walked = [n for n in oos if n.get("walked_or_waited") == "walked"]
    unit = round(row["list"] - row["cost"], 2)
    walked_units = sum(n.get("qty") or 1 for n in walked)
    return {
        "sku": sku, "description": row.get("description"),
        "counted_oos_nos": len(oos), "walked": len(walked),
        "walked_cost": {"dollars": round(walked_units * unit, 2),
                        "basis": (f"{walked_units} walked unit(s) × ${unit:.2f} recorded "
                                  f"margin on {sku} — counted from the ledger")},
        "recorded_point": rp, "proposed_point": proposed,
        "math": (f"pace {pace}/day × (lead {lead}d + safety {safety['days']}d) = "
                 f"{pace * (lead + safety['days']):.1f} → propose {proposed}; the recorded "
                 f"point was {rp} and the recorded pace beat it"),
        "pace_basis": row.get("pace_basis") or "recorded on the catalog row",
        "safety_source": safety["_source"],
        "history": oos,
        "note": "a DRAFT for a human decision — changing a reorder point commits cash to shelf",
    }


# ---------------------------------------------------------------- the vendor packet
#
# Verbatim ledger rows only. A fill *rate* needs a denominator this ledger does
# not record, so the packet never states one — what we cannot count is not here.

def vendor_packet(vendor_id, window_days=60, ref=None):
    v = store.by_id("vendors", vendor_id)
    if not v:
        return {"error": "no such vendor"}
    ix = store.index("catalog", "sku")
    skus = {c["sku"] for c in store.load("catalog") if c.get("vendor") == vendor_id}
    rows = [n for n in recent_nos(window_days, kinds=("out_of_stock",), ref=ref)
            if n.get("sku") in skus]
    walked = [n for n in rows if n.get("walked_or_waited") == "walked"]
    walked_cost = 0.0
    for n in walked:
        p = price_no(n, ix)
        if p["priced"]:
            walked_cost += p["dollars"]
    return {
        "vendor": vendor_id, "name": v["name"], "window_days": window_days,
        "rows": rows,
        "counted": {"fill_failures": len(rows), "walked": len(walked),
                    "waited": len(rows) - len(walked),
                    "walked_margin_dollars": round(walked_cost, 2)},
        "rule": ("verbatim ledger rows only — nothing in this packet is a rate, an estimate, "
                 "or an industry stat. A fill rate needs a denominator this ledger does not "
                 "record, so none is stated; what we cannot count is not in the packet"),
        "note": "a DRAFT for a human to take into the negotiation — never sent by software",
    }


# ---------------------------------------------------------------- stock answers
#
# "Do you have X" is answered from the counted stock record or with an honest
# no. The copy runs its own optimism check structurally before it ships.

OPTIMISM = ("should have", "probably", "pretty sure", "might have", "usually have",
            "i think we", "almost certainly", "im sure we", "i'm sure we")


def optimism_ok(text):
    t = (text or "").lower()
    hits = [w for w in OPTIMISM if w in t]
    if hits:
        return False, f"optimism refused — forbidden language: {', '.join(hits)}"
    return True, "ok"


def _tokens(s):
    out = set()
    for t in re.findall(r"[a-z0-9]+", (s or "").lower()):
        if len(t) > 3 and t.endswith("s"):
            t = t[:-1]
        out.add(t)
    return out


def find_item(query):
    """Best catalog match by description-token containment. Deliberately strict:
    a loose match answers about the wrong part, confidently."""
    qt = _tokens(query)
    best, best_key = None, (0.0, 0, 0)
    for row in store.load("catalog"):
        dt = _tokens(row.get("description"))
        if not dt:
            continue
        ov = len(qt & dt) / len(dt)
        key = (ov, len(qt & dt), len(dt))
        if key > best_key:
            best_key, best = key, row
    return best if best_key[0] >= 0.75 else None


def stock_answer(query, ref=None):
    """Counted stock or the honest no. Never optimism, never 'in back'."""
    as_of = store.load("config").get("counts_as_of") or "the last recorded count"
    row = find_item(query)
    if not row:
        ans = ("Straight answer: that is not something we carry — no guessing, no 'let me "
               "see what's in back'. The ask goes into the counted ledger the moment it is "
               "said; enough counted no's and the stocking case drafts itself from the "
               "arithmetic, not from anyone's memory of being asked.")
        okp, why = optimism_ok(ans)
        assert okp, why  # structural: the shipped copy passes its own check
        return {"carried": False, "answer": ans, "capture": "not_carried"}
    counts = row.get("on_hand") or {}
    total = sum(counts.values())
    per = " · ".join(f"{b}: {n}" for b, n in counts.items())
    if total > 0:
        ans = (f"Yes — counted stock on {row['sku']} ({row['description']}): {per}, as of "
               f"{as_of}. That is the shelf record, not a hunch; we will hold it at the "
               f"counter on your word.")
        capture = None
    else:
        ans = (f"Honest no — the counted record on {row['sku']} ({row['description']}) says "
               f"zero at every branch as of {as_of}. Nobody here will send your crew to an "
               f"empty shelf on a hunch about the back room. This miss is itself logged as a "
               f"counted no, and the reorder-point autopsy runs from exactly these.")
        capture = "out_of_stock"
    okp, why = optimism_ok(ans)
    assert okp, why
    return {"carried": True, "sku": row["sku"], "counts": counts, "as_of": as_of,
            "answer": ans, "capture": capture}


# ---------------------------------------------------------------- triage
#
# The contractor-down emergency reads FIRST — a crew standing around is the
# call that decides whose number they dial next time.

CONTRACTOR_DOWN = (
    r"\b(crew|guys?|job ?site|jobsite|job|site) (is |are )?(standing|sitting|stalled|down|waiting)",
    r"\bright now\b",
    r"\bneed .{0,30}\btoday\b",
    r"\bemergency\b",
    r"\bdown until\b",
)
NO_REPORT = (
    r"\b(don'?t|do not|didn'?t|did not) (carry|have|stock)\b",
    r"\bwe (were|are|'re|ran) out\b",
    r"\bturned away\b",
    r"\b(he|she|they|customer|guy) walked\b",
    r"\bout of stock\b",
)
PRICE_ASK = (r"\bprice on\b", r"\bhow much\b", r"\bquote\b", r"\bpricing\b")
WILLCALL = (r"\bwill[ -]?call\b", r"\border\b.{0,24}\bready\b", r"\bready for pickup\b")


def read_message(text):
    """contractor_down | no_report | price_ask | willcall | human. The
    contractor-down reads first — answered from counted stock, never optimism."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in CONTRACTOR_DOWN:
        if re.search(rx, t):
            return {"label": "contractor_down",
                    "why": "a crew is standing around — answered from counted stock only; "
                           "an optimistic guess here costs them the trip and us the account"}
    for rx in NO_REPORT:
        if re.search(rx, t):
            return {"label": "no_report",
                    "why": "a no said at the counter — captured into the ledger; the capture "
                           "IS the product"}
    for rx in PRICE_ASK:
        if re.search(rx, t):
            return {"label": "price_ask",
                    "why": "price/quote ask — answered from recorded list and counted stock"}
    for rx in WILLCALL:
        if re.search(rx, t):
            return {"label": "willcall", "why": "will-call status — checked against the order "
                                                "record by a person; no invented status"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("counter triage",
                   costly_label="contractor_down",
                   costly_note=("A CREW STANDING AROUND IS THE CALL THAT DECIDES WHOSE NUMBER "
                                "THEY DIAL NEXT TIME — it must reach the counted-stock answer, "
                                "never an optimistic guess. Over-routing a price ask costs a read."))

EVAL_CASES = [
    {"input": "my crew is standing around, do you have 2 in EMT connectors RIGHT NOW",
     "label": "contractor_down"},
    {"input": "job is down until we get a 3/4 pex crimp tool, need it today",
     "label": "contractor_down"},
    {"input": "emergency — the site needs 200 ft of 12/2 MC right now",
     "label": "contractor_down"},
    {"input": "customer asked for a ridgeline press jaw, we don't carry it", "label": "no_report"},
    {"input": "we were out of 2 in emt connectors again, he walked", "label": "no_report"},
    {"input": "turned away another guy asking for pex crimp rings", "label": "no_report"},
    {"input": "didn't have the 6 in dwv coupling in stock", "label": "no_report"},
    {"input": "price on 500 ft of 12/2 romex", "label": "price_ask"},
    {"input": "how much for a case of pvc primer", "label": "price_ask"},
    {"input": "can you quote 40 sticks of 2 in rigid", "label": "price_ask"},
    {"input": "is my will call order ready", "label": "willcall"},
    {"input": "order 5512 ready for pickup?", "label": "willcall"},
    {"input": "", "label": "human"},
    {"input": "what time do you open saturday", "label": "human"},
    {"input": "who do I talk to about a return", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the contractor-down reads first"},
    "log_no":              {"rung": "R2", "reason": "the capture IS the product — a no not written down is the leak itself; seconds matter at the counter"},
    "price_no_without_comparable": {"rung": "R0", "reason": "counted, never dollared without a recorded basis — a counted mystery beats an invented dollar", "never_promote": True},
    "stocking_case_below_threshold": {"rung": "R0", "reason": "one loud contractor asking twice is an anecdote, not demand — structural: the case creator recounts the counted ledger itself and no force path exists", "never_promote": True},
    "stock_answer_optimism": {"rung": "R0", "reason": "'should have some in back' is how a crew drives forty minutes for nothing — answers cite counted stock only", "never_promote": True},
    "invent_vendor_stats": {"rung": "R0", "reason": "the packet is the counted ledger verbatim — an invented fill rate hands the rep the rebuttal that sinks the whole file", "never_promote": True},
    "draft_stocking_case": {"rung": "R1", "reason": "money onto a shelf — a human commits the inventory dollars, with the threshold arithmetic attached"},
    "draft_reorder_autopsy": {"rung": "R1", "reason": "changing a reorder point commits cash to stock — a human decides, with the pace × lead-time math shown"},
    "draft_vendor_packet": {"rung": "R1", "reason": "outward to a vendor rep — a human sends; the counted rows do the talking"},
    "draft_counter_reply": {"rung": "R1", "reason": "outward reply — a human sends; counts and recorded prices only"},
})
gate = Gate(store, matrix)

MOVING = ("read_message", "log_no", "draft_stocking_case", "draft_reorder_autopsy",
          "draft_vendor_packet", "draft_counter_reply")


def automation():
    return automation_rate(store.events(), MOVING,
                           exclude_actors=("contractor:", "customer:"))


# ---------------------------------------------------------------- the counted week

def counted_week(ref=None):
    """This week's counted no's against the counted baseline of the prior eight
    weeks. Both sides counted; a thin baseline is named, never assumed."""
    ref = ref or now()
    ix = store.index("catalog", "sku")

    def bucket(rows):
        d = 0.0
        unpriced = 0
        for n in rows:
            p = price_no(n, ix)
            if p["priced"]:
                d += p["dollars"]
            else:
                unpriced += 1
        return {"count": len(rows), "priced_dollars": round(d, 2), "unpriced": unpriced}

    all_rows = recent_nos(63, ref=ref)
    week, prior = [], []
    for n in all_rows:
        age = (ref - parse(n["at"])).days
        (week if age < 7 else prior).append(n)
    this_week = bucket(week)
    if len(prior) < 25:
        return {"this_week": this_week,
                "baseline": unmeasured(f"only {len(prior)} counted no's in the prior 8 weeks; "
                                       f"need 25 to state a baseline", field="weekly_avg"),
                "delta": unmeasured("no baseline to compare against", field="count"),
                "note": "counted from the ledger — never asserted"}
    pb = bucket(prior)
    baseline = {"weekly_avg": round(pb["count"] / 8, 1),
                "weekly_priced_dollars": round(pb["priced_dollars"] / 8, 2),
                "weeks": 8}
    return {"this_week": this_week, "baseline": baseline,
            "delta": {"count": round(this_week["count"] - baseline["weekly_avg"], 1),
                      "priced_dollars": round(this_week["priced_dollars"]
                                              - baseline["weekly_priced_dollars"], 2)},
            "note": "counted from the ledger — never asserted"}


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Counter OS — what the counted no's are worth")
        .line("Captured demand", "revenue",
              "counted priced-no margin (60d) × 365/60 × your capture rate after stocking",
              ["priced_no_dollars_60d", "capture_rate"],
              lambda g: float(g["priced_no_dollars_60d"]) * (365 / 60) * float(g["capture_rate"]),
              note="the priced-no dollars are counted from the ledger; the capture rate is your call")
        .line("OOS walks recovered", "revenue",
              "counted walked-OOS margin (60d) × 365/60 × the share better reorder points recover",
              ["walked_oos_dollars_60d", "recovery_share"],
              lambda g: float(g["walked_oos_dollars_60d"]) * (365 / 60) * float(g["recovery_share"]),
              note="the walked cost is counted; how much a better reorder point recovers is yours")
        .line("Counter seconds", "time_saved",
              "captures/wk × seconds saved each ÷ 3600 × 52 × loaded rate",
              ["captures_wk", "seconds_saved", "loaded_rate"],
              lambda g: float(g["captures_wk"]) * (float(g["seconds_saved"]) / 3600) * 52
                        * float(g["loaded_rate"]),
              note="capture must cost less than the no itself — that is the design constraint, "
                   "and this line proves it either way")
        .line("Vendor concessions", "scenario",
              "you decide what the counted packet is worth across a negotiation",
              ["vendor_concession_value"], lambda g: float(g["vendor_concession_value"]),
              assumption="never a saving — a concession not yet won is not our number"))


def roi(given):
    ix = store.index("catalog", "sku")
    rec = {}
    rows60 = recent_nos(60)
    priced = walked_oos = 0.0
    for n in rows60:
        p = price_no(n, ix)
        if p["priced"]:
            priced += p["dollars"]
            if n["kind"] == "out_of_stock" and n.get("walked_or_waited") == "walked":
                walked_oos += p["dollars"]
    if rows60:
        rec["priced_no_dollars_60d"] = round(priced, 2)
        rec["walked_oos_dollars_60d"] = round(walked_oos, 2)
    wk = recent_nos(7)
    if wk:
        rec["captures_wk"] = len(wk)
    # The concession line is never satisfiable from recorded data — only a human
    # who just left the negotiation can put a number on it, so it merges from
    # `given` alone and stays blank otherwise.
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out
