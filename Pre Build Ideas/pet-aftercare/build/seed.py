#!/usr/bin/env python3
"""Ember OS — synthetic Willow Creek Pet Aftercare. Synthetic only:
invented names, invented clinics, 555 phones."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(60)

CLINIC_A = ["Riverbend", "Cedar Hollow", "Maple Gate", "Foxglove", "Stonebridge", "Larkspur",
            "Willow Bend", "Copper Creek", "Harvest Hill", "Bluebell", "Quarry Ridge",
            "Meadowlark", "Alder Grove", "Juniper Flats", "Redbud", "Silver Birch",
            "Chestnut Row", "Ivy Lane", "Granite Falls", "Hollyhock"]
CLINIC_B = ["Animal Hospital", "Veterinary Clinic", "Pet Clinic", "Animal Care"]
PET_NAMES = ["Max", "Bella", "Luna", "Cooper", "Daisy", "Milo", "Rosie", "Biscuit", "Shadow",
             "Olive", "Juniper", "Finn", "Pepper", "Gus", "Willow", "Hazel", "Banjo", "Clover",
             "Moose", "Pippa", "Scout", "Tilly", "Bear", "Poppy"]
FAMILIES = ["Whitcomb", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel",
            "Osei", "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner",
            "Iglesias", "Thorne", "Vega", "Kolb", "Ashworth", "Nakamura"]
STAFF = ["driver M. Ortega", "driver L. Chen", "intake R. Solís", "operator K. Alvarez",
         "operator D. Whitmore", "care desk J. Patel", "care desk A. Brooks"]
MESSAGES = [
    "when will Luna's ashes be ready to come home",
    "can your driver collect two pets from our clinic tomorrow",
    "we'd like to add a paw print keepsake for Daisy",
    "thank you for taking such good care of our girl",
]


def chain(tag, stage_idx, t0):
    """Transfers 0..stage_idx along the chain, each with its tag check."""
    out = []
    for i in range(stage_idx):
        out.append({"at": iso(t0 + timedelta(days=i, hours=rng.randint(1, 8))),
                    "from": core.CHAIN_STEPS[i], "to": core.CHAIN_STEPS[i + 1],
                    "tag_check": {"tag": tag, "by": rng.choice(STAFF),
                                  "at": iso(t0 + timedelta(days=i, hours=rng.randint(1, 8)))}})
    return out


def main():
    store.wipe()
    store.save("config", {"company": "Willow Creek Pet Aftercare",
                          "phone": "555-0138", "clinics": 40,
                          "service_lines": list(core.SERVICE_LEVELS)})

    clinics = []
    for i in range(40):
        name = f"{CLINIC_A[i % len(CLINIC_A)]} {CLINIC_B[i % len(CLINIC_B)]}"
        clinics.append({"id": f"cx_{i:03d}", "name": name, "phone": f"555-01{40 + i:02d}",
                        "preferences": {
                            "paperwork": rng.choice(["signed release with each pet",
                                                     "emailed manifest at end of day",
                                                     "paper tag plus signed release"]),
                            "urn_default": rng.choice(["standard cedar", "classic brass",
                                                       "photo box"]),
                            "pickup_days": rng.choice([["Mon", "Thu"], ["Tue", "Fri"],
                                                       ["Wed"]])}})
    store.save("clinics", clinics)

    pets = []
    for i in range(300):
        tag = f"WC-{1000 + i}"
        level = rng.choices(core.SERVICE_LEVELS, weights=[30, 45, 25])[0]
        # most complete (home); the rest spread across the chain
        stage_idx = rng.choices([5, 4, 3, 2, 1], weights=[55, 18, 12, 9, 6])[0]
        intake = now() - timedelta(days=rng.randint(2, 150))
        p = {"id": f"pt_{i:03d}", "name": rng.choice(PET_NAMES),
             "species": rng.choice(["dog", "dog", "cat"]), "sex": rng.choice(["m", "f"]),
             "family": f"{rng.choice(['Sam', 'Ana', 'Lee', 'Mara', 'Jo', 'Theo'])} "
                       f"{rng.choice(FAMILIES)}",
             "phone": f"555-0{rng.randint(200, 899)}", "clinic_id": rng.choice(clinics)["id"],
             "tag": tag, "service_level": level,
             "election_ref": f"EL-{2600 + i}", "intake_at": iso(intake),
             "custody": chain(tag, stage_idx, intake)}
        if stage_idx >= 4:
            p["ashes_ready_at"] = p["custody"][3]["at"]
        if stage_idx == 5:
            p["returned_at"] = p["custody"][4]["at"]
            if rng.random() < 0.3:
                p["keepsakes"] = {"paw_print": {"at": p["returned_at"]}}
        pets.append(p)
    # a handful returned this week, so the counted panel has something to count
    for p in pets:
        if p.get("returned_at") and rng.random() < 0.06:
            t0 = now() - timedelta(days=rng.randint(6, 10))
            p["intake_at"] = iso(t0)
            p["custody"] = chain(p["tag"], 5, t0)
            p["ashes_ready_at"] = p["custody"][3]["at"]
            p["returned_at"] = p["custody"][4]["at"]

    # -- demo fixtures (demo_tag: sweeps skip them; the UI drives them)
    t0 = now() - timedelta(days=9)
    pets += [
        # the identity worry — Max, chain complete to the urn, every tag check recorded
        {"id": "pt_demo_max", "name": "Max", "species": "dog", "sex": "m",
         "family": "Ellery Whitcomb", "phone": "555-0417", "clinic_id": "cx_000",
         "tag": "WC-0417", "service_level": "private", "election_ref": "EL-0417",
         "intake_at": iso(t0), "custody": chain("WC-0417", 4, t0),
         "ashes_ready_at": iso(t0 + timedelta(days=4)), "demo_tag": "demo"},
        # a transfer awaiting its tag check — Biscuit, at the facility
        {"id": "pt_demo_transfer", "name": "Biscuit", "species": "dog", "sex": "f",
         "family": "Noor Osei", "phone": "555-0522", "clinic_id": "cx_003",
         "tag": "WC-0902", "service_level": "individual", "election_ref": "EL-0902",
         "intake_at": iso(now() - timedelta(days=2)),
         "custody": chain("WC-0902", 2, now() - timedelta(days=2)), "demo_tag": "demo"},
        # the deliberate gap — Shadow's record jumps facility → urn: HOLD
        {"id": "pt_demo_gap", "name": "Shadow", "species": "cat", "sex": "m",
         "family": "Rhea Bostic", "phone": "555-0633", "clinic_id": "cx_007",
         "tag": "WC-0771", "service_level": "individual", "election_ref": "EL-0771",
         "intake_at": iso(now() - timedelta(days=6)), "demo_tag": "demo",
         "custody": chain("WC-0771", 2, now() - timedelta(days=6)) + [
             {"at": iso(now() - timedelta(days=2)), "from": "facility", "to": "urn",
              "tag_check": {"tag": "WC-0771", "by": "operator K. Alvarez",
                            "at": iso(now() - timedelta(days=2))}}]},
        # the service-level wall — Juniper is private; the communal load is below
        {"id": "pt_demo_private", "name": "Juniper", "species": "dog", "sex": "f",
         "family": "Marisol Vega", "phone": "555-0744", "clinic_id": "cx_011",
         "tag": "WC-0655", "service_level": "private", "election_ref": "EL-0655",
         "intake_at": iso(now() - timedelta(days=1)),
         "custody": chain("WC-0655", 2, now() - timedelta(days=1)), "demo_tag": "demo"},
        {"id": "pt_demo_com1", "name": "Gus", "species": "dog", "sex": "m",
         "family": "Perry Havel", "phone": "555-0755", "clinic_id": "cx_012",
         "tag": "WC-0656", "service_level": "communal", "election_ref": "EL-0656",
         "intake_at": iso(now() - timedelta(days=1)),
         "custody": chain("WC-0656", 2, now() - timedelta(days=1)), "demo_tag": "demo"},
        # the engraving proof — Olive; also the before-the-clock case (12 days)
        {"id": "pt_demo_proof", "name": "Olive", "species": "cat", "sex": "f",
         "family": "Dana Nakamura", "phone": "555-0866", "clinic_id": "cx_015",
         "tag": "WC-0480", "service_level": "individual", "election_ref": "EL-0480",
         "intake_at": iso(now() - timedelta(days=16)),
         "custody": chain("WC-0480", 4, now() - timedelta(days=16)),
         "ashes_ready_at": iso(now() - timedelta(days=12)),
         "keepsakes": {"engraving": {"text": "Olive · 2014–2026 · Good girl, forever",
                                     "proof_drafted_at": iso(now() - timedelta(days=3))}},
         "demo_tag": "demo"},
        # the aged-remains case — Pepper, at the policy clock (200 days > 180)
        {"id": "pt_demo_aged", "name": "Pepper", "species": "dog", "sex": "m",
         "family": "Iris Calloway", "phone": "555-0977", "clinic_id": "cx_019",
         "tag": "WC-0311", "service_level": "individual", "election_ref": "EL-0311",
         "intake_at": iso(now() - timedelta(days=210)),
         "custody": chain("WC-0311", 4, now() - timedelta(days=210)),
         "ashes_ready_at": iso(now() - timedelta(days=200)), "demo_tag": "demo"},
        # Cooper — the status ask + the offered-once rule
        {"id": "pt_demo_status", "name": "Cooper", "species": "dog", "sex": "m",
         "family": "Tess Ashworth", "phone": "555-0288", "clinic_id": "cx_021",
         "tag": "WC-0533", "service_level": "individual", "election_ref": "EL-0533",
         "intake_at": iso(now() - timedelta(days=5)),
         "custody": chain("WC-0533", 4, now() - timedelta(days=5)),
         "ashes_ready_at": iso(now() - timedelta(days=1)), "demo_tag": "demo"},
        # Milo — the return arrangement
        {"id": "pt_demo_return", "name": "Milo", "species": "cat", "sex": "m",
         "family": "Ade Okafor", "phone": "555-0399", "clinic_id": "cx_024",
         "tag": "WC-0544", "service_level": "communal", "election_ref": "EL-0544",
         "intake_at": iso(now() - timedelta(days=4)),
         "custody": chain("WC-0544", 4, now() - timedelta(days=4)),
         "ashes_ready_at": iso(now() - timedelta(days=1)), "demo_tag": "demo"},
        # Daisy — the add-on order
        {"id": "pt_demo_addon", "name": "Daisy", "species": "dog", "sex": "f",
         "family": "Ruth Barrera", "phone": "555-0410", "clinic_id": "cx_027",
         "tag": "WC-0555", "service_level": "individual", "election_ref": "EL-0555",
         "intake_at": iso(now() - timedelta(days=3)),
         "custody": chain("WC-0555", 3, now() - timedelta(days=3)), "demo_tag": "demo"},
    ]
    store.save("pets", pets)

    loads = [
        {"id": "ld_demo_communal", "kind": "communal", "at": iso(),
         "pets": ["pt_demo_com1"], "demo_tag": "demo"},
        {"id": "ld_demo_private", "kind": "private", "at": iso(),
         "pets": ["pt_demo_private"], "demo_tag": "demo"},
    ]
    store.save("loads", loads)

    messages = [{"id": f"ms_{i:03d}", "from": f"{rng.choice(['Sam', 'Ana', 'Lee', 'Mara'])} "
                                              f"{rng.choice(FAMILIES)}",
                 "text": t, "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages += [
        {"id": "ms_demo_worry", "from": "Ellery Whitcomb", "pet_id": "pt_demo_max",
         "text": "how do I know these are really Max's ashes",
         "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"},
        {"id": "ms_demo_clinic", "from": "Riverbend Animal Hospital", "clinic_id": "cx_000",
         "text": "riverbend animal hospital has three patients ready for pickup",
         "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"},
        {"id": "ms_demo_status", "from": "Tess Ashworth", "pet_id": "pt_demo_status",
         "text": "any update on Cooper? we miss him",
         "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"},
        {"id": "ms_demo_status2", "from": "Tess Ashworth", "pet_id": "pt_demo_status",
         "text": "is Cooper ready to come home yet",
         "at": iso(now() - timedelta(minutes=10)), "demo_tag": "demo"},
        {"id": "ms_demo_addon", "from": "Ruth Barrera", "pet_id": "pt_demo_addon",
         "text": "we'd like to add a paw print keepsake for Daisy",
         "at": iso(now() - timedelta(minutes=65)), "demo_tag": "demo"},
        {"id": "ms_demo_return", "from": "Ade Okafor", "pet_id": "pt_demo_return",
         "text": "can you deliver Milo's ashes to our house on saturday",
         "at": iso(now() - timedelta(minutes=80)), "demo_tag": "demo"},
    ]
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"pets": len(pets), "clinics": len(clinics)})
    print(f"Seeded {len(pets)} pets, {len(clinics)} clinics, {len(loads)} chamber loads, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
