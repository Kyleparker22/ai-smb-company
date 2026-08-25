#!/usr/bin/env python3
"""Field OS — synthetic ag-services operation. `python3 seed.py`.

"Prairie Line Ag Services" — ~180 growers, ~600 jobs incl. RUP orders with and
without licensed applicators, as-applied records present and missing, messages
incl. every complaint type. Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(30)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
PRODUCTS = [("glyphosate 4L", False), ("2,4-D LV6", False), ("atrazine 4L", True),
            ("paraquat", True), ("chlorpyrifos", True), ("urea 46-0-0", False),
            ("fungicide blend", False)]
MESSAGES = [
    "your rig sprayed right up to my fence and now my tomatoes are curling",
    "what rate of atrazine should I run on my corn",
    "can you get my beans sprayed this week before the rain",
    "invoice looks good, check is in the mail",
]
LICENSES = [f"APL-{n}" for n in (48211, 48377, 51022, 52940)]


def main():
    store.wipe()
    store.save("config", {"company": "Prairie Line Ag Services", "revenue": "$7M",
                          "rigs": 6, "software": "modelled, not connected"})

    growers = [{"id": f"gr_{i:03d}", "name": f"{rng.choice(LAST)} Farms"} for i in range(180)]
    store.save("growers", growers)

    jobs = []
    for i in range(600):
        product, rup = rng.choice(PRODUCTS)
        requested = now() - timedelta(days=rng.randint(1, 120))
        done = rng.random() < 0.7
        j = {"id": f"jb_{i:04d}", "grower": rng.choice(growers)["name"],
             "desc": f"{rng.randint(40, 640)}ac {product}", "rup": rup,
             "requested_at": iso(requested),
             "applicator_license": rng.choice(LICENSES) if (not rup or rng.random() < 0.85) else None,
             "window_note": rng.choice(["wind under 10 by thursday", "ground dry enough friday",
                                        None, "before the front saturday"])}
        if done:
            complete = rng.random() < 0.8
            j["as_applied"] = {
                "acres": rng.randint(40, 640) if complete else None,
                "product": product,
                "rate": f"{rng.choice([16, 22, 32, 48])} oz/ac",
                "applied_at": iso(requested + timedelta(days=rng.randint(1, 10))),
                "applicator_license": j["applicator_license"] if complete else None}
            if rng.random() < 0.6:
                j["billed_at"] = iso(requested + timedelta(days=rng.randint(11, 25)))
        jobs.append(j)

    # demo jobs
    jobs.append({"id": "jb_demo_norec", "grower": "Osei Farms", "desc": "320ac atrazine 4L",
                 "rup": True, "applicator_license": "APL-48211",
                 "requested_at": iso(now() - timedelta(days=8)),
                 "as_applied": {"acres": 320, "product": "atrazine 4L", "rate": "32 oz/ac",
                                "applied_at": None, "applicator_license": None},
                 "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_complete", "grower": "Mercer Farms", "desc": "240ac glyphosate",
                 "rup": False, "applicator_license": "APL-48377",
                 "requested_at": iso(now() - timedelta(days=6)),
                 "as_applied": {"acres": 240, "product": "glyphosate 4L", "rate": "22 oz/ac",
                                "applied_at": iso(now() - timedelta(days=2)),
                                "applicator_license": "APL-48377"},
                 "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_rup", "grower": "Havel Farms", "desc": "160ac paraquat",
                 "rup": True, "applicator_license": None,
                 "requested_at": iso(now() - timedelta(days=1)), "demo_tag": "demo"})

    messages = [{"id": f"ms_{i:03d}", "from": f"{rng.choice(LAST)}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_drift", "from": "neighbor on CR-12",
                     "text": "your rig sprayed right up to my fence and now my tomatoes are curling",
                     "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_rate", "from": "Pruitt",
                     "text": "what rate of atrazine should I run on my corn",
                     "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"})

    store.save("jobs", jobs)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"jobs": len(jobs)})
    print(f"Seeded {len(growers)} growers, {len(jobs)} jobs, {len(messages)} messages")


if __name__ == "__main__":
    main()
