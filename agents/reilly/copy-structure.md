# Outbound Copy Structure (v2: commission-breath-removal)

> **Owner: Michelle** (outbound copy/messaging) as of 2026-06-15 — split from Reilly. File kept at this path (referenced widely + in the decision log); ownership is Michelle's. **Reilly** loads the finished copy into Instantly (`instantly.py --create`) and runs the campaign.

The writing methodology for every cold outbound campaign. Reusable across verticals. Reed produces the demo video referenced in Email 2. Luka enforces brand voice over the whole thing.

**Decision log:** `/decisions/2026-06-08_reilly-copy-structure-v2.md`
**Supersedes:** v1 ICA framework (single-question-led, pain-mirror pattern) — retired 2026-06-08

> **Reusability note:** Once Reilly has run 3+ clean campaigns under v2, these patterns extract into `yourco-template` by Kemba as the canonical "Outbound Cold Sequence v2" primitive. Until then, this file is the source of truth.

---

## Philosophy

**Peer-to-peer, consultative, non-salesy outreach to land high-trust clients.**

Built around removing **commission breath** — the smell of self-interest that makes a prospect defensive. Radically honest. Prospects feel safe telling us the truth because they don't feel sold or manipulated.

This is the **Chet Holmes / Gap Selling / Sandler "negative reverse" school**. YourCo's executive-trust archetype maps cleanly onto it: high-trust buyers respond to peer consultation, not pitches.

### Core mechanics
1. **Poke the bear** — lead with a problem the prospect may not realize they have, never with a pitch.
2. **Problem-first framing** — name the operational reality before naming the solution.
3. **Very short, low-pressure** — every email earns its existence in fewer words than the last.
4. **Paint the Nirvana** — after the problems land, show what life looks like once they're gone. Operational outcomes AND financial outcomes.
5. **Pricing stays out of cold** — pricing converts the conversation from consultative to transactional. First call only.

### What we will not do (commission breath markers)
- Lead with what we do.
- Use the word "solutions."
- Quote pricing in cold sequence.
- Use "Just following up" — signals a script, breaks trust.
- Ask "did you see my last email?" — manipulative, low-status.
- Insert "Hope this finds you well."
- Use exclamation points in any cold touch.
- Ask for "30 minutes" twice in the same touch.
- Force a Calendly link as the visual focus of an email — link lives in the Founder's signature, not the body.

---

## Step 0 — read recent learnings

Before producing a campaign, read the most recent entries (last ~5, past 30 days) in `/learnings/sales-copy/` for patterns that apply, and apply what fits — a subject line that landed, an opener that fell flat, a Nirvana framing that converted. Note which entries you applied in the campaign's handoff. (An empty folder means nothing to apply yet — expected pre-launch.)

---

## The 6-touch sequence (3 emails + 3 SMS, 21 days)

| Touch | Day | Channel | Role | Job |
| --- | --- | --- | --- | --- |
| 1 | 1 | **Email 1** | **Poke the bear + Nirvana** | Name 2-3 problems the owner may not realize they have. Paint Nirvana — operational + financial outcomes |
| 2 | 3 | **SMS 1** | Bump | Short reference to Email 1 + Calendly link + STOP |
| 3 | 7 | **Email 2** | **Show, don't tell** | Reed-produced demo video (animated GIF preview → Loom). What an YourCo digital employee actually looks like for them |
| 4 | 10 | **SMS 2** | Bump | Short reference to the video + Calendly + STOP |
| 5 | 14 | **Email 3** | **Reframe + release** | Hit the problems once more (different angle), paint Nirvana once more (sharper outcomes), low-pressure release |
| 6 | 21 | **SMS 3** | Break-up | Final note + Calendly + STOP |

### Why this cadence
- **3 emails, not 5**: every additional cold email lowers reply rate and raises commission-breath risk. Three is enough to land the problem, prove it, and reframe.
- **3 SMS, not 0**: owner-operators are mobile-first. SMS is where they actually read. Each SMS does one job, references the prior email, links to Calendly.
- **21 days, not 14**: low-pressure means breathing room. The owner reads Email 1 Monday, gets the bump Wednesday, sees the video the next Monday, gets a second bump Thursday, gets the reframe Thursday after, and the break-up the following week. Feels like a peer following up — not a sales sequence.

