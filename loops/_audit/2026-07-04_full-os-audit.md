> ⚠️ **EXAMPLE — not yours.** An artifact from the source company, restored because other pages
> cite it and the reasoning would otherwise dead-end. It describes **someone else's business**.

# Full OS Audit — 2026-07-04

One-time deep audit of the entire yourco OS (runtime, agents, processes, clients, finance, hygiene), run via five parallel reviewers + synthesis. Requested by the Founder on the arrival of Fable 5. Next audit suggested: ~2026-07-18.

**Verdict: the machine is healthy; the business layer around it is what needs attention.** The runtime, approval gate, Slack control surface, and agent wiring are in genuinely good shape (the governance watchdog even caught real drift this morning). The critical findings are commercial, not technical: the first two engagements are unpapered/stalled, and finance is flying blind.

---

## Critical (business) — do these first

1. **Sample Client is stalled.** Proposal out since ~2026-06-14; the planned 6/25 scope call has no documented outcome; CRM says "discovery — re-scoping" while `clients/_pipeline.md` says "Proposal" (they disagree). No follow-up cadence exists. → the Founder: confirm what happened on 6/25, log the next touch in CRM, and fix the stage. Add a deal-age rule (Proposal >7 days without a next date → flag) to the pipeline loop or watchdog.
2. **Sample Product has no written terms.** ~67 commits of production-grade build for a handshake partnership (Nick sells / yourco builds, target $5–10k/yr/company, internal test ~1 month then market). No agreement, no deal in CRM, cost.md is a one-time snapshot not a rolling ledger. Claims-verification + approval-rate features carry E&O-adjacent exposure (Rafi/Ray should look before anything goes public — legal-before-public gate already noted). → Paper the partnership (even one page: IP, revenue split, who pays data costs), create the CRM entry, start monthly cost entries.
3. **Finance is blind.** `runway.md` cash-on-hand = TBD (runway uncomputable), `token_spend.md` all TBD, expenses ledger ~$250+/mo behind confirmed charges (Canva, ElevenLabs, Twilio deposit, Tailscale, Instantly duplicate, Anthropic top-ups), no monthly close has ever completed, and the `finance-close` loop was never wired to a timer. June 1 card decline is a flashing signal. → Before July 7 (first Monday): the Founder supplies cash figure; Charles reconciles the ledger; run the first real close; wire the finance-close timer.
4. **Cost-tracking policy is unenforced.** CLAUDE.md mandates per-client cost.md + Atlas rollup; only prospect-a has one (static), Sample Client has none, no rollup artifact exists anywhere. → Create sample-client/cost.md; add a monthly cost-rollup step feeding the close; watchdog check for stale cost files.

## Runtime & loops

Health: 12+ loops firing on schedule (inbox-triage, monday-briefing, sales, finance, pipeline-report, content, customer-health, eval-review, advisor, brett-ideas, watchdog, sadie all current). Approval gate matches documented posture exactly (drafts/posts/reads allowed; send/delete/Bash denied). Slack listener injection-hardening verified sound (allowlist, env-var prompt passing, Socket Mode, gate preserved).

