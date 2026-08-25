# Client Error Sweep Loop (per live engagement — activation-gated)

> **Owner: Kimi** (delivery) per engagement, observed by Atlas. A nightly triage of a live client deployment's production errors: separate **actionable** from **noise**, propose fixes (draft-only — a fix ships through the normal approval-gated path), escalate what threatens the outcome. **This is the reliability moat made nightly** — the client never sees the errors because we saw them first. Adopted 2026-07-05 (`decisions/2026-07-05_loop-patterns-adoption.md`).
>
> **Not scheduled until a client is live.** One instance per live engagement, instantiated from this SOP — an error sweep with no production traffic is empty runs and eval noise (`runtime/activation-triggers.md` §Loop triggers). **First candidate: Sample Product** once public (its VPS services — `storm_alerts.py`, publisher — already run in production; the runtime alarm watches yourco's own loops, not client services).

## Instantiating for a client (Kemba, at go-live)
1. Copy this SOP's checklist into `clients/<client>/loops/error-sweep.md` with the engagement's specifics: which logs/services (systemd units, app logs, API error responses, webhook failures), where they live, and the client's definition of "actionable."
2. Write `runtime/prompts/error-sweep-<client>.md` (point at the client SOP; include the loop-contract footer).
3. systemd pair `yourco-error-sweep-<client>.{service,timer}` — default **nightly 05:30 ET** (before the morning loops, after the client's business day).
4. Rafi sanctions in `runtime/agent-registry.json` → Kolby evals the first week's outputs → the Founder enables the timer. Same climb as everything else: the sweep **starts R1** (findings + proposed fixes only); auto-remediation is earned on the streak rule, per-action.

## The triage bar (what "actionable" means — tune per client)
**Actionable** = reproducible or recurring, attributable to something we control, and it degrades the client's outcome (a failed alert send, a stuck pipeline stage, a data-sync error, an auth failure on a service we run). **Noise** = transient third-party blips that self-recovered, rate-limit backoffs that worked, single non-recurring warnings, upstream outages we can only note. When unsure, one line in the artifact — never silently dropped. The triage IS the value: an unsorted error dump is what the client could have gotten from a log file.

## Inputs (read every run)
1. The engagement's service logs / error surfaces since the last sweep (as specified in `clients/<client>/loops/error-sweep.md`).
2. The prior sweep artifact — open findings, recurrence tracking (is yesterday's "transient" back today?).
3. The engagement's eval + guardrail definitions (`clients/<client>/`) — an error that breaches a guardrail is automatically SEV-1.

## Steps
1. **Sweep** all error surfaces since the last run. Count everything; triage everything.
2. **Classify** each distinct error: ACTIONABLE (with severity: SEV-1 outcome-threatening / SEV-2 degrading / SEV-3 hygiene) or NOISE (with the one-line reason). A "transient" seen 3 runs running is reclassified ACTIONABLE — recurrence beats any single-run judgment.
3. **Propose fixes** for actionables: root cause (or best hypothesis + what would confirm it), the proposed fix, and how we'd verify it — **as a draft/proposal artifact, never applied by this loop.**
4. **Write the artifact** to `clients/<client>/loops/error-sweep/YYYY-MM-DD.md`: counts (total seen / actionable / noise), the actionable table (error · first seen · recurrence · severity · proposed fix · status), noise summary, open-findings carryover.
5. **Escalate:** SEV-1 → Slack the engagement channel + `#all-yourco` immediately, signed "— Kimi (error sweep)". SEV-2/3 → the engagement channel only. Clean night → artifact only, no post (the watchdog verifies the loop ran).

## Watchdog triggers (escalate)
- Any SEV-1, or any guardrail breach → immediate, top of post.
- The same actionable open ≥3 sweeps with no movement → escalate to the Founder via the open-loops chaser queue.
- Error volume spiking vs the trailing week (>3×) → flag even if all individually minor.
- A sweep that can't read its log surfaces = a MISSED-equivalent — say so loudly; blind ≠ clean.

## Feedback capture
the Founder/Kimi mark each proposed fix approved / rejected / deferred in the artifact; the next run reads it. Patterns (a recurring root cause, a noise rule worth codifying) → `learnings/delivery/`.

## Pre-live handling
Does not run pre-live, by design. If it's ever enabled against a quiet deployment: "0 errors seen across N log lines / M services checked" is the honest artifact — never pad a quiet night into findings.
