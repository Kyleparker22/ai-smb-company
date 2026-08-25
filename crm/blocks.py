#!/usr/bin/env python3
"""Agent blocks — the CRM's capabilities, packaged as named, composable units.

Attio's June 2026 Workflows shipped prebuilt agent actions: Scoring, Routing, Enrichment,
Briefing, Follow-Up, Win/Loss, Churn Risk, Expansion. yourco already *has* every one of
those capabilities — they are simply scattered across a dozen modules with a dozen different
call shapes, each one something you have to already know about to use. Their packaging is
better than ours, and packaging is not cosmetic: a capability nobody can find or compose is,
operationally, a capability you do not have.

So this is one registry with one interface. Every block declares:
  · what it answers, in a sentence
  · which module actually computes it (never a fork — blocks DELEGATE, they never re-derive)
  · what it needs before it can run, and what it does when that is missing
  · its autonomy rung (processes/autonomy-matrix.md) and its owning agent

THE DESIGN RULE THAT MATTERS: a block is a thin adapter over an existing module. The moment
a block computes something itself, the CRM has two answers to one question, which is the
failure this whole codebase is built to avoid (see the 2026-08-13 payout-math incident).
Every `run` below is a delegation.

A block that cannot answer honestly returns `{"status": "refused", "why": ..., "toEnable": ...}`
rather than a number. That refusal is the product: it is what makes the block safe to hand to
an agent running unattended.

Run:
    python3 crm/blocks.py                 # the registry
    python3 crm/blocks.py --run scoring
    python3 crm/blocks.py --run all --json
"""
import json, os, sys, datetime, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
DATA = os.path.join(DATA_DIR, "data.json")
TODAY = datetime.date.today()

# key -> (label, question it answers, module, callable, owner agent, rung, needs)
BLOCKS = {
    "scoring": {
        "label": "Scoring",
        "answers": "Which open deals are real, and which are one-sided?",
        "module": "adversarial", "fn": "compute", "owner": "David", "rung": "R2",
        "needs": "logged activities with an actor (us / them)",
    },
    "routing": {
        "label": "Routing",
        "answers": "Which single relationship, warmed this week, unlocks the most pipeline?",
        "module": "warmpath", "fn": "compute", "owner": "Reilly", "rung": "R1",
        "needs": "graph edges between people and companies",
    },
    "enrichment": {
        "label": "Enrichment",
        "answers": "What is missing on this company that a public source could fill?",
        "module": None, "fn": None, "owner": "David", "rung": "R2",
        "needs": "the server's /api/enrich endpoint (paid + rate-limited)",
        "note": ("Deliberately NOT delegated to a compute() — enrichment writes to records and "
                 "costs money per call, so it stays behind the server endpoint with its own "
                 "rate limit rather than becoming something a loop can fan out."),
    },
    "briefing": {
        "label": "Briefing",
        "answers": "What do I need to know before this meeting?",
        "module": "expansion", "fn": "compute", "owner": "David", "rung": "R3",
        "needs": "nothing — reads whatever exists",
    },
    "follow-up": {
        "label": "Follow-Up",
        "answers": "What is owed, to whom, and by when?",
        "module": "promises", "fn": "compute", "owner": "Kortney", "rung": "R1",
        "needs": "promises confirmed by a human (the extractor proposes, it never promotes)",
    },
    "win-loss": {
        "label": "Win/Loss",
        "answers": "Why did this deal actually die — inertia, a rival, or price?",
        "module": "autopsy", "fn": "compute", "owner": "David", "rung": "R2",
        "needs": "a filled mirror on the deal BEFORE it closed",
    },
    "churn-risk": {
        "label": "Churn Risk",
        "answers": "Which live clients are drifting, and what did we promise them?",
        "module": "expansion", "fn": "compute", "owner": "Kortney", "rung": "R2",
        "needs": "a live client (there are none yet)",
    },
    "expansion": {
        "label": "Expansion",
        "answers": "Who is ready for the next module, on evidence rather than hope?",
        "module": "expansion", "fn": "compute", "owner": "Janice", "rung": "R1",
        "needs": "measured outcomes in clients/<slug>/outcomes.jsonl",
    },
    # ---- yourco-specific blocks, beyond Attio's set -----------------------------------
    "pricing": {
        "label": "Pricing power",
        "answers": "Is the number right? Who accepted without pushback?",
        "module": "pricing_power", "fn": "compute", "owner": "Polo", "rung": "R1",
        "needs": "price events logged on deals",
    },
    "capacity": {
        "label": "Capacity",
        "answers": "Could we actually deliver what we are trying to sell?",
        "module": "capacity", "fn": "compute", "owner": "the Founder", "rung": "R0",
        "needs": "predicted close dates, and a stated concurrent-build ceiling",
    },
    "decline": {
        "label": "Decline",
        "answers": "Which deals should we walk away from, and on what evidence?",
        "module": "antipipeline", "fn": "compute", "owner": "the Founder", "rung": "R0",
        "needs": "nothing — argues from whatever is recorded",
        "note": "R0 by design: walking away from revenue is never delegated.",
    },
    "counterparty": {
        "label": "Counterparty",
        "answers": "What would the buyer see, and what have they disputed?",
        "module": "counterparty", "fn": "disputes", "owner": "the Founder", "rung": "R1",
        "needs": "a record actually shared with a buyer",
        "note": "Renders only. the Founder sends; agents draft.",
    },
    "ghost": {
        "label": "Ghost",
        "answers": "Where would each deal be at our own median pace?",
        "module": "ghost", "fn": "compute", "owner": "David", "rung": "R3",
        "needs": "git history of crm/data.json",
    },
    "mirror": {
        "label": "Mirror",
        "answers": "Where are we ahead of the buyer's own ladder?",
        "module": "mirror", "fn": "compute", "owner": "David", "rung": "R2",
        "needs": "a human filling in the buyer's steps",
    },
    "calibration": {
        "label": "Calibration",
        "answers": "How wrong is the Founder usually, and in which direction?",
        "module": "calibration", "fn": "compute", "owner": "Kolby", "rung": "R3",
        "needs": "resolved predictions (5 per segment)",
    },
    "conversation": {
        "label": "Conversation",
        "answers": "What did they actually say on the call, and what should it change?",
        "module": "conversation", "fn": "compute", "owner": "David", "rung": "R1",
        "needs": "a transcript fed through --scan (Granola is connected; nothing reads it yet)",
        "note": "Proposes candidates with the exact quote. A human confirms; nothing auto-writes.",
    },
    "enrichment-coverage": {
        "label": "Enrichment coverage",
        "answers": "Which fields are missing across the book, and what would it cost to fill them?",
        "module": "enrich_waterfall", "fn": "compute", "owner": "David", "rung": "R2",
        "needs": "nothing to read; the paid provider rungs need wiring before they can fill",
    },
    "decisions": {
        "label": "Decision P&L",
        "answers": "What followed each decision we logged?",
        "module": "decision_pl", "fn": "compute", "owner": "Brett", "rung": "R1",
        "needs": "board history either side of the decision date",
    },
}


