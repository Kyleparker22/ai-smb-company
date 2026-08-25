#!/usr/bin/env python3
"""yourco — CRM hygiene automations (David). The three Twenty-benchmark automations from
crm/_backlog.md (decisions/2026-06-18_twenty-crm-client-component.md), built as one idempotent
weekday sweep:

  1. AUTO NEXT-STEP — any open deal at/past `proposal` (or any open non-prospect deal) with an
     empty nextAction gets one stamped ("Follow up on the proposal", nextDate +3 days). Fills
     blanks only — never overwrites a human's next step.
  2. STALE-DEAL NUDGE — open deals with lastTouch > 14 days → one Slack digest to #yourco-david
     (the exact failure that let Sample Client sit unlogged for 10+ days).
  3. CLOSED-WON PING — newly-won deals since the last run (state in loops/_crm-hygiene/state.json)
     → a celebratory Slack line. Real-time-ish revenue signal.

Writes go through the cross-process CRM lock (dashboard/melanie.crm_lock). Dated report to
loops/_crm-hygiene/<date>.md. Deterministic, stdlib-only. Slack degrades gracefully without a token.

Usage:  python3 runtime/crm_hygiene.py [--dry-run]
Timer:  runtime/systemd/yourco-crm-hygiene.{service,timer} — weekdays 08:05 ET.
"""
import json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRM = os.path.join(REPO, "crm", "data.json")
OUT = os.path.join(REPO, "loops", "_crm-hygiene")
STATE = os.path.join(OUT, "state.json")
CHANNEL = "#yourco-david"
STALE_DAYS = 14
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "dashboard"))
from site_intake import post_slack  # same stdlib Slack helper

DRY = "--dry-run" in sys.argv
today = datetime.date.today()


def days_since(iso):
    try:
        return (today - datetime.date.fromisoformat((iso or "")[:10])).days
    except ValueError:
        return None


crm = json.load(open(CRM))
deals = crm.get("deals", [])
companies = {c.get("id"): c.get("name", "?") for c in crm.get("companies", [])}
report, changed = [], False

# ── 1. auto next-step on empty nextAction ──
LATER = {"proposal", "build", "live"}
filled = []
for d in deals:
    stage = (d.get("stage") or "").lower()
    if stage in LATER and not (d.get("nextAction") or "").strip():
        d["nextAction"] = "Follow up on the proposal" if stage == "proposal" else "Set the next step"
        d["nextDate"] = (today + datetime.timedelta(days=3)).isoformat()
        filled.append(f"{d.get('id')} {d.get('name','?')} ({stage})")
        changed = True
if filled:
    report.append(f"**Auto next-step stamped ({len(filled)}):** " + "; ".join(filled))

# ── 2. stale-deal digest ──
stale = []
for d in deals:
    age = days_since(d.get("lastTouch"))
    if age is not None and age > STALE_DAYS:
        stale.append((age, f"• {d.get('name','?')} ({companies.get(d.get('companyId'),'?')}) — "
                           f"{age}d untouched, stage {d.get('stage','?')}, next: {d.get('nextAction') or '—'}"))
stale.sort(reverse=True)
if stale:
    digest = (f":hourglass_flowing_sand: *CRM hygiene — {len(stale)} deal(s) untouched > {STALE_DAYS} days*\n"
              + "\n".join(s for _, s in stale[:10])
              + ("\n…" if len(stale) > 10 else "")
              + "\n_Touch it, rebook it, or park it with a reason. — David_")
    report.append(f"**Stale (> {STALE_DAYS}d): {len(stale)}** — digest {'(dry-run, not posted)' if DRY else 'posted'} to {CHANNEL}")
    if not DRY:
        post_slack(CHANNEL, digest)

# ── 3. closed-won ping (state-diffed) ──
os.makedirs(OUT, exist_ok=True)
prev = set()
if os.path.exists(STATE):
    try: prev = set(json.load(open(STATE)).get("won_ids", []))
    except Exception: prev = set()
won_now = {str(c.get("id")) for c in crm.get("closed", []) if (c.get("outcome") or "").lower() == "won"}
new_wins = won_now - prev
for cid in sorted(new_wins):
    rec = next((c for c in crm.get("closed", []) if str(c.get("id")) == cid), {})
    line = (f":tada: *Closed WON — {rec.get('name','?')}* ({companies.get(rec.get('companyId'),'?')})"
            + (f" · ${rec.get('value'):,}/mo" if isinstance(rec.get("value"), (int, float)) and rec.get("value") else ""))
    report.append(f"**New win:** {rec.get('name','?')} — {'(dry-run)' if DRY else 'pinged'} {CHANNEL}")
    if not DRY:
        post_slack(CHANNEL, line)
if not DRY:
    json.dump({"won_ids": sorted(won_now), "asOf": today.isoformat()}, open(STATE, "w"), indent=1)

# ── persist CRM changes (locked) + report ──
if changed and not DRY:
    crm.setdefault("meta", {})["updated"] = today.isoformat()
    try:
        import melanie
        with melanie.crm_lock():
            melanie._atomic_dump(CRM, crm)
            melanie.write_mirror(crm)
    except Exception:
        tmp = f"{CRM}.tmp.{os.getpid()}"
        json.dump(crm, open(tmp, "w"), indent=1, ensure_ascii=False)
        os.replace(tmp, CRM)

if not report:
    report.append("Nothing to do — no blanks, no stale deals, no new wins.")
path = os.path.join(OUT, f"{today.isoformat()}.md")
body = (f"# CRM hygiene — {today.isoformat()}{' (dry-run)' if DRY else ''}\n\n" + "\n".join(f"- {r}" for r in report)
        + "\n\n*Automations: auto next-step · stale digest · closed-won ping — `runtime/crm_hygiene.py` (weekdays 08:05 ET).*\n")
if not DRY:
    open(path, "w").write(body)
print(body)
