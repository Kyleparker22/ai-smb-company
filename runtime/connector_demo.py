#!/usr/bin/env python3
"""yourco — the give-first demo arsenal (Connector OS step 4).

Generates a real, personalized, self-contained demo-kit instance for a business a connector just met:
walk into your dentist's office, say "watch this," and minutes later they can tap through what an AI
teammate would actually do for them. The connector never pitches — they **give**.

Spec: `processes/partnerships/connector-os.md` §4. Decision: `decisions/2026-08-07_connector-os.md`.
Template (never modified by this script, only copied): `clients/_yourco-template/demo-kit/`.

--------------------------------------------------------------------------------------------------
THE GATE COMES FIRST — ALWAYS
--------------------------------------------------------------------------------------------------
Demo generation is an **R1** capability. Every run loads `crm/connector_ladder.compute()` and refuses
unless `connector_ladder.can(rungN, "demo_generation")` is true. R1 is earned by one referral reaching
a real conversation (sit-down/audit or beyond) — evidence from the CRM, never granted by mood.

Two risks are being gated, per the Founder (2026-08-07): a generated demo (a) carries yourco's brand to a
stranger — an external surface — and (b) costs real build/token spend. Pre-launch, **every** connector
fails this gate, because no connector has signed. That refusal path is the normal path today and it
prints exactly why plus what earns R1.

--------------------------------------------------------------------------------------------------
CONTENT GUARDRAILS (enforced in code, fail-closed — nothing is written if a check trips)
--------------------------------------------------------------------------------------------------
1. **No prices, ever.** Polo owns the bands and prices are shared in proposals only (CLAUDE.md
   §External-surface rules). `_PRICE_RE` scans the entire generated prospect-facing surface — the
   config plus the on-page notice — for currency, amounts, rates, or the word pricing. A hit aborts.
   (The template's `approval.locked` money field is deliberately never populated here.)
2. **No fabricated metrics or testimonials.** The credibility gate: the demo shows what an agent
   *would* do for this business, from its public identity plus plausible-but-clearly-illustrative
   scenarios. It never shows invented client results, percentages, hours-saved, multiples, uptime,
   or quoted praise. `_METRIC_RE` aborts the run on any of them. The monthly-report screen therefore
   ships with the metric **names** and a dash where a number would be — filled in from their real
   numbers once something is actually running.
3. **Every page is marked as a demo/preview.** A generated `demo-notice.js` puts a persistent banner
   on all four screens ("Preview · sample data — nothing here is live and nothing has been sent"),
   on top of the template's own footers, and every sample recipient is suffixed "(sample)".
4. **The connector is named, and named as independent.** The banner reads "Prepared for <business> by
   <connector>, an independent yourco referral partner — not an yourco employee." Counsel question 3
   in connector-os.md is about apparent authority; saying it on the surface is the cheap half of the
   answer (the agreement is the other half, and it is still counsel-gated).
5. **Brand per `brand/DESIGN.md`.** The notice uses the tokens — indigo `#161B33`, cream `#F4EFE6`,
   one brass `#B8965A` detail, lowercase `yourco`, no pure black/white. The kit itself renders in the
   prospect's own brand color; the notice is the one yourco-branded element.
6. **Rate-limited per connector** — MAX_DEMOS_PER_WINDOW in WINDOW_DAYS, counted from `demo.generated`
   events in the attribution log. No bypass flag: raising it is a deliberate code change.
7. **Every generation is logged** to the append-only attribution log via `connector_ladder.log_event`
   (`demo.generated` + connector, business, vertical, rung, path). That is what makes a connector who
   generates fifty demos and books nothing visible immediately (connector-os.md §4).

Sensitive verticals (medical, legal, financial, caregiving, funeral) carry an extra on-page line: the
agent drafts for a licensed human and never gives clinical, legal, or financial advice.

--------------------------------------------------------------------------------------------------
Usage
--------------------------------------------------------------------------------------------------
  python3 runtime/connector_demo.py --connector "Jane Connector" --business "Bayside Dental" \
      --vertical Dental [--out DIR] [--dry-run] [--json]
  python3 runtime/connector_demo.py --list-verticals

  --dry-run   preview what WOULD be generated (files, screens, drafted copy) and write nothing.
              Works even when the gate refuses — clearly labelled internal review, not a bypass:
              it writes no file, logs no event, and produces no surface anyone can be shown.

STAGED: the arsenal is counsel- + launch-gated with the rest of the Connector OS. Nothing here is
offered to any connector yet. Test seam: set YOURCO_ATTRIBUTION_LOG to redirect the append-only log
to a throwaway path (tests only — never in production, where the real log is the audit trail).
"""
import os, sys, re, json, shutil, difflib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATE = os.path.join(REPO, "clients", "_yourco-template", "demo-kit")
VERTICALS_JSON = os.path.join(REPO, "runtime", "intent_verticals.json")
DEFAULT_OUT_ROOT = os.path.join(REPO, "agents", "bird", "connector-demos")

sys.path.insert(0, os.path.join(REPO, "crm"))
import connector_ladder as ladder  # noqa: E402  (gate + attribution log — one source of truth)

# Test seam: redirect the append-only log so a test run never pollutes crm/_attribution-log.jsonl.
_LOG_OVERRIDE = os.environ.get("YOURCO_ATTRIBUTION_LOG")
if _LOG_OVERRIDE:
    ladder.LOG = os.path.abspath(_LOG_OVERRIDE)

CAPABILITY = "demo_generation"          # unlocked at R1 (crm/connector_ladder.py UNLOCKS)
MAX_DEMOS_PER_WINDOW = 5
WINDOW_DAYS = 7
BRAND = {"indigo": "#161B33", "cream": "#F4EFE6", "brass": "#B8965A",
         "on_dark_muted": "rgba(244,239,230,.66)"}

