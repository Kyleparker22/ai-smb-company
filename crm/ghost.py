#!/usr/bin/env python3
"""Ghost pipeline — the counterfactual board.

crm/data.json is git-tracked, so every field has a complete, diffable history.
This module reads that history and answers a question no CRM answers:

    "Where would every deal be RIGHT NOW if it had moved at my own median velocity?"

The gap between the real board and that ghost board, priced in dollars, is the
cost of the weeks the deal wasn't touched — per deal, not in aggregate.

Two outputs:
  1. `timeline`  — the real board reconstructed at every revision (the scrub bar).
  2. `ghost`     — the counterfactual position of every in-motion deal + its price.

Honesty rules (house rule: never invent a number)
  - A stage's median velocity needs >= MIN_OBS completed occupancies. Below that the
    stage reports `evidence: "insufficient"` and falls back to its declared staleDays,
    clearly labelled. It is never presented as measured.
  - Stage keys were renamed on 2026-08-07 (the ladder rewrite). Legacy keys are
    remapped via LEGACY, and every remapped observation is counted and reported.
  - A deal's first appearance in the file is treated as its entry into that stage.
    That is left-censored (it may have existed earlier off-book) and is flagged.

Run:
    python3 crm/ghost.py           # human summary
    python3 crm/ghost.py --json    # the full payload
    python3 crm/ghost.py --fresh   # ignore the cache
"""
import json, os, subprocess, datetime, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
# Enforced by playground/check_isolation.py — a module that reads/writes off HERE
# will read the sandbox and WRITE LIVE, which is how synthetic connectors once
# landed in the real CRM (2026-08-07).
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
CACHE = os.path.join(DATA_DIR, "_ghost-cache.json")
REL = "crm/data.json"

MAX_REVS = 400          # cap the walk; the file has ~56 revisions today
MIN_OBS = 3             # below this we refuse to call a median "measured"
CACHE_VERSION = 6   # bump whenever LEGACY / STAGE_P / the ladder changes — the stamp keys on the
                    # DATA's sha+mtime, not on this file, so a code change alone won't invalidate a
                    # cache. Missing this after the 2026-08-11 stage merge served ghost stages that
                    # no longer existed on the ladder until the next data write.

# Stage keys used before the 2026-08-07 ladder rewrite -> the current ladder.
LEGACY = {   # every pre-2026-08-11 key -> its rung on the current ladder
    "prospect": "pre-convo", "relationship": "pre-convo", "givefirst": "pre-convo", "give-first": "pre-convo",
    "sitdown": "discovery", "audit": "discovery",
    "proposal": "demo-proposal", "signed": "signed-onboarding", "build": "build-implementation",
    "closed": "live",
    # `expand` was a rung until 2026-08-13. It is now a Live client with a SECOND deal, so
    # every historical board state replayed out of git must fold it back into live — otherwise
    # the ghost prices a rung that no longer exists and reports deals as behind on it.
    "expand": "live",
}

# Win probability by stage — mirrors STAGE_BASE in index.html. Change one, change both.
STAGE_P = {"pre-convo": 8, "discovery": 50, "demo-proposal": 70, "signed-onboarding": 90,
           "build-implementation": 93, "testing": 96, "live": 100, "parked": 3}

BENCH = {"parked"}
TERMINAL = {"live", "parked"}


def _git(*args):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, timeout=180)
    return r.stdout if r.returncode == 0 else ""


def _today():
    return datetime.date.today()


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def revisions():
    """[(sha, date)] oldest -> newest, for every commit that touched crm/data.json."""
    out = _git("log", f"--max-count={MAX_REVS}", "--format=%H|%ad", "--date=short", "--", REL)
    rows = []
    for line in out.splitlines():
        if "|" in line:
            sha, date = line.split("|", 1)
            rows.append((sha.strip(), date.strip()))
    return list(reversed(rows))


def norm(stage):
    s = str(stage or "").strip().lower()
    return LEGACY.get(s, s)


def deal_amount(d):
    v = d.get("value")
    try:
        v = float(v or 0)
    except Exception:
        v = 0.0
    if v:
        return v
    try:
        return float(d.get("retainer") or 0) * 12 + float(d.get("buildFee") or 0)
    except Exception:
        return 0.0


def ladder(data):
    """The in-motion ladder, in order, from data.json's own stage list."""
    return [s["key"] for s in data.get("stages", []) if s["key"] not in BENCH]


