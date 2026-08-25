#!/usr/bin/env python3
"""Plat OS — synthetic Meridian Land Surveying. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(53)

LAST = ["Whitcomb", "Ferris", "Okonkwo", "Straub", "Delgado", "Marchetti", "Ainsley", "Kovac",
        "Purnell", "Osei", "Landry", "Bexley", "Trask", "Iverson", "Quill", "Harmon"]
COUNTIES = ["Hart", "Banks", "Franklin", "Madison", "Elbert"]
TITLE_COS = ["Ridgeline Title", "Cornerstone Closings", "Blue Cedar Title", "Landmark Title Group"]
CREWS = ["Crew A — Delgado", "Crew B — Okonkwo"]
TYPES = ["boundary", "mortgage_loc", "topo", "alta", "subdivision"]
ACRES = {"boundary": (0.3, 25), "mortgage_loc": (0.2, 2), "topo": (1, 15),
         "alta": (0.5, 8), "subdivision": (5, 60)}
PRICE = {"boundary": (900, 120), "mortgage_loc": (350, 50), "topo": (1500, 200),
         "alta": (2800, 300), "subdivision": (4000, 250)}
MESSAGES = [
    "is my survey ready yet",
    "what would a boundary survey run on 3 acres",
    "can you pull the deed book and page for the ferris parcel",
    "thanks for getting the crew out so fast",
]


def _chain(i):
    return [{"kind": "deed", "book": 400 + i % 90, "page": 1 + (i * 7) % 300},
            {"kind": "plat", "cabinet": chr(65 + i % 6), "slide": 10 + i % 140}]


def _stage_log(start, durations):
    log, t = [], start
    for stage, d in durations:
        log.append({"stage": stage, "at": iso(t)})
        t += timedelta(days=d)
    return log, t


def main():
    store.wipe()
    store.save("config", {"company": "Meridian Land Surveying", "crews": CREWS,
                          "pls": {"name": "Rosa Whitcomb", "license": "PLS 5521"},
                          "phone": "555-0148"})
    store.save("title_companies", [{"id": f"tc_{i}", "name": n, "phone": "555-01%02d" % (60 + i)}
                                   for i, n in enumerate(TITLE_COS)])

    jobs, sheets = [], []

    # ~200 historical sealed jobs — the comparables and the stage clocks.
    for i in range(200):
        jt = rng.choice(TYPES)
        lo, hi = ACRES[jt]
        acreage = round(rng.uniform(lo, hi), 1)
        base, per = PRICE[jt]
        start = now() - timedelta(days=rng.randint(40, 400))
        log, end = _stage_log(start, [("research", rng.randint(2, 6)),
                                      ("field", rng.randint(1, 4)),
                                      ("draft", rng.randint(3, 8)),
                                      ("pls_review", rng.randint(1, 3)),
                                      ("sealed", 0)])
        jobs.append({"id": f"jb_h{i:03d}", "client": rng.choice(LAST),
                     "job_type": jt, "acreage": acreage, "county": rng.choice(COUNTIES),
                     "stage": "sealed", "stage_log": log,
                     "price": round(base + per * acreage + rng.uniform(-80, 80)),
                     "research_chain": _chain(i),
                     "seal": {"number": f"S-2025-{i:04d}", "date": iso(end)}})

    # ~60 open jobs across the pipeline, most on a title company's closing clock.
    for i in range(60):
        jt = rng.choice(TYPES)
        lo, hi = ACRES[jt]
        stage = rng.choice(("research", "research", "field", "field", "draft", "pls_review"))
        start = now() - timedelta(days=rng.randint(2, 20))
        idx = core.STAGES.index(stage)
        log, _ = _stage_log(start, [(s, rng.randint(1, 4)) for s in core.STAGES[:idx + 1]])
        j = {"id": f"jb_{i:03d}", "client": rng.choice(LAST + TITLE_COS),
             "job_type": jt, "acreage": round(rng.uniform(lo, hi), 1),
             "county": rng.choice(COUNTIES), "stage": stage, "stage_log": log,
             "research_chain": _chain(i) if (stage != "research" or rng.random() < 0.4) else []}
        if rng.random() < 0.7:
            j["closing_date"] = iso(now() + timedelta(days=rng.randint(2, 45)))
        if stage in ("draft", "pls_review") or (stage == "field" and rng.random() < 0.5):
            fd = now() - timedelta(days=rng.randint(1, 8))
            j["fieldwork_done_at"] = iso(fd)
            if i != 37:  # one day sheet missing on purpose — it must READ incomplete
                sheets.append({"id": f"ds_{i:03d}", "job_id": j["id"],
                               "crew": rng.choice(CREWS), "date": fd.date().isoformat(),
                               "points": rng.randint(40, 400),
                               "control": "tied to NGS mon " + rng.choice(["J 41", "K 87", "R 12"]),
                               "obstructions": rng.choice(["none", "heavy canopy SE corner",
                                                           "fence line overgrown"])})
        jobs.append(j)

    # Demo fixtures (demo_tag — the sweeps skip them).
    fd = now() - timedelta(days=3)
    jobs.append({"id": "jb_demo_friday", "client": "Ridgeline Title", "job_type": "boundary",
                 "acreage": 2.4, "county": "Hart", "stage": "draft",
                 "closing_date": iso(now() + timedelta(days=4)),
                 "fieldwork_done_at": iso(fd), "research_chain": _chain(301),
                 "stage_log": [{"stage": "research", "at": iso(now() - timedelta(days=9))},
                               {"stage": "field", "at": iso(now() - timedelta(days=4))},
                               {"stage": "draft", "at": iso(now() - timedelta(days=2))}],
                 "demo_tag": "demo"})
    sheets.append({"id": "ds_demo_friday", "job_id": "jb_demo_friday", "crew": CREWS[0],
                   "date": fd.date().isoformat(), "points": 212,
                   "control": "tied to NGS mon J 41", "obstructions": "none"})
    jobs.append({"id": "jb_demo_sealed", "client": "Cornerstone Closings", "job_type": "boundary",
                 "acreage": 1.1, "county": "Banks", "stage": "sealed",
                 "closing_date": iso(now() + timedelta(days=1)),
                 "research_chain": _chain(302),
                 "seal": {"number": "S-2026-0812", "date": iso(now() - timedelta(days=1))},
                 "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_unsealed", "client": "Blue Cedar Title", "job_type": "boundary",
                 "acreage": 3.2, "county": "Franklin", "stage": "pls_review",
                 "closing_date": iso(now() + timedelta(days=6)),
                 "research_chain": _chain(303),
                 "stage_log": [{"stage": "research", "at": iso(now() - timedelta(days=12))},
                               {"stage": "field", "at": iso(now() - timedelta(days=8))},
                               {"stage": "draft", "at": iso(now() - timedelta(days=5))},
                               {"stage": "pls_review", "at": iso(now() - timedelta(days=1))}],
                 "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_nochain", "client": "Straub", "job_type": "boundary",
                 "acreage": 5.5, "county": "Madison", "stage": "field",
                 "fieldwork_done_at": iso(fd), "research_chain": [],
                 "demo_tag": "demo"})
    sheets.append({"id": "ds_demo_nochain", "job_id": "jb_demo_nochain", "crew": CREWS[1],
                   "date": fd.date().isoformat(), "points": 96,
                   "control": "tied to NGS mon K 87", "obstructions": "creek at west line"})
    jobs.append({"id": "jb_demo_nosheet", "client": "Purnell", "job_type": "topo",
                 "acreage": 4.0, "county": "Elbert", "stage": "field",
                 "fieldwork_done_at": iso(now() - timedelta(days=2)),
                 "research_chain": _chain(304), "demo_tag": "demo"})
    store.save("jobs", jobs)
    store.save("day_sheets", sheets)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_boundary", "from": "Straub",
                     "text": "the buyer says the shed encroaches on the lot next door — "
                             "can you confirm the line",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_closing", "from": "Ridgeline Title",
                     "text": "closing moved to friday, will the survey be done",
                     "job_id": "jb_demo_friday",
                     "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_quote_ok", "from": "Landry",
                     "text": "what would a boundary survey run on 3 acres",
                     "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_quote_none", "from": "Bexley",
                     "text": "can you price an alta survey on 300 acres",
                     "at": iso(now() - timedelta(minutes=65)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("boundary_log", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"jobs": len(jobs), "day_sheets": len(sheets)})
    open_jobs = [j for j in jobs if j["stage"] != "sealed"]
    print(f"Seeded {len(jobs)} jobs ({len(open_jobs)} open), {len(sheets)} day sheets, "
          f"{len(messages)} messages, {len(TITLE_COS)} title companies")


if __name__ == "__main__":
    main()
