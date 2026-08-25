# Client demo kit — show any prospect their employee, before they sign

A reusable, **config-driven** walkthrough. Fill in one file and you have a branded demo of what a prospect's digital employee would do — the give-first "see yours" asset, on sample data. Built from the Sample Client engagement and generalized so every future client gets one in ~15 minutes.

## What's here
- `config.js` — **the only file you edit.** Client name, brand color, use case, the approval items, the status-board jobs, the monthly report. Ships filled with Sample Client as the working example.
- `kit.js` — the shared renderer (CSS + builds each screen from the config). Don't edit.
- `index.html` · `approval.html` · `board.html` · `report.html` — thin shells that render the four screens.
- `demo-script.md` — a narrated click-path to read while you walk a prospect through it.

## Spin up a demo for a new client (3 steps)
1. **Copy** this `demo-kit/` folder into the prospect's engagement folder: `clients/<prospect>/demo-kit/`.
2. **Edit `config.js`** — only that file. Set `client`, `brand` (their hex color), `useCase`, `tagline`, then fill the `approval`, `board`, and `report` blocks with their sample data (their job types, their numbers, a realistic message or two). Tighten `steps` to the screens you're showing.
3. **Serve + present.** Add a launch config (copy the `yourco-demo-kit` entry in `.claude/launch.json`, point `--directory` at the new folder), open `index.html`, and walk `demo-script.md`. Resize to mobile for the approval screen.

That's it — no code edits, no per-client CSS.

## The four screens
- **index** — the hub: the whole setup end to end, linking the screens in order.
- **approval** — the one-tap screen the approver sees on their phone. Drafted message(s); if it's a payment, the amount shows **locked** (computed by code, not editable). Approve / Edit / Decline. This is the moat moment: *nothing reaches a customer without a human tap.*
- **board** — the "operated" view: every item in flight with its gates, a daily nudge list, and the week's metrics.
- **report** — the monthly outcome + reliability proof (0 sent without approval, money by code, uptime).

## When the config isn't enough
The config covers the universal shapes (approvals, a status board, a report). If a prospect's use case needs a screen the kit doesn't have, copy the bespoke reference at `clients/sample-client/prototype/` — it has a greenlit screen and a **runnable agent engine** (`agent.py` + `test_agent.py`) that drafts real messages and proves the money-math with a test suite. Use the kit for the visual walkthrough; use that prototype when you want to show the engine actually running.

## Rules
- **Sample data only — nothing is live, nothing sends.** Say so once up front; never imply a real customer was contacted.
- It's a pre-sale / discovery asset (the proof-led "see yours" play). Build it during discovery; it makes the proposal land because the prospect has already seen their employee work.
- Keep numbers believable for their business — a demo that overclaims hurts more than it helps.
