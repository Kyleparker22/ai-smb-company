#!/usr/bin/env python3
"""The autonomy dial — on the pipeline itself.

Every CRM's headline number is pipeline value. This one carries a second number
that no CRM has ever put on a board:

    the percentage of this pipeline that is running WITHOUT you.

It is the Autonomy Matrix (processes/autonomy-matrix.md) applied to the CRM's own
actions. Each action sits on a rung R0-R3, climbs only on a streak of clean real
uses, and the dial is the measured share of pipeline work executing unattended.

Two dials, kept apart on purpose:
  · OBSERVATION autonomy — analysis, watching, reporting. Cheap to automate, and
    a number that flatters. Reported, but it is not the headline.
  · ACTION autonomy — things that actually move a deal. This is the headline,
    because this is the one that is hard and the one that means anything.

Promotion is never automatic and never computed here. This measures; Kolby evals;
the Founder promotes. That separation is the standard, and a tool that promoted itself
would break the exact thing it exists to prove.

Rungs live in data.json -> meta.autonomy (single source, editable). `--init` seeds them.

Run:
    python3 crm/autonomy.py
    python3 crm/autonomy.py --init
    python3 crm/autonomy.py --json
"""
import json, os, sys, datetime, fcntl

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
# Enforced by playground/check_isolation.py — a module that reads/writes off HERE
# will read the sandbox and WRITE LIVE, which is how synthetic connectors once
# landed in the real CRM (2026-08-07).
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
DATA_JS = os.path.join(DATA_DIR, "data.js")
PENDING = os.path.join(DATA_DIR, "_pending-activities.json")
ESCALATIONS = os.path.join(DATA_DIR, "_agent-escalations.json")
SPREAD = os.path.join(DATA_DIR, "_deal-spread.json")
LOCK = os.path.join(REPO, "runtime", ".repo.lock")
TODAY = datetime.date.today()

WINDOW = 30          # trailing days the dial measures
HUMAN = {"the Founder", "the Founder"}

# Thresholds copied from processes/autonomy-matrix.md §Advancement. Change one, change both.
THRESHOLD = {"R2": {"weeks": 4, "uses": 10}, "R1": {"weeks": 8, "uses": 20}}

ACTIONS = [
    {"key": "read", "label": "Read / roll up the pipeline", "kind": "observation",
     "rung": "R3", "ceiling": "R3", "note": "inherently safe"},
    {"key": "deal-agent-note", "label": "Deal-agent status note", "kind": "observation",
     "rung": "R3", "ceiling": "R3", "note": "writes to agentLog only, reversible in git"},
    {"key": "adversarial-read", "label": "Adversarial read (spread)", "kind": "observation",
     "rung": "R3", "ceiling": "R3", "note": "analysis only, deterministic, writes no deal field"},
    {"key": "escalate", "label": "Raise an escalation", "kind": "observation",
     "rung": "R3", "ceiling": "R3", "note": "queues an ask; commits nothing"},
    {"key": "enrich", "label": "Enrich a company from its public site", "kind": "action",
     "rung": "R2", "ceiling": "R3", "note": "auto + reversible; fills CRM gaps"},
    {"key": "autolog", "label": "Auto-log an activity from mail/calendar", "kind": "action",
     "rung": "R1", "ceiling": "R2", "note": "lands in the pending queue; a human confirms"},
    {"key": "draft-touch", "label": "Draft the next touch", "kind": "action",
     "rung": "R1", "ceiling": "R2", "note": "drafting is free; sending is not"},
    {"key": "queue-artifact", "label": "Queue an artifact build", "kind": "action",
     "rung": "R1", "ceiling": "R2", "note": "spends build time — proposed, not started"},
    {"key": "stage-advance", "label": "Advance a deal a stage", "kind": "action",
     "rung": "R1", "ceiling": "R2", "note": "the exit criteria are a human judgement until evidence says otherwise"},
    {"key": "send-external", "label": "Send anything to a human outside yourco", "kind": "action",
     "rung": "R1", "ceiling": "R1", "note": "gated by design — the Founder sends, agents draft"},
]


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def _load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def actions_of(data):
    return data.get("meta", {}).get("autonomy", {}).get("actions") or ACTIONS


def evidence(data):
    """Count real uses in the trailing window, split by who did them."""
    since = TODAY - datetime.timedelta(days=WINDOW)
    human, agent = {}, {}

    def bump(bucket, key, n=1):
        bucket[key] = bucket.get(key, 0) + n

    for a in data.get("activities", []) or []:
        d = _d(a.get("date"))
        if not d or d < since:
            continue
        who = str(a.get("who") or "").strip().lower()
        # Activity types were standardised + capitalised on 2026-08-11. Matched case-insensitively
        # with the pre-rename keys kept as aliases — when this mapping silently missed, every
        # activity fell through to "read" (an observation) and the ACTION dial read a flattering
        # 100% off an empty denominator.
        t = str(a.get("type") or "").strip().lower()
        key = {"stage change": "stage-advance", "stage": "stage-advance",
               "email": "send-external", "call": "send-external", "text": "send-external",
               "meeting": "send-external", "demo": "send-external", "proposal sent": "send-external",
               }.get(t, "autolog" if t in ("note", "deliverable", "research", "other") else "read")
        bump(human if who in HUMAN or not who else agent, key)

    for deal in data.get("deals", []) or []:
        for l in deal.get("agentLog") or []:
            d = _d(l.get("date"))
            if d and d >= since:
                bump(agent, "deal-agent-note")
        if deal.get("nextDraft"):
            bump(agent, "draft-touch")
        if deal.get("spread"):
            d = _d(deal["spread"].get("date"))
            if d and d >= since:
                bump(agent, "adversarial-read")
    for e in _load(ESCALATIONS, []) or []:
        d = _d(e.get("date"))
        if d and d >= since:
            bump(agent, "escalate")
    for p in _load(PENDING, []) or []:
        bump(agent, "autolog")
    for q in data.get("dispatch", []) or []:
        d = _d(q.get("date"))
        if d and d >= since:
            bump(agent, "queue-artifact")
    return human, agent


