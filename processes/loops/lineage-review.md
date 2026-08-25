# Lineage-review loop — is each agent still mirroring the right expert?

> **Status: LIVE** (repo side) — timer install pending on the VPS. Owner: **Brett**.
> Added 2026-08-23 to close a gap found by measurement: 26 of 27 agents name a real authority they
> mirror, and **nothing had ever re-examined one.**

## Why this exists

Every yourco agent is grounded in a named practitioner — Bird mirrors Jason Lemkin on land-and-expand,
Kolby mirrors Hamel Husain and Shreya Shankar on eval, Polo mirrors Madhavan Ramanujam on pricing. That
lineage is doing real work: it gives each agent a methodology to be judged against instead of a vibe.

But it was **frozen**. Measured 2026-08-23: agents learn *how they run* (53 entries in `learnings/`,
read at Step 0 by every loop) and do not learn *what they know*. Domain currency belonged to exactly one
agent — Brett — company-wide, and no loop had ever asked whether an agent's mirrored authority was still
the right one. If Ramanujam's thinking on pricing moved, or a better authority emerged on eval, no part
of this OS would notice.

Giving 27 agents their own source-watch would be absurd. **One quarterly review, by the agent who
already watches the outside world, is the proportionate answer.**

## Cadence
**Quarterly — second Monday of Jan/Apr/Jul/Oct, 09:45 ET.** Deliberately a week after Polo's pricing
review (first Monday 09:15) so two quarterly loops don't land in the same morning.

## Inputs
- `04_agent_roster.md` §"Expert lineage (who each agent mirrors)" — the 27-row table, the subject
- Each agent's `agents/<name>/_README.md` §Lineage — the long-form claim
- `loops/source-watch/` — what Brett has already seen this quarter; do not re-derive it
- `learnings/advisor/` + `learnings/strategy/` — Step 0
- `rejections/` — an authority previously considered and declined is **not** a fresh idea

## Method
For each of the 27 agents, in roster order:

1. **Is the named authority still the right one for this function?** Not "is it famous" — is it what
   yourco's version of that job should be judged against.
2. **Has their thinking materially moved** since the lineage was written (most were set 2026-06-10)?
   A new book, a reversal, a public correction. *Silence is a valid finding.*
3. **Has a better authority emerged** for that function?

Then classify each agent into exactly one bucket:

| Verdict | Meaning |
|---|---|
| `holds` | Still right, nothing material moved. **Expect most agents here most quarters.** |
| `moved` | The authority is still right but their thinking changed — say what changed and what it implies |
| `replace` | A better authority exists — name it, name what it buys, name what is lost |
| `unverifiable` | Could not check within the compliance bounds. Say so; never infer. |

## Output
One dated artifact: `loops/lineage-review/YYYY-MM-DD.md`, containing:

- A one-line headline: *"N of 27 hold · N moved · N replace proposed · N unverifiable."*
- **Proposals only**, one short block each, for every non-`holds` agent: current lineage → proposed
  change → the evidence → what yourco would do differently as a result.
- The full 27-row verdict table, so a `holds` is a recorded judgement rather than an omission.

## Hard constraints
- **Propose only. Never edit an agent's docs.** The lineage lives in `04_agent_roster.md` and in each
  `agents/<name>/_README.md`; changing either is the Founder's call, applied by hand. An agent that can rewrite
  its own definition is not reviewable.
- **Check `rejections/` before proposing an authority**, and state either "not previously rejected" or
  the file plus what has changed since.
- **No sends, no publishing, no external contact.** Research and write.
- **Never claim a change you cannot cite.** "Ramanujam published X in 2026" needs the X.

## Failure modes / empty handling
- **A quiet quarter is the expected result, not a failure.** If all 27 hold, write that: one line, the
  table, done. A review that proposes something every quarter is pattern-matching, not reviewing.
- **Do not manufacture churn.** Replacing an authority has a real cost — every doc citing the old one
  drifts — so `replace` needs to clear a higher bar than `interesting`.
- If the roster's lineage table and an agent's `_README.md` disagree, that is itself a finding: report
  the mismatch rather than picking one.
- Pre-revenue reality: yourco has **zero clients**. An authority whose advice only applies at scale
  should be flagged as such rather than treated as currently actionable.
