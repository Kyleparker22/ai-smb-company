# Slack channels — the per-agent control surface

> **Status: LIVE REFERENCE** — the per-agent channel map. The listener itself is `yourco-slack-listener`, active on the VPS (verified 2026-08-23).

> The map of which agent posts where. Phase 1 (live design): each agent has **its own channel** so its
> work has a clean, scannable, auditable home — and so the Founder can talk to it there (Phase 2: two-way command,
> see `runtime/slack-agent-listener.py` + `decisions/2026-06-14_slack-agent-control-surface.md`).
> Owner: Kemba/platform. Convention: lowercase `#yourco-<agent>`.

## The map (loop → agent → channel)
| Loop / prompt | Agent | Channel |
|---|---|---|
| `content` | Katie | `#yourco-katie` |
| `pipeline-report` | David | `#yourco-david` |
| `sales` | Atlas (sales report) | `#yourco-atlas` |
| `finance`, `finance-close` | Charles | `#yourco-charles` |
| `pricing-review` | Polo | `#yourco-polo` |
| `eval-review` | Kolby | `#yourco-kolby` |
| `customer-health` | Kortney | `#yourco-kortney` |
| `inbox-triage` | Jim | `#yourco-jim` |
| `brand-audit` | Luka | `#yourco-luka` |
| `advisor` | Brett | `#yourco-brett` |
| `aeo-geo` | Mario | `#yourco-mario` |
| `reilly-outbound` | Reilly | `#yourco-reilly` |
| _(copy)_ | Michelle | `#yourco-michelle` |
| _(audit, on-demand)_ | Bella | `#yourco-bella` |
| _(publish, on-demand)_ | Webb | `#yourco-webb` |
| _(trigger: signed client)_ | Janice | `#yourco-janice` |
| _(trigger: deal near close)_ | Kimi | `#yourco-kimi` |
| _(trigger: Kortney green light)_ | Bird | `#yourco-bird` |
| _(trigger: first invoice)_ | Harry | `#yourco-harry` |
| _(trigger: first hire)_ | Kori | `#yourco-kori` |
| **`sadie-intent`** (Google Alerts/News sweep, weekday AM) | Sadie | `#yourco-sadie` |
| _(legal, on-demand)_ | Ray | `#yourco-ray` |
| _(compliance, on-demand)_ | Rafi | `#yourco-rafi` |
| _(platform / agent factory)_ | Kemba | `#yourco-kemba` |
| _(collateral, on-demand)_ | Pickle | `#yourco-pickle` |
| **`monday-briefing`** | Atlas | **`#all-yourco`** (digest) |
| **`melanie-briefing`** | Melanie | **`#all-yourco`** (digest) |
| **`watchdog`** | System | **`#all-yourco`** (alerts belong in the all-hands) |

## The two roles of `#all-yourco`
`#all-yourco` stays the **executive digest** — the one channel the Founder skims to see the whole OS. It is fed by:
- **Melanie's daily briefing** (07:45 ET) — the cross-OS morning read.
- **Atlas's Monday briefing** (07:55 ET Mon) — the week's top 1–2 actions.
- **The watchdog** — critical alerts (a fired gate, a logging gap) surface here, not buried in an agent channel.

Everything else posts to its **agent channel** — so `#yourco-charles` is a clean ledger of Charles's finance runs, `#yourco-katie` of Katie's content briefs, etc. Per-agent observability; the digest still gives the one-glance roll-up.

## New channels provisioned 2026-06-25
Created for the newly deep-built agents (`decisions/2026-06-25_agent-roster-deep-build.md`): **Bella, Webb** (on-demand) + the trigger-gated **Janice, Kimi, Bird, Harry, Kori** (pre-provisioned so they're summon-ready the moment their trigger fires), plus on-demand channels for **Sadie, Ray, Rafi, Kemba, Pickle** — so every agent except Melanie (the conductor, who uses `#all-yourco`) is commandable. All wired into the listener + sanctioned in `runtime/agent-registry.json`. Channel IDs:

| Channel | ID |
|---|---|
| `#yourco-bella` | C0BD0N5EHKM |
| `#yourco-webb` | C0BD504UALW |
| `#yourco-janice` | C0BD0N7LZCK |
| `#yourco-kimi` | C0BDAMYHVV2 |
| `#yourco-bird` | C0BDAMYU0SY |
| `#yourco-harry` | C0BDAMZ9P1A |
| `#yourco-kori` | C0BD506PNQ6 |
| `#yourco-sadie` | C0BE1NMRAG0 |
| `#yourco-ray` | C0BD7EH45M0 |
| `#yourco-rafi` | C0BD14AN90B |
| `#yourco-kemba` | C0BE1NQSEHE |
| `#yourco-pickle` | C0BD8Q6PJE6 |

**Host step still required:** these were created via Cowork's Slack app, not the runtime control bot — so in each new channel, **invite the `atlas` control bot** (`/invite @atlas`; the one app that routes all agent commands), then restart the listener so it picks up the new channel→agent map (`cd ~/yourco-os && git pull && sudo systemctl restart yourco-slack-listener`). Keep the channels **public** (the listener's `message.channels` event doesn't cover private channels).

## Setup (the Founder's actions — channel creation is a workspace change)
For each channel above: create it in Slack, then **invite the bot** (`/invite @<yourco-bot>`). The bot only posts to channels it's been invited to — an uninvited channel silently drops the post. Until a channel exists + the bot is in it, that loop keeps posting (it will error on the missing channel); create them before the next run, or leave the loop pointed at `#all-yourco` by reverting its one Slack line.

## Gate (unchanged)
Posting only. The host approval gate still **allows** Slack post + Gmail draft and **denies** send / delete / Bash. Phase 1 adds no inbound path and no new capability — it only fans the existing outbound posts into per-agent channels. Inbound command (Phase 2) is a separate, gated build.
