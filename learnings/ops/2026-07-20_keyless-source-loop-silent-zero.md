2026-07-20 — A keyless-source loop reports "OK" forever: zero-signal artifacts must name which sources actually ran

Source: the Founder asked "should we create an agent for intent signals?" — investigation of `loops/sadie/` showed every July sweep (14+ runs, 07-01 → 07-20) wrote "0 signal(s) … across 2 verticals". The VPS log (`loops/_runtime/sadie-intent.log`) revealed why: **all three sources skipped every run** — `runtime/.youtube.env`, `runtime/.bluesky.env`, and `~/.yourco/reddit.env` were missing on the VPS. YouTube + Bluesky creds existed on the Mac only (never propagated); Reddit creds were never created anywhere. Sadie has never actually swept from the runtime — the zeros were structural, not market truth — yet every run logged `OK`, committed, and posted a normal-looking Slack digest.

Pattern: Two compounding failure modes. (1) **Cred wiring is per-machine, and the loop runs on the other machine** — a gitignored env file created during local development silently never reaches the VPS, and nothing checks. (2) **"Empty is a valid result" (the loop contract) is only honest if the artifact distinguishes "looked and found nothing" from "couldn't look"** — Sadie's board printed the skip reasons to a gitignored log while the committed artifact and Slack digest looked like a legitimate quiet market. A zero-streak also never trips anything: watchdog checks *fired*, eval checks *format*, nobody checks *yield*.

Implication:
1. **Any loop that collects from external sources must write source status into the committed artifact** — per source: ran (n results) / skipped (why) / auth-failed. An artifact claiming "0 signals from X+Y+Z" when X, Y, Z never executed fails the loop contract's verification term ("sources actually read").
2. **Wiring a credentialed source isn't done until it's verified on the machine that runs the loop** — `wire-credentialed-connector` must end with a live-fire check on the VPS, not the Mac.
3. **Add a zero-streak invariant** (consistency-check / watchdog): N consecutive zero-yield runs of a collection loop (suggest N=5) → flag "sources or market? verify sources first". A month of zeros should be impossible to miss.
4. When a signal-collection loop reads empty for weeks, suspect the plumbing before concluding the market is quiet.

Audience: Atlas/platform (ops, primary); Kolby (qa-eval — the yield-vs-format gap); Sadie/Reilly (their pipeline was dark all month); anyone invoking `wire-credentialed-connector` or `add-runtime-loop`.

Triggers: skill:wire-credentialed-connector, skill:add-runtime-loop, loop:source-watch, loop:sadie, zero signal artifact, missing api key, silent zero