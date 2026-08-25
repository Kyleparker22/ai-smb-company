#!/usr/bin/env python3
"""Does the money we METERED match the money we EXPLAINED?

THE FAILURE THIS EXISTS TO CATCH
  finance/token_spend.md is the ledger of where yourco's model spend went. Nothing ever
  compared it against what Anthropic actually billed. So `Pre Build Ideas/` — 577 files and
  108 commits — could be built across August and appear in the ledger zero times, and the
  books looked fine, because a ledger with a missing row is indistinguishable from a ledger
  with nothing to add.

  This makes the gap a number. It does not attribute it: it can say "$48 of metered API spend
  is unexplained this month" and it must not guess what caused it.

THE DISTINCTION THAT MAKES IT HONEST
  Two kinds of spend live in that ledger and only one is reconcilable:

    API        claude -p, scripts, the runtime loops. Real variable cost, billed per token,
               and visible in the Admin cost_report feed. THIS is what reconciles.
    Cowork     interactive sessions on the Max subscription. Logged as "$0 marginal" because
               that is true — the seat is already paid for. It NEVER appears in the meter, so
               comparing it would manufacture a discrepancy out of nothing.

  A naive "sum the ledger, compare to the bill" check would be wrong in both directions. This
  one compares API to API and reports Cowork separately as what it is: real work, no marginal
  cost, unverifiable by construction.

  ⚠️ Cowork being $0 marginal is a billing fact, not a licence to skip logging it. The rows
  still matter — they are the record of WHERE THE EFFORT WENT, which is the question the
  ledger gets asked. Zero-cost is not zero-value.

USAGE
  python3 runtime/cost_reconcile.py            human-readable
  python3 runtime/cost_reconcile.py --json     machine-readable
"""
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "finance", "token_spend.md")
METER = os.path.join(ROOT, "loops", "_anthropic", "latest.json")

# A row counts as API-metered only if its source column says so. Anything else is either a
# Cowork self-report or an estimate, and neither is comparable to the bill.
API_SRC = re.compile(r"meter|admin api|claude -p|console", re.I)
COWORK = re.compile(r"cowork|max plan|marginal", re.I)
MONEY = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)")


def rows():
    """Ledger rows as dicts. Sub-tables and separators are skipped, not guessed at."""
    out = []
    for line in open(LEDGER, encoding="utf-8"):
        if not line.startswith("|") or re.match(r"\|\s*-+", line):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 7 or c[0].lower() == "month":
            continue
        if not re.match(r"20\d\d-\d\d", c[0]):        # only rows keyed by a real month
            continue
        out.append({"month": c[0][:7], "engagement": c[1], "model": c[2],
                    "description": c[3], "cost": c[4], "date": c[5], "source": c[6]})
    return out


def amount(text):
    """First dollar figure in a cell, or None. A range like '~$3–5' takes the LOW end —
    under-claiming what we have explained is the safe direction for a gap report."""
    m = MONEY.search(text or "")
    return float(m.group(1).replace(",", "")) if m else None


def metered_by_month():
    if not os.path.exists(METER):
        return {}, None
    d = json.load(open(METER, encoding="utf-8"))
    by = {}
    for day in d.get("days", []):
        by[day["date"][:7]] = by.get(day["date"][:7], 0.0) + (day.get("usd") or 0.0)
    return by, d.get("fetched")


def reconcile():
    led, (met, fetched) = rows(), metered_by_month()
    months = sorted(set(list(met) + [r["month"] for r in led]), reverse=True)
    out = []
    for m in months:
        mine = [r for r in led if r["month"] == m]
        api = [r for r in mine if API_SRC.search(r["source"]) and not COWORK.search(r["source"])]
        cow = [r for r in mine if COWORK.search(r["source"]) or COWORK.search(r["cost"])]
        other = [r for r in mine if r not in api and r not in cow]
        attributed = sum(a for a in (amount(r["cost"]) for r in api) if a)
        billed = met.get(m)
        out.append({
            "month": m,
            "metered": round(billed, 2) if billed is not None else None,
            "attributedApi": round(attributed, 2),
            "unexplained": round(billed - attributed, 2) if billed is not None else None,
            "apiRows": len(api), "coworkRows": len(cow), "otherRows": len(other),
            "totalRows": len(mine),
        })
    return {"generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "meterFetched": fetched, "months": out}


# A month where real work shipped and the ledger says nothing is the Pre Build Ideas pattern —
# the specific failure this file was written for. Commits are the cheapest available proxy for
# "work happened"; it is a signal, never a verdict.
def silent_months(threshold=25):
    import subprocess
    log = subprocess.run(["git", "-C", ROOT, "log", "--format=%ad", "--date=format:%Y-%m"],
                         capture_output=True, text=True, timeout=60).stdout.split()
    by = {}
    for m in log:
        by[m] = by.get(m, 0) + 1
    have = {r["month"] for r in rows()}
    return [{"month": m, "commits": n} for m, n in sorted(by.items(), reverse=True)
            if n >= threshold and m not in have]


def report():
    d = reconcile()
    silent = silent_months()
    L = []
    L.append("# Cost reconciliation — metered vs explained")
    L.append("")
    L.append(f"_Generated {d['generated']}. Meter last fetched: {d['meterFetched'] or 'never'}._")
    L.append("")
    L.append("| month | metered (API) | explained (API) | unexplained | rows: api / cowork / other |")
    L.append("|---|---:|---:|---:|---|")
    for m in d["months"][:8]:
        met = f"${m['metered']:.2f}" if m["metered"] is not None else "—"
        un = "—"
        if m["unexplained"] is not None:
            un = f"**${m['unexplained']:.2f}**" if m["unexplained"] > 5 else f"${m['unexplained']:.2f}"
        L.append(f"| {m['month']} | {met} | ${m['attributedApi']:.2f} | {un} | "
                 f"{m['apiRows']} / {m['coworkRows']} / {m['otherRows']} |")
    L.append("")
    L.append("**Unexplained is a gap, not an accusation.** It means metered API spend that no "
             "ledger row claims. The honest response is to find the work and log it — not to "
             "adjust the number.")
    L.append("")
    L.append("**Cowork rows are excluded from the comparison on purpose.** Interactive sessions "
             "run on the Max subscription at $0 marginal cost and never reach the meter. They "
             "still belong in the ledger: zero-cost is not zero-value, and the ledger's real job "
             "is recording where the effort went.")
    if silent:
        L.append("")
        L.append("## Months where work shipped and the ledger is silent")
        L.append("")
        for s in silent:
            L.append(f"- **{s['month']}** — {s['commits']} commits, **0 ledger rows**. "
                     f"This is the `Pre Build Ideas/` pattern: real work, no record.")
    return "\n".join(L)


if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps({**reconcile(), "silentMonths": silent_months()}, indent=2))
    else:
        print(report())
