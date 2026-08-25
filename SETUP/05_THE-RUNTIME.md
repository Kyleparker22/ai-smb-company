# 05 — The always-on runtime

> **Build step 05.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

## What it is

A VPS that runs the OS 24/7 with no human present. Hostinger, Ubuntu, Claude Code CLI, a git-synced
clone of this repo at `~/yourco-os`, and **systemd timers** firing loops on a schedule. Live since
2026-06-09. Access: `ssh user@your-vps` (Tailscale). Cheat sheet:
`runtime/phone-access.md`.

**The commands live in `runtime/README.md` §"One-time host setup".** This page is the why.

## The approval gate — the whole reason this is safe

The host's `~/.claude/settings.json` allows drafts, posts, and reads, and **denies send, delete, and
Bash**. That single file is what makes "always-on" acceptable:

- **Always-on ≠ auto-send.** Agents draft emails; nothing sends. Proven in production for months.
- **Bash is denied**, which is why loops cannot shell out and why step 04's "design for the output"
  rule exists.
- Reference copy: `runtime/headless-settings.reference.json`. ⚠️ The installed copy is **root-owned on
  the host** — a `git pull` does not update it, and neither does it update installed systemd units.

## How a loop actually runs

`runtime/run-loop.sh` is the wrapper around every loop:

1. Takes the repo lock so concurrent loops cannot race each other's git index.
2. Reads `runtime/prompts/<loop>.md` — the stable prompt.
3. **Appends** two injected blocks: Step 0 learnings retrieved by trigger, and the anti-library.
4. Runs `claude -p` with `--output-format json`, capturing per-run cost.
5. Writes a dated artifact, logs to `loops/_runtime/<loop>.log` (gitignored, host-local), commits and
   pushes.

⚠️ **The injection goes at the END, and that is deliberate.** A prompt's cache is valid only up to the
first token that differs, so content that changes run-to-run must never sit at the front. It was
prepended when first written and fixed 2026-08-24 —
`learnings/ops/2026-08-24_cache-stable-prompt-prefix.md`.

Every loop prompt also carries the shared contract `runtime/prompts/_loop-contract.md`: the
anti-spin/completion rules, Step 0 domains, and the honest-completion standard.

## The closed loop, which is the actual point

A scheduled task is not a loop. A loop is: **(a)** a schedule, **(b)** an artifact the next run reads,
**(c)** a feedback capture step, **(d)** a feed-forward step — patterns written to `learnings/` that the
next run reads as its Step 0 and adjusts to. Observe → write a learning → the next run reads it →
behaviour changes → observe again. Without (d) you have a cron job that produces reports nobody reads.


## Turning a loop on — the four commands

The full host setup is `runtime/README.md` §"One-time host setup". Once the box exists, arming one
loop is:

```bash
sudo cp runtime/systemd/<loop>.service runtime/systemd/<loop>.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now <loop>.timer
systemctl list-timers | grep <loop>          # confirm it is scheduled
```

⚠️ **The installed units are root-owned copies.** A `git pull` does not update an installed
`ExecStart` path — if you move or rename a script, re-install the unit or the timer will keep firing
the old path and fail silently.

**Done-when for this page is one timer firing unattended.** Do not move on until
`loops/<loop>/` contains a dated file you did not create by hand.

## Adding a loop

`.claude/skills/add-runtime-loop/`. The SOP is the method (`processes/loops/<name>.md`), the prompt is
what runs (`runtime/prompts/<name>.md`), the folder is what came out (`loops/<name>/`).

## What is running

~20 loops. **`runtime/agent-registry.json` is the canonical sanctioned list** — not any prose count,
including the one in `CLAUDE.md`, which drifts. The governance watchdog diffs against the registry
every Monday 07:45 ET, so an unsanctioned loop is caught rather than discovered.

`loops/_README.md` maps all 43 output folders and — importantly — the distinction between
`_underscore/` **stores** (written by tools) and plain-name **loop outputs** (written by scheduled
runs).

**One unit is not a loop at all: `yourco-heartbeat.timer`** (added 2026-08-25). Pure shell, no model
call, one line every 15 minutes into `loops/_health/heartbeat.jsonl`. It exists because a log can only
record what happened while the box was working, so **no log can ever record an outage** — availability
is computed as *beats received ÷ beats expected*, which makes a missing line the outage rather than a
hole in the evidence. `Persistent=false` deliberately: a catch-up run would back-fill the exact gap it
exists to expose. ⚠️ **It is committed but NOT yet enabled** — that is a host action:
`sudo systemctl enable --now yourco-heartbeat.timer`. Until it runs, `dashboard/uptime.py` reads
*unmeasured*, never 100%.

## Two operational facts that will bite you

- **Installed systemd units are root-owned copies.** Changing a script's path in git does not update
  `ExecStart`. Re-install the unit.
- **The runtime can go dark silently.** It has three times, on billing. `runtime/sleeptime.py` and the
  watchdog exist because of it; `loops/_watchdog/` is where liveness is actually reported.

## Done when

**a systemd timer has fired unattended and written one dated artifact your next run can read.**

If you cannot point at that, the step is not finished — do not move on.
