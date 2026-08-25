# Michelle — Stage 3: Eval / gates / watchdogs

## What "good" is
**Positive-reply rate** is the metric Michelle is judged on — not opens, not sends. A reply that moves toward a booked call is the signal the copy did its job: it was relevant and honest enough that a high-trust owner chose to answer. Everything below is in service of that, inside the hard constraints (brand, claims, no-pitch, no-pricing, deliverability). The constraints are not negotiable against reply rate — a high-reply email that pitched, fabricated, or quoted a price is a hard fail, not a win.

## Eval set (v0)
Run on every sequence before it routes to the gate, and re-scored against real reply data once a campaign sends.

### 1. Brand-voice adherence
- **Test:** every touch passes `brand/writing-rules.md` — em-dash cap (≤1/paragraph), no slop list (no "leverage / transform / seamless / supercharge / solutions," no "moreover/furthermore," no rule-of-three filler), no "**Bold word:** explanation" bullets, no neat-bow closer, and it survives the read-aloud test (sounds like a person talking to one person).
- **Target:** clears Luka with zero voice fixes outstanding.
- **Measurement:** Michelle's self-check, then Luka's review block. Any flagged fix applied before Polo.

### 2. No-pitch / no-fabrication
- **Test (no-pitch):** the sequence leads with the prospect's problem and a working demo of *their* business, never with what YourCo does or a feature claim. Read aloud — does it sound like a peer giving a heads-up, or a vendor closing? Email 1 / Touch 1 never opens with "We" or "At yourco."
- **Test (no-fabrication):** zero invented metrics, clients, testimonials, or implied track record. Pre-revenue, proof is qualitative + the "we run yourco on its own agents" story + the verifiable 48h go-live. Any number is the owner's own plain math (their job value × their missed calls), never an YourCo result. Stats follow `learnings/content/2026-06-11_external-stats-need-sourcing.md` — sourced or cut.
- **Target:** 100%. A single fabricated proof point is a hard fail.
- **Measurement:** self-check + Luka (pitch tone) + Polo (claims truth).

### 3. Claims / pricing compliance
- **Test:** no pricing anywhere in the cold sequence — not Email 1, 2, 3, the video, or any SMS. Every claim is true and within Polo's locked bounds for the vertical. Inbound price questions are deflected with the first-call template, never answered in copy.
- **Target:** 100% — a single price in cold copy is a hard fail (breaks commission-breath philosophy + Polo's gate).
- **Measurement:** Polo's claims/pricing review block.

### 4. Clarity / microcopy (Shleyner)
- **Test:** every line earns the next; the subject gets the first line read, the first line gets the second read. Subjects lowercase, under ~50 chars, a problem/moment not a pitch. Adverbs, qualifiers, and throat-clearing cut. SMS (when used) single-segment (≤160 chars) with STOP.
- **Target:** no dead lines; a stranger can restate each touch's one job in a sentence.
- **Measurement:** self-check against the read-aloud + "one job per touch" test; Luka spot-check.

### 5. Deliverability-safe
- **Test:** no spam-trigger patterns (ALL-CAPS, multiple links in body, money-claim language, exclamation points in cold touches) that would undercut Reilly's sending reputation. One link surface (the Founder's signature for email; one URL for SMS).
- **Target:** clean — no copy-side deliverability risk introduced.
- **Measurement:** Reilly flags at staging; recorded against the campaign.

### 6. Positive-reply rate (the outcome metric — scored post-send)
- **Test:** positive replies and reply quality (booked calls) per sequence/vertical/subject, from Reilly's reply data.
- **Target:** set a baseline on the first live vertical, then beat it run-over-run (pre-launch there is no number — expected).
- **Measurement:** Reilly's reply/bounce feed → recorded in the campaign artifact → distilled into a `learnings/sales-copy/` entry.

## Hard gates (before any copy is sent)
These gates implement Michelle's place on the **Autonomy Matrix** (`processes/autonomy-matrix.md`; per-action rungs in `02_build.md` §Autonomy): her internal writing is autonomous (R3), but **she never sends** — the message stays at the R1 floor, gated by the Luka → Polo → the Founder chain, and the *copy* only earns higher downstream autonomy as Kolby's positive-reply eval evidence accrues.

In order. Each clears before the next. Michelle never sends.

1. **Michelle self-check** — eval items 1–5 above pass before the draft leaves her hands.
2. **Luka (brand voice)** — `brand/writing-rules.md` + voice/tone compliance; flags fixes inline; must clear.
3. **Polo (claims / pricing)** — no pricing in cold; every claim true + within locked bounds; must clear.
4. **the Founder (final approval)** — campaign-level approval.
5. **Reilly stages it paused** in Instantly — then the **launch gate** (separate, Reilly's): OtherVenture cleared + Rafi's CAN-SPAM/TCPA/FTSA + domain warmup + the Founder's batch approval + (for Email-2/Touch-1) the Reed demo asset registered. Email-first; no cold SMS until Rafi clears it.

All gate decisions logged with a one-line audit trail in the campaign artifact.

## Red-team / failure modes
- **Fabricated proof.** Copy implies a client roster, a testimonial, or a result YourCo hasn't produced. → Caught by eval #2 + Polo. The pre-revenue honest substitutes: qualitative outcomes, the "we run yourco on its own agents" story, the verifiable 48h go-live.
- **Unlocked or leaked pricing.** A number appears in cold copy, or copy is written into a vertical Polo hasn't priced. → Caught by Step 1 (locked-pricing check) + eval #3 + Polo's gate. The reply-to-pricing-ask template handles inbound questions.
- **Commission breath / pitch creep.** Under pressure for replies, copy drifts to "we leverage AI to transform…," opens with "We," or hard-asks for 30 minutes twice. → Caught by the read-aloud no-pitch test + Luka.
- **Spammy tone / deliverability damage.** ALL-CAPS, exclamation points, multiple body links, money-claim language. → Caught by eval #5 + Reilly at staging.
- **Slop tells.** Em-dash overuse, "moreover/furthermore," rule-of-three filler, "Bold word:" bullets, a neat bow. → Caught by eval #1 + Luka.
- **Demo-less touch.** Copy points at a `{{demo_url}}` or video that doesn't exist. → Caught by Step 1 (demo real-or-in-flight) + Reilly's pre-send checklist (no demo, no send).

## Pre-go-live checklist
- [x] Eval set defined (this file)
- [x] Methodology + proof-led copy exist and are owned by Michelle
- [x] Gate order documented (self-check → Luka → Polo → the Founder → Reilly stages paused)
- [ ] First net-new sequence *as Michelle* scored against eval #1–5 and cleared through the gate
- [ ] Baseline positive-reply rate captured on the first live vertical (post-launch)
- [ ] First `learnings/sales-copy/` entry written from real reply data

## Iteration plan
- After each campaign's reply data: write a `learnings/sales-copy/` entry (what subject/opener/Nirvana landed or fell flat); it becomes Step 0 input for the next vertical.
- Maintain a per-vertical subject + angle bank with reply-rate attached, so the next vertical starts from tested patterns.
- Re-score the eval bar as data accrues: once a vertical has a baseline, the target shifts from "clears the gate" to "beats the prior reply rate."
- Extract the v2 patterns + angle bank into `yourco-template` (Kemba) once Reilly has run 3+ clean campaigns.
