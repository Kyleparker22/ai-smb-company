# The Autonomy Matrix — yourco's standard operating model

> **The standard, internal and external (2026-06-25).** Every yourco agent — in our own OS and in every client OS — is governed by this matrix. The **default trajectory of every action is full autonomy**; the human's routine time trends to **zero**. But autonomy is **earned per action on eval evidence**, never switched on. The matrix is how we make "the AI runs everything" both *true* and *safe*. Extends `decisions/2026-06-12_autonomy-ladder.md` + `decisions/2026-06-25_autonomy-by-default-standard.md`. Owners: Kolby (eval) + Rafi (controls) + Brett (strategy).

## The principle
"No human checkpoints" doesn't mean "no controls." A human clicking *approve* is just one implementation of a control. We replace it with controls that **don't need a person** — so the human stops spending time and the safety stays. The moat doesn't disappear; it **relocates from the human to the reliability layer** (eval + guardrails + observability + rollback) — the exact layer a no-code operator can't build. Full-autonomy-done-right is the **premium** tier, not the abandonment of the moat.

## The rungs (every action sits on one)
| Rung | What happens | Control that replaces the human |
|---|---|---|
| **R0 — Observe** | read/gather only, no action | n/a (inherently safe) |
| **R1 — Draft / propose** | produces the action; a human commits | the human (the floor for any unproven or irreversible action) |
| **R1.5 — Second opinion** (added 2026-08-13) | an **independent agent with a different lens** clears it to R2-equivalent handling, or escalates to the human *with the disagreement stated* | the second reader — a control that doesn't need a person, which is exactly this matrix's own claim about where control migrates |
| **R2 — Auto + notify (reversible)** | fires automatically, logged, **undoable** for a set window | eval gate + reversibility/rollback + notify; human may watch/undo, needn't act |
| **R3 — Fully autonomous** | fires unattended; human sees only exceptions | eval gate + guardrails + anomaly watchdog + audit + kill switch |

### R1.5 — what it is and is not (`runtime/second_opinion.py`)
Every agent's escape hatch used to be the founder, so every unproven action landed in one person's queue. R1.5 puts one reader in between. **Its scope is bounded by what a correlated reviewer can actually catch** — completeness, written policy, internal consistency, provenance, arithmetic — and it is printed on every verdict. It does **not** catch a shared wrong premise, it is **not** eval evidence, and **clearing an instance never moves a rung**. An agent may never review its own work (enforced, not advised), and `money`, `destructive`, `config-change` and `external-send` can never be cleared by it at all.

## The controls that make R2/R3 safe (the "no-human" stack)
- **Eval gate** (Kolby) — the action fires only if it passes the test set that has *predicted real-world success*.
- **Guardrails** — hard limits the agent can't cross: spend caps, rate caps, allow-lists, "never touch X."
- **Anomaly watchdog** — halts/flags anything outside the proven envelope.
- **Reversibility + rollback** — auto, but undoable for N minutes.
- **Exception escalation** — the agent handles the 95–99%, pings a human only on the genuine edge case.
- **Full audit + a kill switch** the owner (client / the Founder) holds.
- **A spend cap** (added 2026-08-13, `runtime/agent_payroll.py` + registry §`agent_budgets`) — the eighth governance dimension and the one this stack was missing. ⚠ It **reports**; it does not enforce. A cap fires on the next read and cannot stop a run in flight, and saying otherwise would be a fake control. Real enforcement needs a pre-flight check inside `runtime/run-loop.sh`.
- **Provenance typing** (`runtime/provenance.py`) — untrusted content is fenced as data, the weakest source governs the bundle, and an action class has a minimum trust it will accept. Honest bound: this is discipline + audit trail, **not** CaMeL. The load-bearing control is still the harness deny-list.

## Advancement (earned, never assumed) — the streak rule
An action climbs **one** rung only on a **streak**: **N consecutive uses at its current rung succeed with zero incidents**, per Kolby's eval-vs-reality track record. One green run is luck; a streak is reliability (formalized 2026-07-05, `decisions/2026-07-05_loop-patterns-adoption.md`). The mechanics:
- **Any incident resets the streak to zero** — not a deduction, a reset. The count restarts from the incident, and the incident itself gets a written learning before the climb resumes.
- **The streak is a ledger, not a judgment.** Kolby keeps a per-action streak count in the matrix's Streak ledger (internal: `runtime/autonomy-matrix.md`; per client: `clients/<client>/autonomy-matrix.md`), updated each eval-review. Promotion = the owner (the Founder / the client) acting on a full ledger — never Kolby, never the agent, never automatic.
- **Default thresholds** where the owner hasn't set one: **reversible actions (R2→R3): 4 consecutive clean weekly evals** covering ≥10 real uses; **external / higher-stakes (R1→R2): 8 consecutive clean weeks** covering ≥20 real uses. A streak of *empty* runs doesn't count — the action has to have actually fired.
- Kolby measures; the owner sets and can raise the threshold. New/unproven actions **start at R1** — that gated start is what makes the standard credible (see the hard rule).

