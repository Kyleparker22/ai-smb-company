---
name: checkbox-is-not-clearing-evidence
description: A flipped task checkbox (done:true) is not evidence an open loop cleared when the substantive record contradicts it — reconcile against the data fields, not the checkbox.
metadata:
  type: feedback
---

In the open-loops chaser (and any reconciliation loop), a task marked `done:true` is **not** clearing evidence on its own. Twice in one run (2026-07-07) a checkbox flipped while the underlying record showed the work undone:
- `t_sc_meeting` (Sample Client 6/25) → `done:true` + `nextDate` advanced, but `activities` still ended 06-16, `lastTouch` unchanged, `stage` unchanged — no 6/25 outcome ever logged.
- `t_hank` → `done:true`, but the company name was still the literal placeholder "(the Founder to fill)", the contact was blank, and the deal was still `prospect` at a past-due `nextDate`.

**Why:** a checkbox records intent-to-close, not the work-product. Treating it as "CLEARED" is the same hedge-erosion the eval layer flagged on the 6/25 meeting ([[2026-07-06_cross-session-drift]], and `learnings/qa-eval/2026-07-05_unconfirmed-facts-must-stay-hedged-across-loops`): a soft signal hardening into a fact. The SOP's CLEARED bar is deliberately "evidence required — the draft is gone/sent, the deal moved, the decision file updated," and the watchdog trigger "changed without evidence of clearing → flag it" exists for exactly this.

**How to apply:** when reconciling, check the substantive fields the task was *supposed to change* (activities/`lastTouch`/`stage` for a meeting; company name + contact + deal stage for a "book it" task), not the `done` flag. If they contradict the checkbox: keep the item queued, and file it under the reconciliation-flag section as "checkbox flipped, data contradicts." Clean-CLEARED needs the record; citably-PARKED needs a decision link; a bare checkbox is neither. This is the honesty-anchor role — a checkbox that outruns its evidence is drift, not completion.

Triggers: agent:ray, agent:rafi, gate tracker, clearing a gate, evidence for done, marking complete
