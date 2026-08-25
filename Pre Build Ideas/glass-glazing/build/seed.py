#!/usr/bin/env python3
"""Pane OS — synthetic Clearview Glass Co. Synthetic only: invented names,
555 phones, nothing real."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(59)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne",
        "Vann", "Soriano", "Kwiatkowski", "Ademola"]
CREW = ["Reyes (crew A)", "Okafor (crew A)", "Lindqvist (crew B)", "Bostic (crew B)"]
JOBS = {"shower": (1800, 34.0, 76.0), "storefront": (3200, 60.0, 84.0),
        "window": (650, 36.0, 48.0), "mirror": (420, 48.0, 36.0), "door": (900, 34.0, 78.0)}
MESSAGES = [
    "is my shower glass ready yet",
    "how much for a frameless shower door",
    "our window is all foggy between the panes",
    "what time do you open saturday",
]


def _pair(w, h, kind):
    """Measurement fixtures: matched | single | mismatched (beyond tolerance)."""
    a = {"by": rng.choice(CREW), "at": iso(now() - timedelta(days=rng.randint(4, 20))),
         "width_in": w, "height_in": h}
    if kind == "single":
        return [a]
    if kind == "mismatched":
        b = dict(a, by=rng.choice(CREW), at=iso(now() - timedelta(days=rng.randint(1, 3))),
                 width_in=round(w + rng.choice([0.25, 0.375, 0.5, 0.75]), 4))
        return [a, b]
    b = dict(a, by=rng.choice(CREW), at=iso(now() - timedelta(days=rng.randint(1, 3))),
             width_in=round(w + rng.choice([0.0, 0.0625]), 4),
             height_in=round(h + rng.choice([0.0, 0.0625]), 4))
    return [a, b]


def main():
    store.wipe()
    store.save("config", {
        "company": "Clearview Glass Co.", "crews": 2,
        "fabricator": "Summit Glass Fabrication", "deposit_pct": 50,
        "measurement_tolerance": core.DEFAULT_TOLERANCE,
        "safety_rules": core.DEFAULT_SAFETY_RULES,
    })

    customers = [{"id": f"cu_{i:03d}", "name": rng.choice(LAST),
                  "phone": f"555-01{i % 90:02d}"} for i in range(160)]
    store.save("customers", customers)

    orders = []
    stages = ["quote"] * 50 + ["deposit"] * 45 + ["fabrication"] * 40 + ["install"] * 20 \
             + ["done"] * 45
    for i, stage in enumerate(stages):
        jt = rng.choice(list(JOBS))
        amount, w, h = JOBS[jt]
        amount = round(amount * rng.uniform(0.8, 1.3))
        o = {"id": f"or_{i:03d}", "customer_name": rng.choice(LAST), "job_type": jt,
             "amount": amount, "stage": stage,
             "created_at": iso(now() - timedelta(days=rng.randint(2, 360)))}
        if stage == "deposit":
            kind = rng.choices(["matched", "single", "mismatched"], [70, 20, 10])[0]
            o["measurements"] = _pair(w, h, kind)
            if rng.random() < 0.6:
                o["deposit_paid_at"] = iso(now() - timedelta(days=rng.randint(0, 12)))
                o["deposit_amount"] = round(amount * 0.5)
        elif stage in ("fabrication", "install", "done"):
            o["measurements"] = _pair(w, h, "matched")
            o["deposit_paid_at"] = iso(now() - timedelta(days=rng.randint(10, 60)))
            o["deposit_amount"] = round(amount * 0.5)
            o["released_at"] = iso(now() - timedelta(days=rng.randint(5, 45)))
            o["fabricator_promised_at"] = iso(now() + timedelta(days=rng.randint(3, 21))) \
                if stage == "fabrication" else iso(now() - timedelta(days=rng.randint(1, 30)))
            if stage == "install":
                o["install_scheduled_at"] = iso(now() + timedelta(days=rng.randint(1, 10)))
            if stage == "done":
                o["installed_at"] = iso(now() - timedelta(days=rng.randint(1, 350)))
        orders.append(o)

    for i in range(8):  # board-up history — the counted capture number
        orders.append({"id": f"or_bu_{i:02d}", "customer_name": rng.choice(LAST),
                       "job_type": "board_up", "amount": rng.choice([350, 425, 500]),
                       "stage": "done",
                       "created_at": iso(now() - timedelta(days=rng.randint(5, 340))),
                       "installed_at": iso(now() - timedelta(days=rng.randint(5, 340)))})

    # -- demo fixtures (demo_tag: sweeps skip them; the demo buttons drive them)
    orders += [
        {"id": "or_demo_single", "customer_name": "Soriano", "job_type": "shower",
         "amount": 1840, "stage": "deposit", "demo_tag": "demo",
         "deposit_paid_at": iso(now() - timedelta(days=2)), "deposit_amount": 920,
         "measurements": [{"by": "Reyes (crew A)", "at": iso(now() - timedelta(days=3)),
                           "width_in": 36.0, "height_in": 72.0}]},
        {"id": "or_demo_mismatch", "customer_name": "Kwiatkowski", "job_type": "shower",
         "amount": 2050, "stage": "deposit", "demo_tag": "demo",
         "deposit_paid_at": iso(now() - timedelta(days=2)), "deposit_amount": 1025,
         "measurements": [
             {"by": "Reyes (crew A)", "at": iso(now() - timedelta(days=4)),
              "width_in": 36.0, "height_in": 72.0},
             {"by": "Okafor (crew A)", "at": iso(now() - timedelta(days=1)),
              "width_in": 36.5, "height_in": 72.0}]},
        {"id": "or_demo_matched", "customer_name": "Ademola", "job_type": "shower",
         "amount": 1920, "stage": "deposit", "demo_tag": "demo",
         "deposit_paid_at": iso(now() - timedelta(days=1)), "deposit_amount": 960,
         "measurements": [
             {"by": "Reyes (crew A)", "at": iso(now() - timedelta(days=4)),
              "width_in": 36.0, "height_in": 72.0},
             {"by": "Lindqvist (crew B)", "at": iso(now() - timedelta(days=1)),
              "width_in": 36.0625, "height_in": 72.0}]},
        {"id": "or_demo_nodeposit", "customer_name": "Vann", "job_type": "storefront",
         "amount": 3400, "stage": "deposit", "demo_tag": "demo",
         "measurements": [
             {"by": "Bostic (crew B)", "at": iso(now() - timedelta(days=5)),
              "width_in": 60.0, "height_in": 84.0},
             {"by": "Reyes (crew A)", "at": iso(now() - timedelta(days=2)),
              "width_in": 60.0, "height_in": 84.0625}]},
        {"id": "or_demo_undated", "customer_name": "Trujillo", "job_type": "shower",
         "amount": 1750, "stage": "fabrication", "demo_tag": "demo",
         "deposit_paid_at": iso(now() - timedelta(days=8)), "deposit_amount": 875,
         "released_at": iso(now() - timedelta(days=6)),
         "measurements": _pair(34.0, 76.0, "matched")},
        {"id": "or_demo_dated", "customer_name": "Delacroix", "job_type": "storefront",
         "amount": 3100, "stage": "fabrication", "demo_tag": "demo",
         "deposit_paid_at": iso(now() - timedelta(days=12)), "deposit_amount": 1550,
         "released_at": iso(now() - timedelta(days=10)),
         "fabricator_promised_at": iso(now() + timedelta(days=9)),
         "measurements": _pair(60.0, 84.0, "matched")},
    ]
    store.save("orders", orders)

    remakes = []
    causes = ["measure"] * 10 + ["fab"] * 6 + ["install"] * 4 + ["customer"] * 2
    for i, cause in enumerate(causes):
        remakes.append({"id": f"rm_{i:03d}", "order_id": f"or_{rng.randint(155, 199):03d}",
                        "cause": cause, "cost": rng.choice([320, 540, 780, 1150, 1400]),
                        "at": iso(now() - timedelta(days=rng.randint(3, 360))),
                        "note": "recorded at remake time with its cause code"})
    store.save("remakes", remakes)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "phone": "555-0155",
                 "text": t, "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages += [
        {"id": "ms_demo_breakin", "from": "Marisol Vann", "phone": "555-0134",
         "text": "someone smashed our storefront window, glass everywhere, we're open "
                 "to the street",
         "at": iso(now() - timedelta(minutes=15)), "demo_tag": "demo"},
        {"id": "ms_demo_annealed", "from": "Pruitt", "phone": "555-0161",
         "text": "how much for a new glass panel in our back door",
         "quote_request": {"location": "door", "glass_type": "annealed",
                           "width_in": 34, "height_in": 78},
         "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"},
        {"id": "ms_demo_leadtime", "from": "Trujillo", "phone": "555-0126",
         "text": "when can you have the shower glass in and installed",
         "order_id": "or_demo_undated",
         "at": iso(now() - timedelta(hours=2)), "demo_tag": "demo"},
        {"id": "ms_demo_status", "from": "Delacroix", "phone": "555-0119",
         "text": "any update on the storefront glass order",
         "order_id": "or_demo_dated",
         "at": iso(now() - timedelta(hours=3)), "demo_tag": "demo"},
    ]
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"orders": len(orders), "remakes": len(remakes)})
    print(f"Seeded {len(customers)} customers, {len(orders)} orders, {len(remakes)} remakes, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