### Pattern violations to flag in review
- Email opens with what YourCo does (anywhere before the problem lands)
- Pricing surfaces anywhere in the sequence
- Any touch reads as a pitch (test: read it aloud — does it sound like a friend giving a heads-up, or a vendor closing?)
- Email body emphasizes the Calendly link visually (link belongs in the Founder's signature, period)
- SMS over 160 chars (single-segment only)
- Email 2 ships without the Reed-produced video asset registered in `/agents/Reed/_asset_registry.md`

---

## Email 1 — Poke the bear + Nirvana

**Job:** name 2-3 problems the owner may not realize they're tolerating. Then paint Nirvana — what life looks like once those problems are gone. Operational AND financial outcomes.

### Anatomy

```
Subject line: a problem named directly, not a pitch.

{first_name},

[1. POKE THE BEAR — 2 or 3 SPECIFIC PROBLEMS]
Name problems the owner is tolerating because they've normalized them.
Not generic ("you're too busy") — specific to the vertical's operational
reality (for landscaping: missed inbound calls, estimates that take 3 days
to send, owner stuck on the phone instead of on-site).

3-5 sentences max. One problem per sentence is ideal.

[2. THE QUIET COST]
One sentence connecting the problems to the financial reality.
Not preachy. Not statistical. Just plain math the owner already does in
their head ("every missed call is a $4k–$15k job that went to the next
landscaper on the search results").

[3. NIRVANA — OPERATIONAL]
What the day looks like when those problems are gone.
2-3 sentences. Concrete and visual.
("Every call answered in under 30 seconds. Every estimate booked into
your calendar without you opening your phone. You're on-site, your phone
is in the truck.")

[4. NIRVANA — FINANCIAL]
What the math looks like when those problems are gone.
1-2 sentences. Plain numbers and ranges, never our pricing.
("Most owner-operators we work with claw back 10-15 hours a week and
close 20-30% more of the inbound that was already coming in.")

[4a. THE SPEED CLAIM — 48-HOUR GO-LIVE]
One sentence. Standing YourCo truth, claimable in every campaign because
it's verifiable.
("Live in 48 hours from signed agreement — your digital employee in your
tenant, doing the work.")
This belongs in the Nirvana cluster — it's an outcome (time-to-deploy),
not a pitch.

[5. LOW-PRESSURE RELEASE]
A short, non-pitch close. Never "let me know" or "looking forward to."
Examples that work:
  "If any of that lands, I'd be glad to walk through what it'd look like."
  "If this isn't the season for it, no worries — I'll stop after a few notes."
  "Reply with anything you want me to expand on."

NO direct Calendly text in body. Link lives in the Founder's signature.

[6. FOUNDER'S SIGNATURE — Calendly + website baked in]
— the Founder
yourco  ·  getteamyourco.com  ·  Book 30 min
```

### Subject line patterns

- A problem named (not a pitch): `the calls you're missing while on-site`
- A specific cost: `every missed estimate is the next landscaper's job`
- A peer-to-peer reference: `{first_name} — quick read, no pitch`
- A concrete operational moment: `your phone, on a Tuesday at 2pm`
- Provocation as observation: `what {company_name}'s intake actually looks like`

Lowercase. Under 50 chars. Run A/B with 2 variants for first campaign in a vertical.

### What's banned in Email 1
- Any sentence starting with "We" or "At yourco"
- Any feature claim (no "our AI agents can…")
- Any reference to what we do before problems land
- Any pricing
- "Hope this finds you well" / "Quick question" / "Just reaching out"
- More than 1 link in body (the Founder's signature is the only link surface)
- Calendar links visible in body
- Greeting word ("Hey" / "Hi" / "Hello") — open with just `{first_name},`

---

## Email 2 — Show, don't tell (Reed-produced video)

**Job:** prove the Nirvana from Email 1 is real by *showing* the owner what an YourCo digital employee looks like — as a clean animated workflow. The owner watches; we say very little. (Demo video produced by Reed in Higgsfield as of 2026-06-09 — animated/conceptual, see `/decisions/2026-06-09_Reed-higgsfield-animation-stack.md`.)

### Anatomy

```
Subject line: references the video, not the pitch.
Examples: "30-second look — your intake employee" / "saw this and thought of {company_name}"

{first_name},

[1. ONE-LINE CONTEXT]
Brief — reference to Email 1's problems OR a fresh acknowledgment of
the owner's reality. One sentence.

[2. THE VIDEO — animated GIF preview, embedded inline]
A looping 3-5 second GIF preview of Reed's full demo video. Play-button
overlay. Clicks through to Loom landing page with the full 60-90 sec demo.

The GIF lives directly in the email body. It autoplays silently in every
modern email client (Gmail / Outlook / Apple Mail / mobile). The full
video opens on click.

[3. ONE-LINE FRAME — what the prospect is looking at]
Plain language. ("This is what your intake employee would look like at
{company_name}. Sixty seconds. No software for your team to learn.")

[4. LOW-PRESSURE RELEASE]
("If after watching, it feels worth a conversation — I'd be glad to walk
through what your specific deployment would look like.")

NO direct Calendly text in body. Link lives in the Founder's signature.

[5. FOUNDER'S SIGNATURE]
— the Founder
yourco  ·  getteamyourco.com  ·  Book 30 min
```

### Reed handoff (Reilly → Reed)

When Reilly drafts a campaign that includes Email 2, she **files an asset request to Reed** before staging the campaign in Instantly.

Asset request format (saved at `/agents/Reed/requests/{date}_{vertical}_email2-demo.md`):
- **Requested by:** Reilly
- **Campaign:** `{campaign file path}`
- **Vertical:** e.g., landscaping/hardscaping
- **Use case shown:** lead intake + estimator coordinator (or vertical-specific equivalent)
- **Length target:** 60-90 seconds full video, 3-5 sec GIF preview
- **Tone:** quiet, demonstrative, no voiceover salesmanship — let the workflow speak
- **Distribution:** animated GIF preview embedded in cold email + full Loom landing page
- **Deadline:** campaign launch date – 5 business days

Reed owns: script → real-agent screen capture → assemble → register asset → deliver GIF + Loom link to Reilly. **No publish without the Founder's approval per Reed's existing gate.**

Once Reed delivers the GIF + Loom URL, Reilly drops both into the campaign artifact and stages the campaign.

---

## Email 3 — Reframe + release

**Job:** hit the same problems from Email 1 one more time at a different angle, sharpen the Nirvana with one or two new specific outcomes, then release the owner.

Should be shorter than Email 1. Even less pressure. The job of Email 3 is to make the owner feel respected if they ignore it AND tempted enough to reply if any of it has been simmering.

### Anatomy

```
Subject line: low-pressure, conversational.
Examples: "{first_name} — last note from me" / "this is the last one"

{first_name},

[1. REFRAME THE PROBLEM]
A different cut at the same operational reality from Email 1.
If Email 1 said "every missed call is a $4-15k job," Email 3 might say
"every estimate that takes 3 days to send is a competitor's job by day
two." Same problem, sharper angle.

2 sentences max.

[2. SHARPER NIRVANA]
A new specific outcome the owner hasn't heard yet.
Examples for landscaping:
  - "Your estimate goes out in 4 hours, not 4 days."
  - "Your reviews start showing up automatically because the employee
     asks for them after every completed job."
  - "Your crew shows up to a fully scheduled day, not a chaos morning."

2 sentences max.

[3. RELEASE]
The lowest-pressure close in the sequence. Genuinely lets them go.
("If this isn't a fit right now, totally fine — I'll stop after this
one. If it is, you know where to find me.")

[4. FOUNDER'S SIGNATURE]
— the Founder
yourco  ·  getteamyourco.com  ·  Book 30 min
```

---

## SMS structure (3 messages — short, peer-to-peer)

**Job:** reference the prior email, surface a Calendly link, prove a real human is following up. Single segment when possible (160 chars).

### Anatomy

```
[1. SENDER ID — first 4 words]
"Hi {first_name}, the Founder from yourco" or "{first_name} — the Founder, yourco"

[2. REFERENCE TO PRIOR EMAIL]
"Sent you a note Mon about the calls you're missing..."
"Sent you a short video Mon — 60 sec — showing what your intake
employee would look like..."

[3. CALENDLY LINK]
Inline. Short URL form: getteamyourco.com/book or the Calendly slug.
(10DLC submission must register the URL.)

[4. STOP OPT-OUT]
"Reply STOP to opt out." Mandatory every SMS.

[5. UNDER 160 CHARS]
Cut adverbs first, then qualifiers, then context line.
```

### The 3 SMS

**SMS 1 (Day 3)** — references Email 1's problems.
```
Hi {first_name}, the Founder from yourco. Sent a note Mon about the calls
{company_name} is missing during the day. Worth 30 min? getteamyourco.com/book
Reply STOP to opt out.
```

**SMS 2 (Day 10)** — references Email 2's video.
```
{first_name} — the Founder, yourco. Sent a 60-sec video Mon of what your intake
employee would look like at {company_name}. Worth a look?
getteamyourco.com/book — STOP to opt out.
```

**SMS 3 (Day 21)** — break-up.
```
Hi {first_name}, last from me at yourco. If any of it resonated,
getteamyourco.com/book. Otherwise no worries — done reaching out.
Reply STOP to opt out.
```

### SMS rules
- Lowercase `yourco` in sender ID always (brand wordmark rule)
- Sentence case in body — no ALL CAPS, no shouting
- One URL per SMS — same URL across the whole sequence, must be registered in 10DLC submission
- No emojis (clashes with voice; some carriers flag emojis on marketing)
- Time-of-day window: 9am–6pm in recipient's local timezone, Mon–Fri only
- Frequency cap: 1 SMS per recipient per week
- Suppression list immediately on STOP — Reilly's webhook handler updates `agents/reilly/_suppression.md` same-day
- State suppression list applied at batch time — per current campaign policy (FL, WA, OK, MD, NY, CA suppressed from SMS)

---

## Personalization variables

Every touch uses at least two of:
- `{first_name}` — owner first name; **drop the touch if missing**
- `{company_name}` — business name
- `{city}` — recipient's metro

Optional (when enrichment surfaces it):
- `{review_count}` — Google review count
- `{years_in_business}` — credibility anchor
- `{specific_service}` — e.g., "hardscaping" vs "residential lawn" if source distinguishes
- `{recent_review_quote}` — if a recent review mentions a workflow problem (rare, high impact)

If a touch can't be personalized with at least `{first_name}`, drop the touch for that recipient. No "Hi there" mass-blast feel.

---

## Pricing rule (hard line)

**Pricing does not appear anywhere in the cold sequence — not in Email 1, 2, 3, the video, or any SMS.** Pricing surfaces only on the first call after Calendly booking.

Rationale: commission-breath philosophy depends on the prospect controlling when pricing enters the conversation. Volunteering price in cold copy reads as "we want to close you" — exactly the smell we're removing.

If a prospect replies asking for pricing before booking, Reilly's reply template is:
```
Glad to walk through it on a 30-min call — there are 2 variables (which
agent + how many) that change the math, so a quick conversation gets you
the right number faster than I can type it. getteamyourco.com/book
```

---

## CTA structure

**Email body: zero standalone Calendly or website links.** Both live in the Founder's email signature: `yourco · getteamyourco.com · Book 30 min` (resolves to `calendly.com/the Founder-yourco/30min` via Webb's /book redirect).

This is intentional. The commission-breath philosophy depends on the email feeling like a peer-to-peer note. Naked Calendly links in the body convert the email into a vendor pitch. The signature handles the CTA without the body having to.

**SMS body: one Calendly URL.** Required because SMS doesn't have signatures, and the value of the SMS is the easy mobile tap.

## Signature spec — cold vs reply (locked 2026-06-08)

Reilly uses **two signature templates** depending on whether the message is cold outbound or a reply to a prospect.

### Cold outbound (every Email 1, 2, 3 in the sequence)

Functional and clear. NO wax-seal lines. The prospect doesn't have permission to read clever yet.

```
— the Founder
yourco  ·  getteamyourco.com  ·  Book 30 min
```

### Reply (after a prospect has engaged — replied, opened the Calendly link, or otherwise signaled interest)

Once the prospect has earned the wax seal, the signature line appears as the final line below the contact info. Same functional CTA, plus the brand mark.

```
— the Founder
yourco  ·  getteamyourco.com  ·  Book 30 min

We learn your business. AI does the work.
```

The tagline sits on its own line below the contact info: **We learn your business. AI does the work.** Sentence case; brass final period (brass `#B8965A` when HTML formatting permits; otherwise plain period). No bold, no italics. (Replaces the retired "a learning, I employ." signature line — decision: `/decisions/2026-06-10_brand-tagline.md`.)

### Why the split
- **Cold:** the prospect is in commission-breath-defense mode. Anything clever reads as a sales tactic. Stay functional.
- **Reply:** the prospect has spent attention on YourCo. The signature line is the small craft reward for that attention. It's how the brand signs off the conversation, like a craftsman's mark on the back of the piece.

Same logic applies to the Founder's personal one-to-one outreach (not Reilly's cold campaigns) — wax seal allowed because the relationship is established.

