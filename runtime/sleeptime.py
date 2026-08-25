#!/usr/bin/env python3
"""Sleep-time compute — use the idle box, without spending a token to do it.

The VPS runs ~20 loops on timers and is otherwise idle. Letta's insight is that idle time is
capacity: an agent can reorganise its own memory between tasks. yourco's version is deliberately
narrower and cheaper — **all of it is file work, none of it calls a model.**

  digest   every `learnings/<domain>/` gets a compact digest of its recent entries. Each loop
           reads its domain at Step 0 (the loop contract); today that means re-reading whole
           files every run. A digest turns that into one short read.
  bloat    report domains that have grown past the point where a Step 0 read is cheap. Reports
           only — it never deletes or rewrites a learning. Compression is a judgement call and
           this process does not make judgement calls.
  prewarm  build the expensive dashboard payloads once so the morning surfaces are instant.

WHY IT SHIPS DISARMED, AND STAYS THAT WAY UNTIL SOMEONE DECIDES OTHERWISE
The runtime has gone dark on billing three times (`learnings/ops/2026-06-18_runtime-silent-credit-
death.md`, and the Board is carrying occurrence #3 right now). Adding scheduled work to a box with
an unreliable liveness story is backwards, so:

  1. **ARMED is False.** Without `--arm` (or YOURCO_SLEEPTIME=1) it plans and writes nothing.
  2. **The health gate runs first, every time.** If the runtime looks dark or the loops are stale,
     it refuses — even when armed. A process that quietly does extra work on a sick box is how a
     small problem becomes an invisible one.
  3. **Model-free.** No token is spent, so a runaway schedule cannot produce a bill. If model work
     is ever wanted here it must be a separate, separately-armed thing.

  python3 runtime/sleeptime.py              # dry plan — always safe
  python3 runtime/sleeptime.py --health     # just the gate
  python3 runtime/sleeptime.py --arm        # actually do the work (still gated on health)
"""
import os, re, sys, json, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

ARMED_DEFAULT = False
DIGEST_DIR = "learnings/_digests"
DIGEST_ENTRIES = 5          # what the loop contract asks each run to read
BLOAT_KB = 60               # a domain past this makes a Step 0 read expensive
DARK_DAYS = 3               # no loop artifact anywhere in this many days = the box looks dark
STALE_FRACTION = 0.5        # more than half the tracked loops stale = not healthy


def _read(rel):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def health(today=None):
    """The gate. Returns {ok, reasons[], facts{}} — and `ok` False means do nothing at all."""
    today = today or datetime.date.today()
    reasons, facts = [], {}
    try:
        import refresh
        d = refresh.derive(today)
        ls = d.get("loopSummary") or {}
        facts["loops"] = ls
        tracked = ls.get("tracked") or 0
        stale = (ls.get("stale") or 0) + (ls.get("neverRan") or 0)
        if tracked and stale / tracked > STALE_FRACTION:
            reasons.append(f"{stale} of {tracked} tracked loops are stale or never-run — the "
                           f"runtime is not keeping cadence, so it is in no state for extra work")
        newest = max((l.get("lastArtifact") or "" for l in (d.get("loops") or [])), default="")
        facts["newestArtifact"] = newest or None
        if newest:
            age = (today - datetime.date.fromisoformat(newest)).days
            facts["daysSinceAnyArtifact"] = age
            if age > DARK_DAYS:
                reasons.append(f"no loop has produced an artifact in {age} days — the box looks "
                               f"dark, which is the exact condition that must not be papered over")
        else:
            reasons.append("no loop artifacts at all — cannot establish that the runtime is alive")
    except Exception as e:
        reasons.append(f"could not read runtime health ({type(e).__name__}) — refusing to run "
                       f"blind")

    # billing: the failure mode that actually happened, three times
    cost = None
    try:
        with open(os.path.join(ROOT, "loops", "_anthropic", "latest.json"), encoding="utf-8") as f:
            cost = json.load(f)
    except (OSError, ValueError):
        pass
    if cost and cost.get("connected") and not cost.get("error"):
        facts["cost7d"] = cost.get("cost7d")
        if (cost.get("cost7d") or 0) == 0:
            reasons.append("7-day model spend is $0 — either nothing ran or the account is dead; "
                           "both mean this is the wrong moment to schedule more work")
    else:
        facts["cost7d"] = "unknown (Admin API not wired or stale)"

    return {"ok": not reasons, "reasons": reasons, "facts": facts,
            "note": "The gate runs before any work, armed or not. Refusing is the correct outcome "
                    "on an unhealthy box — this process exists to use spare capacity, never to "
                    "add load to a system that is already failing."}


