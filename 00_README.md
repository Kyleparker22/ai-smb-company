# YourCo LLC — the AI OS workspace

> ⚠️ **TEMPLATE.** You are starting from zero — see `SETUP/00_START-HERE.md`. Filled-in content
> anywhere in this repo belongs to the company it was extracted from and is labelled where it
> appears. The reality levels below tell you which is which; read them first.


**Start here if you are a human.** `CLAUDE.md` is the machine's boot file — it loads into every AI
session automatically and is written for that. This page is the one written for you.

YourCo is a boutique AI-implementation consultancy. The motion is **Audit first → custom AI OS**.
This folder is not a set of notes *about* the company — **it is the company's operating system**:
the agents, the loops, the CRM, the dashboard and the client work all run out of here.

---

## The first thing to understand: five levels of reality

Several folders look alike and mean completely different things. Get this wrong and you will treat
a prototype as a product. Nothing in this workspace is a signed client yet.

| Folder | Reality level | What that means |
|---|---|---|
| `clients/` | 🟢 **REAL** | Actual engagements with actual people. Sample Client is at Proposal — **unsigned, pre-revenue**. |
| `offerings/` | 🟡 **DESCRIBED** | 33 specs.<!--#count: dirs offerings/*--> Written, argued, not built. |
| `Pre Build Ideas/` | 🟡 **BUILT, UNSOLD** | 76<!--#count: files Pre Build Ideas/*/BUILD.md--> running prototypes on invented data. No client, no revenue. |
| `playground/` | ⚪ **FAKE ON PURPOSE** | The sandbox. Synthetic data, real code — practice without touching production. |
| `_archive/` | ⚫ **DEAD** | History only. Never cite it for current state. |

## Where to go for what

| You want… | Open |
|---|---|
| The one-paragraph version of everything | `CLAUDE.md` |
| **The rules — how work is done here** | **`07_RULES.md`** |
| The full thesis: moat, what's parked, why | `01_company.md` |
| How a client engagement actually runs | `02_delivery_loop.md` |
| Who the agents are and what each is allowed to do | `04_agent_roster.md` |
| How the Founder runs the day (the cockpit manual) | `05_operating_rhythm.md` |
| The plan, the numbers, the principles | `06_business-plan.md` |
| What's open right now | YourCo HQ → **The Board** (`./show.sh`) |
| A guided tour you can click through | `START-HERE.html` |

## Every folder

This table must list **every** top-level folder — `runtime/consistency-check.py` fails if one is missing.

| Folder | Files | What's in it |
|---|---|---|
| `app/` | 6 | **The app** — one login in front of HQ, the CRM and the Connector Console, role-scoped, installable on a phone. The two dashboards have no auth of their own; this is what stands in front of them. Private/loopback until the launch-gate clears. |
| `Pre Build Ideas/` | 1265 | 76 industry prototypes, one folder each. Demo-before-Audit inventory. |
| `SETUP/` | 13<!--#count: files SETUP/*.md--> | **How the whole company was stood up**, in the order it has to happen — entity and EIN through to the guardrails. Written as a record: what was set up, **why**, and how it is used. Points at the docs that own the commands rather than restating them. No credentials anywhere in it. |
| `inbox/` | 1 | **Drop it here, decide later.** The one folder that doesn't make you know where a thing belongs before you keep it. `runtime/inbox_triage.py` *proposes* a destination and never files — routing between `decisions/`, `learnings/` and `rejections/` is judgment. Binaries are gitignored: staging, not storage. |
| `loops/` | 357 | Output of the recurring loops — one dated artifact per run. Written by the runtime, not by hand. |
| `clients/` | 351 | One folder per engagement, **and only clients**. Includes `_yourco-template/` (the golden template). |
| `agents/` | 268 | The 27 internal agents' workspaces. Moved here from `clients/` on 2026-08-07. |
| `runtime/` | 175 | The always-on VPS runtime: loop prompts, systemd timers, the approval gate, the registry. |
| `processes/` | 134 | SOPs beyond the delivery loop — outbound, partnerships, gates, walkthroughs. |
| `decisions/` | 115 | Dated log of settled calls and why. Each should carry a **trip-wire** — the condition that reopens it. |
| `offerings/` | 63 | Productized offerings parked as specs. See its `_README.md` for the line vs `Pre Build Ideas/`. |
| `learnings/` | 66 | Observed patterns. Agents write them; the next run reads them at Step 0 and adjusts. |
| `crm/` | 51 | The workspace-native CRM. Source of truth: `crm/data.json`. Owned by David. |
| `dashboard/` | 38 | YourCo HQ — the live command dashboard. Owned by Atlas. |
| `.claude/` | 19 | The skills library (21<!--#count: dirs .claude/skills/*--> repeatable procedures) + `launch.json`, which names every local server. |
| `finance/` | 18 | Revenue, runway, token spend, the 5-year model, legal docs. |
| `brand/` | 10 | Brand kit, design system, writing rules. |
| `rejections/` | 8 | The anti-library: what we decided **not** to do, and what would reopen it. |
| `pricing/` | 8 | Per-vertical and tier pricing. Polo owns the bands. |
| `_archive/` | 7 | Superseded docs. Nothing live. |
| `playground/` | 6 | The sandbox. Real code, synthetic data, outward tools denied. |
| `daily-logs/` | 6 | End-of-session handoff notes. Skim the latest to pick up where the last session stopped. |
| `send-package/` | 4 | The self-contained "how yourco works" bundle you can send someone. |
| `.obsidian/` | 4 | Obsidian vault settings. Obsidian is an optional reader for this folder — nothing depends on it. |

## The loops

~25 recurring loops run headless on a VPS, on systemd timers, with no human. Each produces a dated
artifact in `loops/<name>/` and reads `learnings/` before it starts.

**Don't maintain a loop list here — it drifts.** The canonical list is `runtime/agent-registry.json`,
and a watchdog diffs reality against it every Monday at 07:45 ET.

## How the pieces connect

```
   You ──► YourCo HQ (dashboard/)  ── what needs you, what's open
    │        ▲
    │        │ reads
    │      CRM (crm/data.json) ── the pipeline, source of truth
    │        ▲
    │        │ writes
    └──►  The runtime (VPS) ──► loops/     one dated artifact per run
             │                    │
             │ reads              └──► learnings/  ──┐
             └──────────────────────────────────────┘
                        the loop that makes it improve
```

Two machines share this folder — your Mac and the VPS — each a separate clone, meeting at GitHub
(`yourco/yourco-os`, **private**). Push and pull matter; see `07_RULES.md` §Git.

## New here? Read in this order

1. **`CLAUDE.md`** — 10 minutes, and you'll know what the company is
2. **`07_RULES.md`** — how work gets done, and what's enforced by a machine
3. **`05_operating_rhythm.md`** — how the day actually runs
4. **`clients/sample-client/_README.md`** — the one real engagement, end to end
5. Run **`./show.sh`** and open HQ → **The Board**

Then pick anything from The Board and follow it back to its folder.
