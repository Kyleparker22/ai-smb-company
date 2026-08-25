# 2026-06-07 — CRM architecture: `_pipeline.md` canonical, Instantly CRM activation layer

## Decision
- **`clients/_pipeline.md` is YourCo's canonical CRM.** System of record. Source of truth for every prospect, active engagement, expansion, parked, and lost deal. Queryable by every agent (Atlas, Polo, Brett, Charles, Reilly, future Bird/Kortney).
- **Instantly CRM (bundled with Hyper CRM tier, $97/mo) is the activation layer.** Holds campaign-active prospects, sequence position, reply/bounce/open status. Lives where sending happens.
- **Reilly bridges the two.** She pushes prospects from `_pipeline.md` into Instantly campaigns; she pulls reply/bounce status back into `_pipeline.md` via Instantly webhooks.

## Context
the Founder asked: how is Instantly's CRM, and is it good and easy to use? Reviews say yes (G2 consensus: intuitive setup, sequence-aware pipeline view, good for outbound workflows). The real question wasn't whether to use it — it was *what role* to give it.

We made a hard decision earlier this weekend to keep YourCo's CRM workspace-native (`_pipeline.md`) rather than adopt HubSpot. The reasoning still holds: markdown is portable, agent-readable, version-controllable, free of vendor lock-in, queryable by every agent in the OS via file reads. That decision applies equally to Instantly CRM.

But Instantly CRM is *bundled* in the tier YourCo is now paying for (Hyper CRM, required for SMS). It would be wasteful to ignore it. The question is how to use it without re-introducing a vendor as system of record.

## Options considered
- **A. Use Instantly CRM as system of record.** Rejected — re-introduces the vendor-lock-in problem we already rejected with HubSpot. Atlas can't natively query Instantly's UI; future agents (Bird, Kortney) would have to add Instantly API calls instead of reading workspace files. Pipeline state lives in someone else's database.
- **B. Don't use Instantly CRM at all.** Rejected — wasteful given it's bundled. Reilly genuinely needs a campaign-active view; she'd have to build one from scratch from webhooks if she ignored Instantly's native one.
- **C. `_pipeline.md` canonical, Instantly CRM activation layer.** Chosen.

## Why this won
- **Separation of concerns.** Pipeline-of-truth is workspace; campaign-active state is Instantly. Each is the right tool for its own job.
- **No vendor lock-in on the canonical layer.** If we leave Instantly tomorrow, `_pipeline.md` is unaffected. Reilly swaps her send-layer integrations; the pipeline keeps working.
- **Every agent already reads `_pipeline.md`.** Atlas's Monday briefing, Polo's quarterly review, Charles's per-engagement margin — all read the workspace. No retrofitting.
- **Reilly's update workflow is the bridge.** Same pattern as Reed (asset registry) and the suppression list — agent state lives in the workspace; vendor state stays in the vendor.

## The bridge pattern (Reilly's workflow)
1. **Prospect identified** (via Instantly SuperSearch for trades, Vibe for knowledge work, Outscraper for hyper-local). Recorded in `_pipeline.md` with stage `prospect`, source noted.
2. **Prospect promoted to campaign.** Reilly pushes to Instantly via API. Stage updates to `prospect` → `campaign-active` in `_pipeline.md`; campaign reference recorded.
3. **Reply received.** Instantly webhook fires. Reilly classifies (positive/negative/neutral), updates `_pipeline.md` with reply summary and stage promotion (e.g., `discovery`).
4. **Bounce or opt-out.** Instantly webhook fires. Reilly updates `agents/reilly/_suppression.md` (suppression list) AND records lost reason in `_pipeline.md`.
5. **Engagement signed.** `_pipeline.md` updates to `build` stage; new `clients/<client>/` folder created (Janice's territory when she's built).

## What lives where

| State | Workspace `_pipeline.md` | Instantly CRM |
| --- | --- | --- |
| Prospect identity (name, company, email, phone) | ✅ canonical | mirror |
| Stage (prospect/discovery/proposal/build/live/expansion) | ✅ canonical | n/a |
| Source attribution (Instantly/Vibe/Outscraper/manual) | ✅ canonical | n/a |
| Active campaign reference | mirror | ✅ canonical |
| Sequence position | n/a | ✅ canonical |
| Open / click / reply / bounce status | summary only | ✅ canonical |
| Suppression list | mirror (`agents/reilly/_suppression.md`) | mirror |
| Engagement outcome (won/lost/parked + reason) | ✅ canonical | n/a |

## Reversibility
- **Trivial.** Drop Hyper CRM tier and Instantly CRM goes away; `_pipeline.md` is unaffected. Reilly's update workflow downshifts to email-only with no canonical-state damage.
- **Revisit if:** Instantly CRM proves so useful that mirroring becomes friction (unlikely — bridge is light); or a new send-layer tool offers a materially better activation view we'd want to switch to.

## What this unlocks
- Reilly's campaign workflow has a clean state model
- Atlas's Monday briefing continues reading `_pipeline.md` natively (no Instantly API needed)
- Future agents (Bird for expansion, Kortney for customer health) read the workspace, not the vendor
- The "workspace = system of record" principle now applies consistently across CRM, finance, pricing, brand, and engagement state
