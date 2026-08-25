#!/usr/bin/env python3
"""Halflife OS — synthetic Merrick & Vance (4-attorney PI/litigation firm).
Synthetic only: invented parties, invented custodians, 555 phones."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(64)
RET = core.DEFAULT_RETENTION["days"]

CLIENTS = ["Odell Ransom", "Renata Holloway", "Curtis Angeline", "Bea Okonkwo",
           "Marisol Vega", "Denny Kowalczyk", "Priya Ramanathan", "Gus Ferreira",
           "Lettie Marsh", "Hollis Trent", "Yusuf Adeyemi", "Carmen Delgadillo",
           "Ike Barrows", "Nadia Petrov", "Sam Whitlock", "Ada Lindqvist"]
OPPOSING = ["Pemberton Fuel Stop", "Bluff Road Logistics", "Carraway Markets",
            "Tri-County Transit", "Ridgeline Towing", "Halvorsen Paving",
            "Stateline Rideshare LLC", "Mercy General (synthetic)", "Kestrel Storage LLC",
            "Dockside Freight Co", "Yellow Pine Grocers", "Vantage Delivery"]
CASE_TYPES = ["auto", "premises", "dog_bite", "trucking"]

# (custodian_type, item type, source, custodian)
POOL = [
    ("gas_station_cctv", "footage", "forecourt camera", "Pemberton Fuel Stop"),
    ("municipal_camera", "footage", "intersection camera, 5th & Oak", "City of Fairview DOT"),
    ("retail_cctv", "footage", "parking-lot camera", "Carraway Markets"),
    ("residential_doorbell", "footage", "doorbell camera across the street", "homeowner (synthetic)"),
    ("transit_bus_camera", "footage", "bus forward dashcam", "Tri-County Transit"),
    ("rideshare_dashcam", "footage", "rideshare interior cam", "Stateline Rideshare LLC"),
    ("vehicle_edr", "edr", "event data recorder, defendant vehicle", "Ridgeline Towing"),
    ("tow_yard_vehicle_hold", "edr", "vehicle hold, lot 4", "Ridgeline Towing"),
    ("cell_carrier_records", "records", "call detail records", "carrier (synthetic), 555-0100"),
    ("police_bodycam", "records", "responding-officer bodycam", "Fairview PD records div."),
    ("hospital_records", "records", "ER intake records", "Mercy General (synthetic)"),
    ("witness_memory", "witness", "bystander witness", "witness (synthetic), 555-0142"),
]
LONG = [p for p in POOL if RET[p[0]] >= 120]

MESSAGES = [
    "any update on my case",
    "what's happening with the insurance claim",
    "did you get my medical records yet",
    "how long do i have to file after a car accident",
    "what time does your office open",
    "i was rear-ended on route 9 yesterday and my neck hurts",
]


def _mk_item(mid, incident, age):
    ct, typ, source, custodian = rng.choice(POOL if age < 100 else LONG)
    days = RET[ct]
    item = {"id": store.nid("ev"), "matter_id": mid, "type": typ, "source": source,
            "custodian": custodian, "custodian_type": ct,
            "created_at": iso(incident), "state": "at_large"}
    if typ == "witness":
        # a witness clock anchors on last recorded contact
        if age > 100:
            item["last_contact"] = iso(now() - timedelta(days=rng.randint(2, 60)))
        elif rng.random() < 0.6:
            item["last_contact"] = iso(incident + timedelta(days=rng.randint(0, 3)))
    expired = days <= age and not (typ == "witness" and item.get("last_contact"))
    if expired:
        if _mk_item.lost < 8 and rng.random() < 0.6:
            item.update(state="LOST", died_at=iso(incident + timedelta(days=days)),
                        was_on_notice=rng.random() < 0.4)
            _mk_item.lost += 1
        else:
            item.update(state="secured", receipt=f"RCPT-{rng.randint(1000, 9999)}",
                        secured_at=iso(incident + timedelta(days=rng.randint(1, max(2, days - 1)))))
    else:
        r = rng.random()
        if r < 0.25:
            item.update(state="on_notice", letter_drafted=True,
                        notice={"sent_at": iso(incident + timedelta(days=rng.randint(1, 5))),
                                "by": "amerrick"})
        elif r < 0.45:
            item.update(state="secured", receipt=f"RCPT-{rng.randint(1000, 9999)}",
                        secured_at=iso(now() - timedelta(days=rng.randint(0, min(age, 20)))))
    return item


_mk_item.lost = 0


def main():
    store.wipe()
    store.save("config", {"firm": "Merrick & Vance", "attorneys": 4,
                          "sub": "PI / litigation · evidence half-life ledger"})

    matters, evidence = [], []

    # -- the hot matter: the demo path's regular (non-demo-tagged) fixtures
    incident0 = now() - timedelta(days=21)
    m0 = {"id": "mat_000", "client": "Odell Ransom", "case_type": "auto",
          "opposing": "Pemberton Fuel Stop", "incident_date": iso(incident0),
          "stage": "intake", "opened_at": iso(now() - timedelta(days=20))}
    matters.append(m0)
    evidence += [
        # 21 days into a 30-day clock → 9 days left
        {"id": "ev_9days", "matter_id": "mat_000", "type": "footage",
         "source": "forecourt camera, pump 3", "custodian": "Pemberton Fuel Stop",
         "custodian_type": "gas_station_cctv", "created_at": iso(incident0),
         "state": "at_large"},
        # custodian type NOT in the retention table → UNKNOWN, tops the queue
        {"id": "ev_unknown", "matter_id": "mat_000", "type": "footage",
         "source": "yard camera over the fence line", "custodian": "Kestrel Storage LLC",
         "custodian_type": "private_warehouse_cam", "created_at": iso(incident0),
         "state": "at_large"},
        # a witness going stale: 100 days since contact on a 120-day window
        {"id": "ev_witness_stale", "matter_id": "mat_000", "type": "witness",
         "source": "bystander Marisol Vega, 555-0142", "custodian": "witness (synthetic)",
         "custodian_type": "witness_memory",
         "created_at": iso(now() - timedelta(days=130)),
         "last_contact": iso(now() - timedelta(days=100)), "state": "at_large"},
    ]

    # -- the lost ledger: history the queue counts but does not forgive
    old = now() - timedelta(days=80)
    evidence += [
        {"id": "ev_lost_notice", "matter_id": "mat_000", "type": "footage",
         "source": "loading-dock camera", "custodian": "Dockside Freight Co",
         "custodian_type": "retail_cctv", "created_at": iso(old), "state": "LOST",
         "died_at": iso(old + timedelta(days=45)), "was_on_notice": True},
        {"id": "ev_lost_quiet", "matter_id": "mat_000", "type": "footage",
         "source": "intersection camera, 5th & Oak", "custodian": "City of Fairview DOT",
         "custodian_type": "municipal_camera", "created_at": iso(old), "state": "LOST",
         "died_at": iso(old + timedelta(days=14)), "was_on_notice": False},
    ]

    # -- the book of business
    for i in range(1, 70):
        age = rng.randint(3, 24) if rng.random() < 0.6 else rng.randint(25, 150)
        incident = now() - timedelta(days=age)
        m = {"id": f"mat_{i:03d}", "client": rng.choice(CLIENTS),
             "case_type": rng.choice(CASE_TYPES), "opposing": rng.choice(OPPOSING),
             "incident_date": iso(incident),
             "stage": rng.choice(["intake", "signed", "treating", "records"]),
             "opened_at": iso(incident + timedelta(days=rng.randint(0, 4)))}
        matters.append(m)
        for _ in range(rng.randint(3, 5)):
            evidence.append(_mk_item(m["id"], incident, age))

    # -- demo fixtures (demo_tag → skipped by queue and sweeps)
    evidence.append({
        "id": "ev_demo_notice", "matter_id": "mat_000", "type": "footage",
        "source": "car-wash bay camera", "custodian": "Pemberton Fuel Stop",
        "custodian_type": "gas_station_cctv",
        "created_at": iso(now() - timedelta(days=5)), "state": "on_notice",
        "letter_drafted": True,
        "notice": {"sent_at": iso(now() - timedelta(days=3)), "by": "amerrick"},
        "demo_tag": "demo"})

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(CLIENTS),
                 "matter_id": f"mat_{rng.randint(1, 69):03d}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES)]
    messages.append({"id": "ms_demo_tip", "from": "Odell Ransom", "matter_id": "mat_000",
                     "text": "the gas station across the street probably has it on camera",
                     "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"})

    store.save("matters", matters)
    store.save("evidence", evidence)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"matters": len(matters), "evidence": len(evidence)})
    lost = sum(1 for e in evidence if e["state"] == "LOST")
    print(f"Seeded {len(matters)} matters, {len(evidence)} evidence items "
          f"({lost} LOST with history), {len(messages)} messages")


if __name__ == "__main__":
    main()
