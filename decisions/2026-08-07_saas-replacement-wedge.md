# 2026-08-07 — SaaS-replacement as an operated-module wedge (yes); dev-shop cloning (no)

## Decision
yourco offers **"SaaS replacement / build-vs-rent"** as a **named entry wedge into the OS** — replacing a client's specific overpriced single-workflow tool with a custom module the **client owns** and **yourco operates**, scoped by the Audit and delivered as a form-factor-2/3 module (`processes/ai-os-modules.md`). It is **not** a new product tier and **not** a software-cloning dev shop. The wedge is the angry invoice; the OS is the business.

## Context
the Founder surfaced the "clone-a-thon" startup idea (a bounty marketplace for killing your own SaaS + a Clone Index). The marketplace was declined for yourco (`decisions/2026-07-05_tool-triage.md` §Addendum 2026-08-04 covers the sibling Sila call; the marketplace verdict: wrong shape/time/legal, a Holdco-level venture at most). the Founder then asked the sharper question: *should yourco just offer building/cloning those systems as a service?* Yes — but only in the operated-module framing, because the same work sold two different ways is two different businesses.

## Options considered
- **Operated-module wedge (chosen)** — replace a named-pain tool with an owned-by-client, operated-by-yourco module; qualify hard; keep the moat.
- **Custom software / clone dev shop (rejected)** — repositions yourco into the most commoditized market there is; the build is the commodity, the operated reliability layer is the moat (CLAUDE.md). Every coding-agent freelancer competes there.
- **Build-and-hand-off (rejected)** — the CharlieOS "install it, you run it" anti-model yourco counter-positions against; hands the reliability burden back and deletes the moat.

## Why
- **It attacks the real bottleneck: the first client.** "Let us audit your AI opportunities" is abstract; *"you pay $28k/yr for X, your team uses seven of its screens, we'll build those seven as a module you own and we operate — for less than the renewal"* is concrete, quantified, and painful. A sharper cold hook that leads into the OS.
- **It's already expressible in the model** — a SaaS replacement ships as form factor 3 (embedded surface) or 2 (headless automation); no new machinery.
- **It sharpens the positioning against the rent-forever complaint:** SaaS = own nothing; a dev shop = you own it but it rots because you run it; **yourco = you own the asset, we operate the reliability.** A differentiated third position.

## Guardrails (non-negotiable — without these it becomes the rejected version)
1. **Build from the client's workflow spec — never the incumbent's code, never a named-product clone.** Clean-room, functions-not-screens. Never market a competitor's product name. (The clone-a-thon writeup's own #1 legal risk.)
2. **Operated, never hand-off.** Reliability/eval/approval/upgrades stay on yourco — that's the moat and the retainer.
3. **Qualify hard to the clonable tier only:** single-workflow horizontal tools (form builders, scheduling, e-sign, approval flows, internal dashboards, reporting layers, light project trackers). **Out of scope:** systems of record, compliance-locked tools, anything with real network effects — exactly where a weekend replacement loses someone's data and kills the brand. (Adopt the writeup's SAM carve-out verbatim as the qualification filter.)
4. **Not a repositioning.** One product, one motion (`decisions/2026-06-18_offering-narrowing-os-first.md`) holds — this is an entry wedge + Audit lens + module form-factor, not a fifth SKU.

## Open — needs a ruling before it goes in a proposal
**Ownership / IP + retainer terms (Polo + Ray).** "You own the asset, we operate it" is the differentiating line, but yourco today *operates* the OS without client code ownership being a selling point. Introducing ownership touches IP and could undercut recurring lock-in. Honest middle to evaluate: **client owns their workflow logic + data + a portable export; yourco owns/operates the reliability layer + infra.** Counsel-gate #13 (`processes/counsel-gates.md`); no ownership promise in any proposal until ruled.

## Reversibility
Cheap. It's a marketing wedge + an Audit lens + a module shape, not infrastructure. If the hook underperforms once outbound is live (post-OtherVenture), drop the framing; the OS motion is unchanged. The one sticky part is the ownership/IP terms — settle those before promising, precisely so they don't have to be walked back.

## Downstream (swept same session)
- `processes/new-offering-lines.md` — added as entry wedge **B7** + a "how they connect" line.
- `processes/audit-sop.md` — build-vs-rent teardown lens added (Bella flags + quantifies the clonable overpriced tools).
- `processes/counsel-gates.md` — gate #13 (ownership/IP + retainer terms).