# ---- content guardrails --------------------------------------------------------------------
_PRICE_RE = re.compile(
    r"(?:[$€£]\s?\d)"                                   # $1,000 / £50
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:dollars?|usd|eur|gbp)\b"
    r"|\b(?:per month|/mo\b|/month\b|monthly (?:fee|rate|price|cost))"
    r"|\bpricing\b|\bprices?\b|\bretainer\b|\bdeposit of\b|\binvoice for\b",
    re.I)
_METRIC_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s?%"                              # any percentage claim
    r"|\b\d+(?:\.\d+)?x\b"                              # 3x
    r"|\bsaved\b|\b~?\d+\s*(?:hours?|hrs?)\b"        # any hours-saved style claim
    r"|\b(?:increased?|boosted?|grew|reduced?|cut)\s+(?:\w+\s+){0,3}(?:by\s+)?\d"
    r"|\bROI\b|\bup to \d|\bguaranteed?\b"
    r"|\btestimonial|\b(?:clients?|customers?)\s+(?:say|said|report|saw)\b"
    r"|\buptime\b|\b\d+\s+(?:clients|customers|businesses)\b",
    re.I)


def scan_content(text):
    """Every guardrail violation in the prospect-facing surface. Empty list = clean."""
    bad = []
    for label, rx in (("price/currency", _PRICE_RE), ("fabricated metric/claim", _METRIC_RE)):
        for m in rx.finditer(text or ""):
            s = max(0, m.start() - 45)
            bad.append(f"{label}: …{(text[s:m.end() + 45]).strip()}…")
    return bad


# ---- verticals -----------------------------------------------------------------------------
def load_verticals():
    """The canonical vertical list — runtime/intent_verticals.json, the same one Sadie's sweep uses."""
    with open(VERTICALS_JSON, encoding="utf-8") as f:
        d = json.load(f)
    return [v["vertical"] for v in d.get("verticals", []) if v.get("vertical")]


# Archetype per vertical. Five shapes cover the list; anything unmapped gets `generic`, which is
# honest rather than wrong. All copy below is ILLUSTRATIVE — no results, no numbers, no prices.
ARCHETYPE_OF = {
    "trades": ["Landscaping", "Hardscaping", "HVAC", "Plumbing", "Roofing", "Electrical",
               "Auto Repair", "Cleaning Services", "Pest Control", "Restoration", "Garage Door",
               "Tree Service", "Pool Service", "Solar", "Fencing & Decks", "Painting",
               "Window & Door", "General Contractors", "Home Builders", "Concrete & Masonry",
               "Foundation Repair", "Flooring", "Kitchen & Bath Sample Company 47", "Septic & Well",
               "Excavation", "Commercial Cleaning", "Moving & Storage",
               "Porta Potty & Portable Sanitation", "Waste Hauling & Junk Removal",
               "Biohazard Cleanup"],
    "clinic": ["Dental", "Med Spa", "Veterinary", "Peptide Clinics", "Wellness Clinics",
               "IV Therapy", "Hormone / TRT Clinics", "Recovery & Cold Plunge", "Family Medical",
               "Orthodontics", "Chiropractic", "Physical Therapy", "Plastic Surgery", "Dermatology"],
    "professional": ["Law Firms", "Real Estate", "Accounting / CPA", "Sample Contact",
                     "Insurance Agencies", "Public Adjusters", "Mortgage Brokers",
                     "Property Management", "Title & Escrow", "Bookkeeping"],
    "hospitality": ["Boutique Hotels", "Sports & Fitness Facilities"],
    "care": ["Caregiving", "Funeral Homes"],
}
SENSITIVE = {"clinic", "professional", "care"}

