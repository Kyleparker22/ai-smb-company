#!/usr/bin/env python3
"""yourco — the connector approves yourco's first message to their contact, and earns their way off it.

On a **Sourcer** submission yourco calls a business owner the connector knows personally. yourco is
therefore about to spend *their* relationship capital, using their name as the reason the call isn't
cold — and in every other referral program on earth the referrer has no say in how that is done.

So give them the gate. yourco drafts the first outbound; it renders in their console; they approve it,
edit it, or decline it. And then — this is the part that makes it yourco's product rather than a
courtesy — **their position on that gate is earned on evidence, exactly like an agent's**
(`processes/autonomy-matrix.md`). The Autonomy Matrix, pointed at a human on the other side of the
relationship.

| Rung | What happens | Earned by |
|---|---|---|
| **A0 · You approve every one** | Nothing goes out until they say so | the floor — everyone starts here |
| **A1 · We tell you first** | Draft is shown for `NOTIFY_HOURS`; silence releases it | `A1_CLEAN` consecutive clean approvals |
| **A2 · We just go** | yourco drafts and proceeds; they see it on their log | `A2_CLEAN` more, still clean |

A **clean** approval is one approved without edits and never followed by a complaint. Editing is not
a failure — an edit is the connector telling us our draft was wrong about someone they know, which is
the single most valuable signal here — but it *does* mean the draft wasn't right, so it doesn't count
toward earning your way off the gate. **Any complaint resets to A0**, the same way an agent's rung
drops when its evidence reverses.

**Two gates, not one.** A connector approving a draft does NOT mean yourco sends it. yourco's own
approval gate still applies (`the Founder sends; agents draft` — CLAUDE.md), so a released draft is a draft
that has cleared the *connector's* objection and is queued for yourco's normal send path. Nothing in
this module sends anything, and `release()` is deliberately named for what it does.

Storage: `meta.connectorApprovals` — append-style, never edited except to record the decision.

Usage:
  python3 crm/connector_approvals.py                # every connector's rung + open drafts
  python3 crm/connector_approvals.py "Sample Contact"
"""
import os, sys, json, uuid, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
CRM = os.path.join(DATA_DIR, "data.json")
sys.path.insert(0, HERE)
import connector_ladder as ladder
from connector_statements import submissions

META_KEY = "connectorApprovals"
NOTIFY_HOURS = 24        # A1: how long a draft waits before silence releases it
A1_CLEAN = 5             # clean approvals to earn A1
A2_CLEAN = 10            # further clean approvals to earn A2
MAX_DRAFT = 4000

RUNGS = [
    {"n": 0, "key": "A0", "name": "You approve every one",
     "what": "Nothing reaches anyone you sent us until you have read it and said yes.",
     "earn": "where everyone starts"},
    {"n": 1, "key": "A1", "name": "We tell you first",
     "what": f"We show you the draft and wait {NOTIFY_HOURS} hours. Say nothing and it goes forward; "
             f"one click stops it.",
     "earn": f"{A1_CLEAN} approvals in a row with no edits and no complaints"},
    {"n": 2, "key": "A2", "name": "We just go",
     "what": "We write and proceed. Everything still appears on your log, and one click puts you back "
             "on the gate for good.",
     "earn": f"{A2_CLEAN} more, still clean"},
]
DECISIONS = ("approved", "edited", "declined", "released", "stopped")


class ApprovalError(PermissionError):
    """A decision the caller may not make. Raised BEFORE anything is written."""


def _rows(d, connector=None):
    rows = ((d.get("meta") or {}).get(META_KEY) or [])
    if connector is not None:
        rows = [r for r in rows if (r.get("connector") or "") == connector]
    return sorted(rows, key=lambda r: r.get("createdAt") or "")


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def rung_for(name, d=None):
    """Their position on the gate, computed from their own decision history. Never granted.

    Read strictly newest-backward: a complaint anywhere resets the streak, so the count is of
    consecutive clean approvals **since the last complaint**, not lifetime.
    """
    d = d if d is not None else json.load(open(CRM))
    rows = _rows(d, name)
    incidents = [i for i in ((d.get("meta") or {}).get("connectorIncidents") or [])
                 if (i.get("connector") or "") == name and i.get("kind") == "complaint"]
    last_complaint = max((i.get("at") or "" for i in incidents), default="")

    streak = 0
    for r in rows:
        if (r.get("decidedAt") or "") <= last_complaint:
            continue                                    # everything before the reset is spent
        st = r.get("status")
        if st in ("approved", "released"):
            streak += 1
        elif st in ("edited", "declined", "stopped"):
            streak = 0                                  # not punishment — just not evidence of a clean draft

    n = 2 if streak >= (A1_CLEAN + A2_CLEAN) else (1 if streak >= A1_CLEAN else 0)
    if (d.get("meta") or {}).get("connectorApprovalHold", {}).get(name):
        n = 0                                           # they asked to go back on the gate — always honoured
    rung = RUNGS[n]
    nxt = RUNGS[n + 1] if n < 2 else None
    need = (A1_CLEAN - streak) if n == 0 else ((A1_CLEAN + A2_CLEAN) - streak) if n == 1 else 0
    return {"n": n, "key": rung["key"], "name": rung["name"], "what": rung["what"],
            "streak": streak, "next": nxt, "needed": max(0, need),
            "resetBy": last_complaint or None, "held": bool(
                (d.get("meta") or {}).get("connectorApprovalHold", {}).get(name))}


