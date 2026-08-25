# Offboarding & Data Export — SOP

> The mirror of `onboarding.md`. A client pause or exit must be **clean, drama-free, and data-returned** — never a hostage situation. It's both an enterprise-trust signal (a graceful exit gets referrals and return business) and a **legal obligation** (the DPA requires data deletion on termination; this is the procedure behind that clause). Owners: **Janice** runs it (onboarding's mirror) · **Rafi** (data deletion + compliance) · **Charles** (final billing) · **Kortney** (the relationship + the readout). Trigger sources: client cancels, non-renewal, or suspension for non-payment (per the Engagement Agreement §2).

## Principle
We make leaving as easy as joining. We return the client's data, delete our copy on schedule, confirm it in writing, and leave the door open. No friction, no retention games.

---

## Path A — Pause (temporary)
For a client who wants to stop for a season, not leave.
- [ ] Confirm scope + restart intent + effective date; log it.
- [ ] **Suspend the employee** — stop the live triggers (number/inbox/schedule), but preserve config, logs, and the trained logic so restart is fast.
- [ ] **Billing** — pause or move to a reduced hold rate per the agreement (Charles).
- [ ] Keep data intact (no deletion during a pause) — note the pause in the client folder.
- [ ] Resume = re-point the trigger + un-pause billing. Near-instant, because nothing was torn down.

> The client can request a pause from their **console** ("Pause [employee]") — that flags Janice/Kortney; it doesn't self-execute billing or data changes.

## Path B — Offboard (permanent)
1. **Confirm & log** — who requested, when, reason, effective date. Honor the notice period in the Engagement Agreement. Acknowledge in writing same day.
2. **Final billing reconciliation** (Charles) — final/prorated invoice, settle any balance, stop recurring billing on the effective date. Record in `finance/revenue.md`.
3. **Wind down the employee** — stop all triggers; deprovision the employee identity (`<employee>@<client-domain>` / number); **revoke YourCo's access to the client's tenant, domain, and connectors**; disable integrations.
4. **Data export to the client** — package what the employee produced and touched (interaction logs, booked records, CRM entries, any deliverables) in a usable format ([[CSV/JSON/PDF]]) and deliver securely. This is the client's data; they get it back.
4a. **Configuration handover** (Janice/Kemba) — package the employee's **configuration, prompts, and
   workflow documentation in human-readable form** so the client, or whoever comes next, can see exactly
   what ran and why. *This is a contractual obligation, not a courtesy* — Engagement Agreement §3.1
   (added 2026-08-24) promises it, and until that clause exists in practice the contract over-promises
   what this SOP delivers. **What is NOT handed over:** yourco's platform, eval frameworks, templates and
   tooling (Agreement §5) — the employee stops because it runs on yourco's infrastructure, which is the
   same reason the client never received an infrastructure bill.
4b. **Open the transition window** (Kortney) — for **[[30]] days** after the effective date, yourco answers
   reasonable transition questions. Diary the end date; say plainly when it closes rather than letting it
   fade.
5. **Data deletion per the DPA** (Rafi) — delete the client's data from YourCo systems within the DPA-specified window; purge from runtime, dashboards, backups (per policy), and any connector caches. **Issue a written deletion confirmation** to the client. Document what was deleted and when.
6. **Revoke & remove** — rotate/revoke any keys or credentials tied to the engagement; remove the client from the runtime, the internal dashboard, and active monitoring; disable the client console (or switch it to a read-only export-only mode for the agreed grace period).
7. **Close the loop with the client** (Kortney) — an offboarding note: what was delivered over the engagement, the data handoff, the deletion confirmation, and an open door to return. Graceful.
8. **Archive & learn** — `git mv clients/<client>/ _archive/`. Capture the **exit reason** → `learnings/` (churn analysis): why they left, what we'd change. Feed-forward to delivery + sales.

## Checklist (Path B)
- [ ] Request confirmed + logged + acknowledged (Janice)
- [ ] Final invoice settled; recurring billing stopped (Charles)
- [ ] Employee deprovisioned; tenant/connector access revoked (Janice/Kemba)
- [ ] Data exported + delivered to client (Janice)
- [ ] **Configuration/prompts/workflow docs handed over in readable form (Janice/Kemba) — Agreement §3.1**
- [ ] **Transition window opened + end date diarised (Kortney) — Agreement §3.1**
- [ ] Data deleted per DPA + written confirmation issued (Rafi)
- [ ] Keys revoked; removed from runtime/dashboard/monitoring (Kemba)
- [ ] Offboarding note sent; door left open (Kortney)
- [ ] Client folder archived; exit learning written (Janice/Kortney)

## Gates (the Founder/compliance must-approve)
- Anything touching the client's tenant/data during wind-down stays gated.
- The DPA deletion step is **not optional and not silent** — it produces a written confirmation. Rafi signs off.

## Console hooks (Webb)
The client console should expose, at end-of-engagement: **Pause**, **Request data export**, and **Request offboarding** — each flags the team (never self-executes billing/data actions). Closes the loop with the "Use daily → Leave/pause" lifecycle stage.