ARCHETYPES = {
    "trades": {
        "use_case": "Missed-call rescue → the follow-up drafted before you're off the job",
        "pillar": "Intake / Front Desk",
        "step1": ("A call comes in while the crew is working",
                  "Nobody can pick up. Your front-desk teammate answers in {biz}'s voice, gets the name, "
                  "the address, and what they need — then drafts the follow-up. Nothing goes out yet."),
        "approver": "whoever runs the phone",
        "kind": "Missed-call follow-up",
        "to": "Dana Whitfield (sample)",
        "sub": "Called this afternoon — driveway and front walkway, asked about getting on the schedule",
        "email": ("Subject: Sorry we missed you — {biz}\n\n"
                  "Hi Dana,\n\n"
                  "Thanks for calling {biz} this afternoon. The crew was out on a job and we couldn't "
                  "get to the phone.\n\n"
                  "You mentioned the driveway and front walkway. I can get someone out to look at it and "
                  "walk you through the options. Would Thursday morning or Friday afternoon suit you "
                  "better?\n\n"
                  "Either way, we'll take care of you.\n\n"
                  "— {biz}"),
        "sms": "Hi Dana — {biz} here, sorry we missed your call. Thursday AM or Friday PM to come take a look?",
        "board_title": "jobs and inquiries in flight",
        "jobs": [
            {"name": "Dana Whitfield (sample)", "project": "Driveway + front walkway", "when": "called today",
             "badge": "new inquiry", "badgeClass": "run",
             "gates": [("Answered", "done", "Picked up in your voice, details captured"),
                       ("Follow-up", "pend", "Drafted — waiting on your okay"),
                       ("Visit", "wait", "Two windows offered")],
             "next": "your tap sends the follow-up; the visit lands on the calendar from her reply."},
            {"name": "Ellis Property (sample)", "project": "Repair quote requested", "when": "opened Tuesday",
             "badge": "in progress", "badgeClass": "run",
             "gates": [("Answered", "done", "Web form captured and qualified"),
                       ("Follow-up", "done", "You approved it Tuesday"),
                       ("Visit", "pend", "Awaiting a reply — nudge drafted")],
             "next": "gone quiet two days; the check-in is written and waiting on you."},
            {"name": "Marcus Reed (sample)", "project": "Seasonal service, repeat customer", "when": "booked",
             "badge": "booked ✓", "badgeClass": "go", "greenlit": True,
             "gates": [("Answered", "done", "Recognised as a returning customer"),
                       ("Follow-up", "done", "Sent after your approval"),
                       ("Visit", "done", "On the schedule")],
             "next": "nothing needed from you."},
        ],
        "nudges": ["<b>Ellis Property</b> — no reply since Tuesday. A short check-in is drafted and waiting on your okay.",
                   "<b>Two after-hours calls</b> last night — both answered, both drafted, both waiting for you."],
        "did": ["Answered every call the crew couldn't get to — including after hours — in your voice.",
                "Captured the name, the address, and what they actually want, without a form.",
                "Drafted the follow-up text and email, and held them until a human tapped approve.",
                "Chased the ones that went quiet, and flagged the ones worth a phone call from you."],
        "track": ["calls answered that would have gone to voicemail",
                  "follow-ups drafted and approved",
                  "inquiries that turned into a booked visit"],
    },
    "clinic": {
        "use_case": "New-patient inquiries answered, and the schedule kept full",
        "pillar": "Intake / Front Desk",
        "step1": ("Someone calls or messages about becoming a patient",
                  "Your front-desk teammate answers in {biz}'s voice, takes what's needed to book, and "
                  "drafts the reply. It never gives clinical guidance — that stays with your team."),
        "approver": "your front-desk lead",
        "kind": "New-patient reply",
        "to": "Priya Raman (sample)",
        "sub": "Asked about becoming a new patient and what appointment times look like",
        "email": ("Subject: Welcome to {biz}\n\n"
                  "Hi Priya,\n\n"
                  "Thanks for reaching out to {biz} — we'd be glad to see you.\n\n"
                  "I have space Tuesday morning or Thursday afternoon for a first visit. Let me know "
                  "which works and I'll hold it for you, and I'll send the new-patient forms so you're "
                  "not filling anything in at the door.\n\n"
                  "Anything clinical, our team will go through with you in person.\n\n"
                  "— The team at {biz}"),
        "sms": "Hi Priya — {biz} here. I can hold Tuesday AM or Thursday PM for your first visit. Which suits?",
        "board_title": "inquiries and appointments in flight",
        "jobs": [
            {"name": "Priya Raman (sample)", "project": "New patient — first visit", "when": "messaged today",
             "badge": "new inquiry", "badgeClass": "run",
             "gates": [("Answered", "done", "Replied in your voice, no clinical content"),
                       ("Reply", "pend", "Drafted — waiting on your okay"),
                       ("Booked", "wait", "Two times offered")],
             "next": "one tap sends it; the booking follows from her reply."},
            {"name": "Jordan Bell (sample)", "project": "Rescheduled, never rebooked", "when": "3 weeks quiet",
             "badge": "in progress", "badgeClass": "run",
             "gates": [("Spotted", "done", "Found in the gap list"),
                       ("Reply", "pend", "Warm rebooking note drafted"),
                       ("Booked", "wait", "Not yet")],
             "next": "the rebooking note is written and waiting for a human to approve."},
            {"name": "Alina Cruz (sample)", "project": "Forms + reminders", "when": "confirmed",
             "badge": "confirmed ✓", "badgeClass": "go", "greenlit": True,
             "gates": [("Answered", "done", "Reminder acknowledged"),
                       ("Reply", "done", "Approved and sent"),
                       ("Booked", "done", "Forms returned before the visit")],
             "next": "nothing needed from you."},
        ],
        "nudges": ["<b>Jordan Bell</b> — rescheduled and never rebooked. A warm note is drafted, waiting on you.",
                   "<b>Two after-hours inquiries</b> answered overnight — replies drafted, nothing sent."],
        "did": ["Answered new-patient calls and messages after hours, in your practice's voice.",
                "Held every reply for a human tap — nothing reached a patient unapproved.",
                "Spotted patients who slipped off the schedule and drafted the rebooking note.",
                "Kept forms and reminders moving so the front desk wasn't chasing them."],
        "track": ["inquiries answered outside office hours",
                  "replies drafted and approved by your team",
                  "gaps in the schedule surfaced before the day arrived"],
    },
    "professional": {
        "use_case": "Every inquiry answered, every document chased — drafted for your review",
        "pillar": "Intake / Front Desk",
        "step1": ("An inquiry arrives — a call, a form, a referral",
                  "Your intake teammate answers in {biz}'s voice, collects what's needed to triage, and "
                  "drafts the reply for a licensed human to review. It never gives advice."),
        "approver": "whoever reviews intake",
        "kind": "New inquiry reply",
        "to": "T. Okafor (sample)",
        "sub": "Inquiry submitted this morning — asked what happens next and how soon you can talk",
        "email": ("Subject: Thanks for reaching out — {biz}\n\n"
                  "Hi,\n\n"
                  "Thanks for contacting {biz}. I've passed your note to the team and someone will go "
                  "through it with you properly.\n\n"
                  "To make that call useful, could you confirm the best number to reach you and a couple "
                  "of times that suit? I have Wednesday morning and Thursday afternoon open.\n\n"
                  "Nothing in this note is advice — the team will cover that with you directly.\n\n"
                  "— {biz}"),
        "sms": "Hi — {biz} here, thanks for your inquiry. Wednesday AM or Thursday PM for a quick call?",
        "board_title": "inquiries and files in flight",
        "jobs": [
            {"name": "T. Okafor (sample)", "project": "New inquiry — triage", "when": "arrived today",
             "badge": "new inquiry", "badgeClass": "run",
             "gates": [("Captured", "done", "Details collected, nothing advised"),
                       ("Reply", "pend", "Drafted for your review"),
                       ("Call", "wait", "Two windows offered")],
             "next": "your review sends it; the call books from the reply."},
            {"name": "Halvorsen file (sample)", "project": "Outstanding documents", "when": "opened last week",
             "badge": "in progress", "badgeClass": "run",
             "gates": [("Captured", "done", "Checklist built from the file"),
                       ("Reply", "pend", "Chase note drafted"),
                       ("Complete", "wait", "Two items outstanding")],
             "next": "the chase is written; approve it and it goes."},
            {"name": "Renwick matter (sample)", "project": "Status update to the client", "when": "current",
             "badge": "up to date ✓", "badgeClass": "go", "greenlit": True,
             "gates": [("Captured", "done", "Milestones tracked"),
                       ("Reply", "done", "You approved the update"),
                       ("Complete", "done", "Client acknowledged")],
             "next": "nothing needed from you."},
        ],
        "nudges": ["<b>Halvorsen file</b> — two documents still outstanding. The chase note is drafted, waiting on you.",
                   "<b>An inquiry from Friday</b> hasn't had a human reply yet — the draft is ready."],
        "did": ["Answered inquiries the same hour they arrived, in your firm's voice.",
                "Drafted every reply for a licensed human to review — never advice, never sent unapproved.",
                "Chased outstanding documents until the checklist was complete.",
                "Flagged anything sitting too long before the client had to ask."],
        "track": ["inquiries answered the same day",
                  "replies drafted and reviewed before sending",
                  "outstanding items closed without a human chasing them"],
    },
    "hospitality": {
        "use_case": "Every question answered, every booking followed up",
        "pillar": "Intake / Front Desk",
        "step1": ("A guest question or booking request comes in",
                  "Your front-desk teammate answers in {biz}'s voice, handles what it can, and drafts "
                  "anything that needs a person. Nothing goes out unapproved."),
        "approver": "your duty manager",
        "kind": "Guest reply",
        "to": "The Alvarado party (sample)",
        "sub": "Asked about availability and what's included",
        "email": ("Subject: Thanks for getting in touch — {biz}\n\n"
                  "Hi,\n\n"
                  "Thanks for reaching out to {biz}. I've got availability across the dates you mentioned "
                  "and can hold something while you decide.\n\n"
                  "Let me know which works and anything you'd like set up in advance, and I'll get it "
                  "arranged before you arrive.\n\n"
                  "— {biz}"),
        "sms": "Hi — {biz} here. I can hold those dates for you while you decide. Want me to?",
        "board_title": "guest requests in flight",
        "jobs": [
            {"name": "The Alvarado party (sample)", "project": "Availability inquiry", "when": "today",
             "badge": "new inquiry", "badgeClass": "run",
             "gates": [("Answered", "done", "Replied in your voice"),
                       ("Reply", "pend", "Drafted — waiting on you"),
                       ("Held", "wait", "Dates offered")],
             "next": "one tap sends it and the hold goes on."},
            {"name": "Weekend group (sample)", "project": "Follow-up after a visit", "when": "last week",
             "badge": "in progress", "badgeClass": "run",
             "gates": [("Answered", "done", "Thank-you drafted"),
                       ("Reply", "pend", "Waiting on your okay"),
                       ("Rebooked", "wait", "Not yet")],
             "next": "approve the note and it goes out this afternoon."},
            {"name": "Standing booking (sample)", "project": "Reminder + details confirmed", "when": "confirmed",
             "badge": "confirmed ✓", "badgeClass": "go", "greenlit": True,
             "gates": [("Answered", "done", "Reminder acknowledged"),
                       ("Reply", "done", "Approved and sent"),
                       ("Held", "done", "Details confirmed")],
             "next": "nothing needed from you."},
        ],
        "nudges": ["<b>Weekend group</b> — no follow-up sent yet. The thank-you is drafted and waiting on you.",
                   "<b>Overnight questions</b> answered — anything needing a person is drafted, not sent."],
        "did": ["Answered guest questions at any hour, in your voice.",
                "Drafted every reply that needed a person and held it for approval.",
                "Followed up after visits so nobody had to remember to.",
                "Confirmed details ahead of arrival without the desk chasing."],
        "track": ["questions answered outside desk hours",
                  "replies drafted and approved",
                  "follow-ups that would otherwise have been missed"],
    },
    "care": {
        "use_case": "Every inquiry answered with care, and nothing said that shouldn't be",
        "pillar": "Intake / Front Desk",
        "step1": ("Someone reaches out at a hard moment",
                  "Your teammate answers in {biz}'s voice — warm, brief, and human. It never gives "
                  "medical, legal, or financial guidance. Anything that needs a person is drafted and waits."),
        "approver": "whoever handles first contact",
        "kind": "First-contact reply",
        "to": "The Bennett family (sample)",
        "sub": "Reached out this morning asking how to start and who to speak to",
        "email": ("Subject: We're here — {biz}\n\n"
                  "Hello,\n\n"
                  "Thank you for reaching out to {biz}. Someone from our team will speak with you "
                  "personally — you don't need to sort anything out before then.\n\n"
                  "If it helps, let me know a time today or tomorrow that suits and I'll make sure "
                  "someone calls you then.\n\n"
                  "— {biz}"),
        "sms": "Hello — {biz} here. Someone from our team will call you personally. What time today or tomorrow suits?",
        "board_title": "families and inquiries in flight",
        "jobs": [
            {"name": "The Bennett family (sample)", "project": "First contact", "when": "this morning",
             "badge": "new inquiry", "badgeClass": "run",
             "gates": [("Answered", "done", "Warm acknowledgement, nothing advised"),
                       ("Reply", "pend", "Drafted — waiting on a person"),
                       ("Call", "wait", "Times offered")],
             "next": "a person approves it, and a person makes the call."},
            {"name": "Ongoing arrangement (sample)", "project": "Check-in", "when": "due",
             "badge": "in progress", "badgeClass": "run",
             "gates": [("Noticed", "done", "Check-in due"),
                       ("Reply", "pend", "Note drafted"),
                       ("Done", "wait", "Not yet")],
             "next": "the note is written; your team decides whether to send it or call instead."},
            {"name": "Recent inquiry (sample)", "project": "Details confirmed", "when": "handled",
             "badge": "handled ✓", "badgeClass": "go", "greenlit": True,
             "gates": [("Answered", "done", "Acknowledged same day"),
                       ("Reply", "done", "Approved by your team"),
                       ("Done", "done", "Call took place")],
             "next": "nothing needed from you."},
        ],
        "nudges": ["<b>Ongoing arrangement</b> — a check-in is due. The note is drafted; a person decides.",
                   "<b>An overnight inquiry</b> was acknowledged warmly; the real reply is waiting for a person."],
        "did": ["Acknowledged every inquiry quickly and warmly, at any hour.",
                "Never offered medical, legal, or financial guidance — that stayed with your people.",
                "Drafted the replies that needed a person, and waited.",
                "Made sure nobody sat unanswered because the day got busy."],
        "track": ["inquiries acknowledged within the hour",
                  "replies drafted for a person to approve",
                  "follow-ups that didn't fall through"],
    },
    "generic": {
        "use_case": "Every inbound answered, every follow-up drafted",
        "pillar": "Intake / Front Desk",
        "step1": ("An inquiry comes in and nobody's free to take it",
                  "Your front-desk teammate answers in {biz}'s voice, captures what matters, and drafts "
                  "the follow-up. Nothing goes out yet."),
        "approver": "whoever runs the inbox",
        "kind": "Inquiry follow-up",
        "to": "Sam Delaney (sample)",
        "sub": "Got in touch this morning asking how to get started",
        "email": ("Subject: Thanks for getting in touch — {biz}\n\n"
                  "Hi Sam,\n\n"
                  "Thanks for reaching out to {biz}. Sorry we couldn't get to you straight away.\n\n"
                  "I'd like to get you to the right person. Would Wednesday morning or Thursday "
                  "afternoon work for a quick call?\n\n"
                  "— {biz}"),
        "sms": "Hi Sam — {biz} here, sorry we missed you. Wednesday AM or Thursday PM for a quick call?",
        "board_title": "inquiries in flight",
        "jobs": [
            {"name": "Sam Delaney (sample)", "project": "New inquiry", "when": "today",
             "badge": "new inquiry", "badgeClass": "run",
             "gates": [("Answered", "done", "Captured in your voice"),
                       ("Follow-up", "pend", "Drafted — waiting on you"),
                       ("Call", "wait", "Two windows offered")],
             "next": "one tap sends it."},
            {"name": "Quiet since Tuesday (sample)", "project": "No reply yet", "when": "opened Tuesday",
             "badge": "in progress", "badgeClass": "run",
             "gates": [("Answered", "done", "Reply approved and sent"),
                       ("Follow-up", "pend", "Nudge drafted"),
                       ("Call", "wait", "Not yet")],
             "next": "the nudge is written and waiting on your okay."},
            {"name": "Booked (sample)", "project": "Call on the calendar", "when": "booked",
             "badge": "booked ✓", "badgeClass": "go", "greenlit": True,
             "gates": [("Answered", "done", "Same hour"),
                       ("Follow-up", "done", "Approved and sent"),
                       ("Call", "done", "On the calendar")],
             "next": "nothing needed from you."},
        ],
        "nudges": ["<b>Quiet since Tuesday</b> — a short nudge is drafted and waiting on you.",
                   "<b>After-hours inquiries</b> answered overnight; the replies are drafted, not sent."],
        "did": ["Answered inbound the moment it arrived, including after hours, in your voice.",
                "Captured what actually matters instead of a form nobody fills in.",
                "Drafted every follow-up and held it until a human approved.",
                "Chased the quiet ones and surfaced anything worth your call."],
        "track": ["inbound answered that would have been missed",
                  "follow-ups drafted and approved",
                  "inquiries that turned into a real conversation"],
    },
}


