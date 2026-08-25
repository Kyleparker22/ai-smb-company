"""
Add illustrative operating activity on top of an imported real portfolio.

seed_parker.py imports the books a manager actually keeps: their doors, tenants,
rents and trust ledger. Those books say nothing about the maintenance, turnovers,
vendors or owner prospects of the current week, so the boards that show day-to-day
operation come up empty and the platform looks broken rather than idle.

This fills those boards using THEIR real units and tenants, so a prospect sees
their own portfolio in motion. Every record it writes is stamped illustrative:true
and the dataset carries a banner saying so on every page. The money is never
touched — the trust ledger, charges and payments stay exactly as imported, because
that is the part they will check against their own spreadsheet.

    python3 seed_parker.py "/path/to/journal.xlsx"     # their real books
    python3 seed_activity.py                           # then this
"""
import sys, os, random, datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

R = random.Random(20260819)          # fixed seed: the demo looks the same every run
UTC = dt.timezone.utc
NOW = dt.datetime.now(UTC)


def ago(days=0, hours=0):
    return (NOW - dt.timedelta(days=days, hours=hours)).isoformat()


def ahead(days=0):
    return (NOW + dt.timedelta(days=days)).isoformat()


def sid(prefix):
    return f"{prefix}_{R.getrandbits(40):010x}"


VENDORS = [
    ("Queen City Plumbing", ["plumbing"], 118, True),
    ("Carolina Air & Heat", ["hvac"], 135, True),
    ("Meck Electric", ["electrical"], 125, False),
    ("Bramlett Handyman Services", ["handyman", "carpentry"], 85, False),
    ("Southside Turnover & Clean", ["cleaning", "paint"], 70, False),
]

# Written the way a tenant actually texts, because triage quality is the demo.
TICKETS = [
    ("water heater making a banging noise and the hot water runs out fast", "P2", "hvac", 0, "open", None),
    ("garage door won't close all the way, keeps reversing", "P3", "handyman", 1, "open", None),
    ("no hot water at all since last night", "P1", "plumbing", 0, "dispatched", 380),
    ("kitchen faucet dripping, getting worse", "P3", "plumbing", 3, "open", None),
    ("AC not keeping up, house is 79 with it set to 72", "P2", "hvac", 2, "dispatched", 465),
    ("gutter came loose on the side of the house after the storm", "P3", "handyman", 5, "open", None),
    ("dishwasher leaking onto the floor", "P2", "plumbing", 6, "resolved", 212),
    ("bedroom outlet stopped working", "P3", "electrical", 9, "resolved", 165),
    ("front porch light out, bulb didn't fix it", "P4", "electrical", 12, "resolved", 140),
]