def build_timeline():
    """Reconstruct {date, sha, stages:{dealId:stageKey}} at every revision, plus a deal index."""
    snaps, index, remapped = [], {}, 0
    for sha, date in revisions():
        blob = _git("show", f"{sha}:{REL}")
        if not blob:
            continue
        try:
            d = json.loads(blob)
        except Exception:
            continue
        stages = {}
        for deal in d.get("deals", []) or []:
            did = deal.get("id")
            if not did:
                continue
            raw = str(deal.get("stage") or "").strip().lower()
            key = norm(raw)
            if key != raw:
                remapped += 1
            stages[did] = key
            co = next((c for c in d.get("companies", []) or [] if c.get("id") == deal.get("companyId")), {})
            index[did] = {"name": co.get("name") or deal.get("name") or did,
                          "useCase": deal.get("useCase") or "",
                          "amount": deal_amount(deal),
                          "owner": deal.get("owner") or ""}
        if snaps and snaps[-1]["stages"] == stages:
            snaps[-1]["date"] = date          # same board, later commit — keep one row
            snaps[-1]["sha"] = sha[:10]
            continue
        snaps.append({"date": date, "sha": sha[:10], "stages": stages})
    return snaps, index, remapped


def occupancies(snaps, data=None):
    """Per deal: [(stage, enteredISO, leftISO|None)] from consecutive snapshots.

    Git revisions are the primary evidence. Stage-move activities (written by the
    board's advance flow since v2.1) are a second source: they carry the exact day
    of a move that two weekly commits would otherwise smear. Where both exist the
    activity wins, because it is dated by the event rather than by the commit."""
    out, cur = {}, {}
    for s in snaps:
        for did, stage in s["stages"].items():
            c = cur.get(did)
            if c is None:
                cur[did] = {"stage": stage, "since": s["date"]}
                out.setdefault(did, [])
            elif c["stage"] != stage:
                out[did].append((c["stage"], c["since"], s["date"]))
                cur[did] = {"stage": stage, "since": s["date"]}
    for did, c in cur.items():
        out.setdefault(did, []).append((c["stage"], c["since"], None))

    if data:
        for did, moves in stage_activity_moves(data).items():
            spans = out.get(did)
            if not spans:
                continue
            for when in moves:                       # snap a boundary to the true move date
                for i, (stage, since, until) in enumerate(spans):
                    if until and abs((_d(until) - when).days) <= 7:
                        spans[i] = (stage, since, when.isoformat())
                        if i + 1 < len(spans):
                            nx = spans[i + 1]
                            spans[i + 1] = (nx[0], when.isoformat(), nx[2])
                        break
    return out


def stage_activity_moves(data):
    """{dealId: [date]} for every logged stage advance. The board writes these on each move."""
    by_co = {}
    for d in data.get("deals", []) or []:
        by_co.setdefault(d.get("companyId"), []).append(d.get("id"))
    out = {}
    for a in data.get("activities", []) or []:
        if a.get("type") != "stage":
            continue
        when = _d(a.get("date"))
        if not when:
            continue
        for did in by_co.get(a.get("companyId"), []):
            out.setdefault(did, []).append(when)
    return out


def velocities(occ, data):
    """Median days-in-stage from your OWN history. Refuses to fake a median below MIN_OBS."""
    buckets = {}
    for did, spans in occ.items():
        for stage, since, until in spans:
            if until is None:
                continue                      # still sitting there — not a completed occupancy
            a, b = _d(since), _d(until)
            if not a or not b:
                continue
            buckets.setdefault(stage, []).append(max(0, (b - a).days))
    stale = {s["key"]: s.get("staleDays") for s in data.get("stages", [])}
    out = {}
    for key in ladder(data):
        obs = sorted(buckets.get(key, []))
        if len(obs) >= MIN_OBS:
            out[key] = {"days": round(statistics.median(obs), 1), "n": len(obs),
                        "evidence": "measured", "observations": obs}
        else:
            fb = stale.get(key)
            out[key] = {"days": float(fb) if fb else None, "n": len(obs),
                        "evidence": "policy", "needs": MIN_OBS - len(obs),
                        "note": (f"only {len(obs)} completed occupancy(ies) — running on the stage's declared "
                                 f"staleDays ({fb}d), which is the ladder's stated policy, not a measured median. "
                                 f"{MIN_OBS - len(obs)} more completed move(s) here makes it measured."
                                 if fb else f"only {len(obs)} observation(s) and no staleDays — no number produced"),
                        "observations": obs}
    return out


