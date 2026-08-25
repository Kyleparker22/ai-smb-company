# Janice — Stage 2: Build

## Build approach
Janice is a **template + SOP build**, not a from-scratch one. The substrate already exists: the golden `clients/_yourco-template/` to clone, the `processes/onboarding.md` runbook, the delivery-loop Stage 0 convention, and the tenant-isolation model in `03_internal_platform.md`. Building Janice means: (1) turn the Hour-0 sequence into a step-by-step SOP with hard gates, (2) ship the actual templates an onboarding needs (intake, access request + approval, folder scaffold, handoff), (3) wire the security/approval posture explicitly, and (4) hold her to the eval set in `03_eval.md`. **Activation-ready, not running** — these are the rails the Founder runs Hour 0 on until the first signature hardens them.

## The onboarding SOP (the Hour-0 sequence, step by step)
Trigger: **a deal signs** (Ray/Rafi confirm signature; David logs the deal in the CRM). Janice runs the following in order. Steps marked **[GATE]** stop for the Founder's approval before proceeding.

### Step 1 — Stand up the engagement folder
- `cp -r clients/_yourco-template clients/<client>` (clone, **never fork** — client logic is overlay per `03_internal_platform.md`).
- Fill the `_README` engagement summary: client, vertical, the named employee(s), executive sponsor + point of contact, signed date, **+48h go-live target**, CRM deal ID.
- Multi-employee deal → **one folder, one entry per employee** in the summary.
- If a folder already exists from the proposal stage (the common case — Stage 0 allows early creation), Janice **adopts and completes** it rather than recloning.

### Step 2 — Send the onboarding intake (the pre-call form)
- Send the **Onboarding Intake Checklist** (template below) to the point of contact. Type-agnostic; short enough to return same-day.
- The intake collects the *operational* facts the Audit didn't already settle: who the point of contact is, the systems involved, what kicks the work off, and what a human must approve.
- **The intake does NOT ask for credentials.** Credentials are handled in Step 4 under the access request, never in a general form (security posture — see below).

### Step 3 — Book the discovery call
- Schedule a 30–45 min discovery call **within 24h of signing** (calendar connector; draft the invite, the Founder/PoC confirm).
- The discovery call is the **Janice→Kimi seam**: Janice opens it and hands the package to Kimi there.

### Step 4 — Credential / tenant-access request + approval **[GATE]**
- Determine the **least-privilege** access the first use case needs (from the Audit + intake): exactly which systems, which scopes, read vs write, and why each is needed.
- Produce the **Credential / Access Request + Approval** record (template below) and route it to the Founder. **No provisioning happens before the Founder approves.**
- Credentials are collected via the client's own least-privilege mechanism — OAuth consent, a scoped service account, a delegated admin grant — **never plaintext passwords in email or chat.** Where a secret must be held, it goes in the client's approved secret store / the runtime's secret handling, never in the repo, never in a doc.

### Step 5 — Provision tenant access + the named-employee identity **[GATE — same approval as Step 4]**
- On the Founder's approval only: provision the scoped access, and stand up the **named employee identity** in the client's tenant — `<employee>@<client-domain>` (preferred: the employee lives in *their* world) or an YourCo-tenant alias if the client prefers.
- Wire the employee to the systems the use case touches (their calendar, CRM, inbox, and for voice use cases Vapi/Twilio — only if the engagement is a voice one).
- Record what was provisioned (and its scope) in the access-approval record's "Provisioned" section — the audit trail.
- YourCo is a **scoped, client-approved guest**: access is least-privilege, revocable, and logged. No data is copied into YourCo's environment.

