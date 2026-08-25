#!/usr/bin/env python3
"""The calibrated founder — a forecast model of the FORECASTER.

Every stage move on the board captures one extra thing: the prediction made at that
moment (close date + amount + confidence). When the deal resolves, the prediction is
graded automatically. Over time this measures the founder's own bias — per segment,
per stage — and corrects the weighted forecast by MEASURED error instead of by
generic stage probabilities.

Forecasting tools model the pipeline. This models the person doing the forecasting.

Three outputs, in increasing order of how long they take to become available:
  1. `overdue`     — live on day one: predictions whose close date has already passed
                     while the deal is still open. A hard lower bound on optimism that
                     needs no resolution at all.
  2. `bias`        — per-segment median timing error and amount ratio, once a segment
                     has MIN_N resolved predictions. Below that it refuses and says so.
  3. `forecast`    — the weighted pipeline, corrected by (2) where (2) exists, and
                     explicitly uncorrected where it doesn't.

Run:
    python3 crm/calibration.py            # the report
    python3 crm/calibration.py --json
"""
import json, os, sys, datetime, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
# Enforced by playground/check_isolation.py — a module that reads/writes off HERE
# will read the sandbox and WRITE LIVE, which is how synthetic connectors once
# landed in the real CRM (2026-08-07).
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
DATA = os.path.join(DATA_DIR, "data.json")
TODAY = datetime.date.today()

MIN_N = 5            # resolved predictions per segment before a correction is applied
BENCH = {"parked"}
TERMINAL = {"live"}

# mirrors STAGE_BASE in index.html and STAGE_P in ghost.py — change one, change all three
STAGE_BASE = {"pre-convo": 8, "discovery": 50, "demo-proposal": 70, "signed-onboarding": 90,
              "build-implementation": 93, "testing": 96, "live": 100, "parked": 3}


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def segment_of(company):
    """Same taxonomy the board segments by: warm / sourced / inbound / other."""
    if not company:
        return "other"
    if company.get("example"):
        return "example"
    s = str(company.get("source") or "").lower()
    if any(k in s for k in ("warm", "network", "referral", "family", "friend", "intro")):
        return "warm"
    if any(k in s for k in ("inbound", "site", "form", "website")):
        return "inbound"
    if any(k in s for k in ("sourced", "outbound", "cold", "instantly", "apollo", "vibe")):
        return "sourced"
    return "other"


def amount_of(d):
    v = float(d.get("value") or 0)
    return v or float(d.get("retainer") or 0) * 12 + float(d.get("buildFee") or 0)


def collect(data):
    """Every prediction ever made, joined to its outcome where one exists."""
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    rows = []

    def take(holder, resolved):
        for p in holder.get("predictions") or []:
            co = cos.get(holder.get("companyId"), {})
            rows.append({
                "dealId": holder.get("id"), "company": co.get("name") or holder.get("name"),
                "segment": segment_of(co), "madeOn": p.get("at"), "atStage": p.get("atStage"),
                "closeDate": p.get("closeDate"), "amount": float(p.get("amount") or 0),
                "confidence": p.get("confidence"), "by": p.get("by") or "the Founder",
                "resolved": resolved,
                "outcome": holder.get("outcome") if resolved else None,
                "actualClose": holder.get("closedDate") if resolved else None,
                "actualAmount": (float(holder.get("value") or 0) or
                                 float(holder.get("retainer") or 0) * 12) if resolved else None,
                "openStage": None if resolved else holder.get("stage"),
            })

    for d in data.get("deals", []) or []:
        take(d, False)
    for c in data.get("closed", []) or []:
        take(c, True)
    return rows


def grade(rows):
    """Attach the error terms. Timing/amount error only exists for a deal that actually closed won."""
    for r in rows:
        r["timingErrorDays"] = None
        r["amountRatio"] = None
        r["outcomeHit"] = None
        if not r["resolved"]:
            pd = _d(r["closeDate"])
            r["daysPastPrediction"] = (TODAY - pd).days if pd and pd < TODAY else None
            continue
        r["daysPastPrediction"] = None
        r["outcomeHit"] = (r["outcome"] == "won")
        pd, ad = _d(r["closeDate"]), _d(r["actualClose"])
        if r["outcome"] == "won" and pd and ad:
            r["timingErrorDays"] = (ad - pd).days      # + = closed later than predicted (optimistic)
        if r["outcome"] == "won" and r["amount"] and r["actualAmount"]:
            r["amountRatio"] = round(r["actualAmount"] / r["amount"], 3)
    return rows


def _bias_block(sample, label):
    timing = [r["timingErrorDays"] for r in sample if r["timingErrorDays"] is not None]
    ratios = [r["amountRatio"] for r in sample if r["amountRatio"] is not None]
    hits = [r["outcomeHit"] for r in sample if r["outcomeHit"] is not None]
    out = {"segment": label, "resolved": len(hits), "needs": max(0, MIN_N - len(hits))}
    if len(hits) < MIN_N:
        out.update({"status": "insufficient", "hitRate": None, "timingBiasDays": None, "amountBias": None,
                    "note": (f"{len(hits)} resolved prediction(s) in this segment — {MIN_N - len(hits)} more "
                             f"before a correction is applied. No bias is claimed from this sample.")})
        return out
    out["status"] = "measured"
    out["hitRate"] = round(sum(1 for h in hits if h) / len(hits), 3)
    out["timingBiasDays"] = round(statistics.median(timing), 1) if len(timing) >= 3 else None
    out["amountBias"] = round(statistics.median(ratios), 3) if len(ratios) >= 3 else None
    bits = []
    if out["timingBiasDays"] is not None:
        t = out["timingBiasDays"]
        bits.append(f"closes land a median of {abs(t):.0f}d {'later' if t > 0 else 'earlier'} than you say")
    if out["amountBias"] is not None:
        a = out["amountBias"]
        bits.append("value lands about right" if 0.9 <= a <= 1.1 else
                    f"value lands at {a:.2f}× what you predict")
    bits.append(f"{out['hitRate']*100:.0f}% of what you predicted actually won")
    out["reading"] = f"{label}: " + "; ".join(bits)
    return out


