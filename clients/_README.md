# /clients/ — engagement folders

> ⚠️ **NOT YOURS YET.** Three **worked example engagements**, with names, domains and locations removed. They exist so
you can see what a real proposal, discovery doc and roadmap look like. **No one is your
client yet.** Replace these with your own as you sign them.


**Reality level: 🟢 REAL people, but 🟡 no signed clients yet.** Sample Client is at `demo-proposal`;
Sample Realty and Prospect A are at `discovery`. yourco is pre-revenue.

## Why this is still called `clients/` and not `prospects/`

the Founder asked the fair question on 2026-08-23: nothing in here is a client, so shouldn't it be
`prospects/`, with folders *moving* to `clients/` on signature?

**The diagnosis is right; the move is the wrong fix, and it was measured before being declined.**

- A folder holds an **engagement**, which spans prospect → client. The name stays true through
  signature; only the *stage* changes, and stage is not the folder's job.
- **`crm/data.json` already owns stage** — HQ's `Clients` door reads it, and this workspace spent
  2026-08-23 removing exactly this kind of second copy of a fact. A path that encodes stage is a fact
  in two places, and the path would be the one that goes stale.
- Moving a folder *on signature* breaks ~50 references (Sample Client alone: 49) **on the day the
  relationship matters most** — mid-onboarding, while Janice provisions and Kimi builds.
- Renaming the whole folder was considered as the one-time alternative and rejected on measurement:
  **191 live files reference `clients/`**, including 23 in `runtime/` (Python that reads these paths
  at run time), 12 in `crm/`, 8 in `dashboard/`. That is a code refactor, not a rename, for the gain
  of one word — at a moment when the actual bottleneck is an unsigned proposal.

**So: one folder, from first-call onward. The CRM says what stage it is. `_README.md` in each folder
states it too, and `runtime/consistency-check.py` fails when the two disagree.**

## What's in here

| Folder | What it is |
|---|---|
| `_yourco-template/` | The golden template every engagement is cloned from. Client logic is overlay, never a fork. Its `_README` groups all 30 entries. |
| `sample-client/` · `sample-realty/` · `prospect-a/` | The three live engagements. |
| `_fixture-northside-dental/` | **A fictional client**, not an engagement. The end-to-end dry-run of Janice + Kimi + the templates, cited as the worked example by `processes/adversarial-eval.md` and `processes/sandbox-test-tenant.md`. Renamed from `_dryrun-` on 2026-08-23 to say what it is. |
| `_pipeline.md` | A read-only **mirror** of the CRM. See below. |
| `_internal-rollout.md` | Agent provisioning notes. |

*(Two folders left on 2026-08-23: the "Sage" home-services demo was a **sales asset**, not a client, and
moved to `agents/Reed/demos/home-services-intake-sage/`; the June commercial-path tabletop was a
point-in-time record and went to `_archive/`.)*

## The structure inside an engagement

Measured 2026-08-23: across the three engagements **only two files existed in all of them** —
`_README.md` and `cost.md`. Three engagements had invented three different shapes, with subfolders
meaning the same thing under different names (`attachments`/`assets`, `deliverables`/`listing-presentation`).

### Required in every engagement folder — from day one
| File | Why |
|---|---|
| `_README.md` | What this engagement is + the "How the OS works this client" agent map |
| `cost.md` | The spend ledger. yourco absorbs the cost; margin per client is the metric. |
| `01_discovery.md` | The use case, the outcome, the quantified bottleneck |

### Applied 2026-08-23 — the convention is not just written down
- **sample-client** was already compliant: `attachments/` `meetings/` `platform/` `prototype/`.
- **sample-realty** had 10 subfolders, three of them synonyms for client-facing output. `listing-presentation/`,
  `pamphlet/` and `listing-copy/` now sit under `deliverables/`. `assets/` **stays at the client root** —
  `tour.html` reads it relatively and `site/index.html` reads it as `../assets/`, so moving it breaks both;
  `site/`, `tools/`, `pm-module/`, `demo-kit/` and `audit-report/` are distinct things, not synonyms.
- **prospect-a** was missing `01_discovery.md`. Written as an explicit **reconstruction** from the
  README and build journal, with every field that was never captured marked as such — including the two
  that matter: **no agreed success criteria and no papered partnership.** That is why an engagement can be
  "built and operating in preview" and still sit at `discovery` in the CRM.

### Use these names when you need them — don't invent a synonym
| Folder | For |
|---|---|
| `meetings/` | Call notes and transcripts |
| `attachments/` | Files **they** sent us |
| `deliverables/` | Finished things **we** handed over |
| `prototype/` · `platform/` | Running code built for this engagement |

### Delivery files — only once there is something to deliver
`02_build.md` · `03_eval.md` · `go-live.md` · `weekly/YYYY-MM-DD.md`. **None of these exists yet and
that is correct** — no engagement has reached delivery.

⚠️ **Sample Client numbers its files as a sales progression** (`01_discovery` → `07_proposal-os`) rather
than the delivery one, because it has been in the sell for months. Deliberate. When it signs, the
delivery files get added alongside — they do not replace it. **Don't "fix" it.**

## `_pipeline.md` is a MIRROR — not the source of truth

> ⚠️ **The source of truth is `crm/data.json`** (live at `/crm/`, owned by David). **Do not edit
> `_pipeline.md` by hand** — edit the CRM and let the mirror follow.

Refreshed by the `pipeline-report` loop, which has not run since 2026-07-06. Despite that the mirror has
held: all three live deals are present, because Atlas reconciled it by hand on 2026-08-17. Roughly nine
`pre-convo` rows are absent, which is within scope — the bench is the part a mirror may omit.
`runtime/consistency-check.py` now fails if any deal at **discovery or later** goes missing.
