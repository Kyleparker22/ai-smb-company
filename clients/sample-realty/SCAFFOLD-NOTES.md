# Scaffold notes — what's done vs. what's left

This engagement was **scaffolded from the Audit** by `runtime/scaffold_engagement.py`. Roughly 80% of the setup is done; the remaining 20% is the part that *can't* be 1-clicked — and that part is the moat.

## ✅ Done by the scaffolder (the "1-click")
- Client folder cloned from `_yourco-template` (discovery/build/eval/go-live/cost docs, client-console, demo-kit).
- `01_discovery.md` pre-filled from the Audit diagnosis (bottlenecks, the first build, the roadmap).

## 🔧 Kimi finishes (human + build — NOT 1-clickable, by design)
- **Integration** into the client's actual tools/tenant (their CRM, calendar, phone, email) — every client is different.
- **Eval** against *their* success criteria — the harness that proves it works before it goes live.
- **The approval gate** — what's human-approved vs. autonomous, per this engagement.
- **The 48-hour build + go-live** — `processes/discovery-to-48h-build.md`.
- Provisioning (Janice): tenant access + the employee's mailbox.

> The scaffolder gets you to a running start; reliability is still earned per client. That's intentional — the part we *don't* automate is exactly what clients pay yourco to own.
