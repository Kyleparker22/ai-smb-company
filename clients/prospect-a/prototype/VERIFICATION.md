# AI Verification layer — read the reports, don't just count them

**Nick's ask:** *"I want the AI to read all of the reports though and make sure that
Nick isn't wasting his roofers' time with false or inaccurate reports. Especially
for claims afterwards."*

This is the yourco moat, made concrete. Two jobs:
1. **Pre-dispatch** — don't send crews on a thin or false report.
2. **Claim-grade** — the storm must hold up when the homeowner files (NOAA
   *measured* data is the insurance standard).

The rule engine (`storm_poc.py`) checks *sources agree + magnitude clears a
threshold*. This layer (`verify_ai.py`) has the AI **read the raw report text** —
the spotter remark, whether hail was **measured** or **estimated**, who reported
it — and judge credibility the way a sharp human would.

## The rubric (how it weighs evidence)
- **MEASURED beats ESTIMATED.** Airport/mesonet instruments (ASOS, AWOS, Mesonet, Buoy) are the insurance gold standard; "Public" / "Broadcast Media" / "social media" are estimates — weak on their own.
- **Read the remark against the number.** A report logged as `1.00" hail` whose remark says *"pea to quarter size"* is overstated → downgrade.
- **Corroboration up, contradiction down.** Multiple independent measured reports (or a report + an NWS warning) raise confidence; conflicting sizes lower it.
- **Skew skeptical.** A wasted crew trip and a bad claim both cost Nick more than a missed marginal storm.

Output per storm: `dispatch` (GO / HOLD / REJECT) · `confidence` · `claim_grade` (bool) · `verified_hazard` (what the evidence *actually* supports) · `reasoning` · `red_flags` · `claim_packet`.

## Proven on real data (this week's flagged storms)
The rule engine flagged all three as **HIGH**. Reading the actual reports changes the call:

| Storm (rule-engine flag) | What the reports actually say | AI verdict |
|---|---|---|
| **Duval 6/23 — WIND 60mph** | A dozen **MEASURED** airport/mesonet stations 44–60mph; ASOS KNIP measured a 60mph gust | **GO · HIGH · claim-grade** — real, measured, documented |
| **Calhoun 6/30 — HAIL 1.00" + WIND 69mph** | Wind = **measured** ASOS 69mph + 911 downed-trees (solid). Hail 1.00" = **one ESTIMATED broadcast-media** report ("mothball size"), *contradicted* by a pea-sized report | **GO on WIND** (claim-grade); **hail flagged** — dispatch for wind, don't lead the claim with hail |
| **Palm Beach 6/24 — HAIL 1.00"** | The only hail report is **one PUBLIC estimate**: *"Pea to quarter size hail."* The 1.00" number **overstates** the remark | **REJECT / HOLD** — marginal small hail, single unverified estimate; likely a wasted trip |

That Palm Beach call is the entire pitch: the threshold engine says "1-inch hail, go" and the AI says "that's a social-media pea-to-quarter guess — don't roll the crews." **This is Nick not wasting his roofers' time.**

## Claim packet (for `claim_grade` storms)
An insurance-ready evidence trail the roofer/adjuster can lean on — e.g. for Duval:
> **CLAIM EVIDENCE — Duval County, FL — 2026-06-23.** Peak wind **60 mph, measured** (ASOS KNIP, Jacksonville NAS, 21:26Z), corroborated by measured gusts of 52–56 mph at KNRB Mayport and downtown mesonet stations, plus an ASOS 49 mph at Jacksonville Intl. Source of record: NOAA Local Storm Reports (the standard insurance carriers use for wind/hail verification). Verified by yourco storm-command.

Because we **retain the evidence** (every report's source, measured/estimated flag, timestamp, remark — captured in `last_run.json`), the packet is auditable, not asserted.

## Where it fits the autonomy matrix
This is the eval/verification layer, not an approval bypass. Nick still taps to dispatch (R1). The AI does the *credibility reasoning* he does by hand — and gates out the junk before it ever reaches his approval screen. As its verdicts prove out against reality (Kolby-style eval), the low-confidence auto-holds can earn toward full autonomy.

## Cost note (this changes the economics — honestly)
Earlier the engine used ~$0 in AI tokens because it was pure rules. **This layer adds real token cost** — the AI reads a few dozen report snippets per storm. It's still modest: a handful of storms/day, ~1–2k tokens each. Default model is `claude-opus-5`; for production volume set `VERIFY_MODEL=claude-sonnet-5` (or `claude-haiku-4-5`) — plenty for reading remarks, far cheaper. Rough order: **cents to low-dollars per day.** Per yourco's model, a token bill that prevents wasted crew trips and strengthens claims is money well spent. Updated in `cost.md`.

## Run it
```
pip install anthropic
export ANTHROPIC_API_KEY=...        # or add to .env
python3 storm_poc.py && python3 verify_ai.py     # -> verified_ai.json
```
Off unless the key is set — the engine runs fine without it (verification enriches; it never blocks the pull). Or run the same rubric as a runtime `claude -p` step (the yourco loop pattern) with no key.
