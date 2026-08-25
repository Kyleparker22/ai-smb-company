# <YOUR COMPANY> — AI OS Workspace

> **Fill this file in before you rely on it.** It is the always-loaded boot context: every agent
> session starts by reading it. An agent reasoning from a boot file that describes someone else's
> business will be confidently, fluently wrong — which is worse than knowing nothing.
>
> The original version of this file (the source company's, ~200 lines of specifics) is preserved at
> `_ORIGINAL-CLAUDE.md` **as a worked example of how dense and specific this should get.** Read it,
> then write yours. Do not simply un-comment it — almost none of it is true for you.
>
> Start at `SETUP/00_START-HERE.md`.

## What this business is

<!-- One paragraph. What you sell, to whom, and what makes it defensible. Be specific enough that an
     agent could tell a good-fit prospect from a bad one. -->

**Status: nothing built yet.** Update this line as you go — it is the fastest way for an agent to
avoid claiming things you have not done.

| Layer | Status | Notes |
|---|---|---|
| Entity / EIN / bank | ☐ not started | `SETUP/01` |
| Domain / email | ☐ not started | `SETUP/02` |
| Repo renamed, this file written | ☐ not started | `SETUP/03` |
| Local environment + connectors | ☐ not started | `SETUP/04` |
| Always-on runtime | ☐ not started | `SETUP/05` |
| First agent | ☐ not started | `SETUP/06` |
| CRM / dashboard | ☐ not started | `SETUP/07` |
| First customer conversation | ☐ not started | `SETUP/09` |

## What you sell

<!-- Your offer. If you have tiers or packages, name them and what separates them. Keep prices OUT of
     public-facing surfaces; they belong in proposals. -->

## The defensible part

<!-- What is hard to copy about how you deliver. If the honest answer is "nothing yet", write that —
     an agent that knows you have no moat will not claim one on a sales call. -->

## How to work in this OS

These carry over from the system this template came from. They are the part worth keeping.

- **You send; agents draft.** Nothing goes to a human outside the company without you sending it.
  Agents produce copy and a link and stop. The runtime's approval gate enforces the technical half
  (`deny: send, delete, Bash`); the cultural half is that a draft is the deliverable.
- **Change-one-sweep-all.** Canonical facts get duplicated across surfaces. When you change one,
  grep the repo and update every copy **in the same commit**. This is the most common failure mode in
  a repo like this, by a wide margin.
- **Refuse rather than guess.** A number a system cannot defend should not be printed. Say what is
  missing instead. Every dashboard here works that way and it is why they can be trusted.
- **Closed loops, not cron jobs.** A recurring process needs (a) a schedule, (b) an artifact the next
  run reads, (c) a feedback step, (d) a pattern written to `learnings/` that changes the next run.
  Without (d) you have a job that produces reports nobody reads.
- **Write the decision down.** Choices go to `decisions/`, observed patterns to `learnings/`,
  procedures to `.claude/skills/`, things ruled out to `rejections/`. Undecided → `inbox/`.
- **Secrets never touch chat.** They go straight into a gitignored env file — `runtime/.<service>.env`,
  never `runtime/.env.<service>` (`.gitignore` matches `*.env`; the reversed form commits your key).
- **Never bare `git add -A`.** Use `runtime/commit-scoped.sh "msg" <paths>` so concurrent sessions
  don't get swept into your commit.


## External-surface rules

Anything a person outside the company can see. Several of these were learned by violating them.

- **Agent names are internal.** External surfaces describe agents by *function*, never by name.
- **No prices on the public site.** Bands live in proposals; the site says what you do, not what it costs.
- **Client-facing surfaces are white-label** — the client's brand only, unless they agree to co-brand.
- **Public stats must be recent and cited** — 12–18 months, with the source named.
- **No fabricated proof.** No invented metrics, testimonials, logos, or implied endorsements. Pre-revenue
  means outcomes are described qualitatively, and that is fine.
- **You send; agents draft.** Repeated here because it is the one that matters most.

## Folder map

Full version with reality levels in `00_README.md`. The short form:

`SETUP/` the build guide · `runtime/` the loop machinery · `.claude/skills/` repeatable procedures ·
`crm/` `dashboard/` `app/` your surfaces · `agents/` the roster · `processes/` SOPs ·
`clients/` engagements · `decisions/` `learnings/` `rejections/` memory · `loops/` what ran ·
`finance/` the books · `inbox/` undecided

⚠️ **`Pre Build Ideas/`, `offerings/`, `clients/`, and every `_EXAMPLE_` file contain the source
company's material**, kept to show the shape. They are labelled where they appear. Nothing in them is
yours until you replace it.

### Also in this repo

- `Pre Build Ideas 2/` — see `00_README.md` for what lives here
- `_archive/` — see `00_README.md` for what lives here
- `_archive 2/` — see `00_README.md` for what lives here
- `agents 2/` — see `00_README.md` for what lives here
- `brand/` — see `00_README.md` for what lives here
- `brand 2/` — see `00_README.md` for what lives here
- `clients 2/` — see `00_README.md` for what lives here
- `crm 2/` — see `00_README.md` for what lives here
- `daily-logs/` — see `00_README.md` for what lives here
- `dashboard 2/` — see `00_README.md` for what lives here
- `finance 2/` — see `00_README.md` for what lives here
- `inbox 2/` — see `00_README.md` for what lives here
- `learnings 2/` — see `00_README.md` for what lives here
- `loops 2/` — see `00_README.md` for what lives here
- `offerings 2/` — see `00_README.md` for what lives here
- `playground/` — see `00_README.md` for what lives here
- `pricing/` — see `00_README.md` for what lives here
- `pricing 2/` — see `00_README.md` for what lives here
- `processes 2/` — see `00_README.md` for what lives here
- `runtime 2/` — see `00_README.md` for what lives here
- `send-package/` — see `00_README.md` for what lives here
- `send-package 2/` — see `00_README.md` for what lives here

## Founder

<!-- Your name, your email, what only you do. Agents route decisions to a person; tell them who. -->