def _walk(start_stage, start_date, vel, order, today):
    """Advance a deal from start_stage/start_date through the ladder at median velocity."""
    if start_stage not in order:
        return start_stage, 0.0
    i = order.index(start_stage)
    cursor = start_date
    while i < len(order) - 1:
        v = vel.get(order[i], {}).get("days")
        if not v:
            break                              # no velocity for this rung — stop honestly
        nxt = cursor + datetime.timedelta(days=float(v))
        if nxt > today:
            break
        cursor, i = nxt, i + 1
        if order[i] in TERMINAL:
            break
    return order[i], (today - cursor).days


PLAYGROUND_REFUSAL = {
    "unavailable": True,
    "reason": ("Ghost replays git history of crm/data.json. Playground data is untracked, "
               "and using the live file's history would show real deals inside the sandbox. "
               "Open the live CRM for Ghost."),
}


def compute(fresh=False):
    # Refuse in the sandbox, HERE rather than in the caller. This check lived only in
    # crm/server.py's route until 2026-08-24, so the API refused correctly while
    # `YOURCO_DATA_ROOT=… python3 crm/ghost.py` happily replayed the LIVE repo history and printed
    # real deal velocity under a PLAYGROUND banner — the exact outcome playground/_README.md says
    # must never happen ("real past deals inside the sandbox as if they were synthetic"). A guard
    # that only one entry point applies is a guard the next entry point will not have.
    if os.environ.get("YOURCO_DATA_ROOT"):
        return dict(PLAYGROUND_REFUSAL)
    with open(DATA) as f:
        data = json.load(f)
    head = (_git("log", "--max-count=1", "--format=%H", "--", REL) or "").strip()
    stamp = f"{CACHE_VERSION}:{head}:{os.stat(DATA).st_mtime_ns}"
    if not fresh and os.path.exists(CACHE):
        try:
            with open(CACHE) as f:
                c = json.load(f)
            if c.get("_stamp") == stamp:
                return c
        except Exception:
            pass

    snaps, index, remapped = build_timeline()
    occ = occupancies(snaps, data)
    vel = velocities(occ, data)
    order = ladder(data)
    today = _today()

    rows, total_gap, policy_gap, unpriced_n = [], 0.0, 0.0, 0
    measured_rungs = sum(1 for v in vel.values() if v["evidence"] == "measured")
    for deal in data.get("deals", []) or []:
        stage = norm(deal.get("stage"))
        if stage in TERMINAL or stage in BENCH:
            continue
        spans = occ.get(deal["id"], [])
        # Origin = the first time this deal was observed ON THE LADDER. Time spent on the
        # bench (Relationship/Parked) is not pipeline time and must not be charged as delay.
        on_ladder = [s for s in spans if norm(s[0]) in order]
        if on_ladder:
            origin_stage, origin_date = norm(on_ladder[0][0]), _d(on_ladder[0][1])
            censored = True   # first sighting in the file, not necessarily its first day
        else:
            origin_stage, origin_date, censored = stage, _d(deal.get("stageSince")), False
        if not origin_date:
            origin_date = today
        ghost_stage, ghost_dwell = _walk(origin_stage, origin_date, vel, order, today)

        ri = order.index(stage) if stage in order else -1
        gi = order.index(ghost_stage) if ghost_stage in order else -1
        oi = order.index(origin_stage) if origin_stage in order else ri

        # Every rung whose median produced this row's claim — position AND cost.
        path = order[min(oi, ri): max(ri, gi) + 1] if oi >= 0 and ri >= 0 else []
        unpriced = sorted({k for k in path if vel.get(k, {}).get("evidence") != "measured"})

        expected = 0.0
        for k in order[oi:ri] if (oi >= 0 and ri >= 0) else []:
            v = vel.get(k, {}).get("days")
            if v:
                expected += float(v)
        entered = _d(deal.get("stageSince")) or origin_date
        actual = max(0, (entered - origin_date).days)
        behind = round(actual - expected)

        amount = deal_amount(deal)
        raw_gap = amount * (STAGE_P.get(ghost_stage, 0) - STAGE_P.get(stage, 0)) / 100.0
        priced = not unpriced and amount > 0
        basis = "measured" if not unpriced else ("policy" if len(unpriced) == len(path) else "mixed")
        if priced:
            total_gap += max(0.0, raw_gap)
        else:
            unpriced_n += 1
            if amount > 0:
                policy_gap += max(0.0, raw_gap)
        co = next((c for c in data.get("companies", []) or [] if c.get("id") == deal.get("companyId")), {})
        rows.append({
            "id": deal["id"], "company": co.get("name") or deal.get("name"), "useCase": deal.get("useCase") or "",
            "amount": amount, "real": stage, "ghost": ghost_stage,
            "rungsBehind": max(0, gi - ri), "rungsAhead": max(0, ri - gi),
            "daysBehind": behind, "ghostDwell": ghost_dwell,
            "originStage": origin_stage, "originDate": origin_date.isoformat(),
            "leftCensored": censored,
            "priced": priced, "basis": basis,
            "evGap": round(raw_gap) if priced else None,
            "evGapProvisional": round(raw_gap),
            "unpricedRungs": unpriced,
            "explain": (
                f"first on the ladder at {origin_stage} on {origin_date.isoformat()}; your own median takes "
                f"{round(expected)}d to reach {stage}, this took {actual}d"
                if priced else
                f"first on the ladder at {origin_stage} on {origin_date.isoformat()}; "
                + ("no priced value on the deal — position shown, cost not claimed" if amount <= 0 else
                   "its path crosses rung(s) with no measured median (" + ", ".join(unpriced) +
                   ") — position shown on placeholder velocity, cost not claimed")),
        })
    rows.sort(key=lambda r: (-(r["evGap"] or 0), -r["daysBehind"]))

    out = {
        "_stamp": stamp,
        "generated": today.isoformat(),
        "revisions": len(snaps),
        "spanFrom": snaps[0]["date"] if snaps else None,
        "spanTo": snaps[-1]["date"] if snaps else None,
        "legacyRemapped": remapped,
        "order": order,
        "stageLabels": {s["key"]: s["label"] for s in data.get("stages", [])},
        "velocity": vel,
        "measuredRungs": measured_rungs,
        "totalRungs": len(order),
        "timeline": snaps,
        "dealIndex": index,
        "ghost": rows,
        "totalEvGap": round(total_gap),
        "totalEvGapPolicy": round(policy_gap),
        "unpricedDeals": unpriced_n,
        "honesty": ("Velocity is measured only where this pipeline has produced at least "
                    f"{MIN_OBS} completed stage occupancies. {measured_rungs} of {len(order)} rungs are measured; "
                    "the rest fall back to the declared staleDays and are labelled. A deal whose path crosses any "
                    "unmeasured rung gets a ghost POSITION but no dollar figure — the cost is left unclaimed rather "
                    f"than invented, and it does not enter the total. {unpriced_n} deal(s) are in that state today."),
    }
    try:
        tmp = CACHE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(out, f)
        os.replace(tmp, CACHE)
    except Exception:
        pass
    return out