def archetype_for(vertical):
    for key, verticals in ARCHETYPE_OF.items():
        if vertical in verticals:
            return key
    return "generic"


# ---- generation ----------------------------------------------------------------------------
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-") or "unknown"


def build_config(business, vertical, connector, brand_hex="#2f5d7c"):
    """The generated `window.DEMO` object. Illustrative only — no prices, no invented results."""
    a = ARCHETYPES[archetype_for(vertical)]
    sensitive = archetype_for(vertical) in SENSITIVE
    fmt = lambda s: s.format(biz=business)  # noqa: E731

    steps = [
        {"n": 1, "flow": True, "title": fmt(a["step1"][0]), "desc": fmt(a["step1"][1])},
        {"n": 2, "href": "approval.html", "title": "You approve before anything sends",
         "desc": "The drafted message, on your phone. Approve, edit, or decline — it waits either way."},
        {"n": 3, "href": "board.html", "title": "See everything in flight from one screen",
         "desc": "What's answered, what's drafted, what's gone quiet — and what needs a nudge today."},
        {"n": 4, "href": "report.html", "title": "A monthly report of what it actually did",
         "desc": "The measures filled in from your own numbers once it's running — never guessed."},
    ]

    tagline = (f"This is a preview built for {business} — sample data, nothing live, nothing sent. "
               f"It shows what an AI teammate would do inside {business}: answer what comes in, draft "
               f"what needs saying, and wait for a human before anything reaches a real person.")

    approval = {
        "approver": a["approver"],
        "intro": "one message is drafted and waiting on you",
        "items": [{
            "kind": a["kind"], "to": a["to"], "sub": fmt(a["sub"]),
            "email": fmt(a["email"]), "sms": fmt(a["sms"]),
            "together": "Sends as email and text together, from your own address and your own number.",
        }],
    }

    board = {
        "title": a["board_title"],
        "metrics": [
            {"v": str(len(a["jobs"])), "l": "items in flight (sample)"},
            {"v": str(sum(1 for j in a["jobs"] if any(g[1] == "pend" for g in j["gates"]))),
             "l": "drafted, waiting on you", "accent": True},
            {"v": str(sum(1 for j in a["jobs"] if j.get("greenlit"))), "l": "closed out"},
            {"v": "0", "l": "sent without a human tap", "accent": True},
        ],
        "nudges": [fmt(n) for n in a["nudges"]],
        "jobs": [{"name": j["name"], "project": j["project"], "total": j["when"],
                  "badge": j["badge"], "badgeClass": j["badgeClass"],
                  "greenlit": bool(j.get("greenlit")),
                  "gates": [{"label": g[0], "state": g[1], "text": g[2]} for g in j["gates"]],
                  "next": j["next"]} for j in a["jobs"]],
    }

    reliability = [
        {"v": "0", "l": "messages reach anyone without a human tap — that's the design, not a target"},
        {"v": "0", "l": "figures invented — anything numeric is computed by tested code or left blank"},
        {"v": "1", "l": "tap to approve, edit, or decline — the control never leaves your team"},
    ]
    if sensitive:
        reliability.append({"v": "0", "l": "clinical, legal, or financial guidance given — ever"})

    report = {
        "period": "sample month",
        "stats": [{"v": "—", "l": f"{t} — filled in from your own numbers once it's running"}
                  for t in a["track"]],
        "buckets": [],
        "did": [fmt(x) for x in a["did"]],
        "reliability": reliability,
        "reliabilityLine": (
            "This is what the report would show. The numbers stay blank here on purpose — a preview that "
            "invents results isn't worth reading. What is real today is the design: every outgoing message "
            "waits for a human, every change ships behind an eval suite, and every action lands in an audit "
            "log you can read back."),
    }

    return {
        "client": business,
        "brand": brand_hex,
        "employee": "your AI teammate",
        "useCase": a["use_case"],
        "tagline": tagline,
        "_preview": {
            "generatedFor": business, "vertical": vertical, "pillar": a["pillar"],
            "preparedBy": connector,
            "note": ("Preview on sample data. Nothing here is live, nothing has been sent, and no real "
                     "person has been contacted."),
        },
        "steps": steps, "approval": approval, "board": board, "report": report,
    }


