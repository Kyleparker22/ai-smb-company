#!/usr/bin/env python3
"""yourco — the last two, both behind the launch gate, and both instrumented anyway.

Fourth and final cluster of the 2026-08-25 metric sweep. Michelle owns *positive reply rate* and
Webb owns *bookings from the site*, and neither can be non-zero while the launch-gate holds: no
outbound has been sent and no site has been published. **A gate is not something a metric can fix.**

So, exactly as with the client-#1 cluster, the question was the other one: *the day the gate clears,
will these compute — or will the first campaign and the first bookings arrive unattributed?* Both
would have. Three defects were fixed that only bite once the gate opens, which is the worst time to
find them:

1. **There was no way to say a reply was GOOD.** `seqStatus` had one undifferentiated `replied`, so
   "positive reply rate" — the number outbound copy is judged on everywhere — was not expressible in
   yourco's own record. Instantly classifies interest already (`runtime/instantly.py::_is_warm`), but
   that lived in a vendor's database. `replied-positive` / `replied-negative` now exist here, and the
   legacy `replied` counts toward CONTACTED and never toward POSITIVE — a vocabulary change must not
   promote old rows into wins.
2. **`runtime/promote.py` — the only path cold leads enter the CRM by — wrote three things wrong**
   and every one of them would have fired on the first real campaign: a `prospect` stage that was
   retired in the 2026-08-07 ladder restructure (so each promoted lead lands off the board), a
   nested `seq: {status}` that nothing reads (the schema field is a flat `seqStatus`), and no
   `stageHistory` (so deals produced by outbound would carry no clock). `promote_intent.py` and
   `intent_server.py` had the dead stage too.
3. **Every Calendly link on the site was bare.** A booking from the site was indistinguishable from
   one out of an email, a connector, or a pasted URL. All 61 links across 24 pages now carry
   `utm_source=site` and the page they came from, which Calendly passes through to the booking
   record — and `Booking` is now an activity type distinct from `Meeting`, because `contact.nextMeeting`
   holds only the NEXT one and overwrites the last.

**Both metrics still refuse, and refuse loudly with the gate named.** A `0` here would read as a
verdict on the copy and on the site, when the truth is that neither has been allowed to run. That
distinction is the whole reason these are refusals rather than zeros — the same call made for Katie.

Read-only. Consumed by `dashboard/northstar.py`. CLI: `python3 dashboard/gate_metrics.py`
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO

# Contacted = anything past "not started". `replied` (legacy, undifferentiated) counts here and
# never in POSITIVE.
CONTACTED = {"sent", "opened", "replied", "replied-positive", "replied-negative", "bounced"}
POSITIVE = {"replied-positive"}
MIN_CONTACTED = 30      # no reply rate off a handful — a 1-in-8 campaign is not a 12.5% rate


def _crm():
    try:
        with open(os.path.join(ROOT, "crm", "data.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _OtherVenture_open():
    """True while the master launch gate blocks external surfaces. Read from the tracker, which is
    the only place its state lives (processes/launch-gate.md)."""
    try:
        with open(os.path.join(REPO, "processes", "launch-gate.md"), encoding="utf-8") as f:
            return "🔴" in f.read()
    except OSError:
        return True     # unreadable gate is treated as closed — never assume permission


# ── Michelle ────────────────────────────────────────────────────────────────────────────────
def positive_reply_rate():
    """Positive replies over leads contacted.

    Counted from `deal.seqStatus`, which yourco owns, rather than from Instantly's dashboard — the
    vendor holds the classification but the record has to live here or it disappears with the
    subscription."""
    crm = _crm()
    deals = (crm.get("deals") or []) + (crm.get("closed") or [])
    st = [(d.get("seqStatus") or "").strip().lower() for d in deals]
    contacted = sum(1 for s in st if s in CONTACTED)
    positive = sum(1 for s in st if s in POSITIVE)
    legacy = sum(1 for s in st if s == "replied")

    if not contacted:
        gate = ("the launch-gate is open and 10DLC registration is blocked, so nothing has been "
                "sent" if _OtherVenture_open() else "no lead carries a sequence status past 'not started'")
        return None, "%", (f"no lead has been contacted — {gate}. A 0% here would read as a verdict "
                           f"on the copy; the copy has not run.")
    if contacted < MIN_CONTACTED:
        return None, "%", (f"{contacted} lead(s) contacted — no rate below {MIN_CONTACTED}. "
                           f"One reply in eight is not a 12.5% reply rate, it is one reply.")
    note = f"{positive} positive of {contacted} contacted"
    if legacy:
        note += (f" · {legacy} carry the legacy undifferentiated 'replied' and count as contacted "
                 f"only — a vocabulary change must not promote old rows into wins")
    return round(positive / contacted * 100, 1), "%", note


# ── Webb ────────────────────────────────────────────────────────────────────────────────────
def bookings_from_site():
    """Bookings at companies the site produced.

    `Booking` is a separate activity type from `Meeting` on purpose: a booking is a slot taken, a
    meeting is one that happened, and `contact.nextMeeting` records only the next one — so without
    the activity, the second booking erases the first."""
    crm = _crm()
    cos = [c for c in (crm.get("companies") or []) if not c.get("archived")]
    site_ids = {c.get("id") for c in cos if (c.get("channel") or "") == "inbound-site"}
    bookings = [a for a in (crm.get("activities") or []) if (a.get("type") or "") == "Booking"]

    if not bookings:
        gate = ("the site is unpublished behind the launch-gate" if _OtherVenture_open()
                else "the site is live but no booking has been logged")
        return None, "bookings", (f"no booking has been logged — {gate}. The instrument is complete: "
                                  f"`Booking` is an activity type, and all 61 Calendly links across "
                                  f"the site carry utm_source so the attribution survives the click.")
    if not site_ids:
        return None, "bookings", (f"{len(bookings)} booking(s) logged, none at a company whose "
                                  f"channel is inbound-site — so none is attributable to the site "
                                  f"rather than to an email, a connector or a pasted link")
    n = sum(1 for a in bookings if a.get("companyId") in site_ids)
    return n, "bookings", (f"{n} of {len(bookings)} logged booking(s) came from a site-sourced "
                           f"company ({len(site_ids)} such compan(y/ies))")


METRICS = {
    "positiveReplyRate": positive_reply_rate,
    "bookingsFromSite": bookings_from_site,
}
MECHANISM = {
    "positiveReplyRate": "crm",
    "bookingsFromSite": "crm",
}


def main():
    print("\n=== the two behind the gate ==================================================")
    print(f"    launch-gate: {'OPEN (blocking)' if _OtherVenture_open() else 'cleared'}\n")
    for k, fn in METRICS.items():
        v, unit, note = fn()
        shown = "—" if v is None else f"{v}{'%' if unit == '%' else ' ' + unit}"
        print(f"  {k:<20} {shown:>8}   {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
