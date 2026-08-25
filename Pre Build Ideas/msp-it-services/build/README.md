# Queue OS — build 14

Pre-built vertical AI OS for managed service providers.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py             # 60 agreements, ~500 tickets
python3 test_queue_os.py    # 37 assertions
```

Launch name **`prebuild-queue-os`** (port 8834, 127.0.0.1 only).

## What it is

"Northgate Managed IT" — 18 people, $4.2M. Three modules: **ticket triage**, **SLA watchtower**,
**agreement-scope ledger**.

## The refusals it is organised around

**A security ticket is closed by a human security engineer or not at all.** Software attempting to
close one is refused, logged, and never becomes an approvable row. Five typed security signals
(phishing, ransomware indicators, account compromise, MFA bombing, exfil patterns) escalate at R2
— act now, tell the human. The eval's costly class is a security signal read as routine: *A BREACH
WITH YOUR NAME ON THE INCIDENT REPORT.* Recall 1.0, zero missed.

**The scope engine never asserts billable off silence.** In-scope cites the clause. Out-of-scope
cites the exclusion and drafts a billable at R1. A category the agreement never mentions is
**ambiguous** and goes to a human — a distinct verdict, not a default.

Also: `auto_remediate_production` R0 (drafts runbook steps; hands touch prod), `send_credentials`
R0, `bill_client` R1 never-promoting, and an SLA clock that is *unknowable and says so* when the
agreement has no tier on file.

## 10-minute demo

Board → Queue (triage the phishing demo ticket; try "Close (as software)" on the ransomware ticket
— refused; a human closes it) → SLA (breached first, the unknowable clock named) → Scope ledger
(the cabling ticket cites X-1; the lobby-TVs ticket comes back ambiguous) → ROI → Trust.

## What this does not do yet

- **No integrations.** PSA/RMM (ConnectWise/Autotask/NinjaOne), M365 audit logs are adapter seams.
- **Triage is deterministic pattern-matching** — right for the security stop, brittle for real
  ticket prose. A real deployment puts a model behind the routine path and leaves the security
  patterns and the close refusal exactly as they are.
- **No remediation of any kind** — by design; the build drafts, humans act.
- **Nothing is sent.**
