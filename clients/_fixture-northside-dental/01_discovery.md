# Discovery — Northside Dental / Remy (text-intake + scheduling)  🧪 DRY RUN

**Call date:** 2026-06-12 (mock) · **Attendees:** Dr. Patel (owner), Maria (office manager) · **Vertical:** dental

## 1. The job
First job: **handle inbound new-patient inquiries** (from the website "Request an Appointment" form + the info@ inbox) — acknowledge fast, qualify, book a new-patient visit, confirm, log. **Employee type:** text-intake + scheduling.

## 2. The trigger
A new **web-form submission** or an **inbound email** to info@northsidedental from a prospective patient.

## 3. The inputs + decision logic
- **Inputs:** the patient's message, the practice's new-patient calendar availability, the accepted-insurance list, the new-patient appointment types + durations.
- **Decision logic (qualify):** new vs. existing patient · reason for visit (cleaning/checkup vs. specific concern) · **is it clinical/urgent** (pain, swelling, trauma → escalate, don't advise) · insurance (in the accepted list? if unsure → flag, don't guess) · preferred days/times.

## 4. The output / action
- Acknowledge within minutes; collect the qualifying info conversationally.
- Offer 2–3 open new-patient slots; **book** the chosen one into Google Calendar; send a confirmation; **log** to the practice management system (PMS) / a tracking sheet.
- **Escalate** clinical questions, urgent/painful cases, and insurance it can't confirm to a human (front desk).

## 5. The gated actions (approval line)
- **Auto (no human):** acknowledge, qualify, offer slots, **book an open new-patient slot**, send the standard confirmation, log.
- **Escalate to a human (gated):** anything clinical/urgent · out-of-network or unconfirmable insurance · existing-patient changes (reschedule/cancel an existing treatment) · any request outside new-patient intake.

## 6. The systems (read/write)
- **Email** — the info@ inbox (read inbound, send the confirmation/reply). · **Google Calendar** — the new-patient scheduling calendar (read availability, create the event). · **PMS / tracking** — log the inquiry + booking (PMS API if available, else a Google Sheet stand-in at first). · Access path: **the Founder-approve tenant access**; practice grants it.

## 7. Brand voice + identity
- Operates as **"Remy, Northside Dental's front-desk assistant."** Tone: warm, calm, professional — reassuring, never clinical. Fixed copy: a confirmation template with date/time/address/what-to-bring + a "reply to reach a person" line.

## 8. Success metric (Desired Outcome)
- New-patient inquiries **acknowledged < 5 min**, **booked same day** where possible; the number of inquiries that go un-replied → **zero**; front desk freed from intake triage.

## 9. Approvals & constraints
- Go-live approver: Maria (office manager) + Dr. Patel.
- **Compliance: this is PHI.** Remy collects health-reason info. The practice is the HIPAA covered entity; **YourCo is a business associate → a BAA is required** (the standard DPA is *not* a BAA). Minimize what's collected/stored; no clinical advice. → see `_findings.md` #1.

## Build inputs confirmed?
- [x] Job + trigger + decision logic locked
- [x] Type + **stack selected** (text-intake + scheduling → Email + Calendar + PMS/Sheet)
- [x] Systems + access path known
- [x] Gated-actions (approval line) defined — clinical/insurance/existing-patient escalate
- [x] Brand voice + fixed copy captured
- [x] Success metric agreed · approver named
- [ ] ⚠️ **BAA** required before any PHI flows (blocks go-live for this vertical) — `_findings.md` #1
