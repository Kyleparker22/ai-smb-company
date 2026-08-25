# The Simulated Company — Build Spec

**Working name:** The Simulated Company (frontier #22)
**Author:** the Founder
**Stack:** no new runtime — `playground/prospect.py` (built 2026-08-08) generates a filled `config.js` for the **live** `clients/_yourco-template/demo-kit/`; deterministic RNG (same profile + seed = same world); output lands in the gitignored sandbox (`playground/data/_prospects/<slug>/`) and is served by the `yourco-prospect-demo` launch entry (:8809)
**Status:** **BUILT** — roadmap row #22. Verified rendering end-to-end 2026-08-08.
**Pillar / form factor:** Sales (pillar 2) with an Intake face; form factor 3 (a walkthrough surface).

---

## 1. Concept

Every operated-AI sale dies in the same place. Before the buyer has seen one thing work, they are asked for data, tenant access, credentials, and an IT conversation. The risk lands before the value, so most deals never reach the value at all — and the smaller the business, the more fatal this is, because there is no IT function to absorb it.

The Simulated Company inverts the order. From a short profile of what the prospect told us across a table — their job types and ticket ranges, their crew and sub names, their suppliers, their volume, who approves what — it generates **their** business as a working walkthrough: the approval screen with their customer and their deposit math, the job board with their suppliers going quiet, the monthly report shaped to their volume. Zero data access, zero integration, zero permission. They watch their own company run, and only then decide whether to hand over the real thing.

**Centrepiece one: same code, different data.** The generator fills the *live* demo kit — it never forks it. This is the playground's founding rule (`playground/_README.md`) applied to the sales surface: a forked demo drifts from the product the day either side changes, and then you are demoing something you do not sell.

**Centrepiece two: modelled, and labelled modelled.** Figures are derived from the numbers the prospect gave us and are titled that way on the surface itself — *"volume coordinated — modelled from the 14 jobs/mo you told us, not a measured result"*; *"uptime · this is a walkthrough, not a running system."* The kit's own banner (*"mockups on sample data — nothing here is live"*) stays on every screen.

## 2. Why it's never been done

Vendor demos come in two shapes, and both fail this job. The **generic demo** shows the vendor's fictional company, so the buyer spends the meeting translating instead of reacting. The **POC/pilot** shows the buyer's real business but costs the thing that kills the deal — data access, security review, weeks of calendar — and vendors accept that cost because their software genuinely cannot be populated without real data.

An operated AI OS can be, because the OS is not a database the buyer fills; it is a set of workflows whose *shape* is the product. Given a description of the business, the workflow shape is fully determined — which means a walkthrough indistinguishable in structure from the real deployment can be generated from a conversation. The unlock is yourco's config-driven kit plus the playground's data-substitution architecture, both of which already existed for other reasons. Nobody has combined them because nobody else's demo layer and sandbox layer are the same layer.

## 3. Build shape

| Piece | What it is | Status |
|---|---|---|
| Profile schema | `client · brand · useCase · approver · trigger · jobTypes[low,high] · customers · suppliers · subs · jobsPerMonth · depositPct · statedAdminHoursPerWeek` | **built** — `--example` prints the canonical shape (the single source; not duplicated into a committed file) |
| Generator | Deterministic build of the hero approval item (real job type, ticket inside their range, deposit computed), board metrics + nudges, monthly report, reliability block | **built** — `build_config()` |
| Honesty layer | Modelled figures labelled inline; `_SYNTHETIC.md` written beside every generated tenant; provenance header in the emitted `config.js` naming the profile it came from | **built** |
| Guards | Refuses a profile missing `client`/`jobTypes`; refuses to write into `clients/`; writes only under the sandbox root | **built** |
| Serving | `yourco-prospect-demo` in `.claude/launch.json` (:8809, 127.0.0.1) over `playground/data/_prospects` | **built** |

**Effort band:** XS per prospect — a profile is a 10-minute artifact of the discovery conversation, and generation is instant. **Effort band to build:** S (one session).

## 4. Moat fit

- **Attacks the actual bottleneck.** Pre-revenue with zero signed clients, the binding constraint is that nobody has seen the thing work in their own terms. This removes every precondition to that experience.
- **Compounds with the Audit.** The walkthrough is generated *from* discovery answers, so building it forces the audit questions to be asked precisely — and what the profile cannot fill is itself a finding (the instrumentation gap the Audit then prices).
- **No-code can't follow** for the boring structural reason: they have no template to fill, because each of their builds is bespoke clicking. There is nothing to parameterise.
- **Zero drift by construction** — the demo is the product's own template, so the model-upgrade dividend and every product improvement reach the sales surface for free.
- **Interlocks:** the Spend Teardown (#23) supplies the profile's cost side; the Mirror Close (#21) is the honest read of the deal this walkthrough is trying to move; Leak Meter (#16) is what these modelled figures become once they are measured.

## 5. Gates / compliance

- **Credibility gate — the binding one.** yourco is pre-revenue; a generated walkthrough that implied delivered outcomes would breach it on the surface a prospect trusts most. Enforced in the generator, not by discipline: outcome figures carry "modelled from…, not a measured result" in the label itself, and the uptime slot renders "—".
- **No counsel gate.** Shown 1:1, unbranded in the OtherVenture sense, nothing published or sent.
- **No real prospect data.** The profile holds what they said in conversation — business shape, not records. No customer PII, no exports, no credentials. If a prospect offers real data at this stage, it is declined until there is a signed engagement and a DPA (gate #1).
- **Named customers in the walkthrough are invented** unless the prospect supplied them as examples themselves.

## 6. Pricing frame

**Not priced.** It is pre-sale collateral generated from a conversation. Charging for it would convert a 10-minute artifact into a deliverable with scope, and the entire value is that it costs the buyer nothing and risks the buyer nothing.

## 7. Activation trigger (build)

**None — built.** Its *use* trigger is any prospect who has had a real discovery conversation, which is where the profile comes from. It cannot be run cold: a profile of guesses produces someone else's business with the prospect's logo on it, which is worse than a generic demo because it is confidently wrong about their trade. The generator enforces the floor by refusing a profile without job types.

## 8. What we will NOT do

- **No modelled figure presented as a delivered result.** Not in the surface, not in the walkthrough script, not verbally. If it was computed from what they told us, the label says so.
- **No forking the demo kit.** The generator fills the live template. A prospect-specific HTML edit is forbidden — it drifts the demo from the product, which is the failure this architecture exists to prevent.
- **No real prospect data pre-signature.** Not even if offered, and especially not customer records.
- **No writing into `clients/`.** A synthetic walkthrough in the client tree would read as a real engagement folder to every future session. Refused in code.
- **No invented testimonials, logos, case studies, or third-party names** anywhere in a generated tenant.
- **No claim that this is their system running.** It is a walkthrough of what would be built. The distinction is stated out loud in the meeting, not just printed in the footer.
