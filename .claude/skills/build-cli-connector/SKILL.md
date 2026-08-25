---
name: build-cli-connector
description: Build a small CLI that wraps a service yourco needs when no MCP server exists (or the only MCP is remote/OAuth and can't run headless). Use when an agent or loop needs to read from or write to a program — an API, a SaaS tool, a local binary — and there is nothing in `.mcp.json` for it.
---

# build-cli-connector — reach a program that has no MCP

## When
An agent or loop needs a service and `.mcp.json` has nothing for it. Also correct when an MCP *exists*
but is **remote/OAuth-only** (Canva, DocuSign, Monarch, Granola, Vibe) and therefore cannot run on the
VPS — `runtime/connectors.md` lists these.

**NOT for:** a service that already has a self-hostable stdio MCP (migrate it instead — `connectors.md`
§"How to migrate ONE connector"), or a one-off lookup you will never repeat (just do it in Cowork).

## The thing to understand before you write any code

**A headless loop cannot run your CLI.** The approval gate denies Bash (`runtime/headless-settings.reference.json`),
and that is deliberate — it is the control that makes always-on safe. So a CLI invoked by the agent
works in Cowork and silently does nothing in production.

**Design for the output, not the invocation.** The agent does not need to run the tool; it needs the
tool's answer. Three delivery paths, in order of preference:

| Path | How it reaches the agent | Use when |
|---|---|---|
| **1. Artifact** (default) | a systemd timer runs the CLI on its own schedule → it writes a dated file → the loop *reads* the file | almost always. This is how every `runtime/*.py` already works. No Bash needed by anyone. |
| **2. Wrapper injection** | `runtime/run-loop.sh` runs the CLI **before** `claude -p` and injects stdout into the prompt | the loop needs *fresh* data at run time. Proven — this is how Step 0 learnings and the anti-library reach every loop (`run-loop.sh:92,104`). Read-only, must be fast, must fail soft. |
| **3. Wrap it as an MCP** | a real stdio server in `.mcp.json` | only when an agent genuinely needs to *choose* calls interactively. Biggest job, and it widens the unattended attack surface — `connectors.md` is explicit that migrating every connector headless is **not** the goal. |

If you find yourself wanting the agent to shell out, you have picked the wrong path.

## Steps

**Before code — the two gates**
1. **Compliance check (Rafi).** Read the service's *current* API/data terms for (a) commercial use and
   (b) feeding content to an LLM. Several major platforms forbid one or both on free tiers — Reddit and
   X are confirmed (`learnings/ops/2026-06-11_platform-api-terms-gate.md`, `agents/rafi/reddit-api-assessment.md`). A
   ToS-violating scraper is an auto-skip, not a design problem. Cite the clause and the date read.
2. **Pick the path** from the table above and say which, in the file's own docstring. A CLI whose
   delivery path was never chosen is the one that turns out to be unreachable in production.

**Repo side (any session)**
3. **Write it in `runtime/<service>_cli.py`**, starting from `template.py` in this skill folder. Rules
   that are not optional here:
   - **No model calls inside the tool.** It fetches and formats; judgment stays with the agent reading
     the output (`learnings/ops/2026-08-09_inference-only-where-judgment-is-needed.md`).
   - **`--dry` and `--json`** on every tool. `--dry` must make no write and no billable call.
   - **Refuse rather than guess.** No data is a real answer — print it and exit non-zero. A tool that
     invents a plausible empty result is worse than one that fails.
   - **Reads and writes are separate subcommands**, and anything that sends, posts, deletes, or spends
     requires an explicit `--commit` flag. Default is always the safe verb.
4. **Secrets → the gitignored env file** — `runtime/.<service>.env`, matching the files already
   there (`.slack.env`, `.twilio.env`, `.yelp.env`), per `.claude/skills/wire-credentialed-connector/`.
   ⚠️ **The shape matters:** `.gitignore` matches `*.env`, so `runtime/.stripe.env` is ignored and
   `runtime/.env.stripe` is **not** — the reversed form commits the credential. Confirm with
   `git check-ignore -v <path>` before writing a single character of the secret into it. Never in
   the source, never in a prompt, **never pasted into chat** — a secret that reaches a transcript gets
   rotated. Read them with `os.environ`; fail with a message naming the missing key and the file it
   belongs in.
5. **Write the artifact** (path 1) to `loops/_<service>/<YYYY-MM-DD>.md` and give that folder a
   `_README.md` saying what writes it and what reads it.
6. **Document it in `runtime/README.md`** — the convention there is that a new capability gets a short
   section with its usage line and its reasoning. Three tools were added on 2026-08-24 without this and
   it had to be caught by audit.
7. **Add a live-check row** to `runtime/connectors.md`'s table: service · env keys · kind · the exact
   call that proves it works. An untested connector reads identical to a working one.

**Host side (VPS — the Founder runs these, label every block [VPS])**
8. Put the credential in the runtime user's env file; **do not** commit it.
9. If path 1: add the `.service`/`.timer` per `.claude/skills/add-runtime-loop/`, then
   `sudo systemctl daemon-reload && sudo systemctl enable --now <unit>.timer`.
   ⚠️ systemd units are **root-owned copies** — a `git pull` does not update an installed `ExecStart`.
   Changing the script's path means re-installing the unit.
10. Smoke-test headless and confirm the gate still denies what it should.

## Gotchas
- **Building for path 3 by reflex.** An MCP is the biggest job and usually the wrong one. Ask what the
  agent needs to *know*, not what it needs to *call*.
- **`cmd | tail` hides the exit code.** A pipeline reports its last stage, so a failed fetch piped
  anywhere exits 0 and reads as success. Verify the *effect* — the artifact's contents — not the
  invocation (`learnings/ops/2026-08-24_pipe-to-tail-hides-exit-status.md`, which cost real time twice
  in one day).
- **Wrapper injection that fails hard kills the loop.** Path 2 must be `|| VAR=""` and non-fatal: the
  loop still runs with a degraded prompt. See `run-loop.sh:92`.
- **Rate limits and cost.** A timer that polls every five minutes is a bill and a ban. Pick the slowest
  interval that answers the question, and log what a run costs if it is billable
  (`.claude/skills/log-build-cost/`).
- **Untested = unproven.** Do not write "live" in `connectors.md` until the live-check call has actually
  returned. The security-model panel reads a control with no test behind it as *untested*, never proven.
- **Client credentials are per-client**, in that client's own gitignored store (Sample Client's pattern in
  `connectors.md`), never in yourco's shared env.

## Canonical docs
`runtime/connectors.md` is the truth for what is reachable headless vs Cowork-only and carries the
live-check table. `.claude/skills/wire-credentialed-connector/` owns the secret-handling half;
`.claude/skills/add-runtime-loop/` owns scheduling. This skill is the delta between them: **choosing the
delivery path, and writing a tool that refuses rather than guesses.**
