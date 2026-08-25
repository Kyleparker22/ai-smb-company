#!/usr/bin/env python3
"""coach — role-aware practice and growth areas for connectors, advisors and partners.

    python3 crm/coach.py roles
    python3 crm/coach.py drills --role connector --rung R0
    python3 crm/coach.py growth --role connector --who "Jane Doe"
    python3 crm/coach.py session --role advisor --who "Sam" --json

WHAT THIS IS, AND WHAT THE CURRICULUM ALREADY WAS
`crm/connector_training.py` is the training GATE: which lessons a person may see, and whether their
completed training lets them hold the rung their evidence earned. It teaches. It does not practise.

This is the practice half — the difference between reading "here is what a good intro sounds like"
and being made to say one and get told what was wrong with it. It supplies:
  * DRILLS       authored scenarios attached to a lesson, each with a rubric
  * GROWTH       what this person should work on next, computed from drills taken and lessons held
  * SESSION      an ordered plan an agent can run with a human, one call

WHY THE ENGINE IS DETERMINISTIC AND THE COACHING IS NOT
Selecting the next drill, tracking who has done what, computing a gap — all mechanical, so none of it
calls a model (`learnings/ops/2026-08-09_inference-only-where-judgment-is-needed.md`). Judging a free
-text answer against a rubric is genuine judgment, so an AGENT does that, using what this serves. The
split is the point: the state is auditable and repeatable, the coaching is adaptive.

THE HONESTY CONSTRAINT THAT SHAPES EVERYTHING HERE
yourco has **n=0 connectors, n=0 advisors and n=0 signed clients.** So a coach here cannot say what
top performers do, cannot benchmark, and cannot claim a growth area from field results that do not
exist. It may only teach what yourco has actually written down, and may only infer a growth area from
what the person did IN PRACTICE. Every refusal below exists to keep that line — see `refusals()`.
"""
import os, sys, json, argparse, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "crm"))

STORE = os.path.join(ROOT, "loops", "_coach")

# A role is coachable only when its DUTIES ARE WRITTEN DOWN SOMEWHERE yourco can cite. That is not a
# formality: a coach that teaches undocumented duties is authoring them, and for one role below that
# would mean drafting a term of an unsigned legal instrument.
ROLES = {
    "connector": {
        "label": "Connector",
        "what": "Refers business to yourco; from R1 also recruits connectors. Never quotes, "
                "negotiates, or signs on yourco's behalf.",
        "content": "processes/partnerships/connector-training",
        "source": "processes/partnerships/connector-os.md + rep-packet.md",
        "coachable": True,
    },
    "advisor": {
        "label": "Advisor",
        "what": "Full-time yourco salesperson: runs the audit-shaped sales conversation, scopes the "
                "OS, and carries the proposal — inside the approval gate (the Founder sends).",
        "content": "processes/advisor-training",
        "source": "decisions/2026-07-06_advisors-connectors-taxonomy.md + processes/audit-sop.md",
        "coachable": True,
    },
    "partner": {
        "label": "Partner",
        "what": "A Member of the LLC (the Founder 50 / Partner B 35 / Mike 15).",
        "content": None,
        "source": "finance/legal-docs/operating-agreement-DRAFT.md",
        "coachable": False,
        "why_not": (
            "Partner duties are NOT written down, and that is a known open issue — the operating "
            "agreement's own gap #8, \"The undefined lane\": \"'Substantially full time' against no "
            "written duties means Service Failure never fires,\" whose fix is D5 / Schedule C-1 lane "
            "definitions for all three Principals. Those definitions are unanswered, the OA is "
            "unsigned, and the whole instrument sits behind counsel gate #14.\n"
            "Writing a partner curriculum would author Schedule C-1 by the back door: a training "
            "module stating what a Partner is responsible for becomes the de facto duties document, "
            "drafted without counsel, against a live legal question about when Service Failure "
            "fires. That is a worse outcome than having no partner coach.\n"
            "UNBLOCKS WHEN: D5 / Schedule C-1 is answered and counsel gate #14 clears. At that point "
            "the lane definitions ARE the curriculum's source and this role becomes coachable with "
            "no redesign — the content directory is the only missing piece."
        ),
    },
}