def notice_text(business, connector, vertical):
    """The two lines every generated page shows. Named separately so the guardrail scan sees them."""
    line = "Preview · sample data — nothing here is live and nothing has been sent."
    sub = (f"Prepared for {business} by {connector}, an independent yourco referral partner "
           f"— not an yourco employee.")
    if archetype_for(vertical) in SENSITIVE:
        sub += (" This teammate drafts for a licensed human and never gives clinical, legal, "
                "or financial advice.")
    return line, sub


def notice_js(business, connector, vertical):
    """The persistent demo/preview banner injected on every generated page (brand/DESIGN.md tokens)."""
    line, sub = notice_text(business, connector, vertical)
    payload = json.dumps({"line": line, "sub": sub, "brand": BRAND})
    return (
        "/* yourco — generated demo notice. Every page is marked as a preview (connector_demo.py\n"
        "   guardrail 3). Do not remove: a generated demo that doesn't say it's a demo is the one\n"
        "   thing this arsenal must never produce. */\n"
        "(function () {\n"
        "  var N = " + payload + ";\n"
        "  function mount() {\n"
        "    var b = document.createElement('div');\n"
        "    b.setAttribute('role', 'note');\n"
        "    b.style.cssText = 'position:sticky;top:0;z-index:9999;background:" + BRAND["indigo"] + ";"
        "color:" + BRAND["cream"] + ";border-bottom:1px solid " + BRAND["brass"] + ";"
        "padding:9px 16px;font:600 12.5px/1.45 -apple-system,system-ui,\"Segoe UI\",Helvetica,Arial,sans-serif;"
        "text-align:center;letter-spacing:.01em';\n"
        "    var one = document.createElement('div'); one.textContent = N.line;\n"
        "    var two = document.createElement('div');\n"
        "    two.style.cssText = 'font-weight:500;color:" + BRAND["on_dark_muted"] + ";margin-top:2px';\n"
        "    two.textContent = N.sub;\n"
        "    b.appendChild(one); b.appendChild(two);\n"
        "    document.body.insertBefore(b, document.body.firstChild);\n"
        "  }\n"
        "  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);\n"
        "  else mount();\n"
        "})();\n")


