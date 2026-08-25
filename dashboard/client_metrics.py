#!/usr/bin/env python3
"""yourco — the six numbers waiting on client #1, and the three that would have been lost anyway.

Third cluster from the 2026-08-25 metric sweep (`dashboard/northstar.py`). Six agents owned a number
that needed a customer, and **no amount of building produces a customer.** So the honest question was
not "how do we make these read a value" — it was:

    *When client #1 finally lands, will these numbers actually compute — or will the data
    already have been destroyed, never captured, or scoped to something the agent cannot move?*

For three of the six the answer was no, and that is what got fixed.

**THE ONE THAT COULD ONLY BE FIXED BEFORE THE FACT.** `deal.stageSince` records only the CURRENT
stage's entry date. The moment a deal advances, the date it entered the previous stage is
**overwritten**, and nothing else recorded it — there were **zero** stage-change activities in the
whole log. So *days from signature to go-live* (Janice) and *days from discovery to go-live* (Kimi)
would have been unmeasurable **after** client #1 as well: by the time anyone asked, the answer would
already be gone. `deal.stageHistory` now appends on every move. History before 2026-08-25 is
genuinely lost for existing deals and these functions say so rather than filling it in.

**TWO WERE SCOPED TO SOMEONE ELSE'S OUTCOME.** Reed's number was "assets that appeared in a *won*
deal" — a production agent graded on whether the Founder closes. Re-scoped to **reach**: an asset that got
in front of a prospect did its job; what happened next is the sales agent's number. Pickle was
re-scoped the same way in the CRM cluster, and the two now share a single blocker — *nothing is
registered on the deal where it was used*, which is one habit, not two problems.

**ONE WAS ALREADY COMPUTABLE.** Polo's "proposals at a locked band" needed no customer at all: a
price is quoted before anything is signed, `deal.priceEvents` has recorded one since 2026-08-13, and
`pricing/README.md` carries the locked band table. It reads **0 of 1** — the only price ever quoted
sits below every band, including the on-ramp floor. That is exactly the failure the metric exists to
catch, and it was sitting in the data the whole time.

**THE THREE THAT ARE HONESTLY JUST WAITING.** Harry (an invoice), Kortney (a live client to score)
and the go-live durations need the event itself. Their instruments are now complete and empty —
`finance/actuals.json.invoices` and `deal.health` — on the same principle as `agent_budgets`: the
meter goes in before the first reading, because a meter installed afterwards measures nothing that
already happened.

Read-only. Consumed by `dashboard/northstar.py`. CLI: `python3 dashboard/client_metrics.py`
"""
import os, re, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO

SIGNED_STAGE = "signed-onboarding"
LIVE_STAGE = "live"
DISCOVERY_STAGE = "discovery"


