# Source-watch loop — the named-source steal sweep

> **Owner: Brett** (advisor / external landscape — `agents/brett/_README.md`). the Founder's ask (2026-07-29): whenever the named people/orgs post a new YouTube video or article, review it and surface anything yourco should implement or use. This loop is the standing version of the interactive tool-triage sessions — same filter, scheduled, batched weekly.

## Cadence
**Weekly, Friday 07:30 ET** — deliberately 30 min before Brett's Friday ideas drop (08:00), so the drop can read this artifact as fresh outside signal.

## The roster (the Founder owns membership; Brett proposes changes)
**Active — video (YouTube):**
| Source | Where | Why |
|---|---|---|
| **Greg Isenberg** | YouTube channel (@GregIsenberg) | Startup ideas / agency+AI models; already a proven source in the triage ledger (the Gannon pod came from his show) |

**Active — articles / posts:**
| Source | Where | Why |
|---|---|---|
| **Greg Isenberg** | gregisenberg.com newsletter (RSS/web) | Written twin of the channel |
| **Y Combinator** | ycombinator.com blog + YC Library; their YouTube channel counts for the video half too | Startup/AI canon; early signal on what founders are building |
| **The FoundedCEO Brief** | foundedceo.substack.com (RSS: `/feed`) | Business/startup/tech news with founder+VC insights (the Founder-named 2026-07-29) |

**Proposed — pending the Founder's confirmation (do NOT sweep until confirmed; listed so the roster shows the candidates):**
| Source | Type | Why |
|---|---|---|
| **Anthropic** (anthropic.com/news + engineering blog) | Articles | Highest-ROI candidate: the stack rides Claude, and the model-upgrade dividend is a standing pitch — release notes turn into client value the week they ship |
| **Every.to** | Articles | Daily AI×business essays; dense in exactly the operated-AI patterns yourco trades in |
| **Dan Martell** | YouTube | "Buy Back Your Time" — SMB owner-drain language; direct vocabulary for the Audit + exit-flip lane |
| **Acquiring Minds** | YouTube/podcast | SMB-acquisition interviews; feeds the ETA offering + exit-flip lane directly |
| **Alex Hormozi** | YouTube | SMB offers/pricing/guarantees mechanics (the risk-reversal steal lives in this world). ⚠️ steal mechanics only, never voice — hype register conflicts with `brand/writing-rules.md` |
| **Liam Ottley** | YouTube | The AI-automation-agency archetype's biggest channel — competitive intel: what prospects and cheap competitors are watching |
| **Colossus** (joincolossus.com) | Articles | Deep business essays; source of the Invisible Companies steal |
| **BizBuySell Insight Report** | Quarterly data | The exit-flip lane needs sourced listing-market stats anyway (the "most listings never sell" number) |
| **Cody Schneider** (companiesgraph.com; X/LinkedIn; proposed 2026-07-29 from the Isenberg episode triage) | Articles/posts | Highest-density practitioner feed on marketing-agent build patterns — the Marketing pillar's delivery playbook, published in public |

**Roster rules:** hard cap **10 active sources** (token + attention budget). **Quarterly prune:** any source producing zero steals/adopts in 90 days → Brett proposes dropping it in the artifact; the Founder confirms. Adding a source = the Founder names it (or approves a Brett proposal); edit this table.

## Method (compliance-bounded — Rafi posture)
1. **Detect new items since last run.** State lives in `loops/source-watch/state.json` (per-source list of seen item IDs/URLs + resolved YouTube channel IDs). YouTube via the **official channel RSS** (`https://www.youtube.com/feeds/videos.xml?channel_id=…`) or the YouTube Data API (already wired for Sadie); articles via RSS where it exists, else WebFetch of the source's index page. **No scraping of ToS-gated platforms; no paywall circumvention** — a paywalled item is triaged from its public preview or skipped with a note.
2. **Headline filter first.** List every new item; kill the obviously irrelevant on title/description alone (one line each). Cap the full sweep at **~15 new items/run** — if a backlog exceeds that, take newest-first and say what was dropped (no silent truncation).
3. **Read/watch what survives.** Articles: WebFetch. Videos: pull the **public captions/transcript** (the yt-dlp pattern sanctioned in `agents/sadie/_README.md`) — never fabricate a summary from a title.
4. **Triage each survivor against the standing filter** (`.claude/skills/tool-triage/` + `decisions/2026-07-05_tool-triage.md`): (a) the moat test, (b) compliance posture, (c) moves revenue or the reliability layer in ≤60 days. Check the ledger for prior art before calling anything new. **Deep-dive at most 2 items per run** — the rest get one-line verdicts.
5. **Verdict vocabulary is the house one:** adopt (rare) · steal-the-pattern · trigger-gate · skip.

## Output
- **Artifact:** `loops/source-watch/<YYYY-MM-DD>.md` — per-item: source, title, link, one-line verdict; a "Steals proposed" section on top (if any) with the specific pattern + which agent/doc would absorb it; a "Quiet" line when nothing cleared the filter.
- **Slack:** digest to **`#yourco-brett`** (internal, inside the approval gate).
- **Proposals, not edits (R1 by design):** this loop **never writes to `decisions/`, agent docs, or the triage ledger itself.** A proposed steal/adopt sits in the artifact + Slack digest until **the Founder approves**; absorption into the ledger/docs happens in a Cowork session (or the Founder tells Brett in-channel to log it). This mirrors the Sadie draft-then-approve pattern — the filter's judgment is cheap to run, expensive to get wrong silently.

## Failure modes / empty handling
- **Quiet week is a valid result:** "reviewed N items, nothing worth stealing" — never pad a verdict to look productive (loop contract).
- A source whose feed errors twice in a row → flag in the artifact for the Founder (don't silently skip forever).
- Transcript unavailable → triage from description and say so; never invent content.
- Pre-revenue guard: verdicts must name it when a shiny item would pull from the beachhead — that's part of the verdict, not a footnote (filter rule 7).

## Status
- [x] SOP + prompt + systemd pair + watchdog row + registry sanction (repo side, 2026-07-29)
- [x] **[VPS — the Founder]** timer installed + enabled 2026-07-29 (`list-timers` confirmed: next fire Fri 2026-07-31 07:30 EDT); smoke-test run same day. (Done during the VPS recovery — the box had been offline since ~07-25.)
- [ ] the Founder confirms/edits the proposed-sources table above
