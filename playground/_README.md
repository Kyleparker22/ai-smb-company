# The Playground — practice yourco without touching yourco

> Built 2026-08-07 (the Founder): *"a place to build and test things — practice — to see what they look
> like or how they function before pushing anything live, and enter test data to see how things
> flow. It should also incorporate all of our AI agents."*

```bash
python3 playground/seed.py            # build a synthetic yourco (default: 15 live clients)
./playground/run.sh                   # CRM :8890 · HQ :8891 · Connector Console :8892
./playground/run.sh stop
python3 playground/seed.py --wipe     # delete it
```

Or from Cowork: `preview_start` with `yourco-playground-hq`, `yourco-playground-crm`, or
`yourco-playground-connector-console`.

**After changing any `crm/` or `dashboard/` module, run:**

```bash
python3 playground/check_isolation.py
```

---

## The one idea: same code, different data

`YOURCO_DATA_ROOT` is the whole mechanism. Set it, and `crm/server.py` and `dashboard/server.py`
read and write `playground/data/` instead of the repo. **Code and HTML are never copied.**

That is a deliberate choice over a forked sandbox. A copy would drift the day either side
changed — the "change one, sweep all" failure `CLAUDE.md` names as the #1 cross-session bug —
and you would end up diffing two CRMs. Here there is exactly one CRM, so the playground is
always showing you the *current* product. The cost is that you can't break the UI
experimentally in the playground; for that, use a git worktree.

```
YOURCO_DATA_ROOT unset  →  live      (byte-identical to before this existed)
YOURCO_DATA_ROOT set    →  sandbox
```

## What makes it safe

| Guard | Where |
|---|---|
| Git sync **force-disabled** whenever the var is set — not defaulted off, overridden | `crm/server.py` `GIT_SYNC = … and not PLAYGROUND` |
| `playground/data/` is gitignored — synthetic records can never be committed | `.gitignore` |
| A fixed, un-dismissable **PLAYGROUND** banner + `⚠ PLAYGROUND` in the browser-tab title | injected via `/api/mode` |
| Every CRM record carries `example: true`; `meta.note` says SYNTHETIC | `seed.py` |
| Agents run with 15 outward-facing tools **denied** and `cwd` inside the sandbox | `agent.py` `DENY` |
| **Ghost refuses to run** in the playground | `crm/ghost.py` `compute()` — in the module since 2026-08-24, so the CLI and the API both refuse; see below |
| Console logins + rendered consoles land in the sandbox, not the repo | `YOURCO_CONNECTOR_AUTH_DIR`, `_connector-consoles/` |
| A machine check proves live files are byte-identical after a seed | `playground/check_isolation.py` — **run every Monday by `runtime/consistency-check.py`** since 2026-08-24; before that, eleven modules said "Enforced by" it and nothing ran it |

**Why Ghost refuses.** The Ghost insight reconstructs past board states from the git history of
`crm/data.json`. Playground data is untracked, so it has no history — and falling back to the
*live* file's history would render real past deals inside the sandbox as if they were synthetic.
Wrong answer, confidently displayed, is the failure mode this OS cares most about. It returns an
explanation instead.

⚠️ **Until 2026-08-24 that refusal lived only in `crm/server.py`'s route.** The API refused correctly;
`YOURCO_DATA_ROOT=… python3 crm/ghost.py` did not — it replayed the **live** repo's history and
printed real deal velocity, which is precisely the outcome the paragraph above says must never
happen. The check now sits in `ghost.compute()`, so every caller inherits it and the route holds the
only remaining copy of nothing — it defers to `ghost.PLAYGROUND_REFUSAL`. A guard only one entry
point applies is a guard the next entry point will not have.

## What's seeded vs snapshotted

- **Seeded (invented):** the CRM, engagement folders under `clients/`, `finance/revenue.md`,
  dashboard state, loop artifacts. Every name is fictional. Deterministic — same `--seed`,
  same world, so a bug is reproducible.
- **Snapshotted (copied verbatim at seed time):** the OS's own reference docs that the Board
  reads — counsel gates, the launch-gate, the three backlogs, `agent-registry.json`, the loop
  prompts and timers. Faking those would make the Board meaningless. Reseed to refresh them.

```bash
python3 playground/seed.py --clients 40     # what does HQ look like at 40 clients?
python3 playground/seed.py --clients 0      # the empty state, honestly
python3 playground/seed.py --seed 99        # a different world, same shape
```

## The agents

```bash
python3 playground/agent.py --list                # 25 prompts + their cadences
python3 playground/agent.py --show customer-health # the prompt + its inputs — no API call, no auth
python3 playground/agent.py --run  customer-health # the real thing, against synthetic data
```

`--run` is a genuine `claude -p` invocation — the same one the VPS makes — with three changes:
data root points at the sandbox, `cwd` is the sandbox, and every send/post/publish tool is
denied. The agent is told up front that it is in a playground and that **naming what the
synthetic data is missing is itself a useful output** — a gap there is a finding about the
seeder or the prompt.

**Two blockers stand between you and a live run, and `--run` names whichever it hits:**

1. **Headless auth.** `claude -p` spawned as a subprocess has no session of its own. On this
   Mac it currently returns *"Not logged in."* Fix: run `claude` once in a terminal and complete
   `/login`. (The VPS already has this.)
2. **API balance.** The org's Anthropic balance is exhausted — spend fell to $0.83 across
   2026-08-01..08-06 against an ~$8/day baseline, and every model loop has been dark since
   ~08-04. Fix: top up + enable auto-reload.

`--show` works regardless of both. That is deliberate: the playground should still teach you
something on a day the API is dead.

## What this is not

- **Not the sandbox test-tenant.** `processes/sandbox-test-tenant.md` is an yourco-owned
  Google/Twilio tenant for proving a *client's* downstream actions actually fire. Different
  problem, still valid, unaffected by this.
- **Not a code staging environment.** Use a git worktree to break things.
- **Not connected to anything.** No client, no prospect, no inbox, no Slack.

## The leak this already caught

The first version of the seeder wrote **synthetic connectors into the real `crm/data.json`**.
Not a near-miss — it happened, and it was reverted from git.

The cause was a split brain. `connector_training.py` had been pointed at the sandbox, but the
module it delegates its writes to — `connector_writes.py`, the *single locked write path* —
still resolved `os.path.join(HERE, "data.json")`. Reads came from the sandbox; writes went to
production. **That is strictly worse than having no sandbox**, because it looks like it works.

Twelve modules across `crm/` and `dashboard/` had the same pattern, including
`melanie.write_mirror`, which is why `crm/data.js` was also being rewritten. Fixing only the
one that bit us would have left eleven loaded guns, so the rule is now enforced by machine:

> **HERE is CODE. Data files resolve under `DATA_DIR`.**

`check_isolation.py` fails the build if any `crm/` or `dashboard/` module resolves a
`.json`/`.jsonl`/`.js` file off `HERE`, and — the test that would actually have caught it —
hashes six guarded live files before and after a full seed and fails if any byte moves.

## Known gaps

- The seeder writes no `repApplicants`, `graph`, or `dispatch` data, so the CRM's Lineage and
  Warm-path views are empty in the sandbox rather than wrong.
- `--run` on an agent still needs headless auth + a funded API balance (see above).