def build():
    units = core.load("units") or []
    tenants = core.load("tenants") or []
    props = core.load("properties") or []
    owners = core.load("owners") or []
    if not units:
        sys.exit("no portfolio imported yet — run seed_parker.py first")

    occupied = [u for u in units if u.get("tenant_id")]
    ten_by_id = {t["id"]: t for t in tenants}
    prop_by_id = {p["id"]: p for p in props}
    own_by_prop = {p["id"]: p.get("owner_id") for p in props}
    own_by_id = {o["id"]: o for o in owners}

    # ── vendors ──────────────────────────────────────────────────────────────
    vendors = []
    for i, (name, trades, hourly, after_hours) in enumerate(VENDORS, 1):
        vendors.append({
            "id": f"vnd_{i}", "name": name, "trades": trades, "hourly": hourly,
            "tier_seed": "great" if i < 3 else "ok",
            "phone": f"704-555-0{100+i*7}",
            "email": name.lower().replace(" ", "").replace("&", "and") + "@example.com",
            "insurance_expires": ahead(R.randint(40, 300)),
            "w9_on_file": True, "after_hours": after_hours,
            "service_areas": ["Yourtown", "Yourtown", "Yourtown"],
            "active": True, "illustrative": True,
        })
    vendor_for = {}
    for v in vendors:
        for t in v["trades"]:
            vendor_for.setdefault(t, v["id"])

    # ── maintenance requests across their real units ─────────────────────────
    requests = [r for r in (core.load("requests") or [])]      # keep imported history
    new_reqs, approvals, messages = [], [], []
    for i, (text, pri, trade, days, status, cost) in enumerate(TICKETS):
        u = occupied[i % len(occupied)]
        t = ten_by_id.get(u["tenant_id"], {})
        p = prop_by_id.get(u["property_id"], {})
        rid = sid("req")
        req = {
            "id": rid, "unit_id": u["id"], "property_id": u["property_id"],
            "tenant_id": u.get("tenant_id"),
            "title": text, "description": text,
            "category": trade, "priority": pri, "status": status,
            "submitted_at": ago(days=days, hours=R.randint(1, 20)),
            "channel": R.choice(["sms", "app", "phone"]),
            "photos": ["(illustrative) tenant photo"] if R.random() < .5 else [],
            "triage": {"category": trade, "priority": pri, "confidence": round(R.uniform(.78, .94), 2),
                       "reasons": [f"keyword match on {trade}"], "trade": trade,
                       "by": "agent:triage"},
            "vendor_id": vendor_for.get(trade) if status != "open" else None,
            "cost": cost, "illustrative": True,
        }
        if status == "resolved":
            req["resolved_at"] = ago(days=max(0, days - 2))
        new_reqs.append(req)

        # the expensive ones stop and ask — that gate is the product
        if cost and cost > 400:
            oid = own_by_prop.get(u["property_id"])
            owner = own_by_id.get(oid, {})
            limit = owner.get("spend_approval_limit", 400)
            if cost > limit:
                approvals.append({
                    "id": sid("apr"), "at": ago(hours=R.randint(2, 30)), "agent": "dispatch",
                    "kind": "spend", "subject": rid,
                    "summary": f"${cost} — {text[:58]}",
                    "payload": {"request": rid, "amount": cost,
                                "owner": owner.get("name", "owner"), "emergency": pri == "P1"},
                    "why_human": f"${cost} exceeds the ${limit} standing authority on "
                                 f"{p.get('name','this property')}",
                    "status": "pending", "illustrative": True,
                })

    # a disbursement waiting on a human — the permanent R0 gate
    if owners:
        o = owners[0]
        approvals.append({
            "id": sid("apr"), "at": ago(hours=6), "agent": "books",
            "kind": "disbursement", "subject": o["id"],
            "summary": f"Monthly owner disbursement drafted — {o.get('name','owner')}",
            "payload": {"owner": o["id"], "drafted": True},
            "why_human": "Executing a transfer is permanently a human action. "
                         "The draft is ready; you move it at the bank and record the reference.",
            "status": "pending", "illustrative": True,
        })

    # a drafted tenant message waiting to go out
    if occupied:
        t = ten_by_id.get(occupied[0]["tenant_id"], {})
        messages.append({
            "id": sid("msg"), "at": ago(hours=3), "agent": "concierge",
            "to_kind": "tenant", "to_id": t.get("id"),
            "subject": "Your water heater visit",
            "body": "Queen City Plumbing can come Thursday between 9 and 12, or Friday "
                    "after 1. Reply with whichever suits and I'll book it.",
            "status": "draft", "illustrative": True,
        })

    # ── one turnover, on a unit with no sitting tenant ────────────────────────
    turnovers = []
    vacant = [u for u in units if not u.get("tenant_id")]
    target = vacant[0] if vacant else occupied[-1]
    turnovers.append({
        "id": sid("trn"), "unit_id": target["id"], "property_id": target["property_id"],
        "tenant_id": None, "state": "make_ready",
        "opened_at": ago(days=21), "moveout_date": ago(days=18), "moved_out": ago(days=18),
        "new_lease_start": None, "vacancy_days": 18,
        "tasks": [
            {"name": "Move-out inspection", "state": "done", "at": ago(days=17)},
            {"name": "Carpet clean", "state": "done", "at": ago(days=12)},
            {"name": "Paint touch-up", "state": "in_progress", "vendor": "vnd_5"},
            {"name": "Re-key", "state": "pending"},
            {"name": "Listing photos", "state": "pending"},
        ],
        "history": [{"state": "opened", "at": ago(days=21)},
                    {"state": "make_ready", "at": ago(days=17)}],
        "illustrative": True,
    })

    # ── owner prospects for the growth board ─────────────────────────────────
    prospects = [
        {"id": sid("pros"), "at": ago(days=6), "name": "Yourtown investor — 4 doors",
         "contact": "(withheld until contacted)",
         "note": "Self-managing four rentals near Marvin; asked about fees at a closing.",
         "source": {"kind": "manual", "by": "human:mgr_1"}, "stage": "recorded",
         "stage_at": ago(days=6), "history": [{"stage": "recorded", "at": ago(days=6)}],
         "illustrative": True},
        {"id": sid("pros"), "at": ago(days=15), "name": "Ballantyne owner — 2 doors",
         "contact": "(withheld until contacted)",
         "note": "Out-of-state, tired of coordinating repairs by text.",
         "source": {"kind": "manual", "by": "human:mgr_1"}, "stage": "meeting",
         "stage_at": ago(days=3),
         "history": [{"stage": "recorded", "at": ago(days=15)},
                     {"stage": "meeting", "at": ago(days=3)}],
         "illustrative": True},
    ]

    core.save("vendors", vendors)
    core.save("requests", requests + new_reqs)
    core.save("approvals", approvals)
    core.save("messages", messages)
    core.save("turnovers", turnovers)
    core.save("prospects", prospects)

    cfg = core.load("config", {}) or {}
    cfg["notice"] = ("Real portfolio and trust ledger · maintenance, vendors, turnover "
                     "and leads are illustrative")
    cfg["illustrative"] = {"requests": len(new_reqs), "vendors": len(vendors),
                           "approvals": len(approvals), "turnovers": len(turnovers),
                           "prospects": len(prospects),
                           "note": "money collections were not touched"}
    core.save("config", cfg)
    return new_reqs, approvals, vendors, turnovers, prospects


if __name__ == "__main__":
    r, a, v, t, p = build()
    print(f"requests {len(r)} · approvals {len(a)} · vendors {len(v)} · "
          f"turnovers {len(t)} · prospects {len(p)}")
    print("money collections untouched — ledger, charges and payments are still the real import")
