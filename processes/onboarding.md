# Onboarding Runbook (Hour 0) — signed deal → delivery start

**Owner:** **Janice** (`agents/janice/` — built 2026-06-11; the Founder holds until the first engagement hardens it). The seam between a signed agreement and Kimi's 48-hour build. Generalized for **any vertical and any employee type**. Hands off to Kimi (`processes/discovery-to-48h-build.md`) at the discovery call.

**Trigger:** signed agreement received.

## Lineage — who Janice mirrors
Janice's onboarding discipline mirrors **Lincoln Murphy (customer success / "the customer's Desired Outcome")**:
- **Onboard toward the customer's Desired Outcome**, not a feature checklist — the goal is the required outcome, experienced the right way.
- **Time-to-first-value is everything** — the faster a new client feels the win, the stickier the engagement; the 48-hour go-live is that principle made literal.
- **Set expectations, reduce friction** — clear next steps, the access needed, who owns what; a smooth start predicts a healthy engagement.

**YourCo fit:** YourCo sells an outcome live in 48 hours. Janice makes Hour 0 → discovery → handoff frictionless so Kimi can deliver that promise. Tenant access = the Founder must-approve.

## The Hour-0 sequence
1. **Spin up the engagement folder.** `cp -r clients/_yourco-template clients/<client>` and fill the `_README.md` engagement summary (client, vertical, the named employee(s), signed date, +48h target). For a **multi-employee** deal: one folder, an entry per employee — Kimi builds them sequenced.
2. **Send the pre-call intake** — a short, **type-agnostic** form so the discovery call starts from facts (works for voice, email-intake, scheduling, drafting, Q&A, data/ops):
   - **What's the most repetitive thing your team does that feels like it shouldn't require a human?** (their answer is usually the first job)
   - What kicks it off — an inbound call, an email/web-form, a calendar time, a record changing?
   - What does the employee need to know or have access to in order to do the job?
   - What should it produce or do — and what must a human approve before it goes out?
3. **Book the discovery call** (30–45 min) within 24h of signing — via Calendly/Calendar.
4. **Provision the named employee identity** — pick the name (per the roster's human-name convention) + set up `<employee>@<client-domain>` or an yourco-tenant alias. *Tenant access = the Founder must-approve.*
5. **Pricing + cost** — record the agreed build fee + retainer in `clients/<client>/cost.md`; confirm the vertical pricing ref.
6. **Brief the client** — what to expect over the next 48 hours, who their point of contact is, the go-live target date.
7. **Hand off to Kimi** — at the discovery call, delivery takes over (`processes/discovery-to-48h-build.md`, Hour 0–4 onward).

## The "go-ready" gate — when the 48h clock starts
The 48h promise is **48 hours from go-ready**, not from e-signature. **Go-ready = signed + deposit authorized + the client has granted everything the employee needs.** Confirm and check off the client-side prerequisites *before* starting the clock — a delay here pauses it (fair to both sides; this is the honest condition behind the live "48h" promise):
- [ ] Access granted to the tools the employee works inside (phone line / inbox / calendar / CRM — per discovery)
- [ ] Email/identity routing ready (`employee@client-domain` mailbox or alias + any DNS/forwarding)
- [ ] Phone path ready (number forwarded/ported, if voice)
- [ ] Discovery inputs delivered (the facts the build needs)
> The clock starts the moment all of the above are true. Janice confirms "go-ready" and logs the timestamp — *that* is Hour 0, not the signature.

## Hard gates
- [ ] Engagement folder created from `_yourco-template`
- [ ] Discovery call booked ≤ 24h from signing
- [ ] Employee identity provisioned (**tenant access the Founder-approved**)
- [ ] Pricing + cost recorded
- [ ] Client briefed on the 48h timeline (and on what "go-ready" needs from them)

## What the Founder approves
- Any access to the client's tenant / domain / number.
- The named employee identity going live in the client's environment.

> Janice onboards + provisions; **Kimi** builds + delivers. The signed-deal handoff is this runbook → the build playbook. Both agents are built (2026-06-11, generalized); the Founder holds both until the first real engagement hardens them.
