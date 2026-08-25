# loops/melanie-briefing/ — Melanie's daily morning briefing

One dated artifact per run (`YYYY-MM-DD.md`). The runtime loop `melanie-briefing` (prompt: `runtime/prompts/melanie-briefing.md`, timer: `runtime/systemd/yourco-melanie-briefing.timer`) fires **weekday mornings ~07:45 ET**: Melanie reads the live CRM + dashboard data, writes the Founder's personal "here's your day" briefing in her voice, drops it here, and **posts it to Slack** (`#all-yourco` by default — repoint to a DM or a `#daily` channel as you like).

This is the "it finds you" push: the same briefing Melanie gives when you open the HQ dashboard, delivered to Slack before you open anything. Text-only (the spoken ElevenLabs voice lives on the dashboard). Personal/daily — distinct from Atlas's weekly strategic Monday briefing in `loops/monday-briefing/`.

**Status: LIVE as of 2026-07-06** — timer installed + enabled on the VPS (verified via `systemctl list-timers`); first fire **Tue 2026-07-07 07:45 ET**. It's also in the watchdog roster now, so a future silent stall gets caught.

*History:* staged 2026-06-13 but the go-live host step (`systemctl enable --now`) was skipped, so it sat written-but-never-run for ~3 weeks, invisible because it also wasn't in the watchdog table. Diagnosed 2026-07-06 by the dashboard's loop-health derivation. Lesson (feeds the add-runtime-loop skill): a loop isn't "built" until the host step is done AND the watchdog row exists.

Uses the already-live, gate-approved Slack-post capability, so no new keys. Run on demand any time with `./runtime/run-loop.sh melanie-briefing`.
