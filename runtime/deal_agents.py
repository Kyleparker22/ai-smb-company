#!/usr/bin/env python3
"""Deal agents — the deterministic half of "one agent per deal."

Every deal on the ladder gets a standing micro-agent. This engine runs the parts
that need no LLM: staleness watch, artifact-engagement (heat) rollup, exit-criteria
nag, and the escalation queue. The LLM half (drafting the actual touch, the call
brief from Granola history) runs via runtime/prompts/deal-agent.md on the runtime,
reading the escalation queue this engine writes.

Run:  python3 runtime/deal_agents.py            (safe: writes agentLog + escalations only)
      python3 runtime/deal_agents.py --dry      (print, write nothing)

Writes, under the repo lock:
  - crm/data.json  → deals[].agentLog (append, capped at 12), deals[].heatNote
  - crm/_agent-escalations.json → items the LLM loop (or a Cowork session) should draft for
Never touches: stage, nextAction, nextDraft (drafting is the LLM's job; moving stages is the Founder's).
"""
import json, os, sys, subprocess, datetime, fcntl

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "crm", "data.json")
TELEMETRY = os.path.join(REPO, "crm", "telemetry.jsonl")
ESCALATIONS = os.path.join(REPO, "crm", "_agent-escalations.json")
LOCK = os.path.join(REPO, "runtime", ".repo.lock")
TODAY = datetime.date.today().isoformat()
DRY = "--dry" in sys.argv

BENCH = {"parked", "pre-convo"}
LOG_CAP = 12


def heat_rollup():
    """path -> {views, minutes, last} from the beacon log."""
    rows = {}
    if not os.path.exists(TELEMETRY):
        return rows
    with open(TELEMETRY) as f:
        for line in f:
            try:
                ev = json.loads(line)
            except Exception:
                continue
            p = str(ev.get("p", "")).split("?")[0]
            r = rows.setdefault(p, {"views": 0, "beats": 0, "last": ""})
            r["views" if ev.get("e") == "view" else "beats"] += 1
            r["last"] = max(r["last"], str(ev.get("ts", ""))[:19])
    return rows


def deal_heat(deal, heat):
    v = m = 0
    last = ""
    for a in deal.get("artifacts", []):
        base = str(a.get("link", "")).split("?")[0]
        if not base:
            continue
        for p, r in heat.items():
            if p == base or (base.endswith("/") and p.startswith(base)):
                v += r["views"]; m += r["beats"] * 15 / 60
                last = max(last, r["last"])
    return v, round(m), last


def age_days(iso):
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(iso)).days
    except Exception:
        return None


