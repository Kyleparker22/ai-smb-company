#!/usr/bin/env python3
"""The calibration wager — bet the owner on their own self-knowledge, then settle it.

A proposal asks a prospect to believe a claim about their business. This asks them
to make ten claims about their own business, in writing, and then measures them.
Ninety days later the conversation is not "did you like the pitch" — it is "here is
where you were wrong about your own company, by how much, and in which direction."

That is a bet we can offer honestly while pre-revenue, because the thing being
tested is them, not us. It costs one conversation, it creates a dated checkpoint the
deal cannot drift past, and the answer is interesting whether we win or lose.

`crm/calibration.py` measures OUR forecasting bias. This measures THEIRS. Same
discipline, opposite subject.

TWO REFUSALS, both load-bearing:
  * A question we never instrumented is reported UNMEASURED, never as wrong. If we
    failed to capture the actual, that is our failure, and scoring it against them
    would be the exact dishonesty this instrument is built to punish.
  * No settlement before the settle date. An early read on a 90-day question is a
    guess wearing a scoreboard.

Run:
    python3 crm/wager.py --questions                       # the standard ten
    python3 crm/wager.py --open <dealId> --answers a.json  # capture their predictions
    python3 crm/wager.py --measure <wagerId> --actuals b.json
    python3 crm/wager.py --settle <wagerId>
    python3 crm/wager.py --list
"""
import json, os, sys, argparse, datetime, statistics, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
DATA = os.path.join(DATA_DIR, "data.json")
STORE = os.path.join(DATA_DIR, "_wagers.jsonl")
TODAY = datetime.date.today()

WINDOW_DAYS = 90
DEFAULT_TOL = 20.0        # % relative error inside which a prediction counts as "held up"

# The ten. Chosen because each is (a) something an owner is certain about, (b) cheap
# for an operated OS to measure once it is running, and (c) reliably wrong in a
# direction that costs money. `betterIsHigher` is what makes "optimistic" computable
# rather than rhetorical.
QUESTIONS = [
    {"key": "missed_calls", "unit": "per 10 inbound", "betterIsHigher": False,
     "q": "Out of every 10 inbound calls, how many go unanswered or to voicemail?"},
    {"key": "quote_hours", "unit": "hours", "betterIsHigher": False,
     "q": "From request to quote in the customer's hands — what's your typical turnaround, in hours?"},
    {"key": "quote_close_rate", "unit": "%", "betterIsHigher": True,
     "q": "What percentage of the quotes you send turn into paid work?"},
    {"key": "followup_rate", "unit": "%", "betterIsHigher": True,
     "q": "What percentage of unaccepted quotes get followed up more than once?"},
    {"key": "ar_days", "unit": "days", "betterIsHigher": False,
     "q": "From invoice sent to money in the account — how many days, on average?"},
    {"key": "repeat_revenue", "unit": "%", "betterIsHigher": True,
     "q": "What percentage of this year's revenue came from customers you'd served before?"},
    {"key": "top_source_share", "unit": "%", "betterIsHigher": True,
     "q": "Your single biggest source of new work — what share of leads does it actually bring?"},
    {"key": "owner_admin_hours", "unit": "hours/week", "betterIsHigher": False,
     "q": "How many hours a week do you personally spend on admin — not selling, not delivering?"},
    {"key": "margin_spread", "unit": "points", "betterIsHigher": False,
     "q": "Between your best and worst job last quarter, how many points of margin separate them?"},
    {"key": "first_responder", "unit": "%", "betterIsHigher": True,
     "q": "When a customer contacts several businesses, how often are you the first to respond?"},
]
BY_KEY = {q["key"]: q for q in QUESTIONS}


