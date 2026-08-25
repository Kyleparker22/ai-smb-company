#!/usr/bin/env python3
"""Marquee OS — domain core (party & tent rental).

Rules live here: weather-first triage (the wind worry on a booked event reads
before everything), the wind rule (software states the recorded forecast
against the recorded rated limit and NEVER makes the call), counted-stock
reservations where an oversell has no code path, the 811 wall, per-municipality
permit clocks as date alerts, deposit math that only runs from the recorded
condition pair, and the matrix.

The thesis: a tent company's catastrophes are a staked tent in wind and a stake
through a gas line — both human calls software must never make — and its quiet
leaks are a double-booked weekend, a missed permit clock, and a deposit
deducted on memory instead of evidence. Make the first two structurally
unmakeable by software and the last three a matter of counting.

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

TABLES = ("config", "inventory", "bookings", "messages", "conditions",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="MARQUEEOS_DATA_ROOT")


# ---------------------------------------------------------------- counted stock

def weekend_of(date_iso):
    """The Saturday of the week containing the date. A weekend is the unit of
    capacity — same-weekend turnaround of a staked tent is not assumed."""
    d = parse(date_iso)
    if not d:
        return None
    return (d - timedelta(days=(d.weekday() - 5) % 7)).date().isoformat()


def reserved_for_weekend(weekend):
    """Per-item quantities held by CONFIRMED bookings on that weekend. Demo
    rows count too — a reservation is a reservation; excluding any class of
    booking from the count is how an oversell sneaks back in."""
    res = {}
    for b in store.load("bookings"):
        if b.get("status") != "confirmed" or weekend_of(b.get("event_date")) != weekend:
            continue
        for iid, qty in (b.get("items") or {}).items():
            res[iid] = res.get(iid, 0) + qty
    return res


def availability(event_date):
    w = weekend_of(event_date)
    res = reserved_for_weekend(w)
    return {i["id"]: {"name": i.get("name"), "stock": i.get("stock", 0),
                      "reserved": res.get(i["id"], 0),
                      "available": i.get("stock", 0) - res.get(i["id"], 0)}
            for i in store.load("inventory")}


def reserve(customer, event_date, items, site=None, municipality=None,
            deposit=None, demo_tag=None):
    """Reservations draw from counted stock or go to the waitlist — honestly.

    The confirmed branch exists only when every line fits counted stock for
    that weekend. There is no force flag and no override argument; that
    absence is the guarantee. An oversell is not refused — it is unwritable.
    """
    inv = store.index("inventory")
    unknown = sorted(i for i in items if i not in inv)
    if unknown:
        return {"refused": f"unknown item(s): {', '.join(unknown)} — reservations draw "
                           f"from the counted catalog only; a line that isn't counted "
                           f"can't be promised"}
    w = weekend_of(event_date)
    res = reserved_for_weekend(w)
    short = {i: {"want": q, "available": max(inv[i]["stock"] - res.get(i, 0), 0)}
             for i, q in items.items() if q > inv[i]["stock"] - res.get(i, 0)}
    status = "waitlisted" if short else "confirmed"
    b = {"id": store.nid("bk"), "customer_name": customer, "event_date": event_date,
         "weekend": w, "site": site, "municipality": municipality,
         "items": dict(items), "deposit_amount": deposit, "status": status,
         "booked_at": iso()}
    if demo_tag:
        b["demo_tag"] = demo_tag
    if short:
        b["waitlist_short"] = short
    store.upsert("bookings", b)
    gate.act("reserve_inventory", "desk", b["id"],
             {"status": status, "weekend": w, "items": dict(items),
              "short": short or None})
    why = ("every line fits counted stock for that weekend" if not short else
           "short on " + ", ".join(f"{k} (want {v['want']}, {v['available']} available)"
                                   for k, v in sorted(short.items())) +
           " — waitlisted honestly; nothing was taken from another event")
    return {"booking": b["id"], "status": status, "short": short or None, "why": why}


def capacity_board(ref=None):
    """The weekend as a capacity plan: every confirmed reservation's items
    against counted stock, per upcoming weekend."""
    ref = ref or now()
    inv = store.load("inventory")
    weekends = sorted({weekend_of(b.get("event_date"))
                       for b in store.load("bookings")
                       if b.get("status") == "confirmed" and parse(b.get("event_date"))
                       and parse(b["event_date"]) >= ref - timedelta(days=2)})
    out = []
    for w in weekends:
        res = reserved_for_weekend(w)
        rows, idle_value, reserved_value, full = [], 0.0, 0.0, []
        for it in inv:
            r = res.get(it["id"], 0)
            av = it.get("stock", 0) - r
            rate = it.get("day_rate", 0)
            rows.append({"item": it["id"], "name": it.get("name"),
                         "stock": it.get("stock", 0), "reserved": r, "available": av})
            idle_value += max(av, 0) * rate
            reserved_value += r * rate
            if av <= 0 and r:
                full.append(it["id"])
        out.append({"weekend": w, "rows": rows, "full": full,
                    "idle_value": round(idle_value, 2),
                    "reserved_value": round(reserved_value, 2)})
    return {"weekends": out,
            "note": "reserved is counted from confirmed bookings; available is stock "
                    "minus that count — the only two numbers a promise can stand on"}


# ---------------------------------------------------------------- the wind rule

def wind_check(booking):
    """Software's entire role in the wind question: state the recorded forecast
    against the recorded per-tent rated limit. It never says 'safe' and never
    makes the call — install / hold / strike belongs to a human, on the record."""
    tents = [(iid, qty) for iid, qty in (booking.get("items") or {}).items()
             if iid.startswith("tent_")]
    if not tents:
        return {"applies": False,
                "why": "no tent on this booking — no staked structure, no wind rule"}
    inv = store.index("inventory")
    gust = (booking.get("forecast") or {}).get("gust_mph")
    rows, parts, flag = [], [], False
    for iid, qty in tents:
        item = inv.get(iid) or {}
        name = item.get("name", iid)
        rating = item.get("wind_rating_mph")
        if rating is None:
            rows.append({"tent": iid, "status": "no_rating",
                         "why": f"no recorded rated wind limit for the {name} — the "
                                f"manufacturer's number gets recorded or the tent doesn't "
                                f"go up; a guess is not a limit"})
            parts.append(f"the {name} has no recorded rated wind limit on file, which "
                         f"itself stands the install down until the number is recorded")
            flag = True
        elif gust is None:
            rows.append({"tent": iid, "status": "no_forecast", "rated_mph": rating,
                         "why": "no recorded forecast for this date — the flag waits "
                                "for a recorded number; nobody guesses"})
            parts.append(f"no forecast is recorded yet for your date; the {name} carries "
                         f"a recorded rated limit of {rating} mph installed")
        elif gust > rating:
            rows.append({"tent": iid, "status": "exceeds", "forecast_gust_mph": gust,
                         "rated_mph": rating})
            parts.append(f"the forecast on file for your site is gusts to {gust} mph; "
                         f"the {name} is rated to {rating} mph installed, on record — "
                         f"the forecast exceeds the rated limit")
            flag = True
        else:
            rows.append({"tent": iid, "status": "inside", "forecast_gust_mph": gust,
                         "rated_mph": rating})
            parts.append(f"the forecast on file is gusts to {gust} mph against the "
                         f"{name}'s recorded rated limit of {rating} mph — inside "
                         f"the recorded limit")
    return {"applies": True, "flag": flag, "rows": rows,
            "summary": "; ".join(parts) + ".",
            "note": "software states the numbers; a human owns install / hold / "
                    "strike, on the record"}


def weather_call(booking_id, human=None, decision=None, note=None):
    """The install/hold/strike decision. Software calling it is refused at R0 —
    permanently. A named human records the call, with the numbers attached."""
    b = store.by_id("bookings", booking_id)
    if not b:
        return {"error": "no such booking"}
    wc = wind_check(b)
    if not human or decision not in ("install", "hold", "strike"):
        return gate.act("make_weather_call", "weather", booking_id,
                        {"wind": wc.get("summary"), "attempted_decision": decision})
    ev = store.log_event("weather_call", booking_id, f"human:{human}", "R1",
                         {"decision": decision, "note": note, "wind": wc.get("summary")})
    b["weather_call"] = {"decision": decision, "by": human, "at": iso(), "note": note}
    store.upsert("bookings", b)
    return {"recorded": True, "decision": decision, "by": human, "event": ev["id"],
            "wind": wc.get("summary")}


# the tone rule: a wind reply may state numbers and name the human — it may not soothe
REASSURANCE_FORBIDDEN = ("it'll be fine", "it will be fine", "totally safe",
                         "perfectly safe", "completely safe", "nothing to worry",
                         "don't worry", "no need to worry", "rest assured",
                         "guaranteed safe", "no danger")


def tone_ok(text):
    t = (text or "").lower()
    hits = [w for w in REASSURANCE_FORBIDDEN if w in t]
    if hits:
        return False, f"no reassurance on a safety question — forbidden language: {', '.join(hits)}"
    return True, "ok"


# ---------------------------------------------------------------- the 811 wall + site checklist

def can_install(booking):
    """The recorded 811 locate ticket is a wall, not a checkbox. Surface and
    power are checklist items — surfaced by name when unrecorded."""
    chk = booking.get("site_checklist") or {}
    if not chk.get("locate_ticket"):
        return False, ("no recorded 811 locate ticket for this site — the install is "
                       "refused. A stake through a gas line is the other fatal case; "
                       "the ticket is a wall, not a checkbox.")
    unrecorded = [f for f in ("surface", "power") if not chk.get(f)]
    why = f"811 ticket {chk['locate_ticket']} on record"
    why += f" · surface: {chk['surface']}" if chk.get("surface") else " · surface: UNRECORDED"
    why += f" · power: {chk['power']}" if chk.get("power") else " · power: UNRECORDED"
    if unrecorded:
        why += f" — unrecorded checklist item(s) named, not assumed: {', '.join(unrecorded)}"
    return True, why


# ---------------------------------------------------------------- permit clocks

DEFAULT_PERMIT_RULES = {
    "_source": ("DEFAULT per-municipality tent-permit table, simplified — replace with "
                "each municipality's actual ordinance before go-live. Every date here is "
                "a DATE ALERT, not legal advice; filing is a human act."),
    "municipalities": {
        "Fairfield": {"apply_days_before": 14, "tent_sqft_threshold": 400},
        "Ashford":   {"apply_days_before": 10, "tent_sqft_threshold": 700},
        "Belmont":   {"apply_days_before": 21, "tent_sqft_threshold": 400},
    },
}


def permit_rules():
    return store.load("config").get("permit_rules") or DEFAULT_PERMIT_RULES


def tent_sqft(items):
    total = 0
    for iid, qty in (items or {}).items():
        m = re.match(r"tent_(\d+)x(\d+)", iid)
        if m:
            total += int(m.group(1)) * int(m.group(2)) * qty
    return total


def permit_board(ref=None):
    """Per-municipality tent-permit clocks as DATE ALERTS. A municipality with
    no recorded rule is named, never defaulted."""
    ref = ref or now()
    rules = permit_rules()
    rows = []
    for b in store.load("bookings"):
        if b.get("status") != "confirmed" or not parse(b.get("event_date")):
            continue
        if parse(b["event_date"]) < ref - timedelta(days=1):
            continue
        sqft = tent_sqft(b.get("items"))
        if not sqft:
            continue
        muni = b.get("municipality")
        rule = rules["municipalities"].get(muni)
        row = {"booking": b["id"], "customer": b.get("customer_name"),
               "event_date": b.get("event_date"), "municipality": muni,
               "tent_sqft": sqft}
        if not rule:
            row.update(unmeasured(f"no permit rule recorded for {muni or 'this municipality'} "
                                  f"— the clock cannot run; a human looks up the ordinance",
                                  field="days_left"))
            rows.append(row)
            continue
        if sqft < rule["tent_sqft_threshold"]:
            row.update(permit="not required",
                       why=f"{sqft} sqft is under {muni}'s recorded {rule['tent_sqft_threshold']} "
                           f"sqft threshold")
            rows.append(row)
            continue
        if b.get("permit_ref"):
            row.update(permit="filed", permit_ref=b["permit_ref"])
            rows.append(row)
            continue
        deadline = parse(b["event_date"]) - timedelta(days=rule["apply_days_before"])
        row.update(permit="NOT FILED", deadline=deadline.date().isoformat(),
                   days_left=(deadline - ref).days,
                   label="DATE ALERT — the permit clock, not legal advice; filing is a human act")
        rows.append(row)
    rows.sort(key=lambda r: (r.get("days_left") is None,
                             r["days_left"] if r.get("days_left") is not None else 0))
    return {"rows": rows, "rules_source": rules["_source"]}


# ---------------------------------------------------------------- deposit math

def deposit_math(booking):
    """Deposit arithmetic runs ONLY from the recorded out-condition and
    return-condition pair. One missing → refused with the missing record named.
    With both: new damage = return minus out, item by item, at recorded cost."""
    if booking.get("deposit_amount") in (None, ""):
        return {"refused": "no recorded deposit on this booking — nothing to settle"}
    conds = [c for c in store.load("conditions") if c.get("booking_id") == booking["id"]]
    out_rec = next((c for c in conds if c.get("kind") == "out"), None)
    ret_rec = next((c for c in conds if c.get("kind") == "return"), None)
    missing = ([] if out_rec else ["out-condition record"]) + \
              ([] if ret_rec else ["return-condition record"])
    if missing:
        return {"refused": f"cannot touch the deposit — missing: {', '.join(missing)}. A "
                           f"deduction without both condition records is an accusation, not "
                           f"arithmetic — and a refund without them throws away the evidence."}
    prior = {d.get("item") for d in (out_rec.get("damage") or [])}
    new = [d for d in (ret_rec.get("damage") or []) if d.get("item") not in prior]
    deduction = round(sum(d.get("cost", 0) for d in new), 2)
    refund = round(max(0.0, booking["deposit_amount"] - deduction), 2)
    return {"deposit": booking["deposit_amount"], "new_damage": new,
            "deduction": deduction, "refund": refund,
            "evidence": {"out": out_rec["id"], "return": ret_rec["id"],
                         "out_photos": out_rec.get("photos", 0),
                         "return_photos": ret_rec.get("photos", 0)},
            "basis": (f"${booking['deposit_amount']:,.0f} deposit − "
                      f"${deduction:,.0f} for damage on return that was not on the "
                      f"out-condition record = ${refund:,.0f} refund — the condition "
                      f"pair's arithmetic, photos referenced"),
            "note": "a DRAFT at R1 — a human sends the refund or the deduction, "
                    "evidence attached"}


# ---------------------------------------------------------------- triage

WEATHER = (
    r"\b(gusts?|storm|thunderstorm|high winds?|hurricane|tornado)\b",
    r"\bwind\w*\b.*\b(tent|safe|rating|rated|hold|worry|worried)\b",
    r"\b(tent|canopy|marquee)\b.*\b(safe|hold up|blow|stand up|withstand)\b",
    r"\b(forecast|weather)\b.*\b(event|tent|worried|worry|safe)\b",
)
CHANGE = (
    r"\b(add|remove|swap|change|move|reschedule|switch)\b.*\b(order|booking|reservation|"
    r"tent|date|floor|chairs?|tables?)\b",
    r"\b(our|the|my) (order|booking|reservation|date)\b.*\b(change|move|different|instead)\b",
)
BOOKING = (
    r"\b(available|availability|do you have|need|looking for|rent|book|reserve|quote)\b.*"
    r"\b(tents?|tables?|chairs?|dance floors?|linens?)\b",
    r"\b(tents?|tables?|chairs?)\b.*\b(available|availability)\b",
)
DEPOSIT = (r"\bdeposit\b",)
STATUS = (
    r"\b(what time|when)\b.*\b(crew|delivery|deliver|arriv|setup|set up|pickup|install)\w*",
    r"\b(is|are)\b.*\b(order|booking|reservation|we)\b.*\bconfirmed\b",
    r"\bconfirmed for\b",
)


def read_message(text):
    """weather_worry | booking_request | change_request | deposit_ask | status |
    human. The weather worry reads FIRST — a staked tent in wind is the
    fatal case, and the one message that cannot wait in a queue."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in WEATHER:
        if re.search(rx, t):
            return {"label": "weather_worry",
                    "why": "a wind/safety worry on a booked event — software states the "
                           "recorded forecast against the recorded rated limit; a human "
                           "makes the install/hold/strike call, on the record"}
    for rx in CHANGE:
        if re.search(rx, t):
            return {"label": "change_request", "why": "a change to an existing booking — "
                                                      "redrawn against counted stock"}
    for rx in BOOKING:
        if re.search(rx, t):
            return {"label": "booking_request", "why": "a new booking — reserves from "
                                                       "counted stock or waitlists honestly"}
    for rx in DEPOSIT:
        if re.search(rx, t):
            return {"label": "deposit_ask", "why": "a deposit question — answered from the "
                                                   "recorded condition pair, or not at all"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status", "why": "status — answered from the booking record"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- recovered, counted

def recovered_this_week(ref=None):
    """Counted, never asserted: bookings confirmed, replies a human actually
    sent (an agent's draft is not a send), deposit settlements a human sent,
    and permit alerts raised — all inside 7 days."""
    ref = ref or now()
    confirmed = [b for b in store.load("bookings")
                 if b.get("status") == "confirmed" and b.get("booked_at")
                 and (ref - (parse(b["booked_at"]) or ref)).days <= 7]
    def human_sent(kinds):
        return sum(1 for e in store.events(kind=kinds)
                   if str(e.get("actor", "")).startswith("human:")
                   and (ref - (parse(e.get("at")) or ref)).days <= 7)
    replies = human_sent(("draft_booking_reply", "draft_change_reply",
                          "draft_weather_note", "draft_status_reply"))
    deposits = human_sent(("draft_deposit_refund", "draft_deposit_deduction"))
    alerts = sum(1 for e in store.events(kind="permit_alert")
                 if (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"bookings_confirmed": len(confirmed),
            "booked_value": round(sum(b.get("deposit_amount") or 0 for b in confirmed), 2),
            "replies_sent": replies, "deposit_actions_sent": deposits,
            "permit_alerts": alerts,
            "note": "counted from the book and the event log — a draft is not a send, "
                    "and neither is asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="weather_worry",
                   costly_note=("A STAKED TENT IN WIND KILLS. The wind worry on a booked "
                                "event that sits unread in a queue is the fatal case — "
                                "over-routing a chair count to a person costs a read."))

EVAL_CASES = [
    {"input": "they're calling for 50mph gusts saturday, is the tent safe", "label": "weather_worry"},
    {"input": "storm coming during the reception, will the tent hold up", "label": "weather_worry"},
    {"input": "forecast says high winds for our event, should we be worried", "label": "weather_worry"},
    {"input": "it's supposed to thunderstorm sunday, is the 40x60 going to be okay", "label": "weather_worry"},
    {"input": "wind rating question — what are your tents rated for", "label": "weather_worry"},
    {"input": "do you have a 40x60 tent available the first weekend of june", "label": "booking_request"},
    {"input": "need 200 chairs and 20 round tables for a graduation party", "label": "booking_request"},
    {"input": "can we add a dance floor to our order", "label": "change_request"},
    {"input": "we need to move our tent order to the following saturday", "label": "change_request"},
    {"input": "when do we get our deposit back", "label": "deposit_ask"},
    {"input": "you charged our deposit for a stain we didn't make", "label": "deposit_ask"},
    {"input": "what time is the crew arriving friday", "label": "status"},
    {"input": "is our order confirmed for the 14th", "label": "status"},
    {"input": "", "label": "human"},
    {"input": "do you do fireworks too", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":      {"rung": "R3", "reason": "routing only; the weather worry reads first"},
    "make_weather_call": {"rung": "R0", "reason": "software states the recorded forecast against the "
                                                  "recorded rated wind limit — a human owns install / "
                                                  "hold / strike, on the record", "never_promote": True},
    "oversell_inventory": {"rung": "R0", "reason": "structural, not just refused — reservations draw "
                                                   "from counted stock or the waitlist; no code path "
                                                   "writes a confirmed booking past the count", "never_promote": True},
    "install_without_utility_locate": {"rung": "R0", "reason": "the recorded 811 ticket is a wall — a stake "
                                                               "through a gas line is the other fatal case", "never_promote": True},
    "deduct_deposit_without_condition_records": {"rung": "R0", "reason": "a deduction needs the recorded out-condition "
                                                                         "AND return-condition — anything else is an "
                                                                         "accusation, not arithmetic", "never_promote": True},
    "reserve_inventory": {"rung": "R2", "reason": "internal state from counted stock — the waitlist branch "
                                                  "is the honesty, and it cannot oversell by construction"},
    "permit_alert":      {"rung": "R2", "reason": "an internal date alert; a missed clock is a fine or a "
                                                  "shut-down event"},
    "draft_weather_note": {"rung": "R1", "reason": "outward, safety-adjacent — numbers stated, tone-checked, "
                                                   "a human sends"},
    "draft_booking_reply": {"rung": "R1", "reason": "outward promise of counted stock — a human sends"},
    "draft_change_reply": {"rung": "R1", "reason": "outward — a change redraws against the count; a human sends"},
    "draft_status_reply": {"rung": "R1", "reason": "outward — a human sends"},
    "draft_deposit_refund": {"rung": "R1", "reason": "money out — drafted from the condition pair, a human sends"},
    "draft_deposit_deduction": {"rung": "R1", "reason": "money kept + relationship — evidence attached, a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Marquee OS — what it computes to")
        .line("Idle weekend inventory put to work", "revenue",
              "counted idle day-rate value on the busiest weekend × your utilization lift",
              ["idle_weekend_value", "utilization_lift"],
              lambda g: float(g["idle_weekend_value"]) * float(g["utilization_lift"]),
              note="the idle value is counted from the capacity board; the lift is your call")
        .line("Deposit disputes avoided", "scenario", "disputes/yr × avg dispute",
              ["disputes_yr", "avg_dispute"],
              lambda g: float(g["disputes_yr"]) * float(g["avg_dispute"]),
              assumption="never a saving — the dispute that didn't happen cannot be counted")
        .line("Permit fines & shut-downs", "scenario", "you decide what a missed clock costs",
              ["permit_fine_value"], lambda g: float(g["permit_fine_value"]),
              assumption="an exposure you weigh — a fine that wasn't issued is not our number")
        .line("Office & phone hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]),
              note="reported separately; never summed into revenue"))


def roi(given):
    rec = {}
    cb = capacity_board()
    if cb["weekends"]:
        busiest = max(cb["weekends"], key=lambda w: w["reserved_value"])
        rec["idle_weekend_value"] = busiest["idle_value"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "reserve_inventory", "permit_alert", "draft_weather_note",
          "draft_booking_reply", "draft_change_reply", "draft_status_reply",
          "draft_deposit_refund", "draft_deposit_deduction")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
