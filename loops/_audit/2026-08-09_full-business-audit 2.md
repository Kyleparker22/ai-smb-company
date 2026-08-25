# Full business audit — yourco, 2026-08-09

*the Founder asked for an audit of every aspect of yourco with honest thoughts on all of it. This is that.
Everything below is evidenced with a file, a date, or a number. Where something couldn't be verified,
it says so. Written to be useful, not comfortable.*

---

## The headline

**yourco has built an extraordinary machine and has not yet run a business.** The OS is genuinely ahead
of what most funded startups have. The company underneath it has $0 cash, $0 revenue, two unpaid
subscriptions, an API that has been dark since ~July 30, a runtime that has been **paused for 5 days
without anyone noticing**, and three deals that have not moved in 20–54 days.

The constraint has never been the machine. It has been the same four human actions for two months.

---

## The numbers that frame everything

| | |
|---|---|
| Live clients / MRR | **0 / $0** |
| Cash on hand | **$0** · runway **0.0 months** (`finance/runway.md`) |
| Fixed monthly burn | **~$614** — personally funded by the Founder as charges arrive |
| Unpaid right now | **Hostinger $24.49** (failed Jul 9 *and* Jul 20 — the box the whole runtime runs on) · **Descript $35** |
| Deals past first touch | **3** — Sample Client (proposal, **54 days in stage**), Nick (sitdown, last touched **40 days ago**), Sample Realty (sitdown, 20d) |
| Companies with any logged activity | **13 of 25** |
| Commercial activities logged, last 30 days | **12** (2 meetings) |
| Deals that changed stage, last 30 days | **2** |
| Git commits, last 30 days | **289** |
| New code files, last 30 days | **84** |
| Repo | **1,009 markdown files · 819k words · 249 python files · 100 decisions · 44 learnings · 17 skills** *(corrected 08-09: my first pass read 3,004 files / 2.46M words because three abandoned git worktrees triple every repo-wide grep — see Appendix E)* |
| Counsel gates | **12 blocked / 3 cleared** — and **no counsel engaged**, 33 days after that was named the headline gap |

**84 new code files against 12 commercial touches.** That ratio is the audit.

---

## Finding 1 — The company is cash-insolvent, and the infrastructure is now failing for non-payment

This outranks everything else and it is not a metaphor. `finance/runway.md` says cash on hand is **$0**
and runway is **0.0 months**, against ~$614/mo of obligations. The observable consequences are already
in the ledger: a card decline June 1, an Anthropic credit lapse June 16–18, **Hostinger failing twice**
(July 9 and July 20 — still unpaid), Descript failing July 10–12, and **the API dark since ~July 30**.

Two things follow that the Founder should sit with:

- **The runtime host is unpaid.** Everything called "always-on" runs on a box whose bill has failed
  twice. If Hostinger suspends it, the OS doesn't degrade — it stops.
- **Burn was understated by 48% for weeks.** The Claude Max subscription ($200/mo, first receipt
  Jul 27) was off-book, so every pulse through 07-27 reported ~$414 when the real number was ~$614.
  The finance layer was reporting confidently on incomplete data.

**The honest framing:** this is not a company with a runway problem. It is a company with no runway,
funded personally, spending ~$614/mo to operate machinery that serves zero customers.

---

## Finding 2 — The always-on OS has been OFF for five days, and its own watchdog could not tell you

`runtime/.paused` exists on the VPS, **created Aug 4 at 17:12**, empty, with no explanation. Every
timer since has fired, seen the flag, and exited. Verified on the box:

```
watchdog          [2026-08-09] watchdog PAUSED (runtime/.paused present)
initiative        [2026-08-07] initiative PAUSED
melanie-briefing  [2026-08-07] melanie-briefing PAUSED
sadie-intent / crm-hygiene / crm-autolog / content / inbox-triage / open-loops-chaser … all PAUSED
```

**The watchdog — whose entire job is catching silent loop failure — is itself paused.** The monitor
lives inside the thing it monitors, so when the system stopped, the alarm stopped with it.

