#!/usr/bin/env python3
"""Receipt OS — synthetic Beacon Title & Escrow. `python3 seed.py [--months 6]`.

~90 closings/mo of control events: callback verifications, dual-control
releases, blocked attempts, drills for 2 of 3 controls (positive_pay left
honestly UNTESTED), and 3 exceptions seeded honestly — wires that moved with a
gap in their chain. Synthetic only; every phone is a 555 number.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(71)

STAFF = ["D. Okafor", "R. Whitfield", "M. Trujillo", "S. Lindqvist", "J. Mercer"]
FIRST = ["Alma", "Bennett", "Corinne", "Dashiell", "Elena", "Franklin", "Greta", "Hugo",
         "Imogen", "Jonas", "Katya", "Lionel", "Mira", "Nolan", "Opal", "Petra"]
LAST = ["Ashford", "Bellamy", "Castellanos", "Drummond", "Eberhart", "Fontaine", "Gallagher",
        "Hollis", "Ingram", "Jarvis", "Kowalczyk", "Lockhart", "Mendonca", "Naismith",
        "Ostrander", "Pemberton"]
BLOCK_VECTORS = [
    "spoofed seller email with new wiring instructions — blocked at intake, callback failed",
    "caller could not answer the recorded-number callback — release held",
    "lookalike domain requested a payoff account change — blocked at intake",
    "urgent same-day change request, no match to the recorded number — held",
]
MESSAGES = [
    "any update on the Bramble Way closing?",
    "our cyber renewal is coming up, the underwriter needs your wire controls documentation",
    "a realtor asked how we protect buyer funds, do we have something to share",
    "thanks for the smooth closing last week!",
]
WIRE_CHANGE_TEXT = "updated wiring instructions attached, please use these for closing"


def two_staff():
    return rng.sample(STAFF, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=6)
    args = ap.parse_args()
    days = args.months * 30

    store.wipe()
    store.save("config", {
        "company": "Beacon Title & Escrow", "offices": 3, "closings_mo": 90,
        "phone": "(555) 013-4400",
        "policy_period": {"start": iso(now() - timedelta(days=days + 2)),
                          "end": iso(now() + timedelta(days=365 - days)),
                          "label": "current cyber/E&O policy period"},
        "production": "modelled, not connected",
    })
    store.save("wires", [])
    store.save("ledger", [])
    store.save("messages", [])
    store.save("approvals", [])
    store.save("events", [])

    n = args.months * 90
    wires, corrected = [], None
    for i in range(n):
        age = rng.randint(0, days - 1)
        released = now() - timedelta(days=age, hours=rng.randint(1, 12))
        wid = f"wr_{i:03d}"
        # the 3 honest exceptions get fixed ids
        if i == 100:
            wid = "wr_exc_single_1"
        elif i == 200:
            wid = "wr_exc_single_2"
        elif i == 300:
            wid = "wr_exc_callback"
        w = {"id": wid, "file_ref": f"BX-{1000 + i}",
             "party": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
             "amount": rng.randint(40, 900) * 1000,
             "released_at": iso(released)}
        wires.append(w)

        had_change = wid == "wr_exc_callback" or rng.random() < 0.15
        if had_change:
            core.ledger_append("wire_change_request", wid,
                               {"verbatim": WIRE_CHANGE_TEXT, "channel": "email"},
                               at=iso(released - timedelta(days=2)))
            if wid != "wr_exc_callback":  # the honest gap: a change that moved unverified
                core.ledger_append("callback_verification", wid,
                                   {"who_called": rng.choice(STAFF),
                                    "number_called_ref": core.CALLBACK_REF},
                                   at=iso(released - timedelta(days=1)))
        if wid not in ("wr_exc_single_1", "wr_exc_single_2"):  # the honest gaps: one human only
            a, b2 = two_staff()
            core.ledger_append("dual_control_release", wid,
                               {"human_a": a, "human_b": b2}, at=iso(released))

    # the planted client-data fixture the scrub test hunts for
    planted = {"id": "wr_planted", "file_ref": "BX-2214", "party": "Marisol Etheridge",
               "amount": 412500, "released_at": iso(now() - timedelta(days=21))}
    wires.append(planted)
    a, b2 = two_staff()
    core.ledger_append("dual_control_release", "wr_planted", {"human_a": a, "human_b": b2},
                       at=planted["released_at"])

    # blocked attempts, a few recent
    for i, back in enumerate((160, 120, 95, 60, 33, 12, 3)):
        core.ledger_append("blocked_attempt", None,
                           {"vector": BLOCK_VECTORS[i % len(BLOCK_VECTORS)]},
                           at=iso(now() - timedelta(days=back)))

    # drills for 2 of 3 controls — positive_pay honestly UNTESTED
    core.ledger_append("drill_result", None,
                       {"control": "callback_verification", "result": "pass",
                        "run_by": "S. Lindqvist"}, at=iso(now() - timedelta(days=150)))
    core.ledger_append("drill_result", None,
                       {"control": "callback_verification", "result": "pass",
                        "run_by": "D. Okafor"}, at=iso(now() - timedelta(days=20)))
    core.ledger_append("drill_result", None,
                       {"control": "dual_control_release", "result": "pass",
                        "run_by": "R. Whitfield"}, at=iso(now() - timedelta(days=60)))

    # one correction, the append-only way: the wrong caller name, fixed by a new entry
    bad = core.ledger_append("callback_verification", "wr_005",
                             {"who_called": "J. Mercer", "number_called_ref": core.CALLBACK_REF},
                             at=iso(now() - timedelta(days=40)))
    core.ledger_correct(bad["id"], "caller recorded wrong — M. Trujillo placed the call",
                        {"who_called": "M. Trujillo"}, at=iso(now() - timedelta(days=40)))

    # demo fixtures (demo_tag → excluded from every counted number)
    demo_rel = now() - timedelta(hours=6)
    wires.append({"id": "wr_demo_chain", "file_ref": "BX-9001", "party": "Petra Naismith",
                  "amount": 285000, "released_at": iso(demo_rel), "demo_tag": "demo"})
    core.ledger_append("wire_change_request", "wr_demo_chain",
                       {"verbatim": WIRE_CHANGE_TEXT, "channel": "email"},
                       at=iso(demo_rel - timedelta(hours=30)), demo_tag="demo")
    core.ledger_append("callback_verification", "wr_demo_chain",
                       {"who_called": "D. Okafor", "number_called_ref": core.CALLBACK_REF},
                       at=iso(demo_rel - timedelta(hours=26)), demo_tag="demo")
    core.ledger_append("dual_control_release", "wr_demo_chain",
                       {"human_a": "D. Okafor", "human_b": "S. Lindqvist"},
                       at=iso(demo_rel), demo_tag="demo")
    store.save("wires", wires)

    messages = [{"id": f"ms_{i:03d}", "from": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                 "text": t, "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 2)]
    messages.append({"id": "ms_demo_wire", "from": "Jonas Hollis", "channel": "email",
                     "text": WIRE_CHANGE_TEXT,
                     "at": iso(now() - timedelta(minutes=15)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_insurer", "from": "the E&O broker",
                     "text": "our cyber renewal is coming up, the underwriter needs your wire "
                             "controls documentation",
                     "at": iso(now() - timedelta(hours=1)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_realtor", "from": "Greta Pemberton",
                     "text": "a realtor asked how we protect buyer funds, do we have something "
                             "to share",
                     "at": iso(now() - timedelta(hours=2)), "demo_tag": "demo"})
    store.save("messages", messages)

    store.log_event("seeded", "all", "human:seed", None,
                    {"wires": len(wires), "ledger": len(store.load("ledger"))})
    print(f"Seeded {len(wires)} wires, {len(store.load('ledger'))} ledger entries, "
          f"{len(messages)} messages — 3 exceptions, positive_pay UNTESTED")


if __name__ == "__main__":
    main()
