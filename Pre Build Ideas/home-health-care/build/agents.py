#!/usr/bin/env python3
"""Shift OS — the agents: fill engine, message triage, retention, EVV, referrals.

Three things this file structurally cannot do: answer a clinical question,
assign a caregiver to an unapproved pairing, or message a caregiver about
retention.

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import days_until, iso, now, parse


# ---------------------------------------------------------------- 1 · the fill engine

def fill(shift_id, ref=None):
    ref = ref or now()
    shift = store.by_id("shifts", shift_id)
    if not shift:
        return {"error": "no such shift"}
    client = store.by_id("clients", shift.get("client_id")) or {}
    res = core.fill_candidates(shift, client, ref=ref)
    waves = [res["ranked"][:3], res["ranked"][3:6]]

    for c in waves[0]:
        if c["approved_pairing"]:
            gate.act("offer_shift_approved_pairing", "fill", shift_id,
                     {"summary": f"{c['name']} offered {shift['starts_at'][11:16]} "
                                 f"({client.get('name')})",
                      "overtime_cost": c["overtime_cost"], "reasons": c["reasons"]})
        else:
            gate.act("assign_new_pairing", "fill", shift_id,
                     {"summary": f"NEW PAIRING: {c['name']} has never worked "
                                 f"{client.get('name')} — needs approval",
                      "reasons": c["reasons"]})
        if c["overtime_hours"]:
            gate.act("flag_overtime", "fill", shift_id,
                     {"summary": f"{c['name']} would go {c['overtime_hours']}h into overtime "
                                 f"(~${c['overtime_cost']})"})
    return {"shift": shift, "client": {"name": client.get("name"), "zone": client.get("zone"),
                                       "care_plan": client.get("care_plan")},
            "wave_one": waves[0], "wave_two": waves[1], "blocked": res["blocked"][:12],
            "note": res["note"]}


def accept_fill(shift_id, caregiver_id, ref=None):
    """A caregiver said yes. An APPROVED pairing fills; a new one cannot."""
    ref = ref or now()
    shift = store.by_id("shifts", shift_id)
    if not shift:
        return {"error": "no such shift"}
    if not core.pairing_approved(caregiver_id, shift["client_id"]):
        return {"filled": False,
                "refused": "this caregiver has never been approved for this client. A new pairing "
                           "goes to a human — a stranger arriving unannounced is how a family "
                           "starts shopping",
                "gate": gate.act("assign_new_pairing", "fill", shift_id,
                                 {"summary": f"{caregiver_id} → {shift['client_id']} needs approval"})}

    def _fill():
        shift.update(state="scheduled", caregiver_id=caregiver_id, filled_at=iso(ref))
        store.upsert("shifts", shift)
        return shift["id"]

    res = gate.act("offer_shift_approved_pairing", "fill", shift_id,
                   {"summary": f"filled {shift['starts_at'][11:16]} with {caregiver_id}"},
                   execute=_fill)
    mins = None
    if shift.get("opened_at"):
        a = parse(shift["opened_at"])
        mins = round((ref - a).total_seconds() / 60, 1) if a else None
    if res.get("executed"):
        store.log_event("shift_filled", shift_id, "agent:fill", "R2", {"minutes": mins})
    return {"filled": bool(res.get("executed")), "time_to_fill_minutes": mins, "gate": res}


def callout(shift_id, ref=None):
    """The 6am call. Opens the shift and builds the ranked list in one move."""
    ref = ref or now()
    shift = store.by_id("shifts", shift_id)
    if not shift:
        return {"error": "no such shift"}
    shift.update(state="open", opened_at=iso(ref), previous_caregiver=shift.get("caregiver_id"),
                 caregiver_id=None)
    store.upsert("shifts", shift)
    return fill(shift_id, ref)


# ---------------------------------------------------------------- 2 · message triage

def handle_message(message_id, ref=None):
    ref = ref or now()
    m = store.by_id("messages", message_id)
    if not m:
        return {"error": "no such message"}
    r = core.read_message(m.get("text", ""))
    gate.act("read_message", "triage", message_id, {"summary": m.get("text", "")[:70], "read": r})
    m.update(handled_at=iso(ref), tier=r["tier"], kind=r.get("kind"))
    store.upsert("messages", m)
    out = {"message": message_id, "read": r, "steps": []}

    if r["tier"] == "crisis":
        gate.act("route_crisis", "triage", message_id,
                 {"summary": f"CRISIS ({r['kind']}) — human now", "why": r["why"]})
        step = {"action": "route_crisis", "kind": r["kind"], "why": r["why"],
                "said": core.EMERGENCY_INSTRUCTION,
                "refused": "the system did not assess, did not reassure and did not advise. All "
                           "three would be practising nursing"}
        if r.get("mandatory_report"):
            gate.act("mandatory_report", "triage", message_id,
                     {"summary": "possible abuse or neglect — flagged for a human"})
            step["mandatory_report"] = core.MANDATORY_REPORT_NOTE
        out["steps"].append(step)
        return out

    if r["tier"] == "clinical":
        gate.act("route_clinical", "triage", message_id,
                 {"summary": "clinical question — routed unanswered", "why": r["why"]})
        out["steps"].append({
            "action": "route_clinical", "why": r["why"],
            "said": "That one needs one of our nurses rather than me — I've sent it straight to "
                    "them and they'll call you back today. If anything changes suddenly, call 911.",
            "refused": "no medication guidance, no dosing, no symptom interpretation, no care-plan "
                       "change, no opinion on how they are doing"})
        return out

    out["steps"].append({"action": "answer_logistics",
                         "said": "Happy to help with that — let me check the schedule and confirm."})
    return out


def sweep_messages(limit=200, ref=None):
    n = 0
    for m in sorted(store.load("messages"), key=lambda x: x["at"]):
        if m.get("handled_at") or m.get("demo_tag"):
            continue
        handle_message(m["id"], ref)
        n += 1
        if n >= limit:
            break
    return {"handled": n}


# ---------------------------------------------------------------- 3 · retention

def retention(ref=None):
    ref = ref or now()
    shifts = store.load("shifts")
    every = [r for r in (core.retention_risk(cg, shifts, ref) for cg in store.load("caregivers")) if r]
    rows = [r for r in every if r["at_risk"]]
    rows.sort(key=lambda r: -r["count"])
    single = len(every) - len(rows)
    if rows:
        gate.act("retention_list", "retention", f"retention_{iso(ref)[:10]}",
                 {"summary": f"{len(rows)} caregivers showing at least one signal"})
    return {"rows": rows[:40], "n": len(rows), "single_signal": single,
            "signals": core.RETENTION_SIGNALS,
            "floor": core.RISK_SIGNAL_FLOOR,
            "note": "a list for a human conversation. The system never messages a caregiver about "
                    "this — an automated 'we noticed you seem unhappy' is worse than silence"}


# ---------------------------------------------------------------- 4 · EVV

def evv(ref=None):
    ref = ref or now()
    board = core.evv_board(ref)
    for r in board["rows"][:60]:
        gate.act("evv_flag", "compliance", r["shift"],
                 {"summary": f"{len(r['exceptions'])} exception(s) on {r['shift']}",
                  "types": [e["type"] for e in r["exceptions"]]})
    return board


# ---------------------------------------------------------------- 5 · referrals

def referral(text, source, ref=None):
    ref = ref or now()
    r = core.read_message(text)
    if r["tier"] != "routine":
        return handle_message(store.upsert("messages", {
            "id": store.nid("m"), "at": iso(ref), "text": text, "from": source})["id"], ref)
    res = gate.act("referral_response", "intake", f"ref_{iso(ref)}",
                   {"summary": f"referral from {source}", "preview": text[:90]})
    return {"acknowledged": True, "gate": res,
            "captured": {"source": source, "need": text[:200], "at": iso(ref)},
            "note": "response latency to a referral source is recorded — that is what wins census. "
                    "Nothing clinical was assessed here"}


def run_all():
    return {"messages": sweep_messages(), "retention": {"n": retention()["n"]},
            "evv": {"exceptions": evv()["count"]}}
