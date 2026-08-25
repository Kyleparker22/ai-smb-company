#!/usr/bin/env python3
"""HQ usage — the two views that need HQ to remember it was looked at.

**N2 · what changed since you last looked.** Dashboards render state; the question a returning
founder actually has is *what moved*. Because every HQ payload is derived, it is also
fingerprintable — so HQ can store a snapshot per visit and compute a true cross-company delta
rather than a changelog somebody writes.

**N1 · the panel-usefulness audit.** HQ has 65 panels and one reader. Every dashboard product adds
panels; none tells you which of its own are dead weight. Two facts settle it — *was this opened*
and *did anything on it change* — and both are now recorded. A panel that is never opened and never
changes is proposed for removal, with the evidence, using the same verdict shape as agent
retirement. It is the only feature in HQ that argues for making HQ smaller.

WHAT IS AND ISN'T RECORDED
Visits are door-level, appended to `loops/_hq/visits.jsonl` — no timing, no mouse, no content, and
one user. Snapshots store **fingerprints** (counts and hashes), never payload bodies: a snapshot
file that accumulated whole CRM payloads would be a slow-growing copy of the company in a log.

HONESTY RULES
- **A never-opened panel is not automatically dead.** It may be new, or it may be the one nobody
  looks at *because nothing is wrong*. Verdicts distinguish `never opened` from `opened, never
  changed`, and neither is a delete instruction — this proposes, like everything else here.
- **No baseline, no delta.** On a first visit there is nothing to diff and the view says so rather
  than presenting today's state as if it were news.
- **Silence is reported.** "Nothing changed since Monday" is a real, useful answer and renders as
  one.
"""
import os, sys, json, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "runtime"))

from ledger import Ledger  # noqa: E402

VISITS = Ledger("loops/_hq/visits.jsonl")
SNAPS = Ledger("loops/_hq/snapshots.jsonl")

STALE_PANEL_DAYS = 30      # never opened in this long, and never changing -> propose removal
MIN_SNAPSHOTS = 2          # below this there is no delta to compute, and we say so

# The sample floor for a REMOVAL verdict. Without it the audit proposed deleting 19 of 26 panels
# off two snapshots taken seconds apart — the same mistake the agent-retirement pass made, and
# the same fix: a confident verdict needs enough evidence to be worth anything. Until both are
# met every panel reads `warming up` and nothing is proposed.
MIN_DAYS_RECORDING = 14
MIN_VISITS = 10

# Door -> the panels it contains. Kept here rather than parsed out of index.html: the audit must
# survive a UI refactor, and a panel that disappears from the map is itself worth noticing.
DOORS = {
    "today": ["overview", "goals"],
    "board": ["board"],
    "clients": ["clients"],
    "partners": ["governance", "lockin", "advocate", "partnerwork"],
    "commercial": ["pipeline", "finance", "delivery", "scale"],
    "system": ["loops", "trust", "compliance", "reports"],
    "evidence": ["trustledger", "tripwires", "timemachine", "twin", "vacancies"],
    "wbr": ["wbr", "prosecution", "whatchanged", "panelaudit"],
    "agents": ["agents"],
}
PANEL_DOOR = {p: d for d, ps in DOORS.items() for p in ps}


# ---- fingerprints ----------------------------------------------------------
def _h(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:12]


def fingerprint():
    """A small, comparable summary of the whole company. Counts and hashes only."""
    fp, errs = {}, {}

    def grab(name, fn):
        try:
            fp[name] = fn()
        except Exception as e:
            errs[name] = f"{type(e).__name__}: {e}"[:120]

    def _board():
        import board
        b = board.build()
        c = b.get("counts", {}).get("byState", {})
        return {"needsYou": c.get("needs-you", 0), "blocked": c.get("blocked", 0),
                "missing": c.get("missing", 0), "total": len(b.get("items") or []),
                "owners": b.get("counts", {}).get("byOwner", {})}

    def _goals():
        import server
        g = server.goals_currents()
        return {k: v for k, v in g.items() if not k.startswith("_")}

    def _lockin():
        import lockin
        d = lockin.build()
        return {"locked": d.get("lockedConfirmed"), "counts": d.get("counts"),
                "session": d.get("sessionsDone")}

    def _trip():
        import tripwires
        d = tripwires.build()
        return {"fired": len(d.get("fired") or []), "covered": d.get("covered")}

    def _trust():
        import trust
        d = trust.build()
        return {"actions": d["ledger"]["total"], "incidents": d["ledger"]["incidents"],
                "drills": d["drills"]["runs"], "undetected": d["drills"]["undetected"]}

    def _vac():
        import vacancies
        d = vacancies.build()
        return {"clusters": d["counts"], "retire": d["retire"]["counts"]}

    def _loops():
        import refresh
        return (refresh.derive().get("loopSummary") or {})

    for n, f in (("board", _board), ("goals", _goals), ("lockin", _lockin),
                 ("tripwires", _trip), ("trust", _trust), ("vacancies", _vac), ("loops", _loops)):
        grab(n, f)
    return {"parts": fp, "errors": errs, "hash": _h(fp)}


