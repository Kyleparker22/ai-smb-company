#!/usr/bin/env python3
"""Change OS — synthetic subcontractor. `python3 seed.py [--projects 25]`.

"Meridian Mechanical" — $14M mechanical sub, TX+FL, 18 GCs, projects at every
stage, field notes including genuinely ambiguous ones, retainage that outlived
its jobs, and deadlines both comfortable and uncomfortably near.
Synthetic only; 555 phones; no real firms.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(11)

GC_NAMES = ["Harlow Build Group", "Crestline Constructors", "Bandera GC", "Palmetto Builders",
            "Ironvale Construction", "Sunbelt Commercial", "Copper Ridge GC", "Lakemont Builders",
            "Stonebriar Construction", "Gulfline Contractors", "Redbud Builders", "Vantage GC",
            "Halstead Construction", "Bluebonnet Commercial", "Seagrove Builders", "Northfork GC",
            "Quarryside Construction", "Everline Builders"]

PROJECT_KINDS = ["office TI", "medical office building", "school addition", "distribution center",
                 "hotel", "multifamily podium", "grocery remodel", "municipal annex"]

BASE_NOTES = [
    "installed VAV boxes per plans, floor {n} complete",
    "hung {n} sticks of pipe on L{m}",
    "rough-in east wing per drawings",
    "set RTUs per spec, crane day went clean",
    "poured footings per spec, section {c}",
    "finished insulation L{m} per contract",
]
CHANGE_NOTES = [
    ("super directed us to add a second condensate run on L{m}", 4200, False),
    ("GC wants the duct rerouted around new steel, not on drawings", 9800, False),
    ("owner asked for extra floor drain in kitchen", 2600, True),
    ("T&M ticket signed for saturday demo work", 5400, True),
    ("re-ran the feeder after the layout changed", 7600, False),
    ("delay - electrical trade not clear of our area again, crew standing", 3100, False),
    ("waiting on RFI {n} answer before closing wall", 0, False),
    ("architect changed the spec on grille finishes, resubmitting", 1900, True),
]
AMBIG_NOTES = ["misc site stuff, talked to jim", "long day", "see photos", ""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", type=int, default=25)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {
        "company": "Meridian Mechanical", "revenue": "$14M", "field_headcount": 62,
        "erp": "modelled, not connected", "bonding_capacity": 8_000_000,
        "comfortable_backlog": 30,
        "notice_rules": core.DEFAULT_NOTICE_RULES,
    })

    gcs = [{"id": f"gc_{i:02d}", "name": n} for i, n in enumerate(GC_NAMES)]
    store.save("gcs", gcs)

    projects, pay_apps, notes = [], [], []
    for i in range(args.projects):
        gc = rng.choice(gcs)
        state = rng.choice(["TX", "TX", "FL"])
        started = now() - timedelta(days=rng.randint(30, 600))
        value = rng.randint(300, 2400) * 1000
        done = rng.random() < 0.35
        p = {"id": f"prj_{i:03d}", "name": f"{rng.choice(PROJECT_KINDS)} — {gc['name'].split()[0]}",
             "gc_id": gc["id"], "state_code": state, "contract_value": value,
             "first_furnish": iso(started + timedelta(days=rng.randint(5, 20))),
             "final_furnish": iso(started + timedelta(days=rng.randint(120, 300))) if done else None,
             "substantial_completion": iso(now() - timedelta(days=rng.randint(20, 300))) if done else None,
             "retainage_terms_days": 60, "notices_filed": [], "started": iso(started)}
        # a slice has no SOV → % complete unknowable; and one project sits in a
        # state with no rule set, so its deadlines are honestly uncomputable
        if rng.random() < 0.12:
            p["contract_value"] = None
        if i == args.projects - 1:
            p["state_code"] = "GA"
        projects.append(p)

        # pay apps: monthly, some slow GCs
        gc_slow = hash(gc["id"]) % 3 == 0
        months = rng.randint(2, 10)
        for m in range(months):
            billed_at = started + timedelta(days=30 * (m + 1))
            if billed_at > now():
                continue
            billed = round(value / max(months, 1) * rng.uniform(0.7, 1.1), 2) if value else rng.randint(40, 180) * 1000
            ret = round(billed * 0.10, 2)
            paid_lag = rng.randint(55, 95) if gc_slow else rng.randint(25, 50)
            paid_at = billed_at + timedelta(days=paid_lag)
            pay_apps.append({"id": store.nid("pa"), "project_id": p["id"], "gc_id": gc["id"],
                            "billed": billed, "retainage_held": ret, "retainage_released": 0,
                            "billed_at": iso(billed_at),
                            "paid": billed - ret if paid_at < now() else 0,
                            "paid_at": iso(paid_at) if paid_at < now() else None})

        # field notes
        for _ in range(rng.randint(4, 10)):
            r = rng.random()
            if r < 0.62:
                t = rng.choice(BASE_NOTES).format(n=rng.randint(2, 40), m=rng.randint(1, 6), c="B")
                est, has_dir = 0, False
            elif r < 0.90:
                t, est, has_dir = rng.choice(CHANGE_NOTES)
                t = t.format(n=rng.randint(90, 140), m=rng.randint(1, 6))
            else:
                t, est, has_dir = rng.choice(AMBIG_NOTES), 0, False
            notes.append({"id": store.nid("nt"), "project_id": p["id"], "text": t,
                          "est_value": est, "at": iso(started + timedelta(days=rng.randint(10, 200))),
                          "directive_ref": f"dir_{store.nid('x')[2:8]}" if (est and has_dir) else None})

    # a demo note guaranteed on the board: a directed extra with NO directive on file
    notes.append({"id": "nt_demo", "project_id": projects[0]["id"], "demo_tag": "demo",
                  "text": "super directed us to add a second condensate run on L3",
                  "est_value": 4200, "at": iso(now() - timedelta(hours=20)), "directive_ref": None})
    demo_co = {"id": "co_demo", "project_id": projects[0]["id"], "note_id": "nt_demo",
               "state": "draft", "value": 4200, "directive_ref": None,
               "summary": "second condensate run on L3 (super's direction, nothing signed)",
               "created_at": iso(), "demo_tag": "demo"}

    store.save("projects", projects)
    store.save("pay_apps", pay_apps)
    store.save("notes", notes)
    store.save("cos", [demo_co])

    invitations = []
    for i in range(8):
        gc = rng.choice(gcs)
        invitations.append({"id": f"inv_{i:02d}", "gc_id": gc["id"],
                            "project": f"{rng.choice(PROJECT_KINDS)} bid",
                            "value": rng.randint(200, 3000) * 1000,
                            "trade_fit": rng.random() < 0.7,
                            "bond_required": rng.random() < 0.3,
                            "due": iso(now() + timedelta(days=rng.randint(3, 21)))})
    store.save("invitations", invitations)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"projects": len(projects), "notes": len(notes), "pay_apps": len(pay_apps)})
    print(f"Seeded {len(projects)} projects, {len(notes)} notes, {len(pay_apps)} pay apps, "
          f"{len(invitations)} invitations")


if __name__ == "__main__":
    main()
