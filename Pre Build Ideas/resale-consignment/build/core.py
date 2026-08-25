#!/usr/bin/env python3
"""Consign OS — domain core (resale & consignment shops).

Rules live here: claim-first triage (the counterfeit accusation is the
reputation/legal event), the authenticity rule (software never calls an item
genuine — the record speaks or nothing does), the consignor ledger (payouts and
markdowns are the recorded agreement's arithmetic), the offer floor clamp, the
recall/prohibited wall, and the unsold-item clock.

Channel note, structural: CHANNELS below contains the shop's own floor and its
BUSINESS commerce channels only. Automating a personal marketplace account is
ToS-breaking bot behavior and is out of scope by construction — there is no
personal-account channel for any code path to use.

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

TABLES = ("config", "consignors", "items", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CONSIGNOS_DATA_ROOT")

CHANNELS = ("shop_floor", "web_store", "marketplace_business")

# ---------------------------------------------------------------- the agreement

DEFAULT_AGREEMENT = {
    "_source": ("DEFAULT consignment agreement, simplified — replace with the agreement the shop "
                "actually signs before go-live. Every clock date is a DATE ALERT, not legal "
                "advice."),
    "consignor_split": 0.6,                    # consignor's share of the sale price
    "term_days": 60,                           # listing term before reclaim opens
    "reclaim_window_days": 30,                 # consignor's window to take the item back
    "markdowns": [(30, 1.0), (60, 0.8), (10**6, 0.6)],   # days-listed → price factor
}


def agreement_for(consignor):
    """The recorded agreement: shop default, overridden by anything recorded on
    the consignor. Numbers come from here or they don't come."""
    base = store.load("config").get("agreement") or DEFAULT_AGREEMENT
    out = dict(base)
    for k in ("consignor_split", "term_days", "reclaim_window_days", "markdowns"):
        if (consignor or {}).get(k) is not None:
            out[k] = consignor[k]
            out["_source"] = base["_source"] + f" (this consignor's recorded {k} applies)"
    return out


def payout_math(item, consignor=None):
    """The payout DRAFTS from the recorded agreement: recorded sale price × the
    consignor's recorded split. Ad-hoc numbers can't be produced; missing
    inputs are named."""
    consignor = consignor if consignor is not None else store.by_id("consignors",
                                                                    item.get("consignor_id"))
    ag = agreement_for(consignor)
    missing = [f for f, v in (("sold_price", item.get("sold_price")),
                              ("consignor_split", ag.get("consignor_split"))) if v in (None, "")]
    if missing:
        return {"refused": (f"cannot draft a payout — missing: {', '.join(missing)}. The "
                            f"agreement's arithmetic needs its inputs; a number from memory is "
                            f"how the consignor relationship ends.")}
    amount = round(item["sold_price"] * ag["consignor_split"], 2)
    return {"amount": amount, "split": ag["consignor_split"],
            "basis": (f"${item['sold_price']:,.2f} recorded sale × {ag['consignor_split']:.0%} "
                      f"recorded split — the agreement's arithmetic"),
            "agreement_source": ag["_source"],
            "note": "a DRAFT for a human to pay — software never settles off the agreement"}


def markdown_price(item, ref=None):
    """The current price per the recorded markdown schedule. The schedule's own
    arithmetic — an off-schedule number has no path out of here."""
    ref = ref or now()
    ag = agreement_for(store.by_id("consignors", item.get("consignor_id")))
    listed = parse(item.get("listed_at"))
    if not listed:
        return {"refused": "not listed yet — no schedule clock to run"}
    if item.get("list_price") in (None, ""):
        return {"refused": "no recorded list price — nothing for the schedule to mark down"}
    days = (ref - listed).days
    factor = next(f for d, f in ag["markdowns"] if days < d)
    return {"price": round(item["list_price"] * factor, 2), "factor": factor,
            "days_listed": days,
            "basis": f"day {days} of the recorded schedule → ×{factor}",
            "agreement_source": ag["_source"]}


# ---------------------------------------------------------------- authenticity

FORBIDDEN_CLAIMS = ("authentic", "genuine", "100% real", "guaranteed real", "certified",
                    "verified real", "the real thing")


