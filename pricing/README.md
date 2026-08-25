# /pricing/

YourCo's pricing system. **Owned by Polo** (`agents/polo/`); **the Founder locks every number.** Source of
truth for what anything costs — every other surface in the repo points here rather than restating.

> ⚠️ **Pre-revenue.** These are positioning ranges, not validated prices. Nothing here has been paid
> by anyone. Tier *names* are locked; most tier *prices* are still Polo's v0 proposal awaiting the Founder.

## The unit of sale (since 2026-06-22)

**The AI OS tier ladder — horizontal, not per-vertical.**
`decisions/2026-06-22_horizontal-positioning-and-os-tiers.md` · prices in **`v0/os-tiers.md`**.

| Tier 🔒 | Agents (guide) | Implementation | Retainer |
|---|---|---|---|
| *on-ramp — single employee* | 1 | $1,000–5,000 | **$1,500** floor · cap 3, then graduate |
| **Core** | ~3 | $2,000–2,500 | $3,000–4,000 |
| **Suite** | ~5 | $2,500–3,500 | $4,500–6,000 |
| **Operation** | ~7 | $3,500–4,500 | $6,500–8,000 |
| **Command** | up to 10 | $4,500–5,000 | $8,500–10,000 |

Agent count is the *included* guide, **never a meter** — price on scope and the reliability SLA.
The ladder is a split of the envelope Polo locked 2026-06-16 ($2–5k + $3–10k/mo), not a new model.
**The Audit is the front door that sizes which tier fits, and it is currently free** (`v0/audit.md`).

## Every file

| File | What it is |
|---|---|
| **`v0/os-tiers.md`** | **Start here.** The four priced tiers, the on-ramp, Command overage, and the no-inversion guardrail (3 à-la-carte employees cap at $2,500 so the $3,000 Core floor is always a step up). |
| `v0/audit.md` | The Audit. **$0 since 2026-08-16** — the $1,000/$1,500 fees are suspended, not deleted, and the file records exactly what free costs. |
| `v0/vertical-ranges.md` | The locked envelope the ladder splits, plus the three within-band levers: job/customer value · compliance lift · volume/complexity. |
| `v0/tier2-production.md` | Production/Tier-2 employee pricing — value-based, not cost-plus. |
| `v0/landscaping-hardscaping.md` | The one locked vertical (2026-06-07). Prices live; the *lead-vertical stance* was retired 2026-08-05. Still anchors the on-ramp floor. |
| `v0/ready-to-hire.md` | ⛔ **Parked.** Prices the Ready-to-Hire catalog, whose pages were dialled back to `_parked/` on 2026-06-22. Kept because `hire-config.js` preserves the numbers. |
| `CHANGELOG.md` | Every pricing change, dated, with reason and approval. |

## The rules that are *about* pricing rather than a price

1. **No specific prices on the public site.** Polo owns the bands; prices are shared in proposals,
   where scope is real. *(`v0/ready-to-hire.md` argues the opposite for catalog SKUs — that conflict
   is unresolved and parked along with the pages.)*
2. **No cold prospecting at unlocked prices.** Every new vertical gets its own locked pricing
   decision before Reilly's first cold campaign in it. **Reilly cannot quote an unlocked vertical** —
   route the request to Polo.
3. ⚠️ **Open (Polo, flagged 2026-08-05):** targeting went horizontal and warm-first, so most warm
   deals now land in *unlocked* verticals. Do the horizontal OS bands govern them? Undecided —
   Polo rules **before the first warm proposal in an unlocked vertical**.
4. ⚠️ **Watchpoint:** a low onboarding price can signal "automation gig" rather than "boutique
   implementation." Revisit after the first 3–5 closes on close-rate and retention.

## What changed, and why this page was rewritten

Until 2026-08-24 this README described the **pre-June model**: pricing as "vertical-specific, not
universal," with landscaping as the only locked vertical, and a Files list naming two of the seven
files here. It never mentioned `os-tiers.md` — the file every other doc in the repo points at. Two
model changes had happened underneath it (06-22 horizontal ladder, 08-05 horizontal targeting) and
the index never moved. A reader following it landed on a retired strategy and never found the unit
of sale.

**Versioning:** `v0` = June 2026 onward. Increment per-file when a number is materially revised
against real market data — which requires having sold something first.