PAGES = [("index.html", "index", "Your setup, end to end"),
         ("approval.html", "approval", "Approve before it sends"),
         ("board.html", "board", "Everything in flight"),
         ("report.html", "report", "What it did")]


def page_html(filename, page, title, business):
    return ('<!DOCTYPE html>\n<html lang="en">\n<head><meta charset="utf-8" />'
            '<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            f'<title>{title} — {business} (demo preview)</title>\n'
            f'<meta name="robots" content="noindex, nofollow" /></head>\n'
            f'<body data-page="{page}"><div id="app"></div>\n'
            '<script src="config.js"></script><script src="demo-notice.js"></script>'
            '<script src="kit.js"></script></body>\n</html>\n')


def plan_files(business, vertical, connector):
    """Everything that would be written, as {relative path: content}. kit.js is copied verbatim."""
    cfg = build_config(business, vertical, connector)
    cfg_js = ("/* GENERATED by runtime/connector_demo.py — a give-first demo preview.\n"
              f"   For: {business} ({vertical}) · prepared by: {connector} · "
              f"{datetime.date.today().isoformat()}\n"
              "   Sample data only. No prices, no invented results, nothing live, nothing sent. */\n"
              "window.DEMO = " + json.dumps(cfg, indent=2, ensure_ascii=False) + ";\n")
    notice = notice_js(business, connector, vertical)

    files = {"config.js": cfg_js, "demo-notice.js": notice}
    for fn, page, title in PAGES:
        files[fn] = page_html(fn, page, title, business)
    files["README.md"] = (
        f"# Demo preview — {business}\n\n"
        f"Generated {datetime.date.today().isoformat()} by `runtime/connector_demo.py` for **{connector}**, "
        f"vertical **{vertical}**, pillar **{ARCHETYPES[archetype_for(vertical)]['pillar']}**.\n\n"
        "**Sample data only.** Nothing here is live, nothing has been sent, and no real person has been "
        "contacted. Every screen carries a preview banner saying so.\n\n"
        "Open `index.html` and walk the four screens in order. `demo-script.md` is what to say.\n\n"
        "Only `config.js` is worth editing — `kit.js` is the shared renderer, copied verbatim from "
        "`clients/_yourco-template/demo-kit/`.\n\n"
        "House rules that produced this file, and that still apply if you edit it: no prices (they come "
        "from yourco in a proposal, never from a demo), no invented results or testimonials, and the "
        "preview banner stays.\n")
    files["demo-script.md"] = (
        f"# Walking {business} through this\n\n"
        "Two minutes, four taps. Give-first: you are showing them something, not selling them something.\n\n"
        "1. **Open with the banner.** \"This is a preview on made-up data — nothing here is real and "
        "nothing has been sent. I just wanted you to see it.\"\n"
        f"2. **index.html** — \"Here's the whole thing end to end for {business}.\" Read step 1 out loud.\n"
        "3. **approval.html** — hand them your phone. Let *them* tap approve. This is the moment: "
        "nothing reaches a customer without a human tap.\n"
        "4. **board.html** — \"And you'd see everything in flight from one screen, including what's gone "
        "quiet.\"\n"
        "5. **report.html** — point at the dashes. \"Those stay blank on purpose. I'm not going to show "
        "you numbers nobody earned yet.\"\n\n"
        "**Close by giving, not asking:** \"Want me to introduce you to the people who build these? No "
        "pressure either way.\"\n\n"
        "**Do not:** quote a number, promise a timeline, or answer a commercial question. You are an "
        "independent referral partner, not an yourco employee — hand those to yourco and you keep the "
        "relationship clean.\n")
    return cfg, files


