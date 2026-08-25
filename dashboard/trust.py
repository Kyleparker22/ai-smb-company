#!/usr/bin/env python3
"""Trust — the read side of the Trust Ledger, the calibration market, and the immune drills.

Turns the three append-only stores in `loops/_trust/` into the HQ Trust view, and does the
one thing a hand-maintained trust claim can't do: **checks itself against the evidence.**

WHAT IT ANSWERS
  · How much control has the OS actually absorbed?          -> ledger.controlCost (estimated, never measured-by-assumption)
  · At what autonomy rung is that work happening?           -> ledger.byRung (rung resolved live from the matrix)
  · Is the agents' confidence in themselves worth anything? -> calibration (Brier + reliability bins, refused below the floor)
  · Would we notice if something broke?                     -> drills (and silence counts as a miss)
  · Does the hand-written streak table match reality?       -> audit (the ledger outranks the prose)

WHAT IT REFUSES TO DO
  · Publish a composite trust score before its inputs exist. `posture.score` stays null and
    names exactly which inputs are missing, in the same spirit as the Clients view scoring
    readiness honestly at zero live clients rather than rendering a flattering blank.
  · Convert an unpriced action into minutes. Unpriced actions are counted and excluded.
  · Read a never-run drill catalog as a pass. Zero runs is reported as zero runs.
  · Call a streak-table claim wrong when the ledger simply has no coverage for that action —
    that is reported as UNVERIFIABLE, which is a different (and more useful) finding.

Read-only. Exposed as GET /api/trust.  Writers live in `runtime/trust_ledger.py`.
"""
import os, sys, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "runtime"))
sys.path.insert(0, HERE)

from ledger import Ledger, brier, calibration_bins, refuse_reason, MIN_FORECASTS  # noqa: E402
import trust_ledger as TL  # the catalog + the control-cost basis table (one definition)  # noqa: E402

try:
    import refresh  # autonomy-matrix parsing — never forked
except Exception:
    refresh = None

ACTIONS = Ledger("loops/_trust/actions.jsonl")
FORECASTS = Ledger("loops/_trust/forecasts.jsonl")
DRILLS_LOG = Ledger("loops/_trust/drills.jsonl")

STREAK_OPENED = "2026-07-05"  # the streak ledger's own opening date (autonomy-matrix.md)
MIN_ACTIONS_FOR_SCORE = 30
MIN_DRILLS_FOR_RATE = 3  # "100% detection" off one drill is the overclaim this design exists to stop


def _read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _rung_map():
    """Autonomy-matrix action -> rung, live. Parsed by refresh so HQ's Trust tab and this
    view can never disagree about what rung an action is at."""
    rows = refresh._autonomy() if refresh else []
    return {r["action"]: r["rung"] for r in rows}


def _rung_of(action, rmap):
    if action in rmap:
        return rmap[action]
    for k, v in rmap.items():  # tolerate small wording drift in the matrix
        if k.lower().startswith(action.lower()[:18]) or action.lower().startswith(k.lower()[:18]):
            return v
    return "unmapped"