def brand_line(item):
    """The only brand statement software can make. A recorded third-party cert
    is CITED; without one, the brand is what the consignor tagged — and the
    listing says so."""
    brand = item.get("brand_claim")
    if not brand:
        return {"line": "", "state": "no brand claim on the record"}
    cert = item.get("auth_cert")
    if cert and cert.get("authenticator") and cert.get("ref"):
        return {"line": (f"Authenticated by {cert['authenticator']} (cert {cert['ref']}) — "
                         f"the certificate, not our judgment, is the statement"),
                "state": "third-party cert on the record"}
    return {"line": (f"Tagged {brand} by the consignor — not authenticated. Priced and sold "
                     f"as tagged."),
            "state": "consignor tag only — software never calls an item genuine"}


def listing_ok(text, item=None):
    """Structural check on outbound listing/reply copy: authenticity claims are
    forbidden language unless a recorded cert is being cited."""
    t = (text or "").lower()
    has_cert = bool((item or {}).get("auth_cert", {}).get("ref")) if item else False
    hits = [w for w in FORBIDDEN_CLAIMS if w in t]
    if hits and not has_cert:
        return False, (f"no authenticity claims without a recorded certificate — forbidden "
                       f"language: {', '.join(hits)}")
    return True, "ok"


# ---------------------------------------------------------------- listings

PROHIBITED = {
    "_source": ("DEFAULT recall/prohibited list, simplified from CPSC-style resale rules — "
                "replace with the maintained list before go-live."),
    "terms": ("drop-side crib", "recalled", "car seat", "firearm", "ammunition",
              "expired formula", "prescription"),
}


def prohibited_list():
    return store.load("config").get("prohibited") or PROHIBITED


def can_list(item):
    """The wall before the floor: recalled/prohibited goods can't be listed by
    any path, and a listing without the recorded condition is how the damage
    dispute starts."""
    text = " ".join(str(item.get(k) or "") for k in ("title", "category", "intake_notes")).lower()
    rules = prohibited_list()
    hits = [t for t in rules["terms"] if t in text]
    if hits:
        return False, (f"prohibited/recall match: {', '.join(hits)} — this category does not "
                       f"reach the floor or any channel. {rules['_source']}")
    if not item.get("condition_notes"):
        return False, ("no recorded condition notes from intake — a listing without the recorded "
                       "condition is how the damage dispute starts. Record the condition first.")
    if item.get("list_price") in (None, ""):
        return False, "no list price recorded — pricing is a decision, not a default"
    return True, "intake record complete; the description will carry only what it says"


def describe(item):
    """The listing body, built ONLY from the recorded intake facts. A field the
    record doesn't carry renders as 'not recorded' — never a plausible guess,
    never hype."""
    bl = brand_line(item)
    cond = item.get("condition_notes") or "not recorded"
    dims = item.get("dimensions") or "not recorded"
    body = (f"{item.get('title', 'Item')} — {item.get('category', 'general')}. "
            f"Condition, as recorded at intake: {cond}. Dimensions: {dims}."
            + (f" {bl['line']}" if bl["line"] else ""))
    okc, why = listing_ok(body, item)
    return {"body": body, "brand": bl, "listing_ok": okc, "why": why,
            "channels": list(CHANNELS),
            "note": "built from the intake record only — nothing invented, nothing promised"}


# ---------------------------------------------------------------- the offer floor

def offer_check(item, offer):
    """An offer below the consignor's recorded floor cannot be accepted by
    software — the counter drafts at the floor. No recorded floor → software
    doesn't negotiate at all."""
    floor = item.get("floor_price")
    if floor in (None, ""):
        return {"refused": ("no recorded floor from the consignor — software doesn't negotiate "
                            "someone else's property without their recorded number. The "
                            "consignor decides.")}
    if offer in (None, ""):
        return {"refused": "no offer amount to check"}
    if float(offer) < float(floor):
        return {"action": "counter", "floor": floor,
                "why": (f"${float(offer):,.0f} is below the consignor's recorded ${floor:,.0f} "
                        f"floor — the counter drafts at the floor; acceptance below it is the "
                        f"consignor's call, never software's")}
    return {"action": "accept_draft", "floor": floor,
            "why": f"at or above the recorded ${floor:,.0f} floor — an acceptance DRAFTS for a human"}


# ---------------------------------------------------------------- the clock

RECLAIM_MAX_TOUCHES = 3
RECLAIM_COOLDOWN_DAYS = 7


