#!/usr/bin/env python3
"""The mirror board — the buyer's OWN ladder, run beside ours.

Our stages describe our process: we did a sit-down, we sent a proposal. None of
that is what the buyer is actually working through. They are clearing an entirely
different, mostly invisible ladder — whether they've said it out loud to anyone
else, where the money comes from, what happens to them personally if it fails,
and what sentence they'll use to explain it to their team.

Deals die in that second column, and no CRM has that column.

The derived signal is OVERREACH: our stage assumes buyer steps they haven't
cleared. "We are at Proposal; they have never cleared budget" is the whole
diagnosis, and it is computable the moment the mirror is filled in.

The step template lives in data.json -> meta.mirrorSteps so the UI and this module
read one definition (change-one-sweep-all). `--init` writes it if absent.

Run:
    python3 crm/mirror.py            # the mirror + overreach report
    python3 crm/mirror.py --init     # seed meta.mirrorSteps into data.json
    python3 crm/mirror.py --json
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
LOCK = os.path.join(REPO, "runtime", ".repo.lock")
TODAY = datetime.date.today()

BENCH = {"parked", "pre-convo"}   # no conversation has happened yet, so there is no buyer ladder to map

# The buyer's ladder. Not our stages restated — the things THEY have to clear,
# in the order a real buyer clears them.
STEPS = [
    {"key": "felt", "label": "Named it to themselves",
     "ask": "Have they said the problem out loud, in their own words, unprompted?"},
    {"key": "internal", "label": "Said it to someone else inside",
     "ask": "Has anyone else in their world heard them say it — partner, ops lead, spouse?"},
    {"key": "budget", "label": "Knows where the money comes from",
     "ask": "Can they name the line this gets paid out of, without checking?"},
    {"key": "risk", "label": "Priced their personal downside",
     "ask": "Do they know what happens to THEM if this fails? Unanswered, it stalls at the last step."},
    {"key": "story", "label": "Has the sentence for their team",
     "ask": "What exact sentence do they use to explain this to the people it changes?"},
    {"key": "authority", "label": "Everyone who can say no has been in a room",
     "ask": "Who else can kill this, and have they been present rather than briefed?"},
    {"key": "switch", "label": "Pictured the first Monday after",
     "ask": "Can they describe a normal Monday once it's running? If not, it isn't real to them yet."},
]

# What our stage silently assumes they've already cleared.
ALL7 = ["felt", "internal", "budget", "risk", "story", "authority", "switch"]
REQUIRES = {
    "pre-convo": [],
    "discovery": ["felt", "internal", "budget"],
    "demo-proposal": ["felt", "internal", "budget", "risk", "story"],
    "signed-onboarding": ALL7[:6],
    "build-implementation": ALL7,
    "testing": ALL7,
    "live": ALL7,
}


def steps_of(data):
    return data.get("meta", {}).get("mirrorSteps") or STEPS


def compute(data):
    steps = steps_of(data)
    keys = [s["key"] for s in steps]
    cos = {c["id"]: c for c in data.get("companies", []) or []}
    stages = {s["key"]: s for s in data.get("stages", []) or []}
    rows = []
    for d in data.get("deals", []) or []:
        stage = d.get("stage")
        if stage in BENCH:
            continue
        m = d.get("mirror") or {}
        st = m.get("steps") or {}
        cleared = [k for k in keys if str(st.get(k, {}).get("status") if isinstance(st.get(k), dict)
                                          else st.get(k)) == "yes"]
        blocked = [k for k in keys if str(st.get(k, {}).get("status") if isinstance(st.get(k), dict)
                                          else st.get(k)) == "no"]
        unknown = [k for k in keys if k not in cleared and k not in blocked]
        required = REQUIRES.get(stage, [])
        overreach = [k for k in required if k not in cleared]
        depth = 0
        for k in keys:                      # how far up their ladder they've actually got, in order
            if k in cleared:
                depth += 1
            else:
                break
        first_gap = next((k for k in keys if k not in cleared), None)
        # Steps cleared ABOVE the first gap. This is the most useful thing the board can say:
        # a buyer who has the story and can picture the Monday but can't name the budget line is
        # enthusiastic and unengaged, which looks like progress and isn't. Never inferred — it
        # only appears when a human marked those later steps yes.
        out_of_order = [k for k in cleared[depth:]]
        rows.append({
            "dealId": d.get("id"), "company": cos.get(d.get("companyId"), {}).get("name") or d.get("name"),
            "stage": stage, "stageLabel": stages.get(stage, {}).get("label") or stage,
            "champion": m.get("champion") or "", "economicBuyer": m.get("economicBuyer") or "",
            "politicalRisk": m.get("politicalRisk") or "", "theirNarrative": m.get("theirNarrative") or "",
            "blockers": m.get("blockers") or [],
            "cleared": cleared, "blocked": blocked, "unknown": unknown,
            "clearedCount": len(cleared), "depth": depth, "firstGap": first_gap,
            "outOfOrder": out_of_order,
            "required": required, "overreach": overreach,
            "unmapped": len(cleared) + len(blocked) == 0,
            "verdict": ("not mapped" if len(cleared) + len(blocked) == 0 else
                        ("clear" if not overreach else
                         f"we are ahead of them on {len(overreach)} step(s)")),
        })
    rows.sort(key=lambda r: (-len(r["overreach"]), r["depth"]))
    n_over = sum(1 for r in rows if r["overreach"] and not r["unmapped"])
    n_unmapped = sum(1 for r in rows if r["unmapped"])
    return {
        "generated": TODAY.isoformat(), "steps": steps, "requires": REQUIRES, "rows": rows,
        "overreachDeals": n_over, "unmappedDeals": n_unmapped,
        "honesty": ("A step counts as cleared only when someone marked it yes. Unknown is not cleared and is "
                    "never inferred from our own stage — inferring it would delete the entire point of the "
                    f"second column. {n_unmapped} deal(s) have no mirror filled in at all and are reported as "
                    "unmapped rather than clear."),
    }


def init(data):
    """Seed the step template into data.json so the UI and this module share one definition."""
    lock = open(LOCK, "a+")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        with open(DATA) as f:
            fresh = json.load(f)
        meta = fresh.setdefault("meta", {})
        if meta.get("mirrorSteps"):
            return False
        meta["mirrorSteps"] = STEPS
        meta["mirrorRequires"] = REQUIRES
        tmp = DATA + ".tmp.mirror"
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
        print("seeded meta.mirrorSteps" if init(data) else "meta.mirrorSteps already present — untouched")
        return
    r = compute(data)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Mirror board — their ladder, {len(r['rows'])} deal(s)\n")
    for row in r["rows"]:
        print(f"  {row['company'][:30]:<30} us: {row['stageLabel']:<14} "
              f"them: {row['clearedCount']}/{len(r['steps'])} ({row['depth']} in sequence)   {row['verdict']}")
        if row["overreach"]:
            print(f"      not cleared but assumed by {row['stageLabel']}: {', '.join(row['overreach'])}")
        if row["outOfOrder"]:
            print(f"      cleared ABOVE the gap: {', '.join(row['outOfOrder'])} — enthusiasm is running "
                  f"ahead of commitment")
        if row["firstGap"]:
            s = next(x for x in r["steps"] if x["key"] == row["firstGap"])
            print(f"      next thing to find out → {s['ask']}")
    print(f"\n{r['honesty']}")


if __name__ == "__main__":
    main()
