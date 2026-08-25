#!/usr/bin/env python3
"""Encounter OS — synthetic seed. Deterministic."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import REQUIRED_DOC, store
from _kit.store import iso, now

R = random.Random(8898)

STATES = ["FL", "GA", "TX", "NY", "CA", "NC", "SC", "TN", "AZ", "CO", "OH", "PA", "WA", "IL"]
COVERED = ["FL", "GA", "TX", "NC", "SC", "TN", "AZ", "OH"]          # the roster's licences
FIRST = ["Aisha", "Brandt", "Camille", "Devon", "Esme", "Franco", "Greta", "Hollis", "Imani",
         "Jarek", "Kai", "Lucia", "Milo", "Nadia", "Owen", "Petra", "Quinn", "Rosa", "Sven", "Tara"]
LAST = ["Ames", "Bellweather", "Cho", "Delacroix", "Eastwood", "Farrow", "Grimaldi", "Haddad",
        "Ivers", "Jansen", "Kovac", "Lund", "Moreau", "Nayar", "Ortiz", "Pike"]
COMPLAINTS = ["weight management follow-up", "refill request", "new consult — fatigue",
              "sleep issues", "hormone follow-up", "skin concern", "anxiety follow-up"]
URGENT_TEXT = ["I've had chest pain since this morning", "I can't breathe properly",
               "I've been thinking about hurting myself", "my speech went slurred an hour ago",
               "I'm pregnant and having severe pain"]
ROUTINE_TEXT = ["Looking to continue my program, no problems so far.",
                "I need a refill and a quick check-in.",
                "Been tired for a few weeks, want to talk it through.",
                "Following up on my last visit, everything is stable."]


def build(n_patients=180):
    store.wipe()
    store.save("config", {
        "company": "Northline Telehealth",
        "kind": "Multi-state async + sync telehealth clinic",
        "staff": "11 (4 MDs, 3 NPs, 4 coordinators)",
        "revenue": "~$4.1M/yr",
        "note": "SYNTHETIC DEMONSTRATION DATA — no real clinic, clinician, patient or encounter.",
    })

    clinicians = []
    for i, (name, lic) in enumerate([
            ("Dr. R. Okonkwo", ["FL", "GA", "SC"]),
            ("Dr. M. Halvorsen", ["TX", "AZ"]),
            ("Dr. P. Nagarajan", ["FL", "NC", "TN"]),
            ("NP J. Castellanos", ["GA", "SC", "OH"]),
            ("NP L. Brenner", ["TX", "AZ", "TN"]),
            ("Dr. S. Whitfield", ["NY"]),          # inactive — the trap
            ("NP D. Amos", ["FL", "NC"])]):
        clinicians.append({"id": f"cl{i+1}", "name": name, "licences": lic,
                           "modalities": ["general"] + (["weight"] if i % 2 == 0 else []),
                           "active": name != "Dr. S. Whitfield"})
    store.save("clinicians", clinicians)

    patients, intakes, encounters = [], [], []
    for i in range(n_patients):
        pid = f"pt{i+1:04d}"
        # Most patients are in covered states; a real minority are not — that is the finding.
        state = R.choice(COVERED) if R.random() < 0.82 else R.choice([s for s in STATES if s not in COVERED])
        patients.append({"id": pid, "name": f"{R.choice(FIRST)} {R.choice(LAST)}",
                         "state": state,
                         "joined": iso(now() - timedelta(days=R.randint(5, 600)))})

        if R.random() < 0.42:
            urgent = R.random() < 0.06
            answers = {"chief_complaint": R.choice(COMPLAINTS),
                       "duration": R.choice(["3 days", "2 weeks", "a month", "6 months"]),
                       "medications": R.choice(["none", "lisinopril", "metformin", "levothyroxine"]),
                       "allergies": R.choice(["none", "penicillin", "sulfa"]),
                       "conditions": R.choice(["none", "hypertension", "PCOS", "hypothyroid"]),
                       "pregnancy_status": R.choice(["n/a", "not pregnant", "unknown"])}
            if R.random() < 0.25:
                del answers[R.choice(list(answers))]
            intakes.append({"id": f"in{i+1:04d}", "patient": pid,
                            "at": iso(now() - timedelta(days=R.randint(0, 40))),
                            "narrative": R.choice(URGENT_TEXT if urgent else ROUTINE_TEXT),
                            "answers": answers, "triaged_at": None, "label": None})

        if R.random() < 0.75:
            paid = now() - timedelta(days=R.randint(0, 180))
            started = None
            if R.random() < 0.72:
                started = iso(paid + timedelta(days=R.randint(0, 5)))
            doc = {k: True for k in REQUIRED_DOC}
            if started and R.random() < 0.3:
                for _ in range(R.randint(1, 2)):
                    doc.pop(R.choice(list(doc)), None)
            enc = {"id": f"e{4000+i}", "patient": pid,
                   "clinician": R.choice([c["id"] for c in clinicians if c["active"]]),
                   "paid_at": iso(paid), "amount": R.choice([79, 99, 129, 149, 189]),
                   "started_at": started,
                   "documentation": doc if started else {},
                   "closed_at": None, "closed_by": None}
            if started and not [k for k in REQUIRED_DOC if not doc.get(k)] and R.random() < 0.8:
                enc["closed_at"] = iso((now() - timedelta(days=R.randint(0, 100))))
                enc["closed_by"] = "clinician"
            encounters.append(enc)

    store.save("patients", patients)
    store.save("intakes", intakes)
    store.save("encounters", encounters)
    store.save("approvals", [])
    store.save("events", [])

    for e in encounters[:70]:
        store.log_event("route_patient", e["patient"], "agent:router", "R2", {})
        if e.get("closed_at"):
            store.log_event("close_encounter", e["id"], "human:clinician", "R1", {})

    uncovered = sorted({p["state"] for p in patients if p["state"] not in COVERED})
    print(f"seeded {len(patients)} patients · {len(clinicians)} clinicians "
          f"({sum(1 for c in clinicians if not c['active'])} inactive) · {len(intakes)} intakes "
          f"· {len(encounters)} encounters")
    print(f"  uncovered states with patients: {', '.join(uncovered)}")
    return {"patients": len(patients)}


if __name__ == "__main__":
    build()
