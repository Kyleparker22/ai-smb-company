#!/usr/bin/env python3
"""Consign OS — synthetic Second Story Consignment. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(50)

LAST = ["Ashford", "Bellamy", "Cadena", "Duval", "Eastman", "Fiore", "Grantham", "Hobbs",
        "Ibarra", "Jessup", "Kimura", "Lockhart", "Moss", "Novak", "Ortega", "Pemberton",
        "Quill", "Ramsey", "Soto", "Tibbets"]
TITLES = [("mid-century walnut dresser", "furniture", 220), ("brass floor lamp", "home", 65),
          ("leather club chair", "furniture", 340), ("cast iron dutch oven", "kitchen", 45),
          ("wool peacoat", "apparel", 85), ("oak bookshelf", "furniture", 130),
          ("ceramic table lamp", "home", 40), ("vintage denim jacket", "apparel", 55),
          ("teak patio set", "outdoor", 410), ("stand mixer", "kitchen", 120)]
MESSAGES = [
    "would you take $40 for the dresser",
    "is the gucci belt authentic",
    "when can i pick up the bookshelf",
    "what are your hours on sunday",
]


def main():
    store.wipe()
    store.save("config", {"company": "Second Story Consignment", "storefronts": 2,
                          "channels": list(core.CHANNELS)})

    consignors = [{"id": f"cn_{i:03d}", "name": f"{rng.choice(LAST)}"} for i in range(60)]
    # one consignor with a recorded non-default split, so agreement_for is exercised
    consignors[0].update(name="Pemberton", consignor_split=0.5)
    store.save("consignors", consignors)

    items = []
    for i in range(400):
        title, cat, price = rng.choice(TITLES)
        cn = rng.choice(consignors)
        intake = now() - timedelta(days=rng.randint(0, 110))
        it = {"id": f"it_{i:03d}", "consignor_id": cn["id"], "title": title, "category": cat,
              "intake_at": iso(intake),
              "condition_notes": rng.choice(["light wear, one scuff on the left side",
                                             "excellent, no visible flaws recorded",
                                             "water ring on top surface, noted at intake",
                                             None]),
              "dimensions": rng.choice(['36" × 18" × 30"', None]),
              "list_price": price, "floor_price": round(price * 0.6),
              "status": "intake"}
        r = rng.random()
        if r < 0.55 and it["condition_notes"]:
            it["status"] = "listed"
            it["listed_at"] = iso(intake + timedelta(days=rng.randint(1, 5)))
        elif r < 0.8 and it["condition_notes"]:
            it["status"] = "sold"
            it["listed_at"] = iso(intake + timedelta(days=2))
            it["sold_at"] = iso(intake + timedelta(days=rng.randint(5, 40)))
            it["sold_price"] = round(price * rng.choice([1.0, 0.8, 0.6]), 2)
            if rng.random() < 0.6:
                it["paid_out_at"] = iso(now() - timedelta(days=rng.randint(1, 30)))
        items.append(it)

    # -- the demo set -------------------------------------------------------
    items += [
        # the counterfeit claim + authenticity pair
        {"id": "it_demo_lv", "consignor_id": "cn_001", "title": "monogram handbag",
         "category": "apparel", "intake_at": iso(now() - timedelta(days=9)),
         "condition_notes": "corner wear, patina on handles, noted at intake",
         "list_price": 480, "floor_price": 400, "status": "listed",
         "listed_at": iso(now() - timedelta(days=7)),
         "brand_claim": "Louis Vuitton", "demo_tag": "demo"},
        {"id": "it_demo_cert", "consignor_id": "cn_002", "title": "leather belt",
         "category": "apparel", "intake_at": iso(now() - timedelta(days=12)),
         "condition_notes": "unworn, tags attached", "list_price": 190, "floor_price": 150,
         "status": "listed", "listed_at": iso(now() - timedelta(days=10)),
         "brand_claim": "Gucci",
         "auth_cert": {"authenticator": "Meridian Authentication Co.", "ref": "MA-88412"},
         "demo_tag": "demo"},
        # the offer clamp
        {"id": "it_demo_dresser", "consignor_id": "cn_003",
         "title": "mid-century walnut dresser", "category": "furniture",
         "intake_at": iso(now() - timedelta(days=20)),
         "condition_notes": "light wear, one scuff on the left side",
         "list_price": 220, "floor_price": 55, "status": "listed",
         "listed_at": iso(now() - timedelta(days=18)), "demo_tag": "demo"},
        {"id": "it_demo_nofloor", "consignor_id": "cn_004", "title": "brass floor lamp",
         "category": "home", "intake_at": iso(now() - timedelta(days=6)),
         "condition_notes": "excellent", "list_price": 65, "floor_price": None,
         "status": "listed", "listed_at": iso(now() - timedelta(days=5)), "demo_tag": "demo"},
        # the wall
        {"id": "it_demo_recall", "consignor_id": "cn_005", "title": "drop-side crib",
         "category": "kids", "intake_at": iso(now() - timedelta(days=1)),
         "condition_notes": "good condition", "list_price": 80, "floor_price": 40,
         "status": "intake", "demo_tag": "demo"},
        {"id": "it_demo_nocond", "consignor_id": "cn_006", "title": "ceramic table lamp",
         "category": "home", "intake_at": iso(now() - timedelta(days=2)),
         "condition_notes": None, "list_price": 40, "floor_price": 20,
         "status": "intake", "demo_tag": "demo"},
        # the clock
        {"id": "it_demo_interm", "consignor_id": "cn_007", "title": "oak bookshelf",
         "category": "furniture", "intake_at": iso(now() - timedelta(days=32)),
         "condition_notes": "solid, shelf pins complete", "list_price": 130, "floor_price": 80,
         "status": "listed", "listed_at": iso(now() - timedelta(days=30)), "demo_tag": "demo"},
        {"id": "it_demo_reclaim", "consignor_id": "cn_008", "title": "wool peacoat",
         "category": "apparel", "intake_at": iso(now() - timedelta(days=72)),
         "condition_notes": "two buttons replaced, noted", "list_price": 85, "floor_price": 40,
         "status": "listed", "listed_at": iso(now() - timedelta(days=70)), "demo_tag": "demo"},
        {"id": "it_demo_expired", "consignor_id": "cn_009", "title": "vintage denim jacket",
         "category": "apparel", "intake_at": iso(now() - timedelta(days=100)),
         "condition_notes": "faded, small tear at cuff, noted", "list_price": 55,
         "floor_price": 25, "status": "listed",
         "listed_at": iso(now() - timedelta(days=98)), "demo_tag": "demo"},
        # the ledger
        {"id": "it_demo_sold", "consignor_id": "cn_000", "title": "teak patio set",
         "category": "outdoor", "intake_at": iso(now() - timedelta(days=30)),
         "condition_notes": "weathered evenly, structurally sound",
         "list_price": 410, "floor_price": 250, "status": "sold",
         "listed_at": iso(now() - timedelta(days=28)),
         "sold_at": iso(now() - timedelta(days=3)), "sold_price": 380, "demo_tag": "demo"},
        {"id": "it_demo_nosplit", "consignor_id": "cn_010", "title": "stand mixer",
         "category": "kitchen", "intake_at": iso(now() - timedelta(days=25)),
         "condition_notes": "all attachments present", "list_price": 120, "floor_price": 70,
         "status": "sold", "listed_at": iso(now() - timedelta(days=23)),
         "sold_at": iso(now() - timedelta(days=2)), "sold_price": None, "demo_tag": "demo"},
    ]
    store.save("items", items)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages += [
        {"id": "ms_demo_fake", "from": "Ramsey",
         "text": "the louis vuitton bag i bought yesterday is a fake",
         "item_id": "it_demo_lv", "at": iso(now() - timedelta(minutes=15)),
         "demo_tag": "demo"},
        {"id": "ms_demo_auth", "from": "Soto", "text": "is the gucci belt authentic",
         "item_id": "it_demo_cert", "at": iso(now() - timedelta(minutes=25)),
         "demo_tag": "demo"},
        {"id": "ms_demo_offer", "from": "Duval", "text": "would you take $40 for the dresser",
         "item_id": "it_demo_dresser", "offer_amount": 40,
         "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"},
        {"id": "ms_demo_offer_ok", "from": "Moss", "text": "how about $60 for the dresser",
         "item_id": "it_demo_dresser", "offer_amount": 60,
         "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"},
        {"id": "ms_demo_nofloor", "from": "Quill", "text": "can you do 30 on the brass lamp",
         "item_id": "it_demo_nofloor", "offer_amount": 30,
         "at": iso(now() - timedelta(minutes=45)), "demo_tag": "demo"},
        {"id": "ms_demo_payout", "from": "Pemberton",
         "text": "when do i get paid for my items that sold",
         "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"},
    ]
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"items": len(items)})
    print(f"Seeded {len(consignors)} consignors, {len(items)} items, {len(messages)} messages")


if __name__ == "__main__":
    main()
