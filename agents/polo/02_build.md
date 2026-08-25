# Polo — Stage 2: Build

## Inbox — routed requests
*Backlog items filed to Polo by name. Clear when done; fold the outcome into `/pricing/` + a CHANGELOG entry.*

- **[2026-07-20] Godfather-Offer test on the Audit** (routed by the Founder, from the *Sell Like Crazy* triage — `decisions/2026-07-05_tool-triage.md` §2026-07-20). Suby's "make the first yes almost stupid to refuse" applied to yourco's front door. **Do:** pressure-test whether the paid **Audit** offer is genuinely irresistible and maximally risk-reversed. Concrete levers to price/decide: (a) **credit the Audit fee toward the build** if they proceed (removes the "wasted spend" objection); (b) a scoped outcome/results assurance that composes with the existing `decisions/2026-06-12_48h-guarantee.md` without over-promising pre-proof; (c) confirm the Audit price sits at the "trivial to say yes, still signals seriousness" point. Output: a recommendation to the Founder (Polo proposes, the Founder locks) — do **not** adopt Suby's discount/urgency/scarcity tactics; they clash with the premium/trust brand. Note the beachhead reality: the binding constraint is the first *close*, so this is the highest-leverage of the two sharpens.

## Build approach
Polo v0 ships as **the pricing system structure plus the research-and-decision pattern.** When the Founder or Reilly requests a vertical pricing build, Polo executes a defined research → propose → approve → lock workflow.

## Components

### 1. Pricing system structure
- `/pricing/README.md` — how pricing works at YourCo
- `/pricing/v0/<vertical>.md` — canonical pricing per vertical
- `/pricing/CHANGELOG.md` — every change with reason + approval reference
- Three-layer structure (onboarding + per-agent setup + bundled MRR with marginal pricing) is the universal frame; only dollar amounts vary by vertical

### 2. The vertical pricing build workflow
When triggered (by the Founder or as Reilly's pre-campaign gate):
1. **Research** the vertical via WebSearch: typical revenue per business, software stack, owner pain points, comparable services pricing (VAs, agencies, software), industry-specific pressures (seasonality, regulation, cycle length)
2. **Draft** a pricing proposal as a decision doc at `/decisions/YYYY-MM-DD_pricing-<vertical>.md` — short, opinionated, ≤ 2 pages
3. **Surface** to the Founder for review via Slack post + decision doc reference
4. On the Founder's **explicit approval**, write the canonical reference at `/pricing/v0/<vertical>.md` and log in `CHANGELOG.md`
5. **Signal Reilly** that the vertical is now unlocked for campaigning

### 3. Quarterly review pattern
Scheduled task `yourco-polo-quarterly-pricing-review` runs first Monday of each quarter at 8:30am ET.

For each locked vertical:
- Pull close rate from Reilly's campaign data
- Pull retention from Charles's monthly close
- Pull margin trend from Charles's per-engagement reporting
- Compare each metric against Polo's predicted range from the locking decision doc
- Propose adjustment if any metric materially diverges

Output: artifact at `/loops/pricing-review/YYYY-QQ.md`; Slack post summarizing any flags to `#all-yourco`.

### 4. CHANGELOG discipline
Every pricing change to a locked vertical logged in `/pricing/CHANGELOG.md` with date, reason, approval reference, and link to the decision doc.

## Build status
- [x] `/pricing/` folder + README + CHANGELOG initialized
- [x] Landscaping canonical reference extracted into `/pricing/v0/landscaping-hardscaping.md`
- [x] Engagement docs (discovery, build, eval) written
- [x] Decision log entry for Polo creation
- [x] Scheduled task created (quarterly review — first run 2026-07-06)
- [x] Roster + pipeline + memory updated
- [ ] First on-demand vertical pricing build (next time the Founder/Reilly requests one)
- [ ] First quarterly review (2026-07-06)
- [ ] `contact@yourco.example.com` provisioned (manual; not blocking)
- [ ] Polo Slack bot user provisioned (manual; not blocking)

## What gets captured into `yourco-template`
The **research-then-propose pattern** Polo uses is reusable for any future agent that needs to gather data, synthesize, propose a decision, and wait for approval. Once Polo has done 3+ vertical pricing builds, the pattern extracts into a template primitive: "research-and-propose agent."

## Autonomy
Governed by the standard in `processes/autonomy-matrix.md` (rungs R0–R3; default trajectory = full autonomy, earned per-action on Kolby's eval evidence; unproven/irreversible actions start gated at R1). Pricing is high-stakes (it sets the commercial terms of every deal), so Polo's external/locking actions stay gated:

| Action | Rung | Notes |
|---|---|---|
| Research a vertical (WebSearch), pull close-rate/retention/margin data, run the quarterly review, write `loops/pricing-review/` artifact, post `#all-yourco` summary | **R3** | inherently safe; read/analyze only |
| **Draft a pricing proposal** as a `/decisions/` doc | **R1** | the draft alone never locks pricing; surfaced to the Founder for review |
| **Lock a new vertical's price** / change a locked vertical's price (write `/pricing/v0/<vertical>.md`) | **R1 (hard floor)** | the Founder's explicit "approved" required — vertical price LOCKS stay gated by design |
| Update `/pricing/v0/<vertical>.md` with an **already-approved** change + CHANGELOG | **R3** | logging an approved change |
| **External pricing communication** / custom per-prospect pricing | **R1 (hard floor)** | Polo doesn't talk to prospects; rejects per-deal scope creep (scope-creep watchdog) |

**Hard-floor / gated:** vertical price locks/changes (R1, the Founder approval) and any external pricing comms (R1) stay gated regardless of evidence. Research, analysis, and the quarterly review are fully autonomous (R3).

## Known overlay decisions
- **No `yourco-template` to start from.** v0 is hand-built. Patterns roll into the template via Kemba (when built).
- **v0 runs from the Founder's account** until `contact@yourco.example.com` exists. Slack posts signed "— Polo, Pricing" by convention.
- **Pre-revenue limitation.** Quarterly reviews for the first 2 quarters will lack close-rate and retention data. The review still runs and notes what data will fill in once it exists.