def run_block(key, data=None):
    """Delegate. A block NEVER computes — it calls the module that owns the answer."""
    b = BLOCKS.get(key)
    if not b:
        return {"status": "unknown", "why": f"no block '{key}'", "available": sorted(BLOCKS)}
    if not b.get("module"):
        return {"status": "refused", "block": key, "why": b.get("note") or "not a compute block",
                "toEnable": b["needs"]}
    try:
        mod = importlib.import_module(b["module"])
        fn = getattr(mod, b["fn"])
        # The modules were written independently and their signatures differ: some take a
        # required `data`, some default it, some read the file themselves. Inspect rather than
        # guess — the first cut caught the resulting TypeError and reported it as a REFUSAL,
        # which is far worse than crashing: a block that says "I cannot answer" when it simply
        # was not called correctly teaches an operator to distrust a working instrument.
        import inspect
        # Dispatch on the parameter NAME. Matching on position alone would hand the dataset to
        # decision_pl.compute(top=...) — a row limit — which fails deep inside with a type error
        # the block would then report as a REFUSAL. A block that says "I cannot answer" when it
        # was simply called wrong is worse than one that crashes: it teaches distrust of a
        # working instrument.
        sig = inspect.signature(fn)
        names = list(sig.parameters)
        wants_data = bool(names) and names[0] == "data"
        if wants_data:
            if data is None:
                with open(DATA) as f:
                    data = json.load(f)
            out = fn(data)
        else:
            out = fn()
        return {"status": "ok", "block": key, "label": b["label"], "owner": b["owner"],
                "rung": b["rung"], "result": out}
    except Exception as e:
        # A block failing must never take the caller down — it degrades to a refusal that
        # names the cause, which is what an unattended loop needs in order to keep going.
        return {"status": "refused", "block": key, "why": f"{type(e).__name__}: {e}",
                "toEnable": b["needs"]}


def registry():
    return {"generated": TODAY.isoformat(), "count": len(BLOCKS),
            "blocks": [{"key": k, **{x: y for x, y in v.items() if x != "fn"}}
                       for k, v in BLOCKS.items()]}


def main():
    if "--run" in sys.argv:
        which = sys.argv[sys.argv.index("--run") + 1]
        keys = sorted(BLOCKS) if which == "all" else [which]
        out = {k: run_block(k) for k in keys}
        if "--json" in sys.argv:
            print(json.dumps(out, indent=2, default=str)); return
        for k, r in out.items():
            b = BLOCKS.get(k, {})
            mark = "ok " if r["status"] == "ok" else "REF"
            print(f"  [{mark}] {b.get('label', k):<16} {b.get('rung','')}  {b.get('owner','')}")
            if r["status"] != "ok":
                print(f"         {r.get('why','')[:110]}")
        return
    r = registry()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Agent blocks — {r['count']} composable capabilities\n")
    print(f"  {'BLOCK':<16}{'RUNG':<6}{'OWNER':<10}ANSWERS")
    for b in r["blocks"]:
        print(f"  {b['label']:<16}{b['rung']:<6}{b['owner']:<10}{b['answers']}")
    print("\n  Every block delegates to the module that owns the answer — none compute their own.")
    print("  A block that cannot answer honestly refuses and says what would enable it.")


if __name__ == "__main__":
    main()
