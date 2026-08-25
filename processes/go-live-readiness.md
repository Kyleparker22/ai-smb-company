# Go-Live Readiness Plan

**Goal:** build everything internally over the next few weeks so go-live (company + website + outreach + delivery) is a smooth, fully-automated switch-flip — not a scramble. Decided 2026-06-10: no deploy, no outreach sends until the full launch; until then, **build + stage + test everything.**

**Owner:** the Founder (conductor); per-workstream agent owners below. Living doc — update status as workstreams complete.

## Status legend
✅ ready · 🟡 in build / staged · 🔴 not started · ⏳ blocked on an external gate

## Workstreams

| # | Workstream | Owner | Status | What's left before go-live |
|---|---|---|---|---|
| 1 | **Always-on runtime / infra** | Kemba (the Founder holds) | ✅ live | **9 loops armed** on host (sales/finance/briefing/watchdog/content + Luka brand-audit + Polo pricing-review, installed 2026-06-10) + Jim daily desk built. Connectors Slack/Gmail/Calendar, approval gate, git-sync. Left (optional): connect **Vibe** (sourcing); fold homepage onto `site.css`. |
| 2 | **Website** | Webb | 🟡 staged | yourco.com v2 + getteamyourco.com landing built, Luka-passed, ported. Left at launch: **deploy** (Vercel + DNS), homepage CSS unify, retire/keep `diagnostic.html`. |
| 3 | **Outreach engine** | Reilly | 🟡 / ⏳ | 20-lead landscaping batch sourced + staged. Gated on warmup (~June 22) + 10DLC (escalated). Left: finalize batch, **email-only-vs-SMS** decision, batch approval, send infra confirmed. |
| 4 | **Demos** | Reed | 🟡 | ✅ Landscaping Email-2 demo **published + approved** (campaign gate met; GIF preview auto-generated in Instantly at send). Left (optional, needs the Founder creative input): produce the scripted **generic founder/exec-ops demo** ("Atlas: The Monday Briefing") — better fit for the website homepage + non-landscaping outreach. Per-vertical demos: defer until a vertical is targeted. |
| 5 | **Delivery rails** | Janice → Kimi (not built; the Founder holds) | 🟢 rails ready | **Built 2026-06-10:** `yourco-template` scaffold (`clients/_yourco-template/` — discovery/build/eval/cost/go-live) + onboarding runbook (`processes/onboarding.md`, Janice) + build playbook (`processes/discovery-to-48h-build.md`, Kimi). A signed deal now has a complete path: clone → onboard → 48h build → go-live → iterate. Left: the Janice/Kimi *agents* (trigger-gated on a real deal); the per-engagement Vapi/Twilio build happens at delivery time. the Founder runs the rails until the agents exist. |
| 6 | **Legal / contracts** | Ray (not built) | 🟢 drafts ready | **Built 2026-06-10:** engagement agreement + mutual NDA + Ray context doc (`processes/contracts/` + `agents/ray/`). **Counsel review required before first signature** (with the FTSA/TCPA memo). DocuSign connected for execution; the Founder approves sends. |
| 7 | **Scheduling / inbox** | Jim (not built) | 🟢 rails ready | **Built 2026-06-10:** daily desk loop (inbox triage → routine drafts → today's-call prep → needs-the Founder short list), `processes/loops/inbox-triage.md` + `agents/jim/` + runtime scaffolding. Drafts only; external invites in-loop. Arm the timer at go-live (or now). Quiet until outreach generates inbound. |
| 8 | **Finance** | Charles | 🟡 | Loops live. Left: set **cash-on-hand** in `runway.md` (unblocks runway); test the monthly-close ritual; optional live bank connection. |
| 9 | **Brand / content / collateral** | Luka · Katie · Pickle | 🟢 mostly | Brand v0.3 + content loop live; **Luka audit loop wired** (#1); **Pickle collateral built 2026-06-10** (`agents/pickle/collateral/`: one-pager, battlecard, case-study template). Left: **Canva visual layer** (design the one-pager PDF/deck from the content); **Katie content runway** (pre-write launch posts). |
| 10 | **QA / eval** | Kolby (not built) | 🟢 rails ready | **Built 2026-06-10:** six-dimension eval rubric (`processes/eval-rubric.md`) + weekly cross-agent eval-review loop (`processes/loops/eval-review.md`) + `agents/kolby/` + runtime scaffolding. Scores every agent's output, tracks drift, flags fails; reports only. Install the timer to start the weekly internal QA. Client-eval domain activates at first engagement. |

## Launch sequence (the go-live day runbook — draft)
1. **Deploy web** — yourco.com + getteamyourco.com live, `/book` → Calendly, analytics on (Webb).
2. **Confirm send gates** — warmup complete + 10DLC approved (Reilly).
3. **Approve + fire** the first outreach batch (the Founder approves → Reilly sends).
4. **Inbound handling** — replies → Jim triage → calls booked → call prep (Atlas/Reilly).
5. **Close** — fit call → audit or direct build → Ray contract signed → Janice onboards → Kimi runs 48h build → employee live.
6. **Run** — Charles tracks cash/MRR; Kortney watches client health; Bird scopes expansion. All loops continue.

## Recommended build order (next few weeks)
1. ✅ **Finish runtime automation** — Luka + Polo loops built **and installed on host** (2026-06-10). *All nine loops armed.*
2. ✅ **Reed: Email-2 demo asset** — already published+approved (landscaping). Optional next: produce the scripted **generic** demo (needs the Founder creative input + final-cut approval) — deferred unless the Founder wants it now.
3. ✅ **Delivery rails** — `yourco-template` scaffold + onboarding runbook + build playbook built (2026-06-10). Signed deal → clone → onboard → 48h build → go-live path is complete. Janice/Kimi agents trigger-gated on a real deal.
4. ✅ **Ray: contracts** — engagement agreement + mutual NDA + Ray context drafted (2026-06-10); **counsel review before first use**. Also in motion: **Reed YourCo-explainer** script drafted → pending the Founder approval → generate → swap homepage embed.
5. ✅ **Jim: inbox + scheduling** — daily desk loop built (2026-06-10, `processes/loops/inbox-triage.md`); arm the timer at go-live.
6. ✅ **Pickle collateral** — one-pager + battlecard + case-study template built (2026-06-10, `agents/pickle/collateral/`). Left: Canva visual layer + Katie content-runway (pre-write launch posts).
7. ✅ **Kolby: eval** — six-dimension rubric + weekly cross-agent eval-review loop built (2026-06-10); arm the timer to start internal QA.
8. **Deploy + execute the launch sequence** — last, on the Founder's go. **All build workstreams (#1–7) complete — only the launch remains.**

> Principle: everything above is built and **tested in dry-run** now, so launch day is flipping switches on proven systems.
