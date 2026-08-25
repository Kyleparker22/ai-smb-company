# The Local Mesh — client OSes transacting agent-to-agent (Frontier #10)

**Status:** architecture sketch, not a build spec. Activation is years out (§5); this exists so nearer-term builds (immune system, template hooks, audit trail) are laid down mesh-compatible rather than mesh-hostile.
**Roadmap row:** `offerings/_frontier-roadmap.md` #10 — "Client OSes transacting agent-to-agent — the local-economy agent network." Trigger: client density in one region (~5+).
**Owners:** Brett (frame) + Kimi (eventual build) + Rafi (trust/controls) + Ray (transaction/liability terms, when real).

---

## 1. Concept

When enough yourco clients operate in one region, their OSes start transacting with each other directly: the hardscaper's OS requests a quote from the electrician's OS for the outdoor-kitchen job; the property manager's OS books the landscaper's OS for spring cleanups; the roofer's OS refers storm-damage interior work to the restoration firm's OS — agent-to-agent, in seconds, with **both sides approval-gated** by their own Autonomy Matrix. yourco clients become each other's fastest suppliers, best referral sources, and most reliable counterparties, because both ends of every transaction run on rails yourco operates. The local economy's coordination layer, owned by the only party running both sides.

## 2. Protocol shape — structured intents, not free chat

Agents do not converse; they exchange **typed intents** with defined lifecycles. Free-form agent-to-agent chat is unauditable, unevalable, and prompt-injectable across a tenant boundary — everything the moat forbids. The mesh speaks a small vocabulary:

- **Intent types (initial):** `quote.request` / `quote.response` · `booking.request` / `booking.confirm` / `booking.decline` · `referral.offer` / `referral.accept` · `availability.check` / `availability.response` · `status.update` (on an open transaction).
- **Envelope (every message):** intent type + schema version · sender/receiver tenant IDs (yourco-attested, §3) · transaction ID (threads the lifecycle) · structured payload (job scope, window, site data *the requester chooses to share*) · the sending tenant's approval state (which rung authorized this — auto within earned autonomy, or human-approved).
- **Lifecycle:** every intent belongs to a transaction state machine (open → responded → accepted/declined → fulfilled → closed), so "what happened" is always a queryable state, never a chat log to interpret. Unanswered intents expire honestly; expiry is a recorded outcome, not silence.
- **Approval-gated at both ends:** an inbound `quote.request` surfaces in the receiving client's OS at whatever rung *that client* has earned/set for "respond to mesh intents" (starts R1 — a human sees every early mesh transaction on both sides; climbs per the streak rule like any other action, per `processes/autonomy-matrix.md`). Money never moves on the mesh at launch — intents coordinate; invoicing/payment stay in each business's existing rails until a far-future, counsel-shaped phase.
- **No cross-tenant free text beyond schema fields**, and free-text fields (job description) are treated as untrusted input on receipt — sanitized, never executed as instructions (standard injection posture at a trust boundary, even a friendly one).

## 3. Trust & identity — the core advantage

Open agent-to-agent protocols die on the identity problem: who is this agent, who stands behind it, why believe its claims? The mesh skips the entire problem: **both sides are known yourco tenants.**

- **Identity:** yourco attests every participant — tenant IDs are assigned, not claimed; there is no anonymous or self-registered node. A mesh counterparty is by definition a business yourco audited, built for, and operates.
- **Capability truth:** an agent's claims ("we do paver installs, ~2-week lead time") are backed by an OS yourco runs — grounded in real calendars and real capacity, not marketing copy. Misrepresentation isn't a fraud vector; it's a bug yourco fixes.
- **Behavioral trust:** every participant runs the same reliability layer (eval, guardrails, watchdogs, audit) and the same earned-autonomy standard (`offerings/autonomy-standard/STANDARD-v0.md`). The mesh doesn't need a reputation system at small scale — it inherits yourco's; a simple fulfilled/expired/disputed record per tenant is enough bookkeeping until density demands more.
- This is why the mesh can be *simple*: hard federation problems (identity, spam, adversarial agents, incompatible schemas) are pre-solved by the closed membership. The moat isn't the protocol — anyone can write JSON schemas — it's the operated fleet on both ends.

## 4. What yourco owns

- **The rails:** intent schemas + versioning, routing between tenants, the transaction state machines, expiry/retry semantics.
- **The audit trail:** every intent, response, approval (and which rung authorized it), and state change — append-only, per-transaction, visible to both counterparties for their own transactions and to yourco across the mesh. When a deal goes sideways, the record of who offered what, when, is a fact, not a memory. (Ray shapes what yourco's role in disputes is and is NOT, before activation — yourco is the rails, not the arbiter or a broker, pending that work.)
- **The tenant boundary:** a transaction shares only its own payload. Counterparties never see each other's OS internals, other transactions, customers, or pricing beyond what an intent explicitly carries.
- **The directory:** which tenants participate, in which intent types, in which region — participation is opt-in per client, per intent type, in their engagement terms.

## 5. Activation reality

Honest prerequisites, in order: **(1)** ~5+ operated clients in one region with plausibly-transacting trades (the St Pete/Tampa concentration would be the natural first mesh); **(2)** those clients' OSes individually mature — mesh actions ride on tenants that have already earned real autonomy internally; **(3)** counsel shaping (Ray): referral-fee rules between clients, yourco's non-broker role, liability language in the engagement terms; **(4)** client appetite, contracted per tenant. That is **years out** — and correctly so. The mesh is where "Compound" goes once the flywheel actually spins (roadmap interlocks); building it before density would be the plan's named failure mode #1 (building instead of selling). Until then, the only mesh work permitted is keeping current builds compatible: tenant IDs stable, audit trails append-only, intents-not-chat as the standing pattern for anything cross-tenant.

## 6. Interlock with the Immune System — one network, two services

The mesh is the **second service on a network the immune system builds first.** Same substrate, opposite directions of value:

| | Immune System (#8) | Local Mesh (#10) |
|---|---|---|
| What flows | defensive patterns (anonymized, human-gated) | commercial intents (structured, approval-gated) |
| Direction | hub-reviewed broadcast to all tenants | point-to-point between two tenants |
| Live at | client #2 | ~5+ clients, one region |

Shared machinery: the tenant registry/IDs (immune system's opaque engagement IDs grow into mesh identity) · the cross-tenant chokepoint pattern (one audited path across any tenant boundary) · the append-only audit discipline · the per-action autonomy grading on both ends. The immune system also makes the mesh *sellable*: a business will let its OS transact with a counterparty's OS precisely because both are inside the same defended, evaled, human-gated fleet. Defense first, commerce second — and by the time density arrives, the network's rails already exist and have years of audit history.

## 7. What we will NOT do

- **No open protocol / external nodes:** no federation with non-yourco agents, no public API, no joining third-party agent-commerce networks. The closed fleet IS the product; opening it re-imports every problem §3 skips.
- **No free-chat agent negotiation** across tenants — intents only, forever.
- **No payments on the rails at launch**, and none ever without dedicated counsel work (money transmission, broker exposure).
- **No yourco take-rate on transactions** as the initial model — the mesh is retention/expansion value for operated clients, not a marketplace toll booth. Polo revisits only at real density, and any referral-fee mechanics inside the mesh get the same counsel scrutiny as the human referral program (counsel gate #5 precedent).
- **No matchmaking editorializing:** the mesh routes intents; it does not rank, recommend, or steer one client's demand toward another client. Steering is a conflict-of-interest engine.
- **No building any of this before the density trigger** — this document's job is compatibility, not construction.
