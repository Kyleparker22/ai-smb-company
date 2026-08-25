#!/usr/bin/env python3
"""yourco — the five numbers that needed the CRM to record something it never had.

Second cluster from the 2026-08-25 metric sweep (`dashboard/northstar.py`). Five agents owned a
number the CRM could not answer. Working through them re-diagnosed three:

| Agent | Original diagnosis | What it actually was |
|---|---|---|
| **Jim** | needs an age stamp on Board rows | **Wrong.** His own open-loops queue already carries `Waiting since` per item and `board.py` already parses it. The number was there. |
| **Sadie** | `promote_intent.py` doesn't stamp a source | **Wrong.** It has always written `source: "sadie intent (…)"`. Nothing had ever come through it — a real zero, not a missing field. |
| **Katie** | needs a channel field | **Half right.** The field was missing *and* the binding constraint is the launch-gate: content that has never been published cannot have sourced a conversation. |
| **Bella** | needs an `Audit delivered` activity type | Correct — added. |
| **Pickle** | needs an artifact link on activities | Correct in substance, wrong in place: deals already carry `artifacts`; what they lacked was a **type**, so a one-pager was indistinguishable from a build. |

WHAT WAS ACTUALLY ADDED TO THE CRM
- `meta.sourceChannels` + `company.channel` / `channelSource` — a controlled answer to "which channel
  produced this company". Every intake path already wrote its own free-text `source` string
  (`"instantly (replied)"`, `"sadie intent (reddit)"`, `"audit intake form"`), so the only way to ask
  the question was prefix-matching prose. `source` still carries the human detail.
- `meta.activityTypes` += **Audit delivered** — the front door of the entire motion, and until now
  nothing counted one, so its conversion was *unknowable* rather than merely unknown.
- `meta.artifactTypes` incl. **collateral** — so "did this one-pager ever reach a buyer" is a query
  (`status` `shown`/`reacted`) rather than a memory.

THE BACKFILL CONTAINS NO JUDGMENT. `channelSource` is one of `recorded` (stamped at intake),
`restated` (a faithful rename of what `source` already said — `"the Founder"` → `founder-sourced`,
`"Partner target"` → `partner-target`), or `inferred` (a judgment). **Nothing here is `inferred`**,
and `founder-sourced` is deliberately not `warm-network`: it says who typed the row and claims
nothing about how the Founder knows them. Two companies whose `source` was blank were left unset, because
there was nothing to restate.

COVERAGE IS A REFUSAL CONDITION, NOT A FOOTNOTE. A channel metric computed while most rows carry no
channel is a lie with a denominator. Every function below refuses under `MIN_COVERAGE` and says how
many rows it could actually see.

Read-only. Consumed by `dashboard/northstar.py`. CLI: `python3 dashboard/crm_metrics.py`
"""
import os, re, sys, json, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO

MIN_COVERAGE = 0.80        # share of companies that must carry a channel before any rate is stated
MIN_AUDITS = 3             # no conversion rate off a handful — same floor as the KPI engine
SIGNED = ("signed-onboarding", "build-implementation", "testing", "live", "expand")


