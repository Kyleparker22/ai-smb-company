#!/usr/bin/env python3
"""Delta OS — synthetic Keystone Interior Systems. Synthetic only: invented
GCs, invented jobs, 555 phones. Nothing here is a real company or person."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(63)

JOBS = [
    ("jb_01", "Alder Street Medical Office", "Bellwether Construction Group"),
    ("jb_02", "Riverbend Apartments Bldg C", "Harlan-Reyes Builders"),
    ("jb_03", "Wexford Elementary Addition", "Cardinal Point GC"),
    ("jb_04", "Granite Junction Hotel", "Northgate Constructors"),
    ("jb_05", "Lot 9 Office Shell", "Summit & Vane Construction"),
    ("jb_06", "Marquette Lofts", "Ironline Builders"),
]

CLAUSES = {
    "jb_01": {"days": 10, "method": "written notice to the General Contractor's project manager",
              "text": "The Subcontractor shall provide written notice of any change, changed "
                      "condition, or extra work within ten (10) days of discovery, or the claim "
                      "is waived."},
    "jb_02": {"days": 7, "method": "written notice by email to the GC project engineer",
              "text": "Claims for extra work must be noticed in writing within seven (7) days of "
                      "the event giving rise to the claim."},
    "jb_03": {"days": 21, "method": "certified mail to the Construction Manager",
              "text": "Notice of any changed condition shall be given within twenty-one (21) "
                      "days of the Subcontractor first observing the condition."},
    "jb_04": {"days": 5, "method": "written notice to the superintendent and PM jointly",
              "text": "Written notice of extra or changed work is required within five (5) days "
                      "of the condition first being observed; unnoticed work is deemed included."},
    "jb_05": {"days": 14, "method": "written notice to the Owner's representative via the GC",
              "text": "The Subcontractor waives any claim not noticed in writing within "
                      "fourteen (14) days of discovery."},
    # jb_06 deliberately has NO recorded clause — the gap the notice letter names.
}

# demo plan lines (locations the observations below will hit)
DEMO_PLAN = [
    ("pl_d1", "jb_01", "L2 east wing", '5/8" Type X drywall', 1200, "sf", 3),
    ("pl_d2", "jb_01", "lobby", "ACT ceiling grid 2x2", 900, "sf", 3),
    ("pl_d3", "jb_02", "stair B", '5/8" Type X drywall', 800, "sf", 2),
    ("pl_d4", "jb_03", "L1 corridor", '3-5/8" 20ga metal stud framing', 260, "lf", 4),
    ("pl_d5", "jb_04", "L3 units", '5/8" Type X drywall', 2200, "sf", 2),
    ("pl_d6", "jb_05", "clinic corridor", '5/8" Type X drywall', 600, "sf", 1),
    ("pl_d7", "jb_06", "unit corridors L2", '5/8" Type X drywall', 1400, "sf", 5),
]

FILL_LOCS = ["L1 west wing", "L1 east wing", "L2 west wing", "L2 corridor", "L3 corridor",
             "stair A", "elevator lobby", "mech room", "amenity room", "unit block A",
             "unit block B"]
CREW = ["T. Ruiz", "M. Okafor", "J. Lindqvist", "D. Trujillo", "S. Havel", "R. Osei"]

MESSAGES = [
    ("jb_01", "P. Mercer — Bellwether PE", "when will your crew finish level 3"),
    ("jb_03", "K. Bostic — Cardinal Point super", "need a schedule update, are you done by friday"),
    ("jb_05", "A. Renner — Summit & Vane PM", "what's your manpower look like next week"),
    ("jb_02", "M. Ocampo — Harlan-Reyes PM", "who do we send the insurance cert to"),
    ("jb_04", "L. Calloway — Northgate super", "can you wrap the ceilings by the 20th"),
    ("jb_06", "C. Iglesias — Ironline PM", "lunch truck is on site by the north gate"),
]


def main():
    store.wipe()
    store.save("config", {"company": "Keystone Interior Systems",
                          "trade": "drywall & framing subcontractor",
                          "office_phone": "(555) 014-8830", "active_jobs": len(JOBS),
                          "rate_schedule": core.DEFAULT_RATE_SCHEDULE})

    store.save("jobs", [{"id": j, "name": n, "gc": g} for j, n, g in JOBS])
    store.save("contracts", [
        {"id": f"ct_{j[-2:]}", "job_id": j, "gc": g,
         "notice_clause": CLAUSES.get(j),
         **({} if j in CLAUSES else
            {"note": "subcontract on file; the notice clause was never recorded — the gap the "
                     "notice letter names"})}
        for j, n, g in JOBS])

    # -- plan lines: the demo seven + filler to ~40, one line per (job, location)
    plan = [{"id": i, "job_id": j, "location": loc, "spec": sp, "qty": q, "unit": u, "rev": r}
            for i, j, loc, sp, q, u, r in DEMO_PLAN]
    specs = list(core.DEFAULT_RATE_SCHEDULE["rates"].items())
    n = 0
    for j, _, _ in JOBS:
        for loc in rng.sample(FILL_LOCS, 6):
            sp, entry = rng.choice(specs)
            qty = rng.choice([120, 260, 400, 850, 1200, 1600] if entry["unit"] == "sf"
                             else [60, 120, 240, 380])
            n += 1
            plan.append({"id": f"pl_{n:03d}", "job_id": j, "location": loc, "spec": sp,
                         "qty": qty, "unit": entry["unit"], "rev": rng.choice([1, 2, 3, 4, 5])})
    store.save("plan_lines", plan)

    # -- observations: 18 clean matches (field == plan, the honest majority)
    #    + 7 deltas, one of each demo class. ~25 total.
    obs = []

    def clean(oid, line, hours_ago):
        obs.append({"id": oid, "job_id": line["job_id"], "location": line["location"],
                    "photo_ref": f"IMG_{rng.randint(1000, 9999)}.jpg",
                    "observed_spec": line["spec"], "observed_qty": line["qty"],
                    "by": rng.choice(CREW), "at": iso(now() - timedelta(hours=hours_ago))})

    filler = [p for p in plan if p["id"].startswith("pl_0")]
    by_job = {}
    for p in filler:
        by_job.setdefault(p["job_id"], []).append(p)
    clean("ob_clean_1", by_job["jb_01"][0], 3)
    clean("ob_clean_2", by_job["jb_02"][0], 5)
    clean("ob_clean_3", by_job["jb_03"][0], 4)
    clean("ob_clean_4", by_job["jb_05"][0], 6)
    k = 0
    for j, lines in by_job.items():
        for line in lines[1:4]:
            k += 1
            if k > 14:
                break
            clean(f"ob_fill_{k:02d}", line, rng.randint(2, 30))

    obs += [
        # added_scope by quantity — the main demo flow (10-day clause, window live)
        {"id": "ob_demo_qty", "job_id": "jb_01", "location": "L2 east wing",
         "photo_ref": "IMG_2214.jpg", "observed_spec": '5/8" Type X drywall',
         "observed_qty": 1450, "by": "T. Ruiz",
         "note": "third layer carried past the elevator shaft per super",
         "at": iso(now() - timedelta(hours=6))},
        # changed_spec — also the price-unconfirmed refusal demo
        {"id": "ob_demo_spec", "job_id": "jb_02", "location": "stair B",
         "photo_ref": "IMG_1108.jpg",
         "observed_spec": '5/8" Type X drywall, 2-hr shaft wall', "observed_qty": 800,
         "by": "M. Okafor", "note": "shaft-wall assembly in place of standard board",
         "at": iso(now() - timedelta(hours=5))},
        # rework — the note carries the tear-out language
        {"id": "ob_demo_rework", "job_id": "jb_03", "location": "L1 corridor",
         "photo_ref": "IMG_3341.jpg", "observed_spec": '3-5/8" 20ga metal stud framing',
         "observed_qty": 90, "by": "J. Lindqvist",
         "note": "tore out and re-framed 90 lf after plumbing rerouted through our wall",
         "at": iso(now() - timedelta(hours=4))},
        # UNPLANNED — a location with no plan line at all
        {"id": "ob_demo_unplanned", "job_id": "jb_04", "location": "roof access corridor",
         "photo_ref": "IMG_4420.jpg", "observed_spec": "soffit framing + drywall",
         "observed_qty": 40, "by": "D. Trujillo",
         "note": "soffit built at roof access per field direction",
         "at": iso(now() - timedelta(hours=3))},
        # off-schedule spec — pricing must refuse (not on the rate schedule)
        {"id": "ob_demo_offsched", "job_id": "jb_05", "location": "clinic corridor",
         "photo_ref": "IMG_5512.jpg", "observed_spec": "abuse-resistant board (AR-1)",
         "observed_qty": 600, "by": "S. Havel",
         "note": "AR board installed per architect walk",
         "at": iso(now() - timedelta(hours=7))},
        # expired window — photo dated 12 days ago on the 5-day-clause job
        {"id": "ob_demo_expired", "job_id": "jb_04", "location": "L3 units",
         "photo_ref": "IMG_0937.jpg", "observed_spec": '5/8" Type X drywall',
         "observed_qty": 2600, "by": "R. Osei",
         "note": "extra layer at party walls, found reviewing old uploads",
         "at": iso(now() - timedelta(days=12))},
        # the no-clause job — the notice letter must refuse and name the gap
        {"id": "ob_demo_noclause", "job_id": "jb_06", "location": "unit corridors L2",
         "photo_ref": "IMG_7781.jpg", "observed_spec": '5/8" Type X drywall',
         "observed_qty": 1650, "by": "T. Ruiz",
         "note": "corridor extended past unit 214 per super",
         "at": iso(now() - timedelta(hours=8))},
    ]
    store.save("observations", obs)
    store.save("deltas", [])

    messages = [{"id": f"ms_{i:03d}", "job_id": j, "from": frm, "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 48)))}
                for i, (j, frm, t) in enumerate(MESSAGES)]
    messages.append({"id": "ms_demo_verbal", "job_id": "jb_01",
                     "from": "D. Petras — Bellwether super",
                     "text": "go ahead and add the soffit in the lobby, we'll paper it later",
                     "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_backcharge", "job_id": "jb_02",
                     "from": "M. Ocampo — Harlan-Reyes PM",
                     "text": "we're backcharging you for the patch repair on level 2",
                     "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"jobs": len(JOBS), "plan_lines": len(plan), "observations": len(obs)})
    print(f"Seeded {len(JOBS)} jobs, {len(plan)} plan lines, {len(obs)} observations, "
          f"{len(store.load('contracts'))} contracts (1 without a notice clause), "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