def compute(data):
    rows = grade(collect(data))
    resolved = [r for r in rows if r["resolved"]]
    open_rows = [r for r in rows if not r["resolved"]]

    segments = sorted({r["segment"] for r in rows if r["segment"] != "example"})
    bias = {s: _bias_block([r for r in resolved if r["segment"] == s], s) for s in segments}
    bias["_all"] = _bias_block(resolved, "all deals")

    # --- day-one signal: predictions already past their own date, deal still open ----
    overdue = sorted([r for r in open_rows if r.get("daysPastPrediction")],
                     key=lambda r: -r["daysPastPrediction"])
    od_median = round(statistics.median([r["daysPastPrediction"] for r in overdue]), 1) if overdue else None

    # --- corrected forecast ---------------------------------------------------------
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    latest = {}
    for r in open_rows:
        cur = latest.get(r["dealId"])
        if not cur or str(r["madeOn"] or "") > str(cur["madeOn"] or ""):
            latest[r["dealId"]] = r

    fc, raw_total, corr_total, uncorrected = [], 0.0, 0.0, 0
    for d in data.get("deals", []) or []:
        if d.get("stage") in BENCH or d.get("stage") in TERMINAL:
            continue
        co = cos.get(d.get("companyId"), {})
        seg = segment_of(co)
        p = latest.get(d.get("id"))
        base = STAGE_BASE.get(d.get("stage"), 15) / 100.0
        amt = amount_of(d)
        b = bias.get(seg) or bias["_all"]
        row = {"dealId": d.get("id"), "company": co.get("name") or d.get("name"), "segment": seg,
               "stage": d.get("stage"), "amount": amt,
               "predicted": {"closeDate": p["closeDate"], "amount": p["amount"],
                             "confidence": p["confidence"], "madeOn": p["madeOn"]} if p else None,
               "corrected": None, "basis": "uncorrected",
               "why": "no measured bias for this segment yet — the stage prior is used unchanged"}
        raw_total += amt * base
        if b["status"] == "measured":
            k = 4
            blended = ((base * k) + b["hitRate"] * b["resolved"]) / (k + b["resolved"])
            cd = _d(p["closeDate"]) if p and p.get("closeDate") else None
            row["corrected"] = {
                "prob": round(blended, 3),
                "closeDate": (cd + datetime.timedelta(days=b["timingBiasDays"])).isoformat()
                             if cd and b["timingBiasDays"] is not None else None,
                "amount": round((p["amount"] if p and p.get("amount") else amt) * b["amountBias"])
                          if b["amountBias"] is not None else None,
            }
            row["basis"] = "corrected"
            row["why"] = f"corrected by your measured {seg} bias (n={b['resolved']})"
            corr_total += (row["corrected"]["amount"] or amt) * blended
        else:
            uncorrected += 1
            corr_total += amt * base
        fc.append(row)

    return {
        "generated": TODAY.isoformat(),
        "minResolvedPerSegment": MIN_N,
        "predictionsTotal": len(rows), "predictionsOpen": len(open_rows), "predictionsResolved": len(resolved),
        "bias": bias,
        "overdue": overdue, "overdueMedianDays": od_median,
        "forecast": fc,
        "rawWeighted": round(raw_total), "correctedWeighted": round(corr_total),
        "uncorrectedDeals": uncorrected,
        "unpredictedDeals": [f["company"] for f in fc if not f["predicted"]],
        "honesty": (f"A segment's bias is applied only after {MIN_N} resolved predictions in it. Until then the "
                    "forecast runs on the unchanged stage prior and says so per deal — no correction is "
                    "invented from a small sample. The overdue list needs no resolutions and is live immediately: "
                    "it is a lower bound on timing optimism, not the full bias."),
    }


def main():
    with open(DATA) as f:
        data = json.load(f)
    r = compute(data)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Calibration ledger — {r['predictionsTotal']} prediction(s): "
          f"{r['predictionsOpen']} open, {r['predictionsResolved']} resolved\n")
    if r["overdue"]:
        print(f"Already past your own predicted close date (median {r['overdueMedianDays']}d):")
        for o in r["overdue"]:
            print(f"  {o['company'][:30]:<30} said {o['closeDate']} — {o['daysPastPrediction']}d ago, still {o['openStage']}")
        print()
    print("Measured bias:")
    for k, b in r["bias"].items():
        print(f"  {b.get('reading') or (b['segment'] + ': ' + b['note'])}")
    print(f"\nWeighted pipeline: ${r['rawWeighted']:,} on the stage prior → "
          f"${r['correctedWeighted']:,} corrected ({r['uncorrectedDeals']} deal(s) uncorrected)")
    if r["unpredictedDeals"]:
        print(f"\nNo prediction on record: {', '.join(r['unpredictedDeals'])}")
        print("  (every stage move from now on captures one — that is where the ledger fills from)")
    print(f"\n{r['honesty']}")


if __name__ == "__main__":
    main()