def clock_state(item, ref=None):
    ref = ref or now()
    ag = agreement_for(store.by_id("consignors", item.get("consignor_id")))
    listed = parse(item.get("listed_at"))
    if not listed:
        return {"state": "unlisted", "why": "no listing date — the term clock never started"}
    days = (ref - listed).days
    if days < ag["term_days"]:
        return {"state": "in_term", "days_listed": days,
                "term_ends_in": ag["term_days"] - days,
                "label": "DATE ALERT — the recorded term"}
    reclaim_days = days - ag["term_days"]
    if reclaim_days < ag["reclaim_window_days"]:
        return {"state": "reclaim_window", "days_listed": days,
                "reclaim_ends_in": ag["reclaim_window_days"] - reclaim_days,
                "label": "DATE ALERT — the consignor's reclaim window; the ladder runs"}
    return {"state": "clock_complete", "days_listed": days,
            "label": "clock complete — donation is now a human decision, and only now"}


def can_donate(item, ref=None):
    st = clock_state(item, ref)
    if st["state"] != "clock_complete":
        return False, (f"the clock is at '{st['state']}' — donating an item the consignor can "
                       f"still reclaim is conversion, not housekeeping. {st.get('label', '')}")
    return True, st["label"]


def reclaim_plan(item, ref=None):
    ref = ref or now()
    st = clock_state(item, ref)
    if st["state"] != "reclaim_window":
        return {"action": "none", "why": f"clock at '{st['state']}' — the ladder only runs in "
                                         f"the reclaim window"}
    touches = item.get("reclaim_touches") or []
    if len(touches) >= RECLAIM_MAX_TOUCHES:
        return {"action": "none", "why": (f"ladder exhausted at {RECLAIM_MAX_TOUCHES} — silence "
                                          f"is an answer; the clock runs out on its own and "
                                          f"donation stays a human act")}
    last = parse(touches[-1]["at"]) if touches else None
    if last and (ref - last).days < RECLAIM_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {RECLAIM_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_notice", "why": f"touch {len(touches)+1} of {RECLAIM_MAX_TOUCHES}"}


# ---------------------------------------------------------------- boards

def floor_board(ref=None):
    ref = ref or now()
    unlisted, aged, owed = [], [], []
    consignors = store.index("consignors")
    for it in store.load("items"):
        if it.get("demo_tag"):
            continue
        if it.get("status") == "intake":
            days = (ref - (parse(it.get("intake_at")) or ref)).days
            unlisted.append({"item": it["id"], "title": it.get("title"), "days_waiting": days})
        elif it.get("status") == "listed":
            st = clock_state(it, ref)
            md = markdown_price(it, ref)
            row = {"item": it["id"], "title": it.get("title"),
                   "list_price": it.get("list_price"), **st}
            if "price" in md:
                row["current_price"] = md["price"]
            aged.append(row)
        elif it.get("status") == "sold" and not it.get("paid_out_at"):
            m = payout_math(it, consignors.get(it.get("consignor_id")))
            owed.append({"item": it["id"], "title": it.get("title"),
                         "consignor": consignors.get(it.get("consignor_id"), {}).get("name"),
                         "amount": m.get("amount"),
                         "unpayable": m.get("refused")})
    unlisted.sort(key=lambda r: -r["days_waiting"])
    aged.sort(key=lambda r: -(r.get("days_listed") or 0))
    payable = [o for o in owed if o.get("amount") is not None]
    return {"unlisted": unlisted[:40], "unlisted_count": len(unlisted),
            "aged": aged[:40],
            "owed": owed[:40],
            "owed_total": round(sum(o["amount"] for o in payable), 2),
            "owed_unpayable": len(owed) - len(payable),
            "note": ("payouts owed are counted from the ledger; a sold item whose agreement "
                     "inputs are missing is listed as unpayable, never estimated")}


def recovered_this_week(ref=None):
    """Counted: items sold, payouts paid, listings published (human sends count;
    agent drafts don't), reclaim notices sent."""
    ref = ref or now()
    sold = [i for i in store.load("items")
            if i.get("sold_at") and (ref - (parse(i["sold_at"]) or ref)).days <= 7]
    paid = [i for i in store.load("items")
            if i.get("paid_out_at") and (ref - (parse(i["paid_out_at"]) or ref)).days <= 7]

    def human_sends(kind):
        return sum(1 for e in store.events(kind=kind)
                   if str(e.get("actor", "")).startswith("human:")
                   and (ref - (parse(e.get("at")) or ref)).days <= 7)

    return {"items_sold": len(sold),
            "sales_value": round(sum(i.get("sold_price") or 0 for i in sold), 2),
            "payouts_paid": len(paid),
            "listings_published": human_sends("publish_listing"),
            "reclaim_notices_sent": human_sends("draft_reclaim_notice"),
            "note": "counted from the ledger and the event log — human sends count; agent "
                    "drafts don't"}


# ---------------------------------------------------------------- triage

CLAIM_MSG = (
    # "not fake"/"not a replica" is an ASK, not an accusation — the lookbehind
    # keeps "how do i know it's real and not fake" out of the claim lane
    r"(?<!not )(?<!not a )\b(fake|counterfeit|knock ?offs?|replicas?)\b",
    r"\b(scratch\w*|broken|damaged|chipped|missing|stain\w*|cracked|wobbl\w*)\b.*"
    r"\b(dresser|table|chair|bag|purse|jacket|coat|lamp|sofa|couch|item|bookshelf|didn'?t show)\b",
    # the reversed order — "the lamp arrived cracked" (found by the eval)
    r"\b(dresser|table|chair|bag|purse|jacket|coat|lamp|sofa|couch|item|bookshelf)\b.*"
    r"\b(scratch\w*|broken|damaged|chipped|cracked|wobbl\w*|stain\w*|missing)\b",
    r"\b(you (didn'?t|never) (show|mention|disclose))\b",
)
AUTH_ASK = (
    r"\bis (the|that|this|it)\b.*\b(authentic|real|genuine|legit)\b",
    r"\b(authentic|real|genuine|legit)\b.*\?\s*$",
    r"\bhow do i know it'?s (real|authentic|not fake)\b",
)
OFFER = (
    r"\b(would|will|can|could) you (take|do|accept|go)\b.*\d",
    r"\b(lowest|best|final) (price|you.?d take|offer)\b",
    r"\bi'?ll (give|offer|pay) (you )?\$?\d",
    r"\bhow about \$?\d",
)
PICKUP = (
    r"\b(when|what time) can i (pick|come|get|grab)\b",
    r"\b(come|stop|swing) by\b.*\b(for|to (get|grab|pick))\b",
    r"\bpick(ing)? ?up\b.*\b(today|tomorrow|saturday|sunday|monday|tuesday|wednesday|thursday|"
    r"friday|this week)\b",
)
PAYOUT = (
    r"\b(when|where).{0,24}\b(paid|payment|payout|check|money)\b",
    r"\bmy (check|money|payout|payment)\b",
    r"\b(get paid|owe me|owed)\b",
)


def read_message(text):
    """claim | auth_ask | offer | pickup | payout | human. The claim reads
    first — the counterfeit accusation is the reputation/legal event."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in CLAIM_MSG:
        if re.search(rx, t):
            return {"label": "claim",
                    "why": "a counterfeit/damage claim — never denied and never certified by "
                           "software; the record is pulled and a human decides"}
    for rx in AUTH_ASK:
        if re.search(rx, t):
            return {"label": "auth_ask",
                    "why": "an authenticity question — the record speaks (the consignor tag or "
                           "a cited cert); software never calls an item genuine"}
    for rx in OFFER:
        if re.search(rx, t):
            return {"label": "offer",
                    "why": "a buyer offer — checked against the consignor's recorded floor"}
    for rx in PICKUP:
        if re.search(rx, t):
            return {"label": "pickup", "why": "pickup scheduling — slots propose at R2, the "
                                              "buyer confirms"}
    for rx in PAYOUT:
        if re.search(rx, t):
            return {"label": "payout",
                    "why": "a consignor payout ask — answered from the ledger, the agreement's "
                           "arithmetic cited"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="claim",
                   costly_note=("THE COUNTERFEIT ACCUSATION HANDLED AD-HOC IS THE ONE-STAR STORY "
                                "AND THE LEGAL EXPOSURE. Over-routing an offer costs a read."))

EVAL_CASES = [
    {"input": "the louis vuitton bag i bought yesterday is a fake", "label": "claim"},
    {"input": "pretty sure this coach purse is a knockoff, i want a refund", "label": "claim"},
    {"input": "the dresser has a huge scratch you didn't show in the photos", "label": "claim"},
    {"input": "the lamp arrived cracked", "label": "claim"},
    {"input": "is the gucci belt authentic", "label": "auth_ask"},
    {"input": "how do i know it's real and not fake", "label": "auth_ask"},
    {"input": "would you take $40 for the dresser", "label": "offer"},
    {"input": "can you do 60 on the lamp", "label": "offer"},
    {"input": "lowest price you'd take on the patio set", "label": "offer"},
    {"input": "when can i pick up the bookshelf", "label": "pickup"},
    {"input": "can i come by saturday for the table", "label": "pickup"},
    {"input": "when do i get paid for my items that sold", "label": "payout"},
    {"input": "where's my check for the coat that sold last week", "label": "payout"},
    {"input": "", "label": "human"},
    {"input": "what are your hours on sunday", "label": "human"},
    {"input": "do you take donations", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":         {"rung": "R3", "reason": "routing only; the claim reads first"},
    "certify_authenticity": {"rung": "R0", "reason": "software never calls an item genuine — the recorded cert is cited or the consignor tag is stated, and nothing else exists", "never_promote": True},
    "deny_claim":           {"rung": "R0", "reason": "the counterfeit/damage claim gets the record and a human — software assembles, never rules", "never_promote": True},
    "settle_off_agreement": {"rung": "R0", "reason": "payouts and markdowns are the recorded agreement's arithmetic or a human — never an ad-hoc number", "never_promote": True},
    "accept_below_floor":   {"rung": "R0", "reason": "the consignor's recorded floor is their property line — acceptance below it is their call, never software's", "never_promote": True},
    "list_prohibited_item": {"rung": "R0", "reason": "the recall/prohibited list is a wall, not a warning", "never_promote": True},
    "donate_before_clock":  {"rung": "R0", "reason": "donating what the consignor can still reclaim is conversion, not housekeeping — and donation is human-only even after the clock", "never_promote": True},
    "log_claim":            {"rung": "R2", "reason": "the claim record and the evidence pull cannot wait"},
    "markdown_on_schedule": {"rung": "R2", "reason": "the recorded schedule's own arithmetic — the agreement already decided this number"},
    "propose_pickup":       {"rung": "R2", "reason": "proposing slots commits nobody; the buyer confirms"},
    "draft_listing":        {"rung": "R1", "reason": "outward copy in the shop's name — a human publishes"},
    "publish_listing":      {"rung": "R1", "reason": "putting the shop's word on a business channel is the shop's reputation"},
    "draft_offer_reply":    {"rung": "R1", "reason": "outward reply about someone else's property — a human sends"},
    "draft_auth_reply":     {"rung": "R1", "reason": "outward reply, claim-checked structurally — a human sends"},
    "draft_payout":         {"rung": "R1", "reason": "money — a human pays, with the agreement math attached"},
    "draft_reclaim_notice": {"rung": "R1", "reason": "outward notice on a legal clock — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Consign OS — what it computes to")
        .line("Listing hours returned", "time_saved", "items listed/mo × min per listing × 12 × rate",
              ["items_listed_month", "min_per_listing", "rate"],
              lambda g: float(g["items_listed_month"]) * float(g["min_per_listing"]) / 60 * 12
              * float(g["rate"]),
              note="the intake backlog is counted; the minutes are yours")
        .line("Sell-through lift on aged inventory", "revenue",
              "aged inventory value × your lift × shop share",
              ["aged_value", "sell_lift", "shop_share"],
              lambda g: float(g["aged_value"]) * float(g["sell_lift"]) * float(g["shop_share"]),
              note="aged value is counted from the floor; the lift is your call, not ours")
        .line("The counterfeit file", "scenario",
              "you decide what a procedure-handled accusation is worth",
              ["counterfeit_value"], lambda g: float(g["counterfeit_value"]),
              assumption="never a saving — the lawsuit that didn't run is not our number"))


def roi(given):
    rec = {}
    fb = floor_board()
    rec["aged_value"] = round(sum(r.get("current_price") or r.get("list_price") or 0
                                  for r in fb["aged"]), 2)
    rec["items_listed_month"] = len(fb["unlisted"]) + len(fb["aged"])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_claim", "draft_listing", "publish_listing", "draft_offer_reply",
          "draft_auth_reply", "draft_payout", "draft_reclaim_notice", "markdown_on_schedule",
          "propose_pickup")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("buyer:", "consignor:"))
