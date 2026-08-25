---
name: log-build-session
description: Journal the TIME, the STEPS, and the cost of a build session for a client/prospect, so future builds are estimable from evidence. Invoke at the START of any session doing real build work for a `clients/<client>/` engagement, at each meaningful milestone during it, and at the END. Also use when anyone asks "how long will a build like this take?" — that question is answered by `--estimate`, never from memory.
---

# log-build-session

## Canonical doc
`loops/_build-journal/_README.md` (the journal + its honesty rules) and the tool itself,
`runtime/build_journal.py --help`. This skill is the *when and how*, not a second copy of the format.

## How this relates to `log-build-cost` — read this first, they must not drift
Two tools, one build, no overlap:

| | `log-build-session` (this) | `log-build-cost` |
|---|---|---|
| Captures | **time + process/steps** | **dollars** |
| Writes to | `loops/_build-journal/sessions.jsonl` (append-only log) | `clients/<client>/cost.md` (the ledger table) |
| Answers | "how long does a build like this take, and what does it consist of?" | "what has this engagement cost us?" |
| Owner of the roll-up | the next build's estimate | Charles, at monthly close |

**`--stop` is the bridge.** It prints the exact `cost.md` Ledger row for the session (right phase,
right columns, right Evidence marking) — so running this skill *satisfies* log-build-cost for that
session rather than duplicating it. `--append-ledger` inserts the row for you. Phases are the same
four (`discovery` / `build` / `tools` / `run`) — the tool enforces them; never invent a fifth here.

## When
1. **At the start of real build work** for a `clients/<client>/` engagement — before the first file
   is written, not after. A session started at the end is a guess about its own start time.
2. **At each meaningful milestone during it** — `--step` after finishing a distinct piece of work
   (data model done, engine wired, approval gate in, leak test passed). Steps are what turn the
   journal into a playbook; a session with a duration and no steps tells the next build nothing.
3. **At the end** — `--stop` with the self-reported cost.
4. **Whenever the estimate question comes up** — scoping a proposal, Polo pricing a band, the Founder
   asking "how long will this take?" — run `--estimate`, quote what it says, including a refusal.

**Does NOT apply to:** internal yourco work (loops, agents, the site) — that's
`finance/token_spend.md`, Charles's own log, not a client build.

## Steps
1. **Open the session** (Cowork/host — headless loops have no Bash):
   ```
   python3 runtime/build_journal.py --start <client> --phase <discovery|build|tools|run> \
       --kind "<estimation bucket>" --what "<one line: what you're building>"
   ```
   `--kind` is the bucket `--estimate` matches on later — reuse an existing one verbatim when the
   work is the same shape ("quote platform", "demo kit", "discovery + proposal", "console build").
   A new spelling of an existing kind splits the sample and weakens every future estimate.
2. **`--step "<what you just did>"`** at each milestone. Write the step as the *next* builder would
   need it ("mapped the Aspire export to quote-engine inputs"), not as a diary entry ("worked on
   quotes"). Steps time themselves — the gap to the previous mark is recorded.
3. **Close it**:
   ```
   python3 runtime/build_journal.py --stop --cost <your $ estimate> [--tokens N] --notes "<outcome>"
   ```
   Then take the printed ledger row and either pass `--append-ledger`, or paste it into the Ledger
   table in `clients/<client>/cost.md`. Either way, log-build-cost is now satisfied for this session.
4. **Commit** via `runtime/commit-scoped.sh` scoped to `loops/_build-journal/sessions.jsonl` (plus
   the cost.md if you appended) — never bare `git add -A`.

### Answering "how long will this take?"
```
python3 runtime/build_journal.py --estimate "<kind>"
```
Quote its output as-is, **including when it refuses**. "Two sessions on record — too few to
estimate; here's what they were" is a legitimate, useful answer to give the Founder or a prospect. Do not
convert a refusal into a number by averaging in your head — that's the exact failure the floor exists
to prevent, and it would put a fabricated build estimate into a proposal.

## Gotchas
- **Cowork/Claude Code sessions cannot auto-attribute tokens.** The self-report at `--stop` IS the
  capture mechanism — the same lesson `log-build-cost` was written for. Don't skip `--cost` because
  the number is rough; a rough `est.` beats a blank. Never pass `--metered` unless you are holding a
  console or invoice figure for that spend.
- **The org spend number attached to a session is context, not an allocation.** It is org-wide (every
  loop, every agent, both machines). Never present it as this build's cost, and never divide it.
- **A forgotten session is not a 14-hour build.** Past 8h, `--stop` refuses and asks for `--hours`
  (the real time worked) — answer honestly rather than reaching for `--accept-stale`; one inflated
  session skews the median for every future build of that kind. `--list-open` before you start, so
  yesterday's session isn't still hanging.
- **The journal is append-only.** Never edit or delete a line in `sessions.jsonl`. Fix a mistake with
  `--correct <session> --set key=value --why "..."` — the correction is a new event and the original
  stays visible. That's what makes it auditable.
- **Two sessions open at once** makes `--step`/`--stop` ambiguous; the tool refuses and asks for
  `--session <id>`. Prefer one open session at a time.
- **Backfills are marked and excluded** from hours medians. Backfilling from a cost ledger row is
  encouraged (it gives the estimator a real sample) — but never state hours you don't actually know
  just to make a backfill "count": leave `--hours` off and it will honestly read `unknown`.
- The journal is internal. Nothing in it — hours, steps, our cost — ever goes on a client surface,
  proposal, or invoice breakdown. It informs the price; it is never shown as the price.
