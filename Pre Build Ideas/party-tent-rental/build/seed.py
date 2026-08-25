#!/usr/bin/env python3
"""Marquee OS — synthetic Fairfield Event Rentals. Synthetic only: invented
names, 555 phones, no real municipality's ordinance. The seeder draws from the
same counted stock the product does — it cannot oversell either."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(55)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel",
        "Osei", "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner",
        "Iglesias", "Thorne", "Ambrose", "Kowalski", "Nakamura", "Fontaine"]
STREETS = ["Harbor Lane", "Mill Pond Rd", "Orchard Hill Dr", "Beacon St",
           "Quarry Ridge Way", "Sycamore Ct", "Old Post Rd", "Larkspur Ave"]
MUNIS = ["Fairfield", "Ashford", "Belmont"]

INVENTORY = [
    {"id": "tent_20x20", "name": "20x20 frame tent", "stock": 8,
     "wind_rating_mph": 60, "day_rate": 350},
    {"id": "tent_20x30", "name": "20x30 frame tent", "stock": 6,
     "wind_rating_mph": 60, "day_rate": 450},
    {"id": "tent_30x60", "name": "30x60 pole tent", "stock": 4,
     "wind_rating_mph": 45, "day_rate": 900},
    {"id": "tent_40x60", "name": "40x60 pole tent", "stock": 2,
     "wind_rating_mph": 40, "day_rate": 1600},
    {"id": "table_round_60", "name": "60\" round table", "stock": 150, "day_rate": 12},
    {"id": "chair_folding", "name": "white folding chair", "stock": 1500, "day_rate": 2},
    {"id": "dance_floor_12x12", "name": "12x12 dance floor", "stock": 3, "day_rate": 400},
]

MESSAGES = [
    "do you have a 20x30 tent available the first weekend of june",
    "need 200 chairs and 20 round tables for a graduation party",
    "can we add a dance floor to our order",
    "when do we get our deposit back",
    "what time is the crew arriving friday",
    "do you do fireworks too",
]


def main():
    store.wipe()
    store.save("config", {"company": "Fairfield Event Rentals",
                          "crews": 2, "phone": "(555) 014-2280"})
    store.save("inventory", INVENTORY)

    # -- the two weekends: next Saturday, and the one after (deliberately near capacity)
    ref = now()
    sat1 = ref + timedelta(days=((5 - ref.weekday()) % 7 or 7))
    sat2 = sat1 + timedelta(days=7)
    sat_prev = sat1 - timedelta(days=7)          # last weekend, for deposit demos

    avail = {w: {i["id"]: i["stock"] for i in INVENTORY}
             for w in (sat1.date().isoformat(), sat2.date().isoformat())}

    # the demo fixtures below hold real weekend-1 stock — reserve it FIRST so
    # the random deal cannot oversell what they hold (the seeder counts too)
    for iid, q in {"tent_40x60": 1, "tent_20x20": 1, "tent_30x60": 1, "tent_20x30": 1,
                   "chair_folding": 300, "table_round_60": 15}.items():
        avail[sat1.date().isoformat()][iid] -= q

    def take(w, iid, qty):
        if avail[w][iid] >= qty:
            avail[w][iid] -= qty
            return qty
        got = avail[w][iid]
        avail[w][iid] = 0
        return got

    # weekend 2 is the crunch: every 40x60, every 30x60, most frame tents
    tent_plan = {
        sat1.date().isoformat(): (["tent_30x60"] * 2 + ["tent_20x30"] * 3 +
                                  ["tent_20x20"] * 4),
        sat2.date().isoformat(): (["tent_40x60"] * 2 + ["tent_30x60"] * 4 +
                                  ["tent_20x30"] * 5 + ["tent_20x20"] * 7),
    }

    bookings, n = [], 0
    for sat, plan in ((sat1, tent_plan[sat1.date().isoformat()]),
                      (sat2, tent_plan[sat2.date().isoformat()])):
        w = sat.date().isoformat()
        non_tent = 24 - len(plan)
        for tent_id in plan + [None] * non_tent:
            n += 1
            day = sat + timedelta(days=rng.choice([0, 0, 1]))
            muni = rng.choice(MUNIS)
            items = {}
            if tent_id:
                items[tent_id] = take(w, tent_id, 1)
            q = take(w, "chair_folding", rng.choice([40, 60, 80, 100]))
            if q:
                items["chair_folding"] = q
            q = take(w, "table_round_60", rng.choice([5, 8, 10, 12]))
            if q:
                items["table_round_60"] = q
            if tent_id and rng.random() < 0.3:
                q = take(w, "dance_floor_12x12", 1)
                if q:
                    items["dance_floor_12x12"] = q
            b = {"id": f"bk_{n:03d}", "customer_name": rng.choice(LAST),
                 "event_date": day.date().isoformat(), "weekend": w,
                 "site": f"{rng.randint(4, 96)} {rng.choice(STREETS)}, {muni}",
                 "municipality": muni, "items": items, "status": "confirmed",
                 "deposit_amount": rng.choice([200, 300, 500, 800]),
                 "booked_at": iso(ref - timedelta(days=rng.randint(2, 45))),
                 "phone": f"(555) 01{rng.randint(0, 9)}-{rng.randint(1000, 9999)}"}
            if tent_id:
                b["site_checklist"] = {"locate_ticket": f"811-2026-{4400 + n}",
                                       "surface": rng.choice(["lawn", "gravel", "asphalt"]),
                                       "power": rng.choice(["house", "generator"])}
                rule = core.DEFAULT_PERMIT_RULES["municipalities"][muni]
                if core.tent_sqft(items) >= rule["tent_sqft_threshold"]:
                    b["permit_ref"] = f"TP-2026-{700 + n}"
            bookings.append(b)

    # -- demo fixtures (demo_tag: sweeps skip them; the buttons press them) ----
    w1 = sat1.date().isoformat()
    bookings.append({
        "id": "bk_demo_gust", "customer_name": "Renner", "demo_tag": "demo",
        "event_date": w1, "weekend": w1,
        "site": f"27 Harbor Lane, Fairfield", "municipality": "Fairfield",
        "items": {"tent_40x60": 1, "chair_folding": 120, "table_round_60": 15},
        "status": "confirmed", "deposit_amount": 500,
        "booked_at": iso(ref - timedelta(days=30)),
        "forecast": {"gust_mph": 50, "recorded_at": iso(ref - timedelta(hours=3)),
                     "source": "recorded forecast entry for the site and date"},
        "site_checklist": {"locate_ticket": "811-2026-5117", "surface": "lawn",
                           "power": "generator"},
        "permit_ref": "TP-2026-771", "phone": "(555) 012-8841"})
    bookings.append({
        "id": "bk_demo_no811", "customer_name": "Okafor", "demo_tag": "demo",
        "event_date": w1, "weekend": w1,
        "site": "8 Quarry Ridge Way, Ashford", "municipality": "Ashford",
        "items": {"tent_20x20": 1, "chair_folding": 40}, "status": "confirmed",
        "deposit_amount": 200, "booked_at": iso(ref - timedelta(days=12)),
        "site_checklist": {"surface": "lawn", "power": "house"},
        "phone": "(555) 016-3374"})
    bookings.append({
        "id": "bk_demo_permit", "customer_name": "Fontaine", "demo_tag": "demo",
        "event_date": w1, "weekend": w1,
        "site": "51 Beacon St, Belmont", "municipality": "Belmont",
        "items": {"tent_30x60": 1, "chair_folding": 80}, "status": "confirmed",
        "deposit_amount": 300, "booked_at": iso(ref - timedelta(days=8)),
        "site_checklist": {"locate_ticket": "811-2026-5240", "surface": "lawn",
                           "power": "house"}, "phone": "(555) 019-6620"})
    bookings.append({
        "id": "bk_demo_muni", "customer_name": "Ambrose", "demo_tag": "demo",
        "event_date": w1, "weekend": w1,
        "site": "3 Old Post Rd, Kern Township", "municipality": "Kern Township",
        "items": {"tent_20x30": 1, "chair_folding": 60}, "status": "confirmed",
        "deposit_amount": 300, "booked_at": iso(ref - timedelta(days=6)),
        "site_checklist": {"locate_ticket": "811-2026-5251", "surface": "gravel",
                           "power": "house"}, "phone": "(555) 013-9082"})
    # last weekend, back in the yard: the deposit demos
    for bid, cust, dep in (("bk_demo_dep_full", "Havel", 500),
                           ("bk_demo_dep_partial", "Trujillo", 400),
                           ("bk_demo_dep_clean", "Yamada", 500)):
        bookings.append({
            "id": bid, "customer_name": cust, "demo_tag": "demo",
            "event_date": sat_prev.date().isoformat(),
            "weekend": sat_prev.date().isoformat(),
            "site": f"{rng.randint(4, 96)} {rng.choice(STREETS)}, Fairfield",
            "municipality": "Fairfield",
            "items": {"tent_20x30": 1, "chair_folding": 60}, "status": "completed",
            "deposit_amount": dep, "booked_at": iso(ref - timedelta(days=40)),
            "phone": f"(555) 017-{rng.randint(1000, 9999)}"})
    store.save("bookings", bookings)

    conditions = [
        {"id": "cd_out_full", "booking_id": "bk_demo_dep_full", "kind": "out",
         "notes": "sidewalls clean; two chairs with existing scuffs noted",
         "damage": [{"item": "chair scuffs (pre-existing)", "cost": 0}], "photos": 9},
        {"id": "cd_ret_full", "booking_id": "bk_demo_dep_full", "kind": "return",
         "notes": "one sidewall stained on return; scuffed chairs unchanged",
         "damage": [{"item": "chair scuffs (pre-existing)", "cost": 0},
                    {"item": "sidewall stained", "cost": 150}], "photos": 11},
        {"id": "cd_out_partial", "booking_id": "bk_demo_dep_partial", "kind": "out",
         "notes": "all items clean at load-out", "damage": [], "photos": 7},
        # bk_demo_dep_partial deliberately has NO return record — the refusal demo
        {"id": "cd_out_clean", "booking_id": "bk_demo_dep_clean", "kind": "out",
         "notes": "all items clean at load-out", "damage": [], "photos": 8},
        {"id": "cd_ret_clean", "booking_id": "bk_demo_dep_clean", "kind": "return",
         "notes": "all items clean on return", "damage": [], "photos": 8},
    ]
    store.save("conditions", conditions)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(ref - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_gust", "from": "Renner", "demo_tag": "demo",
                     "booking_id": "bk_demo_gust",
                     "text": "they're calling for 50mph gusts saturday, is the tent safe "
                             "for the reception",
                     "at": iso(ref - timedelta(minutes=20))})
    messages.append({"id": "ms_demo_book", "from": "Kowalski", "demo_tag": "demo",
                     "text": "do you have a 40x60 tent available that saturday",
                     "wants": {"tent_40x60": 1}, "event_date": sat2.date().isoformat(),
                     "at": iso(ref - timedelta(minutes=35))})
    messages.append({"id": "ms_demo_deposit", "from": "Trujillo", "demo_tag": "demo",
                     "booking_id": "bk_demo_dep_partial",
                     "text": "when do we get our deposit back",
                     "at": iso(ref - timedelta(minutes=50))})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"bookings": len(bookings), "inventory": len(INVENTORY)})
    print(f"Seeded {len(INVENTORY)} inventory lines, {len(bookings)} bookings "
          f"({sat1.date()} and {sat2.date()} weekends; the second near capacity), "
          f"{len(conditions)} condition records, {len(messages)} messages")


if __name__ == "__main__":
    main()
