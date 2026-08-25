#!/usr/bin/env python3
"""Protocol OS — domain core (cash-pay peptide / longevity clinic).

The generic clinic pitch is "you miss calls." True, and not where the money is.
In a cash-pay program business **revenue is retention**: a patient on a protocol
either continues or quietly stops, and the clinic usually finds out a month later
by noticing the refill never happened.

So this core is built around the **cycle**, not the funnel: who is due, who is
lapsing, who went quiet after a dose change. Around that sit the two things that
make the cycle safe — an inbox that never mistakes a symptom for admin, and a
hard structural rule that a patient who stopped for a medical reason is never
marketed to again.

Nothing here gives clinical advice, adjusts a dose, or interprets a symptom.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "patients", "protocols", "refills", "messages",
          "labs", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="PROTOOS_DATA_ROOT")

URGENT_INSTRUCTION = ("If you are having trouble breathing, chest pain, severe swelling, or you "
                      "feel this is an emergency, call 911 or go to the nearest emergency room "
                      "now — do not wait for a reply here.")

# A patient stops for a reason, and only one of those reasons may ever be
# followed up commercially. This tuple is the whole guardrail.
CONTACTABLE = ("active", "lapsed")
NEVER_CONTACT = ("discontinued_medical", "adverse_event", "deceased", "opted_out", "transferred")


# ---------------------------------------------------------------- the inbox

# Symptoms that must reach a clinician. Over-routing is deliberate: an admin
# question sent to a nurse costs a minute, a reaction filed as a refill request
# costs a patient.
# NOTE on the regexes below: a trailing \b after an alternation of PREFIXES
# (`\b(wheez|reschedul)\b`) can never match, because there is no word boundary
# between "wheez" and "ing". Prefixes therefore carry an explicit \w* instead.
# The suite caught this; it is the kind of bug that silently downgrades an
# emergency to admin, so it is written down rather than just fixed.
URGENT = (
    ("breathing", r"\bcan'?t breathe\b|\bshort(ness)? of breath\b|\bwheez\w*|"
                  r"\bthroat (closing|tight)\b|\bstruggling to breathe\b"),
    ("anaphylaxis", r"\bhives\b|\b(face|lips?|tongue|throat)\b[^.!?]{0,30}\bswell\w*|"
                    r"\bswell\w*[^.!?]{0,30}\b(face|lips?|tongue|throat)\b|"
                    r"\banaphyla\w*"),
    ("cardiac", r"\bchest pain\b|\bheart (is )?(racing|pounding)\b|\bpalpitation\w*"),
    ("severe_gi", r"\bvomit\w*[^.!?]{0,20}\b(all|non ?stop|constantly|since)\b|"
                  r"\bcan'?t keep (anything|water|food) down\b|"
                  r"\bsevere (abdominal|stomach) pain\b"),
    ("injection_site", r"\babscess\w*|\bpus\b|\bred streak\w*|\bhot (and )?swollen\b|"
                       r"\binfect(ed|ion)\b"),
    ("neuro", r"\bfainted\b|\bpassed out\b|\bvision (changes|blurry)\b|\bnumbness\b|"
              r"\bconfusion\b|\bblurry vision\b"),
)
CLINICAL = (
    r"\b(dose|dosage|increase|decrease|skip|double)\b|\btitrat\w*",
    r"\bis (it|this|that) (normal|ok(ay)?|safe)\b",
    r"\b(side ?effects?|reaction|nausea|headache|fatigue)\b|\bbruis\w*",
    r"\bcan i (take|use|combine|stop)\b",
    r"\bpregnan\w*|\bbreastfeed\w*",
)
ADMIN = (
    r"\b(invoice|receipt|payment|card|billing|charge)\b",
    r"\breschedul\w*|\b(appointment|book|cancel|address|shipping|tracking)\b",
    r"\b(refill|reorder|next (shipment|order))\b",
)


def read_message(text):
    t = (text or "").lower()
    for kind, pat in URGENT:
        if re.search(pat, t):
            return {"label": "urgent", "kind": kind,
                    "why": f"an urgent {kind.replace('_',' ')} signal — a person is told now",
                    "route": "clinician, immediately"}
    for pat in CLINICAL:
        if re.search(pat, t):
            return {"label": "clinical", "kind": None,
                    "why": "a clinical question — routed to a clinician unanswered",
                    "route": "clinician queue"}
    for pat in ADMIN:
        if re.search(pat, t):
            return {"label": "admin", "kind": None,
                    "why": "administrative — safe to handle",
                    "route": "front desk"}
    return {"label": "unclear", "kind": None,
            "why": "nothing matched — a human reads it rather than the system guessing",
            "route": "front desk"}


# ---------------------------------------------------------------- the cycle

def contactable():
    """The only patients any outreach can see. This is a query-level exclusion,
    not a filter applied late — the sweep literally cannot reach the others."""
    return [p for p in store.load("patients") if p.get("status") in CONTACTABLE]


def due_and_lapsing(soon_days=7, lapse_days=14):
    """Who is due for a refill, and who has already slipped past it.

    Both come off the patient's own protocol interval and their own last fill —
    never off an assumed cadence.
    """
    idx = {p["id"]: p for p in contactable()}
    protos = {p["patient"]: p for p in store.load("protocols")}
    rows = []
    for pid, p in idx.items():
        pr = protos.get(pid)
        if not pr or not pr.get("interval_days") or not pr.get("last_fill"):
            rows.append({"patient": pid, "name": p.get("name"), "state": "unknown",
                         "_missing": "no protocol interval or no recorded fill — nothing to compute from"})
            continue
        due = (parse(pr["last_fill"]) or now()) + timedelta(days=int(pr["interval_days"]))
        d = (due - now()).days
        state = "overdue" if d < 0 else ("due" if d <= soon_days else "on_track")
        if state == "overdue" and abs(d) >= lapse_days:
            state = "lapsing"
        rows.append({"patient": pid, "name": p.get("name"), "protocol": pr.get("name"),
                     "due_at": iso(due), "days": d, "state": state,
                     "cycles": pr.get("cycles_filled", 0)})
    order = {"lapsing": 0, "overdue": 1, "due": 2, "unknown": 3, "on_track": 4}
    rows.sort(key=lambda r: (order.get(r["state"], 9), r.get("days") if r.get("days") is not None else 0))
    return rows


def continuation_rate(window_days=180, floor=20):
    """Of patients who started a protocol in the window, how many are still on it.
    The one number this business actually runs on."""
    cutoff = now() - timedelta(days=window_days)
    started = [p for p in store.load("protocols")
               if p.get("started_at") and (parse(p["started_at"]) or now()) >= cutoff]
    if len(started) < floor:
        return unmeasured(f"only {len(started)} protocols started in {window_days} days — need {floor}",
                          field="rate", n=len(started))
    idx = store.index("patients")
    still = [p for p in started if (idx.get(p["patient"], {}) or {}).get("status") == "active"]
    return {"rate": round(len(still) / len(started), 3), "started": len(started),
            "continuing": len(still),
            "note": "counted from protocol starts and current status — never asserted"}


def silent_after_change(days=21):
    """Patients whose dose changed and who have not been heard from since.

    This is the retention signal a clinic almost never has: the quiet stop that
    follows a change nobody followed up on. It is a *prompt for a human call*,
    never an automated nudge — which is why it carries no message draft.
    """
    out = []
    idx = {p["id"]: p for p in contactable()}
    for pr in store.load("protocols"):
        p = idx.get(pr.get("patient"))
        if not p or not pr.get("last_change"):
            continue
        since = days_until(pr["last_change"])
        if since is None or -since < days:
            continue
        heard = [m for m in store.load("messages") if m.get("patient") == pr["patient"]
                 and (parse(m.get("at")) or now()) > (parse(pr["last_change"]) or now())]
        if not heard:
            out.append({"patient": pr["patient"], "name": p.get("name"),
                        "protocol": pr.get("name"), "changed": pr["last_change"],
                        "days_quiet": -since,
                        "action": "a person calls — this is not an automated touch"})
    out.sort(key=lambda r: -r["days_quiet"])
    return out


# ---------------------------------------------------------------- labs

def labs_waiting():
    """Baseline or follow-up labs drawn but not reviewed. A result sitting
    unreviewed is the clinic's quietest liability."""
    rows = [l for l in store.load("labs") if l.get("resulted_at") and not l.get("reviewed_at")]
    for r in rows:
        r["days_waiting"] = -(days_until(r["resulted_at"]) or 0)
    rows.sort(key=lambda r: -r["days_waiting"])
    return rows


