# The Gap Audit — the negative-space review

> **Why this exists.** The OS is good at improving what runs and at chasing the active thread. It was *not* good at noticing what's **absent** — a surface or process that simply doesn't exist generates no bad run to observe, so it never gets flagged. On 2026-06-12 the founder had to surface that the client-facing console didn't exist (`learnings/strategy/2026-06-12_client-facing-gap.md`). This audit installs the missing loop: a scheduled hunt for what *should* exist but doesn't. **Owner: Brett** (strategy/pre-mortem). Cadence: monthly + at every major build milestone or before any launch gate.

## The discipline
Most reviews ask "is what we built working?" This one asks the inverted question: **"walk the whole journey — what can't the actor do or see yet?"** Absence, not defect.

## The two sweeps

### Sweep 1 — the client lifecycle (walk it end to end, name the holes)
For each stage, ask "what does the client experience here, and what's missing?"
1. **Discover** — can a prospect find and understand us? (site, collateral, demos)
2. **Believe** — can they see proof before buying? (Instant Employee, eval-gated seal, glass box)
3. **Buy** — is the path to signed clean? (proposal, pricing, contract, e-sign)
4. **Onboard** — first 48h: do they know what's happening? (discovery, go-live note)
5. **Use daily** ← *the stage that was empty.* Can they watch it work, approve, intervene, reach a human? (**client console**)
6. **See value** — do they see outcomes + reliability without asking? (console metrics + weekly readout)
7. **Expand** — is the next employee an obvious, easy yes? (Bird's expansion path)
8. **Leave / pause** — can they pause or offboard cleanly, with their data? (trust + exit)

### Sweep 2 — the company surfaces (does each have an owner + an artifact?)
For every function (sales, delivery, eval, finance, compliance, client experience, runtime, security): **is there a DRI, and is there a living artifact the next run reads?** A function with no owner or no artifact is a latent gap. The client-experience function had neither until this audit.

### Sweep 3 — wiring consistency (is each new thing wired all the way through?)
A new agent or loop is usually built in pieces, and a piece gets missed. Check, mechanically: **every loop in `runtime/prompts/` has (a) a matching `runtime/systemd/yourco-<loop>.{service,timer}`, (b) an entry in `dashboard/data.json` loops[] with the count in metrics matching, and (c) a Slack channel in `runtime/slack-channels.md` + the listener maps.** A loop missing its systemd unit can't run; one missing its dashboard entry makes the count dishonest. (Mario's AEO/GEO loop shipped without its unit or dashboard entry — caught in cleanup, not by a run. This sweep is so it's caught by a run.)

## Output (each run)
A dated list in `loops/gap-audit/` (or appended here): each gap = **what's missing · which stage/function · who should own it · build-now or backlog.** Anything launch-critical → into `processes/launch-runbook.md`. Anything that reveals a *pattern* of missing → a `learnings/` entry so the cause, not just the instance, is fixed.

## The standing question (for the assistant + every agent)
At the end of any build sprint, before "done": **walk acquire → buy → onboard → use daily → see value → expand and name what's unbuilt.** Don't only chase the stated next item. The gap is usually in the stage nobody was asked about.
