# Ready-to-Hire — one-page PRD per SKU

> One tight PRD per off-the-shelf employee (`clients/webb/pages/yourco-site-v2/hire-config.js`). The discipline
> (from the "build the smallest working version" playbook): **User · Problem · Input · Output · Core features ·
> Edge cases · Won't build.** Each PRD is the build spec for Kimi (golden pattern), the demo script for Reed,
> and the scope fence that keeps a catalog SKU from sliding into a custom build (→ that routes to the Audit/OS).
> Spec context: `processes/off-the-shelf-employees.md`. Owner: Kimi (build) · Bella/Polo (scope + price) · Webb (page).

---

## 1. AI Front Desk (voice) — `receptionist`
- **User:** an owner/team that can't always answer the phone (on the job, after hours, slammed).
- **Problem:** missed & after-hours calls become a competitor's booked job; ~26% of local-business calls go unanswered (Invoca, Dec 2025).
- **Input:** inbound call → connected phone (forwarding) + calendar + services/FAQ + booking rules + voice/tone config. **Increasingly: an AI caller** (Google "Ask for Me") asking price/availability.
- **Output:** answered call (human or AI caller) → qualified → booked on the calendar (or message taken) → logged as a lead; owner notified.
- **Core features:** 24/7 answer in brand voice; qualify; book/route; **handle a self-identified AI caller via a deterministic pricing/availability path**; lead capture + notify; approval on anything customer-facing.
- **Edge cases:** angry caller / emergency → escalate to human; ambiguous request → take message; spam/robocall → drop; double-booking → calendar check; caller wants a firm price we can't give → ranges + book a quote.
- **Won't build:** deep custom CRM/field-service integrations, complex multi-department IVR trees, outbound cold calling. (→ Audit/OS.)

## 2. Missed-Call Text-Back — `missed-call-textback`
- **User:** anyone who can't always pick up but can't afford to lose the lead.
- **Problem:** ~85% of callers who can't reach you won't call back; the lead is gone in seconds.
- **Input:** a missed/unanswered call event (number forwarding) + the auto-text copy + optional booking link.
- **Output:** instant SMS to the caller opening a real reply thread → routed to booking/answer.
- **Core features:** fire on missed call within seconds; branded, tone-set message; two-way thread; hand to booking; 10DLC-compliant.
- **Edge cases:** repeat caller (don't spam); after-hours (set expectation); opt-out/STOP handling; non-mobile number (skip).
- **Won't build:** full SMS marketing campaigns/blasts, cold texting. (Compliance + scope.)

## 3. Review Responder — `review-responder`
- **User:** local business whose rank + trust ride on its star rating.
- **Problem:** reviews go unanswered; responding well protects reputation + local SEO, but it's a daily chore.
- **Input:** new review (Google/Yelp profile access) + tone rules + auto-post-vs-approve setting.
- **Output:** a drafted (or auto-posted) on-brand reply per review; negative ones flagged to owner.
- **Core features:** monitor profiles; draft in owner voice; escalate/flag negatives; auto-post positives if opted in; approval gate default.
- **Edge cases:** fake/abusive review → flag, don't engage; legal/medical complaint → human only; review that needs a real fix → notify owner.
- **Won't build:** review *generation*/solicitation gating (separate), responses on platforms without an API.

## 4. Reminder & Recall — `reminder-recall`
- **User:** appointment-based business with no-shows and lapsing customers.
- **Problem:** forgotten appointments leave unfillable gaps; recurring customers lapse unnoticed.
- **Input:** scheduling tool/calendar access + reminder copy & timing + "lapsed" definition.
- **Output:** timed reminders (cut no-shows) + re-engagement nudges to lapsed customers → rebookings.
- **Core features:** reminder cadence; confirm/reschedule handling; recall rule by recency; rebook into calendar.
- **Edge cases:** customer replies "cancel" → free the slot + offer rebook; opt-out; duplicate reminders; timezone.
- **Won't build:** full loyalty/marketing automation, payment collection. (→ OS.)

## 5. Inbox & FAQ Responder — `faq-responder`
- **User:** anyone drowning in repetitive inbound email/form questions.
- **Problem:** the same questions (hours, pricing ranges, service area, lead times) eat the owner's day.
- **Input:** inbox/form access + the FAQ set + escalation rules.
- **Output:** instant accurate answers to common questions; real/edge ones escalated to the owner.
- **Core features:** watch inbox/form; answer from the FAQ knowledge; escalate by rule; approval option.
- **Edge cases:** complaint/legal → human; custom quote → capture + route; unknown question → escalate, never guess.
- **Won't build:** full helpdesk/ticketing, account-specific support needing internal-system access. (→ OS.)

## 6. Lead Intake & Booking — `lead-intake`
- **User:** business with steady inbound leads that slip through the cracks.
- **Problem:** leads arrive across channels and sit unworked; no consistent qualify-and-book.
- **Input:** lead source(s) + qualifying questions + where leads land (CRM) + the booked next step.
- **Output:** every lead greeted, qualified, captured to CRM, and booked to the next step; owner notified.
- **Core features:** multi-source intake; qualify by rules; write to CRM; book the next step; notify.
- **Edge cases:** unqualified lead → polite decline/route; duplicate → merge; high-value lead → flag for owner; missing info → ask.
- **Won't build:** custom pricing/estimating logic, deep CRM customization, full sales sequences. (→ Estimate assistant / OS.)

---
**Shared (every SKU):** yourco operates it (client never touches infra); the pre-built **eval set runs against the
client's config before go-live**; anything customer-facing is **approval-gated** until the earned-autonomy ladder
opens it (`decisions/2026-06-12_autonomy-ladder.md`); month-to-month, pause anytime. If a prospect needs anything in
a SKU's **Won't build** list, that's the signal to route them to the **Audit → custom OS** motion.