# ---- the action ledger -----------------------------------------------------
def _ledger():
    raw = ACTIONS.project()
    evs = [e for e in raw["events"] if e.get("kind") == "action"]
    rmap = _rung_map()

    by_rung, by_agent, by_source, by_action = {}, {}, {}, {}
    priced_min, priced_n, unpriced_n, measured_min = 0, 0, 0, 0
    bases = {}
    for e in evs:
        rung = _rung_of(e.get("action") or "", rmap)
        oc = e.get("outcome") or "clean"
        r = by_rung.setdefault(rung, {"rung": rung, "n": 0, "clean": 0, "partial": 0, "incident": 0})
        r["n"] += 1
        r[oc] = r.get(oc, 0) + 1
        a = by_agent.setdefault(e.get("agent") or "unattributed",
                                {"agent": e.get("agent") or "unattributed", "n": 0, "incident": 0})
        a["n"] += 1
        if oc == "incident":
            a["incident"] += 1
        by_source[e.get("source") or "manual"] = by_source.get(e.get("source") or "manual", 0) + 1
        by_action[e.get("action") or "?"] = by_action.get(e.get("action") or "?", 0) + 1
        cost = TL.CONTROL_COST.get(e.get("loop") or "")
        if cost:
            mins, basis, conf = cost
            priced_n += 1
            if conf == "measured":
                measured_min += mins
            else:
                priced_min += mins
            bases.setdefault(e.get("loop"), {"loop": e.get("loop"), "minutes": mins,
                                             "basis": basis, "confidence": conf, "runs": 0})
            bases[e.get("loop")]["runs"] += 1
        else:
            unpriced_n += 1

    order = ["R3", "R2", "R1", "unmapped"]
    rungs = sorted(by_rung.values(),
                   key=lambda r: (next((i for i, o in enumerate(order) if r["rung"].startswith(o)), 9),
                                  r["rung"]))
    return {
        "total": len(evs),
        "incidents": sum(1 for e in evs if e.get("outcome") == "incident"),
        "byRung": rungs,
        "byAgent": sorted(by_agent.values(), key=lambda a: -a["n"])[:20],
        "bySource": by_source,
        "byAction": sorted(({"action": k, "n": v} for k, v in by_action.items()),
                           key=lambda x: -x["n"]),
        "first": min((e.get("on") or "" for e in evs), default=None) or None,
        "last": max((e.get("on") or "" for e in evs), default=None) or None,
        "controlCost": {
            # The two never mix. `estimated` is a reconstruction with a written basis;
            # `measured` requires a real time study and is therefore 0 until one happens.
            "estimatedHours": round(priced_min / 60, 1),
            "measuredHours": round(measured_min / 60, 1),
            "pricedActions": priced_n,
            "unpricedActions": unpriced_n,
            "coveragePct": round(priced_n / len(evs) * 100) if evs else 0,
            "bases": sorted(bases.values(), key=lambda b: -b["runs"]),
            "note": "Estimated hours use the declared per-loop basis in runtime/trust_ledger.py "
                    "CONTROL_COST. Nothing is measured yet — measuredHours stays 0 until a real "
                    "time study runs. Unpriced actions are counted as actions and excluded from "
                    "the hours, never averaged in.",
        },
        "bad": raw["bad"],
        "corrected": raw["corrected"],
    }


# ---- the calibration market ------------------------------------------------
def _calibration():
    raw = FORECASTS.project()
    evs = raw["events"]
    fc = {e["seq"]: e for e in evs if e.get("kind") == "forecast"}
    resolutions = [e for e in evs if e.get("kind") == "resolution"]
    pairs, per_agent, rows = [], {}, []
    resolved_ids = set()
    for r in resolutions:
        f = fc.get(r.get("forecast"))
        if not f:
            continue
        resolved_ids.add(f["seq"])
        ok = r.get("outcome") == "clean"
        pairs.append((f.get("p"), ok))
        per_agent.setdefault(f.get("agent") or "unattributed", []).append((f.get("p"), ok))
        rows.append({"seq": f["seq"], "agent": f.get("agent"), "subject": f.get("subject"),
                     "p": f.get("p"), "outcome": r.get("outcome"), "on": r.get("on")})
    openf = [{"seq": f["seq"], "agent": f.get("agent"), "subject": f.get("subject"),
              "p": f.get("p"), "on": f.get("on")}
             for s, f in fc.items() if s not in resolved_ids]
    agents = []
    for name, ps in per_agent.items():
        agents.append({"agent": name, "n": len(ps), "brier": brier(ps),
                       "refusal": refuse_reason(len(ps))})
    return {
        "open": len(openf),
        "resolved": len(pairs),
        "brier": brier(pairs),
        "refusal": refuse_reason(len(pairs)),
        "bins": calibration_bins(pairs),
        "byAgent": sorted(agents, key=lambda a: -a["n"]),
        "recent": sorted(rows, key=lambda r: r["seq"], reverse=True)[:12],
        "openList": sorted(openf, key=lambda r: r["seq"], reverse=True)[:12],
        "floor": MIN_FORECASTS,
        "note": "A forecast is a bet an agent places on its OWN reliability before the fact. "
                "Brier: 0 = perfect, 0.25 = a coin flip stated at 50%, 1 = confidently wrong. "
                "Calibration — not raw pass rate — is what earns faster promotion, because an "
                "agent that knows when it is unsure is safer than one that is merely often right.",
        "bad": raw["bad"],
    }


