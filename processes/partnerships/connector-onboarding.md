# Connector onboarding — what actually happens when someone goes official

> **The gap this fills (2026-08-07):** flipping `teamStatus` prospect → active in the CRM used to do
> *nothing*. No trigger, no checklist, no provisioning. This runbook is the R0 rung made operational.
> Owner: **Bird** (runs it) · David (CRM) · Charles (payout setup) · Ray (papers) · the Founder (signs).
> **Counsel + launch gated** — no connector reaches step 1 until the program clears.

> **Ownership — updated 2026-08-07 (the Founder's call).** **Kori owns connector people-ops**: onboarding,
> provisioning (email/Slack/console), training progression, and the ongoing people relationship. Her
> scope broadens from "internal employees" to **yourco's internal team — employees *and* contract
> partners** (the title matters: an internal doc reading "the Employee Manager owns our contractors" is
> the kind of sentence a reclassification claim would enjoy; the function is people-ops, so name it that).
> **Bird keeps the program**: terms, enablement content, deal registration, growth, and the commercial
> relationship. Ray owns the papers, Charles the payouts, the Founder signs.
>
> *Why it was Bird before:* Bird already owned partnerships in `partner-enablement-kit.md` before this
> week's work, and connectors-as-contractors sat awkwardly under an "Employee Manager." the Founder's
> 2026-08-07 classification call — **contractors legally, team operationally** — resolves it: the
> people-ops function is Kori's, with the contractor line preserved in the paperwork.
>
> **Activation note:** Kori's original trigger was yourco's first human hire. It is now **whichever comes
> first — the first human hire or the first connector onboarding.** She wakes up for this.

## The trigger
**`teamStatus: prospect → active` on their CRM contact is the switch.** Nothing before it is onboarding
(a prospective connector is a person on a bench). Nothing after it is optional — every step below is
owed to them the week they sign.

## The steps

### Before the flag flips — the papers (Ray + the Founder)
1. **Connector Agreement countersigned** — the counsel-cleared version, both signatures, PDF filed to
   `processes/partnerships/legal/signed/<connector-slug>-<date>.pdf` (gitignored — PII).
2. **W-9 on file** *before* any payout can be computed (`referral-program.md` §5.2). No W-9 → they can
   refer, but Charles cannot pay; say so plainly at signing rather than at first payday.
3. **Income Disclosure Statement delivered** alongside the agreement — required at the point the
   opportunity is presented, not after.
4. **Payee choice recorded** — individual or their own entity, their call, never required
   (`counsel-review-checklist.md` item 15a). Whatever the W-9 says is who gets paid.

### The flag (David)
5. **CRM: `teamStatus` → `active`**, `lastTouch` stamped, `relationship` filled if known.
6. **Ladder recomputes → R0** and `connector_ladder.py --sync` records the movement to the attribution
   log with its evidence. *This is the first entry in their permanent record — their console history
   starts here.*
7. **Recruited-by set** if someone brought them in (`meta.repRecruiters`) — this is what makes the
   downline tree and the override real. Set it at onboarding or it gets forgotten.

### Provisioning (Bird + Kimi)
8. **Connector Console login issued** — their own account, not a shared link. Mechanics:
   - Operator issues a **one-time setup token** for them (`--issue-setup-token "<name>"`), delivered to
     them directly. It expires and works once.
   - **They set their own passphrase** via that token. yourco never sees, stores, or asks for it — only
     a hash. **Never accept a connector's password over text, email, or a call**; if one is ever
     disclosed, reset it rather than using it.
   - They log in at the console; **identity comes from their session, never the URL**, and every read
     and write is scoped server-side to them (plus their downline, if they have one).
   - **The walkthrough IS the R0 training.** The console does not open onto a dashboard — it opens onto
     the R0 curriculum, and nothing else is visible (not their ledger, not Resources) until those
     lessons are marked complete. So the day-1 session is: sit with them, go through R0 together,
     and watch the rest of the console unlock at the end of it. That is the onboarding.
   A partner portal is standard and carries no classification risk — unlike a company mailbox (8a).
8a. **yourco email + Slack — DECIDED (the Founder, 2026-08-07): every connector gets both, from day one.**
   Rationale: one organized channel of record instead of personal inboxes, and prospects hearing from
   an yourco address makes the introduction look unified and professional.
   - **Provision:** `contact@yourco.example.com` (Workspace seat — a real per-seat cost per connector,
     Charles books it) + their own `#yourco-<name>`-style Slack access scoped to connector channels,
     not internal agent channels.
   - **⚠️ What this obligates, because it isn't free.** Company email, company tools, and company Slack
     are recognized **worker-classification factors** — they argue the person is an employee. the Founder's
     classification call (2026-08-07) is **independent contractors, treated like team**, which means the
     paperwork now has to carry weight the informal setup used to: the Connector Agreement must state
     the email/Slack/tools are **licensed, revocable, non-exclusive tools provided for convenience,
     conferring no employment**, and the *reality* must match — no set hours, no required minimums, no
     supervision of how they spend their time, and they remain free to refer for anyone else.
   - **The rule that matters:** it is inconsistency that creates liability, not either model. Every
     surface must say the same thing. The packet, the agreement, and every generated demo page say
     *"an independent referral partner, not an yourco employee"* — that language stays, and the tools
     must be framed to match it. **Counsel confirms the package before the first connector**
     (`counsel-review-checklist.md` item 13a).
9. **Referral-spotter consent conversation** — opt-in only, scoped, revocable, recorded in
   `meta.connectorConsent`. **Declining is a normal answer**; the spotter is a convenience, never a
   condition. If they opt in, the loop picks them up on its next run.
10. **Enablement handed over** — the Connector Packet, the ideal-client cheat sheet
    (`partner-enablement-kit.md`), and the one intro sentence that is the whole job.

### First 30 days (Bird)
11. **Day 1:** the walkthrough call — console, packet, what R0 permits and what it doesn't (they cannot
    quote prices or generate demos yet; say it clearly so they don't improvise).
12. **Day 7:** "who are your first three?" — a working session on their own list, not a nag.
13. **Day 30:** first check-in against the ladder — either they've reached R1 (a real conversation) or
    the honest conversation about whether this fits.

## What R0 permits — say this out loud at signing
From `connector_ladder.UNLOCKS` (the single source; never quote a different list):
- **Can:** make warm introductions · **submit contacts for yourco to approach (Sourcer mode — $25 on
  verification, $25 if it books a real conversation; accrued, not payable until launch)** · use the
  console · use the spotter (if opted in).
- **Cannot yet:** generate demos (R1) · recruit other connectors (**R1**, moved from R2 on 2026-08-11) ·
  quote prices (R2) · run audit conversations with oversight (R3).
- **Every rung now needs BOTH** (the Founder 2026-08-07): the evidence *and* that rung's training. A connector
  who produces a live retained client but hasn't finished R1 training **holds R1, not R2** — the console
  tells them so in those words. So recruiting requires **one referral that reached a real conversation**
  and completing the R1 training; the integrity framing survives the move, just at a lower bar: *you
  can't build a team on a thing you haven't done yourself — or been trained on.*
- **The recruiting lesson still needs an operator's confirmation** even though it now sits at R1
  (`connector_training.CONFIRM_CAPS`). A bare rung threshold would have silently made it self-marked
  when the capability moved; recruiting is the stakes, not the rung number it happens to sit on.

The recruiting gate still surprises people, and the honest sentence is unchanged: *you can't build a
team on a thing you haven't done yourself yet.* What changed on 2026-08-11 is only **how much** counts
as having done it — one real conversation, not a client live and retained 90 days
(`decisions/2026-08-11_connector-program-v2.md`). Do not describe R2 as the recruiting gate; that is
now false, and a connector told it would be waiting months for something already open to them.

## Automation status (honest, 2026-08-07)
| Step | Today |
|---|---|
| Ladder recompute + log entry on flag flip | **Manual** — run `python3 crm/connector_ladder.py --sync`. Should become automatic when the CRM writes `teamStatus`. |
| Console render | **Manual** — `python3 processes/partnerships/connector-console/server.py --render "<name>"` |
| Everything else | **Human** — by design. The walkthrough call is the onboarding. |

*Wiring the flag-flip → sync → console-render chain is the first automation to build once real
connectors exist. Until then, doing it by hand three times teaches us what to automate.*