# ---- the work (all file-only) ----------------------------------------------
def _domains():
    d = os.path.join(ROOT, "learnings")
    out = []
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, name)
        if not os.path.isdir(p) or name.startswith("_"):
            continue
        files = sorted(f for f in os.listdir(p) if f.endswith(".md") and not f.startswith("_"))
        size = sum(os.path.getsize(os.path.join(p, f)) for f in files) if files else 0
        out.append({"domain": name, "files": files, "count": len(files), "bytes": size})
    return out


def _first_line(rel):
    for line in (_read(rel) or "").splitlines():
        s = line.strip().lstrip("# ").strip()
        if s:
            return s[:160]
    return ""


def plan(today=None):
    doms = _domains()
    digests = [{"domain": d["domain"], "entries": min(DIGEST_ENTRIES, d["count"]),
                "writes": f"{DIGEST_DIR}/{d['domain']}.md"} for d in doms if d["count"]]
    bloat = [{"domain": d["domain"], "kb": round(d["bytes"] / 1024), "files": d["count"]}
             for d in doms if d["bytes"] > BLOAT_KB * 1024]
    return {"digests": digests, "bloat": bloat, "domains": len(doms),
            "prewarm": ["dashboard/board.build", "dashboard/clients.build", "dashboard/trust.build"]}


def do_digests(today=None):
    written = []
    out_dir = os.path.join(ROOT, DIGEST_DIR)
    os.makedirs(out_dir, exist_ok=True)
    for d in _domains():
        if not d["count"]:
            continue
        recent = d["files"][-DIGEST_ENTRIES:]
        lines = [f"# {d['domain']} — Step 0 digest", "",
                 f"> Generated by `runtime/sleeptime.py` on {datetime.date.today().isoformat()}. "
                 f"The {len(recent)} most recent of {d['count']} entries, newest last. This is a "
                 f"POINTER LIST, not a replacement — if one of these bears on your run, open the "
                 f"file. Never cite a digest line as the learning itself.", ""]
        for f in recent:
            summary = _first_line("learnings/" + d["domain"] + "/" + f)
            lines.append("- **" + f[:-3] + "** — " + summary)
        lines.append("")
        lines.append(f"*Full domain: `learnings/{d['domain']}/` ({d['count']} entries, "
                     f"{round(d['bytes']/1024)}KB).*")
        p = os.path.join(out_dir, f"{d['domain']}.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        written.append(f"{DIGEST_DIR}/{d['domain']}.md")
    return written


def do_prewarm():
    done, failed = [], []
    for mod, fn in (("board", "build"), ("clients", "build"), ("trust", "build")):
        try:
            m = __import__(mod)
            getattr(m, fn)()
            done.append(f"{mod}.{fn}")
        except Exception as e:
            failed.append(f"{mod}.{fn}: {type(e).__name__}")
    return {"warmed": done, "failed": failed}


def run(armed=False):
    h = health()
    p = plan()
    if not armed:
        return {"ran": False, "armed": False, "health": h, "plan": p,
                "why": "disarmed — this is a dry plan. Pass --arm to do the work."}
    if not h["ok"]:
        return {"ran": False, "armed": True, "health": h, "plan": p,
                "why": "REFUSED by the health gate: " + "; ".join(h["reasons"])}
    return {"ran": True, "armed": True, "health": h, "plan": p,
            "digests": do_digests(), "prewarm": do_prewarm(),
            "bloatReported": p["bloat"],
            "why": "healthy and armed — file work only, no model calls"}


def build():
    """HQ payload."""
    h = health()
    p = plan()
    return {"generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "armedByDefault": ARMED_DEFAULT, "health": h, "plan": p,
            "note": "Ships disarmed and gated. Model-free by design: no token is spent here, so "
                    "a scheduling mistake cannot produce a bill."}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="yourco sleep-time compute")
    ap.add_argument("--arm", action="store_true")
    ap.add_argument("--health", action="store_true")
    a = ap.parse_args()
    if a.health:
        h = health()
        print(("HEALTHY — safe to run" if h["ok"] else "NOT HEALTHY — would refuse"))
        for r in h["reasons"]:
            print("  ! " + r)
        print("  facts:", json.dumps(h["facts"], default=str))
        sys.exit(0 if h["ok"] else 1)
    armed = a.arm or os.environ.get("YOURCO_SLEEPTIME") == "1"
    r = run(armed)
    print(f"sleep-time compute — armed={r['armed']} ran={r['ran']}")
    print("  " + r["why"])
    if not r["health"]["ok"]:
        for x in r["health"]["reasons"]:
            print("  ! " + x)
    pl = r["plan"]
    print(f"  would write {len(pl['digests'])} digest(s) across {pl['domains']} domains; "
          f"{len(pl['bloat'])} domain(s) over {BLOAT_KB}KB")
    if r.get("digests"):
        print(f"  wrote: {len(r['digests'])} digests · prewarm {r['prewarm']}")
