# Cross-session drift: facts change in one surface and rot in the others

**Observed (2026-07-05/06, by the Founder, repeatedly):** parallel sessions update a canonical fact in one place
and the other surfaces keep the old value — commission tiers lived at three different values at once
(one-pager v0 3/5/10 · spec examples 15/20 · locked v1 10/12.5/15); "net-30" survived after the 2nd-Friday
cadence was locked; the video ledger stopped at v6 while v10 was live; pricing never got the locked tier
names; a whole fix-set sat uncommitted and invisible to every other session.

**Why:** the repo is the only shared state between sessions, and canonical facts are hand-duplicated
across surfaces (site · packets · specs · CRM meta · CLAUDE.md). Nothing forced propagation or checked
coherence, so every parallel writer created drift a human had to catch by eye.

**How to apply (every agent, every run):**
1. **Change-one-sweep-all** — before committing a changed fact, grep the repo for the old value and update
   every surface in the same commit (rule now in CLAUDE.md §How to work).
2. **Commit before you stop.** Uncommitted work does not exist to other sessions or the VPS.
3. **When drift is caught by a human, encode it** — add the invariant to `runtime/consistency-check.py`
   (Mon 07:40 watchdog → `loops/_consistency/`). Human catch = one-time; invariant = forever.

Triggers: skill:log-decision, changing a canonical fact, consistency check, updating a price, updating a cadence, sweep all surfaces
