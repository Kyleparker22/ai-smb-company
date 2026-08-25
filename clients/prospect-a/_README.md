# Prospect A — Sample Product (engagement)

> **Stage:** `discovery` — mirrored from `crm/data.json`, which owns it. Do not edit this by hand; change the CRM and this follows. `runtime/consistency-check.py` fails if the two disagree.


**Operated storm-verification product** for Prospect A (roofing / storm restoration, Florida): multi-source storm data (NOAA + Xweather on his key; HailTrace/IHM ready-to-connect) → deterministic cross-verify engine → AI verification layer reads raw report remarks (credibility + claim-grade) → one-tap approve → crew SMS. **LIVE** on a Cloudflare preview (D1 + VPS auto-publisher); embedded-AI-surface form factor, white-label (bit us once — no yourco branding on Nick's surfaces).

**Status:** built and operating in preview; **partnership unpapered — legal before public launch** (Ray's gate). Paid-keys hold lifted 2026-07-03.

## The docs (this folder — one client, one folder)
- `prototype/` — the whole system: engine (`*.py`), demo (`demo.html`, :8796 `nick-storm-demo`), crew app (`crew_server.py`, :8798 `nick-crew-app`), spec docs (`BUILD-PLAN.md`, `DATA-SOURCES.md`, `PRICING.md`, `ROADMAP.md`, `VERIFICATION.md`, `XWEATHER_WEBHOOK.md`), validation vs Nick's hand-checked week
- `cost.md` — operating economics (~$15–40/mo: Twilio + verification tokens; engine itself ~$0 — the value is the verification layer, not compute)

## How the OS works this client (agents across the whole process)
Per the Founder 2026-08-07 (pattern set on Sample Realty): agents help end-to-end. Internal names — never on client-facing surfaces:
- **David / CRM** — Nick's company/deal + activity log current; partnership terms tracked on the deal once papered.
- **Polo** — prices it (what Nick pays is separate from cost.md's operating model; partnership/rev-share structure pending the paper).
- **Kolby** — eval: verification-layer accuracy (verdict self-scoring loop is live), alert precision/recall vs Nick's manual weeks, demo QA.
- **Rafi** — guardrails: SMS compliance (A2P 10DLC), no auto-send without Nick's one-tap approve, **open: duplicate-SMS bug** (2026-07-05 audit) stays on his watch until closed.
- **Ray** — the gate that matters: **partnership agreement before public launch**; also platform-ToS posture on any added sources.
- **Charles** — cost.md roll-up (weekly pulse + monthly close); watches Twilio + token spend vs whatever Nick pays once papered.
- **Reed** — the white-label follow-up video (shipped 2026-07-05, `agents/Reed/productions/`); future demo assets, credibility gate applies.
- **Kimi / Janice** — light here (product is built); Janice re-engages if this becomes a papered, onboarded engagement with SLAs.
- **Atlas + runtime loops** — the storm loop + auto-publisher run on the VPS now; production error sweep active; per `runtime/activation-triggers.md`.

## Open items
- **Paper the partnership** (Ray/counsel) — the blocker for public.
- **Duplicate-SMS bug** — still open from the 2026-07-05 bug audit; Rafi's watch.
- Xweather-only source validation (drop HailTrace/IHM if no hail gap) — `prototype/README.md` §source-scope.
