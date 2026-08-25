# rejections — the anti-library

`decisions/` records what was **chosen**. `learnings/` records what was **observed**. This folder records what was **rejected**, and — the load-bearing part — **the condition that would reopen it**.

## Why it exists
yourco runs an unusual number of idea generators: Brett weekly, Melanie's daily initiative loop, the advisory panels, source-watch, connector-spotter, tool-triage. Their rejects used to vanish into artifacts nobody re-reads, so the same idea came back months later with no evidence attached and one person re-adjudicated it from scratch. That is the highest-volume claim on the Founder's attention that produces nothing.

**A rejection is a trip-wire pointed at a non-decision.** It uses the *same* check grammar as `decisions/_TRIPWIRES.md` and is evaluated against the *same* live facts by the *same* engine (`dashboard/tripwires.py`) — so there is no second language to learn and no second set of facts that could disagree with HQ.

## The contract for idea loops
Before proposing, run the check and put one of two lines in the artifact:

```bash
python3 runtime/rejections.py --check "the idea, in one line"
```

- `not previously rejected` — nothing on file scored above the strong bar.
- `previously rejected <date> (<file>) because <reason>; what has changed since is <X>` — required on a strong hit.

**Re-proposing is allowed and expected.** The ledger does not veto; it makes a re-proposal carry evidence. An idea killed in June when there were zero clients is not the same idea in a five-client business — but somebody has to say which of those two it is.

## Entry format
One file per rejected idea, `YYYY-MM-DD_slug.md`. Scaffold with `python3 runtime/rejections.py --new "<idea>"`.

| Field | Required | Notes |
|---|---|---|
| `Proposed by` | ✅ | who/what raised it, and where |
| `Rejected` | ✅ | date + who killed it |
| `Why` | ✅ | the reason a future proposer has to answer. **Cite, don't restate** — a reason copied out of a decision is a fact in two places, and that is the #1 drift mode |
| `Revisit if` | ✅ | prose. The condition that would reopen it |
| `Check` | — | optional machine test. Write `` `_none — <why>` `` when it genuinely isn't measurable |
| `Check covers` | — | required whenever the check is a *partial* proxy — an uncaveated partial check turns a nuanced revisit trigger into a green light |
| `Review` | — | a date; past it the entry reads `due` |
| `Tags`, `Source` | — | |

## Verdicts
| Verdict | Meaning |
|---|---|
| `reopened` | the check fired — live data now satisfies the revisit condition |
| `due` | the review date has passed |
| `standing` | a revisit condition exists, nothing has fired |
| `unconditional` | **no revisit condition was written** — flagged, not accepted. A permanent veto whose author can't name what would reopen it hasn't finished being made |
| `error` | the check couldn't be evaluated — never read as "did not fire" |

## Honest limits
- **Matching is advisory.** Deterministic token overlap, no model. It is tuned to *over*-report near-neighbours and to demand the "what changed" line only on a strong hit, because a false "already rejected" suppresses a good idea — strictly worse than a re-proposal.
- **It cannot see rejects that were never written down.** The six seeded entries came from decisions and learnings that documented a rejection; everything killed in conversation before 2026-08-13 is not here and never will be.
- **Match quality tracks how richly the entry is written.** Token overlap has a real ceiling: a one-line `Why` with no `Tags` surfaces as a near-neighbour but may not clear the strong bar, while a properly-filled entry does. This is measured, not theoretical — `runtime/test_agentops.py` pins both behaviours side by side. **That is what `Tags` are for**: they are not decoration, they are the terms a future proposer is likely to use.

```bash
python3 runtime/rejections.py --list    # everything + live revisit status
python3 runtime/rejections.py --due     # only what reality has reopened
```