def _load(role):
    import connector_training as ct
    cfg = ROLES[role]
    if not cfg["coachable"] or not cfg.get("content"):
        return []
    d = os.path.join(ROOT, cfg["content"])
    return ct.load_lessons(d) if os.path.isdir(d) else []


def _drills_file(role):
    """Drills live in `_drills.json` beside the lessons, NOT in frontmatter.

    The lesson frontmatter parser (`connector_training._frontmatter`) is a deliberate minimal
    `key: value` reader with no YAML dependency, shared with the Connector Console and covered by its
    own tests — it cannot hold a list of objects, and widening it to carry drills would put a coaching
    feature inside the parser that gates a connector's rung. A sibling JSON file is the convention the
    folder already uses for `_resources.json`, so this adds no new idea.

    Authored, never generated: a drill is content the Founder can veto, and it stays identical between runs,
    so two people practising the same rung get the same test.
    """
    cfg = ROLES[role]
    if not cfg["coachable"] or not cfg.get("content"):
        return {}
    fp = os.path.join(ROOT, cfg["content"], "_drills.json")
    if not os.path.exists(fp):
        return {}
    try:
        return json.load(open(fp, encoding="utf-8")).get("drills", {})
    except (OSError, ValueError):
        return {}


def _drills_of(role, lesson, blob):
    out = []
    for i, d in enumerate(blob.get(lesson["slug"], [])):
        if not isinstance(d, dict) or not d.get("prompt"):
            continue
        out.append({"id": f"{lesson['slug']}#{i+1}", "lesson": lesson["slug"],
                    "rung": lesson.get("rung"), "prompt": d["prompt"],
                    "looks_like": d.get("looks_like", ""), "fails_if": d.get("fails_if", "")})
    return out


def drills(role, rung=None):
    blob = _drills_file(role)
    out = []
    for l in _load(role):
        if rung and l.get("rung") != rung:
            continue
        out += _drills_of(role, l, blob)
    return out


