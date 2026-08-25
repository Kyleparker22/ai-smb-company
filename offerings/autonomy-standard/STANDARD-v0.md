# The yourco Autonomy Standard

**Version 0 · authored by yourco · 2026**

*The rules by which an AI system earns the right to act without a human — written by an operator that runs its own business on these rules, published so anyone can hold us to them.*

---

## Why a standard

Every serious conversation about AI in a business arrives at the same question: *what is the AI allowed to do on its own?* Today that question is mostly answered by vibes — either blanket fear ("a human reviews everything, forever") or blanket faith ("it's autonomous, trust us"). Both are wrong, and the second one is dangerous: an unproven agent acting unattended on high-stakes actions is how executive trust in AI gets destroyed — one wrong message sent to the wrong customer, unsupervised, on day one.

This standard replaces vibes with a rule: **autonomy is earned per action, on evidence, and any incident sends it backward.** The destination for every action is full autonomy — the human's routine time should trend to zero. But "no human checkpoint" never means "no control." It means the control has migrated off the human and onto machinery that doesn't need one: evaluation gates, hard guardrails, anomaly watchdogs, reversibility, audit, and a kill switch the owner holds.

## The three rungs

Every action an AI system can take sits on exactly one rung.

| Rung | What happens | The control |
|---|---|---|
| **R1 — Gated** | The AI produces the action; a human commits it. | The human. This is the floor for any unproven or irreversible action. |
| **R2 — Auto + notify, reversible** | The action fires automatically, is logged and notified, and remains **undoable for a set window**. The human may watch or undo, but needn't act. | Evaluation gate + reversibility + notification. |
| **R3 — Autonomous** | The action fires unattended; the human sees only exceptions. | Evaluation gate + hard guardrails (spend caps, rate caps, allow-lists) + anomaly watchdog + full audit + a kill switch the owner holds. |

Purely observational work — reading, gathering, summarizing, with no action taken — is inherently safe and sits at R3 from the start. Everything that *does* something enters the ladder.

R2 is not a compromise rung; it is the load-bearing one. Most of the value of autonomy (the human stops spending time) arrives at R2, while the cost of an error stays bounded (undoable within the window). Many actions should live at R2 for a long time. Some should live there forever (§ "Ceilings").

## Per-action, not per-system

A system is never "autonomous." An **action** is at a rung. The same AI employee might hold R3 for organizing an inbox, R2 for booking calendar slots, and R1 for sending external email — simultaneously, correctly. Grading the system instead of the action is the root error of both the fear posture (one scary action gates everything) and the faith posture (one easy action licenses everything). Under this standard, every capability in a deployment is enumerated, and each carries: its current rung, its ceiling, and the evidence required to advance.

New and unproven actions **start at R1.** This is the hard rule from which the standard's credibility flows: *never start a high-stakes action above R1 on day one, before any evaluation track record exists.* The gated start is the proof step, not bureaucracy.

## Evidence: how an action climbs

An action advances **one rung at a time**, and only on a **streak** — one green run is luck; a streak is reliability.

**The record.** Advancement is grounded in an evaluation-versus-reality record: the action's outputs are evaluated on a recurring cadence against what actually happened in the real world (was the draft approved unchanged? did the booking conflict? did anyone complain?). The record is kept by a designated evaluation owner as a per-action **streak ledger** — counts of consecutive clean evaluation periods and real uses. The ledger holds counts only; it never holds the authority to promote.

**The thresholds.** Where the accountable owner has not set stricter ones, yourco's operating defaults — the same thresholds we run internally — are:

- **R2 → R3 (reversible actions):** 4 consecutive clean weekly evaluations, covering at least 10 real uses.
- **R1 → R2 (external or higher-stakes actions):** 8 consecutive clean weekly evaluations, covering at least 20 real uses.

**Empty runs don't count.** A clean week in which the action never actually fired advances nothing — the streak measures demonstrated reliability, not elapsed time. And streaks open at zero: prior good behavior that predates formal tracking is not retroactively counted. Start honest, not reconstructed.

**Promotion is a human decision.** When a streak crosses its threshold, the evaluation owner recommends; the accountable owner — the business the system serves — decides. Never the evaluator, never the AI, never automatic. The owner may set thresholds higher than the defaults at any time, per action; they may not set them lower than "a real streak of real uses."

## Incidents: how an action falls

An **incident** is any action-execution failure with real-world effect or near-effect: a wrong send, a bad booking, a guardrail breach, an output that required emergency human correction.

- **Any incident resets the streak to zero.** Not a deduction — a reset. The count restarts from the incident.
- The incident gets a **written post-incident record** — what happened, why the controls didn't catch it, what changed — before the climb resumes. No write-up, no restart.
- The accountable owner may additionally **demote** the action a rung or raise its threshold; severe incidents on high-stakes actions should be expected to.
- Infrastructure failures in a different domain (a scheduler outage, a network fault) are logged and fixed but do not reset the streaks of actions that didn't misexecute — resets follow the failure's actual domain, so the ledger stays a measure of the action, not of the weather.

## Ceilings: what may never advance

Some actions have a ceiling below R3 **by design**, and no amount of clean evidence lifts it:

- **Destructive and irreversible actions** — hard deletion of data, signing, filing, anything with no rollback path — remain gated (R1) permanently, or R2 at most under strong standing controls.
- **Shell / arbitrary-code access** for an operational agent remains denied where it would let the agent bypass every other control. A gate an agent can route around is not a gate.
- **Regulated advice** (medical, legal, financial) never exceeds draft-for-professional-review. The AI does not freelance in licensed domains.
- **Messages sent in another party's legal name** (e.g., to a business's own customers, where that business is the sender of record under law) cap at R2 — automatic but supervised and reversible — absent explicit, case-by-case exception with counsel.
- **Movement of money** caps at R2 with hard per-transaction and per-day limits as standing guardrails; never unattended without them.

A capped ceiling is not a failure of the standard. It is the standard working: full autonomy is the default *trajectory*, not a universal endpoint, and the actions listed here are precisely the ones where a human's judgment or the law's structure is the control that works.

## What this asks of the operator

Running this standard honestly requires machinery, not policy documents: recurring evaluation against reality, per-action guardrails, anomaly detection, reversibility windows, append-only audit of every action and every promotion, and a kill switch in the owner's hand. An operator who cannot show you the streak ledger, the evaluation record, and the audit trail is not running this standard — they are describing it.

That is the honest cost of the standard, and it is also the point: safe full autonomy is *expensive to fake and cheap to verify.* Ask for the ledger.

## Publication stance

yourco authored this standard and **runs it on yourco first.** Our own internal AI operation is graded by these exact rules — our own send/delete/shell actions started gated, our own streak ledger opened at zero, our own promotions wait for the thresholds above. We do not ask any client to accept unattended autonomy that we have not first earned, by this standard's own arithmetic, on ourselves.

Version 0 is published at yourco's launch as a citable public document. We expect it to be argued with, and we will revise it in public — version-numbered, with changes logged. Numbers in this document are yourco's real operating thresholds, not aspirations; where we have no evidence yet, this document says nothing rather than something impressive.

**The standard in one sentence:** every action starts gated, earns each rung on a streak of real, evaluated, incident-free use, falls back on any incident, and some actions never advance at all — with the evidence auditable and the kill switch in the owner's hand the whole way.

---

*yourco · the Autonomy Standard v0 · this document governs yourco's own operation and every system yourco operates for a client. Feedback and challenges are welcome — a standard that can't survive scrutiny isn't one.*