### Step 6 — Record pricing + sync the CRM
- Seed `clients/<client>/cost.md` with the agreed **build fee + monthly retainer** (confirm against Polo's vertical pricing ref in `pricing/`).
- Sync the engagement folder summary against **David's CRM deal** (cite the deal ID; folder ↔ CRM stay one truth).

### Step 7 — Brief the client (kickoff)
- Send the **Client Kickoff Brief** (template below): the next 48 hours, their point of contact at YourCo, the go-live target, and the one-sentence outcome they signed for (Murphy framing — their Desired Outcome, not YourCo's mechanics).

### Step 8 — Hand off to Kimi
- Write the **Janice→Kimi Handoff** doc (template below) into `clients/<client>/onboarding/handoff-to-kimi.md`.
- Hand off **at the discovery call** — Kimi takes the engagement from discovery onward (`processes/discovery-to-48h-build.md`, Hour 0–4 on). Janice's job ends when Kimi can start cold.

### Step 9 — Close the loop
- Write a `learnings/onboarding/YYYY-MM-DD_<client>.md` entry: anything that was slow, any access ask that was unclear, any handoff field Kimi had to chase. The next onboarding reads it as Step 0.

## Security / approval posture (the moat made literal at Hour 0)
This is where YourCo's executive-trust moat is won or lost — Hour 0 is the first time a client hands over real access.
- **Least-privilege by default.** Request the narrowest scope the use case needs, never "admin to be safe." Read-only where read-only suffices.
- **Scoped + revocable.** OAuth/service-account/delegated grants the client can revoke; no shared passwords.
- **Client-approved AND the Founder-approved.** The client consents to each grant; the Founder approves before Janice provisions. Two locks.
- **No secrets in the repo or docs.** The access-approval record names *what* access and *why* — never the secret value.
- **Audit trail.** Every grant + provisioning action is logged in the access-approval record with timestamp + approver.
- **Runtime gate.** Once Janice runs on the always-on runtime, the approval gate (`~/.claude/settings.json`: allow drafts/requests/reads; **deny send/delete/Bash**) means Janice can *prepare and request* tenant changes but cannot execute them unattended — always-on ≠ auto-provision.

## Autonomy
Janice operates under yourco's **Autonomy-by-default standard** (`processes/autonomy-matrix.md`; standard set `decisions/2026-06-25_autonomy-by-default-standard.md`, extending `decisions/2026-06-12_autonomy-ladder.md`). Every action sits on a rung (R0 Observe · R1 Draft/propose · R2 Auto+notify+reversible · R3 Fully autonomous); the trajectory is full autonomy earned per-action on Kolby's eval evidence — **but client-facing + irreversible actions start gated (R1).** For the engagement Janice onboards, the **per-client** matrix (`clients/<client>/autonomy-matrix.md`, template `clients/_yourco-template/autonomy-matrix.md`) governs the running employee; this section governs **Janice's own onboarding actions**. The ladder is explicit here: *removing the Founder means removing the Founder, not the controls* — and tenant access is the one control that **never leaves a human, because the human is the client** (they authorize access to their own systems by definition).

### Action → rung
| Action | Rung | Control |
|---|---|---|
| Clone engagement folder · fill `_README` summary · build the scaffold | **R3** (internal) | reversible in git; clone-not-fork eval (#4) is the gate, not a person |
| Seed `cost.md` · sync the CRM deal | **R3** (internal) | reversible; CRM-sync eval (#7) |
| Write the Janice→Kimi handoff doc | **R3** (internal) | handoff-completeness eval (#5); Kimi acknowledges |
| Draft the intake · access-request · kickoff brief; book the discovery call (draft invite) | **R2** (draft/propose+notify) | drafts surfaced for confirm; runtime deny-send keeps them unsent |
| **Send** intake / access-request / kickoff to the client | **R1 (gated)** | external email → PoC/the Founder confirm; climbs on eval evidence |
| **Tenant access / credential provisioning** (request) | **R1 (gated)** | least-privilege; **client consents + the Founder approves** before anything is provisioned |
| **Provision** scoped access + the named-employee identity in the client tenant | **R1 (gated, hard floor)** | the "Provisioned" table fills **only after** the approval block is signed; runtime denies unattended execution |

### Hard floor / gated (non-overridable)
- **Tenant access / credential provisioning → R1, double-lock (client consent + the Founder approval).** This is the **one hard, non-overridable gate** (logged in `04_agent_roster.md` + the `_README` charter). Per the ladder, the client authorizing access to their **own** systems is their action by definition — so this gate does **not** climb off the human; the human it never leaves is the *client*. Hard caps even on the autonomy trajectory: least-privilege, no plaintext secrets, full audit trail.
- **Bash / delete on the runtime → denied** (the standard's load-bearing deny; an agent that can shell bypasses every gate). Provisioning is done through scoped client grants, never shell.
- A **security miss is a hard fail at any rung** — the autonomy level never trades against the zero-security-miss gate (eval co-primary).

## Connectors used
- **Calendar** — book the discovery call + kickoff (draft invite; confirm).
- **Gmail/email (`contact@yourco.example.com`)** — send the intake, the access request, the kickoff brief (drafts → the Founder/PoC confirm).
- **Google/Microsoft tenant admin (client's)** — provision the employee mailbox + scoped access (the Founder-approved, in the client's tenant).
- **Vapi/Twilio** — only for voice/phone use cases; provision the line + voice identity (the Founder-approved).
- **Workspace files** — clone the folder, write the summary, access record, handoff, learnings.
- **CRM (`/crm/`)** — sync against David's deal record.

## Closed-loop wiring
- **(a) Scheduled trigger:** event-driven, not cron — fires on a signed-deal signal (the activation trigger). Dormant until then.
- **(b) Artifact output:** the populated engagement folder + access-approval record + handoff doc — the next stage (Kimi) reads them.
- **(c) Feedback capture:** Kimi flags any handoff gap back; the Founder flags any onboarding friction.
- **(d) Feed-forward:** `learnings/onboarding/` entries the next onboarding reads at Step 0 — e.g., "Microsoft tenants need the delegated-admin grant *before* mailbox creation; sequence it first."

---

## TEMPLATE 1 — Onboarding Intake Checklist
*(Janice sends this to the client point of contact after signature. Type-agnostic, any vertical. Worked example values shown for the illustrative "Northwind Services" engagement — NOT a real client.)*

```
YOURCO ONBOARDING INTAKE — <Client>
Returned by: <point of contact>      Target: same-day

1. Your point of contact
   - Name / role / email / phone:        e.g. Dana Okafor, Ops Lead, dana@northwind.example
   - Best way + time to reach you:        e.g. email; 9–5 CT

2. The first job (confirm the Audit's pick, or correct it)
   - The most repetitive task that shouldn't need a human:  e.g. triaging inbound service requests + scheduling
   - What kicks it off (call / email / form / calendar / a record changing): e.g. inbound email to service@
   - What it should produce or do:        e.g. a drafted reply + a booked slot
   - What a human MUST approve before it goes out:  e.g. any quote over $500

3. The systems involved
   - Email/calendar platform:             e.g. Google Workspace
   - CRM / scheduling / other tools the job touches:  e.g. HubSpot, Calendly
   - (Voice only) phone system:           e.g. n/a — text engagement

4. Identity for your new employee
   - Preferred employee name (or use YourCo's suggestion):  e.g. "Reilly"
   - Mailbox in YOUR domain or an YourCo alias:  e.g. reilly@northwind.example

5. Anything we should know
   - Sensitivities, compliance constraints, blackout dates:  e.g. none

NOTE: Do NOT send passwords here. We'll request scoped, revocable access
separately — you approve exactly what we can see, and you can revoke it anytime.
```

---

## TEMPLATE 2 — Credential / Access Request + Approval record
*(`clients/<client>/onboarding/access-approval.md`. Janice fills the request; **the Founder approves before any provisioning**; Janice records what was provisioned.)*

```
ACCESS REQUEST + APPROVAL — <Client>
Engagement: <client> · Employee: <name> · Use case: <one line> · CRM deal: <id>

--- REQUESTED (Janice fills) ---
| System        | Scope requested            | Read/Write | Why (the use case needs it)         | Grant mechanism        |
|---------------|----------------------------|------------|-------------------------------------|------------------------|
| Google W'space| Mailbox: reilly@<domain>   | own only   | the employee's identity to send/recv| admin-created account  |
| Gmail (svc)   | service@ inbox             | read       | read inbound requests to triage     | delegated access       |
| HubSpot       | Contacts + Deals           | read+write | log + update the request record     | scoped OAuth / API key |
| Calendly      | one calendar               | read+write | book the slot                       | scoped OAuth           |

Least-privilege check: [ ] each scope is the narrowest the use case needs
No-plaintext check:    [ ] no passwords requested; OAuth / service-account / delegated only
Client consent:        [ ] client has approved each grant on their side

--- APPROVAL (the Founder) ---
Approved by: ______   Date/time: ______   Notes / scope changes: ______
[ ] APPROVED as requested   [ ] APPROVED with changes (see notes)   [ ] DENIED

--- PROVISIONED (Janice, AFTER approval only) ---
| System | What was provisioned | Scope granted | Timestamp | Revocable by client? |
|--------|----------------------|---------------|-----------|----------------------|
Secrets stored in: <client's approved secret store / runtime secret handling> — NEVER in this repo.
```

---

## TEMPLATE 3 — Engagement-folder scaffold
*(What `cp -r clients/_yourco-template clients/<client>` yields + the `onboarding/` subfolder Janice adds. Confirms clone-not-fork.)*

```
clients/<client>/
├── _README.md            # engagement summary — Janice fills on signing
├── 01_discovery.md       # Bella's Audit findings flow in; Kimi completes
├── 02_build.md           # Kimi
├── 03_eval.md            # Kimi
├── go-live.md            # Kimi
├── weekly-readout.md     # Kortney/Kimi, post-go-live
├── cost.md               # Janice seeds fee + retainer; Charles/Atlas roll up
├── demo-kit/             # pre-sale "see yours" walkthrough (carried from template)
├── audit-report/         # Bella's audit output
└── onboarding/           # ← Janice's working area
    ├── intake.md         # the returned intake (Template 1)
    ├── access-approval.md# the access request + approval record (Template 2)
    └── handoff-to-kimi.md# the handoff (Template 4)
```

`_README.md` engagement-summary fields Janice fills: **client · vertical · executive sponsor · point of contact · named employee(s) + email(s) · signed date · +48h go-live target · agreed fee + retainer · CRM deal ID · onboarding status.**

---

## TEMPLATE 4 — Janice → Kimi Handoff
*(`clients/<client>/onboarding/handoff-to-kimi.md`. Kimi must be able to start the build COLD from this — eval-checked for completeness before the discovery call.)*

```
HANDOFF: Janice → Kimi — <Client>
Discovery call: <date/time>   Go-live target (+48h): <date>

1. THE OUTCOME (one sentence, the client's words):  e.g. "Inbound service requests get a same-hour drafted reply and a booked slot, and I only touch the >$500 quotes."

2. THE FIRST USE CASE
   - Trigger: e.g. inbound email to service@
   - Produces: e.g. drafted reply + booked Calendly slot
   - Approval pattern: e.g. human-must-approve any quote >$500; full autonomy on scheduling

3. SYSTEMS + ACCESS (already provisioned — see access-approval.md)
   - e.g. Gmail service@ (read), HubSpot (r/w), Calendly (r/w) — provisioned & confirmed working: [ ]

4. THE EMPLOYEE IDENTITY
   - Name + email (live in tenant): e.g. reilly@northwind.example — provisioned: [ ]

5. POINT OF CONTACT + CONSTRAINTS
   - e.g. Dana Okafor (Ops Lead); no blackout dates; standard data handling

6. COMMERCIALS (for context, not action)
   - Fee / retainer recorded in cost.md: [ ]   CRM deal synced: [ ]

7. OPEN FLAGS FOR KIMI
   - e.g. client wants a second use case (logged as expansion candidate — do NOT scope into build #1)

Handoff complete: [ ] all required fields present   Janice → Kimi acknowledged: [ ]
```

---

## Build status
- [x] Onboarding SOP defined (this file)
- [x] All four templates shipped (intake / access-approval / folder scaffold / handoff)
- [x] Security + approval posture wired (least-privilege, no-plaintext, double-lock, audit trail)
- [x] Eval set defined (`03_eval.md`)
- [x] Engagement docs scaffolded (this folder)
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder, not blocking dormant state)
- [ ] First onboarding run *as Janice* on the first signature — confirmed against the eval set
- [ ] Runtime approval gate enforced for Janice's tenant-touching steps (v1, on activation)

## Known overlay decisions
- **Dormant until first signature** — same v0 pattern as Kimi/Charles ("the Founder holds until the first engagement hardens it"). No fabricated onboardings.
- **Clone, never fork** — Janice's Step 1 always clones the golden template; any abstraction gap goes to `decisions/` for a template upgrade, never a fork.
- **Folder may pre-exist from proposal stage** — per `02_delivery_loop.md` Stage 0, Janice adopts-and-completes rather than reclones.
- **Tenant access = the Founder must-approve** — the one hard, non-overridable gate; logged in `04_agent_roster.md` and the `_README` charter.
