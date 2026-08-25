# runtime/ — the always-on headless runtime

> **Status: LIVE REFERENCE** — how the runtime works. Read this before touching a loop. Verified 2026-08-23.

How YourCo's loops run 24/7 on the VPS. Decision + status: `decisions/2026-06-09_always-on-runtime.md`. Full setup: `processes/claude-code-setup.md`.

## Pieces
- **`runtime/run-loop.sh`** (repo root) — the per-loop runner. `runtime/run-loop.sh <name>` sources secrets + nvm, `git pull`s, runs `runtime/prompts/<name>.md` headless via `claude -p`, then commits + pushes any artifacts. Logs → `loops/_runtime/<name>.log` (gitignored).
- **`runtime/prompts/<name>.md`** — the agent prompt for each loop (short; points at the loop SOP in `processes/loops/`).
- **`runtime/systemd/`** — one `.service` + `.timer` per loop. Reference copies; installed to `/etc/systemd/system/` on the host.
- **`runtime/headless-settings.reference.json`** — reference copy of the host approval gate. Active file is the server's `~/.claude/settings.json` (machine-local so Cowork is unaffected).
- **`runtime/runtime-alarm.sh`** + **`yourco-runtime-alarm.{service,timer}`** — an **API-independent** failure alarm (hourly, pure shell + curl). Greps `loops/_runtime/*.log` for the latest FAILED run (incl. "Credit balance is too low") and posts to a Slack incoming webhook. It never calls the model, so it survives a dead credit balance — the one failure the Claude watchdog can't catch (it shares the same credits). Needs `runtime/.alarm.env` with `SLACK_ALARM_WEBHOOK=...`. Background: `learnings/ops/2026-06-18_runtime-silent-credit-death.md`.

## The evidence writers (added 2026-08-07)
The write side of HQ's **Evidence** door (`decisions/2026-08-07_evidence-door.md`). The dashboard
only ever reads; everything that records evidence lives here.
- **`ledger.py`** — the shared append-only JSONL store, extracted once so the four newer stores
  can't each invent their own half-correct version. Four properties it makes impossible to
  violate: monotonic seq (allocated under an exclusive `flock`, so concurrent loops can't
  collide) · never edited — **corrections are new events citing the original** · corrupt lines
  counted and surfaced, never swallowed · shared Brier/calibration scoring with a sample floor.
- **`trust_ledger.py`** — the trust ledger, the calibration market, and the **drill catalog**.
  `--backfill-loops` seeds actions from committed artifacts (idempotent); `--sweep` expires
  overdue drills to UNDETECTED; `--status` prints the whole picture. The `CONTROL_COST` table is
  the single place a human-minutes estimate may be declared, and every entry carries a written
  basis and a confidence — nothing is `measured` until somebody actually times it.
- **`dri_twin.py`** — the DRI twin: `--queue` lists real open decision points (Jim's queue + the
  Board), `--predict` records a call **before** the Founder makes it, `--resolve` scores it.
- **`drills/`** — deliberately induced faults against yourco's own OS, and whether it noticed.
  See `runtime/drills/README.md` — and note the naming: this is **not** `runtime/immune/`, which
  is the cross-client vaccination system. One manufactures failures, the other propagates the
  lesson from real ones.
- **`heartbeat.sh`** + `systemd/yourco-heartbeat.{service,timer}` — **runtime availability**
  (added 2026-08-25). One line every 15 minutes to `loops/_health/heartbeat.jsonl`; uptime is
  *beats received ÷ beats expected*, so **a missing line IS the outage** — a log can only record what
  happened while the box was working. Pure shell, zero API calls, so it survives the dead-credit
  failure that took the runtime down for three days in June and again in July. `Persistent=false` on
  purpose: a catch-up run would back-fill the gap it exists to expose. It does not commit per beat —
  beats ride the next loop's `git add -A`, plus an opportunistic self-push at most every 6h so a
  total outage still becomes visible when no loop is running. Read by `dashboard/uptime.py`.
  **Host step (the Founder):** `sudo cp runtime/systemd/yourco-heartbeat.{service,timer}
  /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now
  yourco-heartbeat.timer`. Until then the metric reads *unmeasured*, not 100%.
- **`test_numbers.py`** — 33 assertions over `dashboard/northstar.py` + `dashboard/kpis.py`.
  Pins the three ways a scoreboard gets dishonest: counting activity as an outcome, rendering a
  missing input as zero, and forecasting off a rate of zero. Also asserts neither module writes.
