#!/usr/bin/env python3
"""Advocate — the people loop, on the Partners door.

`processes/yourco-flywheel.md` §The people loop says the connector program is a *loop*, not a
channel: a happy client or warm relationship becomes a connector, climbs R0–R4 on computed
evidence, produces reach, and at R2 may recruit more connectors. This renders whether that loop
is actually turning.

Today it is not, and the panel's job is to say so precisely rather than to look busy. The
flywheel section carries a belief-not-finding marker; this is the surface that will eventually
remove it — or keep it honest indefinitely.

NO FORKED MATH.  Rungs come from `crm/connector_ladder.compute()` — the same function the
connector console and the statements use. This module never re-derives a rung, a tier, or a
commission; it reads what the ladder computed and arranges it.

THE ONE THING IT MUST NOT DO is imply the loop can be started by recruiting harder. It can't:
R1 requires a real referral conversation and R2 requires a live client retained 90 days, so the
people loop is downstream of delivery by construction. That dependency is rendered as a first-
class fact, because the failure mode here is a founder recruiting connectors instead of closing
client #1 — and the ladder is the thing that refuses it.

Read-only. Exposed as GET /api/advocate.
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "crm"))

FLYWHEEL = "processes/yourco-flywheel.md"


def _crm():
    try:
        with open(os.path.join(ROOT, "crm", "data.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def build():
    try:
        import connector_ladder as cl
    except Exception as e:
        return {"error": f"connector ladder unavailable: {type(e).__name__}: {e}"}

    try:
        computed = cl.compute()
    except Exception as e:
        return {"error": f"ladder compute failed: {type(e).__name__}: {e}"}

    d = _crm()
    meta = d.get("meta") or {}

    # ---- rung distribution, including the rung that isn't one --------------
    # rungN == -1 is "Not joined" — a contact tagged connector who has signed nothing. Folding
    # that into R0 would report a joined network that does not exist.
    rungs = [{"key": r["key"], "name": r["name"], "n": r["n"],
              "earn": r.get("earn", ""), "unlocks": cl.unlocks_at(r["n"])}
             for r in cl.RUNGS]
    dist = {r["key"]: 0 for r in cl.RUNGS}
    not_joined = 0
    people, blocked_by_training = [], 0
    for name, c in sorted(computed.items()):
        if c.get("rungN", -1) < 0:
            not_joined += 1
        else:
            dist[c["rung"]] = dist.get(c["rung"], 0) + 1
        if c.get("blockedByTraining"):
            blocked_by_training += 1
        people.append({
            "name": name, "rung": c.get("rung"), "rungName": c.get("rungName"),
            "rungN": c.get("rungN"), "teamStatus": c.get("teamStatus"),
            "evidenceRung": c.get("evidenceRung"),
            "blockedByTraining": bool(c.get("blockedByTraining")),
            "trainingNeeded": c.get("trainingNeeded"),
            "nextRung": c.get("nextRung"), "nextRungEarn": c.get("nextRungEarn"),
            "unlocks": c.get("unlocks") or [],
            "referrals": (c.get("evidence") or {}).get("referrals", 0),
            "conversations": (c.get("evidence") or {}).get("conversations", 0),
            "live": (c.get("evidence") or {}).get("live", 0),
            "activeMRR": (c.get("book") or {}).get("activeMRR", 0),
            "downline": len(c.get("downline") or []),
        })
    joined = sum(dist.values())
    producing = sum(v for k, v in dist.items() if k in ("R2", "R3", "R4"))

    # ---- the client -> connector arc (EXPAND feeding REACH) ----------------
    companies = d.get("companies", []) or []
    referring = [c.get("name") for c in companies
                 if (c.get("referrer") or "").strip() or c.get("referredByCompany")]
    credit = ((meta.get("referralProgram") or {}).get("clientCreditPerMonth")
              or meta.get("clientReferralCredit") or 100)

    # ---- what actually gates the loop --------------------------------------
    r1 = next((r for r in cl.RUNGS if r["key"] == "R1"), {})
    r2 = next((r for r in cl.RUNGS if r["key"] == "R2"), {})
    gates = [
        {"rung": "R1", "requires": r1.get("earn", "a real referral conversation"),
         "meaning": "a connector cannot prove out without a live conversation yourco actually had"},
        {"rung": "R2", "requires": r2.get("earn", "a live client retained 90 days"),
         "meaning": "recruiting other connectors unlocks here — so the downline cannot exist "
                    "before a delivered, retained client does"},
    ]

    turning = joined > 0 and producing > 0
    if not computed:
        zero = ("No connector contacts at all. The loop has no population — it cannot turn, and "
                "nothing here is a measurement.")
    elif joined == 0:
        zero = (f"{not_joined} people are tagged as connectors and **none has joined** — nobody "
                f"holds even R0, because nobody has signed a referral agreement. The loop has "
                f"never turned once. This is the honest state, not a slow start.")
    elif not producing:
        zero = (f"{joined} joined, none producing. Reach exists on paper; no referral has become "
                f"a live client yet.")
    else:
        zero = None

    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "turning": turning,
        "zeroState": zero,
        "counts": {
            "contacts": len(computed), "notJoined": not_joined, "joined": joined,
            "producing": producing, "blockedByTraining": blocked_by_training,
            "referringClients": len(referring),
        },
        "byRung": [{**r, "n_people": dist.get(r["key"], 0)} for r in rungs],
        "notJoined": not_joined,
        "people": sorted(people, key=lambda p: (-(p["rungN"] if p["rungN"] is not None else -1),
                                                -p["referrals"], p["name"]))[:40],
        "clientArc": {
            "creditPerMonth": credit,
            "referringClients": referring,
            "note": (f"A client who refers earns ${credit}/mo credit per active referred client — "
                     f"the arc from EXPAND back into REACH. "
                     + ("No client is referring yet." if not referring else "")),
        },
        "gates": gates,
        "dependency": ("The people loop is downstream of delivery by construction: R1 needs a real "
                       "referral conversation and R2 needs a live client retained 90 days. "
                       "Recruiting connectors is never a substitute for closing client #1 — the "
                       "ladder refuses it."),
        "launchSubsidy": {
            "note": "The mechanic that makes each turn cheaper than the last: a new connector "
                    "inherits yourco's proof instead of building their own. Under-equipping one "
                    "doesn't slow the loop, it prevents it starting.",
            "byRung": [{"rung": r["key"], "unlocks": r["unlocks"]} for r in rungs if r["unlocks"]],
        },
        "gated": {
            "downlineOverride": "counsel-gated (MLM) — renders informational · NOT PAYABLE. "
                                "Recruiting unlocks at R2; paying on a downline does not.",
        },
        "source": {"ladder": "crm/connector_ladder.py (compute — same function the console uses)",
                   "flywheel": FLYWHEEL},
        "note": "Rungs are computed from CRM evidence, never granted. 'Not joined' is kept "
                "separate from R0: folding it in would report a network that does not exist.",
    }


if __name__ == "__main__":
    d = build()
    if d.get("error"):
        raise SystemExit(d["error"])
    c = d["counts"]
    print(f"ADVOCATE — the people loop  ·  turning: {d['turning']}")
    print(f"  {c['contacts']} connector contacts · {c['notJoined']} not joined · "
          f"{c['joined']} joined · {c['producing']} producing")
    if d["zeroState"]:
        print("  " + d["zeroState"].replace("**", ""))
    print("\n  rungs:")
    for r in d["byRung"]:
        print(f"    {r['key']} {r['name']:<14} {r['n_people']:>3} people   "
              f"unlocks: {', '.join(r['unlocks']) or '—'}")
    print(f"\n  client arc: {d['clientArc']['note']}")
    print(f"  gates:")
    for g in d["gates"]:
        print(f"    {g['rung']} — {g['requires']}")
    print(f"\n  {d['dependency']}")
    print(f"  downline: {d['gated']['downlineOverride']}")