def guardrail_check(cfg, business, connector, vertical):
    """Scan everything a prospect can actually read — the DEMO payload + the on-page banner.

    Deliberately NOT the generated file headers or the connector-facing README/demo-script: those
    *talk about* the no-prices rule, and a scanner that trips on the word in its own rule is a
    scanner nobody keeps. Fail-closed on the surface that matters.
    """
    line, sub = notice_text(business, connector, vertical)
    surface = json.dumps(cfg, ensure_ascii=False) + "\n" + line + "\n" + sub
    return scan_content(surface)


def unique_dir(path):
    if not os.path.exists(path):
        return path
    for i in range(2, 50):
        cand = f"{path}-{i}"
        if not os.path.exists(cand):
            return cand
    raise RuntimeError("too many demos generated at the same path today")


# ---- the gate ------------------------------------------------------------------------------
def recent_demo_count(connector):
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=WINDOW_DAYS)
    n = 0
    for e in ladder.read_events():
        if e.get("event") != "demo.generated" or e.get("connector") != connector:
            continue
        try:
            if datetime.datetime.fromisoformat(e.get("ts", "")) >= cutoff:
                n += 1
        except ValueError:
            continue
    return n


def resolve_connector(state, name):
    for k in state:
        if k.lower() == (name or "").strip().lower():
            return k, None
    close = difflib.get_close_matches(name or "", list(state), n=3, cutoff=0.5)
    return None, close


def check_gate(state, connector):
    """(ok, reason, detail). The gate is evaluated before anything else is decided."""
    s = state[connector]
    if not ladder.can(s["rungN"], CAPABILITY):
        r1 = next(r for r in ladder.RUNGS if r["n"] == 1)
        return False, "rung", {
            "rung": s["rung"], "rungName": s["rungName"], "rungN": s["rungN"],
            "needs": "R1 · Proven", "earn": r1["earn"], "evidence": s["evidence"],
            "unlocks": s["unlocks"]}
    used = recent_demo_count(connector)
    if used >= MAX_DEMOS_PER_WINDOW:
        return False, "rate", {"used": used, "limit": MAX_DEMOS_PER_WINDOW, "windowDays": WINDOW_DAYS}
    return True, None, {"rung": s["rung"], "used": used, "limit": MAX_DEMOS_PER_WINDOW}


# ---- CLI -----------------------------------------------------------------------------------
def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv and len(argv) > argv.index(flag) + 1 else default