And *before* the pause there was a second, separate failure. Around Aug 2–3, six loops ran, did their
work, and then **failed to save it**:

```
sales / finance / monday-briefing / pipeline-report / eval-review / finance-close
   → FAILED (git push, exit 1)
```

The VPS clone had diverged from the remote; `run-loop.sh` pushed, was rejected, and the output was
stranded. So for roughly a week the OS was doing work nobody received, and then for five days it did
nothing at all — and both were invisible.

**I have deliberately not un-paused it.** I don't know why it was paused, and resuming twenty loops
that will fail on push and consume API credit the company cannot pay for would make things worse. That
is the Founder's call, and it should come *after* the push failure and the billing are fixed.

**The deeper point, because it matters commercially:** yourco's entire pitch is the reliability layer —
eval, observability, watchdogs, the thing no-code can't build. That layer just failed on yourco's own
OS, silently, for a week. The lesson isn't that the moat is fake; it's that **a watchdog inside the
system it watches is not a watchdog.** Fixing that honestly makes the pitch stronger, because it will
be true.

---

## Finding 3 — This is the second audit to say the same thing

The **2026-07-04 full OS audit** named four critical items. Thirty-five days later:

| 07-04 critical | Status today |
|---|---|
| Sample Client stalled | **Still stalled** — 54 days at proposal |
| Sample Product unpapered | **Still unpapered** — 0 signed documents on file |
| Finance blind | **Worse than blind** — now measured, and the measurement is $0 cash / 0.0 months |
| Cost tracking unenforced | **Fixed** (2026-07-06) |

One of four. And the one that got fixed is the one that could be fixed *by building something*.

That is the pattern this audit exists to name: **yourco reliably closes any gap that can be closed with
code, and reliably does not close gaps that require the Founder to talk to a human.** A third audit will say
this again unless something structural changes.

---

## Finding 4 — One un-taken action gates fourteen others

Counsel has not been engaged. Not "engaged and slow" — **not engaged**, 33 days after the tracker named
it the headline gap. Behind that single email sit: the connector program in its entirety, the referral
override, the equity/phantom track, the 50/50 operating agreement the Founder actively wants to sign, the
client contract suite, and the launch of everything external.

Meanwhile the **master gate is still undefined**. `processes/launch-gate.md` — the gate blocking the
entire company from going external — literally reads *"the Founder to fill: one honest sentence on what the
OtherVenture matter is and why it blocks yourco going external"* and *"the Founder to fill: what specifically has
to happen for this to count as cleared."* The estimate ("~weeks out") is **8 weeks old**.

**A gate nobody has defined cannot be cleared, and it is currently the justification for not launching
anything.** That deserves scrutiny: is OtherVenture genuinely blocking, or has an undefined gate become a
comfortable reason to keep building?

---

## Finding 5 — The build:sell ratio, stated plainly

In the last 30 days yourco produced 289 commits and 84 new code files: the Connector OS (ladder, audit
log, console, auth, training, arsenal, spotter), the playground, the trust ledger, the evidence door,
the build journal, token forensics, seven CRM insight modules, and a full HQ redesign.

In the same 30 days: **12 logged commercial activities, 2 meetings, 2 stage changes, 0 signatures.**

Today's session alone built an entire Connector OS — four subsystems, an authenticated console, a
13-lesson curriculum, operator confirmation flows — **for a program that is counsel-gated, has zero
active connectors, and cannot legally be offered to anyone.** The legal send that would unblock it has
been pending 33 days and did not happen today either.

None of that work is bad. Most of it is genuinely excellent. But it is all *pre-positioning for a
business that hasn't started*, and pre-positioning has no natural stopping point — which is exactly why
it keeps winning the day against the four uncomfortable phone calls.

---

## What is genuinely excellent (this is not a demolition)

1. **The honesty architecture is world-class and rare.** Systems that refuse to state numbers they can't
   defend: the Evidence door, `--estimate` refusing at n<3, the cost feed refusing to price an unknown
   model, the demo generator's fail-closed content scan, the ladder failing closed on missing training.
   Most companies build systems that flatter them. yourco built systems that argue with it.
