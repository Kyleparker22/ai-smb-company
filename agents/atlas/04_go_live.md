# Atlas — Go-Live Note

> Atlas's own go-live record (the dogfood deployment: YourCo running Atlas on YourCo). Written by Atlas, signed by the Founder.

## What's live
- **The Monday briefing loop** — fires Mon 07:55 ET on the always-on runtime, headless, self-gating, auto commit/push. First production run: week of 2026-06-08. Proven in production.
- **The runtime watchdog** — Atlas's "who watches the watchers" check (Mon 08:15 ET), confirming the scheduled loops fired (`processes/loops/watchdog.md`).
- **Ops synthesis / BI** — Atlas reads the loop artifacts + David's pipeline + Charles's finance into the Monday briefing and the dashboard (`/dashboard/`).

## How it went live
Per the always-on runtime migration (`decisions/2026-06-09_always-on-runtime.md`): VPS + Claude Code + git-synced repo + systemd timers + the host approval gate (drafts/posts/reads allowed; send/delete/Bash denied). Atlas was the first loop migrated and the proof that "always-on ≠ auto-send."

## Status
🟢 **Live since 2026-06-09** (runtime v0). Briefing + watchdog firing weekly. Email identity `contact@yourco.example.com` to be provisioned. Health + cost rollup feeds the dashboard.

## Sign-off
- the Founder: ☐ (confirms the briefing + watchdog are landing usefully each week — the "What worked / what I'd do differently" lines on the artifacts are the feedback loop.)