# ---------------------------------------------------------------- eval

triage_eval = Eval(
    "message triage",
    costly_label="urgent",
    costly_note=("A REACTION FILED AS A REFILL REQUEST is the failure this inbox exists to "
                 "prevent. Over-routing an admin question to a nurse costs a minute; the bias "
                 "is deliberate and permanent."))

EVAL_CASES = [
    {"input": "my face and lips are swelling up", "label": "urgent"},
    {"input": "I can't breathe properly since last night", "label": "urgent"},
    {"input": "chest pain and my heart is racing", "label": "urgent"},
    {"input": "the injection site is hot and swollen with pus", "label": "urgent"},
    {"input": "I fainted this morning", "label": "urgent"},
    {"input": "I've been vomiting nonstop since yesterday", "label": "urgent"},
    {"input": "should I increase my dose this week?", "label": "clinical"},
    {"input": "is it normal to feel tired on this?", "label": "clinical"},
    {"input": "can I combine this with my other medication", "label": "clinical"},
    {"input": "I need a copy of my receipt", "label": "admin"},
    {"input": "can I reschedule my appointment to Friday", "label": "admin"},
    {"input": "when is my next shipment going out", "label": "admin"},
    {"input": "hello", "label": "unclear"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "classification only; the biased stop is the point"},
    "route_urgent":       {"rung": "R2", "reason": "tell a clinician now — waiting for a click defeats the stop"},
    "clinical_advice":    {"rung": "R0", "reason": "answering a clinical question is practising medicine",
                           "never_promote": True},
    "adjust_dose":        {"rung": "R0", "reason": "a dose or titration change is a prescriber's decision, never software's",
                           "never_promote": True},
    "interpret_labs":     {"rung": "R0", "reason": "reading a result to a patient is a clinical act",
                           "never_promote": True},
    "contact_excluded":   {"rung": "R0", "reason": "a patient who stopped for a medical reason is never marketed to again",
                           "never_promote": True},
    "draft_refill_nudge": {"rung": "R1", "reason": "outward message to a patient — a human sends"},
    "book_appointment":   {"rung": "R1", "reason": "a booking is a promise of clinician time"},
    "send_receipt":       {"rung": "R2", "reason": "administrative, reversible, and the patient asked for it"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Protocol OS — what it computes to")
        .line("Lapsing patients continued", "revenue",
              "lapsing × your recovery rate × cycle value",
              ["lapsing_count", "recovery_rate", "cycle_value"],
              lambda g: float(g["lapsing_count"]) * float(g["recovery_rate"]) * float(g["cycle_value"]),
              note="the lapsing count is counted; recovery rate and cycle value are yours")
        .line("Quiet-after-change calls that land", "revenue",
              "silent × your recovery rate × cycle value",
              ["silent_count", "recovery_rate", "cycle_value"],
              lambda g: float(g["silent_count"]) * float(g["recovery_rate"]) * float(g["cycle_value"]),
              note="a prompt for a human call — the revenue is the clinician's, not the software's")
        .line("Inbox and refill-chasing time", "time_saved", "hrs/wk × 52 × rate",
              ["inbox_hours_wk", "staff_rate"],
              lambda g: float(g["inbox_hours_wk"]) * 52 * float(g["staff_rate"]),
              note="reported separately; never summed into revenue")
        .line("Urgent messages reaching a clinician fast", "scenario",
              "you decide what this is worth",
              ["urgent_value"], lambda g: float(g["urgent_value"]),
              assumption=("patient-safety routing is never monetized by us — this line is yours "
                          "or it stays blank")))


def roi(given):
    rec = {}
    rows = due_and_lapsing()
    lapsing = [r for r in rows if r.get("state") in ("lapsing", "overdue")]
    if rows:
        rec["lapsing_count"] = len(lapsing)
    sil = silent_after_change()
    if sil:
        rec["silent_count"] = len(sil)
    vals = [r.get("value") for r in store.load("refills") if r.get("value")]
    if len(vals) >= 25:
        rec["cycle_value"] = round(median(vals), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "route_urgent", "draft_refill_nudge", "book_appointment", "send_receipt")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("patient:",))