2. **The consistency watchdog + invariants pattern.** 14 machine-checked invariants, each born from a
   drift a human caught once. This is a genuinely good idea most engineering orgs don't have.
3. **The Connector OS design.** Setting aside the timing, the *design* is real IP: an audit log a
   referrer can read, a trust ladder mirroring the agent autonomy matrix, training gating advancement,
   operator confirmation where money starts. Nobody in that category has this.
4. **The decision log.** 100 decisions with context, options, and reversibility. This is the single
   highest-value artifact in the repo and the reason this audit could be written at all.
5. **The delivery assets are real.** Sample Client's Field-to-Quote platform and Sample Product are
   working software, not slideware — genuine proof that the delivery claim isn't a bluff.
6. **The moat thesis is correct and externally validated.** The FDE transcript, Mario's competitive
   scan, and the market's $150k–$1M FDE salaries all confirm the positioning. yourco is right about
   the market. It just hasn't entered it.

---

## What to delete, stop, or park

**Stop maintaining (they cost attention and return nothing at 0 clients):**
- The **playground** (`playground/`) — a synthetic sandbox to practice yourco, built while the real
  yourco had no customers. Archive it.
- **DRI twin, time machine, calibration market, trust ledger** — sophisticated instrumentation that is
  structurally blocked until there is revenue and history to instrument. They cannot produce a real
  number today and won't for months.
- **Conduit** (`offerings/conduit/`) and **yourco Care** — two whole vertical offerings spec'd while the
  horizontal one has no customer. Park explicitly rather than leaving them warm.
- **The three stub training lessons** and any further curriculum work until a connector exists.
- **Mario's AEO/GEO loop** — optimizing answer-engine visibility for a site that isn't deployed.

