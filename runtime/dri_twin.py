#!/usr/bin/env python3
"""The DRI twin — a scoreboard for how well the OS predicts the Founder's own calls.

THE POINT.  The autonomy matrix says every agent's routine work trends toward full autonomy
on eval evidence, and the founder's time trends to zero. That second half has never been
measurable. This measures it: before the Founder decides an escalation, the twin records what it
thinks he will decide and how sure it is. When he decides, the call is recorded. Over time
the scoreboard says — per class of decision, on evidence — how much of the Founder's judgment the
OS has actually learned.

WHY IT STARTS EMPTY, AND MUST.  A prediction only counts if it was recorded BEFORE the
outcome. Backfilling predictions against decisions already in `decisions/` would produce a
flattering scoreboard out of hindsight — the exact fabricated-completeness failure the loop
contract calls the cardinal sin. So the ledger opens at zero, the same way Kolby opened the
autonomy streak ledger at zero rather than reconstructing prior clean runs.

WHAT CAN NEVER BE EARNED.  Mirrors `runtime/autonomy-matrix.md` §"What stays gated regardless
of evidence". Some classes stay the Founder's no matter how good the scoreboard gets — see
`NEVER_EARNS`. A twin that predicts a legal-gate call correctly 50 times in a row has earned
the right to *prepare* the call, never to make it. Prediction accuracy is not authority.

  loops/_twin/predictions.jsonl   kind=prediction  the call, before the fact
                                  kind=outcome     what the Founder actually decided

CLI
  python3 runtime/dri_twin.py --queue                       # open decision points awaiting a prediction
  python3 runtime/dri_twin.py --predict <itemId> --class pricing --says "..." --p 0.7
                              [--because "decisions/2026-…md; …"] [--question "..."]
  python3 runtime/dri_twin.py --resolve <seq> --actual "..." [--hit|--miss] [--note ...]
  python3 runtime/dri_twin.py --score
"""
import os, sys, re, json, hashlib, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ledger import Ledger  # noqa: E402

PRED = Ledger("loops/_twin/predictions.jsonl")

# Decision classes — how the Founder's calls actually cluster in decisions/ and the open-loops queue.
CLASSES = ["pricing", "scope", "positioning", "stack", "roster", "legal-gate", "spend",
           "client-commitment", "publish-send", "process"]

# Classes where a perfect record still earns nothing. Not a threshold — a category.
NEVER_EARNS = {
    "legal-gate": "counsel-gated by definition; an agent cannot accept legal risk for the company",
    "publish-send": "the Founder sends; agents draft (CLAUDE.md). Irreversible and outward-facing.",
    "spend": "money leaving the company is the founder's call regardless of prediction accuracy",
    "client-commitment": "a promise to a client creates an obligation the OS cannot be liable for",
}

# Promotion thresholds for the classes that CAN earn — same shape as the autonomy streak rule.
EARN_MIN_RESOLVED = 10
EARN_MIN_HITRATE = 0.90
EARN_MAX_BRIER = 0.10
EARN_MIN_STREAK = 8

CLASS_HINTS = [
    ("pricing", r"\b(pric|rate|retainer|discount|quote|fee|commission|%)"),
    ("legal-gate", r"\b(counsel|legal|attorney|contract|agreement|gate|complian|classif)"),
    ("spend", r"\b(buy|purchase|subscri|budget|spend|invoice|pay|cost)"),
    ("publish-send", r"\b(send|publish|post|launch|announce|email|outreach|deploy)"),
    ("client-commitment", r"\b(client|Client Owner|southern|proposal|deliver|deadline|promise)"),
    ("roster", r"\b(agent|hire|roster|activate|owner|assign)"),
    ("stack", r"\b(tool|stack|api|vendor|platform|migrat|build vs|adopt)"),
    ("positioning", r"\b(position|messag|brand|copy|site|narrative|offer)"),
    ("scope", r"\b(scope|cut|park|defer|priorit|sequence)"),
]


def item_id(text):
    """Stable id for an open decision point, so a prediction binds to the same item across runs."""
    norm = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", (text or "").lower())).strip()
    return hashlib.sha1(norm.encode()).hexdigest()[:10]


def suggest_class(text):
    """A SUGGESTION only — the predictor sets the real class. Keyword matching is not judgment."""
    t = (text or "").lower()
    for cls, rx in CLASS_HINTS:
        if re.search(rx, t):
            return cls
    return "process"