def main():
    with open(DATA) as f:
        d = json.load(f)
    stages = {s["key"]: s for s in d.get("stages", [])}
    heat = heat_rollup()
    escalations, reports = [], []

    for deal in d.get("deals", []):
        stage = deal.get("stage", "")
        if stage in BENCH or stage in ("live", "expand"):
            continue
        co = next((c for c in d.get("companies", []) if c["id"] == deal.get("companyId")), {})
        cfg = stages.get(stage, {})
        notes, esc = [], []

        a = age_days(deal.get("lastTouch") or deal.get("stageSince") or TODAY) or 0
        lim = cfg.get("staleDays", 7)
        if a >= lim:
            esc.append(f"STALE {a}d (limit {lim}d for {stage}) — draft the re-engage touch")
        elif a >= lim * 0.7:
            notes.append(f"approaching stale ({a}d of {lim}d)")
        else:
            notes.append(f"{a}d touched — healthy")

        arts = deal.get("artifacts", [])
        if stage == "discovery" and not arts:
            esc.append("Discovery with zero artifacts — queue the give-first build")
        unreacted = [x for x in arts if x.get("status") in ("built",)]
        if unreacted:
            notes.append(f"{len(unreacted)} artifact(s) built but not yet shown: " +
                         ", ".join(x["name"] for x in unreacted[:2]))

        v, m, last = deal_heat(deal, heat)
        if v:
            deal["heatNote"] = f"{v} views · ~{m}m · last {last[:16]}"
            notes.append(f"heat: {deal['heatNote']}")
            if last[:10] == TODAY:
                esc.append(f"ENGAGED TODAY ({v} total views) — draft the strike-while-warm follow-up")
        if not deal.get("nextAction"):
            esc.append("No next action on an in-motion deal — draft one")
        if not deal.get("nextDraft") and stage in ("discovery", "demo-proposal"):
            esc.append(f"No draft attached at {stage} — write the touch for the Founder to send")

        note = f"[{stage}] " + "; ".join(notes + [f"⚠ {e}" for e in esc])
        reports.append((co.get("name", deal.get("name", "?")), note))
        log = deal.setdefault("agentLog", [])
        if not (log and log[-1].get("date") == TODAY and log[-1].get("note") == note):
            log.append({"date": TODAY, "agent": "deal-agent", "note": note})
            del log[:-LOG_CAP]
        for e in esc:
            escalations.append({"date": TODAY, "dealId": deal["id"], "company": co.get("name", ""),
                                "stage": stage, "ask": e, "status": "open"})

    if DRY:
        for nm, note in reports:
            print(f"• {nm}: {note}")
        print(f"\n{len(escalations)} escalation(s)")
        return

    lock = open(LOCK, "a+")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        with open(DATA) as f:      # re-read under the lock, re-apply only our fields
            fresh = json.load(f)
        by_id = {x["id"]: x for x in d["deals"]}
        for deal in fresh.get("deals", []):
            src = by_id.get(deal["id"])
            if src is None:
                continue
            if "agentLog" in src:
                deal["agentLog"] = src["agentLog"]
            if "heatNote" in src:
                deal["heatNote"] = src["heatNote"]
        tmp = DATA + ".tmp.agents"
        with open(tmp, "w") as f:
            json.dump(fresh, f, indent=2, ensure_ascii=False)
        os.replace(tmp, DATA)
        js = os.path.join(REPO, "crm", "data.js")
        with open(js, "w") as f:
            f.write("/* AUTO-GENERATED from data.json by server.py. Source of truth is data.json. */\n")
            f.write("window.CRM_DATA = " + json.dumps(fresh, indent=2, ensure_ascii=False) + ";\n")
        with open(ESCALATIONS, "w") as f:
            json.dump(escalations, f, indent=2, ensure_ascii=False)
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
    print(f"deal-agents: {len(reports)} deals reported, {len(escalations)} escalation(s) → {os.path.basename(ESCALATIONS)}")

    # The adversarial half: two opposed readers over the same evidence, and the spread
    # between them stored on the deal. Deterministic like everything above, so it rides
    # the same schedule rather than needing a timer of its own. Never fatal.
    try:
        r = subprocess.run([sys.executable, os.path.join(REPO, "crm", "adversarial.py")],
                           capture_output=True, text=True, timeout=180)
        print("deal-agents: " + ((r.stdout or "").strip().splitlines() or ["adversarial reads: no output"])[-1])
    except Exception as e:
        print(f"deal-agents: adversarial reads skipped ({type(e).__name__}: {e})")

    # Refresh the derived outcomes mirror so the CRM's reports (and the static dashboard) see
    # every client ledger without walking clients/ themselves.
    try:
        r = subprocess.run([sys.executable, os.path.join(REPO, "crm", "expansion.py"), "--mirror"],
                           capture_output=True, text=True, timeout=120)
        if (r.stdout or "").strip():
            print("deal-agents: " + (r.stdout or "").strip().splitlines()[-1])
    except Exception as e:
        print(f"deal-agents: outcomes mirror skipped ({type(e).__name__}: {e})")

    # Push the confirmed promise ledger out to each client folder, so the client console
    # shows current promise debt. Writes nothing where there are no confirmed promises —
    # the console hides the section rather than rendering an empty or invented ledger.
    try:
        r = subprocess.run([sys.executable, os.path.join(REPO, "crm", "promises.py"), "--export"],
                           capture_output=True, text=True, timeout=120)
        line = next((l for l in (r.stdout or "").splitlines() if l.startswith("exported:")), None)
        if line:
            print("deal-agents: " + line)
    except Exception as e:
        print(f"deal-agents: promise export skipped ({type(e).__name__}: {e})")


if __name__ == "__main__":
    main()
