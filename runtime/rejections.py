#!/usr/bin/env python3
"""The anti-library — what yourco decided NOT to do, and the condition that would reopen it.

WHY THIS EXISTS.  `decisions/` records what was chosen. `learnings/` records what was observed.
Neither records what was **rejected** — so the OS's idea generators (Brett weekly, Melanie's
daily initiative loop, the advisory panels, source-watch, connector-spotter) have no memory of
their own rejects. The same idea comes back months later with no evidence attached, and one
person re-adjudicates it from scratch. That is the single highest-volume claim on the Founder's
attention that produces nothing.

WHAT IT IS.  One markdown file per rejected idea, each carrying a **revisit condition** written
in the *existing* trip-wire grammar (`decisions/_TRIPWIRES.md`) and evaluated against the *same*
live facts by the *same* engine (`dashboard/tripwires.py`). A rejection is a trip-wire pointed at
a non-decision — which is why this is cheap: there is no second check language to learn, and no
second set of facts that could disagree with HQ about what MRR is.

HOW A LOOP USES IT.  Before proposing, an idea loop runs `--check "<the idea>"` and must state
one of two things in its artifact:
    "not previously rejected"
    "previously rejected <date> (<file>) because <reason>; what has changed since is <X>"
A re-proposal is never forbidden — it is required to carry evidence. Munger's inversion, made
machine-checkable.

FOUR HONESTY RULES (tests in runtime/test_agentops.py):

1. **Matching is ADVISORY and says so.**  Similarity is deterministic token overlap — no model,
   no embedding — and the output ranks *candidates* with scores. It never returns a verdict of
   "duplicate". A false positive here suppresses a good idea, which is strictly worse than a
   re-proposal, so the tool is built to under-claim.
2. **A rejection with no revisit condition is FLAGGED, not accepted.**  `unconditional` is a
   reported state, not a silent one — the same standard `decisions/_TRIPWIRES.md` applies to
   decisions: a call whose author can't name what would reopen it hasn't finished being made.
3. **A check that can't be evaluated is an error, never a "did not fire".**  Inherited from the
   trip-wire engine, on purpose. Silence has to mean something.
4. **Near-misses are counted, not hidden.**  Candidates below the similarity floor are reported
   as a count with the floor that produced it.

CLI
  python3 runtime/rejections.py --check "sell the audit as a standalone product"
  python3 runtime/rejections.py --list            # every rejection + live revisit status
  python3 runtime/rejections.py --due             # only the ones reality has reopened
  python3 runtime/rejections.py --new "<idea>"    # scaffold a new entry
"""
import os, re, sys, json, argparse, datetime

ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REJECTIONS = os.path.join(ROOT, "rejections")
sys.path.insert(0, os.path.join(CODE_ROOT, "dashboard"))

# TWO thresholds, deliberately. The first tuning had one, and a genuinely-new idea that shared
# four generic words with an old rejection got told it was "previously rejected" — which is the
# suppression failure this tool must not have. So: show context liberally, DEMAND the evidence
# line only on a strong hit.
MIN_SIM = 0.25       # show as a near-neighbour worth reading
STRONG_SIM = 0.40    # …and only at this level does the artifact owe a "what changed" line
TOP_N = 5

STOP = {"a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "is", "it", "that", "this",
        "with", "as", "at", "by", "be", "not", "from", "we", "our", "us", "should", "could",
        "would", "do", "does", "make", "build", "new", "idea", "into", "its", "their", "them"}

FIELDS = {
    "proposed": r"^\s*[-*]\s*\*\*Proposed by:?\*\*\s*(.+)$",
    "rejected": r"^\s*[-*]\s*\*\*Rejected:?\*\*\s*(.+)$",
    "why": r"^\s*[-*]\s*\*\*Why:?\*\*\s*(.+)$",
    "revisit": r"^\s*[-*]\s*\*\*Revisit if:?\*\*\s*(.+)$",
    "check": r"^\s*[-*]\s*\*\*Check:?\*\*\s*(.+)$",
    "covers": r"^\s*[-*]\s*\*\*Check covers:?\*\*\s*(.+)$",
    "review": r"^\s*[-*]\s*\*\*Review:?\*\*\s*(.+)$",
    "tags": r"^\s*[-*]\s*\*\*Tags:?\*\*\s*(.+)$",
    "source": r"^\s*[-*]\s*\*\*Source:?\*\*\s*(.+)$",
}


