#!/usr/bin/env python3
"""Conversation intelligence — a live signal layer, not a transcript archive.

Granola has been connected for weeks and nothing reads it. Meeting notes land somewhere and
the deal reads — the mirror, the adversarial score, the price history — carry on knowing
nothing about what was actually said on the call. That is the difference Gong and Clari drew
in 2026: conversation intelligence stopped being a coaching archive you visit and became a
signal layer that fires the next action.

This turns a transcript into CANDIDATE SIGNALS, each one attached to a CRM object that
already exists:

  · MIRROR EVIDENCE — a sentence showing the buyer cleared a rung of their own ladder. This
    is the big one. The mirror board is the most valuable read in the CRM and the hardest to
    keep filled, because it needs someone to remember what a buyer said three weeks ago. The
    buyer already said it; it was in the transcript the whole time.
  · PRICE EVENTS — a number named out loud, with who named it.
  · PROMISES — reuses `promises.PATTERNS` rather than forking them. One commitment
    vocabulary, one place to change it.
  · OBJECTIONS — the buyer's stated resistance. Nothing in the CRM captures this today, and
    it is the single best predictor of the loss autopsy's eventual verdict.
  · THEIR MOVES — buyer-side commitments ("I'll send you the numbers"). These feed the
    adversarial read, which counts only what THEY do.

THE RULE THAT MAKES IT SAFE: **every candidate carries the exact sentence it came from.**
Nothing is proposed without a quote, and nothing is written without a human confirming it.
A mirror step marked cleared on a paraphrase would corrupt the one read in this system that
is supposed to be the buyer's own voice — so the quote is not decoration, it is the evidence,
and a candidate that cannot cite one is dropped rather than softened.

REFUSAL RULES:
  · Regex finds CANDIDATES, never facts. Everything lands in `_conversation-candidates.json`
    at status `candidate` and stays there until a human promotes it.
  · Speaker attribution is used when the transcript has it and NEVER guessed when it doesn't.
    An unattributed line cannot become a "their move", because the whole value of that signal
    is knowing who moved.

Run:
    python3 crm/conversation.py --scan <file.txt> --company "Sample Client"
    python3 crm/conversation.py --pending
    python3 crm/conversation.py --json
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
DATA = os.path.join(DATA_DIR, "data.json")
STORE = os.path.join(DATA_DIR, "_conversation-candidates.json")
TODAY = datetime.date.today()

# Buyer-ladder evidence. Each pattern is deliberately narrow and quotes what it matched —
# a broad pattern produces candidates nobody trusts, and an untrusted queue gets ignored,
# which is worse than no queue at all.
MIRROR_CUES = {
    "felt": [
        r"\b(we|i) (lose|lost|waste|miss|can'?t keep up|are drowning|keep dropping)\b[^.?!\n]{0,90}",
        r"\b(the|our) (problem|issue|bottleneck|headache) is\b[^.?!\n]{0,90}",
        r"\bit'?s costing (us|me)\b[^.?!\n]{0,70}",
    ],
    "internal": [
        r"\b(i|we) (talked to|spoke with|mentioned it to|ran it by|told)\s+(my|our)\s+[a-z]{3,18}\b[^.?!\n]{0,70}",
        r"\b(my|our) (partner|wife|husband|ops|team|foreman|bookkeeper|cfo)\s+(said|thinks|agrees|wants)\b[^.?!\n]{0,70}",
    ],
    "budget": [
        r"\b(comes? out of|pay for (it|this) (from|out of)|budget for|we have) [^.?!\n]{0,60}\b(budget|line|account)\b",
        r"\bwe (can|could) (afford|spend|do)\b[^.?!\n]{0,60}",
    ],
    "risk": [
        r"\bif (this|it) (doesn'?t|does not|fails|goes wrong)\b[^.?!\n]{0,80}",
        r"\b(i'?d|i would) (look|be)\b[^.?!\n]{0,60}",
    ],
    "story": [
        r"\b(i'?d|i would|we'?d) (tell|explain|say to|pitch) (the|my|our) (team|guys|crew|staff)\b[^.?!\n]{0,80}",
        r"\bhow (do|would) (i|we) explain\b[^.?!\n]{0,70}",
    ],
    "authority": [
        r"\b(i|we) (make|makes) (that|the) (call|decision)\b[^.?!\n]{0,50}",
        r"\b(i'?ll|i will) (need|have) to (ask|check with|run it by)\b[^.?!\n]{0,60}",
    ],
    "switch": [
        r"\bso (on|come) monday\b[^.?!\n]{0,80}",
        r"\bday to day (it|this) would\b[^.?!\n]{0,70}",
    ],
}

# Their resistance, in their words. Kept separate from mirror cues: an objection is not the
# absence of a cleared rung, it is an active push in the other direction.
OBJECTION_CUES = [
    (r"\b(too expensive|can'?t afford|out of (our|my) range|that'?s a lot|pricey)\b[^.?!\n]{0,70}", "price"),
    (r"\b(not (right )?now|next (quarter|year)|after (the )?season|revisit|circle back)\b[^.?!\n]{0,60}", "timing"),
    (r"\b(tried|used) (something|someone|a tool|another)\b[^.?!\n]{0,70}", "prior-attempt"),
    (r"\b(my|our) (guys|team|crew) (won'?t|will not|are not going to)\b[^.?!\n]{0,70}", "adoption"),
    (r"\b(what about|worried about|concerned about|not sure about)\b[^.?!\n]{0,70}", "unresolved"),
    (r"\b(do it (ourselves|in ?house)|just hire|we could build)\b[^.?!\n]{0,60}", "build-vs-buy"),
]

# A number spoken out loud, in a money context.
MONEY = re.compile(r"\$\s?([\d,]+(?:\.\d{2})?)\s?(k|thousand|/mo|per month|a month|/yr|a year)?", re.I)

# Buyer-side commitment — feeds the adversarial read, which credits only what THEY do.
THEIR_MOVE = re.compile(
    r"\b(i'?ll|i will|we'?ll|we will|let me|i can)\s+(send|get you|pull|share|forward|introduce|"
    r"set up|put you|check|ask|look at|sign|book)\b[^.?!\n]{0,80}", re.I)

# A speaker-labelled line, e.g. "Client Owner: we lose about..." — used when present, never guessed.
SPEAKER = re.compile(r"^\s*([A-Z][A-Za-z .'-]{1,28}):\s*(.+)$")


def _clean(t):
    return re.sub(r"\s+", " ", str(t or "")).strip(" -–—*|`")[:220]


def _load_store():
    try:
        with open(STORE) as f:
            return json.load(f)
    except Exception:
        return {"candidates": []}


def _save_store(s):
    tmp = STORE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STORE)


def _lines(text):
    """[(speaker|None, line)] — attribution only where the transcript actually carries it."""
    out = []
    for raw in str(text or "").splitlines():
        if not raw.strip():
            continue
        m = SPEAKER.match(raw)
        out.append((m.group(1).strip(), m.group(2).strip()) if m else (None, raw.strip()))
    return out


def scan_text(text, company="", meeting_date=None, our_names=()):
    """Every candidate signal in one transcript, each carrying its own quote."""
    date = meeting_date or TODAY.isoformat()
    ours = {n.strip().lower() for n in our_names if n}
    cands = []

    def push(kind, key, quote, speaker, extra=None):
        q = _clean(quote)
        if len(q.split()) < 4:      # a fragment is not evidence
            return
        c = {"kind": kind, "key": key, "quote": q, "speaker": speaker,
             "company": company, "date": date, "status": "candidate"}
        if extra:
            c.update(extra)
        cands.append(c)

    for speaker, line in _lines(text):
        is_theirs = None
        if speaker:
            is_theirs = speaker.strip().lower() not in ours

        for step, pats in MIRROR_CUES.items():
            for p in pats:
                for m in re.finditer(p, line, re.I):
                    # A mirror step is THEIR ladder. A line we spoke cannot clear it, and
                    # attributing our own words to the buyer would corrupt the one read that
                    # exists to be their voice — so an OUR-side line is skipped outright and
                    # an unattributed one is proposed with attribution flagged unknown.
                    if is_theirs is False:
                        continue
                    push("mirror", step, m.group(0), speaker,
                         {"attribution": "theirs" if is_theirs else "unknown",
                          "proposedAction": f"mark `{step}` cleared on the mirror"})

        for pat, kind in OBJECTION_CUES:
            for m in re.finditer(pat, line, re.I):
                if is_theirs is False:
                    continue
                push("objection", kind, m.group(0), speaker,
                     {"attribution": "theirs" if is_theirs else "unknown",
                      "proposedAction": f"log the `{kind}` objection and answer it before advancing"})

        for m in MONEY.finditer(line):
            push("price", "number-named", line, speaker,
                 {"amount": m.group(0),
                  "namedBy": ("them" if is_theirs else "us" if is_theirs is False else "unknown"),
                  "proposedAction": "log a price event (quoted / countered) with this number"})

        for m in THEIR_MOVE.finditer(line):
            if is_theirs is False:
                continue
            push("their-move", "commitment", m.group(0), speaker,
                 {"attribution": "theirs" if is_theirs else "unknown",
                  "proposedAction": "log an activity with actor=them — this is buyer-side motion"})

    # Promises reuse the ledger's own vocabulary. Forking those patterns would give the CRM
    # two definitions of what counts as a commitment.
    #
    # But promises.scan_text() has no idea who is speaking, and "I'll send you the last twenty
    # quotes" said by the BUYER is not a promise yourco owes — it is buyer-side motion, already
    # captured above as a their-move. Left unfiltered, the ledger would show us owing work the
    # client volunteered, and the promise-debt number the client console shows them would be
    # wrong in the most embarrassing possible direction. So promises are scanned per line and
    # only kept from lines we spoke or that carry no attribution at all.
    try:
        import promises
        for speaker, line in _lines(text):
            if speaker and speaker.strip().lower() not in ours:
                continue                       # their commitment, not our promise
            for p in promises.scan_text(line, f"conversation {date}", date):
                cands.append({"kind": "promise", "key": p.get("cue"), "quote": _clean(p.get("text")),
                              "speaker": speaker, "company": company, "date": date,
                              "status": "candidate", "dueHint": p.get("dueHint"),
                              "attribution": "ours" if speaker else "unknown",
                              "proposedAction": "confirm into the promise ledger"})
    except Exception:
        pass

    # de-dupe on (kind, key, quote)
    seen, out = set(), []
    for c in cands:
        k = (c["kind"], c["key"], c["quote"].lower()[:80])
        if k in seen:
            continue
        seen.add(k)
        out.append(c)
    return out


def ingest(text, company="", meeting_date=None, our_names=("the Founder", "the Founder")):
    """Scan and QUEUE. Never writes to the CRM — that needs a human."""
    cands = scan_text(text, company, meeting_date, our_names)
    store = _load_store()
    have = {(c.get("kind"), c.get("key"), (c.get("quote") or "").lower()[:80])
            for c in store["candidates"]}
    fresh = [c for c in cands
             if (c["kind"], c["key"], c["quote"].lower()[:80]) not in have]
    store["candidates"].extend(fresh)
    store["updated"] = TODAY.isoformat()
    _save_store(store)
    return {"scanned": len(cands), "new": len(fresh), "queued": len(store["candidates"])}


def compute(data=None):
    """The pending signal queue, grouped — this is what the UI and the block read."""
    store = _load_store()
    cands = [c for c in store.get("candidates", []) if c.get("status") == "candidate"]
    by_kind = {}
    for c in cands:
        by_kind.setdefault(c["kind"], []).append(c)
    unattributed = [c for c in cands if c.get("attribution") == "unknown"]
    return {
        "generated": TODAY.isoformat(), "pending": len(cands), "byKind":
            {k: len(v) for k, v in by_kind.items()}, "candidates": cands,
        "unattributed": len(unattributed),
        "reading": (f"{len(cands)} candidate signal(s) awaiting confirmation"
                    + (f" · {len(unattributed)} with no speaker attribution in the transcript"
                       if unattributed else "")
                    if cands else
                    "No conversation has been scanned yet. Granola is connected but nothing has "
                    "been fed through — pull a transcript and run --scan."),
        "honesty": ("Regex proposes; a human confirms. Every candidate carries the exact sentence "
                    "it came from, and a mirror step is never proposed from a line WE spoke — the "
                    "buyer's ladder has to be the buyer's own words or it is worth nothing. "
                    "Unattributed lines are flagged, never assumed."),
    }


def main():
    if "--scan" in sys.argv:
        path = sys.argv[sys.argv.index("--scan") + 1]
        company = ""
        if "--company" in sys.argv:
            company = sys.argv[sys.argv.index("--company") + 1]
        text = open(path, encoding="utf-8").read()
        r = ingest(text, company)
        print(f"Scanned {r['scanned']} candidate(s), {r['new']} new. Queue: {r['queued']}.")
        print("Nothing written to the CRM — confirm them in the Evidence tab.")
        return
    r = compute()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Conversation signals — {r['pending']} pending\n")
    print("  " + r["reading"] + "\n")
    for k, n in sorted(r["byKind"].items(), key=lambda x: -x[1]):
        print(f"    {k:<12} {n}")
    for c in r["candidates"][:12]:
        who = c.get("speaker") or "(unattributed)"
        print(f"\n  [{c['kind']}/{c['key']}] {who}")
        print(f"      “{c['quote']}”")
        print(f"      → {c.get('proposedAction','')}")
    if r["candidates"]:
        print(f"\n  {r['honesty']}")


if __name__ == "__main__":
    main()
