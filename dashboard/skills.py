#!/usr/bin/env python3
"""The skill library, with the one thing a list of skills never tells you: is it being used?

the Founder, 2026-08-23: "I feel like I just forget to use the skills."

A tab that lists every skill does not fix that — it is the same information already sitting
in .claude/skills/, one directory listing away. What is actually missing is the feedback loop: a
skill that has not fired in six weeks is either dead or forgotten, and nobody can tell which
because nothing has ever looked.

So this measures. Most skills leave a trace — daily-log writes to daily-logs/, log-decision to
decisions/, write-learning to learnings/ — and the freshest trace is a lower bound on when the
skill was last used. Where a skill leaves no durable trace (show-surface puts a page on a screen;
tool-triage may only produce an opinion) this says UNMEASURABLE and stops. A guessed usage date
would make the panel worse than the directory listing it replaced.

VERDICTS
  fresh        used within its expected rhythm
  stale        it has a trace, and the trace is old
  never        the skill exists and has produced nothing, ever
  unmeasurable no durable artifact — presence here is a reminder, not a report
"""
import datetime
import glob
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, ".claude", "skills")

# skill -> (glob of the artifact it produces, expected days between uses, one-line trigger)
# "expected" is a rhythm, not an SLA: a skill for a rare event is not failing by being quiet.
TRACE = {
    # Two globs: the second is the pre-2026-08-23 name. See _newest() on why a rename needs it.
    "daily-log":            (("daily-logs/*.md", "01 Daily Logs/*.md"), 3,
                             "End of any working session"),
    "log-decision":         ("decisions/*.md", 14, "A settled call is made"),
    "write-learning":       ("learnings/*/*.md", 14, "A repeatable pattern shows up in practice"),
    "log-build-cost":       ("clients/*/cost.md", 14, "End of a session that did client work"),
    "log-internal-cost":    ("finance/token_spend.md", 7, "End of a session that built anything internal"),
    "log-build-session":    ("loops/_build-journal/*", 14, "Start + end of a client build"),
    "add-runtime-loop":     ("runtime/prompts/*.md", 60, "A process should run on a cadence"),
    # agents/*/ was too loose — any edit inside any agent folder read as "an agent was wired".
    "wire-new-agent":       (None, 60, "An agent is born, promoted, or given a channel"),
    "advisory-panel":       ("loops/_advisory/*.md", 90, "A major decision needs stress-testing"),
    "scaffold-engagement":  ("clients/*/01_discovery.md", 90, "First real call or proposal sent"),
    "promote-warm-lead":    (None, 30, "A cold prospect replies with intent"),
    "promote-intent-signal": (None, 30, "A Sadie signal is a real business"),
    "tool-triage":          (None, 21, "\"What are your thoughts on X?\" / a link is pasted"),
    "show-surface":         (None, None, "\"Show me X\" / \"can I see the site\""),
    "create-skill":         (".claude/skills/*/SKILL.md", 60, "You solved something reusable"),
    "deploy-vps-daemon":    (None, None, "An always-on process that is not a timer"),
    "wire-credentialed-connector": (None, None, "A task needs a service with no key yet"),
    # The artifact is the wrapper itself. Rare by nature — most services either have an MCP or
    # aren't needed — so a long rhythm; quiet here is not a failure.
    "build-cli-connector":  ("runtime/*_cli.py", 120, "A service is needed and has no MCP"),
    # A NEW page under an agent's pages/ is a tight signal that a surface was designed — creation,
    # not edit, so restyling an existing page correctly does not read as a use.
    "design-surface":       ("agents/*/pages/**/*.html", 30, "Before writing CSS for anything a human looks at"),
    # The trace IS the practice record — a session that happened wrote a line to loops/_coach/.
    "run-coaching-session": ("loops/_coach/*.jsonl", 30, "\"Coach X\" / onboarding someone into a role"),
    "visual-brand-qa":      (None, None, "Any generated visual, before it reaches the Founder"),
}


def _born(slug):
    """When this skill was ADDED to the repo. A skill cannot have been used before it existed.

    Added 2026-08-24: design-surface was created that day and the panel reported it "fresh — last used
    2026-08-13", because its trace glob matched a page written eleven days earlier. The panel exists
    because the Founder said he forgets to use the skills; a brand-new skill that reads fresh is the one state
    guaranteed never to prompt him, so this is the opposite of the panel's job. Same family as the
    added-vs-modified bug above: evidence has to be attributable to the thing it is evidence FOR.
    """
    out = subprocess.run(
        ["git", "-C", ROOT, "log", "--diff-filter=A", "--format=%ad", "--date=short", "--",
         f".claude/skills/{slug}/SKILL.md"],
        capture_output=True, text=True).stdout.strip().splitlines()
    return out[-1] if out else None