- **Never wired:** `finance-close`, `brand-audit`, `pricing-review` — prompts + registry entries exist, no systemd timers, zero artifacts ever. Wire them or remove from registry (decision either way).
- **Stale:** `aeo-geo` (Mario, monthly) last ran 2026-06-15 — should have fired ~07-01. Check the timer on the VPS.
- **Silent push failures:** `run-loop.sh:44` swallows `git push` failures (`|| true`, no log line) — artifacts could strand on the VPS invisibly. Log push failures into the loop log so `runtime-alarm.sh` can see them. Same class: a hung `claude -p` killed by systemd leaves no FAILED marker; add an `OnFailure=` marker or stale-log check.
- **Registry drift (caught by watchdog):** `yourco-storm-publish.{service,timer}` unsanctioned. This is INTENTIONAL live infra (Nick's feed publisher, every 20 min) — **sanction it in `agent-registry.json` with owner+purpose; do not delete.** Longer term, client-serving units probably deserve their own registry section (client-infra vs internal-agent).
- **Prompt-pattern breaks (minor):** `finance-close.md` points at `finance/monthly_close.md` instead of the `processes/loops/` pattern; `melanie-briefing.md` is inline-only. Normalize or comment why.

## Agents (96% consistent across roster / registry / listener / channels / dashboard)

- **Melanie** not commandable: in dashboard + has folder, missing from listener dicts, registry channels, and channels.md. Wire her or note the omission as deliberate.
- **Jim**: fully wired but has only `_README.md` — no 01_discovery / 02_build / 03_eval. Complete per the checklist (template: kortney).
- **Reed**: missing a row in the `slack-channels.md` map table (functional, doc gap only).
- Counts disagree across surfaces: CLAUDE.md "(15 loops)" vs ~20 built; roster/dashboard/CLAUDE.md agent counts don't reconcile (Sadie/David status ambiguous). Reconcile once, then make the dashboard-refresh derive counts from the registry instead of hand-editing.
- No abandoned agents; role boundaries are clean (no overlap/gap findings).

## Processes & docs

- **Launch runbook stale** (last updated 2026-06-12): domain-warmup "~Jun 20 target" now past; Instant Employee Mode B and the client-console live-feed items have no owner/ETA (recommend: ship console v1 as an honest daily-refreshed digest).
- **The two real gates are untracked.** launch-gate: status/owner/resolution condition documented nowhere. Counsel gates: ≥8 blocking legal items (legal suite, CAN-SPAM address, TCPA/SMS, referral MLM, rep equity/securities, Care, Conduit, Sample Product public) with no central status, last-engagement date, or ETA. → Create `launch-gate.md` + a counsel-gates master table (Ray owns), link both from CLAUDE.md.
- **Pre-narrowing docs still live:** `processes/ready-to-hire-prds.md` (self-serve SKU catalog — archive it); `processes/demand-generation.md` still lists vertical landing pages/Snapshot as buildable Tier-1 (parked 2026-06-22 — annotate); `processes/new-offering-lines.md` needs a post-narrowing preamble.
- **Sample Client rescope (single agent → full OS) has no decision doc.** Write one.
- **Closed-loop feedback not visibly closing:** "what I'd do differently" line absent from recent loop artifacts; learnings/ last entry 2026-06-28 (expected pre-launch, but make "Learnings applied this run" an explicit template field so the mechanism is visible).

## Hygiene

- **Daily logs dead** since 2026-06-25 while 30+ commits landed — the handoff convention broke exactly when the most interesting work (Sample Product) happened. Either schedule an end-of-day loop or officially retire the convention in CLAUDE.md; don't leave it half-alive.
- **Client code in the company repo:** all Sample Product engine/prototype code lives in yourco-os, which syncs to the VPS. No secrets leaked (verified: .env handling clean, no keys in git), but tenant isolation will matter the moment there's a second client. Plan a per-client repo split before engagement #2.
- **Dashboard `data.json` hand-maintained**, last touched 2026-06-30, disagrees with reality (loopsBuilt 18 vs ~20). Wire a refresh step + visible "last updated" stamp.
- Minor: `.DS_Store` committed (gitignore it), CLAUDE.md is 18KB and drifting — trim counts/roster to pointers so it stops rotting.

## Fable 5 upgrade path

`run-loop.sh` calls `claude -p` with **no model pin**, so every loop runs whatever the VPS CLI defaults to — the upgrade is one CLI update, but it's also uncontrolled: all 20 loops jump models simultaneously with no change record.

Recommended sequence:
1. **Don't upgrade blind while token spend is untracked.** Fable 5 is the premium tier; fix `token_spend.md` logging first (or accept a few weeks of unknown delta).
2. Update the CLI on the VPS, then watch the next watchdog + 2–3 loop runs for behavior/cost drift (eval-review Sunday run is a natural checkpoint).
3. Add a `MODEL_PIN` env var (empty = CLI default) to `run-loop.sh` so future upgrades are a deliberate one-line change, and log a `decisions/` entry — model choice is currently ambient, which contradicts the change-control discipline everywhere else in the runtime.
4. Consider per-loop tiers: mechanical loops (inbox-triage, pipeline-report) don't need the top model; judgment loops (advisor, eval-review, monday-briefing, this audit as a recurring loop) are where Fable 5 earns its cost. Per the autonomy matrix, a stronger model = faster eval-evidence accumulation = actions earn autonomy sooner — that's the real Fable 5 payoff, not raw loop output.

## Consolidated action list

| # | Action | Owner | By |
|---|--------|-------|-----|
| 1 | Sample Client: confirm 6/25 outcome, log next touch, fix CRM stage | the Founder + David | 07-07 |
| 2 | Cash-on-hand into runway.md + reconcile expenses.md | the Founder + Charles | 07-07 |
| 3 | First monthly close (June) + wire finance-close timer | Charles + Kemba | 07-07 |
| 4 | Sample Product: written partnership terms + CRM deal + rolling cost.md | the Founder + Ray | 07-10 |
| 5 | Sanction storm-publish in agent-registry.json | Kemba | 07-07 |
| 6 | run-loop.sh: log push failures; add MODEL_PIN var | Kemba | 07-11 |
| 7 | launch-gate doc + counsel-gates master table, linked from CLAUDE.md | the Founder + Ray | 07-11 |
| 8 | Wire or retire brand-audit / pricing-review; check aeo-geo timer | Kemba | 07-11 |
| 9 | Melanie listener wiring; Jim docs; Reed channel-map row | Kemba | 07-11 |
| 10 | Archive ready-to-hire-prds.md; annotate demand-generation.md; refresh launch runbook | the Founder | 07-14 |
| 11 | CLAUDE.md count/roster reconciliation + trim; daily-log decision (loop or retire) | the Founder | 07-14 |
| 12 | Fable 5 CLI upgrade on VPS after #6, with drift watch + decisions/ entry | Kemba | 07-14 |
| 13 | Pricing GTM quoting matrix (vertical → tier → range → escalate-to-Polo) | Polo | 07-21 |
| 14 | Per-client repo isolation plan before engagement #2 | Kemba + Rafi | pre-signing |
