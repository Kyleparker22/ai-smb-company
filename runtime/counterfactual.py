#!/usr/bin/env python3
"""Counterfactual twin — the client's business as it would be running without the OS.

The renewal conversation is usually a slide that says "we saved you time." This is the other
version: a shadow model of the client's business carried forward from their **own pre-engagement
baseline**, compared monthly against their **own actuals**. The gap is the argument, and it is
built from their numbers rather than our claims.

yourco's CRM already has `ghost` — where every deal would be at your own median velocity. This is
the same instrument pointed at the customer.

THE LABEL THAT NEVER COMES OFF
**A counterfactual is a model, not a measurement.** Nobody observed the business that didn't
happen. Every output of this module carries `isModel: true` and the assumption behind each metric,
because the moment a modelled number is quoted as a measured one, the whole instrument becomes a
liability — and it would be quoted that way in a renewal meeting if we let it.

WHAT IT REFUSES
- No `baseline.json` -> refuses. There is no counterfactual without a before.
- A metric measured today with no baseline -> **excluded and named**, never assumed flat.
- A baseline metric with no stated trend -> held flat, and the holding is disclosed per metric.
  Flat is itself an assumption and gets said out loud.
- A baseline older than `STALE_MONTHS` -> still computed, but flagged: the further you project,
  the more the model is arithmetic rather than evidence.

  python3 runtime/counterfactual.py --client _yourco-template
"""
import os, sys, json, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLIENTS = os.path.join(ROOT, "clients")

BASELINE = "baseline.json"
FACTS = "facts.json"
STALE_MONTHS = 12


def _load(client, name):
    p = os.path.join(CLIENTS, client, name)
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"no {name} in clients/{client}/"
    except ValueError as e:
        return None, f"{name} is not valid JSON ({e})"


def _months_between(a, b):
    return max(0, (b.year - a.year) * 12 + (b.month - a.month))


def build_client(client, today=None):
    today = today or datetime.date.today()
    base, err = _load(client, BASELINE)
    if err:
        return {"client": client, "available": False, "reason": err,
                "meaning": "no counterfactual without a before — the baseline is captured at "
                           "discovery and cannot be reconstructed later"}
    facts_doc, ferr = _load(client, FACTS)
    facts = (facts_doc or {}).get("facts") or {}

    captured = str(base.get("capturedOn") or "")
    try:
        cap_date = datetime.date.fromisoformat(captured)
    except ValueError:
        return {"client": client, "available": False,
                "reason": f"baseline.capturedOn is missing or unparseable ({captured!r})"}
    months = _months_between(cap_date, today)

    rows, excluded = [], []
    for key, spec in (base.get("metrics") or {}).items():
        if not isinstance(spec, dict) or not isinstance(spec.get("value"), (int, float)):
            excluded.append({"metric": key, "why": "baseline value missing or not numeric"})
            continue
        b = float(spec["value"])
        trend = spec.get("monthlyTrendPct")
        stated = isinstance(trend, (int, float)) and not isinstance(trend, bool)
        rate = float(trend) / 100.0 if stated else 0.0
        projected = b * ((1 + rate) ** months)
        actual = facts.get(key)
        row = {
            "metric": key,
            "label": spec.get("label") or key,
            "baseline": b,
            "capturedOn": captured,
            "monthsElapsed": months,
            "trendPctPerMonth": trend if stated else None,
            "trendStated": stated,
            # A custom assumption never REPLACES the flat disclosure, only precedes it. The
            # template's own baseline supplied a polite "held flat" sentence that omitted the
            # caveat, which is exactly how the disclosure would quietly disappear in the field.
            "assumption": ((spec.get("assumption")
                            or f"carried forward at {trend}%/month, the client's own stated "
                               f"pre-engagement trend")
                           if stated else
                           ((spec["assumption"] + " — " if spec.get("assumption") else "")
                            + "HELD FLAT: no trend was stated at capture, so the model assumes "
                              "the business would not have changed. Flat is an assumption, not a "
                              "neutral choice")),
            "counterfactual": round(projected, 2),
            "actual": actual if isinstance(actual, (int, float)) else None,
            "lowerIsBetter": bool(spec.get("lowerIsBetter")),
        }
        if row["actual"] is None:
            row["gap"] = None
            row["gapNote"] = "not measured today — no comparison is possible, and none is implied"
        else:
            diff = row["actual"] - row["counterfactual"]
            row["gap"] = round(diff, 2)
            better = (diff < 0) if row["lowerIsBetter"] else (diff > 0)
            row["direction"] = "better than the model" if better else (
                "worse than the model" if diff else "level with the model")
        rows.append(row)

    for k in facts:
        if k not in (base.get("metrics") or {}) and not k.startswith("_"):
            excluded.append({"metric": k, "why": "measured today but never baselined — excluded "
                                                 "rather than assumed flat at engagement start"})

    compared = [r for r in rows if r["gap"] is not None]
    return {
        "client": client,
        "available": True,
        "isModel": True,
        "modelLabel": ("MODEL, NOT A MEASUREMENT. Nobody observed the business that didn't happen. "
                       "These figures are the client's own baseline carried forward under the "
                       "stated assumptions below, compared to their own actuals."),
        "capturedOn": captured,
        "monthsElapsed": months,
        "stale": months > STALE_MONTHS,
        "staleNote": (f"baseline is {months} months old — the further this projects, the more it "
                      f"is arithmetic and the less it is evidence") if months > STALE_MONTHS else None,
        "rows": rows,
        "compared": len(compared),
        "excluded": excluded,
        "factsError": ferr,
        "flatCount": sum(1 for r in rows if not r["trendStated"]),
        "exampleOnly": bool(base.get("_exampleOnly")),
        "note": ("Every metric states the assumption it was projected under. A metric measured "
                 "today with no baseline is excluded and named — never assumed flat at start, "
                 "which would invent a gap. A baseline metric with no stated trend is held flat "
                 "and says so."),
    }