**Cancel now (real money, ~$343/mo recoverable per the ledger's own recommendation):**
- The **duplicate Instantly subscriptions** (~$194/mo) — flagged in June, still unfixed two months later.
- **Descript $35** (unpaid anyway), **Canva $18**, **Plausible $9** (analytics for an undeployed site),
  **ElevenLabs $6**, **Granola $14 → free tier**.

**Fix, don't delete:** Hostinger (pay it — it's the runtime), Google Workspace (it's the identity),
Anthropic (it's the fuel).

---

## Where it's gone overboard

- **819,000 words of markdown** for a company with zero customers — ~32 words of prose per line of working
  code. (My first pass said 2.46M; that was the worktrees triple-counting. The corrected number is still
  ~10 novels.) Some is the decision log (valuable). Much is loop artifacts nobody reads.
- **27 named agents** for a solo founder with no clients. Roughly half have never produced anything a
  human consumed.
- **Four separate audits** in five weeks (07-04, 07-05 ×2, 08-02) — auditing has itself become a form
  of building.
- **The "Obsidian brain"** is, on inspection, the repo opened in Obsidian (config written Jul 27, no
  daily notes, no templates, no dataview). It's a viewer, not a second brain. Nothing wrong with that —
  but it shouldn't be counted as a system.

---

## What's missing that actually matters

1. **A defined launch-gate.** Until it's a sentence with a resolution condition, it's an excuse.
2. **Money in the company bank account.** Even $2–3k would stop the personal-card failures and unpause
   the infrastructure.
3. **An engaged attorney.** One email. Fourteen gates.
4. **A watchdog that lives outside the runtime** — an external heartbeat (phone alarm, a cron on the
   Mac, a free uptime service) that fires when the VPS goes quiet. Today's failure is unfixable from
   inside.
5. **A signed anything.** Sample Client, Nick, or Sample Realty. The first signature changes the
   character of every other problem in this document.

---

## The structural fix — what would make a third audit unnecessary

The pattern is not laziness; it is that **building is available at 2am and phone calls are not**, and
the OS makes building frictionless while doing nothing to make the four uncomfortable actions easier.

Three changes that would actually alter behavior:

1. **A build freeze until a signature.** No new internal machinery — no new agents, loops, consoles, or
   subsystems — until one of the three live deals signs. Bug fixes and client-facing work only. This is
   the single highest-leverage change available, and it costs nothing.
2. **Put the four actions where the building happens.** They currently live in Jim's queue, which is a
   report the Founder reads. Make them the *gate on the session*: the HQ opens on "which of the four did you
   move today?" and nothing else renders until it's answered.
3. **Move the watchdog outside.** External heartbeat, and pay the Hostinger bill today.

---

## The one thing to take away

The machine is not the problem. The machine is, honestly, remarkable — and in six months, with
customers, most of what's been built will look prescient rather than premature.

But right now yourco is a company with no cash, no customers, a paused OS, and an unopened conversation
with a lawyer — that spent the last thirty days building a referral program for people it cannot
legally recruit.

**Everything in this document is downstream of four phone calls and one email.**

---

*Domain deep-dives from four parallel audit agents (infrastructure, knowledge layer, GTM, agents &
finance) are appended below as they complete.*

---

# Appendix A — Infrastructure, runtime, spend (deep read)

## The root cause, and the thing that's worse than the outage

**Why it paused:** Anthropic ran out of API credits **Jul 30 / Aug 1** (`loops/finance/2026-08-03.md`;
`loops/_anthropic/latest.json` shows $0.00 on 08-02, 08-03, 08-06). From Jul 30 every loop logged
`FAILED` twice over — a git rebase conflict *and* the model call itself. Pausing was a reasonable
reaction to that noise. **Leaving it on for five days, undocumented, was not.**

**Why nobody could see it — this is the real defect, not the pause.** Four independent blindfolds, any
one of which would have caught it:
- `runtime/.paused` is **gitignored** → invisible from the Mac.
- `loops/_runtime/` is **gitignored** → run logs never reach the repo.
- `dashboard/board.py` and `dashboard/server.py` both **explicitly skip `_runtime`**.
- **`runtime/runtime-alarm.sh` greps only for `FAILED`. `PAUSED` is invisible to it — so it has posted
  `[alarm] all clear — no new FAILED runs` every hour for five days while the runtime was off.**

An alarm that says "all clear" during an outage is worse than no alarm, because it actively buys false
confidence. And the consistency check ran during this audit and **passed 19 invariants without noticing
the runtime was dark.**

**Three learnings already exist for this exact failure class** (`2026-06-18_runtime-silent-credit-death`,
`2026-07-10_host-billing-is-a-runtime-death-vector`, `2026-07-28_loop-liveness-blindspot`). This is the
**third firing**. The learnings substrate recorded the lesson three times and changed nothing, because a
learning that isn't wired to a detector is a diary entry.

## What survived, and why it's the pattern to copy

The three **deterministic Python loops** — `consistency`, `crm-hygiene`, `agent-registry` — kept
producing straight through both the credit death and the pause, at $0 cost, because they run `python3`
directly instead of `claude -p`. Every loop that needed a model died; every loop that didn't, lived.

*(Caveat found in the same pass: those three bypass `run-loop.sh` entirely, which means they also
ignore the pause switch, the repo lock, and the alarm — and `agent-registry` runs a bare `git add -A`,
the exact thing CLAUDE.md forbids. Right pattern, wrong plumbing.)*

## Concrete deletes (verified dead, not suspected)

| Delete | Why |
|---|---|
| `runtime/rep_intake.py` (99 LOC) | Superseded — `site_intake.py` implements the same endpoint and is the one with a systemd unit |
| `runtime/montage_slack_bridge.py` (196) | Bridges to OpenMontage, killed by decision 2026-06-23 |
| `runtime/recraft.py` (83) | Parked 2026-06-18 (no public API) |
| `runtime/.recraft.env`, `runtime/.yelp.env` | Keys for code that doesn't exist — **revoke at the vendor first** |
| `dashboard/_redesign/` (1,869 lines) | Superseded design exploration, referenced by nothing |
| 3 × `.claude/worktrees/` | Full repo copies, oldest untouched since 07-27 |
| Duplicate `sample-realty-tour` in `.claude/launch.json` | Listed twice |
| `playground/data/* 2` dirs | macOS copy artifacts |

**Repo weight:** 705MB, of which **369MB is `.git`** — the `clients/ → agents/` move duplicated a 6.5MB
mp4 five times in history.

## Subscriptions — $262/mo cancellable, taking burn $614 → ~$236

Instantly duplicate **$97** (the ledger literally calls it *"DUPLICATE of the row above"*) · remaining
Instantly **$194** (accounts unhealthy, warmup **0 of 2**, and `loops/reilly/` + `loops/outreach-eval/`
have **never produced a single artifact**) · Plausible **$9** (script never installed, 61 days) ·
Descript **$35** (unused 61 days, card declining anyway) · Canva **$18** (superseded by Higgsfield in
June) · ElevenLabs **$6** · Granola **$14 → free**. Keep Hostinger, Tailscale, Google Workspace,
Anthropic.

## Latent bugs worth knowing

- **`crm/data.json` is written from 10+ places and six take no lock** — including two that are
  timer-driven and contend with the lock-taking server. The `_rev` guard only covers `/api/data`.
  Nothing tests any of it.
- **Four different `_slug` implementations** (and five copies), **three different `_next_id`
  algorithms**, seven copies of `_load_env`. Slugs become client directory names.
- **No test runner.** Two hand-rolled suites, no pytest, no CI. `crm/server.py`, `dashboard/server.py`,
  and every CRM write path are untested — the highest-risk code is the uncovered code.
- **`runtime/connectors.md` is 45 days stale** and omits 11 credentialed services, including **Twilio,
  which sends real SMS outside the approval gate.**

## The infrastructure verdict

Registry-to-host integrity is exact (30 timers, zero drift), secret hygiene is clean (no live env file
tracked), the approval gate held in production, and there are zero third-party Python dependencies.
The *engineering* is careful.

What failed is the layer above it: **an OS that cannot tell you it has stopped.** And the reason it
kept building anyway is in the same report — **63 commits on 08-07 alone, while the runtime was off and
zero clients were signed.**

---

# Appendix B — The commercial engine (deep read)

## The diagnosis, sharpened

**There is no revenue because nobody has ever been asked to buy anything — and if someone said yes
today, yourco could not take their money.**

The evidence is not ambiguous:

- **22 deals. 19 sit in `relationship`. 0 signed. 0 closed.** All 25 companies have `source` = some
  variant of *"warm network (the Founder)"*. **Zero companies were sourced by any machine ever built.**
- **40 of 49 contacts have neither an email nor a phone number** — including the Client Owner, the one
  real deal. The pipeline is built on people who cannot be addressed.
- **Four external interactions have ever occurred** — 3 meetings + 1 call in 61 days, across two
  accounts. The other 21 activities are internal notes and free deliverables.
- **Zero cold emails have ever been sent.** No deal has `seqStatus`/`seqTouch`. Instantly: one campaign,
  `accounts-unhealthy`, warmup **0 of 2** — at $291/mo.
- **25 Sadie intent sweeps → 0 CRM rows.** 13 content briefs → **0 published.** 36 website pages built →
  **never deployed** (no `vercel.json`, `netlify.toml`, `wrangler.toml`, or `CNAME` exists anywhere).

## Three prerequisites that make a "yes" impossible to accept

1. **Nothing to sign.** Counsel gate #1 — the engagement agreement, DPA, NDA, explicitly marked
   *"Blocks: Any client signing at standard terms"* — is 🔲 **not started**. No counsel engaged.
2. **No way to get paid.** All five Stripe items in `processes/payments.md` are unchecked. No account,
   no ACH, no products, no payment link.
3. **No contact details.** Step 1 of the warm-network play ("block 90 minutes, mine the names") was
   never done — hence 40/49 contacts with no way to reach them.

**If Client Owner signed tomorrow, there is no agreement to hand him and no way to invoice him.**

## ⚠️ Check today: the business inbox may never have been read

The sales loops authenticate as **`you@example.com`, not `founder@yourco.example.com`**
(`loops/sales/2026-08-03.md`). If that's right, **no loop has ever read the business inbox** — and a
prospect reply could be sitting in it unseen. This could not be verified from the repo. It takes two
minutes to check and it is the cheapest possible source of a live opportunity.

## The attention finding — the most important fact in this audit

From `loops/_audit/2026-08-02_session-friction-audit.md`: across **9 substantive sessions and 108 user
messages in a month, Sample Client — the only deal past prospect — appears in none of them.** The single
largest session (23 messages, 5 days, 17MB) was SideProject, a personal project. In the same four weeks, 13
tool/content triages were run.

The audit's own verdict: *"it isn't that the warmest account is hard, it's that it isn't getting
attention."*

## What the business plan already knew

`business-plan.md` §9 adopted exactly the right leading indicator, months ago:

> *"Days since the last real-prospect conversation — watched weekly; when it grows, the company is
> polishing instead of selling."*

The plan diagnosed this company correctly and was then ignored. The metric was never watched.

## Park until there is a paying client

| Item | Evidence |
|---|---|
| **The entire connector program** | 1.7MB, 43 commits, 12 working days, **24 personalized consoles already generated for named people**, 13 training modules, 4 python modules, packet in .md/.html/.pdf, 6 decisions — against **`repApplicants: []`**. It received **more commits than the outbound engine (20) and more than Sample Client (21)**. |
| **Instantly — cancel 2 of 3** | $194/mo for a machine gated from sending, on unhealthy accounts |
| **Sadie's intent sweeps** | 25 runs, 0 promotions; burning API credit against a $0 balance |
| **The 31 frontier offering specs** (`offerings/`) | 31 productized offerings for 0 clients; only 2 contain code. The clearest single overbuild artifact in the repo. |
| **15 parked website pages** | 42% of the site was built then shelved |
| **Mario's AEO/GEO** | Answer-engine optimization for a domain with no deployed site |

## Overbuilt, specifically

- **Seven proprietary CRM insight engines** against 22 deals of which 19 have never been contacted. The
  `calibration` engine measures forecasting bias across stage moves; there have been **~3 stage moves
  ever**. The instrument is more precise than the phenomenon.
- **A 53-vertical target list and 20-industry campaign kit containing zero named companies.** There is
  no prospect list anywhere in the repo. You have industry taxonomy where you need 50 humans with phone
  numbers.
- **A 9.7KB pre-send eval gate** — quality control on emails that have never been sent.
- **Five pricing documents (~35KB)** for zero transactions — and `os-tiers.md` still says *"v0 proposal —
  Polo's draft for the Founder to lock,"* so the tiers treated as canonical elsewhere aren't actually locked.

## The three moves, ranked by likelihood of a signature in 30 days

**1. Put a price in front of Client Owner this week.** He asked about pricing on 08-06 and it was deferred.
He's at `proposal` with a real next action dated 08-13. Name a number and a start date — either a banded
Core figure ($3,000–4,000) or a conscious re-affirmation of the $1,000 brotherhood rate. **Honest
tension:** $1,000 is one-third of the locked Core floor, so converting at it sets a reference price
you'll fight for a year. The larger risk is the one the CRM already named — *at $0 committed he carries
no downside and yourco carries all of it.* The sales loop has asked for this four consecutive runs.

**2. Send the three warm texts today, from your phone, in fifteen minutes.** Joey, Tucker, Brigitte.
The copy has been written verbatim since 2026-07-06 — **34 days**. The audit fee was waived for exactly
these first three **26 days ago**. Zero OtherVenture exposure, zero infrastructure, zero counsel dependency.
This has been the #1 recommendation for **55 days across 12 consecutive Jim runs**. If they don't go
out this week, park all 20 warm names — a 13th run carrying the same item is worse than deleting it.

**3. Engage counsel and set up Stripe.** One engagement moves **14 of 25 gates**, including the
agreement any client must sign and the operating agreement the Founder actively wants to execute. Stripe is
five checklist items. Neither produces a client alone — but both must exist before a "yes" becomes
money. Today, a yes converts to an apology.

**On OtherVenture: don't clear it — *define* it.** Four fields, fifteen minutes. An undefined gate is
currently justifying the non-execution of channels it does not actually block (the warm-network play
explicitly says it is startable now), and it will keep doing so indefinitely.

---

**The commercial verdict in one line:** the OS works, the product is real, the pricing is sound, and the
delivery is proven — the company has simply never made an ask, and has spent two months building
increasingly sophisticated instruments to observe that fact.

---

# Appendix C — Two cross-findings the individual audits could not see

These emerged only from reading four audits against each other. Both are actionable today.

## C1 — ⚠️ The corrected business plan exists in exactly ONE place, and two audits recommended deleting it

On **2026-07-06 (commit `1570c13`)** the business plan was correctly re-run on OS-tier pricing:
**$670k / $4.4M / $12M** ARR on blended retainers of $3,100 / $4,400 / $5,200. It swept 11 files and added
a consistency invariant to prevent regression.

**Then two clones diverged** (this Mac and the VPS — the two-writer model in CLAUDE.md). `1570c13` is
*not* an ancestor of the 2026-07-20 branch, which carried the pre-fix plan forward. The entire 08-05
rewrite series — eleven commits claiming *"every v0 figure preserved (verified)"* — preserved the wrong
v0. The merge at `bc4a2d8` brought in the **decision documenting the fix** but not the **fixed numbers**.

Verified today:
- Live `business-plan.md`: `| **ARR run-rate** | ~$240k | ~$2.0M | ~$7.0M |`
- `.claude/worktrees/friendly-knuth-1079a4/business-plan.md`: contains the corrected figures.

**The infrastructure and knowledge audits both independently recommended `rm`-ing the worktrees** (181MB,
they triple every grep — a genuinely correct recommendation on its own terms). **Doing that first would
have destroyed the only copy of the corrected plan.** Recover the file *before* the cleanup. It is a
copy-paste, not a re-modelling exercise.

## C2 — The guard built to prevent this was destroyed by the same merge, and I made it worse today

The 07-06 commit added **invariant #11: "plan + company doc must speak os-tiers — retired price lines
can't silently reappear."** It is gone. Verified: `grep` for the guard in `runtime/consistency-check.py`
returns **zero** references. The system has been unable to detect its most expensive inconsistency for
34 days.

**And I compounded it today.** Adding the connector-classification and training-curriculum invariants, I
numbered them 11 and 12 without checking — the file now has **two invariants numbered 11 and two
numbered 12**. That's mine, and it makes the missing original harder to notice, not easier.

---

# Appendix D — Offering, pricing, plan, referral program

- **The tier *names* are locked; the tier *prices* are not.** `pricing/v0/os-tiers.md` opens with *"⚠️ v0
  proposal — Polo's draft for the Founder to lock"* and closes with four open lock questions. Untouched for
  **47 days** — while `CLAUDE.md`, `01_company.md`, `goals.json`, and the connector packet's earnings
  math all treat those prices as canonical.
- **Ten pricing contradictions found**, four critical. Worst: `business-plan.md` line 100 carries
  *"Tier 1 ~$4,000 build + $750/mo (landscaping intake, the one locked vertical)"* — a **retired price**,
  **retired vocabulary**, and a **retired vertical** in one 17-word clause.
- **Sample Client is scoped Suite→Operation ($4.5–8k/mo band) and priced at $1,000/mo** — 78–88% below
  list. Engagement #1 sets a reference anchor you'll fight for a year. Decide deliberately before the
  walkthrough, not during it.
- **Zero audits have ever been delivered.** The priced ($1,000/$1,500, locked since 06-16), scoped
  (22KB SOP), templated front door has opened **zero times in 62 days**. Sample Realty's "audit report"
  is a byte-identical copy of the fictional *YourCo Landscaping* sample — same client name, same vertical,
  same `$9,000/mo` number. Meanwhile the SOP has been amended six times since, including an 08-08 rule
  about preserving baselines for **re-audits at renewal** — process optimization on step 12 of a funnel
  whose step 1 has never fired.
- **32 offerings in `offerings/`** against a locked *"one product, one motion"* decision (2026-06-18).
  Only 2 contain code. Two of the built ones correctly refuse to produce output because there is no
  client data — admirable engineering, damning commercially.
- **Connector program, measured:** ~1.05MB of hand-authored source (29× the business plan), 45 commits,
  12 of the company's 57 working days, a 119KB console server — against `repApplicants: []`,
  `repRecruiters: {}`, and an attribution log containing exactly one line that says *"log opened."* It
  received **more commits than the outbound engine and more than Sample Client.**
- **The sharpest single comparison in this audit:** on 2026-08-07, **17 commits** went into a referral
  console for zero connectors — while the same day's own artifact recorded that **three warm outreach
  texts, already written, requiring only a send, had been sitting unsent for 55 days.**

---

# Appendix E — Agents, surfaces, finance, and the knowledge layer

## Theater — things that look like they work

- **"The always-on OS."** CLAUDE.md still claims *"runs 24/7 headless."* Zero timers have artifact
  evidence of firing on schedule in the last 10 days.
- **The Trust Ledger** — 233 actions, "0 incidents," **all carrying the same timestamp**
  (`2026-08-07T19:46:32`): one backfill pass over git history. 81 are `unattributed`.
- **The DRI Twin** — `loops/_twin/` **does not exist on disk.** Zero predictions ever.
- **`autonomy.py` reports "8% of pipeline-moving work runs without you" — and it is wrong**, not merely
  small. It buckets the Founder's own hand-typed notes as uses of the auto-log capability. Agents did 0%.
- **`loops/reilly/` is empty — zero files, ever.** Reilly is "the outbound machine"; Instantly has cost
  ~$898 to date.
- **The auditing machinery produced a confident false finding**: `loops/gap-audit/2026-08-07.md` states
  *"the audit has no price in `pricing/`"* — it has been locked at $1,000/$1,500 since June 16.

## Finance / back-office — the serious gaps

1. **No business bank account.** Every charge runs on personal cards. For a single-member FL LLC that is
   textbook commingling and the classic veil-piercing pattern — and it matters *more* because a **50/50
   partner admission** is contemplated.
2. **No payment rail** — all five Stripe items unchecked. The audit is priced, locked, and **cannot be
   invoiced.**
3. **No CPA, no bookkeeper.** Defensible at $0 revenue, but the FL annual report and a first federal
   return are coming with no owner.
4. **Insurance drafted, nothing bound** — while the engagement agreement §13 already *represents* GL +
   E&O + Cyber coverage.

## The knowledge layer

- **`learnings/` is the one closed loop that actually closed** — 87 of 252 loop artifacts cite a
  *specific* learning filename. Leave it alone; it's the only documentation habit with measured uptake.
- **CLAUDE.md has grown 5.3× in 61 days** (774 → 4,082 words, ~54/day, 53 commits, **never once pruned**).
  At this rate it crosses 5,000 words by mid-September. Roughly a third is historical justification that
  belongs in `decisions/`.
- **Only 8 of 98 decisions carry a supersession marker — and 2 of those 8 are themselves wrong.** One
  announces referral rates of *10/15/20*, a number never locked (truth: 10/12.5/15), sitting in the
  banner line a reader trusts most.
- **The retired landscaping beachhead is still live in 19 files** — including
  `.claude/skills/tool-triage/SKILL.md` **filter rule 7, "Guard the beachhead"**, which is the
  most-invoked skill in the library. Every future triage still weighs against a strategy that no longer
  exists.
- **The orientation test:** a new agent reading the boot context cold would believe n8n is sanctioned
  (a decision explicitly forbids it for this case), get the CRM system-of-record wrong, guard a dead
  beachhead, quote stale pricing, and trust a 35-day-old "latest" daily log. **The philosophy transmits
  perfectly; the facts drift.** CLAUDE.md is well-swept and everything downstream of it is not.