def record_visit(door, panels=None):
    """One door opened. Also snapshots the company, so the next visit has a baseline."""
    door = str(door or "")[:40]
    ev = VISITS.append("visit", door=door, panels=[str(p)[:40] for p in (panels or [])][:40],
                       on=datetime.date.today().isoformat())
    fp = fingerprint()
    SNAPS.append("snapshot", hash=fp["hash"], parts=fp["parts"], errors=fp["errors"],
                 visit=ev["seq"], on=datetime.date.today().isoformat())
    return ev


# ---- N2: what changed -------------------------------------------------------
def _diff(old, new, path=""):
    out = []
    if isinstance(old, dict) and isinstance(new, dict):
        for k in sorted(set(old) | set(new)):
            out += _diff(old.get(k), new.get(k), f"{path}.{k}" if path else k)
    elif old != new:
        out.append({"path": path, "from": old, "to": new,
                    "delta": (new - old) if isinstance(old, (int, float))
                             and isinstance(new, (int, float))
                             and not isinstance(old, bool) and not isinstance(new, bool) else None})
    return out


READABLE = {
    "board.needsYou": "items needing a human", "board.blocked": "blocked items",
    "board.missing": "missing things", "board.total": "open items",
    "goals.mrr": "MRR", "goals.liveClients": "live clients",
    "goals.dealsInMotion": "deals in motion", "goals.activeConnectors": "active connectors",
    "lockin.locked": "lock-in domains locked", "lockin.session": "lock-in sessions elapsed",
    "tripwires.fired": "trip-wires fired", "tripwires.covered": "decisions with a trip-wire",
    "trust.actions": "recorded agent actions", "trust.incidents": "recorded incidents",
    "trust.drills": "immune drills run", "trust.undetected": "undetected drills",
    "loops.stale": "stale loops", "loops.onTime": "on-time loops",
}


def what_changed():
    snaps = [e for e in SNAPS.read()["events"] if e.get("kind") == "snapshot"]
    if len(snaps) < MIN_SNAPSHOTS:
        return {"available": False,
                "reason": (f"{len(snaps)} snapshot(s) recorded — a delta needs at least "
                           f"{MIN_SNAPSHOTS}. HQ is recording from now on; there is nothing to "
                           f"compare against yet, and today's state is not news."),
                "snapshots": len(snaps)}
    prev, curr = snaps[-2], snaps[-1]
    rows = _diff(prev.get("parts") or {}, curr.get("parts") or {})
    for r in rows:
        r["label"] = READABLE.get(r["path"], r["path"])
        r["door"] = r["path"].split(".")[0]
    rows.sort(key=lambda r: (0 if r["path"] in READABLE else 1, r["path"]))
    return {
        "available": True,
        "since": prev.get("ts"), "until": curr.get("ts"),
        "changes": rows,
        "count": len(rows),
        "quiet": not rows,
        "quietNote": ("Nothing changed since you last looked. That is a real answer, and on a "
                      "company this size it is often the correct one.") if not rows else None,
        "snapshots": len(snaps),
        "note": "A computed delta of every derived payload against the snapshot taken at your "
                "last visit — not a changelog anybody writes.",
    }


