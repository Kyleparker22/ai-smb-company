#!/usr/bin/env python3
"""yourco — the own-OS grant: at 5+ live referred clients, the connector's business runs on the product.

The R1 perk is a free digital employee. This is the next order of magnitude: **a connector with five
live referred clients gets an yourco AI OS built and operated for their own business** — their
pipeline, their follow-ups, their downline, their admin — under the same reliability, eval and
approval layer a paying client gets.

Why it is worth real money to give away (the Founder, 2026-08-13):

- **Their intro stops being a sales pitch and becomes testimony.** "I run my business on this" is a
  sentence no compensation plan can buy and no competitor can copy.
- **yourco gets a fleet of live production instances** where the operator is motivated, non-technical
  and highly vocal — the best eval surface available, running for free, on exactly the SMB profile
  the product is sold into.
- **The arithmetic is not close.** Five live clients at the $3,000 Core floor is $15,000/mo of
  referred revenue; a Core-shaped OS costs yourco build time plus absorbed tokens. The grant is
  cheap against the book that earns it, which is the whole reason the threshold exists.

**What this module does and does not do.** It computes *eligibility* and reports *status*. It does not
provision anything: an OS is scoped, built and operated by people (Kimi + the scaffolder), and a
switch that silently promised someone a system nobody had started would be worse than no switch.
`status` therefore separates **earned** (the book qualifies) from **provisioned** (it actually exists),
and the gap between them is a visible commitment yourco owes, not a quiet backlog.

⚠️ **STAGED** like the rest of the program — `GRANT_ACTIVE` is False until launch. Eligibility is
computed and shown as *earned, not yet started*; nothing is promised to anyone before the gate clears.

Usage:
  python3 crm/connector_perks.py                 # every connector's grant status
  python3 crm/connector_perks.py "Sample Contact"
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
CRM = os.path.join(DATA_DIR, "data.json")
sys.path.insert(0, HERE)
import connector_ladder as ladder
from connector_statements import books, CORE_FLOOR

OS_GRANT_THRESHOLD = 5         # live referred clients. the Founder, 2026-08-13.
GRANT_ACTIVE = False           # staged — same posture as BOUNTY_PAYABLE / ESCROW_PAYABLE
META_KEY = "connectorOSGrants"

# Once earned, the grant does NOT lapse if the book dips below the threshold while they remain an
# active connector. This is deliberate and it is a policy choice, not an oversight: a rung governs
# *permissions* and must fall when the evidence does, but this is a running business system somebody
# depends on, and switching off a person's operations because a client churned would be a worse
# failure than the one it corrects. It ends when they leave the program. [[the Founder to confirm]]
STICKY_ONCE_EARNED = True

STATUSES = ("not_yet", "earned", "scoped", "live", "ended")


def _grants(d):
    return ((d.get("meta") or {}).get(META_KEY) or {})


def compute(name, d=None):
    """One connector's grant status. Returns None if they are not a connector in yourco's records."""
    d = d if d is not None else json.load(open(CRM))
    state = ladder.compute(d)
    if name not in state:
        return None
    connectors, _c, _dl = books(d)
    book = connectors.get(name, {"active": [], "inactive": []})
    live = len(book["active"])
    mrr = sum(a.get("mrr") or 0 for a in book["active"])
    rec = _grants(d).get(name) or {}
    recorded = rec.get("status")

    if recorded in ("scoped", "live", "ended"):
        status = recorded                      # a human moved it; the book cannot move it back
    elif live >= OS_GRANT_THRESHOLD:
        status = "earned"
    elif recorded == "earned" and STICKY_ONCE_EARNED:
        status = "earned"                      # earned once, kept while they are active
    else:
        status = "not_yet"

    short = max(0, OS_GRANT_THRESHOLD - live)
    return {
        "connector": name, "status": status, "liveClients": live, "referredMRR": mrr,
        "threshold": OS_GRANT_THRESHOLD, "short": short, "active": GRANT_ACTIVE,
        "sticky": STICKY_ONCE_EARNED,
        "scopedAt": rec.get("scopedAt"), "liveAt": rec.get("liveAt"), "note": rec.get("note"),
        # The arithmetic, stated rather than asserted — the grant's justification is a ratio and the
        # console shows it so nobody has to take "it pays for itself" on faith.
        "bookAtThreshold": OS_GRANT_THRESHOLD * CORE_FLOOR,
        "why": (
            f"You have {live} live referred client{'s' if live != 1 else ''}. "
            + (f"{short} more and yourco builds and runs an AI OS for your own business, free while "
               f"you're active." if status == "not_yet" else
               "You've earned an AI OS for your own business — yourco builds and operates it, free "
               "while you're active."
               + ("" if GRANT_ACTIVE else
                  " The connector program hasn't launched yet, so nothing is scheduled until it does."))
        ),
    }


def set_status(operator, name, status, note="", d=None, commit=True, log=None):
    """Move a grant through scoped → live → ended. An operator's act: provisioning is people, not code."""
    import connector_writes as writes
    operator = (operator or "").strip()
    if not operator:
        raise writes.ScopeError("A grant change must name the operator making it.")
    if status not in STATUSES:
        raise writes.ScopeError(f"Status must be one of: {', '.join(STATUSES)}.")
    d0 = d if d is not None else json.load(open(CRM))
    cur = compute(name, d0)
    if cur is None:
        raise writes.ScopeError(f"{name} is not a connector in yourco's records.")
    if status in ("scoped", "live") and cur["status"] == "not_yet":
        raise writes.ScopeError(
            f"{name} has {cur['liveClients']} live referred client(s); the grant is earned at "
            f"{OS_GRANT_THRESHOLD}. Starting one anyway is the Founder's call to make explicitly, not a "
            f"status flip.")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

    def apply(dd):
        g = dd.setdefault("meta", {}).setdefault(META_KEY, {}).setdefault(name, {})
        g["status"] = status
        g["by"] = operator
        g["updated"] = now
        if note:
            g["note"] = note
        if status == "scoped":
            g.setdefault("scopedAt", now)
        if status == "live":
            g.setdefault("liveAt", now)
        return g

    out = writes._locked_update(apply) if (commit and d is None) else apply(d0)
    emit = log if log is not None else ladder.log_event
    emit("osgrant.changed", connector=name, by=operator, status=status, note=note or None,
         liveClients=cur["liveClients"],
         note2=f"Own-OS grant → {status}")
    return out