def main():
    r = compute(fresh="--fresh" in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2))
        return
    if r.get("unavailable"):
        print("Ghost — unavailable here.\n  " + r["reason"])
        return
    print(f"Ghost pipeline — {r['revisions']} board states, {r['spanFrom']} → {r['spanTo']}")
    print(f"  legacy stage keys remapped: {r['legacyRemapped']} observation(s)\n")
    print("Your measured velocity (median days in stage):")
    for k in r["order"]:
        v = r["velocity"][k]
        if v["evidence"] == "measured":
            print(f"  {k:<13} {v['days']:>6}d   n={v['n']}")
        else:
            print(f"  {k:<13} {'—':>6}    {v['note']}")
    print(f"\nCounterfactual — where {len(r['ghost'])} in-motion deal(s) would be today:")
    for g in r["ghost"]:
        cost = (f"EV gap ${g['evGap']:,} (measured)" if g["priced"]
                else f"EV gap ${g['evGapProvisional']:,} ({g['basis']} velocity — not measured)")
        flag = "" if not g["unpricedRungs"] else "  [unmeasured: " + ",".join(g["unpricedRungs"]) + "]"
        print(f"  {g['company'][:28]:<28} real={g['real']:<12} ghost={g['ghost']:<12} "
              f"{g['rungsBehind']} rung(s) behind, {g['daysBehind']:+}d, {cost}{flag}")
    print(f"\nTotal EV not on the board today: ${r['totalEvGap']:,} measured "
          f"+ ${r['totalEvGapPolicy']:,} on ladder policy ({r['unpricedDeals']} deal(s) not yet measured)")
    print(f"\n{r['honesty']}")


if __name__ == "__main__":
    main()
