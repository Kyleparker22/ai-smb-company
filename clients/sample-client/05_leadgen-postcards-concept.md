# Sample Client — vision-qualified postcard lead gen (module concept)

> **Status: concept — not started. the Founder's idea 2026-07-20.** The second module for Client Owner, and the unstick lever for the stalled proposal: module 1 (proposal automation) saves him time; this one **makes him money**. Deployment order is fixed: **3-address sample → signing meeting → machine build on signature.** Nothing at scale before counsel clears the imagery gate (`processes/counsel-gates.md` #13). Owners: the Founder (pitch) · Bella-pattern build TBD · Ray (gate) · Polo (module pricing).

## The one-liner
Every home **sold in the last 12 months** near Client Owner's territory → **vision-qualify** which ones plausibly want a patio, fence, pool surround, or outdoor kitchen → mail each a **Sample Client postcard of their own house** with a QR code → the QR opens a **per-address page showing an AI concept render of that project on that property** → scans are the lead list, hot and self-qualified.

New owners are the highest-propensity buyers of outdoor work (spend concentrates in the first year), the sold-list is public record, and nobody else in Yourtown is mailing a picture of the prospect's own backyard reimagined. This is yourco's proof-led pattern — "I already built this for you" — translated from Instant Employee demos to hardscaping.

## The pipeline (the scaled machine — post-signature)
1. **Sold-list** — Mecklenburg County public records (POLARIS parcel/sales data), filtered: sold ≤12 mo, single-family, lot size worth hardscaping, price band matching Client Owner's ticket. **No Zillow/Redfin scraping — their ToS forbid it and the county gives the same facts free.** Radius/zips: Client Owner picks.
2. **Vision qualify** (Claude vision) — per parcel, on properly licensed imagery (THE open gate, below): flag candidate projects (no/aged fence · bare or cracked patio · pool w/ dated surround · big blank backyard), confidence-scored; low-confidence → drop, never guess. Attrition expected; over-pull like outbound (2×).
3. **Per-address page + QR** — static page per parcel slug (the `prospect-demo.html?p=` pattern), Sample Client branded, mobile-first: their house, the concept render, "what this takes" band, tap-to-call/book Client Owner. **Render-on-scan:** the premium AI render (Higgsfield, image-first) generates at first scan (or pre-render top-N) — render spend goes only to engaged leads, and **the scan is the intent signal**.
4. **Postcard** — print API (Lob/PostGrid class), front = their house + one-line invitation, back = QR + Sample Client brand + offer. Direct mail is the **lowest-regulation channel we have**: no CAN-SPAM/TCPA/consent/warmup — and therefore *not* blocked by the sending-infra work the email machine waits on. (Whether the *OtherVenture* gate covers client-branded mail for a signed client: it shouldn't — this is Sample Client speaking, not yourco — but confirm with the gate owner; yourco never appears on the surface either way.)
5. **Scan → follow-up** — scan event logged per address → Client Owner notified same day ("32 Hawthorne scanned the pool-surround card twice") → his normal estimate motion. Track: mailed → scanned → called → estimated → closed, per batch, so batch 2 targets better than batch 1 (closed loop).
6. **Report** — per-batch one-pager: cost, scans, estimates, jobs, $ pipeline. This is the case-study engine the brotherhood discount already bought.

## Economics (why this forgives imperfection)
~$1–2/address all-in at small volume (card + postage + data + imagery + amortized render). A 500-card batch ≈ **$500–1,000**. Client Owner's installs run $10k+: **one job pays for ~10–20 batches.** Even 1 close per 500 cards is a wild ROI; scans-as-intent means follow-up effort concentrates on warm addresses only.

## Guardrails (non-negotiable)
- **Credibility gate:** every render is labeled a **concept visualization** on card and page. No fabricated before/afters, no implied "we did this here," no invented neighbor references.
- **Invitation, never observation.** Imagery may predate the sale — so copy never asserts a diagnosis ("your fence is falling apart"), only invites ("wondering what the backyard could be?"). A stale read then costs nothing.
- **White-label:** Sample Client brand only, everywhere the prospect looks. No yourco name/logo (the Sample Product lesson).
- **Taste test before scale:** AI-rendering someone's own home is novel — delightful to most, unsettling to some. First real batch small (≤100), read replies/complaints, then scale.
- **Do-not-mail:** anyone who asks is suppressed permanently (same "dead is dead" rule as the outbound DB).

## Counsel questions for Ray (gate #15 — blocks the scaled machine, NOT the sample)
1. **Imagery licensing — the whole gate.** Google Street View/Maps terms restrict storing, deriving from, and altering imagery; "AI-paint a patio onto a Street View frame and mail it" very likely violates them. Options to put to counsel: county assessor photos (usage terms?) · licensed aerial/streetscape providers (Nearmap/EagleView class — cost?) · **owner-captured photos** (drive-by, public vantage — clean, but only scales to the radius someone will drive). Which imagery source can feed steps 2–3 at scale?
2. County record + any list-broker data: permitted-use for solicitation in ST (expected yes — this is the entire direct-mail industry — confirm).
3. Any ST/local rule on solicitation mailers to new homeowners (expected none beyond honesty basics; confirm).

## The 3-address sample (pre-signature — the ONLY build allowed now)
The pitch artifact for the signing meeting, and it **dodges the counsel gate entirely**: the Founder (or Client Owner) photographs 3 recent-sale houses from the public street — his own camera, no third-party imagery, no ToS. ~a day of work:
1. Pull 3 real recent sales near Client Owner's territory from POLARIS — one patio candidate, one fence, one pool surround.
2. Drive-by photo of each (public vantage).
3. One Higgsfield concept render each (image-first, premium bar, labeled concept).
4. Three postcard fronts/backs (Sample Client brand — Canva kit) + three live QR landing pages (launch.json entry + verified URL before anything is shown).
5. Stage as the meeting close: *"Module 1 saves Charlene and you hours every signed job. Module 2 is this — it fills the pipeline those hours serve. Both come with the signature."*
**Cap:** if Client Owner doesn't sign, this stops at 3 addresses. No machine for an unsigned client (audit lesson: the gap is commercial, not technical — build after the yes).

## Reuse (why this is a module, not a favor)
- **Sample Product — same rig, different feed.** Postcard + per-address QR + landing page + scan-as-intent, fed by verified storm events instead of sold-homes: "your roof took verified hail June 12 — scan for the report." Build once, two engagements amortize it.
- **Generalizes** to any outdoor trade (fence, pool, roofing, landscape) → a **Marketing-pillar module** ("vision-qualified personalized direct mail") in `processes/ai-os-modules.md` once proven on Sample Client. Prove first, generalize second.

## Open decisions
1. Imagery source for scale (counsel + cost — gate #15). 2. Render-on-scan vs pre-render top-N (default: on-scan). 3. Module pricing — Polo (per-batch cost+margin vs bundled in retainer; leans per-batch: it has direct per-unit costs and visible ROI). 4. Print API vendor (Lob-class; pick at build, not now).

## Explicitly not doing
- Scraping Zillow/Redfin/realtor.com (ToS; county data is the same facts, free and clean).
- Mailing at scale before gate #15 clears and the sample has survived the taste test.
- Diagnosing a specific house's condition in copy (invitation only — see guardrails).
- Any yourco branding on any prospect-facing surface.
