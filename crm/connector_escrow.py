#!/usr/bin/env python3
"""yourco — referral escrow: a bond posted against yourco's own conduct, payable to the connector.

Every referral program tracks *deals*. None of them track what a referral **costs the referrer**.

When a connector hands over their dentist, their physio, their mother's landscaper, they are spending
a relationship they will need again. If yourco handles that contact badly — never calls, calls late,
opens badly, gets a complaint — the connector eats a loss that the program has no way of recording,
and the only party who knows it happened is the one who caused it. So yourco records it, against
itself, and pays for it.

**What this is not.** It is not compensation for a lost commission. A referral that simply doesn't
close costs the connector nothing but time, and no bond is owed — businesses say no, that is normal
and it is not a breach. The bond is for **relationship damage caused by yourco's conduct**, which is
a different event with a different cause, and conflating the two would turn this into a guarantee
against ordinary sales outcomes.

**Every breach is computed, not asserted.** Two of the four come straight off the append-only
attribution log and the submission record — yourco cannot fail to notice them, and cannot quietly
decline to record them, because the same timestamps that prove the SLA also prove the miss. The other
two require a human to log an incident, and that asymmetry is stated on the console rather than
hidden: *we catch our own lateness automatically; we rely on you to tell us about a bad conversation.*

| Breach | Detected how | Default |
|---|---|---|
| `verify_late` | verified > `SLA_VERIFY_HOURS` after submission, from the record's own timestamps | computed |
| `never_contacted` | verified, then no first contact within `SLA_CONTACT_DAYS` | computed |
| `bad_first_touch` | an incident logged against the outreach | human-logged |
| `complaint` | the contact complained to the connector or to yourco | human-logged |

⚠️ **STAGED, like every other payment in this program.** `ESCROW_PAYABLE` is False: breaches accrue
and are shown, and nothing is owed or payable until the program launches and counsel clears. The
per-breach amount is a **proposal** (`[[the Founder to confirm]]`), deliberately set equal to one bounty step
so the arithmetic is legible: *we paid you $25 for the contact; we owe you the same if we waste it.*

Usage:
  python3 crm/connector_escrow.py                 # every connector's ledger
  python3 crm/connector_escrow.py "Sample Contact"
"""
import os, sys, json, uuid, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
CRM = os.path.join(DATA_DIR, "data.json")
sys.path.insert(0, HERE)
import connector_ladder as ladder
from connector_statements import submissions, BOUNTY_VERIFIED

SLA_VERIFY_HOURS = 48          # the promise made on the console and in the packet
SLA_CONTACT_DAYS = 5           # verified means we intend to call; this is when "intend" expires
# [[the Founder to confirm]] — proposal, set equal to one bounty step so the sentence is symmetrical.
ESCROW_PER_BREACH = BOUNTY_VERIFIED
ESCROW_PAYABLE = False         # staged, exactly like BOUNTY_PAYABLE
META_KEY = "connectorIncidents"

BREACHES = {
    "verify_late":     ("We were late verifying", "You submitted a contact and we sat on it past the "
                                                  "24–48 hours we promised."),
    "never_contacted": ("We never made the call", "We verified the contact and then didn't reach out. "
                                                  "You spent the relationship and we didn't use it."),
    "bad_first_touch": ("We opened badly",        "Our first contact was logged as mishandled."),
    "complaint":       ("They complained",        "The person you sent us complained about how we "
                                                  "approached them."),
}
COMPUTED = ("verify_late", "never_contacted")
HUMAN_LOGGED = ("bad_first_touch", "complaint")


def _hours_between(a, b):
    try:
        ta = datetime.datetime.fromisoformat(a)
        tb = datetime.datetime.fromisoformat(b)
        return (tb - ta).total_seconds() / 3600.0
    except (TypeError, ValueError):
        return None


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def log_incident(operator, submission_id, kind, note="", d=None, commit=True, log=None):
    """Record a human-observed breach. Deliberately an OPERATOR act, and it costs yourco money.

    A connector cannot log one against yourco themselves — not because they would lie, but because a
    self-serve payout trigger is a different instrument with a different failure mode. They report it;
    yourco records it, under a name, on the permanent log.
    """
    import connector_writes as writes
    operator = (operator or "").strip()
    if not operator:
        raise writes.ScopeError("An incident must name the operator recording it.")
    if kind not in HUMAN_LOGGED:
        raise writes.ScopeError(
            f"{kind!r} is not a human-logged breach. {', '.join(HUMAN_LOGGED)} are logged by hand; "
            f"{', '.join(COMPUTED)} are computed from the record and cannot be entered manually.")
    d0 = d if d is not None else json.load(open(CRM))
    sub = next((r for r in submissions(d0) if r.get("id") == submission_id), None)
    if not sub:
        raise writes.ScopeError("No such submission.")
    now = _now().isoformat(timespec="seconds")
    rec = {"id": f"inc-{now.replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:6]}",
           "submissionId": submission_id,
           "connector": sub.get("connector"), "kind": kind, "note": note,
           "at": now, "by": operator}

    def apply(dd):
        dd.setdefault("meta", {}).setdefault(META_KEY, []).append(rec)
        return rec

    out = writes._locked_update(apply) if (commit and d is None) else apply(d0)
    emit = log if log is not None else ladder.log_event
    emit("escrow.breach", connector=sub.get("connector"), by=operator, submissionId=submission_id,
         kind=kind, note=note or BREACHES[kind][0],
         fault="yourco",  # the field that makes this searchable as OUR failures, not theirs
         note2=None)
    return out