def _newest(pattern, mode="added"):
    """When was a NEW artifact last created under this glob (or any of several)?

    Creation, not modification, and the distinction is the whole accuracy of this panel. The
    first version used last-modified and immediately lied: a commit that added an Owner line to
    all 25 loop prompts made `add-runtime-loop` read "used 0 days ago" when no loop had been
    added in weeks. Editing a file is not invoking the skill that creates that kind of file.

    Uses --diff-filter=A so only the commit that ADDED a path counts, and git rather than mtime
    because a checkout rewrites every mtime to now.

    EXCEPT for append-only ledgers (mode="touched"). token_spend.md and cost.md are invoked by
    APPENDING A ROW, not by being created — measuring their creation date said log-internal-cost
    was 75 days stale on the day it was written. For those, a modification IS the invocation.

    ALSO: `pattern` may be a tuple of globs, and every one is passed to git. This exists because
    git reports a renamed path as R, never A — so a directory rename makes the new glob match
    nothing and the skill reads "never" forever. `daily-log` hit this on 2026-08-23 when
    `01 Daily Logs/` became `daily-logs/`: the panel went from a true "used 2026-08-17" to a false
    "never" the moment the rename was staged. Keep the historical glob alongside the current one.
    `--follow` is not the fix — it takes a single literal path, not a glob.
    """
    flt = ["--diff-filter=A"] if mode == "added" else []
    globs = [pattern] if isinstance(pattern, str) else list(pattern)
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", *flt, "--format=%ad", "--date=short", "--", *globs],
            capture_output=True, text=True, timeout=40).stdout.strip()
    except Exception:
        return None
    return out.split("\n")[0].strip() or None if out else None


# Ledgers you APPEND to. A new row is the invocation; the file was created once and never again.
APPEND_ONLY = {"log-internal-cost", "log-build-cost"}


def _meta(slug):
    """name/description straight from the SKILL.md front matter — never a second copy."""
    path = os.path.join(SKILLS, slug, "SKILL.md")
    if not os.path.exists(path):
        return {}
    head = open(path, encoding="utf-8").read()[:3000]
    m = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\n---)", head, re.S | re.M)
    desc = " ".join(m.group(1).split()) if m else ""
    return {"description": desc, "lines": sum(1 for _ in open(path, encoding="utf-8"))}


def skills():
    today = datetime.date.today()
    out = []
    for slug in sorted(os.listdir(SKILLS)):
        d = os.path.join(SKILLS, slug)
        if not os.path.isdir(d) or slug.startswith("_"):
            continue
        pattern, expect, trigger = TRACE.get(slug, (None, None, ""))
        mode = "touched" if slug in APPEND_ONLY else "added"
        last = _newest(pattern, mode) if pattern else None
        # Discard evidence that predates the skill — it belongs to whatever produced it, not here.
        born = _born(slug)
        if last and born and last < born:
            last = None
        if pattern is None:
            verdict, age = "unmeasurable", None
        elif last is None:
            verdict, age = "never", None
        else:
            age = (today - datetime.date.fromisoformat(last)).days
            verdict = "stale" if (expect and age > expect) else "fresh"
        out.append({"slug": slug, "trigger": trigger, "lastTrace": last,
                    "ageDays": age, "expectDays": expect, "verdict": verdict, **_meta(slug)})
    order = {"stale": 0, "never": 1, "fresh": 2, "unmeasurable": 3}
    out.sort(key=lambda s: (order[s["verdict"]], -(s["ageDays"] or 0)))
    return {"generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total": len(out),
            "counts": {k: sum(1 for s in out if s["verdict"] == k) for k in order},
            "skills": out}


if __name__ == "__main__":
    d = skills()
    print(f"{d['total']} skills · " + " · ".join(f"{v} {k}" for k, v in d["counts"].items()))
    print()
    for s in d["skills"]:
        age = f"{s['ageDays']}d ago" if s["ageDays"] is not None else (s["lastTrace"] or "—")
        print(f"  {s['verdict']:<13}{s['slug']:<30}{age:<12}{s['trigger'][:44]}")
