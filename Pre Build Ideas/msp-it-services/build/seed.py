#!/usr/bin/env python3
"""Queue OS — synthetic MSP. `python3 seed.py [--tickets 500]`.

"Northgate Managed IT" — 18 people, ~60 agreements (gold/silver/bronze) with
real scope clauses, tickets incl. every security type and genuinely ambiguous
scope cases, one agreement with no tier. Synthetic only.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(14)

CLIENT_NAMES = ["Alder & Finch CPA", "Bellhaven Dental", "Crescent Logistics", "Dorset Title",
                "Eastlake Orthopedics", "Fernwood Realty", "Gable Manufacturing", "Hollis Law",
                "Ironwood Church", "Juniper Salon Group", "Kestrel Engineering", "Larkspur Vet",
                "Mosswood Insurance", "Nimbus Marketing", "Oakhurst Schools", "Pinnacle Physical Therapy"]

INCLUDES = [
    {"id": "S-1", "text": "Helpdesk support for covered users and devices", "covers": ["helpdesk"]},
    {"id": "S-2", "text": "Server and workstation patching on the monthly cycle", "covers": ["patching"]},
    {"id": "S-3", "text": "Managed backup and restore for covered servers", "covers": ["backup"]},
    {"id": "S-4", "text": "Managed network equipment under co-management", "covers": ["network"]},
]
EXCLUDES = [
    {"id": "X-1", "text": "Projects, moves, new-site buildouts and cabling are billed separately", "covers": ["project"]},
]

TICKETS = [
    ("got a weird email asking me to approve a payment, I clicked the link", "sec"),
    ("all our files changed to .locked and there's a note on the server", "sec"),
    ("MFA prompts keep flooding my phone with approve requests I didn't make", "sec"),
    ("sign-in from Russia on the CFO account last night", "sec"),
    ("email is down for the whole office", "outage"),
    ("server unreachable since 8am, nobody can work", "outage"),
    ("forgot my password again, sorry", "routine"),
    ("printer on 3rd floor jamming", "routine"),
    ("new hire starts monday, needs laptop and accounts", "routine"),
    ("install zoom on the conference room pc", "routine"),
    ("restore the accounting share from tuesday's backup", "scope_in"),
    ("we're opening a new office in May, need cabling and wifi for 20 desks", "scope_out"),
    ("can you set up the TVs in the lobby to show dashboards", "scope_ambig"),
    ("hey can someone call me about the thing from yesterday", "human"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickets", type=int, default=500)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Northgate Managed IT", "people": 18, "revenue": "$4.2M",
                          "psa": "modelled, not connected", "rmm": "modelled, not connected"})

    clients = []
    for i in range(60):
        name = f"{rng.choice(CLIENT_NAMES)} #{i:02d}"
        tier = rng.choices(["gold", "silver", "bronze"], weights=[0.25, 0.45, 0.3])[0]
        c = {"id": f"cl_{i:02d}", "name": name, "tier": tier,
             "agreement": {"includes": INCLUDES, "excludes": EXCLUDES}}
        clients.append(c)
    clients[7]["tier"] = None  # the agreement with no tier — SLA unknowable
    store.save("clients", clients)

    tickets = []
    for i in range(args.tickets):
        text, kind = rng.choice(TICKETS)
        opened = now() - timedelta(hours=rng.randint(1, 96))
        t = {"id": f"tk_{i:04d}", "client_id": rng.choice(clients)["id"],
             "text": text, "opened_at": iso(opened)}
        if rng.random() < 0.55:
            t["first_response_at"] = iso(opened + timedelta(hours=rng.uniform(0.2, 10)))
        if rng.random() < 0.45:
            t["resolved_at"] = iso(opened + timedelta(hours=rng.uniform(2, 90)))
        tickets.append(t)

    # demo rows: an untriaged phishing ticket and a pre-triaged security ticket to try to close
    tickets.append({"id": "tk_demo_phish", "client_id": clients[0]["id"], "demo_tag": "demo",
                    "text": "got a weird email asking me to approve a payment, I clicked the link",
                    "opened_at": iso(now() - timedelta(minutes=40))})
    tickets.append({"id": "tk_demo_sec", "client_id": clients[1]["id"], "demo_tag": "demo",
                    "text": "all our files changed to .locked and there's a note",
                    "label": "security", "security_kind": "ransomware",
                    "opened_at": iso(now() - timedelta(hours=2))})
    tickets.append({"id": "tk_demo_scope", "client_id": clients[2]["id"], "demo_tag": "demo",
                    "text": "we're opening a new office in May, need cabling and wifi for 20 desks",
                    "label": "human", "opened_at": iso(now() - timedelta(hours=5))})
    tickets.append({"id": "tk_demo_ambig", "client_id": clients[2]["id"], "demo_tag": "demo",
                    "text": "can you set up the TVs in the lobby to show dashboards",
                    "label": "human", "opened_at": iso(now() - timedelta(hours=6))})

    store.save("tickets", tickets)
    store.save("scope_findings", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"clients": len(clients), "tickets": len(tickets)})
    print(f"Seeded {len(clients)} clients, {len(tickets)} tickets")


if __name__ == "__main__":
    main()
