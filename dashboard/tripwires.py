#!/usr/bin/env python3
"""Trip-wires — the decision log, watching itself for expiry.

`decisions/` holds 90+ settled calls. Every one of them was correct given what was true
on the day it was written, and some of them are not correct any more. Nothing in the OS
notices that: a decision file is inert once written, so a strategy that quietly stopped
matching reality keeps steering the company until a human happens to reread it.

This makes the reasoning self-reporting. A decision may carry a `## Trip-wire` section
naming (a) when to look at it again and (b) the evidence that would overturn it — and
where that evidence is something the OS already measures, a machine check that is
evaluated against live data on every dashboard poll.

    ## Trip-wire
    - **Review:** 2026-12-01
    - **Overturn if:** a proven funnel exists with known cost-per-qualified-lead …
    - **Check:** `signedClients >= 3 and OtherVentureCleared`

VERDICTS
  contradicted  the machine check fired — live data now satisfies the overturn condition
  due           the review date has passed
  watching      a trip-wire exists and nothing has fired
  uncovered     no trip-wire (reported, not hidden — coverage is the point)
  unreviewed    uncovered AND older than UNREVIEWED_DAYS, i.e. nobody has looked in months

WHY THE CHECK LANGUAGE IS TINY AND NOT `eval()`
  A decision file is text in a repo that agents and future collaborators edit. Running
  arbitrary Python out of it would make every markdown file a code-execution path. The
  parser below accepts only `<fact> <op> <number>`, bare boolean facts, and `not <fact>`,
  joined by all-`and` or all-`or`. Mixed and/or is REFUSED with an explicit error rather
  than silently guessing a precedence — a trip-wire that reads ambiguously must not fire
  ambiguously.

AUTHORSHIP RULE (why coverage is deliberately low)
  A trip-wire encodes when one of the Founder's strategic calls dies. The seeded ones are
  TRANSCRIPTIONS of revisit conditions the decision files already state in their own
  words — not conditions invented here. Decisions whose revisit condition is qualitative
  ("when hand-coding becomes the bottleneck") carry the prose with no machine check, and
  decisions that never stated one are left `uncovered` on purpose. The coverage number
  is a to-do list for the Founder, not a gap to paper over.

Read-only. Exposed as GET /api/tripwires.
"""
import os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DECISIONS = os.path.join(ROOT, "decisions")

UNREVIEWED_DAYS = 180  # an uncovered decision older than this is called out by age

OPS = {
    ">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b, "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b, "<": lambda a, b: a < b,
}
TERM_RE = re.compile(r"^\s*(not\s+)?([A-Za-z][A-Za-z0-9_]*)\s*(>=|<=|==|!=|>|<)?\s*(-?[\d.]+)?\s*$")


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


# ---- the fact table --------------------------------------------------------
def facts():
    """Everything a trip-wire may reference, computed live.

    Commercial numbers come from server.goals_currents() by lazy import — the same
    computation HQ's Goals band uses — so a trip-wire can never disagree with the
    dashboard about what MRR is. (Lazy because server imports this module; at call
    time it is fully loaded.)"""
    out, notes = {}, {}

    try:
        import server
        cur = server.goals_currents()
        pipe = server.pipeline_summary() or {}
        out.update({
            "mrr": cur.get("mrr") or 0,
            "liveClients": cur.get("liveClients") or 0,
            "dealsInMotion": cur.get("dealsInMotion") or 0,
            "prospects": cur.get("newProspects") or 0,
            "referredMRR": cur.get("referredMRR") or 0,
            "activeConnectors": cur.get("activeConnectors") or 0,
            "activeAdvisors": cur.get("activeAdvisors") or 0,
            "pipelineValue": pipe.get("value") or 0,
        })
        out["signedClients"] = out["liveClients"]
        # "first non-the Founder CRM user" — connectors read the CRM through the scoped console
        out["crmNonFounderUsers"] = out["activeConnectors"] + out["activeAdvisors"]
    except Exception as e:
        notes["commercial"] = f"unavailable ({type(e).__name__}) — checks using them are skipped"

    try:
        import refresh
        d = refresh.derive()
        ls = d.get("loopSummary") or {}
        out.update({"loopsBuilt": ls.get("built") or 0, "loopsStale": ls.get("stale") or 0,
                    "loopsNever": ls.get("neverRan") or 0,
                    "commits7d": (d.get("git") or {}).get("commits7d") or 0})
        g = (d.get("gates") or {}).get("counsel") or {}
        out.update({"counselGatesCleared": g.get("cleared") or 0,
                    "counselGatesTotal": g.get("total") or 0,
                    "counselGatesBlocked": g.get("blockedHard") or 0})
        oak = str((d.get("gates") or {}).get("OtherVenture") or "").lower()
        out["OtherVentureCleared"] = bool(re.search(r"\bcleared\b|✅", oak)) and "not cleared" not in oak
    except Exception as e:
        notes["system"] = f"unavailable ({type(e).__name__}) — checks using them are skipped"

    try:  # the trust ledger — this is what lets an autonomy decision watch its own incidents
        import trust
        t = trust.build()
        out.update({"trustActions": t["ledger"]["total"], "trustIncidents": t["ledger"]["incidents"],
                    "drillsUndetected": t["drills"]["undetected"]})
    except Exception as e:
        notes["trust"] = f"unavailable ({type(e).__name__}) — checks using them are skipped"

    return out, notes


