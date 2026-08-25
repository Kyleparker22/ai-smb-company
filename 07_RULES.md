# 07_RULES.md — how work gets done here

**This page is an index, not a copy.** Every rule below lives somewhere else and is quoted from there.
That is deliberate: a copied rule drifts from its original, and drift across duplicated surfaces is
this workspace's single most common failure. If you change a rule, change it **at its source** and
sweep every surface in the same commit.

**The one rule that governs all the others:** ⭐ **change-one-sweep-all.** Canonical facts are
duplicated across site pages, packets, specs, CRM metadata, `CLAUDE.md` and decisions. When you
change one, `grep` the repo for the old value and update every occurrence in the same commit.
Source: `CLAUDE.md` §How to work in this OS. Machine backstop: `runtime/consistency-check.py`.

---

## Where every rule lives

| # | The rules | Where they live | Enforced by |
|---|---|---|---|
| 1 | 7 working rules (change-one-sweep-all, closed loops, git, secrets, "the Founder sends; agents draft") | `CLAUDE.md` §How to work in this OS | read every session |
| 2 | 6 external-surface rules (no agent names, no public prices, white-label, sourced stats) | `CLAUDE.md` §External-surface rules | read every session |
| 3 | 21<!--#count: dirs .claude/skills/*--> repeatable procedures | `.claude/skills/` | invoked by name |
| 4 | The loop behaviour contract — anti-spin, honest completion, Step 0 | `runtime/prompts/_loop-contract.md` | all 27<!--#count: files runtime/prompts/[a-z]*.md--> loop prompts read it |
| 5 | The owner's rules + 12 core principles | `06_business-plan.md` | judgment |
| 6 | 78<!--#count: match runtime/consistency-check.py /^(# ── (?!report).+)$/--> machine checks | `runtime/consistency-check.py` | **automatic, Mon 07:40 ET** |

Plus the three records that are *not* rules but constrain what you may do:
**`decisions/`** (settled calls) · **`learnings/`** (observed patterns) · **`rejections/`** (the
anti-library — check it before proposing an idea).

---

## The rules that most often get broken

Ranked by how many times each has actually bitten, not by importance in the abstract.

**⭐ Change-one-sweep-all.** See above. Every incident below is a variant of it.

**the Founder sends; agents draft.** Anything going to a human outside yourco — text, email, Slack DM, a
link to a client — is produced as copy and handed to the Founder. Never send it.

**Contact address is `founder@yourco.example.com`.** Never `hello@`, never an OtherVenture address. This leaked
**six times** across site pages, sales collateral and an outbound HTTP header before it became
invariant #47. Nothing yourco may reference OtherVenture or OtherVenture2.

**Secrets never touch chat.** Transcripts persist on disk. Keys go straight into the gitignored env
file — see `.claude/skills/wire-credentialed-connector/`. A secret that reaches chat gets rotated.

**Never `git add -A`.** Multiple sessions share one clone; a bare `add -A` sweeps another session's
in-progress work into your commit and buries it. Use `runtime/commit-scoped.sh "msg" <paths>`.
*(This is also how 577 files entered the repo unnoticed inside a nightly backup.)*

**Local surfaces are served only by name** from `.claude/launch.json` — never guess a port.
Procedure: `.claude/skills/show-surface/`.

**Don't delete stale docs — `git mv` them to `_archive/`** and add a row to its `_README.md` saying
why and what superseded them.

---

## When you do X, update Y

| You did this | Then this must happen |
|---|---|
| Changed a canonical number or name | `grep` the repo and sweep **every** surface, same commit |
| Made a settled call | A dated file in `decisions/` — **with a `## Trip-wire`** naming what would reopen it |
| Noticed a repeatable pattern | An entry in `learnings/<domain>/` with `Triggers:` so it loads when relevant |
| Decided *not* to do something | An entry in `rejections/` with the condition that reopens it |
| Solved something reusable (3+ steps) | A skill in `.claude/skills/` — `.claude/skills/create-skill/` |
| Added a top-level folder | A row in `00_README.md` **and** `CLAUDE.md`'s folder map *(invariant-checked)* |
| Added a local server | An entry in `.claude/launch.json` with a unique port *(invariant-checked)* |
| Added a runtime loop | `.claude/skills/add-runtime-loop/` — prompt, timer, **and** `runtime/agent-registry.json` |
| Created or promoted an agent | `.claude/skills/wire-new-agent/` — 13 steps, half-done wiring is the known failure |
| Created or promoted an agent | **Also give it a number** — an entry in `runtime/agent-registry.json` `agent_metrics.agents` saying what it moves *(invariant-checked)* |
| Changed the north star | `dashboard/goals.json` `northstar` — the Founder's, and only the Founder's. Every `ladders` value in `agent_metrics` is a claim about that number |
| Closed a month | `finance/runway.md` **and** `finance/actuals.json` in the same pass *(invariant-checked)* |
| Did real client work | Log the spend: `.claude/skills/log-build-cost/` |
| Finished a session | `.claude/skills/daily-log/` → `daily-logs/` |
| Caught drift by eye | **Add an invariant** to `runtime/consistency-check.py` so it's never caught by eye twice |

