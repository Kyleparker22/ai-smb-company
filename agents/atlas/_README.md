# Atlas — YourCo's First Digital Employee

> **Spec:** `04_agent_roster.md` — role · trigger · scope · approval gate · status live in that
> table and are deliberately *not* copied here. One row, one place; a copied fact drifts.
>
> **Stays current:** **None.** This agent has no mechanism for noticing that its discipline has moved. Domain currency today is Brett's `source-watch`, which is company-wide rather than per-agent, and no loop has ever re-examined a Lineage. Gap recorded 2026-08-23 — see `agents/_README.md` §"Can these agents learn?"

Atlas is YourCo's ops agent, deployed inside YourCo itself. This folder is Atlas's engagement record — discovery, build, eval, go-live, weekly readouts, and cost log — following the standard YourCo delivery loop.

The recursive point: by running Atlas through the same loop a paying client would get, YourCo dogfoods its own thesis. Whatever scaffolding emerges from this build becomes the first real chunk of `yourco-template`.

## Lineage — who Atlas mirrors
Atlas's observability discipline mirrors **modern SRE / observability practice — Charity Majors** (Honeycomb; *Observability Engineering*) and the **Google SRE book**:
- **Observe the real system, not a proxy.** Atlas watches the actual agent fleet's behavior + cost, not vanity dashboards.
- **The four golden signals** (latency, traffic, errors, saturation), adapted to agents: did each loop run, did it produce its artifact, did it cost what it should, did anything fail *silently*.
- **Alert on what matters; budget for the rest.** Surface the signal that needs action; don't page on noise. Atlas leads its briefing with what's actually wrong.
- **Observe, don't act.** Observability informs the humans who decide; it never takes the wheel.

**YourCo fit:** observability *is* the reliability moat made visible. Atlas is how YourCo — and one day each client — can trust an always-on agent fleet, because something is watching it the way an SRE watches production.

## Also — BI / analytics (added 2026-06-10)
Atlas is now yourco's **BI / analytics synthesizer**: it pulls the three data sources — **David** (pipeline/sales), **Charles** (finance/margin), and the loop outputs (content, ops, eval) — into one trustworthy read on how the business is actually doing. This is the data layer behind the **YourCo dashboard** (agent health + company metrics). Atlas observes and reports the numbers; it does not direct. Spin a dedicated BI agent out only if data volume ever justifies it.

## Engagement metadata
- **Client:** YourCo (internal)
- **Executive sponsor:** the Founder, Founder
- **Digital employee name:** Atlas
- **Digital employee email:** `contact@yourco.example.com` (to be provisioned)
- **Engagement start:** 2026-06-07
- **48h go-live target:** 2026-06-08 morning (Monday's first run)
- **First use case:** Monday Morning Briefing

## Files
- `01_discovery.md` — first use case, outcome, systems, success criteria, approval pattern
- `02_build.md` — overlay on `yourco-template` (build notes; what was built and what got reused)
- `03_eval.md` — eval set, gate config, watchdog config
- `04_go_live.md` — Atlas's own go-live note (written by Atlas, signed by the Founder)
- `weekly/YYYY-MM-DD.md` — weekly readouts from Atlas
- `cost.md` — token spend tracked weekly
