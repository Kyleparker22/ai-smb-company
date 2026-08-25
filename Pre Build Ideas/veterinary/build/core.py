#!/usr/bin/env python3
"""Visit OS — domain core (small-animal veterinary practice).

Rules live here: the message triage with its typed emergency signals, the
reactivation rules with the deceased-patient exclusion built into the query
itself, waitlist ranking, and the autonomy matrix.

The thesis: the practice's growth is already on its own patient list (lapsed
preventives), its dark exam rooms already have a waitlist, and its inbox mixes
bookings with emergencies that cannot wait in a queue. Sort all three without
ever practising medicine.

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

TABLES = ("config", "clients", "patients", "appointments", "waitlist",
          "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="VISITOS_DATA_ROOT")

EMERGENCY_INSTRUCTION = ("If this is an emergency, go to the nearest emergency animal hospital "
                         "now — do not wait for a reply here.")

# ---------------------------------------------------------------- triage

# Typed emergencies. Over-routing is the deliberate bias: a nail-trim question
# escalated costs a shrug; a blocked cat in the queue overnight is dead.
EMERGENCIES = (
    ("toxin", r"\b(ate|got into|swallowed|chew(ed|ing))\b.*\b(chocolate|xylitol|gum|grapes?|raisins?|"
              r"antifreeze|ibuprofen|advil|tylenol|rat poison|lil(y|ies)|onion|medib?one)\b"),
    ("toxin", r"\b(poison(ed)?|toxic)\b"),
    ("gdv", r"\b(belly|abdomen|stomach)\b.*\b(swollen|distended|hard|bloated)\b|\bretching\b|"
            r"\btrying to (vomit|throw up)\b.*\b(nothing|can'?t)\b"),
    ("blocked", r"\b(straining|can'?t|cannot|not able)\b.*\b(pee|urinat)|"
                r"\bno urine\b|\blitter box\b.*\b(nothing|crying)\b"),
    ("breathing", r"\b(can'?t breathe|labou?red breathing|gasping|choking|blue (tongue|gums))\b"),
    ("collapse", r"\b(collapsed?|unresponsive|won'?t wake( up)?|(went|gone) limp)\b"),
    ("seizure", r"\bseizur|convuls|shaking uncontrollab"),
    ("trauma", r"\b(hit by|struck by)\b.*\b(car|truck)\b|\battacked\b|\bbleeding (a lot|heavily|everywhere)\b"),
    ("pale_gums", r"\b(pale|white) gums\b|\bgums (are|look|went) (pale|white|grey|gray)\b"),
)
CLINICAL = (
    r"\b(dose|dosage|dosing|how much)\b.*\b(mg|ml|benadryl|medication|med|pill)\b",
    r"\bis (it|this|that) (normal|ok(ay)?|safe)\b",
    r"\b(vomit(ing|ed)?|diarrhea|limping|not eating|lethargic|itch(y|ing)|lump|bump|rash)\b",
    r"\b(medication|prescription|refill)\b.*\b(change|increase|stop|double)\b",
    r"\bshould (i|we) (be worried|worry|bring)\b",
)
QOL = (
    r"\b(euthan|put (him|her|them) (down|to sleep)|say goodbye|end of life|quality of life)\b",
    r"\b(time to let|letting) (him|her|them) go\b",
)
ROUTINE = (
    r"\b(book|schedule|appointment|nail trim|groom|boarding|records?|invoice|bill)\b",
    r"\b(vaccine|shots?)\b.*\b(due|schedule|book)\b",
    r"\bfood order\b|\bpick ?up\b",
)


def read_message(text):
    """emergency | clinical | qol | routine | human. Empty routes to a human.
    Emergency and QoL never receive an automated answer of any kind."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for kind, rx in EMERGENCIES:
        if re.search(rx, t):
            return {"label": "emergency", "kind": kind,
                    "why": f"typed emergency signal: {kind}",
                    "instruction": EMERGENCY_INSTRUCTION}
    for rx in QOL:
        if re.search(rx, t):
            return {"label": "qol",
                    "why": "quality-of-life conversation — a human, gently, always"}
    for rx in CLINICAL:
        if re.search(rx, t):
            return {"label": "clinical",
                    "why": "clinical question — routed to a DVM unanswered; answering would be practising medicine"}
    for rx in ROUTINE:
        if re.search(rx, t):
            return {"label": "routine", "why": "scheduling / admin language"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- reactivation

REMINDER_COOLDOWN_DAYS = 30
MAX_REMINDERS = 3


def contactable_patients():
    """THE structural exclusion: only active patients are ever visible to the
    reactivation path. Deceased and transferred rows cannot reach a draft."""
    return [p for p in store.load("patients") if p.get("status") == "active"]


def lapsed(ref=None):
    """Active patients past due on anything, with the due item named."""
    ref = ref or now()
    rows = []
    for p in contactable_patients():
        due_items = []
        for k, label in (("annual_due", "annual exam"), ("vaccines_due", "vaccines"),
                         ("preventive_due", "parasite preventive")):
            d = parse(p.get(k))
            if d and d < ref:
                due_items.append({"item": label, "overdue_days": (ref - d).days})
        if due_items:
            rows.append({"patient": p["id"], "name": p["name"], "species": p["species"],
                         "client_id": p["client_id"], "due": due_items,
                         "max_overdue": max(d["overdue_days"] for d in due_items),
                         "reminders": len(p.get("reminders") or [])})
    return sorted(rows, key=lambda r: -r["max_overdue"])


def reminder_plan(patient, ref=None):
    """What happens to one lapsed patient now. The ladder is bounded and the
    status check runs AGAIN here — defence in depth on the unforgivable case."""
    ref = ref or now()
    if patient.get("status") != "active":
        return {"action": "refuse",
                "why": f"patient status is {patient.get('status')!r} — a reminder for a deceased or "
                       f"transferred patient is the failure this vertical never forgives"}
    reminders = patient.get("reminders") or []
    if len(reminders) >= MAX_REMINDERS:
        return {"action": "none", "why": f"ladder exhausted at {MAX_REMINDERS} — silence is an answer"}
    if reminders:
        last = parse(reminders[-1]["at"])
        if last and (ref - last).days < REMINDER_COOLDOWN_DAYS:
            return {"action": "none", "why": f"inside the {REMINDER_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_reminder", "why": f"touch {len(reminders)+1} of {MAX_REMINDERS}"}


# ---------------------------------------------------------------- slot backfill

def rank_waitlist(slot):
    """Ranked candidates for a cancelled slot, reasons on the row, blockers
    named. Nothing books itself — booking drafts are R1."""
    ranked, blocked = [], []
    for w in store.load("waitlist"):
        if w.get("booked_at"):
            continue
        p = store.by_id("patients", w["patient_id"]) or {}
        if p.get("status") != "active":
            blocked.append({"who": w.get("name", w["patient_id"]),
                            "why": f"patient status {p.get('status')!r} — never offered"})
            continue
        if w.get("minutes_needed", 30) > slot.get("minutes", 30):
            blocked.append({"who": w.get("name"), "why":
                            f"needs {w.get('minutes_needed')}m, slot is {slot.get('minutes')}m"})
            continue
        score, reasons = 50, []
        if w.get("doctor_pref") in (None, slot.get("doctor")):
            score += 20
            reasons.append("doctor matches (or no preference)")
        else:
            score -= 15
            reasons.append(f"prefers {w.get('doctor_pref')}")
        wait_days = -(days_until(w.get("since")) or 0)
        score += min(20, wait_days)
        reasons.append(f"waiting {wait_days} days")
        if w.get("reason_urgencyish"):
            score += 15
            reasons.append("recheck the DVM wanted sooner")
        ranked.append({"waitlist_id": w["id"], "who": w.get("name"), "species": w.get("species"),
                       "score": score, "reasons": reasons})
    ranked.sort(key=lambda r: -r["score"])
    return {"candidates": ranked[:8], "blocked": blocked[:8]}


def backfill_stats(window_days=90):
    cutoff = now() - timedelta(days=window_days)
    cancels = [a for a in store.load("appointments")
               if a.get("cancelled_at") and (parse(a["cancelled_at"]) or now()) >= cutoff]
    if len(cancels) < 10:
        return unmeasured(f"only {len(cancels)} cancellations in {window_days} days — need 10",
                          field="backfill_rate", n=len(cancels))
    filled = [a for a in cancels if a.get("backfilled_at")]
    return {"backfill_rate": round(len(filled) / len(cancels), 3),
            "cancellations": len(cancels), "backfilled": len(filled),
            "note": "counted from the appointment log"}


def recovered_this_week(ref=None):
    """Counted, never asserted: reminders a human actually sent, slots
    backfilled, and lapsed patients who came back in, all inside 7 days."""
    ref = ref or now()
    sent = sum(1 for e in store.events(kind="reminder_sent")
               if (ref - (parse(e.get("at")) or ref)).days <= 7)
    filled = [a for a in store.load("appointments")
              if a.get("backfilled_at") and (ref - (parse(a["backfilled_at"]) or ref)).days <= 7]
    returned = [p for p in store.load("patients")
                if p.get("reactivated_at") and (ref - (parse(p["reactivated_at"]) or ref)).days <= 7]
    return {"reminders_sent": sent, "slots_backfilled": len(filled),
            "patients_returned": len(returned),
            "note": "counted from the log and the book — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="emergency",
                   costly_note=("A MISSED EMERGENCY IS A DEAD PATIENT. Over-routing a nail trim "
                                "to a human costs a shrug; the bias is deliberate."))

EVAL_CASES = [
    {"input": "my dog just ate a bar of baker's chocolate", "label": "emergency"},
    {"input": "he keeps retching but nothing comes up and his belly looks swollen", "label": "emergency"},
    {"input": "my cat has been straining in the litter box and nothing, he's crying", "label": "emergency"},
    {"input": "she got hit by a car, leg looks wrong", "label": "emergency"},
    {"input": "he collapsed on the walk and won't wake up properly", "label": "emergency"},
    {"input": "she's gasping and her tongue looks blue", "label": "emergency"},
    {"input": "found him chewing an ibuprofen bottle", "label": "emergency"},
    {"input": "what dose of benadryl can I give a 40lb dog", "label": "clinical"},
    {"input": "she's been vomiting since yesterday, should I be worried", "label": "clinical"},
    {"input": "is it normal for him to limp after his shots", "label": "clinical"},
    {"input": "I think it might be time to put her to sleep, I don't know", "label": "qol"},
    {"input": "can I book a nail trim for saturday", "label": "routine"},
    {"input": "need to schedule his annual and vaccines that are due", "label": "routine"},
    {"input": "", "label": "human"},
    {"input": "hi, quick question when you get a chance", "label": "human"},
    {"input": "she got into the easter lilies on the counter", "label": "emergency"},
    {"input": "his gums look white and he won't get up", "label": "emergency"},
    {"input": "he's shaking uncontrollably and drooling", "label": "emergency"},
    {"input": "found a lump on her shoulder, is that normal", "label": "clinical"},
    {"input": "we're wondering about her quality of life lately", "label": "qol"},
    {"input": "can I get a refill on his food order", "label": "routine"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":     {"rung": "R3", "reason": "routing only; the biased stop is the point"},
    "route_emergency":  {"rung": "R2", "reason": "act now, tell the human — waiting for a click defeats the stop"},
    "clinical_answer":  {"rung": "R0", "reason": "answering a clinical question is practising veterinary medicine", "never_promote": True},
    "qol_conversation": {"rung": "R0", "reason": "euthanasia and quality-of-life talk is a human conversation, always", "never_promote": True},
    "contact_deceased": {"rung": "R0", "reason": "a reminder for a deceased patient is the unforgivable failure", "never_promote": True},
    "draft_reminder":   {"rung": "R1", "reason": "outward message — a human sends"},
    "draft_backfill_offer": {"rung": "R1", "reason": "outward booking offer — a human sends"},
    "book_appointment": {"rung": "R1", "reason": "a booking is a promise of a doctor's time"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Visit OS — what it computes to")
        .line("Lapsed patients reactivated", "revenue", "lapsed × your show rate × avg visit",
              ["lapsed_count", "show_rate", "avg_visit"],
              lambda g: float(g["lapsed_count"]) * float(g["show_rate"]) * float(g["avg_visit"]),
              note="lapsed count is counted; show rate and visit value are yours")
        .line("Cancelled slots backfilled", "revenue", "cancellations × backfill lift × avg visit",
              ["cancellations_90d", "backfill_lift", "avg_visit"],
              lambda g: float(g["cancellations_90d"]) * float(g["backfill_lift"]) * float(g["avg_visit"]))
        .line("Reminder and phone time", "time_saved", "hrs/wk × 52 × rate",
              ["phone_hours_wk", "staff_rate"],
              lambda g: float(g["phone_hours_wk"]) * 52 * float(g["staff_rate"]),
              note="reported separately; never summed into revenue")
        .line("After-hours emergencies routed right", "scenario", "you decide what this is worth",
              ["emergency_value"], lambda g: float(g["emergency_value"]),
              assumption="safety routing is never monetized by us — this line is yours or blank"))


def roi(given):
    rec = {"lapsed_count": len(lapsed())}
    bf = backfill_stats()
    if "_missing" not in bf:
        rec["cancellations_90d"] = bf["cancellations"]
    visits = [a.get("value") for a in store.load("appointments") if a.get("value")]
    if len(visits) >= 30:
        rec["avg_visit"] = round(median(visits), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "route_emergency", "draft_reminder", "draft_backfill_offer",
          "book_appointment")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("client:",))