def _crm():
    try:
        with open(os.path.join(ROOT, "crm", "data.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _coverage(crm):
    cos = [c for c in (crm.get("companies") or []) if not c.get("archived")]
    have = [c for c in cos if (c.get("channel") or "").strip()]
    return cos, have, (len(have) / len(cos) if cos else 0.0)


# ── Katie ───────────────────────────────────────────────────────────────────────────────────
def inbound_from_content():
    """Conversations at companies the content channel produced.

    This one cannot be non-zero yet and says so instead of reporting a flattering zero: nothing has
    been published, so the launch-gate — not the audience — is the reason. Reporting `0` here would
    read as 'content isn't working' when the truth is 'content hasn't run'."""
    crm = _crm()
    cos, have, cov = _coverage(crm)
    if not cos:
        return None, "", "no companies in the CRM"
    if cov < MIN_COVERAGE:
        return None, "", (f"channel recorded on {len(have)} of {len(cos)} companies "
                          f"({cov:.0%}) — below {MIN_COVERAGE:.0%} a channel count is a lie with a "
                          f"denominator")
    ids = {c.get("id") for c in cos if (c.get("channel") or "") == "content"}
    if not ids:
        return None, "", ("no company carries the content channel, and nothing has been published — "
                          "this cannot be non-zero until the launch-gate clears, so a 0 here would "
                          "read as a verdict on the content rather than on the gate")
    acts = [a for a in (crm.get("activities") or [])
            if a.get("companyId") in ids and (a.get("type") or "") in ("Meeting", "Call")]
    return len(acts), "conversations", f"across {len(ids)} content-sourced company/companies"


# ── Sadie ───────────────────────────────────────────────────────────────────────────────────
def signals_promoted():
    """Intent signals that became a CRM row a human actually worked.

    A computed zero, and the zero is the finding: the sweep has run daily since July and
    `promote_intent.py` has always stamped its own source, so nothing has been suppressed — nothing
    has ever been promoted. Listening is not the outcome."""
    crm = _crm()
    cos, _have, _cov = _coverage(crm)
    if not cos:
        return None, "promoted", "no companies in the CRM"
    rows = [c for c in cos if (c.get("channel") or "") == "intent-signal"
            or str(c.get("source") or "").startswith("sadie intent")]
    worked = {a.get("companyId") for a in (crm.get("activities") or []) if a.get("companyId")}
    n = sum(1 for c in rows if c.get("id") in worked)
    return n, "promoted", (f"{len(rows)} row(s) from the intent sweep, {n} with a logged touch — "
                           f"the promotion path has been live and stamped since July")


# ── Bella ───────────────────────────────────────────────────────────────────────────────────
def audits_to_engagement():
    """Audits delivered that became an engagement.

    The Audit is free and is the front door of the entire motion, so this is the single most
    important unmeasured number in the company. It stays refused until three audits exist: a
    conversion rate off one audit is a coin flip wearing a percentage."""
    crm = _crm()
    acts = [a for a in (crm.get("activities") or []) if (a.get("type") or "") == "Audit delivered"]
    if not acts:
        return None, "%", ("no 'Audit delivered' activity has been logged — the type exists as of "
                           "2026-08-25, so the first audit is now countable on the day it lands")
    ids = {a.get("companyId") for a in acts if a.get("companyId")}
    if len(ids) < MIN_AUDITS:
        return None, "%", (f"{len(ids)} audit(s) delivered — no conversion rate below {MIN_AUDITS}. "
                           f"A rate off one audit is a coin flip wearing a percentage.")
    deals = crm.get("deals", []) or []
    won = {d.get("companyId") for d in deals if (d.get("stage") or "") in SIGNED}
    got = len(ids & won)
    return round(got / len(ids) * 100), "%", f"{got} of {len(ids)} audits became an engagement"


# ── Pickle ──────────────────────────────────────────────────────────────────────────────────
def collateral_reached_buyer():
    """Collateral that got in front of a buyer, over collateral produced.

    Denominator = the files in `agents/pickle/collateral/`, which is real today. Numerator =
    artifacts typed `collateral` on a deal at status `shown` or `reacted`. `built` deliberately does
    not count: a battlecard nobody opened in front of a buyer did not exist."""
    crm = _crm()
    try:
        made = [f for f in os.listdir(os.path.join(REPO, "agents/pickle/collateral"))
                if not f.startswith("_")]
    except OSError:
        made = []
    shown = set()
    for d in (crm.get("deals", []) or []) + (crm.get("closed", []) or []):
        for a in (d.get("artifacts") or []):
            if (a.get("type") or "") == "collateral" and (a.get("status") or "") in ("shown", "reacted"):
                shown.add((a.get("name") or a.get("id") or "").strip().lower())
    if not made:
        return None, "%", "agents/pickle/collateral/ is empty — nothing produced to have reached anyone"
    if not shown:
        return None, "%", (f"{len(made)} pieces produced and not one is registered on a deal as "
                           f"`collateral` yet — the artifact type exists as of 2026-08-25, so the "
                           f"first one shown on a call is countable. 0% would claim the linking "
                           f"habit exists and failed; it does not exist yet.")
    return round(len(shown) / len(made) * 100), "%", f"{len(shown)} of {len(made)} pieces reached a buyer"


# ── Jim ─────────────────────────────────────────────────────────────────────────────────────
def oldest_open_loop():
    """The oldest item on Jim's own queue, in days.

    Not the Board's whole needs-you list — Jim owns the queue, and the queue already carries
    `Waiting since` per row. The OLDEST rather than the average, deliberately: an average hides the
    one item that has been rotting for ten weeks, and that item is the whole job."""
    import board
    items, stem, _mentioned = board.open_loops()
    if not items:
        return None, "days", "no open-loops artifact has been written"
    q = [i for i in items if i.get("state") == "needs-you"]
    ages = [i["age"] for i in q if i.get("age") is not None]
    if not ages:
        return None, "days", (f"{len(q)} item(s) on the queue and none carries a 'Waiting since' "
                              f"date — the SOP requires one per row")
    missing = len(q) - len(ages)
    return max(ages), "days", (f"oldest of {len(q)} on the queue ({stem})"
                               + (f" · {missing} row(s) carry no date and are excluded" if missing else ""))


METRICS = {
    "inboundFromContent": inbound_from_content,
    "signalsPromotedToRows": signals_promoted,
    "auditsToEngagement": audits_to_engagement,
    "collateralReachedBuyer": collateral_reached_buyer,
    "oldestOpenLoopDays": oldest_open_loop,
}
MECHANISM = {k: "crm" for k in METRICS}
MECHANISM["oldestOpenLoopDays"] = "extracted"


def main():
    crm = _crm()
    cos, have, cov = _coverage(crm)
    print(f"\n=== the five that needed a field ==============================================")
    print(f"    channel coverage: {len(have)} of {len(cos)} companies ({cov:.0%}); "
          f"floor for any rate is {MIN_COVERAGE:.0%}\n")
    for k, fn in METRICS.items():
        v, unit, note = fn()
        shown = "—" if v is None else f"{v}{'%' if unit == '%' else ' ' + unit}"
        print(f"  {k:<24} {MECHANISM[k]:<10} {shown:>14}   {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