def _append(rec):
    with open(STORE, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _load():
    """Wagers with measurements and corrections folded in. Append-only store."""
    if not os.path.exists(STORE):
        return {}
    wagers = {}
    for line in open(STORE):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        wid = r.get("wagerId")
        if r.get("event") == "wager.opened":
            wagers[wid] = dict(r, actuals={})
        elif wid in wagers and r.get("event") in ("wager.measured", "wager.correction"):
            wagers[wid]["actuals"].update(r.get("actuals") or {})
    return wagers


def _company(deal_id):
    if not os.path.exists(DATA):
        return deal_id
    data = json.load(open(DATA))
    cos = {c["id"]: c.get("name") for c in data.get("companies", []) or []}
    for d in data.get("deals", []) or []:
        if d.get("id") == deal_id:
            return cos.get(d.get("companyId")) or d.get("name") or deal_id
    return None


def open_wager(deal_id, answers, window=WINDOW_DAYS, tol=DEFAULT_TOL):
    name = _company(deal_id)
    if name is None:
        return None, f"no deal {deal_id!r} in the CRM — open the wager against a real deal"
    unknown = [k for k in answers if k not in BY_KEY]
    if unknown:
        return None, f"unknown question key(s): {', '.join(unknown)}"
    if not answers:
        return None, "no predictions given — the wager is the predictions"
    wid = "w" + hashlib.sha1(f"{deal_id}{TODAY}{sorted(answers.items())}".encode()).hexdigest()[:8]
    rec = {
        "event": "wager.opened", "wagerId": wid, "dealId": deal_id, "company": name,
        "opened": TODAY.isoformat(),
        "settles": (TODAY + datetime.timedelta(days=window)).isoformat(),
        "tolerancePct": tol,
        "predictions": {k: float(v) for k, v in answers.items()},
    }
    _append(rec)
    return rec, None


def measure(wid, actuals):
    w = _load().get(wid)
    if not w:
        return None, f"no wager {wid!r}"
    unknown = [k for k in actuals if k not in w["predictions"]]
    if unknown:
        return None, f"actuals given for question(s) never predicted: {', '.join(unknown)}"
    rec = {"event": "wager.measured", "wagerId": wid, "ts": TODAY.isoformat(),
           "actuals": {k: float(v) for k, v in actuals.items()}}
    _append(rec)
    return rec, None


def settle(wid, force=False):
    w = _load().get(wid)
    if not w:
        return None, f"no wager {wid!r}"
    settles = datetime.date.fromisoformat(w["settles"])
    if TODAY < settles and not force:
        return None, (f"not due until {w['settles']} ({(settles - TODAY).days} days out). "
                      f"An early read on a {WINDOW_DAYS}-day question is a guess wearing a scoreboard.")

    scored, unmeasured = [], []
    for key, pred in w["predictions"].items():
        q = BY_KEY[key]
        if key not in w["actuals"]:
            unmeasured.append({"key": key, "q": q["q"], "predicted": pred})
            continue
        act = w["actuals"][key]
        denom = abs(act) if act else (abs(pred) or 1.0)
        err_pct = (pred - act) / denom * 100.0
        # Optimistic = they believed the business was doing better than it was.
        optimistic = (pred > act) if q["betterIsHigher"] else (pred < act)
        scored.append({
            "key": key, "q": q["q"], "unit": q["unit"], "predicted": pred, "actual": act,
            "errorPct": round(err_pct, 1), "absErrorPct": round(abs(err_pct), 1),
            "held": abs(err_pct) <= w["tolerancePct"],
            "direction": "optimistic" if optimistic else "pessimistic",
        })

    held = [s for s in scored if s["held"]]
    opt = [s for s in scored if s["direction"] == "optimistic" and not s["held"]]
    pes = [s for s in scored if s["direction"] == "pessimistic" and not s["held"]]
    lean = ("optimistic" if len(opt) > len(pes) else
            "pessimistic" if len(pes) > len(opt) else "no systematic direction")
    worst = max(scored, key=lambda s: s["absErrorPct"]) if scored else None

    return {
        "wagerId": wid, "company": w["company"], "opened": w["opened"], "settles": w["settles"],
        "tolerancePct": w["tolerancePct"], "scored": scored, "unmeasured": unmeasured,
        "nPredicted": len(w["predictions"]), "nScored": len(scored), "nHeld": len(held),
        "lean": lean, "nOptimistic": len(opt), "nPessimistic": len(pes),
        "medianAbsErrorPct": round(statistics.median([s["absErrorPct"] for s in scored]), 1)
        if scored else None,
        "worst": worst,
        "honesty": (
            f"{len(scored)} of {len(w['predictions'])} predictions could be measured. "
            + (f"The other {len(unmeasured)} "
               f"{'is' if len(unmeasured) == 1 else 'are'} reported unmeasured, not wrong — we did not "
               f"instrument {'it' if len(unmeasured) == 1 else 'them'}, which is our failure and not "
               f"evidence about you. " if unmeasured else "")
            + "Every figure above is a measurement against your own records over the window, not a "
              "benchmark against anyone else's business."),
    }, None


def main():
    ap = argparse.ArgumentParser(description="Open, measure and settle a calibration wager.")
    ap.add_argument("--questions", action="store_true", help="print the standard ten")
    ap.add_argument("--open", metavar="DEALID")
    ap.add_argument("--answers", metavar="JSON", help='file or inline JSON: {"missed_calls": 1, ...}')
    ap.add_argument("--measure", metavar="WAGERID")
    ap.add_argument("--actuals", metavar="JSON")
    ap.add_argument("--settle", metavar="WAGERID")
    ap.add_argument("--force", action="store_true", help="settle before the date (marked in output)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    def _read(v):
        if not v:
            return {}
        return json.load(open(v)) if os.path.exists(v) else json.loads(v)

    if a.questions:
        print(f"The calibration wager — {len(QUESTIONS)} questions\n")
        for i, q in enumerate(QUESTIONS, 1):
            print(f"  {i:>2}. [{q['key']}] {q['q']}")
            print(f"      answer in {q['unit']} · "
                  f"{'higher is better' if q['betterIsHigher'] else 'lower is better'}")
        print("\n  Captured in their words, in writing, before anything is instrumented.")
        return 0

    if a.list:
        ws = _load()
        if not ws:
            print("no wagers open"); return 0
        for wid, w in sorted(ws.items(), key=lambda kv: kv[1]["opened"]):
            due = datetime.date.fromisoformat(w["settles"])
            print(f"  {wid}  {w['company'][:28]:<28} opened {w['opened']}  settles {w['settles']}"
                  f"  {len(w['actuals'])}/{len(w['predictions'])} measured"
                  f"  {'DUE' if TODAY >= due else f'{(due-TODAY).days}d'}")
        return 0

    if a.open:
        rec, err = open_wager(a.open, _read(a.answers))
        if err:
            print("refused: " + err, file=sys.stderr); return 2
        print(f"opened {rec['wagerId']} — {rec['company']}, {len(rec['predictions'])} predictions, "
              f"settles {rec['settles']}")
        return 0

    if a.measure:
        rec, err = measure(a.measure, _read(a.actuals))
        if err:
            print("refused: " + err, file=sys.stderr); return 2
        print(f"recorded {len(rec['actuals'])} actual(s) for {a.measure}")
        return 0

    if a.settle:
        r, err = settle(a.settle, a.force)
        if err:
            print("refused: " + err, file=sys.stderr); return 2
        if a.json:
            print(json.dumps(r, indent=2)); return 0
        print(f"Calibration wager — {r['company']}")
        print(f"opened {r['opened']} · settled {TODAY}"
              + ("  [FORCED — before the settle date]" if a.force and TODAY <
                 datetime.date.fromisoformat(r['settles']) else "") + "\n")
        print(f"  {r['nHeld']} of {r['nScored']} predictions held within {r['tolerancePct']:g}%.")
        if r["lean"] != "no systematic direction":
            print(f"  Where you were off, you leaned {r['lean'].upper()} "
                  f"({r['nOptimistic']} optimistic · {r['nPessimistic']} pessimistic).")
        if r["medianAbsErrorPct"] is not None:
            print(f"  Median error: {r['medianAbsErrorPct']:g}%.")
        print()
        for s in sorted(r["scored"], key=lambda x: -x["absErrorPct"]):
            flag = "held " if s["held"] else f"{s['direction'][:4]} "
            print(f"  [{flag}] {s['q']}")
            print(f"           you said {s['predicted']:g} {s['unit']} · actual {s['actual']:g} "
                  f"({s['errorPct']:+.1f}%)")
        for u in r["unmeasured"]:
            print(f"  [unmea] {u['q']}")
            print(f"           you said {u['predicted']:g} · WE DID NOT MEASURE THIS — not scored")
        print(f"\n  {r['honesty']}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
