---
name: add-runtime-loop
description: Put a new recurring loop on yourco's 24/7 headless VPS runtime (systemd timer + claude -p). Use when a process should run on a cadence with no human — 15+ loops already follow this exact pattern.
---

# add-runtime-loop

## Canonical docs
`runtime/README.md` §"Adding another loop" (mechanics) + `runtime/agent-wiring-checklist.md` step 9 (governance).

## Steps
**Repo (commit + push):**
1. SOP — `processes/loops/<loop>.md`: inputs, method, output format, cadence, failure modes, **pre-revenue/empty handling** (loops must report "quiet" honestly, not fabricate motion).
2. Prompt — `runtime/prompts/<loop>.md`: short, points at the SOP, states what it may NOT do (no send, no delete). End with the standard footer: the loop-contract compliance line + the Step 0 learnings-domain line (copy the pattern from any existing prompt).
3. systemd — copy an existing pair in `runtime/systemd/` → `yourco-<loop>.service`/`.timer`; change `ExecStart`'s loop name + `OnCalendar` to a free slot (stagger — don't stack loops on the same minute).
4. Watchdog — add the loop + cadence to the table in `processes/loops/watchdog.md` so a silent miss gets caught.
5. Registry — sanction the prompt + timer in `runtime/agent-registry.json`.
6. Output home — the loop writes dated artifacts to `loops/<loop>/`; create it with a `_README` stub if helpful.

**Host (the Founder on the VPS):**
7. `sudo cp runtime/systemd/yourco-<loop>.* /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now yourco-<loop>.timer`
8. Smoke-test without waiting for the slot: `sudo systemctl start yourco-<loop>.service`, then check `journalctl -u yourco-<loop>.service` and `loops/_runtime/<loop>.log`.

## Gotchas
- **The #1 observed failure (melanie-briefing 3 weeks, aeo-geo ~1 month — both caught 2026-07-06):** steps 1–6 get committed and the host steps 7–8 never happen — the loop looks "built" in the repo but never runs, and without the step-4 watchdog row the miss is invisible. A loop is not done until `systemctl list-timers | grep <loop>` shows it scheduled on the VPS. If the Founder can't run the sudo step immediately, add it to Jim's open-loops queue — never assume it happened.
- `runtime/run-loop.sh` does `git pull` before and `commit`+`push` after every run — never edit the same file in Cowork and on the server simultaneously.
- If the loop needs a tool the gate doesn't allow, expand `allow` in the host's `~/.claude/settings.json` (safe tools only — never send/delete/pay). The repo copy is only a reference.
- Timer times are ET (host timezone is set to America/New_York); `Persistent=true` so missed runs fire on boot.