def _history(role, who):
    fp = os.path.join(STORE, f"{role}.jsonl")
    if not os.path.exists(fp):
        return []
    rows = []
    for line in open(fp, encoding="utf-8"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("who") == who:
            rows.append(r)
    return rows


def record(role, who, drill_id, verdict, note="", by="agent", commit=True):
    """One practice attempt.

    `by` is load-bearing and must never be dropped:
      * "agent"  — someone else judged the answer against the authored rubric
      * "self"   — the person marked their own attempt in the Connector Console

    These are NOT the same evidence and the store would be worthless if they were merged. A
    self-marked "solid" says the person read the rubric and believed they met it, which is a useful
    practice signal and is not a judgement. Everything downstream keeps them apart: `growth()` reports
    them in separate fields and never lets a self-mark clear a work-on item that an agent flagged.
    """
    if verdict not in {"solid", "shaky", "missed"}:
        raise ValueError("verdict must be solid | shaky | missed")
    if by not in {"agent", "self"}:
        raise ValueError("by must be agent | self")
    row = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "role": role, "who": who,
           "drill": drill_id, "verdict": verdict, "by": by, "note": note[:400]}
    if commit:
        os.makedirs(STORE, exist_ok=True)
        with open(os.path.join(STORE, f"{role}.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    return row


def growth(role, who):
    """What to work on next — and an explicit statement of what this CANNOT see.

    Two honest sources only: drills attempted (practice) and drills never attempted (coverage). Field
    performance is not among them, because there is no field yet.
    """
    cfg = ROLES[role]
    if not cfg["coachable"]:
        return {"role": role, "refused": True, "why": cfg["why_not"]}
    all_d = {d["id"]: d for d in drills(role)}
    hist = _history(role, who)
    judged, selfed = {}, {}
    for r in hist:
        # Rows written before `by` existed were all agent-judged (the console could not write then).
        (selfed if r.get("by") == "self" else judged).setdefault(r["drill"], []).append(r["verdict"])
    seen = set(judged) | set(selfed)

    # A work-on item comes from a JUDGED miss. A later self-mark cannot clear it: the whole point of
    # an outside judgement is that it survives the person's own opinion of how it went.
    weak = [{"drill": k, "lesson": all_d[k]["lesson"], "attempts": len(v),
             "latest": v[-1], "prompt": all_d[k]["prompt"][:140]}
            for k, v in judged.items() if k in all_d and v[-1] in {"shaky", "missed"}]
    self_flagged = [{"drill": k, "lesson": all_d[k]["lesson"], "latest": v[-1]}
                    for k, v in selfed.items()
                    if k in all_d and v[-1] in {"shaky", "missed"} and k not in judged]
    untried = [d for k, d in all_d.items() if k not in seen]
    return {
        "role": role, "who": who, "refused": False,
        "drillsTotal": len(all_d), "attempted": len(seen),
        "judgedCount": len(judged), "selfMarkedCount": len(selfed),
        "selfFlagged": self_flagged[:5],
        "workOn": sorted(weak, key=lambda w: (w["latest"] != "missed", w["drill"]))[:5],
        "neverPractised": [{"drill": d["id"], "lesson": d["lesson"], "rung": d["rung"]}
                           for d in untried][:8],
        "cannotSee": [
            "Real referral or deal outcomes — yourco has no signed clients, so nothing here is "
            "calibrated against results.",
            "How this person compares to others in the role — n=0 in every role; there is no "
            "benchmark and any ranking would be invented.",
            "Anything they do outside a recorded drill.",
            "Whether a self-marked attempt was actually good — a self-mark records that they read "
            "the rubric and formed a view, not that an outside judge agreed.",
        ],
    }


def session(role, who):
    """An ordered plan for one coaching call. The AGENT runs it and judges; this decides the order."""
    cfg = ROLES[role]
    if not cfg["coachable"]:
        return {"role": role, "refused": True, "why": cfg["why_not"]}
    g = growth(role, who)
    plan = [{"do": "re-practise", **w} for w in g["workOn"][:2]]
    plan += [{"do": "new", **d} for d in g["neverPractised"][:3]]
    return {"role": role, "who": who, "label": cfg["label"], "roleIs": cfg["what"],
            "source": cfg["source"], "plan": plan,
            "howToJudge": "For each item read the drill's `looks_like` and `fails_if` out of the "
                          "lesson, listen to their answer, then record solid|shaky|missed with one "
                          "line of why. Do not soften a missed into a shaky — the whole value is the "
                          "thing a polite coach would not say.",
            "cannotSee": g["cannotSee"]}


def refusals():
    return {r: c["why_not"] for r, c in ROLES.items() if not c["coachable"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("roles")
    d = sub.add_parser("drills"); d.add_argument("--role", required=True); d.add_argument("--rung")
    g = sub.add_parser("growth"); g.add_argument("--role", required=True); g.add_argument("--who", required=True)
    s = sub.add_parser("session"); s.add_argument("--role", required=True); s.add_argument("--who", required=True)
    r = sub.add_parser("record")
    for f in ("--role", "--who", "--drill", "--verdict"):
        r.add_argument(f, required=True)
    r.add_argument("--note", default="")
    r.add_argument("--by", default="agent", choices=["agent", "self"],
                   help="who judged: an outside judge (default) or the person themselves")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.cmd == "roles":
        for k, c in ROLES.items():
            n = len(drills(k)) if c["coachable"] else 0
            print(f"  {c['label']:<10} {'coachable' if c['coachable'] else 'NOT COACHABLE':<14} "
                  f"{n} drill(s)")
            if not c["coachable"]:
                print("      " + c["why_not"].split("\n")[0])
        return
    if getattr(a, "role", None) and a.role not in ROLES:
        sys.exit(f"--role must be one of: {', '.join(ROLES)}")
    out = {"drills": lambda: drills(a.role, a.rung),
           "growth": lambda: growth(a.role, a.who),
           "session": lambda: session(a.role, a.who),
           "record": lambda: record(a.role, a.who, a.drill, a.verdict, a.note, by=a.by)}[a.cmd]()
    print(json.dumps(out, indent=2))
    if isinstance(out, dict) and out.get("refused"):
        sys.exit(2)


if __name__ == "__main__":
    main()