# ---- the tiny check language ----------------------------------------------
def evaluate(expr, fact_map, days_since=None):
    """-> (result: bool|None, error: str|None). None result = could not be evaluated,
    which is reported as such and never treated as "did not fire"."""
    if not expr:
        return None, None
    e = expr.strip().strip("`").strip()
    has_and, has_or = re.search(r"\band\b", e), re.search(r"\bor\b", e)
    if has_and and has_or:
        return None, ("mixes 'and' with 'or' — refused rather than guessing precedence; "
                      "split it into two trip-wires")
    joiner = "or" if has_or else "and"
    terms = re.split(r"\b" + joiner + r"\b", e) if (has_and or has_or) else [e]

    results = []
    for t in terms:
        t = t.strip()
        if t.startswith("daysSinceDecision"):
            m = re.match(r"^daysSinceDecision\s*(>=|<=|==|!=|>|<)\s*(-?[\d.]+)$", t)
            if not m or days_since is None:
                return None, f"cannot evaluate '{t}'"
            results.append(OPS[m.group(1)](days_since, float(m.group(2))))
            continue
        m = TERM_RE.match(t)
        if not m:
            return None, f"unparseable term '{t}' — see dashboard/tripwires.py for the grammar"
        neg, name, op, num = m.group(1), m.group(2), m.group(3), m.group(4)
        if name not in fact_map:
            return None, f"unknown fact '{name}'"
        v = fact_map[name]
        if op is None:
            r = bool(v)
        else:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return None, f"fact '{name}' is not numeric — drop the comparison"
            r = OPS[op](v, float(num))
        results.append((not r) if neg else r)
    return (all(results) if joiner == "and" else any(results)), None