def _crm():
    try:
        with open(os.path.join(ROOT, "crm", "data.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _actuals():
    try:
        with open(os.path.join(ROOT, "finance", "actuals.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _entered(deal, stage):
    """The date a deal entered `stage`, or None. Reads stageHistory only — never `stageSince`,
    which answers a different question (when did it enter its CURRENT stage) and would silently
    return the wrong date for any stage the deal has already left."""
    for h in (deal.get("stageHistory") or []):
        if h.get("stage") == stage and h.get("at"):
            return h["at"], (h.get("source") or "recorded")
    return None, None


def _days(a, b):
    try:
        return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days
    except (TypeError, ValueError):
        return None


def _durations(from_stage):
    """Days from `from_stage` to live, across every deal that has reached live."""
    crm = _crm()
    deals = (crm.get("deals") or []) + (crm.get("closed") or [])
    live = [d for d in deals if (d.get("stage") or "") == LIVE_STAGE]
    if not live:
        return None, [], 0
    spans, lost = [], 0
    for d in live:
        a, _sa = _entered(d, from_stage)
        b, _sb = _entered(d, LIVE_STAGE)
        n = _days(a, b) if (a and b) else None
        if n is None:
            lost += 1
        else:
            spans.append(n)
    return live, spans, lost


# ── Janice ──────────────────────────────────────────────────────────────────────────────────
def days_to_go_live():
    """Signature → live. The 48-hour go-live is a public promise; onboarding keeps it or it doesn't."""
    live, spans, lost = _durations(SIGNED_STAGE)
    if live is None:
        return None, "days", ("no deal has reached live. deal.stageHistory now appends on every "
                              "move, so this computes on the day the first one does — before "
                              "2026-08-25 the interval would have been gone by then")
    if not spans:
        return None, "days", (f"{lost} live deal(s), none carrying both a signed and a live entry in "
                              f"stageHistory — the transitions predate the history and are lost")
    return (round(sum(spans) / len(spans)), "days",
            f"median across {len(spans)} engagement(s)"
            + (f" · {lost} excluded, history predates the record" if lost else ""))


# ── Kimi ────────────────────────────────────────────────────────────────────────────────────
def days_discovery_to_go_live():
    """Discovery → live. Kimi builds the thing yourco sells; delivery speed is the headline claim."""
    live, spans, lost = _durations(DISCOVERY_STAGE)
    if live is None:
        return None, "days", ("no engagement has reached live — nothing to time. The clock is "
                              "recorded from now on (deal.stageHistory)")
    if not spans:
        return None, "days", (f"{lost} live deal(s) carry no discovery entry in stageHistory — "
                              f"lost to the pre-2026-08-25 record")
    return (round(sum(spans) / len(spans)), "days",
            f"median across {len(spans)} engagement(s)"
            + (f" · {lost} excluded, history predates the record" if lost else ""))


# ── Kortney ─────────────────────────────────────────────────────────────────────────────────
def clients_healthy():
    """Live clients scored green. Retention starts before renewal — health is the leading half.

    An unscored live client is NOT counted as healthy: 'nobody looked' and 'it's fine' are
    different facts, and only one of them is good news."""
    crm = _crm()
    live = [d for d in (crm.get("deals") or []) if (d.get("stage") or "") == LIVE_STAGE]
    if not live:
        return None, "healthy", ("no live client to score — deal.health is the instrument and it is "
                                 "waiting, not missing")
    scored = [d for d in live if (d.get("health") or "").strip()]
    green = sum(1 for d in scored if d.get("health") == "green")
    if not scored:
        return None, "healthy", (f"{len(live)} live client(s) and none carries a health score — "
                                 f"unscored is not healthy, so this refuses rather than reporting "
                                 f"{len(live)}")
    return green, "healthy", (f"{green} green of {len(scored)} scored"
                              + (f" · {len(live) - len(scored)} unscored" if len(scored) < len(live) else ""))


# ── Harry ───────────────────────────────────────────────────────────────────────────────────
def invoices_paid_on_time():
    """Invoices paid inside their own terms. An invoice still WITHIN terms is neither paid-on-time
    nor late, so it is excluded from both halves rather than quietly counted as a failure."""
    rows = ((_actuals().get("invoices") or {}).get("rows")) or []
    if not rows:
        return None, "%", ("no invoice has been issued — finance/actuals.json.invoices is the "
                           "instrument and it is deliberately empty, on the same principle as the "
                           "agent budgets: the meter goes in before the first reading")
    today = datetime.date.today().isoformat()
    resolved, ontime = 0, 0
    for r in rows:
        issued, terms, paid = r.get("issued"), r.get("termsDays"), r.get("paidOn")
        if not issued or terms is None:
            continue
        due = _days(issued, today)
        if paid:
            resolved += 1
            n = _days(issued, paid)
            if n is not None and n <= terms:
                ontime += 1
        elif due is not None and due > terms:
            resolved += 1                      # unpaid past terms is a resolved failure
    if not resolved:
        return None, "%", f"{len(rows)} invoice(s), none yet resolved — all still inside their terms"
    return round(ontime / resolved * 100), "%", f"{ontime} of {resolved} resolved invoices paid within terms"


# ── Reed ─────────────────────────────────────────────────────────────────────────────────
def _published_assets():
    """Published rows in Reed's asset registry — the denominator, and it is real today."""
    try:
        md = open(os.path.join(REPO, "agents/Reed/_asset_registry.md"), encoding="utf-8").read()
    except OSError:
        return None
    import board
    rows = board._tables(md, r"^registry")
    return [r for r in rows if len(r) >= 3 and "published" in (r[2] or "").lower()]


def videos_reached_prospect():
    """Published assets that got in front of a prospect, over assets published.

    RE-SCOPED 2026-08-25. The original was 'assets that appeared in a won deal', which graded a
    production agent on whether the founder closes. Reach is the boundary of what Reed controls;
    what happens after the prospect watches it is the sales agent's number."""
    made = _published_assets()
    if made is None:
        return None, "%", "agents/Reed/_asset_registry.md is unreadable"
    if not made:
        return None, "%", "no asset is marked published in the registry — nothing to have reached anyone"
    crm = _crm()
    shown = set()
    for d in (crm.get("deals") or []) + (crm.get("closed") or []):
        for a in (d.get("artifacts") or []):
            if (a.get("type") or "") == "video" and (a.get("status") or "") in ("shown", "reacted"):
                shown.add((a.get("name") or a.get("id") or "").strip().lower())
    if not shown:
        return None, "%", (f"{len(made)} published asset(s) and not one is registered on a deal as "
                           f"type `video` — the same missing habit that blocks Pickle: nothing is "
                           f"linked to the deal it was used on. 0% would claim the habit exists and "
                           f"failed.")
    return round(len(shown) / len(made) * 100), "%", f"{len(shown)} of {len(made)} published assets reached a prospect"


# ── Polo ────────────────────────────────────────────────────────────────────────────────────
BAND_RE = re.compile(r"^\|\s*\**\*?([A-Za-z][A-Za-z \-—–]*?)\*?\**\s*\|[^|]*\|[^|]*\|\s*(.+?)\s*\|\s*$", re.M)
# 3+ characters, so a bare "3" out of "cap 3, then graduate" is not read as a $3 retainer. The first
# version did exactly that and reported the $1,000 brotherhood rate as sitting inside the on-ramp
# band ($3–$1,500) — a false pass on the one metric whose whole job is catching an off-band price.
MONEY_RE = re.compile(r"([\d][\d,]{2,})")
MIN_PLAUSIBLE_RETAINER = 500


def locked_bands():
    """The retainer ranges from the locked tier table in pricing/README.md.

    Parsed rather than copied: a second machine-readable copy of a price is a drift surface, and
    price drift is the failure this repo has already had three times."""
    try:
        md = open(os.path.join(REPO, "pricing/README.md"), encoding="utf-8").read()
    except OSError:
        return []
    out = []
    for m in BAND_RE.finditer(md):
        name, retainer = m.group(1).strip(), m.group(2)
        if "Retainer" in retainer or not name or "$" not in retainer:
            continue
        nums = [int(n.replace(",", "")) for n in MONEY_RE.findall(retainer)]
        nums = [n for n in nums if n >= MIN_PLAUSIBLE_RETAINER]
        if not nums:
            continue      # a row whose retainer cell carries no plausible figure is skipped, not guessed
        out.append((name, min(nums), max(nums)))
    return out


def proposals_at_locked_price():
    """Quoted prices that sat inside a locked band. A COUNT, not a rate — with one quote on record a
    percentage would be theatre, and the raw sentence is the useful one."""
    bands = locked_bands()
    if not bands:
        return None, "quoted", ("the locked tier table in pricing/README.md did not parse — refusing "
                                "rather than declaring every price off-band")
    crm = _crm()
    quotes = [(d.get("id"), p) for d in (crm.get("deals") or []) + (crm.get("closed") or [])
              for p in (d.get("priceEvents") or []) if (p.get("kind") or "") == "quoted"]
    if not quotes:
        return None, "quoted", "no price has been quoted — deal.priceEvents is empty"
    inband = 0
    for _id, p in quotes:
        amt = p.get("amount")
        if isinstance(amt, (int, float)) and any(lo <= amt <= hi for _n, lo, hi in bands):
            inband += 1
    return inband, "in band", (f"{inband} of {len(quotes)} quoted price(s) sat inside a locked band "
                               f"({len(bands)} bands read from pricing/README.md)")


METRICS = {
    "daysToGoLive": days_to_go_live,
    "daysDiscoveryToGoLive": days_discovery_to_go_live,
    "clientsHealthy": clients_healthy,
    "invoicesPaidOnTime": invoices_paid_on_time,
    "videosReachedProspect": videos_reached_prospect,
    "proposalsAtLockedPrice": proposals_at_locked_price,
}
MECHANISM = {k: "crm" for k in METRICS}
MECHANISM["invoicesPaidOnTime"] = "finance"
MECHANISM["videosReachedProspect"] = "extracted"


def main():
    print("\n=== the six waiting on client #1 =============================================")
    print("    bands read from pricing/README.md: "
          + ", ".join(f"{n} ${lo:,}–${hi:,}" for n, lo, hi in locked_bands()) + "\n")
    for k, fn in METRICS.items():
        v, unit, note = fn()
        shown = "—" if v is None else f"{v}{'%' if unit == '%' else ' ' + unit}"
        print(f"  {k:<24} {MECHANISM[k]:<10} {shown:>12}   {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