def draft_for(operator, submission_id, text, d=None, commit=True, log=None):
    """yourco records the first-contact draft it intends to send. Always the operator's act."""
    import connector_writes as writes
    operator = (operator or "").strip()
    if not operator:
        raise ApprovalError("A draft must name the operator who wrote it.")
    text = (text or "").strip()
    if not text:
        raise ApprovalError("There is no draft to approve.")
    if len(text) > MAX_DRAFT:
        raise ApprovalError(f"Draft too long (max {MAX_DRAFT} characters).")
    d0 = d if d is not None else json.load(open(CRM))
    sub = next((s for s in submissions(d0) if s.get("id") == submission_id), None)
    if not sub:
        raise ApprovalError("No such submission.")
    if (sub.get("status") or "") not in ("verified", "booked", "client"):
        raise ApprovalError("That submission has not been verified yet — nothing should be sent to an "
                            "unverified contact.")
    who = sub.get("connector")
    now = _now().isoformat(timespec="seconds")
    rung = rung_for(who, d0)
    rec = {"id": f"apr-{now.replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:6]}",
           "submissionId": submission_id,
           "connector": who, "business": sub.get("business"), "draft": text,
           "status": "pending", "createdAt": now, "createdBy": operator,
           "rungAtDraft": rung["key"],
           # A1 auto-release deadline is stamped at draft time so the clock cannot be moved later.
           "releaseAfter": ((_now() + datetime.timedelta(hours=NOTIFY_HOURS)).isoformat(timespec="seconds")
                            if rung["n"] == 1 else None)}

    def apply(dd):
        dd.setdefault("meta", {}).setdefault(META_KEY, []).append(rec)
        return rec

    out = writes._locked_update(apply) if (commit and d is None) else apply(d0)
    emit = log if log is not None else ladder.log_event
    emit("approval.requested", connector=who, by=operator, submissionId=submission_id,
         business=sub.get("business"), rung=rung["key"],
         note=f"First-contact draft for {sub.get('business')} — {rung['name']}")
    if rung["n"] == 2:                      # A2: proceed on draft, still logged, still visible
        return decide(who, rec["id"], "released", d=d0, commit=(commit and d is None), log=log,
                      actor_is_system=True)
    return out


def decide(actor, approval_id, decision, edited=None, d=None, commit=True, log=None,
           actor_is_system=False):
    """The connector's call on one draft — or the system's, when A2/auto-release applies.

    A connector may only decide on drafts about **their own** referrals. Nobody decides for them.
    """
    import connector_writes as writes
    if decision not in DECISIONS:
        raise ApprovalError(f"Decision must be one of: {', '.join(DECISIONS)}.")
    d0 = d if d is not None else json.load(open(CRM))
    rec = next((r for r in _rows(d0) if r.get("id") == approval_id), None)
    if not rec:
        raise ApprovalError("No such draft.")
    if not actor_is_system and (rec.get("connector") or "") != (actor or "").strip():
        raise ApprovalError("That draft is about someone else's referral.")
    if rec.get("status") != "pending":
        return rec                                        # idempotent; a decision is made once
    if decision == "edited" and not (edited or "").strip():
        raise ApprovalError("An edit needs the edited text — otherwise it is just an approval.")
    now = _now().isoformat(timespec="seconds")

    def apply(dd):
        for r in dd.setdefault("meta", {}).setdefault(META_KEY, []):
            if r.get("id") != approval_id:
                continue
            r["status"] = decision
            r["decidedAt"] = now
            r["decidedBy"] = "yourco (auto)" if actor_is_system else actor
            if decision == "edited":
                r["editedDraft"] = (edited or "").strip()[:MAX_DRAFT]
            return r
        return None

    out = writes._locked_update(apply) if (commit and d is None) else apply(d0)
    emit = log if log is not None else ladder.log_event
    emit("approval.decided", connector=rec.get("connector"),
         by=("yourco (auto)" if actor_is_system else actor),
         submissionId=rec.get("submissionId"), business=rec.get("business"),
         decision=decision,
         note=f"{rec.get('business')}: first-contact draft {decision}"
              + (" — released without objection" if actor_is_system else ""))
    return out


def due_for_release(d=None):
    """A1 drafts whose notify window has expired. The runtime calls this; it releases, never sends."""
    d = d if d is not None else json.load(open(CRM))
    now = _now().isoformat(timespec="seconds")
    return [r for r in _rows(d)
            if r.get("status") == "pending" and r.get("releaseAfter") and r["releaseAfter"] <= now]


def pending_for(name, d=None):
    d = d if d is not None else json.load(open(CRM))
    return [r for r in _rows(d, name) if r.get("status") == "pending"]


def compute(name, d=None):
    """Everything the console renders for one connector."""
    d = d if d is not None else json.load(open(CRM))
    rows = _rows(d, name)
    return {"connector": name, "rung": rung_for(name, d),
            "pending": [r for r in rows if r.get("status") == "pending"],
            "history": sorted([r for r in rows if r.get("status") != "pending"],
                              key=lambda r: r.get("decidedAt") or "", reverse=True),
            "notifyHours": NOTIFY_HOURS}


def main():
    d = json.load(open(CRM))
    names = [sys.argv[1]] if len(sys.argv) > 1 else sorted(ladder.compute(d))
    shown = False
    for n in names:
        r = compute(n, d)
        if not r["pending"] and not r["history"]:
            continue
        shown = True
        g = r["rung"]
        print(f"\n# {n} — {g['key']} · {g['name']}  (streak {g['streak']}"
              + (f", {g['needed']} to {g['next']['key']}" if g["next"] else "") + ")")
        for p in r["pending"]:
            print(f"    PENDING  {p['business']:<30} {p['draft'][:60]!r}")
        for h in r["history"][:5]:
            print(f"    {h['status']:<9} {h['business']:<30} {h.get('decidedAt', '')[:10]}")
    if not shown:
        print("No first-contact drafts yet (program pre-launch).")


if __name__ == "__main__":
    main()
