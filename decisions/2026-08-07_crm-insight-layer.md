# 2026-08-07 — the CRM insight layer: seven reads no CRM has

**Decision.** Build seven capabilities into the workspace-native CRM that no commercial CRM ships, and treat
them as **product IP for the Sales pillar** — dogfooded on yourco's own pipeline first, then shipped as a
client OS module. the Founder picked all seven from a brainstorm and asked for them live, not specced.

## Why these seven, and why they're only possible here

Each one is unbuildable in a SaaS CRM for a structural reason, and buildable here for the same reason inverted:

| Capability | Why nobody has it | Why we can |
|---|---|---|
| **Ghost pipeline** — where each deal would be today at your own median velocity | SaaS CRMs keep an audit log, not a reconstructable *state*; and nobody computes a counterfactual board | `crm/data.json` is git-tracked, so every field has a complete, diffable history — 56 revisions / 24 distinct board states as of today |
| **Adversarial reads** — the confidence *spread* between two opposed readers | Vendors sell a single probability, because a single number demos better than a disagreement | one micro-agent per deal already existed; a second with an opposed prior is a prompt and a scorer |
| **Calibrated founder** — bias of the forecaster, not the pipeline | requires capturing a prediction at the moment of a stage move, then grading it; no vendor owns both ends | the board's advance flow already forces exit criteria; one more field rides along |
| **Warm-path routing with a price** | LinkedIn answers "who can introduce me"; nobody prices "warm *this* one person" | `graph.edges` + contact `lastTouch` gives conductance and decay; the ranking is a counterfactual re-solve |
| **Promise ledger** — sold-vs-delivered drift | the CRM and the delivery system are different products from different vendors; nothing reconciles them | `clients/` and `crm/` are the same repo |
| **Mirror board** — the buyer's own ladder | our stages model our process; theirs is invisible and nobody models it | it's a data model plus the discipline to never infer it |
| **Autonomy dial** — % of pipeline running without you | no vendor's incentive points at "use me less" | it is the Autonomy Matrix applied to the CRM's own actions, and it is what we sell |

## The load-bearing design calls

1. **The adversarial split is epistemic, not arbitrary.** The prosecution counts **only buyer-side action**,
   inside a 21-day intent window, and applies the clock at full weight. The defence counts the whole record and
   softens the clock when a next step is booked. So a wide spread means one specific, useful thing: *we are the
   only party moving this deal.* Our own effort is capped (40 pts) and structure is capped (30 pts) — no volume
   of our work can prove their intent. Scores run through a logistic, never a hard clamp, because a reader
   pegged at 100 has lost the resolution the spread exists to measure. Verified in the suite: adding an artifact
   we built moves the defence and leaves the prosecution untouched; a logged meeting moves both.

2. **Every module refuses rather than invents.** This is the same rule `dashboard/clients.py` follows, applied
   seven more times. The ghost prices a deal only when every rung on its path has ≥3 measured occupancies —
   today that is **0 of 8 rungs**, so it reports positions and a separate "on ladder policy" figure derived from
   the stage ladder's own `staleDays`, clearly labelled, and the measured total stays $0. Calibration applies no
   correction below 5 resolved predictions. The mirror reports "unmapped", never "clear". Promise candidates are
   proposed, never accepted. The refusals are the product: a counterfactual that fabricates its baseline is worse
   than no counterfactual.

3. **Bench time is not pipeline delay.** The ghost's origin is a deal's first appearance *on the ladder*, not in
   the file — otherwise months of Relationship-stage warmth get billed as a stalled deal.

4. **The dial's headline is action autonomy, not observation autonomy.** Observation is easy to automate and the
   number flatters (100% today). The headline is the share of *pipeline-moving* work running unattended — **8%**.
   Nothing self-promotes: the module measures uses, Kolby's eval supplies the clean streak, the Founder sets the rung.
   An action that promoted itself would break the standard it measures.

5. **Promise debt is counted and severity-weighted, never converted to dollars.** There is no defensible
   exchange rate between a missed commitment and money.

## What it found on day one, against real data

- **Sample Client** sits at Proposal; its ghost is at **Live** — three rungs. "Stalled" is now a position, not a feeling.
- All three in-motion deals are **contested** (spreads 42/44/26). Every one for the same reason: the only recent
  evidence is ours. Sample Client's last buyer-side signal is **52 days old**, past the intent window entirely.
- The warm graph reaches **2 of 25** companies that carry a value, and **9 companies have no person in the graph
  at all** — reported as a mapping gap, not as cold leads.
- The promise scanner proposed **6 candidates** from the existing record, including "I'll have the updated build
  ready for us to walk through next week" from the 2026-08-07 follow-up draft — a live, unowned commitment.
- **0 predictions** on record, so calibration is empty by design. It starts filling at the next stage move.

## Honest scope

None of this closes revenue this quarter. With 22 deals and one live proposal the numbers are thin, and several
modules (calibration especially) are worth almost nothing until time passes — which is exactly why starting the
clock now is the point. Their larger value is as **the Sales-pillar module we sell**, proven on ourselves first,
in the same pattern as the runtime and the autonomy matrix.

## Where it lives

`crm/{ghost,adversarial,calibration,warmpath,promises,mirror,autonomy}.py` · served at `/api/insight/<key>` ·
UI in `crm/index.html` (Pipeline → Ghost / Mirror, board chips, four Today cards, four dossier sections, seven
Reporting presets, the header dial) · client-facing promise debt in `clients/_yourco-template/client-console.html` ·
refreshed by `runtime/deal_agents.py` · regression suite `crm/test_insights.py` (62 assertions, runs on a copy).