def queue():
    """Open decision points genuinely waiting on the Founder, from the sources that already track
    them — Jim's open-loops queue and the Board's needs-you lane. Nothing invented here."""
    items, seen = [], set()

    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    try:
        import refresh
        nk = refresh.derive().get("needsFounder") or {}
        for it in nk.get("items", []):
            t = it.get("name") or ""
            if not t or item_id(t) in seen:
                continue
            seen.add(item_id(t))
            items.append({"id": item_id(t), "text": t[:200], "source": "open-loops queue",
                          "age": it.get("age"), "sev": it.get("sev"),
                          "suggestedClass": suggest_class(t)})
    except Exception:
        pass

    try:
        import board
        for it in (board.build().get("items") or []):
            if it.get("state") != "needs-you":
                continue
            t = it.get("title") or it.get("text") or ""
            if not t or item_id(t) in seen:
                continue
            seen.add(item_id(t))
            items.append({"id": item_id(t), "text": t[:200], "source": "The Board · needs-you",
                          "age": it.get("age"), "sev": it.get("severity"),
                          "suggestedClass": suggest_class(t)})
    except Exception:
        pass

    predicted = {e.get("item") for e in PRED.project()["events"] if e.get("kind") == "prediction"}
    for it in items:
        it["hasPrediction"] = it["id"] in predicted
    return items


def predict(item, cls, says, p, because=None, question=None, by="twin"):
    if cls not in CLASSES:
        raise SystemExit(f"--class must be one of: {', '.join(CLASSES)}")
    try:
        p = float(p)
    except (TypeError, ValueError):
        raise SystemExit("--p must be a probability between 0 and 1")
    if not 0.0 <= p <= 1.0:
        raise SystemExit("--p must be between 0 and 1")
    if not says:
        raise SystemExit("--says is required: what do you predict the Founder will decide?")
    return PRED.append("prediction", item=item, cls=cls, says=says, p=p,
                       because=because, question=question, by=by,
                       on=datetime.date.today().isoformat())


def resolve(seq, actual, hit=None, note=None):
    preds = {e["seq"]: e for e in PRED.project()["events"] if e.get("kind") == "prediction"}
    if seq not in preds:
        raise SystemExit(f"no prediction with seq {seq}")
    already = {e.get("prediction") for e in PRED.project()["events"] if e.get("kind") == "outcome"}
    if seq in already:
        raise SystemExit(f"prediction {seq} is already resolved — append a correction instead "
                         f"(ledger.py: corrects=<seq>)")
    if hit is None:
        raise SystemExit("say whether the twin was right: --hit or --miss")
    return PRED.append("outcome", prediction=seq, actual=actual, hit=bool(hit), note=note,
                       decidedBy="the Founder", on=datetime.date.today().isoformat())


def _score_cli():
    sys.path.insert(0, os.path.join(ROOT, "dashboard"))
    import twin
    d = twin.build()
    print(f"DRI TWIN — {d['resolved']} resolved of {d['total']} predictions")
    if d["zeroState"]:
        print("  " + d["zeroState"])
    o = d["overall"]
    print("  overall: " + (o["refusal"] or f"{o['hitRate']}% hit · Brier {o['brier']}"))
    for c in d["byClass"]:
        earn = c["earned"]["verdict"]
        print(f"  {c['cls']:<18} n={c['n']:<3} {c['hitRate'] if c['hitRate'] is not None else '—'}"
              f"  streak {c['streak']}  -> {earn}")
    q = d["queue"]
    print(f"\n  queue: {len(q)} open decision point(s); "
          f"{sum(1 for i in q if not i['hasPrediction'])} without a prediction")


def main():
    ap = argparse.ArgumentParser(description="yourco DRI twin")
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--predict"); ap.add_argument("--class", dest="cls")
    ap.add_argument("--says"); ap.add_argument("--p"); ap.add_argument("--because")
    ap.add_argument("--question"); ap.add_argument("--by", default="twin")
    ap.add_argument("--resolve", type=int); ap.add_argument("--actual")
    ap.add_argument("--hit", action="store_true"); ap.add_argument("--miss", action="store_true")
    ap.add_argument("--note"); ap.add_argument("--score", action="store_true")
    a = ap.parse_args()

    if a.queue:
        items = queue()
        if not items:
            print("no open decision points found in the open-loops queue or the Board's "
                  "needs-you lane")
        for i in items:
            mark = "✓predicted" if i["hasPrediction"] else "          "
            print(f"  {i['id']}  {mark}  [{i['suggestedClass']}] {i['text'][:88]}")
        print(f"\n{len(items)} item(s). Suggested classes are keyword hints, not judgment — "
              f"set the real one with --class.")
    elif a.predict:
        ev = predict(a.predict, a.cls or "", a.says, a.p, a.because, a.question, a.by)
        print(f"prediction #{ev['seq']} recorded: [{ev['cls']}] P={ev['p']} — \"{ev['says'][:70]}\"")
        print(f"  resolve when the Founder calls it:  --resolve {ev['seq']} --actual \"...\" --hit|--miss")
    elif a.resolve:
        if a.hit == a.miss:
            raise SystemExit("pass exactly one of --hit or --miss")
        ev = resolve(a.resolve, a.actual or "", hit=a.hit, note=a.note)
        print(f"resolved #{a.resolve}: twin was {'RIGHT' if ev['hit'] else 'WRONG'}")
    elif a.score:
        _score_cli()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