def owed(d=None):
    """Grants earned but not yet started. yourco's commitment backlog — visible, never quiet."""
    d = d if d is not None else json.load(open(CRM))
    out = []
    for name in sorted(ladder.compute(d)):
        r = compute(name, d)
        if r and r["status"] == "earned":
            out.append(r)
    return out


def main():
    d = json.load(open(CRM))
    names = [sys.argv[1]] if len(sys.argv) > 1 else sorted(ladder.compute(d))
    print(f"# Own-OS grant — earned at {OS_GRANT_THRESHOLD} live referred clients "
          f"({'ACTIVE' if GRANT_ACTIVE else 'STAGED — nothing scheduled until launch'})\n")
    any_close = False
    for n in names:
        r = compute(n, d)
        if not r:
            continue
        if r["status"] != "not_yet" or r["liveClients"] > 0:
            any_close = True
            print(f"  {n:<26} {r['status']:<9} {r['liveClients']} live · ${r['referredMRR']:,.0f}/mo")
    if not any_close:
        print("  Nobody has a live referred client yet — no grant is close (program pre-launch).")
    back = owed(d)
    if back:
        print(f"\n  ⚠ {len(back)} grant(s) earned and not yet started: {', '.join(x['connector'] for x in back)}")


if __name__ == "__main__":
    main()