---

## Brand voice (enforced by Luka on every campaign)

- Lowercase `yourco` everywhere — wordmark rule
- Concise, direct, minimal formatting
- Outcomes framing, never features framing
- Never sell tooling; sell the moat (reliability/eval/observability/exec-trust) — but show, don't claim
- No buzzword salad: forbidden list = leverage, synergy, harness, unlock, revolutionize, transform, 10x, supercharge, cutting-edge, game-changer, "solutions"
- No hype emoji (🚀💯🔥) anywhere
- Real examples > abstract claims (every email/SMS should reference something concrete in the owner's reality)
- Confidence through demonstration, not declaration
- **New (v2):** peer-to-peer tone is the baseline. Read every line aloud — if it sounds like a vendor pitching, rewrite it. If it sounds like a friend giving a heads-up, ship it.

Luka reviews every campaign for brand compliance before it goes to the Founder. Voice fixes flagged in Luka's review block must be applied before the Founder's approval gate.

---

## How a campaign moves through the pipeline

1. **Polo confirms vertical pricing is locked** — Reilly cannot campaign into an unlocked vertical
2. **Reilly drafts** the 6-touch sequence using v2 methodology
3. **Reilly requests video asset from Reed** for Email 2 — async; campaign can proceed in parallel
4. **Luka reviews** — voice compliance; flags fixes inline
5. **Reilly applies fixes** — re-files the campaign artifact
6. **Reed delivers** the GIF + Loom URL; Reilly drops both into Email 2
7. **the Founder approves** — campaign-level approval
8. **Reilly stages in Instantly** — paused, awaiting prospect batch + 10DLC + warmup gates
9. **Reilly sources** — multi-source dedup-merge produces prospect list
10. **the Founder approves the batch** — separate gate per Reilly's `02_build.md`
11. **State suppression applied** (FL, WA, OK, MD, NY, CA from SMS)
12. **Reilly launches** — only after all gates clear: campaign approval + batch approval + Reed asset registered + 10DLC brand+campaign approved + warmup complete
13. **Webhooks come back** — replies, opt-outs, bounces feed Reilly's update loop
14. **Reilly updates `_pipeline.md`** — promotes prospects through stages; updates suppression list

---

## v1 → v2 migration note

The previous copy-structure.md used the ICA framework (Identify → Confirm → Action), a single-question-led pattern with pain-mirror copy and pricing transparency in Touch 3. That methodology is retired.

Why the shift: ICA is a *good* cold-email framework, but it's a "transactional outbound" framework — built for SDR-led volume motion. YourCo is selling executive trust to high-trust SMB owners who are exactly the audience that finds transactional outbound off-putting. Commission-breath-removal aligns the cold sequence to the same moat we sell: peer consultation, radical honesty, prospect controls the pace.

All future campaigns use v2 unless the Founder explicitly logs a deviation in the campaign artifact.

— Reilly, Sales
