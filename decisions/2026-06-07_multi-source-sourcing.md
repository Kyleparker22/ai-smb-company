# 2026-06-07 — Multi-source sourcing pipeline (dedup-and-merge across Outscraper + Instantly + Vibe)

> **BUILT 2026-06-14.** Now code, not just a plan: `runtime/outscraper.py` (Google Maps source), `runtime/instantly.py → supersearch()` (Instantly lead-finder), and `runtime/sourcing.py` (the engine: normalize → dedupe by domain/phone/name → stage with `source[]` tags; dry-run by default). Vibe (an MCP) is fed in via `--vibe-json`. Run + keys: `runtime/sourcing-setup.md`. Keys are yours (gitignored); running costs money; sourcing only — sending stays gated.
>
> **AMENDED 2026-06-15** by `decisions/2026-06-15_prospect-data-architecture.md`: the merge target is now an **Instantly campaign (the cold system of record), not the CRM.** Cold leads stage into Instantly; they graduate to the CRM only on a warm reply (`runtime/promote.py`). The dedupe-and-merge below still holds — only the destination changed.

## Decision
For each YourCo vertical, Reilly runs **all approved sourcing tools in parallel**, normalizes results to a common schema, deduplicates hierarchically, merges into one canonical prospect list, and tags each record with the set of source tools that surfaced it. Single-tool primary sourcing is retired.

## Context
Earlier today's amendment to the outbound-sales-stack decision recommended a per-vertical primary-source choice (Instantly for trades, Vibe for knowledge work) after the Vibe coverage test exposed Explorium's weak trade-SMB coverage. the Founder's read after looking at the data more carefully: each tool catches different prospects, and locking to a single primary leaves coverage on the table. Stronger architecture: source from all three, dedupe, merge.