- **`test_evidence.py`** — 54 assertions, each pinning one honesty rule (unpriced work never
  becomes hours · silence scores as a miss · a 1-drill sample can't be a percentage · mixed
  and/or refuses · absence isn't zero · a perfect record still earns nothing on a gated class).
  Run it after touching any of the above.

Kept current by the weekly **`evidence-sweep`** loop (Kolby, Sun 16:30 ET, ahead of the 17:00
eval review) → `loops/_trust/<date>.md`.

## Finding things, and keeping documents honest (added 2026-08-24)

Three tools that answer questions *about the repo itself*. All three are deterministic and none of them
calls a model — `learnings/ops/2026-08-09_inference-only-where-judgment-is-needed.md` is explicit that
wrapping deterministic work in an LLM costs tokens and is less reliable.

`kb.py` — **search everything yourco knows.** Full-text across ~1,250 files in well under a second, and
the thing `grep` cannot do: every result is tagged and ranked by **reality level** (REAL · DOCTRINE ·
DECIDED · BUILT · DESCRIBED · RECORD · DEAD), so a confident hit in `Pre Build Ideas/` cannot read like
one in `clients/`. Refuses a stop-word-only query; reports a genuine miss as a miss.
```
python3 runtime/kb.py "connector override"
python3 runtime/kb.py "audit" --level real
```

`doc_claims.py` — **documents that declare their own checks.** A number in a doc carries its own
verification inline — the digits followed by an HTML comment reading `#count:` and a glob (see any
annotated line in `00_README.md` for the literal form; writing one out here would make this README
itself claim the count) — and every
backticked repo path in a live doc must resolve. It **never edits a document**: a wrong number is
reported, never silently corrected, because the number might be right and the glob wrong.
```
python3 runtime/doc_claims.py --list
```

`inbox_triage.py` — **routes `inbox/`, and never files anything.** Inventories what is waiting,
proposes a destination *with the signal that suggested it*, and prints `undetermined` rather than
guessing. Byte-identical copies of files already in the repo are reported as **duplicates to delete**,
never as something to route. Routing between `decisions/`, `learnings/`, `rejections/` and `offerings/` is judgment; an
auto-filer would manufacture the prototype-read-as-product confusion at scale. See `inbox/_README.md`.
```
python3 runtime/inbox_triage.py --dry
```

All three are covered by invariants in `consistency-check.py`.

## Global pause switch (stop all loops → save credits)
The Slack posting itself is free; the credit cost is the **loops running `claude -p`**. To pause them all at once — no sudo, no per-timer disabling:
```bash
# [VPS] pause every loop (runtime/run-loop.sh loops + sadie-intent): they fire but exit immediately, no model call
touch ~/yourco-os/runtime/.paused
# [VPS] resume
rm ~/yourco-os/runtime/.paused
```
`runtime/run-loop.sh` and `runtime/sadie-intent.sh` check this flag first and exit 0 (logged `PAUSED`, so `runtime-alarm.sh` doesn't false-fire). The file is **host-local + gitignored** (not synced), so it survives the per-run `git pull` and only affects this box. Timers stay installed — nothing to re-enable; deleting the flag resumes on the next scheduled fire. **Not paused by the flag** (stop separately if wanted, needs sudo): the Socket-Mode listeners (`slack-listener`, `telegram-listener` — idle-free, on-demand only), the web servers (CRM/dashboard/site-intake), Sample Product's `storm_*` publishers (Nick's product, not yourco notifications), and `runtime-alarm` (free; nothing to alarm on while paused).

## Updating an agent's docs/prompts (Cowork ⇄ runtime sync)
There is **one source of truth: this git repo.** You do **not** edit anything twice. The VPS is a git-synced clone — `runtime/run-loop.sh` does `git pull` before every scheduled run and `commit`+`push` after, and each run is a fresh `claude -p` whose entire state is repo files. So:
- **Doc / prompt content** (`runtime/prompts/<loop>.md`, `processes/loops/`, `04_agent_roster.md`, `clients/<agent>/`, `CLAUDE.md`, etc.) → **edit locally → commit → push.** The runtime picks it up on its next run's `git pull`. No separate "cloud" edit.
- **Two host-local exceptions** (not in git — these need a manual host touch, and only when you change behavior, not text):
  1. **Approval gate** — the active `~/.claude/settings.json` is machine-local (repo holds only the reference copy). Changing what an agent is *allowed* to do = edit on the host.
  2. **systemd timers/services** — installed to `/etc/systemd/system/`. Changing an agent's *schedule* or adding a new loop = host install + `daemon-reload` (see "Adding another loop" below).
- **Caution:** don't edit the same file in Cowork and on the server at once — you'll get a merge conflict. Make edits here, push, done.

## The approval gate (Step 6)
Lives in the host's `~/.claude/settings.json` `permissions` block, so **every** headless run self-gates — no per-run flags. Per the decided posture:
- **allow** (auto, no human): file Read/Write/Edit/Glob/Grep, Slack post, Gmail read + **draft** + **non-destructive organizing** (create/apply labels, archive = remove INBOX, mark-read; incl. `batch_modify_emails` for bulk relabel — all reversible).
- **deny** (must stay human): Gmail **send** / **delete** (incl. `batch_delete_emails`), and **Bash** (closes the "curl the send API to bypass the gate" hole).
- Anything not listed is blocked in headless mode (no one to prompt). Expand `allow` as loops need more *safe* tools; never add send/delete/pay.

> The Gmail OAuth token holds the broad `gmail.modify` scope (gongrzhe server requirement), so draft-only is enforced ONLY by this gate, not by scope. The `deny` list is load-bearing.

## One-time host setup (Step 5–6)
```bash
# 1. Match the roster cadence (ET) so OnCalendar times are ET
sudo timedatectl set-timezone America/New_York

# 2. Apply the approval gate (copy reference into the ACTIVE user settings)
cp ~/yourco-os/runtime/headless-settings.reference.json ~/.claude/settings.json
#   (or hand-merge if ~/.claude/settings.json already has other keys)

# 3. Make the runner executable
chmod +x ~/yourco-os/runtime/run-loop.sh

# 4. Install + enable the timer(s)
sudo cp ~/yourco-os/runtime/systemd/yourco-*.service ~/yourco-os/runtime/systemd/yourco-*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now yourco-monday-briefing.timer
systemctl list-timers | grep yourco          # confirm it's scheduled

# 5. Smoke-test the wrapper end-to-end without waiting for Monday
sudo systemctl start yourco-monday-briefing.service
journalctl -u yourco-monday-briefing.service --no-pager | tail -30
tail -40 ~/yourco-os/loops/_runtime/monday-briefing.log
#   -> expect: artifact written + committed/pushed, Gmail draft, Slack post, send NOT used
```

## Adding another loop
1. Write `runtime/prompts/<loop>.md` (point it at `processes/loops/<loop>.md`).
2. Copy the briefing `.service`/`.timer`, rename to `yourco-<loop>.*`, change `ExecStart`'s loop name and the `.timer` `OnCalendar` to that loop's slot (sales Mon 07:08, finance Mon 07:24, customer-health Wed 07:00, content Fri 07:00, etc.).
3. `daemon-reload` + `enable --now yourco-<loop>.timer`.
4. If the loop needs a *safe* tool not yet allowed, add it to the gate's `allow` list (never the dangerous ones).

## Notes
- Each run is a fresh `claude -p` — all state lives in repo files (the loops already follow this).
- `git pull` before / `commit`+`push` after each run keeps Cowork ⇄ server in sync. Avoid editing the same file in both at once.
- `Persistent=true` means a missed run (server reboot/offline) fires on next boot.

## The six panel builds (added 2026-08-13)
From `loops/_advisory/2026-08-13_ai-os-design.md`. Three point yourco's own instrumentation at the
client; three harden the OS itself. Endpoints on HQ; writers here.

- **`pregolive.py`** — pre-go-live simulation. Fires ~10 injected data states at a client agent and
  asserts it doesn't crash, doesn't invent numbers absent from its input, and **doesn't obey
  instructions hidden in that input**. A client opts in with `clients/<name>/pregolive.json`; no
  adapter reads **cannot-simulate**, which is a go-live blocker rather than a pass.
  **Model-free by construction** — outbound sockets are blocked for every state (`_NoNetwork`).
  The first version only *claimed* that and fired two live API calls, because the adapter calls
  Claude and falls back only when there is no key. It calls itself a **smoke test, not an eval
  set**, in its own output, so a pass can't be quoted as an eval.
- **`sleeptime.py`** — idle-capacity work: Step 0 digests per `learnings/` domain, bloat reporting
  (reports, never deletes), dashboard pre-warm. **Ships disarmed** (`--arm` or `YOURCO_SLEEPTIME=1`)
  and **the health gate runs first every time** — stale loops, a dark box, or $0 7-day spend and it
  refuses even when armed. Model-free, so a scheduling mistake cannot produce a bill. Today it
  correctly refuses: 17 of 25 tracked loops are stale.
- **`client_tripwires.py`** — the client's own operating decisions, watched for expiry against
  *their* measured numbers (`clients/<name>/facts.json`). Format + worked examples in
  `clients/_yourco-template/client-tripwires.md`. Uses **the same check grammar** as
  `dashboard/tripwires.py` — one dialect, one set of refusals. A check naming a fact nobody
  measures reads `unmeasured` and **never fires**; a `{fact}` placeholder with no value stays
  visibly unfilled rather than resolving to a blank.
- **`counterfactual.py`** — the client's business as it would be running without the OS, projected
  from a discovery-time `baseline.json` and compared to actuals. Every output carries
  `isModel: true`; every metric states its assumption; a metric with no stated trend is held flat
  **and says so** (a custom assumption never replaces that disclosure); a metric measured today but
  never baselined is **excluded and named**, never assumed flat — that would invent a gap.
- **`../dashboard/security_model.py`** — the control set read from the live config rather than
  written by marketing: the deny-list, every action's rung, and which drill last tested it. A
  control with no drill behind it reads **untested**, never proven — that distinction is the
  page's whole credibility. `EXTERNAL_OK = False` until the launch-gate clears.
- **Agent expiry** — `runtime/agent-registry.json` §`agent_review` (review policy, sponsors,
  exemptions) + the `retire` section of `dashboard/vacancies.py`. Proposes only. Output is read
  from three evidence sources — loop artifacts, the trust ledger, and commits under
  `agents/<slug>/` — and the evidence window (post-2026-08-07) is disclosed, so a proposal means
  "nothing since 08-07", not "never".

Tests for all six: `python3 runtime/test_evidence.py` (179 assertions).