# ---- N1: panel usefulness ---------------------------------------------------
def panel_audit(today=None):
    today = today or datetime.date.today()
    visits = [e for e in VISITS.read()["events"] if e.get("kind") == "visit"]
    snaps = [e for e in SNAPS.read()["events"] if e.get("kind") == "snapshot"]

    opened, last_open = {}, {}
    for v in visits:
        for p in (v.get("panels") or []) or DOORS.get(v.get("door"), []):
            opened[p] = opened.get(p, 0) + 1
            last_open[p] = max(last_open.get(p, ""), (v.get("ts") or "")[:10])

    # which fingerprint parts have ever moved
    moved = set()
    for a, b in zip(snaps, snaps[1:]):
        for r in _diff(a.get("parts") or {}, b.get("parts") or {}):
            moved.add(r["path"].split(".")[0])

    # how long has HQ actually been recording?
    days = None
    if snaps:
        first = (snaps[0].get("ts") or "")[:10]
        try:
            days = (today - datetime.date.fromisoformat(first)).days
        except ValueError:
            pass
    warming = (len(snaps) < MIN_SNAPSHOTS or len(visits) < MIN_VISITS
               or (days or 0) < MIN_DAYS_RECORDING)
    warm_why = (f"warming up — {len(visits)}/{MIN_VISITS} visits and {days if days is not None else 0}"
                f"/{MIN_DAYS_RECORDING} days of recording. No panel is proposed for removal until "
                f"both floors are met; a verdict off two snapshots is worthless.")

    rows = []
    for door, panels in DOORS.items():
        for p in panels:
            n = opened.get(p, 0)
            lo = last_open.get(p)
            age = None
            if lo:
                try:
                    age = (today - datetime.date.fromisoformat(lo)).days
                except ValueError:
                    pass
            changes = door in moved or p in moved
            if warming:
                verdict, why = "warming up", warm_why
            elif n == 0 and not changes:
                verdict, why = ("propose removal",
                                "never opened and nothing on it has changed since recording began")
            elif n == 0:
                verdict, why = ("never opened",
                                "it changes, so it carries information — but nobody has looked")
            elif not changes:
                verdict, why = ("static",
                                "opened, but nothing on it has moved — may be a reference panel "
                                "rather than a monitor, which is fine and worth knowing")
            else:
                verdict, why = "earning its place", f"opened {n}x, and its data moves"
            rows.append({"panel": p, "door": door, "opens": n, "lastOpened": lo,
                         "daysSinceOpen": age, "dataMoves": changes,
                         "verdict": verdict, "why": why})
    order = {"propose removal": 0, "never opened": 1, "static": 2, "earning its place": 3,
             "warming up": 4, "unknown": 5}
    rows.sort(key=lambda r: (order.get(r["verdict"], 9), r["door"], r["panel"]))
    return {
        "rows": rows, "panels": len(rows), "doors": len(DOORS),
        "counts": {k: sum(1 for r in rows if r["verdict"] == k) for k in order},
        "visits": len(visits), "snapshots": len(snaps), "daysRecording": days,
        "warmingUp": warming,
        "warmUpNote": warm_why if warming else None,
        "floors": {"visits": MIN_VISITS, "days": MIN_DAYS_RECORDING},
        "note": ("Two facts decide it: was the panel opened, and did anything on it change. "
                 "A never-opened panel is NOT automatically dead — it may be new, or it may be "
                 "the one nobody checks because nothing is wrong. Proposes only; deleting a panel "
                 "is a decision, like retiring an agent."),
    }


def build():
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "whatChanged": what_changed(),
        "panelAudit": panel_audit(),
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--visit", help="record a visit to a door (for testing)")
    a = ap.parse_args()
    if a.visit:
        print("recorded:", record_visit(a.visit))
    d = build()
    w, p = d["whatChanged"], d["panelAudit"]
    print("WHAT CHANGED — " + (w.get("reason") or
                               (w.get("quietNote") or f"{w['count']} change(s) since {w['since']}")))
    for c in (w.get("changes") or [])[:12]:
        arrow = f"{c['from']} -> {c['to']}" + (f"  ({c['delta']:+})" if c.get("delta") else "")
        print(f"   {c['label']:<32} {arrow}")
    print(f"\nPANEL AUDIT — {p['panels']} panels across {p['doors']} doors · "
          f"{p['visits']} visit(s), {p['snapshots']} snapshot(s)")
    print("   " + " · ".join(f"{k} {v}" for k, v in p["counts"].items() if v))
    for r in p["rows"][:10]:
        print(f"   [{r['verdict']:<17}] {r['door']}/{r['panel']:<14} opens={r['opens']} "
              f"moves={r['dataMoves']}")