def main(argv=None, state=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    verticals = load_verticals()

    if "--list-verticals" in argv:
        print(f"# {len(verticals)} verticals (runtime/intent_verticals.json)\n")
        for v in verticals:
            print(f"  {v:<38} → {archetype_for(v)}")
        return 0

    connector_in = _arg(argv, "--connector")
    business = (_arg(argv, "--business") or "").strip()
    vertical_in = (_arg(argv, "--vertical") or "").strip()
    out_arg = _arg(argv, "--out")
    dry = "--dry-run" in argv
    as_json = "--json" in argv

    if not connector_in or not business or not vertical_in:
        print(__doc__.split("Usage\n")[-1].strip())
        return 2

    match = [v for v in verticals if v.lower() == vertical_in.lower()]
    if not match:
        close = difflib.get_close_matches(vertical_in, verticals, n=4, cutoff=0.4)
        print(f"✗ unknown vertical: {vertical_in!r}")
        if close:
            print("  did you mean: " + " · ".join(close))
        print("  --list-verticals for the full list")
        return 2
    vertical = match[0]

    # ---------- the gate, before anything else ----------
    state = state if state is not None else ladder.compute()
    connector, close = resolve_connector(state, connector_in)
    if not connector:
        print(f"✗ no connector named {connector_in!r} in the CRM"
              + (f"\n  did you mean: {' · '.join(close)}" if close else ""))
        return 2

    ok, reason, detail = check_gate(state, connector)
    result = {"connector": connector, "business": business, "vertical": vertical,
              "archetype": archetype_for(vertical), "gate": {"ok": ok, "reason": reason, **detail},
              "dryRun": dry, "written": False, "path": None, "event": None}

    if not ok and not dry:
        if as_json:
            print(json.dumps(result, indent=1))
        elif reason == "rung":
            print(f"✗ REFUSED — {connector} cannot generate demos yet.\n")
            print(f"  Rung now:   {detail['rung'] or '—'} · {detail['rungName']}")
            print(f"  Needs:      {detail['needs']} — demo generation is an R1 capability")
            print(f"  Earns R1:   {detail['earn']}")
            ev = detail["evidence"]
            print(f"  Evidence:   signed={ev['signed']} · referrals={ev['referrals']} · "
                  f"conversations={ev['conversations']} · live={ev['live']}")
            print(f"  Unlocked:   {', '.join(detail['unlocks']) or '(nothing — not joined)'}")
            print("\n  Why the gate exists: a generated demo carries yourco's brand to a stranger and "
                  "costs\n  real build spend. R1 evidence gates both (connector-os.md §4).")
            print("  Nothing was written and nothing was logged.")
            print("  Preview what this WOULD generate, for internal review: add --dry-run")
        else:
            print(f"✗ REFUSED — rate limit: {connector} has generated {detail['used']} demo(s) in the "
                  f"last {detail['windowDays']} days (limit {detail['limit']}).")
            print("  The limit is what keeps 'generate fifty, book nothing' from being free.")
            print("  Nothing was written and nothing was logged.")
        return 1

    # ---------- build ----------
    cfg, files = plan_files(business, vertical, connector)
    violations = guardrail_check(cfg, business, connector, vertical)
    result["guardrails"] = {"clean": not violations, "violations": violations}
    if violations:
        print("✗ ABORTED — content guardrails tripped; nothing written:")
        for v in violations:
            print("   · " + v)
        return 3

    out = out_arg or os.path.join(DEFAULT_OUT_ROOT, slug(connector),
                                  f"{slug(business)}-{datetime.date.today().isoformat()}")
    result["path"] = os.path.relpath(out, REPO) if out.startswith(REPO) else out

    if dry:
        result["files"] = sorted(list(files) + ["kit.js"])
        if as_json:
            print(json.dumps(result, indent=1))
            return 0
        banner = ("GATED — internal preview only. This connector could NOT generate this."
                  if not ok else "Gate passed.")
        print(f"# DRY RUN — nothing written, nothing logged\n\n  {banner}\n")
        if not ok and reason == "rung":
            print(f"  {connector}: {detail['rung'] or '—'} · {detail['rungName']} → needs R1 "
                  f"({detail['earn']})\n")
        print(f"  Would write to:  {result['path']}")
        print(f"  Business:        {business}  ·  vertical: {vertical}  ·  "
              f"archetype: {result['archetype']}  ·  pillar: {cfg['_preview']['pillar']}")
        print(f"  Files ({len(result['files'])}):    " + ", ".join(result["files"]))
        print(f"  Guardrails:      clean (no prices, no invented results)")
        print("\n  Screens:")
        for st in cfg["steps"]:
            print(f"    {st['n']}. {st['title']}")
        print("\n  The drafted message the prospect would approve:\n")
        for ln in cfg["approval"]["items"][0]["email"].splitlines():
            print("    | " + ln)
        print("\n    text: " + cfg["approval"]["items"][0]["sms"])
        print("\n  Banner on every page:")
        print("    | Preview · sample data — nothing here is live and nothing has been sent.")
        print(f"    | Prepared for {business} by {connector}, an independent yourco referral partner "
              f"— not an yourco employee.")
        return 0 if ok else 1

    # ---------- write ----------
    out = unique_dir(out)
    os.makedirs(out, exist_ok=True)
    shutil.copyfile(os.path.join(TEMPLATE, "kit.js"), os.path.join(out, "kit.js"))  # verbatim
    for rel, content in files.items():
        with open(os.path.join(out, rel), "w", encoding="utf-8") as f:
            f.write(content)
    result["path"] = os.path.relpath(out, REPO) if out.startswith(REPO) else out
    result["written"] = True

    ev = ladder.log_event("demo.generated", connector=connector, business=business, vertical=vertical,
                          rung=state[connector]["rung"], path=result["path"], by="connector_demo.py")
    result["event"] = {"id": ev["id"], "seq": ev["seq"], "ts": ev["ts"]}

    if as_json:
        print(json.dumps(result, indent=1))
    else:
        print(f"✓ demo generated for {business} ({vertical}) — prepared by {connector} "
              f"[{state[connector]['rung']}]")
        print(f"  {result['path']}/index.html")
        print(f"  {len(files) + 1} files · sample data only · every page banner-marked as a preview")
        print(f"  logged: demo.generated #{ev['seq']} ({ev['id']}) → "
              f"{os.path.relpath(ladder.LOG, REPO)}")
        used = recent_demo_count(connector)
        print(f"  rate:   {used}/{MAX_DEMOS_PER_WINDOW} in the last {WINDOW_DAYS} days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
