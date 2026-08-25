# Sample Product — subscription economics (v0, assumption-stated)

Per roofing company, per month. Ranges are honest — two inputs are quote-based
(commercial weather/property data). Polo + the Founder lock the final numbers; this is
the model to reason with. Pre-revenue — nothing validated with a paying customer yet.

## The one variable that swings everything: data licensing
Who pays for the premium data (Xweather / HailTrace / property records)?
- **BYO keys** — the roofer brings their own Xweather/HailTrace accounts (Nick already has Xweather). Lowest yourco cost, a little onboarding friction.
- **yourco bundles** — yourco licenses commercial weather + parcel data (better product, one bill for the client), but that's a real cost that only makes sense at volume where it's amortized across many roofers.

Everything below is split by that choice.

## Monthly cost to operate (COGS) — per company
| Line | BYO keys | yourco bundles data |
|---|---|---|
| NOAA / NWS data | $0 | $0 |
| Hosting / infra (amortized) | $5–15 | $5–15 |
| AI verification tokens (reads reports; Sonnet/Haiku) | $5–30 | $5–30 |
| Twilio SMS (number + A2P 10DLC + messages) | $8–25 | $8–25 |
| Xweather (commercial, allocated) | $0 (client's key) | $50–300+ (quote-based; wholesale at volume) |
| Property / parcel data (address tool, canvass) | $0–30 (per-lookup) | $30–150 |
| HailTrace-class hail (optional) | $0 (client's) | $50–200 |
| **Infra + data subtotal** | **~$20–70** | **~$150–650** |
| Operated support / tuning (labor, allocated) | $30–120 | $30–120 |
| **Total COGS / company / mo** | **~$50–190** | **~$180–770** |

*Support labor drops per-client as onboarding + monitoring get automated; it's the real cost at scale, not infra.*

## What to charge (value-based, not cost-plus)
A roofing restoration job is ~$10–15k. Being first to the neighborhood, catching a
storm they'd have missed, or not wasting a crew on a false one is worth *one job* —
which pays for a year of the tool. Comps: hail-map tools $50–300/mo; roofing CRMs
(JobNimbus/AccuLynx) $100–300/user/mo; bought leads $50–200 each. Sample Product
replaces several of those *and* the manual hour + adds claim defensibility.

| Tier | Per company / mo | What's included |
|---|---|---|
| **Core** | **$300–500** | Verification + real-time alerts + one-tap dispatch + crew app. BYO data keys. |
| **Pro** | **$800–1,200** | + property overlay & canvass routes, claim packets, address claim-lookup, learning + ROI. yourco-bundled hail data. |
| **Command / multi-company** | **$1,500–3,000+** | Multi-tenant (Nick's 3 companies), multiple crews, priority operated support. |
| **Add-ons** | per-crew seat $25–75 · extra company $500–1,000 | scales with headcount |
| **One-time** | setup $500–2,500 + A2P 10DLC registration | onboarding + carrier reg |

## Margin
- **Core @ $400, BYO keys, ~$50–190 COGS → ~55–85% gross margin.**
- **Pro @ $1,000, bundled data, ~$180–770 COGS → ~25–80% gross margin** (tighten by bringing data wholesale + automating support).
- Healthy either way, and it improves with scale (data wholesale + support automation). Consistent with yourco's moat/margin thesis: the value is reliability/verification, the compute is cheap.

## Recommendation
1. **Launch Core at ~$400/mo, BYO data keys** — highest margin, lowest friction, and Nick already has Xweather. Proves willingness-to-pay with almost no yourco data cost.
2. **Pro at ~$1,000/mo** once we're bundling data at wholesale and the claim/canvass/learning surfaces are live — that's where the real value (and stickiness) is.
3. **Pin the Xweather commercial quote first** — it's the #1 cost unknown and it decides whether "bundled" pricing has margin. Get a wholesale quote before committing to Pro pricing.
4. Consider a **per-signed-job or rev-share** hybrid later (roofers understand it) — but flat subscription is cleaner to start and easier to forecast.

## Caveats
- Pre-revenue, assumption-stated — validate willingness-to-pay with Nick (and 1–2 others) before locking.
- Xweather/HailTrace/parcel pricing is quote-based; the ranges are estimates, not quotes.
- This is a **productized operated vertical** (like Conduit / yourco Care) — was parked as "subscription later." Revisit against `decisions/` if we productize.
