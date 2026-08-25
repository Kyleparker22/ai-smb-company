# YourCo employee patterns — the library of reusable "employee shapes"

> **Owner: Kemba** (extracts + maintains the patterns) + **Kimi** (delivers them). The menu of digital-employee use cases yourco builds. Each is a *starting blueprint* — tailored per client, overlaid on `yourco-template` (client logic is overlay only). Reilly + Sadie target prospects for these; Pickle frames them in collateral; Polo prices them per vertical. Add a new pattern whenever a real engagement produces a reusable one (+ a `/learnings/delivery/` entry).
>
> **New candidate offering lines (2026-06-16, internal-only):** see `processes/new-offering-lines.md` — single-job *Employees* (diligence copilot, legal-exhibit prep, win/loss intelligence, knowledge-capture) and multi-agent *AI OS* lines (Company OS for acquisitions, GEO/AEO DFY, interior-design ops, staffing/delivery OS) productized at the spec level. Not on the public site (the Founder's call); built per-engagement when sold.
>
> **Tiers:** the patterns below are **Tier 1 ("handle it")**. The up-market **Tier 2 ("produce it")** production employees live in `employee-patterns-tier2.md`; the tier model + the agent-vs-AI-service line are in `processes/employee-tiers.md`.

## The patterns
1. **Intake / front desk** *(the landscaping flagship)* — answers inbound calls/texts, qualifies, books the estimate, confirms, logs.
   - Stack: Vapi + Twilio + Calendar + ElevenLabs + a CRM/Sheet log · Best for: service businesses that miss calls/leads · Discovery focus: call volume, qualification fields, calendar, phone routing.
2. **Automated lead generation** — sources prospects, qualifies on the client's criteria, drafts personalized outreach (human-approved before send).
   - Stack: prospecting source (Vibe) + research + outreach drafting + CRM + suppression · Best for: any business with a sales team and no automated pipeline · Discovery focus: ICP, qualification criteria, channels, **the approval gate + outreach legality (CAN-SPAM/TCPA — Rafi)**.
3. **Internal knowledge base** — indexes the company's docs and answers employee questions in plain language with citations, instead of digging through folders.
   - Stack: doc ingestion + retrieval + a chat/Slack surface · Best for: 50+ employee companies losing hours to "where's that doc" · Discovery focus: where the docs live, access, the top recurring questions, sensitive content.
4. **Customer support automation** — handles 70–80% of routine tickets and escalates the rest to a human; nothing customer-facing sends without the client's approval rules.
   - Stack: ticketing/inbox integration + a support agent + escalation rules + the approval gate · Best for: e-commerce / high-volume support · Discovery focus: ticket categories, the knowledge source, escalation rules, tone, what must never auto-send.
5. **Data analysis / reporting pipeline** — pulls from multiple sources, cleans, analyzes, and generates the recurring report or dashboard.
   - Stack: source connectors + transformation + a dashboard/report surface · Best for: businesses sitting on data nobody has time to use · Discovery focus: the sources, the questions that matter, the report cadence + format.
6. **Competitor monitoring** — watches competitor sites, pricing, social, and launches on a schedule → a structured "what changed" report.
   - Stack: scheduled web monitoring + diffing + report drafting · Best for: marketing teams / founders · Discovery focus: the competitor set, what to watch, the cadence, the report format. *(Respect scraping ToS — Rafi.)*

## The broader library — 20 more shapes
The next highest-demand digital employees, by function. Each tailors per vertical and overlays `yourco-template`; the yourco difference vs a generic automation is always the *named employee + the reliability/eval/approval layer.*

**Sales & revenue**
7. **Appointment setter** — books, confirms, and reschedules meetings; reminders to cut no-shows.
8. **Inbound lead responder** — replies to web-form / chat / inbound leads in seconds, qualifies, routes or books.
9. **Proposal & quote drafter** — turns a call or brief into a ready-to-review proposal or quote.
10. **Follow-up rep** — sequences follow-ups on leads and quotes that went quiet (staged for approval).
11. **CRM hygiene rep** — logs calls/emails, updates records, dedupes — keeps the pipeline clean.
12. **Renewal & upsell rep** — flags upcoming renewals and drafts the expansion offer.

**Customer & service**
13. **Order / job status updater** — answers "where's my order/job?" and pushes proactive status updates.
14. **Review & reputation manager** — requests reviews after a job, monitors them, drafts responses.
15. **Onboarding concierge** — walks new customers from welcome → setup → first value.
16. **Dispatch coordinator** — schedules jobs, routes crews, notifies customers (field service).
17. **Returns / RMA handler** — processes returns and exchanges end-to-end (e-commerce).

**Back office & finance**
18. **Invoicing & AR chaser** — sends invoices and chases overdue, tone-matched (drafts; client approves sends).
19. **Bookkeeping categorizer** — categorizes transactions and flags anomalies for the books.
20. **Document & form processor** — extracts data from invoices/forms/contracts and files it.
21. **Deadline & compliance tracker** — tracks licenses, renewals, and filing deadlines; reminds before they lapse.

**Marketing & content**
22. **Social media manager** — drafts, schedules, and engages across the client's channels.
23. **Content repurposer** — turns one asset (a call, a post) into clips, posts, and an email.
24. **Newsletter writer** — drafts the recurring newsletter from the business's own updates.
25. **SEO content writer** — drafts search-optimized articles on a cadence.

**People & recruiting**
26. **Recruiting screener** — posts roles, screens applicants, schedules interviews.

> 26 shapes total. Lead each *sale* with one (per vertical), prove it, then expand — but the *catalog* shows a prospect the full range so they recognize their own pain. Industry-specific framings (medical intake, real-estate showing coordinator, legal intake, property management…) are tailorings of these shapes, not separate patterns.

## How to use this
- **Sell one well first** (per vertical), build the skill/pattern library from real work, then expand to adjacent verticals — our discipline and the AI-agency playbook agree on this.
- Every pattern overlays on `yourco-template`; the yourco difference vs a generic "automation" is the named employee + the reliability/eval/approval layer underneath each one.
- New reusable patterns from real engagements → add a row here (Kemba) + a `/learnings/delivery/` entry.

> Origin: patterns 2–6 adapted from the "AI agency" service menu (2026-06-11), mapped onto yourco's named-employee + reliability/approval model — the moat that separates us from a generic agency running the same patterns.
