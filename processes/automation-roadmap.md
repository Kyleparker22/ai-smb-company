# YourCo — Automation Roadmap

The sequenced path from "agents run only when Cowork is open" → "the business runs itself between the Founder's approval taps." Ordered by **dependency**, not wishlist. Each item names the manual step it removes, the owning agent, what it's gated on, and status.

**Two standing principles:**
- **Always-on ≠ auto-send.** Every automation still respects the approval gates. Agents draft/stage 24/7; anything in a must-approve list queues for the Founder (approve from your phone, async).
- **Prove the unit before adding the next.** Build an automation when its trigger is real (a live send, a booking, a signed client) — not preemptively.

**Stewardship:** the Founder holds the roadmap (Brett surfaces it in the monthly advisory memo; Kemba executes the platform pieces). Each line is owned by its agent.

---

## Phase 0 — Foundation (do first; everything hangs off it)
| Automation | Removes | Owner | Status |
|---|---|---|---|
| **Always-on runtime** (Claude Code headless + git-synced workspace + cron on a VM) | "Desktop must be open"; no always-listening process for APIs/webhooks | **Kemba** / the Founder | Plan locked — `/decisions/2026-06-09_always-on-runtime.md`; execution pending (infra) |

> Until Phase 0 lands, Phases 1–3 can be *designed* but not truly run unattended. Same-day stopgap: keep Cowork open on an always-on machine.

## Phase 1 — Ready now (build on the runtime; no external trigger needed)
| Automation | Removes | Owner | Depends on | Status |
|---|---|---|---|---|
| **Receipt auto-logging** — parse Stripe/PayPal/Google receipt emails → `expenses.md`; flag new recurring charges | Hand-logging tools (today's Higgsfield/Descript/Vibe/etc. were manual); the off-books risk (caught HighLevel late) | **Charles** | Gmail connector (have) + runtime to run daily | Not started |
| **Auto research cards** — per-prospect site/news → 3–5 points + 1 pain hypothesis, for every sourced lead | Hand-writing research notes during sourcing | **Reilly** | Vibe/enrichment (have) + runtime | Not started |
| **Daily inbox triage** — pull real signal from vendor noise each morning; draft replies to ops items | the Founder scanning 20 receipts to find the 1 that matters | **Atlas** (→ Jim later) | Gmail connector + runtime | Not started |

## Phase 2 — Trigger-gated (wire as the trigger fires)
| Automation | Removes | Owner | Trigger / gate | Status |
|---|---|---|---|---|
| **Reilly reply engine** — classify inbound replies, auto-update suppression + pipeline, draft the commission-breath reply | Manual reply handling + pipeline updates | **Reilly** | First campaign send (~June 22) + webhook endpoint on the runtime | Designed (Reilly build doc); not wired |
| **Reed VO render** — generate the demo voiceover via TTS API, no manual app step | The one manual step in the video pipeline (assign voice in Descript app) | **Reed** | Runtime + a cloud-callable TTS (hosted ElevenLabs MCP, Descript speaker API, or runtime API key) | Open gap — logged in Reed SOP |
| **Email GIF preview** — auto-generate the 3–5s loop for Email 2 | Manual/deferred GIF (Canva MCP unreliable) | **Reed** | A reliable video→GIF path on the runtime | Deferred (Instantly generates at send for now) |
| **Call prep from bookings** — Calendly booking → auto account research + agenda + brief in your inbox | Manual pre-call research | **Jim** (not built) | First booking; Jim built | Not started |
| **Pipeline auto-update** — promote prospects through stages from reply/booking/engagement signals | Hand-updating `clients/_pipeline.md` | **Reilly** / Atlas | Reply engine + bookings live | Not started |

## Phase 3 — The moat (deepest; gated on a live client)
| Automation | Removes | Owner | Trigger / gate | Status |
|---|---|---|---|---|
| **Templated 48h build** — automate the engagement stand-up (Vapi + Twilio + calendar + CRM wiring) from `yourco-template` | The manual engineering of each client's intake agent | **Kemba** (template) → **Kimi** (delivery) | First signed client; playbook exists (`processes/discovery-to-48h-build.md`) | Playbook drafted; template not built |
| **Auto brand-review gate** — Luka's rules run as an automatic pre-publish check in each agent's pipeline | Manual brand review on every asset | **Luka** | Runtime + Luka's rules formalized as checks | Reviews on-demand today |
| **Engagement-health + expansion watchdogs** — friction signals + 2nd/3rd use-case scoping inside live accounts | Manual account monitoring | **Kortney** / **Bird** (not built) | First client live + stable | Park until client |
| **Eval harness automation** — run eval sets across all agents, flag drift/regressions | Manual/embedded evals | **Kolby** (not built) | 3+ agents running regularly | Evals live inside each agent today |

---

## The sequence in one line
**Runtime (Phase 0)** → wire the **ready-now** trio (receipts, research cards, inbox triage) → as sends/bookings go live, wire **Phase 2** (reply engine, VO render, call prep) → as the first client lands, build **Phase 3** (templated delivery, the product scaling).

Each phase compounds: more of the business runs itself, the approval taps stay yours.
