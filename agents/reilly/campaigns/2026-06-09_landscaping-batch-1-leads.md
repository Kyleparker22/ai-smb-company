# Batch 1 — Sourced Leads — Landscaping US National

**Campaign:** `/agents/reilly/campaigns/2026-06-08_landscaping-us-national-batch-1.md`
**Sourced by:** Reilly — 2026-06-09
**Status:** 🟡 STAGED — awaiting the Founder's batch approval (gate 7). NOT loaded into a live Instantly campaign yet; nothing sends until warmup + 10DLC + Reed asset clear.

## Source run
- **Source:** Vibe Prospecting (Explorium) — single-source for this first batch. Instantly SuperSearch + Outscraper not connected in this session; full tri-source dedupe-merge deferred to the national 2,000+ build.
- **ICP filter:** NAICS 561730 (Landscaping Services) · US · 1–50 employees · owner / c-suite · has email + phone · website keywords {lawn care, landscape maintenance, landscaping services, hardscape, lawn maintenance}
- **Raw pull:** 25 prospects. First unfiltered pull caught landscape *architects*, interior plantscaping, farms, and an e-commerce plant shop; the keyword-tightened re-pull returned clean NAICS 561730 service firms at $1–5M revenue.
- **Vibe dataset (canonical, full 25 rows + contacts):** `ds-32bf2a29-e683-4c1c-972c-f90fbaa3af43` → https://app.vibeprospecting.ai/lists?dataset_id=ds-32bf2a29-e683-4c1c-972c-f90fbaa3af43
- **Spend:** 150 credits (25 rows × 5/contact-enrichment). 192 credits remaining.

## Stage-1 ICP-fit gate (applied)
Reilly excludes off-ICP rows before staging. Excluded from the raw pull: Lively Root (e-commerce plants), Panoramic Farm (farm ops), Harold Leidner (landscape *architecture* + finance contact). Kept: owner/operator-led landscaping & lawn-maintenance service firms.

## SMS state suppression (applied at batch time)
Suppressed states for SMS per the Founder 2026-06-08: **FL, WA, OK, MD, NY, CA**. Leads in those states are **email-only** (all 3 emails still send; their 3 SMS touches are dropped). Flagged inline below.

## Verified ICP leads (contacts enriched)
| # | Owner/contact | Company | City, ST | Title | Pro email (status) | Mobile | SMS? | Fit |
|---|---|---|---|---|---|---|---|---|
| 1 | Ted Glaser | Summit Lawns | Lincoln, NE | CEO | ted@summitlawnslincoln.com (valid) | +1 402-326-3623 | ✅ | Strong — owner-led lawn care |
| 2 | Max Broman | Frdm Turf | Draper, UT | CEO | max@frdmturf.com (valid) | +1 801-913-0715 | ✅ | Strong — turf/lawn |
| 3 | Valerie Matthew | Plant This Outdoor Services | Sanford, FL | Owner/CEO | (in dataset) | (in dataset) | ⛔ FL → email-only | Strong — owner, commercial lawn maint. |
| 4 | Jerry Cavitt | Ethoscapes | Sugar Land, TX | COO/CFO | jcavitt@ethoscapestx.com (valid) | +1 469-744-8347 | ✅ | Good — commercial landscaping |
| 5 | Kimberly Jenkins | Clair Lagon USA | Powder Springs, GA | CEO | kimberly@clair-lagon.com (valid) | +1 954-649-4675 | ✅ | Good — landscaping/water features |
| 6 | Ross Blair | The Native Land Company | Parrish, FL | President/CEO | blairr@nativelandcompany.com (valid) | +1 941-705-0563 | ⛔ FL → email-only | Good — environmental/landscape |
| 7 | Shawn Schmidt | LNG Landscapes | Woodbury, MN | CEO | (in dataset) | (in dataset) | ✅ | Watch — possible person↔company match noise; verify before send |
| 8 | Vicki Seredich | New Vista Enterprises | Cleveland, OH | CFO | vickiseredich@newvistaent.com (catch-all) | +1 440-478-3774 | ✅ | Lower — finance contact, catch-all email; prefer owner if enrichment finds one |

> Rows 9–25 live in the Vibe dataset above (full contacts included). Reilly's next automated step runs Gemini Flash enrichment across all 25 to build a research card per prospect (3–5 sourced points + 1 pain hypothesis) and to drop any prospect missing a usable `{first_name}` or professional email. Catch-all / personal-only contacts are deprioritized for deliverability.

## Personalization readiness
Required vars present for the verified set: `{first_name}` ✅, `{company_name}` ✅, `{city}` ✅. Drop any touch missing `{first_name}` per copy-structure.

## Sample research notes (for the strongest leads)
- **Summit Lawns (Ted Glaser):** Brand voice is "Chick-Fil-A-level customer experience for lawn care," tech-forward, anti-"rusty truck" positioning. Pain hypothesis: growth-minded owner who already cares about CX → intake speed + review automation will resonate hard. Lead lead.
- **Frdm Turf (Max Broman):** CEO from a sales/BD background, turf focus. Pain hypothesis: sales-minded owner losing inbound to slow estimate turnaround.
- **Plant This (Valerie Matthew):** Owner-operator, central FL commercial lawn maintenance, multi-metro (Orlando/Jax/Lakeland/Tampa). Pain hypothesis: multi-market scheduling + intake load on one owner. **FL → email-only.**

## Open items before this batch can launch
1. **the Founder batch approval (gate 7)** — approve this list (or trim/expand).
2. ✅ **Reed Email-2 asset — DONE.** Animated demo produced (Higgsfield + Descript), the Founder-approved + published + registered 2026-06-09. https://share.descript.com/view/L6EdW0JYGQJ (inline ~5s GIF preview generated — Canva `DAHMG8SO338`).
3. **10DLC (gate 9)** — required for the SMS touches; FL/WA/OK/MD/NY/CA already suppressed.
4. **Warmup (gate 10 — amended 2026-06-09)** — email may begin on a health-gated low-volume ramp (~June 22 target, ≤10/inbox/day) once warmup metrics are healthy; no longer waiting for full warmup. See `/decisions/2026-06-09_reilly-early-warmup-ramp.md` + send plan in the campaign file.
5. **DNC + suppression scrub (gate 11)** — run before push to Instantly; suppression list currently empty.

— Reilly, Sales
