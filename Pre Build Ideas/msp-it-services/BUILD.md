# Queue OS — MSP / IT services (build 14)

**Working name:** Queue OS · **Launch:** `prebuild-queue-os` · **Port:** 8834

## The idea

A 10–30 person MSP dies by queue: the phishing report sitting behind forty printer tickets, the
SLA breach discovered when the client calls angry, and the out-of-scope project work quietly done
free because nobody checked the agreement. Queue OS triages with a security bias, counts SLA
clocks from the agreement itself, and refuses to call anything billable without the clause.

**Buyer:** the MSP owner / service manager. Thinks in tickets, SLAs, agreement margin.

## The bleeding neck

- A security signal triaged as routine is a breach with the MSP's name on the incident report.
- SLA state lives in people's heads until a breach becomes a churn conversation.
- Scope creep: "while you're in there" work that the agreement never covered, unbilled for years.

## Modules

1. **Ticket triage** (Intake/Operations) — typed security signals (phishing, ransomware indicators,
   impossible-travel logins, MFA bombing, mass encryption) route to a human security escalation
   **immediately** and can never be auto-closed or auto-downgraded. Outages rank; routine drafts.
2. **SLA watchtower** (Operations) — response/resolution clocks counted per agreement tier; the
   ones about to breach ranked; a missing tier means the clock is *unknowable and says so*.
3. **Agreement-scope ledger** (Back Office) — every non-routine ticket checked against the signed
   agreement's clauses. In-scope cites the clause; out-of-scope cites the exclusion and drafts a
   billable; **a category the agreement never mentions is AMBIGUOUS and goes to a human** — the
   system never asserts billable off silence.

## Guardrails (load-bearing)

- `close_security_ticket` / `downgrade_security` — **R0.** A human security engineer closes those.
- `auto_remediate_production` — **R0.** The system drafts runbook steps; hands touch prod.
- `send_credentials` — **R0.** Credentials never travel in a ticket reply.
- `bill_client` — R1, never promotes, and structurally requires a cited exclusion clause.
- The triage eval's costly class is a security signal read as routine.

## ROI model

Out-of-scope work captured → revenue (counted from the ledger) · SLA credits avoided → scenario ·
triage/dispatch hours → time saved · breach exposure → scenario.

## 10-minute demo

Board → triage the phishing ticket (watch it escalate, then try to close it — refused) → SLA
board with the unknowable clock named → scope-check a backup ticket (clause cited) and a
new-office cabling ticket (ambiguous → human) → ROI → trust.

## Build prompt (§8)

Build `Pre Build Ideas/msp-it-services/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8834,
launch `prebuild-queue-os`. Seed "Northgate Managed IT": ~60 agreements across gold/silver/bronze
tiers with real scope clauses, ~500 tickets incl. every security type and genuinely ambiguous
scope cases, one agreement with no tier. Eval costly class = missed security signal. Tests pin the
security R0s, the ambiguous-scope refusal, SLA unknowability, ROI blanks, counted automation.