That last row is the mechanism that makes this page shrink over time. A rule a human has to remember
is a rule that will be broken; a rule a machine checks is a rule that holds.

---

## Git

Two machines push to `main` — this Mac and the VPS runtime — each a separate clone, meeting at
GitHub (`yourco/yourco-os`, private).

- Always `pull --rebase` before pushing
- **Never** `git reset --hard`
- `loops/` artifacts are runtime-owned — prefer the runtime's copy on conflict
- Commit with `runtime/commit-scoped.sh`, never a bare `add -A`
- **Name the paths from what *you* edited, not from `git status`.** The tool is only as scoped
  as the list you hand it: `git status` shows every session's dirty files, so generating the
  list from it re-creates `add -A` one step removed. This happened on 2026-08-23 — a `run-loop.sh`
  move carried an unrelated date fix from a concurrent session into its commit.
- `processes/git-sync.sh` is the full-backup safety net only
- **Two scripts are allowed `add -A`, and only these two:** `processes/git-sync.sh` (above)
  and `runtime/run-loop.sh`, which commits whatever a loop wrote. `runtime/run-loop.sh` is safe because it
  holds the repo lock for its whole run and is the VPS's only writer while a loop is in
  flight — but the caveat is real: **edit a file over SSH while a loop fires and your edit
  lands inside that loop's commit.** Make VPS edits with the runtime paused.
- **Identity is enforced at the source, not by a remap.** Every commit in this repo is authored and
  committed by `the Founder <founder@yourco.example.com>` — verified across all 1,389 commits on `main`.
  There is no `.mailmap`: it was deleted 2026-08-23 after a full history rewrite normalised 406
  commits (2026-06-09 → 06-28) that had carried an OtherVenture address in their metadata. A remap only
  hides an identity from git's own tools — GitHub's web UI ignores it entirely — so the address was
  removed from the data rather than masked. **What holds it now:** `git config user.email` on both
  the Mac and the VPS, plus invariant #47, which scans every tracked file for a banned address.
  If a stray identity ever reappears in `git log`, the fix is the config on whichever machine wrote
  it — never a `.mailmap`, which would put the masking back.

⚠️ **`git stash -u` is the same trap as `add -A`.** The `-u` sweeps *untracked* files — including another session's in-progress work sitting in this shared clone. It bit on 2026-08-23: a stash taken to test whether a drift item pre-existed pulled three unrelated `Pre Build Ideas/` folders in with it. If you must stash to compare against HEAD, scope it to named paths (`git stash push <paths>`), and check `git stash show --stat` before popping.

⚠️ **Worktrees are a trap.** A side worktree is a separate checkout the nightly backup does not see.
27 commits and six days of client work were stranded in one for a week. If you make one, merge it
back the same day or don't make it.

---

## The honesty rules

These are not style preferences — they are the product. yourco sells reliability, so a number this
workspace cannot defend is worse than no number.

- **Refuse rather than estimate.** If the inputs don't support a figure, say what's missing instead.
  Every HQ panel works this way; `runtime/test_evidence.py` holds (run `python3 runtime/test_evidence.py`) assertions enforcing it.
  The one number and the nine KPIs are held the same way — `runtime/test_numbers.py`, (run `python3 runtime/test_numbers.py`) assertions, each pinning a refusal: no activity count standing in for an outcome, no missing input rendering as zero, no forecast off a rate of zero.
- **State a shortfall; don't apologise for it.** Name an error once, fix it, move on.
- **Surface bad news early** — hiding a problem is the breach, not the problem.
- **No fabricated endorsement.** The advisory-panel exercise simulates named real people for internal
  stress-testing. It may never be stated or implied externally as those people advising yourco.
- **Pre-revenue means pre-revenue.** n=0 clients. Nothing here may imply otherwise.

Source: `runtime/prompts/_loop-contract.md` §Honest completion · `06_business-plan.md` §core principles.
