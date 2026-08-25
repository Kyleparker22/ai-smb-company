#!/usr/bin/env python3
"""Route OS — synthetic pest company. `python3 seed.py [--accounts 6800]`.

"Sentry Pest Solutions" — recurring accounts, 6 months of services incl.
skips, messages incl. exposure and safety questions. Synthetic only.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(18)

STREETS = ["Alder Ct", "Bramble Way", "Cedarbrook Ln", "Dove Hollow Rd", "Elmcrest Dr",
           "Foxglove Ave", "Gladehill St", "Harvest Bend", "Ivystone Cir", "Juniper Pass"]
MESSAGES = [
    "my dog licked the baseboard where they sprayed",
    "is it safe for the kids to go back inside now",
    "still seeing ants in the kitchen after last week",
    "please cancel the service, we're moving",
    "can we reschedule to thursday, gate code is 4482",
    "thanks for the great service today",
]
SKIP_REASONS = ["locked gate", "no access", "weather", "customer asked to skip"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--accounts", type=int, default=6800)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Sentry Pest Solutions", "revenue": "$4.5M",
                          "routes": 14, "crm": "modelled, not connected"})

    accounts, services = [], []
    for i in range(args.accounts):
        a = {"id": f"ac_{i:05d}", "name": f"{rng.randint(100,9999)} {rng.choice(STREETS)}",
             "status": "active" if rng.random() < 0.94 else "cancelled",
             "annual_value": rng.choice([420, 480, 540, 660, 840]),
             "payment_issue": rng.random() < 0.04,
             "complaint_open": rng.random() < 0.02}
        accounts.append(a)
        # quarterly-ish service history (light for volume)
        if i < 1500:
            for m in range(2):
                sched = now() - timedelta(days=rng.randint(5, 170))
                status = rng.choices(["completed", "skipped"], weights=[0.93, 0.07])[0]
                s = {"id": store.nid("sv"), "account_id": a["id"],
                     "kind": rng.choices(["regular", "reservice"], weights=[0.9, 0.1])[0],
                     "scheduled_at": iso(sched), "status": status}
                if status == "completed":
                    s["completed_at"] = iso(sched + timedelta(hours=3))
                else:
                    s["skip_reason"] = rng.choice(SKIP_REASONS)
                services.append(s)

    # demo rows: a skipped service to try billing, and fresh messages
    services.append({"id": "sv_demo_skip", "account_id": accounts[0]["id"], "kind": "regular",
                     "scheduled_at": iso(now() - timedelta(days=3)), "status": "skipped",
                     "skip_reason": "locked gate", "demo_tag": "demo"})
    services.append({"id": "sv_demo_done", "account_id": accounts[0]["id"], "kind": "regular",
                     "scheduled_at": iso(now() - timedelta(days=2)), "status": "completed",
                     "completed_at": iso(now() - timedelta(days=2)), "demo_tag": "demo"})

    messages = [{"id": f"ms_{i:03d}", "account_id": rng.choice(accounts)["id"], "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 4)]
    messages.append({"id": "ms_demo_exposure", "account_id": accounts[0]["id"],
                     "text": "my dog licked the baseboard where they sprayed",
                     "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_safety", "account_id": accounts[1]["id"],
                     "text": "is it safe for the kids to go back inside now",
                     "at": iso(now() - timedelta(hours=1)), "demo_tag": "demo"})

    store.save("accounts", accounts)
    store.save("services", services)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"accounts": len(accounts), "services": len(services)})
    print(f"Seeded {len(accounts)} accounts, {len(services)} services, {len(messages)} messages")


if __name__ == "__main__":
    main()
