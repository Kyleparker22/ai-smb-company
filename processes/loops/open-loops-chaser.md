# Open-Loops Chaser Loop

> **Owner: Jim** (chief of staff — the desk). The approval gate stops actions and waits for a human; this loop makes sure the waiting is *visible*. It treats every pending human action as a **queue item with an age**, and nags until each is cleared or explicitly parked. **Reports + reminds only** — it never performs the pending action itself. Runs **weekdays, 07:40 ET** (after inbox-triage 06:45, before the Monday briefing 07:55 — the briefing may read today's artifact). Adopted 2026-07-05 (`decisions/2026-07-05_loop-patterns-adoption.md`); direct response to the 2026-07-04 audit's finding that the top gaps are commercial follow-through, not technical.

## The one distinction that matters
**Waiting-on-the Founder ≠ parked-by-decision.** An unsent proposal follow-up is waiting; the MLM counsel gate is parked on purpose. The chaser **nags the waiting list daily** and merely **inventories the parked list** (surfaced weekly on Mondays, so parked items can't silently become forgotten items). Misfiling a parked item as waiting = noise; misfiling waiting as parked = the exact failure this loop exists to prevent.

## Inputs (read every run)
1. The prior `loops/open-loops/` artifact — the queue state; what cleared, what aged.
2. **Gmail drafts** (`list_drafts` / search) — drafts created by the loops (Jim's triage replies, briefing sends) still sitting unsent, with created-date.
3. **`crm/data.json`** — deals whose `nextDate` is past due, or whose `stageSince` shows a stall (default: >14 days in the same stage with no `lastTouch` movement). Sample Client at Proposal is the canonical case.
4. The latest `loops/_watchdog/` artifact — MISSED loops not yet fixed, and any `🟢 ACTIVATION TRIGGER MET` not yet acted on.
5. The latest `loops/eval-review/` artifact — FAILS with no owner response, and any **streak past threshold awaiting the Founder's promotion call** (`runtime/autonomy-matrix.md` ledger).
6. `runtime/proposed-holds.md` — calendar holds proposed but unconfirmed.
6b. **Referred-intro SLA (added 2026-07-21, `decisions/2026-07-21_connector-program-v11-strengtheners.md`):** companies in `crm/data.json` with a `referrer` (or `referredByCompany`) whose `referredDate` is set but with **no first touch logged** (no activity or deal `lastTouch` on/after `referredDate`) within **1 business day**. A connector whose intro goes stale stops referring — an SLA-blown intro **leads the Slack post ahead of everything else at equal age** (it's both revenue-touching *and* channel-trust-touching). The CRM's Intro Queue tab is the human view of the same data.
7. The counsel/launch gates (parked list): referral MLM + rep equity (`decisions/2026-06-30_*`), Care counsel gate, Conduit's 3 open decisions, Sample Product legal-before-public, the OtherVenture launch gate (`processes/launch-runbook.md`).

## Steps
1. **Reconcile the queue.** Start from the prior artifact: mark items CLEARED (evidence required — the draft is gone/sent, the deal moved, the decision file updated), still WAITING (age +1), or newly PARKED (only if a decision/instruction says so — cite it).
2. **Sweep for new items** from inputs 2–6. Every new item gets: what it is · whose action (almost always the Founder) · waiting since (the real origin date, not today) · the single next step.
3. **Rank the nag list** — age × stakes. Revenue-touching items (a stalled deal, an unsent proposal follow-up) outrank internal hygiene at equal age. Anything waiting **>7 days** gets a 🔴.
4. **Write the artifact** to `loops/open-loops/YYYY-MM-DD.md` (format below).
5. **Slack** — to `#yourco-jim`, signed "— Jim, YourCo Ops":
   - Open items exist → post the **top 5 by rank**, one line each: `🔴/🟡 <item> — waiting <n>d — next step: <one action>`. Lead with the oldest revenue-touching item.
   - Queue empty → `✅ Open-loops: queue clear.` one-liner (rare pre-launch; still post it — the empty confirmation is the point).
   - **Mondays only:** append the parked-list inventory (one line per parked item + which gate opens it), so parked never rots unseen.

## Output artifact format
```
# Open Loops — YYYY-MM-DD

## Cleared since last run
(item · how it cleared · days it waited — the loop's win column. "None.")

## The queue (waiting on a human)
| # | Item | Whose action | Waiting since | Age | Next step |
(🔴 = >7 days. Ranked age × stakes.)

## New today
(items that entered the queue this run. "None.")

## Parked by decision (inventory — not nagged)
(item · the decision/gate that parks it · what would unpark it)

## What I'd do differently next run
(Empty — for the Founder to fill)
```

## Watchdog triggers (escalate)
- Any revenue-touching item 🔴 (>7 days) **two consecutive runs** with no movement → lead the Slack post with it in bold; on Mondays, flag it for the briefing.
- The same item WAITING >21 days → propose a decision: act, delegate, or formally park it (a queue item that old is really an unmade decision).
- Queue reconciliation shows an item vanished without evidence of clearing → flag it (silently dropped ≠ done).

## Feedback capture
the Founder's "What I'd do differently" + any Slack reply in `#yourco-jim` (e.g. "stop nagging X, it's parked — see <decision>") is read next run and applied: the item moves to the parked inventory **with the citation**. No citation → it stays on the nag list. That friction is intentional.

## Pre-scale handling
Pre-launch the queue will be short and slow-moving — that's fine. The loop's value now is preventing exactly the Southern-Cut-style stall the audit found: one deal, quietly aging, nobody's artifact naming the number of days. Grade the honesty of the ages, not the size of the queue.