# ---- parsing the decision files -------------------------------------------
FIELD_RE = {
    "review": re.compile(r"^\s*[-*]\s*\*\*Review:?\*\*\s*(.+)$", re.M | re.I),
    "overturn": re.compile(r"^\s*[-*]\s*\*\*Overturn if:?\*\*\s*(.+)$", re.M | re.I),
    "check": re.compile(r"^\s*[-*]\s*\*\*Check:?\*\*\s*(.+)$", re.M | re.I),
    "owner": re.compile(r"^\s*[-*]\s*\*\*Owner:?\*\*\s*(.+)$", re.M | re.I),
}
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_")
ISO_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _decision(fn, fact_map, today):
    txt = _read(os.path.join(DECISIONS, fn))
    m = DATE_RE.match(fn)
    date = m.group(1) if m else None
    title = next((l[2:].strip() for l in txt.splitlines() if l.startswith("# ")), fn[:-3])
    title = re.sub(r"^Decision\s*[—–-]\s*", "", title).strip()
    st = re.search(r"\*\*Status:?\*\*\s*(.+)", txt)
    status = re.sub(r"[*`]", "", st.group(1)).strip()[:120] if st else ""

    sec = re.search(r"^##+\s*Trip-?wire\s*$\n(.*?)(?=\n##\s|\Z)", txt, re.M | re.S)
    tw = {k: None for k in FIELD_RE}
    if sec:
        for k, rx in FIELD_RE.items():
            mm = rx.search(sec.group(1))
            if mm:
                tw[k] = re.sub(r"\s+", " ", mm.group(1)).strip()

    age = None
    if date:
        try:
            age = (today - datetime.date.fromisoformat(date)).days
        except ValueError:
            pass

    review_date, review_overdue = None, False
    if tw["review"]:
        rm = ISO_RE.search(tw["review"])
        if rm:
            review_date = rm.group(1)
            try:
                review_overdue = datetime.date.fromisoformat(review_date) <= today
            except ValueError:
                pass

    # "**Check:** _none — this reverses on the Founder's call_" is a deliberate, documented absence,
    # not a broken expression. Treat it as prose so it never reports a parse error.
    check_note = None
    if tw["check"] and re.match(r"^_?\s*none\b", tw["check"], re.I):
        check_note, tw["check"] = tw["check"].strip("_ "), None

    result, err = (None, None)
    if tw["check"]:
        result, err = evaluate(tw["check"], fact_map, age)

    if not sec:
        verdict = "unreviewed" if (age or 0) >= UNREVIEWED_DAYS else "uncovered"
    elif result is True:
        verdict = "contradicted"
    elif review_overdue:
        verdict = "due"
    else:
        verdict = "watching"

    return {
        "file": f"decisions/{fn}", "title": title, "date": date, "ageDays": age,
        "status": status, "hasTripwire": bool(sec),
        "review": review_date or tw["review"], "reviewOverdue": review_overdue,
        "overturnIf": tw["overturn"], "check": tw["check"], "checkNote": check_note,
        "checkResult": result, "checkError": err, "verdict": verdict,
    }


ORDER = {"contradicted": 0, "due": 1, "watching": 2, "unreviewed": 3, "uncovered": 4}


def build(today=None):
    today = today or datetime.date.today()
    fact_map, fact_notes = facts()
    rows = []
    try:
        names = sorted(f for f in os.listdir(DECISIONS)
                       if f.endswith(".md") and not f.startswith("_"))
    except OSError:
        names = []
    for fn in names:
        rows.append(_decision(fn, fact_map, today))

    counts = {k: sum(1 for r in rows if r["verdict"] == k) for k in ORDER}
    errs = [r for r in rows if r["checkError"]]
    rows.sort(key=lambda r: (ORDER.get(r["verdict"], 9), -(r["ageDays"] or 0)))
    covered = sum(1 for r in rows if r["hasTripwire"])
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(rows),
        "covered": covered,
        "coveragePct": round(covered / len(rows) * 100) if rows else 0,
        "counts": counts,
        "fired": [r for r in rows if r["verdict"] in ("contradicted", "due")],
        "watching": [r for r in rows if r["verdict"] == "watching"],
        "uncovered": [r for r in rows if r["verdict"] in ("uncovered", "unreviewed")][:60],
        "rows": rows,
        "facts": fact_map,
        "factNotes": fact_notes,
        "checkErrors": [{"file": r["file"], "check": r["check"], "error": r["checkError"]}
                        for r in errs],
        "unreviewedDays": UNREVIEWED_DAYS,
        "note": ("Seeded trip-wires transcribe revisit conditions the decision files already "
                 "state. Uncovered decisions are shown, not hidden — the coverage number is a "
                 "to-do list. A check that cannot be evaluated is reported as an error, never "
                 "silently read as 'did not fire'."),
    }


if __name__ == "__main__":
    d = build()
    print(f"TRIP-WIRES — {d['covered']}/{d['total']} decisions carry one ({d['coveragePct']}%)")
    for k in ORDER:
        print(f"  {k:<14} {d['counts'][k]}")
    if d["fired"]:
        print("\nFIRED:")
        for r in d["fired"]:
            print(f"  [{r['verdict']}] {r['title']}  ({r['file']})")
            if r["verdict"] == "contradicted":
                print(f"      check `{r['check']}` is now TRUE — {r['overturnIf']}")
            else:
                print(f"      review date {r['review']} has passed")
    if d["checkErrors"]:
        print("\nCHECK ERRORS (reported, never treated as 'did not fire'):")
        for e in d["checkErrors"]:
            print(f"  {e['file']}: {e['error']}")
    print(f"\nfacts: {d['facts']}")
    if d["factNotes"]:
        print(f"fact gaps: {d['factNotes']}")
