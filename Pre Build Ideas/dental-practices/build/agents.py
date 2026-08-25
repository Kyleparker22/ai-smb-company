#!/usr/bin/env python3
"""Chair OS — the agents: reactivation, same-day fill, benefits pack, recall.

No agent in this file forms a clinical opinion or tells a patient what is
covered. The first is impossible by construction (there is no code path that
produces a recommendation); the second is blocked by `core.can_state_coverage`
and gated at R1 on top.

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


# ---------------------------------------------------------------- 1 · reactivation

def reactivation(limit=25, ref=None):
    ref = ref or now()
    ranked = core.rank_unscheduled(ref=ref, limit=limit)
    pts = store.index("patients")
    drafted = []
    for r in ranked:
        pt = pts.get(r["patient_id"], {})
        body = _reactivation_copy(r, pt, ref)
        res = gate.act("draft_reactivation", "reactivation", r["id"],
                       {"summary": f"{r['patient']} · {r['label']} · ${r['fee']:,}",
                        "preview": body[:120], "score": r["score"], "why": r["why"],
                        "fee": r["fee"]})
        drafted.append({"plan": r["id"], "approval": res.get("approval"), "body": body,
                        "why": r["why"]})
    return {"drafted": len(drafted), "detail": drafted[:10]}


def _reactivation_copy(r, pt, ref):
    """The doctor's own language about the procedure the doctor diagnosed.
    Nothing here characterises the clinical situation beyond what is recorded."""
    name = (r.get("patient") or "there").split()[0]
    who = r.get("diagnosed_by") or "the doctor"
    tooth = f" on {r['tooth']}" if r.get("tooth") else ""
    days = core.benefit_days_left(pt, ref)
    hook = ""
    if days is not None and days <= 75:
        hook = (f" One practical note: your benefits reset in {days} days, and anything unused "
                f"doesn't carry over.")
    return (f"Hi {name} — {who} noted the {r['label'].lower()}{tooth} at your last visit and it's "
            f"still open on your chart. We have time set aside this month if you'd like to get it "
            f"handled.{hook}")


# ---------------------------------------------------------------- 2 · same-day fill

def same_day_fill(appointment_id, ref=None):
    """A cancellation, worked in waves. The chair goes cold in twenty minutes,
    so this is the module with the shortest clock in the build."""
    ref = ref or now()
    appt = store.by_id("appointments", appointment_id)
    if not appt:
        return {"error": "no such appointment"}
    appt["state"] = "open"
    appt["opened_at"] = iso(ref)
    store.upsert("appointments", appt)
    freed = {"provider_type": appt.get("provider_type", "dds"),
             "minutes": appt.get("minutes", 60), "starts_at": appt["starts_at"]}
    res = core.fill_candidates(freed, ref)
    waves = [res["candidates"][:3], res["candidates"][3:7]]
    for c in waves[0]:
        gate.act("offer_fill_slot", "fill", c["id"],
                 {"summary": f"{c['patient']} · {c['label']} · offered {appt['starts_at'][11:16]}",
                  "fee": c["fee"], "fit": c["fit_why"], "rank": c["rank_why"]})
    return {"opening": {"at": appt["starts_at"], **freed},
            "wave_one": waves[0], "wave_two": waves[1],
            "rejected_sample": res["rejected_sample"], "note": res["note"]}


def accept_fill(appointment_id, plan_id, ref=None):
    ref = ref or now()
    appt, plan = store.by_id("appointments", appointment_id), store.by_id("treatment_plan", plan_id)
    if not appt or not plan:
        return {"error": "unknown appointment or plan"}
    ok, why = core.fits({"provider_type": appt.get("provider_type", "dds"),
                         "minutes": appt.get("minutes", 60)}, plan["procedure"])
    if not ok:
        return {"booked": False, "refused": why}

    def _book():
        appt.update(state="scheduled", procedure=plan["procedure"], patient_id=plan["patient_id"],
                    filled_from_plan=plan_id, filled_at=iso(ref))
        store.upsert("appointments", appt)
        plan["state"] = "scheduled"
        store.upsert("treatment_plan", plan)
        return appt["id"]

    fee = core.PROCEDURES[plan["procedure"]]["fee"]
    res = gate.act("book_from_fill", "fill", appointment_id,
                   {"summary": f"filled {appt['starts_at'][11:16]} with {plan['procedure']}",
                    "fee": fee, "fit": why}, execute=_book)
    minutes = None
    if appt.get("opened_at"):
        a, b = parse(appt["opened_at"]), ref
        minutes = round((b - a).total_seconds() / 60, 1)
    return {"booked": bool(res.get("executed")), "time_to_fill_minutes": minutes, "gate": res}


# ---------------------------------------------------------------- 3 · benefits pack

def benefits_pack(ref=None):
    """Tomorrow's verifications, assembled before the office opens. What it
    could not confirm is an exception list for humans — never an assumption."""
    ref = ref or now()
    day = (ref + timedelta(days=1)).date()
    appts = [a for a in store.load("appointments")
             if a.get("state") == "scheduled" and (parse(a["starts_at"]) or ref).date() == day]
    pts = store.index("patients")
    sheets, exceptions = [], []
    for a in appts:
        pt = pts.get(a.get("patient_id"))
        if not pt:
            continue
        v = core.verify(pt, pt.get("payer"), a["procedure"], ref)
        gate.act("run_verification", "benefits", a["id"],
                 {"summary": f"{pt['name']} · {a['procedure']} · {v['verdict']}"})
        store.upsert("verifications", {"id": store.nid("ver"), **v, "appointment": a["id"]})
        row = {"appointment": a["id"], "patient": pt["name"], "procedure": a["procedure"],
               "payer": core.PAYERS.get(pt.get("payer"), {}).get("label", pt.get("payer")),
               "verdict": v["verdict"], "fields": v["fields"],
               "can_state_coverage": core.can_state_coverage(v)}
        sheets.append(row)
        if v["verdict"] != "confirmed":
            exceptions.append({"patient": pt["name"], "procedure": a["procedure"],
                               "unconfirmed": v.get("unconfirmed_fields", []),
                               "why": next((f["_missing"] for f in v["fields"].values()
                                            if f.get("_missing")), "unconfirmed")})
    return {"date": str(day), "sheets": sheets, "exceptions": exceptions,
            "note": "an unconfirmed field is reported unconfirmed. Nothing here infers a benefit "
                    "from a plan template, and no sheet tells a patient what will be paid."}


# ---------------------------------------------------------------- 4 · recall

def recall_watchtower(ref=None):
    ref = ref or now()
    due, unknown = [], []
    for p in store.load("patients"):
        r = core.recall_due(p, ref)
        if r.get("_missing"):
            unknown.append({"patient": p["name"], "why": r["_missing"]})
            continue
        if r["state"] in ("due", "overdue"):
            due.append({"patient": p["name"], "patient_id": p["id"], **r})
    due.sort(key=lambda r: (0 if r["hook"] == "benefits" else 1, -r["days_since"]))
    if due:
        gate.act("recall_touch", "recall", f"recall_{iso(ref)[:10]}",
                 {"summary": f"{len(due)} due or overdue; "
                             f"{sum(1 for d in due if d['hook']=='benefits')} led by benefit expiry"})
    return {"due": due[:40], "n": len(due), "not_flagged": unknown[:12],
            "note": "a patient with no hygiene history is never called overdue — we do not know "
                    "that they are"}


def run_all():
    return {"reactivation": reactivation(), "benefits": {"n": len(benefits_pack()["sheets"])},
            "recall": {"n": recall_watchtower()["n"]}}