## Options considered
- **A. Single primary source per vertical (the earlier amendment's choice).** Rejected — caught the coverage-test learning but stopped one step short. Still leaves prospects in the under-represented sources untouched.
- **B. Sequential cascade (Outscraper → if thin → Instantly → if thin → Vibe).** Rejected — adds latency and complexity for a marginal cost saving; the parallel approach is faster, cleaner, and yields the cross-source confidence signal.
- **C. Parallel multi-source with dedup-and-merge.** **Chosen.**

## Why this won
- **Maximum coverage.** Each tool has different database depth; the union catches more than any single one.
- **Cross-source match is itself signal.** A prospect appearing in all three sources is high-confidence; a prospect appearing only in Outscraper is by definition a weak-digital-footprint local SMB — exactly the ICP profile for trades. *The "in only Outscraper" tag is a positive ICP indicator for landscaping, not a quality concern.*
- **Tool redundancy.** If any single tool's data quality dips, pricing changes, or API breaks, the pipeline keeps operating on the other two.
- **Future-proofs the architecture.** Adding Leadbay (v1) for predictive scoring, replacing Vibe if a better tool emerges, or swapping Outscraper for a different scraper all plug into the same parallel structure without restructuring the pipeline.
- **Per-vertical source sets stay flexible.** Polo decides which tools are in the set for each vertical — Outscraper drops out for verticals where Maps is weak (law, wealth, insurance); the rest stays the same.

## The pipeline

```
[the Founder: vertical X + filters]
            │
            ▼
Polo's source set for vertical X (e.g., for landscaping: Outscraper + Instantly + Vibe)
            │
            ├──── Outscraper (Google Maps API)
            ├──── Instantly SuperSearch (Instantly API)
            └──── Vibe Prospecting (Explorium MCP)
                  (each runs in parallel)
            │
            ▼
Normalize each tool's output to common schema:
   { name, domain, phone, address, owner, employees, revenue, source[] }
            │
            ▼
Dedup hierarchically:
   Tier 1: match on domain         (highest confidence)
   Tier 2: match on phone          (high confidence; allow 1-digit normalization)
   Tier 3: match on name + city    (lowest; flag for human review when collision count is high)
            │
            ▼
Merge: union of unique records; aggregate source[] field per record
            │
            ▼
Cross-source match tag:
   all-three   → 3 tools surfaced this record
   two-source  → 2 tools
   single-source → 1 tool (Outscraper-only, Instantly-only, or Vibe-only)
            │
            ▼
Canonical merged prospect list → enrichment → research → copy → send
```

## Per-vertical source sets (Polo decides; lands in `/pricing/v0/<vertical>.md` under Sourcing)

| Vertical type | Default source set | Reason |
| --- | --- | --- |
| Trade/services SMB (landscaping, roofing, hardscaping, plumbing/HVAC) | Outscraper + Instantly + Vibe | Cross-source coverage maximizes yield in verticals with weak digital footprints |
| White-collar / knowledge work (law, wealth, insurance, professional services) | Vibe + Instantly | Google Maps weak for these verticals' decision-makers; skip Outscraper |
| Hyper-local single-metro (any vertical) | Outscraper + Instantly | Vibe optional if vertical is also tech-equipped |
| Predictive (v1 with Leadbay) | Vertical's base set + Leadbay scoring overlay | Leadbay ranks, doesn't source — orthogonal layer |

## Cost
- Outscraper: ~$0.001–0.003 per result, pay-per-use
- Instantly SuperSearch: bundled in Hyper CRM tier ($97/mo); usage credits within tier
- Vibe Prospecting: credit-based, usage-only

For a first 1,000-prospect campaign per vertical, total sourcing cost is in the $10–30 range — trivial relative to a single closed engagement ($20k+).

## Implementation notes
- **Outscraper has REST API; no MCP.** Reilly calls it via HTTP.
- **Instantly SuperSearch has programmatic API.** Reilly drives it through Instantly's API.
- **Vibe is MCP-native.** Reilly invokes conversationally through MCP tools.
- The three different invocation styles are abstracted behind the "source step" in Reilly's pipeline — downstream stages (enrichment, research, copy, send) operate on the normalized merged list and don't care which tool surfaced each record.
- **Common schema mapping** is a one-time prompt/format-spec investment; gets captured as a reusable primitive into `yourco-template` once it's stable.

## Pre-campaign gate update
The previous "Vibe coverage test" gate generalizes to a **source-set coverage test**:
- Run the planned source set for the vertical on a representative query
- Report each tool's individual yield (for ongoing per-tool monitoring)
- Compute deduplicated merged total
- Escalate to the Founder if merged total is materially below the vertical's market-size threshold
- The threshold is itself a Polo per-vertical number, landed in the vertical's pricing/playbook doc

For landscaping, the threshold is **≥ 2,000 deduplicated US prospects** before national campaign launch (~5% of estimated US qualified market). Tampa-Bay-only campaigns use a proportional metro-scoped threshold.

## Reversibility
- **Easy to reverse.** Drop any single tool from the source set per vertical (Polo decision); pipeline keeps working on remaining tools.
- **Harder to reverse:** the dedup schema. Pick the right common-schema fields upfront; changing them later requires reprocessing existing prospect records.
- **Revisit if:** one tool consistently catches < 10% incremental over the other two (consolidate to two); a fourth tool emerges with materially differentiated coverage (add a parallel branch).

## What this unlocks
- Reilly's first real campaign on landscaping can use the cross-source merged list directly
- Polo's vertical playbooks now carry three layered decisions: pricing, channels, source set
- Atlas's Monday briefing can report cross-source distribution as a coverage-health signal
- The architecture supports adding Leadbay (v1) as a scoring overlay without restructuring sourcing
- Outscraper-only matches become a positive ICP-indicator label, not a quality concern

## Supersedes
The "primary sourcing tool per vertical" framing from the earlier same-day amendment to `decisions/2026-06-07_outbound-sales-stack.md`. Polo's per-vertical decision is now "source set" + "per-source filters," not "single primary."
