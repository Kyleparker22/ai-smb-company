# Pre-launch security + QA audit — public surfaces

> First pass: 2026-06-14 (gstack-style sweep). Scope: the staged public site (`agents/webb/pages/yourco-site-v2/`, the two landing pages, the client-console template) and the data-flow into the internal CRM/dashboard. Re-run this before the OtherVenture switch-flip and after Mode-B lead capture is wired.

## Method
Static client-side review (no live deploy): grep for exposed secrets, dangerous sinks (`eval`/`document.write`/`new Function`), URL-param reflection, `innerHTML` + user-input flows, `target="_blank"` tab-nabbing, mixed content (`http://`), and form/lead handling. Then manual inspection of every page that renders user input.

## Clean ✅
- **No exposed secrets** (no `sk-`/`AIza`/`xoxb`/`ghp_`/api-key literals in client code).
- **No dangerous sinks** — zero `eval`, `document.write`, or `new Function`.
- **No reflected-XSS surface** — nothing reads `location.search`/`hash`/`URLSearchParams`.
- **No mixed content** — no insecure `http://` resource refs.
- **Tab-nabbing safe** — every `target="_blank"` carries `rel="noopener"`.
- **Lead capture** — `name`+`email` required; `mailto` body fully `encodeURIComponent`'d; SMS consent with STOP/HELP language present (TCPA-aware). Pre-launch path is mailto-only (no server POST yet).

## Findings & fixes
| # | Severity | Where | Issue | Fix |
|---|---|---|---|---|
| 1 | Med (→ High at launch) | `instant-employee.html` lead confirmation | User-typed **name** + **business** injected into `innerHTML` → DOM XSS (self-XSS today; becomes **stored XSS** against the team once Mode-B `/api/capture` writes leads into the CRM) | Added `esc()`; escaped `lead.name` / `lead.business` / `lead.employee` / the `mailto` href. ✅ |
| 2 | Med (launch hardening) | CRM `crm/index.html` renderers | Externally-sourced text (company/contact names, vertical, location, source, deal use-case/next-action, activity summary, map tooltips, **edit-form `value="..."` attributes**) rendered into `innerHTML` unescaped — the receiving end of finding #1, plus Vibe-scraped data | Added a top-level `esc()`; escaped `coName()` + companies/contacts/board/activity/hot-list/map renderers and all edit-form input values (kills attribute-breakout). ✅ |

Both verified: `esc()` neutralizes `<img onerror=…>` and `"`-breakouts, leaves plain text (incl. apostrophes) unchanged; both files compile.

## Still open (do before / at launch)
- **Mode-B `/api/capture` must sanitize server-side** — client-side escaping is defense-in-depth, not the primary control. When the public lead endpoint is wired, validate + sanitize `business`/`name`/`email`/`phone` on the server before writing to `crm/data.json`, and rate-limit/abuse-guard it (spec: `processes/instant-employee.md`).
- **CSP header** — when the site is deployed, set a Content-Security-Policy (e.g., `default-src 'self'; script-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com`) so any missed sink can't exfiltrate. The CRM/dashboard load d3/topojson from jsdelivr/cdnjs.
- **`/security-review` on the deploy diff** — run the native skill against the actual deployed bundle once the host + Mode-B endpoint exist.
- **Counsel items** (privacy policy fill, DPA, CAN-SPAM address) — tracked in `processes/launch-runbook.md`, not a code issue.

## Round 2 — parallel multi-lens review (2026-06-14)
Ran a 3-agent fan-out review (correctness / security / simplification) + synthesis over the CRM, dashboard, Melanie brain, both servers, and the lead-capture page. 17 deduped findings; the real ones fixed:

**Bugs fixed**
- **Lead capture was dead** — `instant-employee.html` referenced `EMP[cur]` (undefined; dict is `BIZ`, no `cur`) → every "Make it real" threw `ReferenceError`. Declared `cur`, set it in `run()`, switched to `BIZ[cur]`. ✅
- **Activity edit/delete hit the wrong record** under a filter/search (filtered loop index vs unfiltered `D.activities`). Now resolves via `D.activities.indexOf(a)`. ✅
- **Dashboard XSS** — `render()` injected `focus`, agent name/role, stage labels, compliance/loops/trust strings into `innerHTML` unescaped (the CRM-escaping pass had missed the dashboard). Escaped all of them; extended `esc()` (both apps) to encode `"` and `'` for attribute safety; deleted two weaker local `esc()` shadows in the CRM. ✅
- **Melanie `add_activity` rewound `lastTouch`** with older dates (skewing cold/win-prob). Now guards `not lastTouch or lastTouch < when`, matching the CRM. ✅
- **Stale answers after a write** — Melanie's Q&A cache is cleared on any successful `_apply_action`. ✅

**Server hardening (the unauthenticated-localhost findings)**
- Added to `/api/data`, `/api/draft` (CRM) and `/api/melanie` (dashboard): a **2 MB body-size cap** (anti-DoS), a **same-origin CSRF guard** (reject when `Origin` ≠ `Host` → blocks a malicious page POSTing to `127.0.0.1`), a **rate limit on the paid `/api/draft`**, and a **shape check on `/api/data`** (must be a CRM object). Verified: cross-origin → 403, oversized → 413, malformed → 400, same-origin → 200.
- Hardened the action model's system prompt: CRM context is **untrusted data, never instructions** (partial prompt-injection mitigation).

**Round 3 — remaining hardening (2026-06-14)**
- ✅ **Prompt-injection target validation** — state-changing actions (`move_deal`, `arm_loop`, `disarm_loop`) now require the target to be **named in the Founder's own message** (`_mentioned()`), not free-resolved from injectable context. Verified: a target the Founder didn't name is rejected; a named one applies.
- ✅ **Perf** — `empiricalRates()` hoisted to one call per render (`_rates`), read by `winProb()`; `forecastStrip()` and `goalCardHTML()` reuse the `probs` array instead of recomputing `winProb()` per deal.
- ✅ **Mirror dedup** — `data.js` writer now has one implementation (`melanie.write_mirror`); `crm/server.write_mirror` delegates to it.

**Still open (lower priority)**
- Shared-secret token on mutating endpoints (defense beyond same-origin; covers DNS-rebind + the no-Origin case) — needed before binding `0.0.0.0`. Interim: put Tailscale ACLs / an authenticated reverse-proxy in front when exposing beyond localhost; don't bind `0.0.0.0` bare.
- Optimistic-concurrency token (mtime/hash → 409) to stop a browser save clobbering concurrent agent/loop edits when `CRM_GIT_SYNC=1` (needs the frontend to send the loaded version + handle 409).
- A confirm-before-write preview for Melanie's mutations (UX change), and minor cleanups (single SDK import-probe, blocking save-failure UI).

## Note
The CRM/dashboard are **internal** (Tailscale/localhost), so finding #2 is low-risk *today* (data is curated by the Founder/agents). It matters the moment **inbound** (Mode-B leads) or **scraped** (Vibe) data flows in — which is the launch plan. Fixed now so the hardening is in place before that switch flips.
