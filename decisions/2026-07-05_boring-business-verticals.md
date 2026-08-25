# 2026-07-05 — Boring-business verticals: 3 added, 2 rejected

**Decision:** Add **porta potty / portable sanitation**, **waste hauling / junk removal / roll-off dumpsters** (SMB slice only), and **crime scene / biohazard cleanup** (as a sub-vertical riding Restoration campaigns) to the target-vertical list + Sadie's intent engine. Reject **bail bonds** and **pawn shops / title loans**.

**Context:** the Founder proposed five "boring business" candidates — unglamorous, cash-rich local services with near-zero AI-vendor attention. Septic was already covered (#22 + intent vertical); the other five were evaluated against the fit filter in `processes/outbound/target-verticals-50.md`. Targeting-layer only: horizontal positioning is unchanged (`decisions/2026-06-22_horizontal-positioning-and-os-tiers.md`), and concentrated outbound stays on the hardscaping/landscaping beachhead — intent scanning is cheap and passive, so new verticals don't dilute it.

**Options considered:** add all five; add none (beachhead purity); add three (chosen).

**Why:**
- *Porta potty* — the rental business septic doesn't cover: route-based swaps, event/construction rentals, recurring billing, phone quoting; missed call = lost multi-month rental. Beachhead-adjacent (same GCs/suppliers as hardscaping).
- *Waste hauling / junk removal* — the genuine gap in the 50-list: route-dense, recurring-revenue, missed-call-heavy; often the same owner as porta potty.
- *Biohazard cleanup* — 24/7 crisis intake (empathy-critical scripting + hard guardrails = the moat), insurance-doc-heavy like Restoration/public adjusters, high ticket. Too small per metro for a standalone push → rides Restoration campaign infra. Warm path: Prospect A's restoration network.
- *Bail bonds rejected* — state-by-state licensing, collections from people in crisis, industry shrinking with bail reform, reputational mismatch with a premium executive-trust brand, and another counsel gate for a small TAM.
- *Pawn / title loans rejected* — regulated consumer finance (TILA, state usury, CFPB, AML/KYC) and no operational wedge: walk-in retail counters aren't missed-call businesses. Reputationally radioactive (title lending especially).
- The meta-pattern is now recorded in the 50-list's "Why NOT": boring is good; **regulated-consumer-finance boring is not**.

**Reversibility:** Additions are cheap to remove (delete the JSON blocks + list rows; no campaigns funded yet). The rejections are revisitable only if the regulatory/brand calculus changes — bail bonds would additionally need Ray/counsel review before any engagement, so a future add starts there.

**Surfaces touched (change-one-sweep-all):** `processes/outbound/target-verticals-50.md` (additions §, Why-NOT §, header count 53) · `runtime/intent_verticals.json` (58 verticals; the 3 new blocks inherit no-config defaults — YouTube comments + Google News + Bluesky; the Founder may add Google-Alert feeds later per `runtime/intent-alerts-setup.md`) · `processes/outbound/industry-campaigns.md` (Restoration rider note).
