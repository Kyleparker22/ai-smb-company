# PM Growth OS — module spec

**Status:** v1 BUILT as spec'd, 2026-08-17 (same day as the spec — the substrate
made it a one-session build, as §Build shape predicted). Implementation:
`pipeline.py` (domain + the scout and scribe agents) · `app/growth.html` (the
cockpit, `/growth`) · pinned by the `6e` domain section and the `9d3` journey
section. Deviations from this spec, all narrowing: the pipeline-read is stage
facts + cadence nags (no velocity/counterfactual analytics yet — CRM-insight
ports are v1.1); pitch-open counting was NOT built (the open privacy decision
below stands, defaulted to "no instrumentation"); cadences live as constants in
`pipeline.py`, not config. The counsel gates below are unchanged and still
block any real prospect.
**What it is:** the Sales-pillar module for a property manager — the system that
turns Property OS's recorded demand (referrals, inquiries, the pitch page) and
its operating evidence into **more doors under management**. Sold as the
expansion inside an account that already runs Property OS, per
`decisions/2026-08-10_lead-high-land-anywhere.md`: the ops module lands, the
growth module is the upsell that was mapped from day one.

**What it is not:** a feature of Property OS. The two share a substrate — the
autonomy matrix, the append-only event log, the approvals queue, the sentinel,
the honest-numbers rules — and nothing else. Merging a CRM into an ops console
is how software becomes broad and mediocre; the moat here is depth of
reliability, and the module boundary is what protects the ops product's trust
story ("it never freelances with your residents") from the outreach product's
compliance regime (TCPA / CAN-SPAM / DNC).

---

## The one-sentence thesis

*(Revised 2026-08-17 — the Founder: the module is NOT referral-only.)* A property
manager's growth engine is **evidence + every channel worked consistently** —
referrals, inbound, and sourced cold prospects alike. The OS manufactures the
evidence (the pitch page), records the demand (referrals, inquiries), and
imports sourced target lists with their provenance; the module's job is the
part humans reliably drop: working every lead to a decision, on time, with the
proof attached, while a human makes every touch. Cold outreach is volume-
disciplined by construction (provenance required, opt-outs permanent, three
touches then rest), because the pitch page's credibility is the asset and
spray-and-pray is how you spend it.

## Who uses it

The PM principal (the P&L owner) and whoever owns door growth — usually the
same person at 20–300 units. Not a sales team. The design target is "the owner
of the firm spends 30 minutes a week deciding, and nothing leaks."

**Intended first deployment (the Founder, 2026-08-17): Sample Realty** — Kimi's firm
is 100%-referral-based, which is precisely the motion this module works. Still
PROSPECT stage (`clients/sample-realty/_README.md`), so this stays product IP
until the engagement signs; sequencing is forced by the evidence rule anyway —
her ops history must accrue in Property OS before the pitch page and the
drafts have real numbers to cite. Ray's counsel gates (live PM data; CAN-SPAM;
NC proposal terms) precede any real prospect.

---

## Scope

### In (v1)

1. **Owner-prospect pipeline** — one row per prospective owner:
   `recorded → researched → first_touch_drafted → contacted → meeting →
   proposal → won/lost`, with the same honest instrumentation the CRM insight
   layer proved out: stage age, who moved it last, and a "the only party
   moving this is us" read. Sources: Property OS referrals (auto-imported),
   pitch-page opens (count only — see privacy line), manual adds.
2. **Evidence-led outreach drafting (R1)** — for each prospect, a drafted
   first touch built from the referrer's note + the pitch page + the specific
   owner-pain the referrer named. A human sends every one, from their own
   mailbox. The module never sends.
3. **Follow-up discipline (R2 for the reminder, R1 for the message)** — the
   thing that actually wins: nothing sits. The module nags the HUMAN on a
   cadence; drafted follow-ups queue behind their approval.
4. **Referral loop management** — thank-you drafts to referrers (R1), status
   updates back to the referring owner ("your introduction became a client"),
   and referral-source arithmetic: which owners' introductions convert,
   counted, never guessed.
5. **Proposal assembly (R0)** — a draft management proposal from a template +
   the prospect's stated portfolio + the pitch-page numbers. Drafted for the
   principal; pricing is the principal's, always.
6. **Won → onboarding handoff** — a won prospect becomes a Property OS
   owner + properties + units scaffold, so the sale flows into the ops module
   without re-keying.

### In (v1.5, 2026-08-17 — prospecting; supersedes the v1 "warm-first" line)

the Founder's call: the module brings in NET-NEW clients, not just referrals. Built
same-day:

7. **Sourced target import** (`import_targets`, R2) — bulk intake of county
   pulls / prospecting exports / meetup sheets. **Provenance is mandatory**
   (we don't contact people we can't say how we found), rows are deduped, and
   two kinds are skipped-and-reported rather than added: opt-outs, and
   previously-LOST prospects (re-approaching a lost prospect is a deliberate
   human decision, never a list side-effect). yourco's own prospecting stack
   (e.g. a Vibe export) can feed this as a file — the module never buys data
   itself.
8. **Cold first-touch drafting** (R1) — its own template: recorded provenance
   surfaced for the human's review, the evidence block, an explicit opt-out
   line, and the physical-address bracket commercial email requires. Same
   numbers rule as every draft.
