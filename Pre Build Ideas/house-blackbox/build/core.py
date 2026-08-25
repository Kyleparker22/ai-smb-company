#!/usr/bin/env python3
"""Blackbox OS — domain core (HVAC & plumbing evidence-priced memberships).

Rules live here: the house black box (per-home equipment ledger — an age nobody
recorded reads UNKNOWN, never guessed), the evidence-priced membership quote
(every factor enumerated in dollars from the RECORDED pricing table, or a flat
provisional plan with the reason named), the re-price clock (renewal only —
mid-term there is deliberately NO code path), the honesty board (renewal prices
that went DOWN, counted), triage with the no-heat/gas-smell emergency first,
and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "homes", "members", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="BLACKBOXOS_DATA_ROOT")

# ---------------------------------------------------------------- the pricing table

DEFAULT_PRICING = {
    "_source": ("DEFAULT evidence-pricing table, simplified — replace with the rates the "
                "company actually adopts before go-live. Every dollar on a quote traces to "
                "a row in this table; there is no other source of price."),
    "base_monthly": 18.0,
    "provisional_monthly": 24.0,
    # per component kind: [[min_age_years, $/mo]] ascending — the highest band crossed applies
    "age_bands": {
        "furnace":      [[0, 0], [8, 3], [15, 9]],
        "ac":           [[0, 0], [8, 2], [15, 7]],
        "water_heater": [[0, 0], [6, 2], [10, 5]],
        "plumbing":     [[0, 0], [20, 3], [40, 6]],
    },
    "callback_per_incident": 2.0,   # per callback inside the window
    "clean_history_credit": -4.0,   # zero callbacks inside the window
    "callback_window_months": 36,
}


def pricing_table():
    return store.load("config").get("pricing_table") or DEFAULT_PRICING


# ---------------------------------------------------------------- the black box

def callbacks_in_window(home, ref=None):
    """Counted from the recorded service history — never estimated."""
    ref = ref or now()
    months = pricing_table()["callback_window_months"]
    cutoff = ref - timedelta(days=months * 30)
    n = 0
    for c in home.get("components") or []:
        for s in c.get("service") or []:
            if s.get("kind") == "callback" and (parse(s.get("at")) or ref) >= cutoff:
                n += 1
    return n


def blackbox(home, ref=None):
    """The flight recorder, read honestly: every component with its recorded
    install year — or UNKNOWN, because an age nobody recorded is not an age."""
    ref = ref or now()
    rows = []
    for c in home.get("components") or []:
        iy = c.get("install_year")
        service = c.get("service") or []
        rows.append({
            "kind": c["kind"],
            "install_year": iy,
            "age_years": (ref.year - int(iy)) if iy else None,
            "age_label": f"{ref.year - int(iy)} years" if iy else "UNKNOWN — install year never recorded",
            "service_visits": sum(1 for s in service if s.get("kind") == "maintenance"),
            "callbacks": sum(1 for s in service if s.get("kind") == "callback"),
        })
    return {"home": home["id"], "owner": home.get("owner"), "address": home.get("address"),
            "components": rows,
            "callbacks_in_window": callbacks_in_window(home, ref),
            "note": "an UNKNOWN stays UNKNOWN — inventing a component age is prohibited (R0)"}


# ---------------------------------------------------------------- the evidence-priced quote

def membership_quote(home, ref=None):
    """price = recorded base + per-component factors from the RECORDED table.
    Every factor comes back as {label, dollars, why} — the quote is the full
    enumeration or it is not a personalized quote at all: a home with any
    unrecorded component age gets the flat PROVISIONAL rate with the reason
    named, never a fake personalized price."""
    ref = ref or now()
    p = pricing_table()
    comps = home.get("components") or []
    unknown = [c["kind"] for c in comps if c.get("install_year") in (None, "")]
    if not comps:
        unknown = ["no components recorded at all"]
    if unknown:
        return {"home": home["id"], "provisional": True,
                "monthly": round(float(p["provisional_monthly"]), 2),
                "unknown_components": unknown,
                "factors": [],
                "reason": (f"install year not recorded for: {', '.join(unknown)}. An age we do "
                           f"not have cannot price a personalized plan, and inventing one is "
                           f"prohibited. This is the flat recorded provisional rate until the "
                           f"record is complete — one free record visit closes the gap."),
                "table_source": p["_source"],
                "note": "PROVISIONAL — no per-component factors are shown because none can be computed honestly"}
    factors = [{"label": "base plan", "dollars": round(float(p["base_monthly"]), 2),
                "why": "the recorded base rate every membership starts from"}]
    for c in comps:
        age = ref.year - int(c["install_year"])
        band_min, dollars = 0, 0.0
        for bmin, d in p["age_bands"].get(c["kind"], [[0, 0]]):
            if age >= bmin:
                band_min, dollars = bmin, float(d)
        why = (f"your {c['kind'].replace('_', ' ')} is {age} years old (installed "
               f"{c['install_year']}) — " + (f"the {band_min}-year band" if band_min
                                             else "inside the youngest band, no surcharge"))
        factors.append({"label": f"{c['kind']} age", "dollars": round(dollars, 2),
                        "kind": c["kind"], "age": age, "band": band_min, "why": why})
    cb = callbacks_in_window(home, ref)
    if cb:
        factors.append({"label": "callback history",
                        "dollars": round(cb * float(p["callback_per_incident"]), 2),
                        "why": (f"{cb} callback(s) in the last {p['callback_window_months']} "
                                f"months: +${p['callback_per_incident']:.0f}/mo each")})
    else:
        factors.append({"label": "clean history",
                        "dollars": round(float(p["clean_history_credit"]), 2),
                        "why": f"zero callbacks in the last {p['callback_window_months']} months"})
    monthly = round(sum(f["dollars"] for f in factors), 2)
    return {"home": home["id"], "provisional": False, "monthly": monthly, "factors": factors,
            "table_source": p["_source"],
            "note": "every factor is enumerated — a quote that hides a factor cannot be produced"}


def quote_complete(q):
    """The structural half of hide_pricing_factor: a personalized quote's price
    IS the sum of its shown factors, to the cent, or it is not a quote."""
    if q.get("provisional"):
        return True, "provisional — a flat recorded rate with the reason named, no hidden factors"
    if not q.get("factors"):
        return False, "a personalized quote with no factors is a hidden price"
    s = round(sum(f["dollars"] for f in q["factors"]), 2)
    if abs(s - q["monthly"]) > 0.005:
        return False, f"factors sum to ${s} but the price says ${q['monthly']} — a hidden factor"
    return True, "the shown factors ARE the price"


# ---------------------------------------------------------------- the re-price clock

def renewal_reprice(member_id, ref=None):
    """Re-pricing happens at RENEWAL ONLY, from the updated record. Returns the
    new price AND the factor deltas that moved it — the renewal draft carries
    them verbatim. Mid-term there is deliberately no code path: no function in
    this build writes `locked_price` after join."""
    ref = ref or now()
    m = store.by_id("members", member_id)
    if not m:
        return {"error": "no such member"}
    home = store.by_id("homes", m["home_id"])
    if not home:
        return {"error": "member has no home record"}
    q = membership_quote(home, ref)
    if q["provisional"]:
        return {"member": member_id, "provisional": True, "locked_price": m["locked_price"],
                "quote": q,
                "note": "the record no longer supports a personalized price — renewal goes "
                        "provisional with the reason named, never a guessed number"}
    old = {f["label"]: f["dollars"] for f in (m.get("factors_at_lock") or [])}
    new = {f["label"]: f["dollars"] for f in q["factors"]}
    cur = {f["label"]: f for f in q["factors"]}
    deltas = []
    for label in sorted(set(old) | set(new)):
        was, nw = float(old.get(label, 0.0)), float(new.get(label, 0.0))
        if abs(was - nw) < 0.005:
            continue
        deltas.append({"label": label, "was": was, "now": nw,
                       "delta": round(nw - was, 2),
                       "why": _delta_why(label, was, nw, cur.get(label))})
    d = round(q["monthly"] - m["locked_price"], 2)
    direction = "up" if d > 0 else "down" if d < 0 else "flat"
    return {"member": member_id, "locked_price": m["locked_price"],
            "new_monthly": q["monthly"], "delta_total": d, "direction": direction,
            "deltas": deltas, "quote": q,
            "note": "re-priced at renewal only, from the updated record — mid-term there is no code path"}


def _delta_why(label, was, now_d, cur):
    d = now_d - was
    sign = f"{'+' if d >= 0 else '-'}${abs(d):.0f}/mo"
    if cur and cur.get("band") and d > 0:
        return f"{cur['kind'].replace('_', ' ')} crossed the {cur['band']}-year band: {sign}"
    return f"{label} moved: ${was:.0f} → ${now_d:.0f} ({sign})"


# ---------------------------------------------------------------- the honesty board

def honesty_board():
    """Counted: members whose renewal price went DOWN — the trust stat a
    flat-plan incumbent cannot print."""
    members = [m for m in store.load("members") if not m.get("demo_tag")]
    renewed = [m for m in members if m.get("renewal_price") is not None]
    if not renewed:
        return unmeasured("no renewals recorded yet — the trust stat is counted, never asserted",
                          field="went_down")
    down = [m for m in renewed if m["renewal_price"] < m["locked_price"]]
    up = [m for m in renewed if m["renewal_price"] > m["locked_price"]]
    return {"renewed": len(renewed), "went_down": len(down), "went_up": len(up),
            "flat": len(renewed) - len(down) - len(up),
            "share_down": round(len(down) / len(renewed), 3),
            "note": "counted from the member records — a renewal price that went DOWN is "
                    "the trust stat no flat plan can print"}


# ---------------------------------------------------------------- the fairness rule

FORBIDDEN_FAIRNESS = ("market rate", "market rates", "going rate", "everyone pays",
                      "standard rate", "that's just the price", "market price")


def fairness_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_FAIRNESS if w in t]
    if hits:
        return False, (f"a fairness answer cites the asker's own factors, never the market — "
                       f"forbidden language: {', '.join(hits)}")
    return True, "ok"


# ---------------------------------------------------------------- the gas script

GAS_SCRIPT = ("If you smell gas: leave the house now — do not flip a light switch, do not "
              "light anything, do not start a car in the garage. From outside, call your gas "
              "utility's emergency line and 911. Everything else waits until you are out.")


# ---------------------------------------------------------------- triage

EMERGENCY = (
    r"\b(no|lost|without)\s+(heat|heating|cool\w*|air|ac|a/c|hot water)\b",
    r"\b(furnace|heater|heat|hvac|ac|a/c|air condition\w*|boiler)\b.*\b(out|down|dead|died|"
    r"stopped|quit|broken?|not (work|turn|kick|start)\w*|won'?t (work|turn|start|kick)\w*)\b",
    r"\b(out|down|dead|died|stopped|quit)\b.*\b(furnace|heater|hvac|boiler|a/c)\b",
    r"\b(smell\w*|odor|odour|whiff)\b.*\bgas\b",
    r"\bgas\b.*\b(smell\w*|leak\w*|odor|odour)\b",
    r"\b(pipe|water line|main)\b.*\b(burst|leak\w*|flood\w*)\b",
    r"\b(burst|leaking|flood\w*)\b.*\b(pipe|basement|ceiling)\b",
)
GAS = (
    r"\b(smell\w*|odor|odour|whiff)\b.*\bgas\b",
    r"\bgas\b.*\b(smell\w*|leak\w*|odor|odour)\b",
)
FAIRNESS = (
    r"\bneighbo?u?r\w*\b.*\b(plan|price|pay\w*|cheaper|less|more|bill)\b",
    r"\b(plan|price|membership|pay\w*|bill)\b.*\bneighbo?u?r\w*",
    r"\bwhy is my (plan|price|membership|bill)\b.*\b(more|higher|expensive)\b",
    r"\b(friend|brother|sister|coworker)\b.*\b(pays? less|cheaper|same plan)\b",
)
QUOTE_ASK = (
    r"\b(how much|price|quote|cost|costs)\b.*\b(membership|plan|maintenance)\b",
    r"\b(membership|maintenance plan|service plan)\b.*\b(cost\w*|price|quote|how much|join|sign)\b",
    r"\b(join|sign up for)\b.*\b(membership|plan)\b",
)
BOOKING = (
    r"\b(schedule|book|set ?up|arrange)\b.*\b(tune[- ]?up|visit|appointment|maintenance|service|inspection)\b",
    r"\b(tune[- ]?up|maintenance visit|inspection)\b.*\b(due|schedule|book|when|next week)\b",
)


def read_message(text):
    """emergency | fairness | quote_ask | booking | human. The emergency reads
    FIRST — the no-heat night and the gas smell are the calls that cannot sit
    in a queue."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in EMERGENCY:
        if re.search(rx, t):
            return {"label": "emergency",
                    "why": "no-heat/no-cool/gas/burst — dispatched first, never queued; a gas "
                           "smell gets the evacuate script verbatim, never reassurance"}
    for rx in FAIRNESS:
        if re.search(rx, t):
            return {"label": "fairness",
                    "why": "a price-fairness challenge — answered with the asker's own recorded "
                           "factors, verbatim, never 'market rates'"}
    for rx in QUOTE_ASK:
        if re.search(rx, t):
            return {"label": "quote_ask",
                    "why": "a membership quote ask — priced from the home's own black box, every "
                           "factor shown in dollars"}
    for rx in BOOKING:
        if re.search(rx, t):
            return {"label": "booking", "why": "service booking — answered from the schedule"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


def is_gas(text):
    t = (text or "").lower()
    return any(re.search(rx, t) for rx in GAS)


# ---------------------------------------------------------------- this week, counted

def won_this_week(ref=None):
    """Counted: members joined, renewals re-priced, quotes a HUMAN sent.
    An agent's gated draft is not a sent quote and is never counted as one."""
    ref = ref or now()
    members = store.load("members")
    joined = [m for m in members if m.get("joined_at")
              and (ref - (parse(m["joined_at"]) or ref)).days <= 7]
    renewed = [m for m in members if m.get("renewal_at")
               and (ref - (parse(m["renewal_at"]) or ref)).days <= 7]
    quotes_sent = sum(1 for e in store.events(kind="draft_quote")
                      if str(e.get("actor", "")).startswith("human:")
                      and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"members_joined": len(joined),
            "monthly_added": round(sum(m.get("locked_price") or 0 for m in joined), 2),
            "renewals_repriced": len(renewed), "quotes_sent": quotes_sent,
            "note": "counted from the member records and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="emergency",
                   costly_note=("A NO-HEAT NIGHT OR A GAS SMELL ROUTED LIKE A ROUTINE TICKET IS "
                                "THE CALL THAT ENDS THE COMPANY. Over-routing a booking ask "
                                "costs a read."))

EVAL_CASES = [
    {"input": "we have no heat and it's 20 degrees outside", "label": "emergency"},
    {"input": "the furnace died overnight", "label": "emergency"},
    {"input": "ac is not working and it's 95 in the house", "label": "emergency"},
    {"input": "i smell gas near the water heater", "label": "emergency"},
    {"input": "there's a gas smell in the basement", "label": "emergency"},
    {"input": "a pipe burst in the laundry room", "label": "emergency"},
    {"input": "how much does the maintenance membership cost", "label": "quote_ask"},
    {"input": "can you quote me the plan for my house", "label": "quote_ask"},
    {"input": "why is my plan more than my neighbor's", "label": "fairness"},
    {"input": "my neighbor pays less for the same plan", "label": "fairness"},
    {"input": "can we schedule the spring tune-up", "label": "booking"},
    {"input": "book a maintenance visit for next week", "label": "booking"},
    {"input": "", "label": "human"},
    {"input": "do you sell air filters", "label": "human"},
    {"input": "what brands do you install", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":         {"rung": "R3", "reason": "routing only; the emergency reads first"},
    "log_emergency":        {"rung": "R2", "reason": "the dispatch record cannot wait — internal, reversible"},
    "log_quote_request":    {"rung": "R2", "reason": "recording the ask is safe; the quote itself is gated"},
    "invent_component_age": {"rung": "R0", "reason": "an unrecorded age reads UNKNOWN and prices provisional — never guessed", "never_promote": True},
    "reprice_mid_term":     {"rung": "R0", "reason": "a locked price is locked — re-pricing exists only at renewal, and no code path can do it mid-term", "never_promote": True},
    "hide_pricing_factor":  {"rung": "R0", "reason": "the quote is the full factor enumeration or a refusal — a hidden dollar is a lie of omission", "never_promote": True},
    "dismiss_gas_smell":    {"rung": "R0", "reason": "a gas smell gets the evacuate script verbatim — never reassurance, never triage-by-vibe", "never_promote": True},
    "draft_quote":          {"rung": "R1", "reason": "outward money copy — a human sends, factors attached"},
    "draft_renewal_notice": {"rung": "R1", "reason": "outward money copy — the factor deltas ride verbatim, a human sends"},
    "draft_fairness_reply": {"rung": "R1", "reason": "outward reply — the asker's own factors, structurally market-language-free"},
    "draft_booking_reply":  {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_emergency_reply": {"rung": "R1", "reason": "outward reply — the script is fixed; a human confirms the dispatch"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def quotes_drafted_90d():
    n = 0
    for e in store.events(since_days=90):
        if e.get("kind") == "draft_quote":
            n += 1
        elif e.get("kind") == "queued_for_approval" \
                and (e.get("detail") or {}).get("action") == "draft_quote":
            n += 1
    return n


def renewals_due_90d(ref=None):
    ref = ref or now()
    return sum(1 for m in store.load("members")
               if not m.get("demo_tag") and m.get("term_end")
               and 0 <= ((parse(m["term_end"]) or ref) - ref).days <= 90)


def roi_model():
    return (Roi("Blackbox OS — what it computes to")
        .line("Membership conversion", "revenue",
              "quotes drafted (90d) × your join rate × avg monthly × 12",
              ["quotes_90d", "join_rate", "avg_monthly"],
              lambda g: float(g["quotes_90d"]) * float(g["join_rate"])
                        * float(g["avg_monthly"]) * 12,
              note="quotes are counted from the event log; the join rate is your call")
        .line("Retention at renewal", "revenue",
              "renewals due (90d) × your saved-renewal lift × avg monthly × 12",
              ["renewals_due_90d", "retention_lift", "avg_monthly"],
              lambda g: float(g["renewals_due_90d"]) * float(g["retention_lift"])
                        * float(g["avg_monthly"]) * 12,
              note="renewals due are counted from the member terms; the lift is yours")
        .line("Office hours on quoting & renewal math", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The price-trust story", "scenario",
              "you decide what a renewal price that can go DOWN is worth",
              ["trust_value"], lambda g: float(g["trust_value"]),
              assumption="never a saving — the member who stayed because the math was visible "
                         "is not our number to claim"))


def roi(given):
    rec = {}
    rec["quotes_90d"] = quotes_drafted_90d()
    rec["renewals_due_90d"] = renewals_due_90d()
    prices = [m.get("locked_price") for m in store.load("members")
              if m.get("locked_price") is not None]
    if prices:
        rec["avg_monthly"] = round(sum(prices) / len(prices), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_emergency", "log_quote_request", "draft_quote",
          "draft_renewal_notice", "draft_fairness_reply", "draft_booking_reply",
          "draft_emergency_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:", "homeowner:"))
