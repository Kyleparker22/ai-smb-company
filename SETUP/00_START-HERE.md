# Build your company — start here

> **You are starting from zero.** Nothing in this repo is set up yet. No entity, no domain, no
> runtime, no agents. Every page below tells you what to do, in the order it has to happen, and ends
> with a **Done when** line so you know whether it worked.
>
> ⚠️ **Where you see completed-looking content — a filled roster, an example loop artifact, a worked
> client engagement — that is the company this template came from, kept so you can see the shape.**
> It is labelled wherever it appears. None of it is yours until you build it.

## Before anything else

- [ ] **[Install what you need](00a_WHAT-YOU-NEED-INSTALLED.md)** — Python 3.10+, git, and the
      Claude Code CLI. Fifteen minutes. Everything below assumes it is done, and **3.10 is a hard
      floor** — parts of this are syntax errors on 3.9.

- [ ] Read `00_README.md` — the map, and the **five reality levels** that tell you which folders hold
      real records and which hold examples. Fifteen minutes, and it prevents the single most common
      mistake with this repo: reading an example as a fact.
- [ ] Read `RENAME-THIS-FIRST.md` and do the find-and-replace. Renaming later is worse.
- [ ] Decide what your business actually does. **This template does not decide that for you** and
      cannot. Everything below is machinery; the machinery is worthless pointed at nothing.

## The build, in dependency order

Each step is blocked by the one before it for a real reason, not tidiness.

| # | Step | You will have | Blocked by |
|---|---|---|---|
| **00a** | [What to install](00a_WHAT-YOU-NEED-INSTALLED.md) | a laptop that can run any of this | nothing — start here |
| **01** | [Entity, EIN, money](01_ENTITY-AND-MONEY.md) | a legal entity, an EIN, a business bank account | 00a |
| **02** | [Identity](02_IDENTITY-AND-EMAIL.md) | a domain, a work email, a brand | 01 (vendors ask for the entity) |
| **03** | [The repo](03_THE-REPO.md) | this repo, renamed and yours | 02 (git identity is your email) |
| **04** | [Claude Code + MCPs](04_CLAUDE-CODE-AND-MCP.md) | a working local environment | 03 |
| **05** | [The always-on runtime](05_THE-RUNTIME.md) | a VPS running one loop unattended | 03, 04 |
| **06** | [The agents](06_THE-AGENTS.md) | your first agent, on a rung | 05 |
| **07** | [CRM, HQ, the app](07_CRM-HQ-AND-APP.md) | your own dashboards, reading your own data | 05 |
| **08** | [Go to market](08_GTM-MACHINE.md) | a site, an offer, a referral motion | 02, 07 |
| **09** | [Delivery](09_DELIVERY.md) | a repeatable way to run a client | 07, 08 |
| **10** | [Back office](10_BACK-OFFICE.md) | books, insurance, a counsel-gate tracker | 01 |
| **11** | [The guardrails](11_GUARDRAILS.md) | checks that catch your own drift | everything above |

## The shortest path to something real

If you want one working thing today rather than the whole system in a month, do **01 → 03 → 04**,
then the first half of **05** — a single loop on a timer, writing one dated artifact.

That is the smallest complete version of this idea: **a scheduled job that leaves a record the next
run reads.** Everything else here is that pattern repeated. Get one working and the rest is volume.

## How to tell whether a step actually worked

Each page ends with a **Done when** line. They are deliberately concrete — *a timer fired and wrote a
file*, not *the runtime is configured*. If you cannot point at the artifact, the step is not done.

## The rule that governs every page

**You send; agents draft.** Nothing here emails, texts, posts, or signs on your behalf. Agents
produce copy and a link and stop. The approval gate on the runtime enforces the technical half
(`deny: send, delete, Bash`); the cultural half is that a draft is the deliverable.

Of everything in this repo, that is the part worth keeping even if you throw out the rest.

## Two honest warnings

**This came from a pre-revenue company.** The machinery is real and runs. The results did not exist
when it was extracted — no signed clients, no referral partners. Where a page describes an outcome,
it is describing an intention. Keep that labelling in your own version; a system that tells you what
it cannot prove is worth more than one that quietly implies it can.

**Nothing here is legal, tax, or financial advice.** Step 01 records what one company did. Your
state, your partners, and your tax situation change the answer. Get counsel before you file anything.