def compute(data):
    acts = actions_of(data)
    human, agent = evidence(data)
    rows = []
    for a in acts:
        h, g = human.get(a["key"], 0), agent.get(a["key"], 0)
        total = h + g
        need = THRESHOLD.get(a["rung"], {})
        rows.append({**a, "usesHuman": h, "usesAgent": g, "uses": total,
                     "unattendedShare": round(g / total, 3) if total else None,
                     "advanceWhen": (None if a["rung"] == a["ceiling"] else
                                     f"{need.get('weeks')} consecutive clean weekly evals covering "
                                     f"≥{need.get('uses')} real uses (Kolby evals · the Founder promotes)"),
                     "usesToward": (None if a["rung"] == a["ceiling"] else
                                    f"{total} use(s) in the last {WINDOW}d of the ≥{need.get('uses')} needed")})

    def dial(kind):
        sel = [r for r in rows if r["kind"] == kind]
        h = sum(r["usesHuman"] for r in sel)
        g = sum(r["usesAgent"] for r in sel)
        return {"human": h, "agent": g, "total": h + g,
                "pct": round(100 * g / (h + g)) if (h + g) else None}

    action, observation = dial("action"), dial("observation")
    blocked = [r["label"] for r in rows if r["rung"] == r["ceiling"] == "R1"]
    return {
        "generated": TODAY.isoformat(), "windowDays": WINDOW,
        "actionDial": action, "observationDial": observation,
        "headline": action["pct"],
        "actions": rows,
        "gatedByDesign": blocked,
        "reading": (
            f"{action['pct']}% of pipeline-moving work ran without you in the last {WINDOW} days "
            f"({action['agent']} of {action['total']} actions)." if action["pct"] is not None else
            f"No pipeline-moving actions recorded in the last {WINDOW} days — the dial has nothing to measure yet."),
        "honesty": ("Observation autonomy is reported but is not the headline: watching a pipeline unattended is "
                    "easy and the number flatters. The headline is action autonomy — work that actually moved a "
                    "deal. Nothing here promotes anything: this module measures uses, Kolby's eval supplies the "
                    "clean-streak evidence, and the Founder sets the rung. An action that promoted itself would break "
                    "the standard it is measuring."),
    }


def init(data):
    lock = open(LOCK, "a+")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        with open(DATA) as f:
            fresh = json.load(f)
        meta = fresh.setdefault("meta", {})
        if (meta.get("autonomy") or {}).get("actions"):
            return False
        meta["autonomy"] = {"note": "CRM action rungs per processes/autonomy-matrix.md. "
                                    "Kolby evals, the Founder promotes — never edited by an agent.",
                            "windowDays": WINDOW, "thresholds": THRESHOLD, "actions": ACTIONS}
        tmp = DATA + ".tmp.auto"
        with open(tmp, "w") as f:
            json.dump(fresh, f, indent=2, ensure_ascii=False)
        os.replace(tmp, DATA)
        with open(DATA_JS, "w") as f:
            f.write("/* AUTO-GENERATED from data.json by server.py. Source of truth is data.json. */\n")
            f.write("window.CRM_DATA = " + json.dumps(fresh, indent=2, ensure_ascii=False) + ";\n")
        return True
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)


def main():
    with open(DATA) as f:
        data = json.load(f)
    if "--init" in sys.argv:
        print("seeded meta.autonomy" if init(data) else "meta.autonomy already present — untouched")
        return
    r = compute(data)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    a, o = r["actionDial"], r["observationDial"]
    print(f"Autonomy dial — pipeline running without you\n")
    print(f"  ACTION       {a['pct'] if a['pct'] is not None else '—'}%   ({a['agent']}/{a['total']} pipeline-moving actions, last {r['windowDays']}d)")
    print(f"  observation  {o['pct'] if o['pct'] is not None else '—'}%   ({o['agent']}/{o['total']})\n")
    for x in r["actions"]:
        tail = f"→ {x['ceiling']}: {x['advanceWhen']}" if x["advanceWhen"] else "at ceiling"
        print(f"  {x['rung']}  {x['label'][:44]:<44} uses {x['uses']:>3} (agent {x['usesAgent']})  {tail}")
    if r["gatedByDesign"]:
        print("\n  Gated by design regardless of evidence: " + ", ".join(r["gatedByDesign"]))
    print(f"\n{r['honesty']}")


if __name__ == "__main__":
    main()