def _stem(w):
    """Crudest possible suffix strip. It exists because the first real test of this tool failed:
    'hardscapers' in a proposal did not match 'hardscaping' in the rejection it was a re-proposal
    of. Full stemming is not worth a dependency here; these four suffixes cover the miss."""
    for suf in ("ing", "ers", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def _tok(text):
    return {_stem(w) for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if w not in STOP and len(w) > 2}


def _field(body, key):
    m = re.search(FIELDS[key], body, re.M | re.I)
    return " ".join(m.group(1).split()) if m else ""


def load(root=REJECTIONS):
    """Every rejection on disk. Unreadable files are counted and surfaced, never skipped."""
    out, unreadable = [], []
    if not os.path.isdir(root):
        return out, unreadable
    for fn in sorted(os.listdir(root)):
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        path = os.path.join(root, fn)
        try:
            body = open(path, encoding="utf-8").read()
        except OSError as e:
            unreadable.append({"file": fn, "error": str(e)})
            continue
        title = ""
        for line in body.splitlines():
            s = line.strip().lstrip("#").strip()
            if s:
                title = s
                break
        m = re.match(r"(\d{4}-\d{2}-\d{2})_", fn)
        rec = {"file": fn, "path": os.path.relpath(path, ROOT), "title": title,
               "date": m.group(1) if m else None}
        for k in FIELDS:
            rec[k] = _field(body, k)
        rec["_tokens"] = _tok(" ".join([title, rec["why"], rec["tags"], rec["revisit"]]))
        out.append(rec)
    return out, unreadable


def _status(rec, fact_map, today):
    """-> (verdict, detail). Verdicts:
       reopened      the check fired — live data now satisfies the revisit condition
       due           the review date has passed
       standing      a revisit condition exists and nothing has fired
       unconditional NO revisit condition was written — flagged, per honesty rule 2
       error         the check could not be evaluated (never read as 'did not fire')"""
    from tripwires import evaluate  # shared engine — one grammar, one set of facts
    if not rec["revisit"] and not rec["check"]:
        return "unconditional", ("no revisit condition was written — a permanent veto with no "
                                 "stated reopening condition is a red flag, not a clean file")
    # Strip the markdown wrapper before testing for the documented-absence marker: the field
    # arrives as `` `_none — why` ``, and a backtick made every documented absence read as a
    # parse error — i.e. as a broken check rather than a deliberate one.
    chk = rec["check"].strip().strip("`").strip()
    if chk and not re.match(r"^_?none\b", chk, re.I):
        res, err = evaluate(chk, fact_map)
        if err:
            return "error", err
        if res:
            return "reopened", f"check fired: `{chk}`" + (
                f"  — covers only: {rec['covers']}" if rec["covers"] else
                "  — no 'Check covers' line, so treat the firing as a prompt to re-read, not a green light")
    if rec["review"]:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", rec["review"])
        if m:
            try:
                if datetime.date.fromisoformat(m.group(1)) <= today:
                    return "due", f"review date {m.group(1)} has passed"
            except ValueError:
                return "error", f"unparseable review date '{rec['review']}'"
    return "standing", rec["revisit"] or "revisit condition is prose-only"


def status_all(today=None, root=REJECTIONS):
    today = today or datetime.date.today()
    recs, unreadable = load(root)
    try:
        from tripwires import facts
        got = facts()            # facts() returns (fact_map, notes) — unpack, never pass the tuple
        fact_map = got[0] if isinstance(got, tuple) else got
        fact_err = None
    except Exception as e:                     # HQ data missing → say so, don't fake evaluation
        fact_map, fact_err = {}, f"{type(e).__name__}: {e}"
    out = []
    for r in recs:
        v, d = ("error", f"live facts unavailable ({fact_err})") if fact_err and r["check"] \
            else _status(r, fact_map, today)
        out.append({**{k: v2 for k, v2 in r.items() if not k.startswith("_")},
                    "verdict": v, "detail": d})
    return {"rejections": out, "unreadable": unreadable, "facts_error": fact_err,
            "counts": {v: sum(1 for r in out if r["verdict"] == v)
                       for v in ("reopened", "due", "standing", "unconditional", "error")}}


def check(idea, today=None, root=REJECTIONS, min_sim=MIN_SIM, top_n=TOP_N):
    """Has this been proposed and killed before? ADVISORY — candidates, never a verdict."""
    today = today or datetime.date.today()
    recs, unreadable = load(root)
    it = _tok(idea)
    scored = []
    for r in recs:
        rt = r["_tokens"]
        # OVERLAP COEFFICIENT, not Jaccard. A one-line proposal checked against a paragraph-long
        # rejection has a huge union, so Jaccard drove every real re-proposal below the floor —
        # the exact false negative this tool exists to prevent. Dividing by the SHORTER side asks
        # the right question: "how much of the shorter text is contained in the longer one?"
        denom = min(len(it), len(rt))
        sim = round(len(it & rt) / denom, 3) if denom else 0.0
        scored.append((sim, sorted(it & rt), r))
    scored.sort(key=lambda s: -s[0])
    above = [s for s in scored if s[0] >= min_sim]
    st = {r["file"]: r for r in status_all(today, root)["rejections"]}
    return {
        "idea": idea,
        "candidates": [{"similarity": s, "shared_terms": terms[:8], "file": r["file"],
                        "path": r["path"], "title": r["title"], "date": r["date"],
                        "why": r["why"], "revisit": r["revisit"],
                        "verdict": st.get(r["file"], {}).get("verdict"),
                        "detail": st.get(r["file"], {}).get("detail")}
                       for s, terms, r in above[:top_n]],
        "below_floor": max(0, len(scored) - len(above[:top_n])),
        "floor": min_sim,
        "strong_floor": STRONG_SIM,
        "strong_hits": [r["file"] for s, _t, r in scored if s >= STRONG_SIM],
        "total_rejections": len(recs),
        "unreadable": unreadable,
        "advisory": ("Similarity is token overlap, not judgment. These are CANDIDATES to read, "
                     "not a duplicate verdict. Re-proposing a rejected idea is allowed and "
                     "expected — it just has to say what changed."),
        "required_line": (
            "previously rejected — cite the file, the reason, and what has changed since"
            if any(s >= STRONG_SIM for s, _t, _r in scored) else
            "not previously rejected"
            + (f" (nearest on file scored {scored[0][0]:.2f}, below the {STRONG_SIM} bar)"
               if scored and scored[0][0] >= min_sim else "")),
    }


TEMPLATE = """# {idea}

- **Proposed by:** {who}
- **Rejected:** {date} by the Founder
- **Why:** [the reason, in one or two sentences — this is what a future proposer has to answer]
- **Revisit if:** [the condition that would make this worth reopening — prose, required]
- **Check:** `[optional machine test, grammar: decisions/_TRIPWIRES.md]`
- **Check covers:** [what the check does NOT cover — write this whenever it is a partial proxy]
- **Review:** {review}
- **Tags:** [comma-separated]
- **Source:** [the artifact where it was proposed and killed]
"""


def render_check(res):
    out = [f'Anti-library check — "{res["idea"][:80]}"', ""]
    if not res["candidates"]:
        out += [f"  No prior rejection resembles this ({res['total_rejections']} on file).",
                f"  Artifact line: \"{res['required_line']}\"", ""]
    for c in res["candidates"]:
        out.append(f"  • [{c['similarity']:.2f}] {c['title']}")
        out.append(f"      {c['path']}  ({c['date']}) — {c['verdict']}")
        if c["why"]:
            out.append(f"      why: {c['why'][:150]}")
        if c["detail"]:
            out.append(f"      {c['detail'][:150]}")
    if res["candidates"]:
        out += ["", f"  Artifact line: \"{res['required_line']}\""]
    if res["below_floor"]:
        out.append(f"  {res['below_floor']} more on file scored below the {res['floor']} floor.")
    out += ["", "  " + res["advisory"]]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="The anti-library — rejected ideas + revisit conditions.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", metavar="IDEA")
    g.add_argument("--list", action="store_true")
    g.add_argument("--due", action="store_true", help="only rejections reality has reopened")
    g.add_argument("--new", metavar="IDEA", help="print a scaffold for a new entry")
    ap.add_argument("--who", default="[agent / loop]")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.new:
        today = datetime.date.today()
        slug = re.sub(r"[^a-z0-9]+", "-", a.new.lower()).strip("-")[:60]
        print(f"# suggested path: rejections/{today}_{slug}.md\n")
        print(TEMPLATE.format(idea=a.new, who=a.who, date=today,
                              review=today + datetime.timedelta(days=180)))
        return

    if a.check:
        res = check(a.check)
        print(json.dumps(res, indent=2) if a.json else render_check(res))
        return

    s = status_all()
    rows = [r for r in s["rejections"] if r["verdict"] in ("reopened", "due")] if a.due else s["rejections"]
    if a.json:
        print(json.dumps({**s, "rejections": rows}, indent=2)); return
    if s["facts_error"]:
        print(f"  ⚠ live facts unavailable — checks reported as errors, not as 'did not fire': {s['facts_error']}\n")
    for r in rows:
        print(f"  [{r['verdict']:>13}] {r['title']}")
        print(f"                  {r['path']}  — {r['detail'][:120]}")
    if not rows:
        print("  (none)" if a.due else "  The anti-library is empty.")
    print("\n  " + "  ".join(f"{k}={v}" for k, v in s["counts"].items() if v))


if __name__ == "__main__":
    main()