def build():
    out = []
    for name in sorted(os.listdir(CLIENTS)) if os.path.isdir(CLIENTS) else []:
        if not os.path.isdir(os.path.join(CLIENTS, name)) or name == "_yourco-template":
            continue
        r = build_client(name)
        if r.get("available"):
            out.append(r)
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "clients": out,
        "zeroState": ("No client has a baseline.json, so no counterfactual exists. The baseline is "
                      "captured at discovery and cannot be reconstructed afterwards — which makes "
                      "capturing it a go-live task, not a renewal-time one.") if not out else None,
        "isModel": True,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", default="_yourco-template")
    a = ap.parse_args()
    d = build_client(a.client)
    if not d.get("available"):
        raise SystemExit(f"{a.client}: {d['reason']}\n  {d.get('meaning','')}")
    print(f"COUNTERFACTUAL TWIN — {d['client']}"
          + ("   [EXAMPLE DATA]" if d["exampleOnly"] else ""))
    print("  " + d["modelLabel"])
    print(f"  baseline captured {d['capturedOn']} · {d['monthsElapsed']} months elapsed"
          + (f" · {d['staleNote']}" if d["stale"] else ""))
    print()
    for r in d["rows"]:
        act = "not measured" if r["actual"] is None else str(r["actual"])
        print(f"  {r['label']}")
        print(f"    baseline {r['baseline']}  ->  without the OS ~{r['counterfactual']}  "
              f"|  actual {act}"
              + (f"  ({r['direction']}, gap {r['gap']:+})" if r["gap"] is not None else ""))
        print(f"    assumption: {r['assumption']}")
    if d["excluded"]:
        print(f"\n  excluded ({len(d['excluded'])}):")
        for x in d["excluded"]:
            print(f"    · {x['metric']} — {x['why']}")
    print(f"\n  {d['flatCount']} metric(s) held flat for want of a stated trend.")
