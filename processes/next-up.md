# Next up — internal work queue

> Running backlog of the next internal work, grouped. Parked 2026-06-10 for tomorrow (2026-06-11).

## A. Activate the agents (let them do real work)
- ✅ **Sadie's first listening sweep** (web) — done 2026-06-11; validated intake intent + the $29-bot floor. **Reddit API blocked by compliance** (Rafi: commercial + LLM use sits outside Reddit's free tier — `agents/rafi/reddit-api-assessment.md`). `listen.py` built + parked. Sadie stays on WebSearch market-intel.
- ✅ **Melanie's first CEO read** — done 2026-06-11; top call (set launch date + freeze non-launch building) agreed in direction; first `learnings/ceo/` gap logged (date is downstream of readiness).
- ✅ **David's pipeline report** — done 2026-06-11; caught + fixed the `_pipeline.md` ↔ CRM drift (sales mirror split from internal rollout). **Kolby's first eval** — done 2026-06-11; baseline scoreboard, 6/7 clean, flagged Katie's unsourced stats. Both loops proven end-to-end.
- ✅ **Armed Kolby (eval-review, Sun 17:00 ET) + David (pipeline-report, Mon 06:50 ET) timers** on the host 2026-06-11.
- Wire **Melanie's CEO-read** + **Sadie's sweep** as scheduled runtime loops *(deferred — Sadie is human-in-the-loop until a compliant lead source; Melanie's cadence TBD with the Founder)*

## B. Finish the tech stack — wire + connect every tool
- ✅ **Instantly** — sync built + **connection verified live** (`crm/integrations/instantly_sync.py`, read-only → CRM, `all:read` key). Fills automatically on Reilly's first campaign. 🟠 **QuickBooks** — deferred (auto-auth hit Intuit 403; pre-revenue, no data; revisit with a QBO account + revenue). **DocuSign**, **Canva**
- **Social platform connectors** — Reddit / X / Instagram / TikTok (for Sadie, Katie, Jim). ⚠️ **Reddit + X: compliance-gated** — commercial + LLM use needs a paid commercial data agreement (Rafi assessment). Revisit only if strategically worth the agreement; otherwise human-in-the-loop. IG/TikTok TBD.
- Live bank/finance feed
- Goal: every tool integrated + feeding the CRM (source of truth) + the dashboard, automated

## C. Access & hosting (use it anywhere) — ✅ DONE 2026-06-11
- ✅ **Hosted the CRM + dashboard** on the VPS as always-on systemd services, bound to the Tailscale IP only (private, never public). CRM edits git-sync.
- ✅ **Mobile access** via Tailscale (VPS + Mac + iPhone mesh): CRM `http://10.0.0.1:8790`, dashboard `:8791` in the phone browser; **Tailscale SSH** (keyless) for files + triggering agents + interactive `claude`. Full setup + phone cheat-sheet: `runtime/phone-access.md`.

## D. Organize — ✅ DONE 2026-06-11
- ✅ Archived 2 stale docs (`_archive/` + convention); rewrote `00_README.md` as an accurate index (all folders, current loops, conventions); fixed the 1 dangling reference; refreshed CLAUDE.md folder map.
- ✅ Consolidated the setup-guide overlap 2026-06-11: archived the redundant `claude-code-setup-diy.md`; kept the referenced canonical `claude-code-setup.md` (now points to the live runtime docs).

## E. Inputs & ideas
- **Review the videos + Instagram links** the Founder has → decide what else to add to YourCo OS

## F. Brand presence
- **Set up YourCo social accounts** — Instagram, X, TikTok, etc.? (decide which, then stand them up)

## G. Launch prep
- ✅ **Launch runbook + readiness audit** — built 2026-06-12 (`processes/launch-runbook.md`): the master launch-gate, the full readiness audit (every blocker, status, owner), the ordered Day-0 switch-flip sequence, the ramp, the first-48h watch. **This is the live launch doc — close its 🔲 items during the OtherVenture wait.**
- ✅ **Funnel** — Reilly's campaign locked + CAN-SPAM footer specified (`agents/reilly/campaigns/`); $29-bot battlecard (Pickle). Open in the runbook: the postal-address pick, batch approval, staging in Instantly.
- 🔲 **Website polish** (Webb) — homepage CSS, OG/social tags, link audit, favicon → tracked in the runbook's audit.

## Standing / deferred
- Compliance: counsel review of the legal suite; 2FA sweep
- Confirm Obsidian vault points at the repo folder (so it mirrors the OS)