def compute(name=None, d=None):
    """The escrow ledger. `name` for one connector, None for everyone. Returns {connector: {...}}."""
    d = d if d is not None else json.load(open(CRM))
    incidents = ((d.get("meta") or {}).get(META_KEY) or [])
    now = _now()
    out = {}

    for s in submissions(d, name):
        who = (s.get("connector") or "").strip()
        if not who:
            continue
        e = out.setdefault(who, {"connector": who, "breaches": [], "owed": 0.0,
                                 "payable": ESCROW_PAYABLE, "submissions": 0})
        e["submissions"] += 1
        st = (s.get("status") or "pending").strip()

        # 1. Late verification — from the record's own two timestamps, or from now if still pending.
        end = s.get("verifiedAt") or now.isoformat(timespec="seconds")
        hrs = _hours_between(s.get("submittedAt"), end)
        if hrs is not None and hrs > SLA_VERIFY_HOURS:
            e["breaches"].append({"kind": "verify_late", "submissionId": s.get("id"),
                                  "business": s.get("business"), "detail": f"{hrs / 24:.1f} days to verify",
                                  "at": s.get("verifiedAt") or "", "computed": True})

        # 2. Verified and then nobody called. Only meaningful once verification happened AND the
        #    contact has not moved on — a submission that reached `booked` or `client` was obviously
        #    contacted, so it cannot be in breach here regardless of what any activity log says.
        if st == "verified" and s.get("verifiedAt"):
            since = _hours_between(s["verifiedAt"], now.isoformat(timespec="seconds"))
            if since is not None and since / 24.0 > SLA_CONTACT_DAYS:
                e["breaches"].append({"kind": "never_contacted", "submissionId": s.get("id"),
                                      "business": s.get("business"),
                                      "detail": f"verified {since / 24:.0f} days ago, still no conversation",
                                      "at": s["verifiedAt"], "computed": True})

    for inc in incidents:
        who = (inc.get("connector") or "").strip()
        if not who or (name is not None and who != name):
            continue
        e = out.setdefault(who, {"connector": who, "breaches": [], "owed": 0.0,
                                 "payable": ESCROW_PAYABLE, "submissions": 0})
        e["breaches"].append({"kind": inc.get("kind"), "submissionId": inc.get("submissionId"),
                              "business": "", "detail": inc.get("note") or "",
                              "at": inc.get("at"), "computed": False, "by": inc.get("by")})

    for e in out.values():
        e["breaches"].sort(key=lambda b: b.get("at") or "", reverse=True)
        e["owed"] = round(len(e["breaches"]) * ESCROW_PER_BREACH, 2)
        e["computedCount"] = sum(1 for b in e["breaches"] if b["computed"])
        e["loggedCount"] = sum(1 for b in e["breaches"] if not b["computed"])
    return out


def main():
    d = json.load(open(CRM))
    book = compute(sys.argv[1] if len(sys.argv) > 1 else None, d)
    if not book:
        print("No submissions yet — nothing yourco could have mishandled (program pre-launch).")
        return
    print(f"# Referral escrow — yourco's conduct on {len(book)} connector(s)")
    print(f"  ${ESCROW_PER_BREACH}/breach · "
          f"{'PAYABLE' if ESCROW_PAYABLE else 'ACCRUED, NOT PAYABLE (staged)'}\n")
    for who, e in sorted(book.items()):
        print(f"  {who}: {len(e['breaches'])} breach(es) → ${e['owed']:,.2f} "
              f"({e['computedCount']} computed, {e['loggedCount']} logged) over {e['submissions']} submission(s)")
        for b in e["breaches"]:
            print(f"      {BREACHES.get(b['kind'], (b['kind'],))[0]:<26} {b['business'] or '—':<26} {b['detail']}")


if __name__ == "__main__":
    main()
