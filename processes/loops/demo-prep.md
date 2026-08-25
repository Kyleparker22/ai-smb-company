# Demo-Prep Loop (staged) — personalize Email-1 demos at scale

> **Owner: Kemba** (the loop) · Reilly (campaign) · Webb (demo generator) · Reed (vertical hero videos).
> Design + rationale: `decisions/2026-06-17_auto-demo-prep-loop.md`. **STAGED** — activates only when its
> dependencies + the OtherVenture/launch gate clear. Prepares + stages; **never sends** (the gate denies send; the Founder
> approves the campaign in Instantly).

## Goal
Turn "new prospects added to a campaign" into "Email 1 carries each prospect's personalized demo, staged for one
approval." The personalization scales (it's a data-driven page); the *video* does not get rendered per prospect.

## The unit of personalization (the correction)
- **Per-vertical hero video** — Reed makes one per active vertical (`snapshot-config.js`), human-approved
  once (realistic, full-blown). NOT auto-generated per prospect.
- **Per-prospect demo page** — `prospect-demo.html?p=<slug>`, generated instantly from the prospect's own
  CRM/enrichment data (name, company, vertical, their numbers), wrapping their vertical's hero video. Cheap, scales.
- **Email 1** embeds that page's URL as `{{demo_url}}` (`processes/outbound/sequence-copy.md` — "no demo, no send").

## Steps (per run)
0. **Dependency check** — if Instantly per-lead merge-var write or the demo generator isn't available, report what's
   missing and stop (don't fake it).
1. **Find new prospects** in the target Instantly campaign (or a fresh `sadie-intent.json` / sourcing batch) lacking
   a `demo_url`.
2. For each: **generate the personalized demo** (slug + data) via the generator (Webb's Mode-B endpoint).
3. **Confirm the vertical hero video exists**; if a vertical has none, **flag Reed** (don't auto-render).
4. **Write `demo_url`** back to the prospect's Instantly record.
5. **Leave the campaign PAUSED.** Report: prospects prepped, missing hero videos, "staged for your approval."

## Hard gates
- **Never sends.** the Founder approves the staged campaign in Instantly — that's the "approve the batch" step.
- **No bespoke per-prospect video** (cost + the realistic-video credibility gate needs human review; OpenMontage CLI
  is Bash-denied on the runtime).
- **Contact-info + dedup discipline** unchanged (David's CRM dedup; cold stays in Instantly until reply).

## Dependencies (before activation)
- ✅ `instantly.py`: read campaign leads + **write per-lead merge vars** — **built 2026-06-17** (`campaign_leads()`,
  `set_lead_variables()`, `write_demo_urls()`; CLI `--leads` / `--write-demos`; staged, never sends). Needs a live
  test against one real campaign (the Founder confirmed Instantly API access).
- The per-prospect demo generator (`prospect-demo.html?p=<slug>` ← CRM/enrichment) = the launch-runbook "Instant
  Employee Mode B" endpoint.
- A hero video per active vertical (Reed).

## Activation
When deps + launch clear: add `runtime/systemd/yourco-demo-prep.{service,timer}` (model on the briefing units) and
`enable --now`. Until then this is design-only; `runtime/prompts/demo-prep.md` exists but no timer is installed.
