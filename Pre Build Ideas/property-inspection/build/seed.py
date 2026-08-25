#!/usr/bin/env python3
"""Inspect OS — synthetic Keystone Property Inspections. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(36)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
AGENTS = ["Hendricks Realty", "Bluestone Group", "Lakeway Brokers", "Fifth & Main Realty"]
FINDINGS = [("roof: three lifted shingles at the south valley, active daylight at decking", "major"),
            ("electrical: double-tapped breaker at panel position 14", "major"),
            ("plumbing: slow drain and corrosion at the main stack cleanout", "minor"),
            ("grading: negative slope at the NE corner, moisture at sill", "major"),
            ("HVAC: filter overdue, coil icing observed", "minor")]
MESSAGES = [
    "is the report ready yet",
    "how much would it cost to fix the deck issue you found",
    "need to book an inspection before closing on the 28th",
    "thanks for being so thorough yesterday",
]


def main():
    store.wipe()
    store.save("config", {"company": "Keystone Property Inspections", "inspectors": 6,
                          "revenue": "$1.4M"})

    inspections = []
    for i in range(140):
        done = rng.random() < 0.8
        insp = {"id": f"in_{i:03d}", "client_name": f"{rng.choice(LAST)}",
                "address": f"{rng.randint(100, 999)} {rng.choice(['Maple', 'Cedar', 'Elm', 'Lake'])} St",
                "inspected_at": iso(now() - timedelta(days=rng.randint(0, 60))) if done else None}
        if done and rng.random() < 0.9:
            insp["report_sent_at"] = iso((now() - timedelta(days=rng.randint(0, 59))))
        inspections.append(insp)
    inspections.append({"id": "in_demo", "client_name": "Dana Okafor",
                        "address": "412 Maple St",
                        "inspected_at": iso(now() - timedelta(hours=6)),
                        "release_authorized": [], "demo_tag": "demo"})
    store.save("inspections", inspections)

    findings = []
    for i in range(200):
        text, sev = rng.choice(FINDINGS)
        findings.append({"id": f"fn_{i:04d}",
                         "inspection_id": rng.choice(inspections)["id"],
                         "text": text, "severity": sev,
                         "at": iso(now() - timedelta(days=rng.randint(0, 60))),
                         "supersedes": None})
    store.save("findings", findings)

    referrals = [{"id": f"rf_{i:03d}", "source": rng.choice(AGENTS + ["direct", "direct"])}
                 for i in range(80)]
    store.save("referrals", referrals)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_soften", "from": "Hendricks Realty",
                     "text": "any chance you could leave out the note about the roof",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_early", "from": "Hendricks Realty",
                     "inspection_id": "in_demo",
                     "text": "I'm the listing agent, can you send me the report before the buyer",
                     "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_cost", "from": "Dana Okafor",
                     "text": "how much would it cost to fix the deck issue you found",
                     "at": iso(now() - timedelta(minutes=55)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"inspections": len(inspections)})
    print(f"Seeded {len(inspections)} inspections, {len(findings)} findings, "
          f"{len(referrals)} referrals, {len(messages)} messages")


if __name__ == "__main__":
    main()
