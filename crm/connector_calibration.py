#!/usr/bin/env python3
"""yourco — the connector's calibration: how good their judgment about their own referrals actually is.

At referral time a connector says how likely they think this one is to become a client. When the
referral resolves, that prediction is scored. Over enough of them, the console can tell them
something nobody has ever told a referrer: **which of your instincts are right.**

Two payoffs, and the second is the one that matters commercially:

1. **For the connector** — real self-knowledge. "You said 80% on six of these and two closed" is more
   useful, and more respectful, than a leaderboard position.
2. **For yourco** — a routing signal that **cannot be gamed by volume.** A per-contact bounty rewards
   submitting more; calibration rewards being *right*, and you cannot improve a Brier score by
   submitting more names. A well-calibrated connector's "this one is hot" earns queue priority —
   earned on measured accuracy, never on how loud they are.

Scoring is the **Brier score** (mean squared error of a probability forecast): 0 is perfect, 0.25 is
what you get by saying 50% every time, 1.0 is confidently wrong every time. It is used instead of a
hit rate because a hit rate cannot tell the difference between someone who says 90% and is right 90%
of the time and someone who says 55% and is right 90% of the time — the second is *underconfident*,
which is a different problem with a different fix.

**The refusal that matters.** Below `MIN_RESOLVED` predictions there is NO score. Not a provisional
one, not a grey one — none, with the count still needed. A calibration number off three data points
is noise presented as a verdict, and this one is attached to a person's sense of their own judgment
and to how yourco prioritises their work.

Storage: `meta.connectorPredictions` — a flat append-style list, one record per prediction:
  {id, connector, subject (companyId or submissionId), subjectKind, confidence 0–100, at, by,
   resolved: bool, outcome: "client"|"dead"|None, resolvedAt}
Predictions are **never edited after the fact** — a connector may not revise a call once they have
seen how it is going, because the whole instrument is worthless if they can.

Usage:
  python3 crm/connector_calibration.py                # every connector
  python3 crm/connector_calibration.py "Sample Contact"
"""
import os, sys, json, uuid, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
CRM = os.path.join(DATA_DIR, "data.json")
sys.path.insert(0, HERE)
import connector_ladder as ladder

META_KEY = "connectorPredictions"
MIN_RESOLVED = 5          # below this: no score at all, and say how many are still needed
BANDS = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 101)]   # for the "when you say X, Y happens" table
# Priority multiplier a well-calibrated connector's high-confidence referral earns in yourco's queue.
# Deliberately small: this orders a queue, it never changes anyone's money.
PRIORITY_MAX = 2.0


class PredictionError(ValueError):
    """A prediction that must not be recorded — raised BEFORE anything is written."""


def _rows(d, connector=None):
    rows = ((d.get("meta") or {}).get(META_KEY) or [])
    if connector is not None:
        rows = [r for r in rows if (r.get("connector") or "") == connector]
    return sorted(rows, key=lambda r: r.get("at") or "")


def predict(actor, subject, confidence, d=None, commit=True, log=None, subject_kind="referral"):
    """Record one prediction. Refuses a second prediction on the same subject by the same connector.

    That refusal is the instrument: a forecast you can revise once you have seen the outcome drift is
    not a forecast. Corrections go the same way the attribution log handles them — a new record that
    cites the old one — never an edit in place.
    """
    import connector_writes as writes
    actor = (actor or "").strip()
    d0 = d if d is not None else json.load(open(CRM))
    state = ladder.compute(d0)
    if actor not in state:
        raise PredictionError(f"{actor or 'You'} is not a connector in yourco's records.")
    try:
        conf = float(confidence)
    except (TypeError, ValueError):
        raise PredictionError("Confidence must be a number between 0 and 100.")
    if not (0 <= conf <= 100):
        raise PredictionError("Confidence must be between 0 and 100.")
    subject = (str(subject or "")).strip()
    if not subject:
        raise PredictionError("A prediction has to be about something — name the referral.")
    if any(r.get("subject") == subject for r in _rows(d0, actor)):
        raise PredictionError("You already called this one. A prediction you can revise after the "
                              "fact isn't a prediction — that is the whole point of the score.")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    rec = {"id": f"pred-{now.replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:6]}",
           "connector": actor, "subject": subject, "subjectKind": subject_kind,
           "confidence": conf, "at": now, "by": actor, "resolved": False, "outcome": None}

    def apply(dd):
        dd.setdefault("meta", {}).setdefault(META_KEY, []).append(rec)
        return rec

    out = writes._locked_update(apply) if (commit and d is None) else apply(d0)
    emit = log if log is not None else ladder.log_event
    emit("prediction.made", connector=actor, by=actor, subject=subject, confidence=conf,
         note=f"{actor} called {subject} at {conf:.0f}%")
    return out


