# 2026-06-15 — Agent scope review: two re-scopes + one documented future-split

## Context
the Founder asked for a review of the agent roster: does any agent have too many jobs and need splitting? The test applied: the roster's own rule (**split only when a job needs a distinct tool stack *and* a distinct eval bar**) plus **separation of duties** (no agent both produces and approves its own work). Verdict: the roster is unusually well-decomposed already; only two agents crossed the line, and one boundary needed sharpening per the Founder's direction.

## Decisions

### 1. Webb's infrastructure → Kemba (re-scope, no new agent)
Webb bundled two disciplines: **web content + conversion** (pages, landing pages, on-page SEO, publishing, Calendly) and **infrastructure** (hosting, DNS, uptime, domains). Different tool stacks, different eval bars (a page's eval = converts / on-brand; infra's = up / secure / resolving).
- **Webb keeps:** the pages — build, content, on-page SEO, conversion, publishing Katie's editorial *to the site*.
- **Kemba takes:** hosting, DNS, uptime/monitoring, domains. Infra is infra; it belongs with the platform/runtime owner Kemba already is. DNS/hosting/domain changes = Kemba + must-approve.
- No new agent — a reassignment to an existing one.

### 2. Content org: function-split (the Founder's call)
Moved the content boundary from **by-format** (Reed=video, Katie=editorial) to **by-function**:
- **Katie = scripting + social distribution.** Writes all copy/scripts (editorial, carousel slide copy, video hooks, event-blast copy) applying `brand/writing-rules.md`, and **posts to the social platforms** (LinkedIn/X/IG/FB/YouTube). Owns the words and the social channel.
- **Reed = all content production.** Renders every asset from Katie's scripts — video (Higgsfield + Descript) AND social visuals (carousels, Shorts).
- **Webb = the site surfaces** — publishes editorial to the site (not social).
- **Pickle (when built) = designed *sales collateral*** (case studies, one-pagers, decks, battlecards) — kept distinct as a positioning discipline; whether its rendering folds into Reed too is the Founder's later call.
- The chain: **Katie scripts → Reed produces → Katie posts (social) / Webb publishes (site)**, under Luka's rules + the Founder's approval.
- **Why:** keeps each agent's eval bar clean as the channel roadmap (FB, YouTube Shorts, event-trigger blasts) expands — Katie never becomes a 5-platform *production* shop; production stays one accountable pipeline in Reed.

### 3. Reilly — documented future split + trigger (NOT now) → ⚡ EXECUTED same day
> **Update 2026-06-15:** the Founder chose to execute this split immediately rather than wait for the trigger. Done — see `decisions/2026-06-15_michelle-split-from-reilly.md`. Michelle (outbound copy/messaging) is spun up; Reilly keeps the machine. The "wait" reasoning below is preserved for the record.
Reilly carries two eval bars: **sourcing/campaign-ops** (ICP-fit, dedup, deliverability) and **messaging/copy** (reply-rate, brand, claims). This is the natural future fault line.
- **Decision: do not split now.** Reilly is pre-revenue and hasn't run one clean campaign — splitting an unproven agent is the shiny-tools trap. The copy eval is already partly externalized (Luka + Polo + the Founder).
- **Trigger to revisit:** when multiple verticals run concurrently and one eval bar strains the other. If it splits then: Reilly = SDR/sourcing + campaign-ops; a new agent = messaging/copy.

## Watch items (no action)
- **Katie channel sprawl** — fine as long as the job stays *write + post* and production stays with Reed. The moment Katie starts *producing* across platforms, peel it off (this decision pre-empts that by giving production to Reed now).
- **Atlas orchestrator elevation** — "observe" and "direct" are two jobs; the roster's revisit condition already refuses to fold them prematurely. Keep that discipline — it's the most important *non*-merge in the org.

## Files touched
`04_agent_roster.md` (Webb/Kemba/Reilly/Reed/Katie rows + boundaries + org chart), `clients/{Reed,katie,webb,kemba}/_README.md` (scope lines), `processes/content/content-engine.md` + `channel-roadmap.md` (produce/post language + owners).
