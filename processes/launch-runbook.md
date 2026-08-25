# Launch Runbook & Readiness Audit

> **The switch-flip plan.** YourCo is built and waiting; this is the single document that turns "the day I'm legally cleared" into a clean, ordered launch instead of a scramble. Two parts: the **Readiness Audit** (every blocker, status, owner — surfaced now while there's time) and the **Go-Live Sequence** (the exact ordered steps for launch day + the first 48 hours). Owners: Atlas/Brett (the plan), the Founder (the gates). Last updated 2026-06-12.

## The master gate (above everything)
🔴 **OtherVenture legal resolution.** YourCo **cannot launch / go live or run any external go-to-market until the OtherVenture matter is resolved (~weeks out).** Everything below stays internal until then. **This is the single trigger** — when it clears, this runbook executes. *Watch: keep the OtherVenture timeline honest — "a few weeks" must not drift to "a few months" (see the pre-mortem, `agents/brett/premortem-2026-06-12.md`).*

> **Gate state lives in the trackers, not here (added 2026-07-05):** `processes/launch-gate.md` (master gate — status, resolution condition, update log) and `processes/counsel-gates.md` (all counsel-blocked items in one table, Ray owns). Update those on any change; this runbook stays the sequence, they hold the status. As of 2026-07-05 the "~weeks out" estimate above is 3+ weeks old and needs a refresh in the tracker.

---

## Part 1 — Readiness Audit
✅ done · 🔲 open (closeable now) · ⏳ in progress / external-gated. **Close the 🔲 items during the wait so launch day has none.**

### Legal & compliance (the launch-critical cluster)
| Item | Status | Owner |
|---|---|---|
| **OtherVenture resolution** (master gate) | 🔴 external | the Founder |
| Counsel review of the legal suite (engagement agreement, DPA, BAA, NDA, privacy policy) | 🔲 open | the Founder → counsel |
| CAN-SPAM postal address — home vs **PO box / registered agent** | 🔲 open | the Founder |
| Privacy policy published at `/privacy` (before the site collects data) | 🟠 draft page live (`privacy.html`, linked in footer) — needs counsel + placeholder fill | Webb/Rafi |
| 2FA sweep across accounts | 🔲 open | the Founder (per-account) |
| 10DLC registration (SMS channel) | ⏳ in progress | the Founder + Instantly |
| FTSA/TCPA counsel sign-off (SMS only — **email-first doesn't need it**) | 🔲 open | the Founder → counsel |

### Infrastructure
| Item | Status | Owner |
|---|---|---|
| Always-on runtime (loops firing autonomously) | ✅ proven in prod | — |
| CRM + dashboard hosted on Tailscale; phone access | ✅ | — |
| Core connectors (Slack, Gmail-draft, Calendar, Instantly, DocuSign, Granola, Vibe) | ✅ live | — |
| Domain warmup `getteamyourco.com` (~90% inbox placement) | ⏳ ~Jun 20 target | the Founder confirms in Instantly |
| QuickBooks · social connectors | 🟠 deferred / TBD | — |
| customer-health timer installed on VPS (no-op pre-client) | 🔲 optional | the Founder (1 cmd) |
| **Connector Console: TLS + public hosting** — see below. **Hard prerequisite: no connector receives a console URL until this is done.** | 🔲 required *if* the connector program launches | Kemba (infra) + the Founder (DNS + sudo) |

#### Connector Console — what "TLS + hosting" actually means (added 2026-08-07)
The console has real per-connector login (`processes/partnerships/connector-console/auth.py`), but today it
runs on **plain HTTP, bound to localhost**. That's safe on the Founder's Mac and unsafe the moment it has a public
address: the session cookie is a bearer token, so over unencrypted HTTP anyone sharing a network with a
connector (coffee-shop wifi) or sitting on the path can read it and become them.

**the Founder's actual to-do list is short — and none of it happens before counsel clears the program:**
1. **Pick the address.** Suggested `connect.yourco.com` (a subdomain of the domain already owned).
   *Do not use the warmed outbound domain* — deliverability must not be disturbed.
2. **Add one DNS A record** pointing that subdomain at the existing Hostinger VPS. No new hosting to buy —
   the runtime box already runs 24/7 and is where this belongs.
3. **Run the TLS + proxy setup on the VPS** (a handful of `sudo` commands; Claude writes them out
   verbatim when the time comes). Recommended: **Caddy** as the reverse proxy — it obtains and renews a
   free Let's Encrypt certificate automatically, so there's no annual expiry to forget. It terminates
   HTTPS and forwards to the console process on localhost.
4. **Run the console as a systemd service** (like every other runtime process) so it survives reboots.

**Also required at the same time, or the auth's guarantees degrade:**
- **Trusted-proxy config** — behind a proxy, every request appears to come from the proxy, which collapses
  the per-IP login throttle into one bucket. `X-Forwarded-For` is deliberately *not* trusted by default
  (a forged header would defeat the throttle); it needs an explicit allowlist.
- **A threading server** — the login path runs a ~47ms scrypt derivation by design; single-threaded, a
  login flood blocks all traffic.
- **Setup-token delivery** — the weakest link in the chain. A token in a compromised mailbox is an account
  takeover. Deliver over a channel already trusted with that person, and consider shortening the 72h window.
- **Never publish `_out/`** — `--render`/`--all` write complete, unauthenticated pages there.

### Funnel / outreach (Reilly)
| Item | Status | Owner |
|---|---|---|
| Campaign copy (6-touch) locked + Luka-reviewed | ✅ | Reilly |
| CAN-SPAM footer specified | ✅ (pending the address pick above) | Reilly |
| $29-bot battlecard (for the discovery call) | ✅ | Pickle |
| Email-2 demo asset (animated) + the live demo gallery upgrade | ✅ / wires in at site-launch | Reed / Webb |
| Batch-1 lead list (≥2,000 deduped, national) | ⏳ sourced, awaiting batch approval | the Founder approves |
| Campaign staged in Instantly (paused, not launched) | 🔲 open | Reilly |

### Website (Webb)
| Item | Status | Owner |
|---|---|---|
| Staged yourco-site-v2 (home, how-it-works, employees, **demos**, **demos-tier2**, **instant-employee**, pricing, about, audit) | ✅ built | Webb |
| **Instant Employee — Mode B (public live generation)** flip: stand up the generation endpoint (server-side, yourco-held key), rate-limit/abuse-guard, per-domain cache, eval the generator itself, swap the `BIZ` lookup for the live call, wire the CTA to capture inbound → CRM. Spec: `processes/instant-employee.md` | 🔲 launch-day | Webb + the Founder |
| Homepage final polish (hero, $29-bot line, CSS) | 🔲 open | Webb |
| Favicon · OG/social tags · link audit | ✅ favicon + OG/Twitter on all 23 pages; `og.png` share image rendered; link audit clean (0 broken/orphans) | Webb |
| Deploy to the live host (the actual flip) | 🔲 launch-day | Webb + the Founder |

### Product / delivery
| Item | Status | Owner |
|---|---|---|
| Delivery lifecycle staffed + generalized (Janice→Kimi→Kolby→Kortney→Bird→Harry) | ✅ | — |
| Eval framework + red-team + autonomy ladder | ✅ | Kolby |
| Contracts + DocuSign send flow | ✅ (counsel review pending) | Ray/Rafi |
| Sandbox test-tenant (live-integration eval) | ⏳ v1 proven; dedicated calendar optional | Kemba/the Founder |
| Pricing v0 (landscaping locked) | ✅ | Polo |
| Client console (live activity · approvals · outcomes · reliability) | ✅ template; per-client overlay at go-live | Webb/Kortney |
| **Console live-data feed** — the console is sold in the proposal ("your live console") but currently shows sample data; wire it to the client's real activity/approvals (same plumbing class as Instant Employee Mode B), or scope v1 honestly as a daily-refreshed digest. *(commercial tabletop 2026-06-12, finding #5)* | 🔲 open | Webb |
| **Branded proposal render** — print-to-PDF, DocuSign-ready, brand-consistent. `agents/pickle/collateral/proposal.html` *(tabletop finding #3 — closed)* | ✅ drafted (Polo locks price per deal) | Pickle/Webb |
| **Payment collection** → **Stripe** (decided 2026-06-12). SOP `processes/payments.md` written; wired into the proposal. Remaining: **the Founder** sets up the account + bank + ACH (agent can't). | 🟠 the Founder-setup | Charles/the Founder |
| **Proposal / SOW template** — turns interested→signed; doubles as the SOW under the agreement. `processes/contracts/proposal-sow.md` | ✅ drafted (Polo locks price) | Pickle/Polo |
| **Offboarding + data-export SOP** — clean pause/exit + DPA data-deletion procedure. `processes/offboarding.md` | ✅ drafted | Janice/Rafi |

### Scale readiness — LOCKED 2026-06-30 (post-launch infra; NOT launch gates)
> The platform calls for running multiple clients — now **locked** (pulled forward so a sign-on surge doesn't force them under fire): `decisions/2026-06-30_multi-client-scaling-locked.md`. Surge handling: `processes/delivery-surge-playbook.md`. Architecture: `03_internal_platform.md` → "Multi-client architecture."

| Item | Status | Owner |
|---|---|---|
| **Per-client API keys / billing isolation** — clean cost attribution, blast-radius containment, rate-limit headroom (the shared credit-balance death already bit once → this is the structural fix; auto-reload + the API-independent alarm stay on every account). | ✅ LOCKED — per-client from client #1 | the Founder → Kemba |
| **Per-client runtime isolation** — shared runtime + strict overlay/credential isolation (default); isolated compute only by exception (regulated/PII — Rafi's trigger). | ✅ LOCKED — shared + overlay isolation | the Founder → Kemba (Rafi) |
| **Multi-tenant vs bespoke** — core OS stays bespoke/isolated; multi-tenant is a per-vertical-product call only (e.g. Conduit). | ✅ LOCKED — bespoke core | the Founder |

---

## Part 2 — Go-Live Sequence

### T-minus (the week before OtherVenture clears — pre-stage everything)
1. **Counsel sign-off** on the legal suite — the one thing with real lead time; start it early.
2. **Pick the CAN-SPAM address** → drop into the campaign footer.
3. **Confirm warmup health** in Instantly (~90% placement) — the email channel's go/no-go.
4. **Approve the batch-1 lead list.**
5. **Webb finishes** the homepage polish + favicon + OG tags + link audit; privacy policy ready to publish.
6. **Stage the campaign in Instantly** (paused).
7. **2FA sweep.** Install the customer-health timer.

### Day 0 — the switch-flip (in order, once OtherVenture clears)
1. **Publish the site live** (deploy yourco-site-v2 + `/privacy`). Verify links, the demo gallery, the Calendly booking.
2. **Final deliverability check** — warmup still healthy; from-address + footer correct.
3. **Fire Reilly Email 1** → the top-fit leads only (≤10/inbox/day), per the locked ramp (`campaigns/…batch-1`).
4. **Confirm the loops are armed** (briefing, sales, finance, pipeline, eval, watchdog, content, inbox-triage) + customer-health.
5. **Start the first-48h watch** (below). Atlas posts launch status to `#all-yourco`.

### The ramp (per Reilly's locked send plan)
| ~Day | Action |
|---|---|
| 0–2 | Email 1 → top-fit, then remaining batch (≤10/inbox/day) |
| ~7 | Email 2 (demo) → full batch |
| ~14 | Email 3 (reframe + release) → full batch |
| when 10DLC clears | activate SMS 1/2/3 (ex-suppressed states) |
Guardrails: ≤10 cold/inbox/day, no >20%/day jumps, **pause-and-recover if spam/bounce climbs.**

### Launch-moment inbound — the "spike" channels (new 2026-06-16)
yourco's GTM is currently outbound-led (Reilly's email ramp). Brett Williams (DesignJoy) is the case for a **launch-spike inbound channel** alongside it: he went from *zero audience* to ~36,000 unique visits and ~$10k day-one revenue from a **single Product Hunt launch**, powered only by friends-and-family upvotes (`agents/brett/competitive-watch.md`).
- **What Product Hunt is:** a daily-refreshing site where people who hunt for new products browse and upvote launches. Submit a product; the more upvotes early, the higher it ranks; the homepage drives a large, free, high-intent traffic spike + often instant customers. It's tuned for *products/tools*, not "book a call" consultancies — which is exactly why yourco needs a **launchable artifact** to use it.
- **What yourco launches there:** the **free online Revenue Leak Snapshot** (a free tool = ideal PH launch) and/or an **off-the-shelf subscribe-and-go employee** (`decisions/2026-06-16_two-motions-productized-employees.md`). Both are self-serve products a hunter can try instantly — unlike the audit→OS consultative motion. The "see yours" instant demo is the hook.
- **Other launch/spike platforms to target (same playbook, sequence over weeks — don't blow them all at once):**
  - **Product Hunt** — the primary; biggest spike, product-obsessed audience. Launch the Revenue Leak Snapshot / off-the-shelf employee.
  - **Hacker News ("Show HN")** — high-quality technical/founder traffic; works for a genuinely interesting free tool (the Missed-Money Meter / Revenue Leak Snapshot), not for a salesy pitch.
  - **Indie Hackers** — founder community; the build-in-public story + the tool. Pairs with the the Founder-as-operator narrative.
  - **Reddit** — relevant subs only (r/smallbusiness, trade subs, r/agency), value-first per Sadie's ToS rules — story/tool, never a pitch. (Reddit *posting* by a human is fine; the *API/automation* is the parked piece.)
  - **BetaList / Peerlist / Uneed / Fazier / Microlaunch / Tiny Launch** — secondary launch directories; cheap incremental spikes, stagger them after PH.
  - **G2 / Capterra** — not a spike but a *standing* presence: list yourco so it shows up in "AI receptionist / AI for [trade]" comparison searches (the AEO real estate the point-competitors already own, `agents/brett/competitive-watch.md`).
  - **AppSumo** — only if a productized SKU fits a lifetime/discount-deal model; evaluate later, lower priority (can erode premium pricing).
- **What it needs:** the site live first (OtherVenture-gated), a real subscribe/try flow (not "contact us"), an upvote/support network lined up ahead of each date (the Founder's personal network + warm contacts + any early users), assets (gallery, tagline, maker comment), and a chosen calendar. **Mostly free + low-risk**, but each is one-shot per product — prep the network before firing, and don't stack them on the same day.
- **Adjacent zero-cost spikes Brett used:** sharing the founder story on **relevant forums/communities** (Reddit per Sadie's ToS rules, indie/SMB communities) — distribution is the moat, and these are free. Sequence: site live → forum/community story + Product Hunt launch → capture the spike into the CRM + the off-the-shelf checkout.
- **Owner:** Katie (launch assets + community) + the Founder (the upvote network + go decision). **Gate:** post-site-live, after the core outbound ramp is healthy — a spike is wasted if the funnel behind it isn't ready.

### Post-launch unlock (once the site has real traffic)
- **Instantly Website Visitors → multi-channel** (`processes/outbound/website-visitors-multichannel.md`): de-anonymize site visitors → email + LinkedIn + phone → a "Site Visitors" Instantly campaign (Michelle's visit-aware copy), email automated + LinkedIn manual. **Gate:** paid Visitors tier + Rafi's privacy-disclosure (visitor identification = personal data) + Ray on the privacy policy. Highest-intent cold source — but only after the site is live + warmed.
- **Google → Microsoft migration (the Founder's intent, noted 2026-07-24 — post-launch, NOT a launch gate):** once yourco is live, switch the workspace stack from Google Workspace/Gmail to **Microsoft 365/Outlook**. Scope when scheduled: the `founder@yourco.example.com` mailbox + agent aliases (currently riding the single Workspace seat), the runtime **Gmail connector → MS Graph** (draft-only approval gate preserved), Bella's `contact@yourco.example.com` send flow, snapshot-intake email, Calendar connector when it lands, and DNS/MX for `yourco.com`. Upside: MS Graph is already the planned stack for Conduit, and most SMB clients live on M365 — dogfooding their tenant model. **Timing rule: not during the launch window or the first live client ramp — email deliverability and the warmed sending domain must not be disturbed mid-ramp; Kemba/platform schedules it as a deliberate migration with the Founder.**

### First 48 hours — the watch
- **Jim** triages every reply; a real prospect reply = top of the needs-the Founder list within the hour.
- **Atlas** watches deliverability + spam/bounce + cost; posts health to `#all-yourco`.
- **David** logs every reply/booked call into the CRM.
- **A booked call →** Janice/Kimi are staged to run discovery → 48h build (first delivery = **white-glove, the Founder-in-the-loop**, per the pre-mortem; *not* the autonomous model yet).
- **the Founder's role:** approve sends, approve the first go-live, make the flagged calls. ~daily, per `05_operating_rhythm.md`.

### Abort / pause conditions
- Deliverability craters (spam folder, bounce spike) → **pause the ramp**, fix warmup, resume low.
- Any compliance surprise (a complaint, a state-law flag) → pause, route to Rafi/counsel.
- The OtherVenture resolution unwinds → **stop**; nothing external goes out.

---

## What only the Founder does at launch
The legal sign-offs, the address pick, the batch approval, the deploy decision, the first go-live approval, and every external send — until the **autonomy ladder** (`decisions/2026-06-12_autonomy-ladder.md`) earns these down on eval evidence. Connected ≠ auto. The machine is ready; these gates are yours.

> **Bottom line:** every 🔲 above is closeable during the OtherVenture wait. Close them, and launch day is a five-step switch-flip — not a scramble. That is the whole point of building it all internally first.
