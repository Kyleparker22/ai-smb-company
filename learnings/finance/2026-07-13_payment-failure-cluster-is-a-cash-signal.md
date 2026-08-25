---
name: payment-failure-cluster-is-a-cash-signal
description: Multiple vendor payment failures in one week — especially small charges clearing while larger ones bounce on the same card — is a leading cash-distress indicator the finance pulse should treat as watchdog-level even when cash-on-hand is "TBD."
metadata:
  type: feedback
---

**Observed (2026-07-13 finance pulse):** In one week, card ••2296 *cleared* the smaller/earlier July charges (Instantly 3× $97 Jul 8, ElevenLabs $6 Jul 9, Granola $14 Jul 8) but *bounced* the later/larger ones — Hostinger $24.49 ("insufficient balance," Jul 9) and Descript $35 (3 failed attempts Jul 10–12). No single failure is alarming; the **cluster + the ordering** (small clears, large bounces) is the signature of a near-limit / low-balance funding source.

**Why it matters:** YourCo has carried "cash on hand = TBD" in `runway.md` since 2026-06-07, so the SOP's "runway <6 months" watchdog is *uncomputable* — it never formally fires. That means a genuine cash constraint can be developing with no numbered trigger to surface it. A payment-failure cluster is the **behavioral proxy** for a tight runway when the number itself is missing. One of those failures was the VPS that runs the entire OS (`[[2026-07-10_host-billing-is-a-runtime-death-vector]]`), so this doubles as a runtime-death signal.

**How to apply (Charles, weekly pulse):**
1. Every pulse, scan the last 7 days of Gmail for **failed/declined/insufficient-balance** payment notices — not just successful receipts. Treat **2+ distinct vendors failing in one week** (or any failure on the runtime host / Anthropic) as a **lead-with-it, watchdog-level item**, even when cash is TBD and no numbered watchdog fires.
2. When failures cluster, check **which charges cleared vs. failed on the same card** — if small/early cleared and larger/later bounced, call out the near-limit-card read explicitly; it's more actionable than listing failures separately.
3. Re-escalate "set cash-on-hand in `runway.md`" from routine-carried-blocker to **urgent** whenever a failure cluster appears — the missing number is exactly what would size the urgency.
4. Book failed charges in `expenses.md` as **UNPAID/failed** (not omitted) so the recurring-cost picture stays honest and the follow-up (renew/fix-card/cancel) has a home.

Triggers: agent:charles, loop:finance, loop:inbox-triage, payment failure, declined charge, cash signal, runway