9. **The do-not-contact ledger** (`record_do_not_contact`, R3) — permanent;
   every import and every draft refuses an opted-out contact by construction;
   `wake` refuses them too.
10. **The touch cap** (`rest_prospect`, R2) — after 3 SENT touches with no
    reply the cadence stops and the prospect rests; only a deliberate human
    action revives it. Silence is an answer.

### Out (still, explicitly)

- **Any automated sending** — email, SMS, or voice. Every outbound message
  is human-sent. The send rail (and its TCPA/CAN-SPAM/DNC machinery) is a
  v2 decision behind counsel — cold outreach makes this gate MORE binding,
  not less.
- **Buying prospecting data inside the module.** Sourcing happens outside
  (with its own consent posture per source); the module imports the result
  with provenance attached.
- **Leasing-side marketing** (listing syndication, ad spend). Commodity
  surface, different buyer problem.
- **Anything that touches residents or applicants.** Growth is owner-side
  only. The applicant no-screening line lives in Property OS and this module
  never gets near it.

---

## The autonomy matrix (draft)

Same grammar as Property OS `core.AUTONOMY`; the send boundary is the moat.

| action                    | rung | why it sits there |
|---------------------------|------|-------------------|
| import_referral           | R3   | already recorded in Property OS; mirroring it is bookkeeping |
| research_prospect         | R2   | assembling public facts into a brief; wrong facts cost an edit |
| draft_first_touch         | R1   | first contact is a relationship moment and a consent question — forever |
| draft_follow_up           | R1   | same exposure as the first touch |
| nag_human_on_cadence      | R2   | reminding the principal costs nothing and is the whole discipline |
| advance_stage             | R2   | reversible bookkeeping, notified |
| draft_proposal            | R0   | a price + terms commitment — principal only, like capital_recommendation |
| send_anything             | R0*  | *does not exist in v1. No send rail is built. Adding one is a counsel-gated v2 decision, not a config flag |
| update_referrer           | R1   | telling an owner what became of their introduction — human sends |
| scaffold_won_client       | R2   | creating the ops-module records for a signed client; reversible |
| import_target_list        | R2   | widens who we may contact — provenance recorded, deduped, opt-outs honored |
| record_do_not_contact     | R3   | honoring an opt-out is always the safe direction; permanent |
| rest_prospect             | R2   | 3 touches + silence = stop; persistence past silence is spam |

Calibration-gated promotion applies as everywhere else
(`decisions/2026-08-13_agent-substrate-upgrade.md`): a rung moves on streak +
calibration evidence, and `draft_first_touch` / `draft_proposal` never move.

## Agents (two, not five)

- **scout** — imports referrals, assembles prospect briefs, computes pipeline
  reads, runs the cadence nag. All R2/R3.
- **scribe** — drafts (first touch, follow-ups, referrer updates, proposals).
  All R0/R1. Screened by the same sentinel pattern; the screen list gains an
  outreach section (no fabricated claims, no competitor disparagement, no
  performance promises the pitch page can't back — every number in a draft
  must trace to a pitch-page figure or be flagged).

## Data model

`prospects` (id, name, contact, source{referral_id | manual | pitch_open},
portfolio_notes, stage, stage_history[], briefs[], drafts[]) ·
`cadences` (prospect_id, next_touch_due, missed_count) ·
plus read-only views over Property OS's `referrals` and the pitch metrics.
Same JSON-store + `store_lock()` substrate; separate data root per client.

## Honest-numbers rules carried over

- Conversion rates refuse below n=10 outcomes ("3 of 4 won" is an anecdote,
  labelled as one).
- Pipeline value is never projected — no weighted forecasts; a stage is a
  fact, a forecast is a model, and v1 ships no model.
- "Pitch page opened" is a count with no identity attached — no tracking
  pixels beyond the server's own access log, no per-viewer analytics. The
  page's credibility partly rests on it not being surveillance.
- Every draft that cites a number must cite a computable one (the scribe
  refuses to draft "we resolve emergencies in 4 hours" if the pitch page says
  `_missing`).

## Counsel gates (before any real prospect)

1. Outreach compliance posture — even human-sent, drafted-by-software email
   at business scale wants a CAN-SPAM review; any future SMS is TCPA.
2. The referral-incentive question — if the PM ever pays owners for
   referrals, that's a separate review (echoes yourco's own item 4c; do not
   inherit yourco's connector mechanics here without it).
3. Proposal template review — management-agreement terms are state-specific.

## Open decisions

- **Where it runs:** same server as Property OS behind a `growth` role, or its
  own port/process. Lean: same store, separate surface — but decide at build.
- **The pitch-open signal:** even a bare count nudges toward "who viewed it?"
  Decide the privacy line before building any instrumentation.
- **Cold sourcing (v2):** whether the module ever gets a prospecting data
  source, and under what consent posture. Default no until a client asks and
  counsel clears.

## Build shape

Same discipline as the first three waves: domain module (`pipeline.py`) +
two agents + surfaces on the existing console pattern + both suites extended.
Estimate: one focused session for v1 as spec'd, because the substrate —
storage, autonomy, approvals, sentinel, testing harness — is already built and
proven. The expensive part is not the code; it's the counsel gates above, and
they are people-work, not sessions.
