# Lab OS — your locations are your lab (build 69)

**Working name:** Lab OS · **Launch:** `prebuild-lab-os` · **Port:** 8889
**Synthetic operator:** "Blue Finch Hospitality" — 5 fast-casual locations.
(Distinct from build 16 Unit OS, which watches food cost and complaints — Lab OS runs the
group as a laboratory.)

## The never-seen mechanism
Five locations is a laboratory nobody uses: continuous honest A/B experiments across units —
menu items, prices, portions — with real statistics that REFUSE to conclude below sample
floors, plus a counterfactual ledger pricing every 86 and stockout. Chains run this
internally with data teams; no product gives it to a 5-unit group.

## Modules
1. **The experiment desk** (Operations) — an experiment = hypothesis + treatment units +
   control units + metric + the recorded minimum sample (config `_source`-named floors);
   results report lift WITH a plain-language confidence read; below the floor the verdict is
   literally "TOO EARLY TO KNOW (n=…, need …)" — an experiment can never conclude early, by
   construction. Confounds honesty: a unit running two overlapping experiments on the same
   metric is refused at creation ("one lever per dial").
2. **The counterfactual ledger** (Back Office) — every 86'd item and stockout priced from
   that unit's OWN recorded sales pace for that item/daypart (median units × price); an item
   with no pace history reads unmeasured, never estimated. The weekly "what the 86 board
   cost you" number is counted.
3. **Rollout gate** (Sales) — a winning experiment drafts a rollout recommendation R1 with
   the full stats attached; rolling out a TOO-EARLY experiment has no path.
4. **The menu graveyard** (Company Brain) — killed items with their recorded numbers, so the
   "let's bring back X" conversation starts from what X actually did.
5. **Intake triage** (Intake) — costly label: the illness claim ("your tacos made me sick" —
   the Unit OS rule holds: logged verbatim, never answered in writing by software) · GM
   result ask · experiment proposal · 86/stockout report · human.

## Guardrails (load-bearing)
- `conclude_below_sample_floor` — **R0, structural**: the verdict enum has no "winner"
  below the floor.
- `rollout_unconcluded_experiment` — **R0, structural**: no path.
- `overlapping_experiments_same_metric` — refused at creation.
- `answer_illness_claim` — **R0**; logged verbatim, human + counsel path.
- `estimate_counterfactual_without_pace` — **R0**; no pace history, no number.
- Outward drafts R1.

## ROI (typed)
Winning-experiment lift (counted from concluded experiments only) · 86-board cost recovered
(counted ledger) · the bad-rollout avoided (scenario) · owner analysis hours (time_saved).

## Demo path
A live experiment (price test, 2 treatment / 3 control) at TOO EARLY → the same experiment
concluded with plain-language stats → rollout draft → early-rollout refusal → the 86 ledger
pricing last Friday's stockout from the unit's own pace → overlap refusal → illness-claim
refusal → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the illness claim.