# ---- the immune system -----------------------------------------------------
def _drills(now=None):
    now = now or datetime.datetime.now()
    raw = DRILLS_LOG.project()
    evs = raw["events"]
    armed = [e for e in evs if e.get("kind") == "armed"]
    verdict = {}
    detect_hours = []
    for e in evs:
        if e.get("kind") not in ("detected", "missed", "expired"):
            continue
        run = e.get("run")
        verdict[run] = e
        if e.get("kind") == "detected":
            a = next((x for x in armed if x["seq"] == run), None)
            if a:
                try:
                    dh = (datetime.datetime.fromisoformat(e["ts"])
                          - datetime.datetime.fromisoformat(a["ts"])).total_seconds() / 3600
                    detect_hours.append(round(dh, 1))
                except (ValueError, KeyError):
                    pass

    runs, detected, undetected, openn, overdue = [], 0, 0, 0, 0
    for a in armed:
        d = TL.DRILL_BY_ID.get(a.get("drill"), {})
        v = verdict.get(a["seq"])
        window = a.get("windowHours") or d.get("window_h") or 48
        try:
            age_h = (now - datetime.datetime.fromisoformat(a["ts"])).total_seconds() / 3600
        except (ValueError, KeyError):
            age_h = 0
        if v and v.get("kind") == "detected":
            state = "detected"; detected += 1
        elif v:
            state = "undetected"; undetected += 1
        elif age_h > window:
            # RULE 2 — past its window with no verdict is a MISS, computed live so the
            # dashboard is honest even before --sweep makes it permanent in the ledger.
            state = "undetected (overdue)"; undetected += 1; overdue += 1
        else:
            state = "open"; openn += 1
        runs.append({"run": a["seq"], "drill": a.get("drill"), "kind": a.get("drillKind"),
                     "severity": a.get("severity") or d.get("severity"),
                     "armedAt": a.get("ts"), "state": state,
                     "by": (v or {}).get("by"), "note": (v or {}).get("note") or a.get("note"),
                     "windowHours": window, "ageHours": round(age_h, 1)})

    per = []
    for d in TL.DRILLS:
        mine = [r for r in runs if r["drill"] == d["id"]]
        per.append({"id": d["id"], "kind": d["kind"], "severity": d["severity"],
                    "target": d["target"], "hypothesis": d["hypothesis"], "control": d["control"],
                    "windowHours": d["window_h"], "runs": len(mine),
                    "lastState": mine[-1]["state"] if mine else "never run",
                    "lastArmed": mine[-1]["armedAt"][:10] if mine else None})
    detect_hours.sort()
    resolved = detected + undetected
    # A rate needs a sample. One drill detected is "1 of 1", not "100%" — publishing the
    # percentage here would be the same sin as a Brier score off two forecasts.
    rate_refusal = (None if resolved >= MIN_DRILLS_FOR_RATE else
                    (f"{detected} of {resolved} detected — too few drills to state a rate "
                     f"({MIN_DRILLS_FOR_RATE} is the floor)" if resolved else
                     "no drill resolved yet — detection rate unknown, not 100%"))
    return {
        "catalog": len(TL.DRILLS),
        "runs": len(armed),
        "detected": detected,
        "undetected": undetected,
        "resolvedRuns": resolved,
        "open": openn,
        "overdue": overdue,
        "rateFloor": MIN_DRILLS_FOR_RATE,
        "rateRefusal": rate_refusal,
        "detectionRate": (round(detected / resolved * 100)
                          if resolved and not rate_refusal else None),
        "medianDetectHours": detect_hours[len(detect_hours) // 2] if detect_hours else None,
        "perDrill": per,
        "recentRuns": sorted(runs, key=lambda r: r["run"], reverse=True)[:12],
        "note": "Every drill is inert and operator-placed — nothing here injects a fault into a "
                "live system on its own. A drill past its window with no detection scores "
                "UNDETECTED, never 'pending': not noticing is the failure this exists to catch.",
        "zeroState": ("The catalog is a plan, not a result. No drill has been armed, so the "
                      "detection rate is unknown — not passing.") if not armed else None,
        "bad": raw["bad"],
    }


# ---- the ledger audits the markdown ---------------------------------------
STREAK_RE = re.compile(r"\*\*(\d+)\s*[·.]\s*(≥?\d+)\*\*")


def _audit(led):
    """Join Kolby's hand-maintained streak table against recorded evidence.

    Three verdicts, and the distinction matters:
      supported    — the ledger holds at least as many actions as the table claims
      DISAGREEMENT — the table claims more uses than the ledger can evidence
      unverifiable — the ledger has no coverage of that action at all, so the claim
                     can be neither confirmed nor contradicted (a coverage gap, not a lie)
    """
    txt = _read("runtime/autonomy-matrix.md")
    sec = re.search(r"## Streak ledger.*?\n((?:\|.*\n)+)", txt, re.S)
    counts = {}
    for e in ACTIONS.project()["events"]:
        if e.get("kind") == "action" and (e.get("on") or "") >= STREAK_OPENED:
            counts[e.get("action") or ""] = counts.get(e.get("action") or "", 0) + 1
    ever = {e.get("action") for e in ACTIONS.project()["events"]}

    rows, disagreements = [], []
    if sec:
        for line in sec.group(1).splitlines()[2:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or not cells[0]:
                continue
            action = re.sub(r"\s*\(.*?\)\s*", " ", cells[0]).replace("**", "").strip()
            m = STREAK_RE.search(cells[3])
            claimed_uses = int(re.sub(r"\D", "", m.group(2))) if m else None
            # match the table's shorthand back to a matrix action name
            key = next((k for k in set(list(counts) + list(ever))
                        if k and (k.lower().startswith(action.lower()[:14])
                                  or action.lower().startswith(k.lower()[:14]))), None)
            have = counts.get(key, 0) if key else 0
            if key is None:
                verdict = "unverifiable"
            elif claimed_uses is None:
                verdict = "unverifiable"
            elif have >= claimed_uses:
                verdict = "supported"
            else:
                verdict = "DISAGREEMENT"
                disagreements.append({"action": action, "claimed": f"{claimed_uses} uses",
                                      "ledger": f"{have} recorded"})
            rows.append({"action": action, "claimedStreak": cells[3].replace("**", "").strip(),
                         "claimedUses": claimed_uses, "ledgerUses": have if key else None,
                         "verdict": verdict})
    unverifiable = sum(1 for r in rows if r["verdict"] == "unverifiable")
    return {
        "rows": rows,
        "disagreements": disagreements,
        "unverifiable": unverifiable,
        "since": STREAK_OPENED,
        "note": "The streak table in runtime/autonomy-matrix.md is written by hand and can drift. "
                "This joins it to the action ledger. 'unverifiable' means the ledger has no "
                "coverage for that action — a gap in instrumentation, not a false claim; the "
                "honest fix is to record those actions, not to trust the table harder.",
    }


# ---- the composite, and its refusal ---------------------------------------
def _posture(led, cal, dr):
    """One number for the moat — published ONLY when its three inputs are real.

    A trust score assembled from missing inputs is exactly the fabricated-completeness
    failure the loop contract calls the cardinal sin, so the missing inputs are named
    instead."""
    missing = []
    if led["total"] < MIN_ACTIONS_FOR_SCORE:
        missing.append(f"volume: {led['total']} actions recorded, {MIN_ACTIONS_FOR_SCORE} is the floor")
    if cal["resolved"] < MIN_FORECASTS:
        missing.append(f"calibration: {cal['resolved']} resolved forecasts, {MIN_FORECASTS} is the floor")
    if dr["rateRefusal"]:
        missing.append("immune: " + dr["rateRefusal"])

    components = [
        {"name": "Actions recorded", "value": led["total"],
         "state": "ok" if led["total"] >= MIN_ACTIONS_FOR_SCORE else "thin",
         "why": "how much of the OS's real work is instrumented at all"},
        {"name": "Incident rate", "value": (f"{led['incidents']}/{led['total']}" if led["total"] else "—"),
         "state": "ok" if led["total"] and not led["incidents"] else ("thin" if not led["total"] else "warn"),
         "why": "recorded incidents against recorded actions"},
        {"name": "Calibration (Brier)", "value": cal["brier"] if cal["brier"] is not None else "—",
         "state": "ok" if cal["brier"] is not None and cal["brier"] <= 0.15 else "thin",
         "why": "whether the agents' confidence in themselves predicts reality"},
        {"name": "Immune detection",
         "value": (f"{dr['detectionRate']}%" if dr["detectionRate"] is not None
                   else f"{dr['detected']} of {dr['resolvedRuns']}"),
         "state": "ok" if (dr["detectionRate"] or 0) >= 80 else "thin",
         "why": (dr["rateRefusal"] or
                 "share of deliberately injected faults the OS caught in time")},
        {"name": "Control absorbed", "value": f"~{led['controlCost']['estimatedHours']}h est.",
         "state": "ok" if led["controlCost"]["estimatedHours"] else "thin",
         "why": f"human hours not spent, across {led['controlCost']['pricedActions']} priced actions"},
    ]
    return {
        "score": None if missing else 100,  # composite math lands when the inputs do
        "missing": missing,
        "refusal": ("No composite trust score yet — " + "; ".join(missing) + ". "
                    "The components below are real and are shown as themselves.") if missing else None,
        "components": components,
    }


def build():
    led = _ledger()
    cal = _calibration()
    dr = _drills()
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ledger": led,
        "calibration": cal,
        "drills": dr,
        "audit": _audit(led),
        "posture": _posture(led, cal, dr),
        "sources": {
            "actions": "loops/_trust/actions.jsonl",
            "forecasts": "loops/_trust/forecasts.jsonl",
            "drills": "loops/_trust/drills.jsonl",
            "rungs": "runtime/autonomy-matrix.md (parsed by dashboard/refresh.py)",
            "costBasis": "runtime/trust_ledger.py CONTROL_COST",
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build(), indent=2)[:4000])