### The calibration half (added 2026-08-13, `runtime/agent_calibration.py`)
**A promotion now needs BOTH: the streak (did it work?) AND calibration (did it know?).** The streak rule alone cannot tell a reliable agent from a lucky one — both produce a clean streak — and four clean weeks from an agent with no sense of its own limits is exactly the profile that produces the first bad unattended action. So each agent is scored on the forecasts it places about its own reliability (`loops/_trust/forecasts.jsonl`; Brier via the shared `runtime/ledger.py`, so HQ and this can never disagree):
- **Below 5 resolved forecasts there is no calibration verdict at all** — `insufficient-evidence`, which is neither a pass nor a fail. A clean streak with no calibration evidence is explicitly **not** a pass; that gap is the whole point.
- **Overconfidence is tested separately from Brier.** A good aggregate can hide a badly miscalibrated ≥80% band, and that band is where promotions get decided. An agent whose high-confidence claims come true materially less often than claimed is **held regardless of its Brier**.
- The thresholds (Brier ≤ 0.15, overconfidence tolerance 0.15) are **starting values by analogy to the streak defaults — not derived from yourco data**, and every output says so. the Founder sets and may raise them.

### Decaying approvals, and silence as evidence (added 2026-08-13, `runtime/decaying_approval.py`)
"The human's routine time trends to zero" is implemented, not just asserted. An R1 request may carry a **safe default on non-response** — and a non-answer whose default fired *and later resolved clean* becomes evidence toward the rung, instead of sitting on The Board meaning nothing. **The boundary is the entire safety story**, checked deterministically on every sweep against the *live* rung:
1. the action class is reversible with internal blast radius, **and**
2. a working rollback is declared, **and**
3. the action is **already at R2 or better** in the matrix.

Anything failing any test: **silence means NO**, the request expires unapproved, and that expiry is recorded as a decision the Founder did not make — never as one the system made for him. Decaying an R1 action would be day-one autonomy on an unproven action, i.e. the hard rule below. Silence alone is never evidence: a fired default with an unresolved outcome is an open item, and an incident resets the streak like any other.

## Default starting rungs by action class
| Action class | Starts | Ceiling | Notes |
|---|---|---|---|
| Read / observe / summarize | **R3** | R3 | inherently safe |
| Internal file edits, drafting | **R3** | R3 | reversible in git |
| Internal posts (Slack) | **R3** | R3 | reversible |
| Label / organize / archive (reversible) | R2 | R3 | |
| Schedule / hold own calendar | R2 | R3 | external invites → R1 |
| External email to known contacts | R1 | R3 | climbs on eval evidence |
| Email to the client's **customers** | R1 | R2\* | client is **sender-of-record** (CAN-SPAM/TCPA) — their action by law |
| Move money / invoices / payments | R1 | R2 | hard caps even at R2; never unattended without a standing guardrail |
| Irreversible / destructive (delete, sign, file) | R1 | R1–R2 | strong-controls only; many stay gated by design |
| Regulated advice (medical / legal / financial) | R1 | R1 | **AI never freelances** — draft-for-human-review only (the Care/Conduit rule) |

\* A *capped ceiling* means the action **never** reaches unattended R3 without a named exception + counsel.

## The hard rule (the moat-killer to avoid)
**Never start a high-stakes action at R2/R3 on day one** — before any eval track record exists. The first unsupervised agent that sends something wrong to a client's customers destroys the executive trust that *is* the business. Autonomy is earned on data; the gated start is the proof step, not bureaucracy.

## How it's used
- **Per engagement:** fill in `clients/<client>/autonomy-matrix.md` (template: `clients/_yourco-template/autonomy-matrix.md`) during discovery — every capability → its starting rung + the evidence to advance. The client dials their **own** appetite per action; "zero human time" = every action at the highest rung its eval evidence + reversibility support.
- **Internally:** yourco runs the same matrix on its own OS first — `runtime/autonomy-matrix.md` — so we climb on our own evals before asking a client to trust it (the "we run yourco on its own agents" proof, made literal).