def resolve(subject, outcome, d=None, commit=True, log=None):
    """Mark every open prediction on `subject` resolved. yourco's act, from the CRM — never the connector's."""
    import connector_writes as writes
    if outcome not in ("client", "dead"):
        raise PredictionError("Outcome must be 'client' or 'dead'.")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    touched = []

    def apply(dd):
        for r in dd.setdefault("meta", {}).setdefault(META_KEY, []):
            if r.get("subject") == subject and not r.get("resolved"):
                r.update(resolved=True, outcome=outcome, resolvedAt=now)
                touched.append(r)
        return touched

    out = writes._locked_update(apply) if (commit and d is None) else apply(d if d is not None else json.load(open(CRM)))
    emit = log if log is not None else ladder.log_event
    for r in touched:
        emit("prediction.resolved", connector=r["connector"], by="yourco", subject=subject,
             confidence=r["confidence"], outcome=outcome,
             note=f"{subject} resolved {outcome} — called at {r['confidence']:.0f}%")
    return out


def compute(name, d=None):
    """One connector's calibration. `brier` is None until MIN_RESOLVED — None means "we won't say"."""
    d = d if d is not None else json.load(open(CRM))
    rows = _rows(d, name)
    done = [r for r in rows if r.get("resolved")]
    open_ = [r for r in rows if not r.get("resolved")]

    bands = []
    for lo, hi in BANDS:
        inb = [r for r in done if lo <= float(r["confidence"]) < hi]
        hits = sum(1 for r in inb if r.get("outcome") == "client")
        bands.append({"lo": lo, "hi": min(hi, 100), "n": len(inb), "hits": hits,
                      "said": (sum(float(r["confidence"]) for r in inb) / len(inb)) if inb else None,
                      "actual": (100.0 * hits / len(inb)) if inb else None})

    if len(done) < MIN_RESOLVED:
        need = MIN_RESOLVED - len(done)
        return {"connector": name, "resolved": len(done), "open": len(open_), "bands": bands,
                "brier": None, "skill": None, "bias": None, "priority": 1.0, "enough": False,
                "why": (f"{len(done)} of your referrals have resolved. A calibration score needs "
                        f"{MIN_RESOLVED} — {need} more to go. Until then there is no score at all, "
                        f"because a number off this few would be noise dressed up as a verdict.")}

    brier = sum((float(r["confidence"]) / 100.0 - (1.0 if r.get("outcome") == "client" else 0.0)) ** 2
                for r in done) / len(done)
    base = sum(1 for r in done if r.get("outcome") == "client") / len(done)
    # Skill vs. always predicting the base rate. >0 means their judgment beats "everyone is average".
    ref = sum((base - (1.0 if r.get("outcome") == "client" else 0.0)) ** 2 for r in done) / len(done)
    skill = None if ref == 0 else round(1 - (brier / ref), 3)
    mean_said = sum(float(r["confidence"]) for r in done) / len(done) / 100.0
    bias = round((mean_said - base) * 100, 1)          # + = overconfident, − = underconfident

    priority = 1.0
    if skill is not None:
        priority = round(max(1.0, min(PRIORITY_MAX, 1.0 + max(0.0, skill))), 2)

    return {"connector": name, "resolved": len(done), "open": len(open_), "bands": bands,
            "brier": round(brier, 4), "skill": skill, "bias": bias, "baseRate": round(base * 100, 1),
            "priority": priority, "enough": True,
            "why": (f"Scored on {len(done)} resolved referrals. "
                    + ("You are well calibrated." if abs(bias) < 8 else
                       (f"You run about {abs(bias):.0f} points "
                        + ("optimistic" if bias > 0 else "pessimistic") + " on average.")))}


def main():
    d = json.load(open(CRM))
    names = ([sys.argv[1]] if len(sys.argv) > 1 else sorted(ladder.compute(d)))
    any_rows = False
    for n in names:
        r = compute(n, d)
        if not r["resolved"] and not r["open"]:
            continue
        any_rows = True
        print(f"\n# {n}")
        print(f"  {r['why']}")
        if r["enough"]:
            print(f"  Brier {r['brier']} · skill {r['skill']} · bias {r['bias']:+} pts · "
                  f"queue priority ×{r['priority']}")
            for b in r["bands"]:
                if b["n"]:
                    print(f"    said {b['lo']}–{b['hi']}%: {b['hits']}/{b['n']} became clients "
                          f"(actual {b['actual']:.0f}%)")
    if not any_rows:
        print("No connector predictions recorded yet (program pre-launch).")


if __name__ == "__main__":
    main()
