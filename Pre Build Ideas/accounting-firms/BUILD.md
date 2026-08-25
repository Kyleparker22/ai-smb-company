# 5 · Accounting, Bookkeeping & Tax Firms — **Close OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

An accounting firm's throughput is not limited by how fast it works. It is limited by **the chase** — the bank statement the client hasn't uploaded, the K-1 that's coming "next week," the eleven questions on the open-items list that have been open for nineteen days. Every close and every tax season is a firm of trained professionals waiting on documents, chasing them by hand, and losing partner visibility into who is actually blocking what. **Close OS** turns the chase into a system: every engagement is a document state machine, every missing item chases itself on a personalized cadence across the client's preferred channel, every arriving document is classified and matched to its request (or flagged as a mismatch), and the partner gets one board showing every engagement, its blocker, and how old that blocker is. The second half is the money half: **unbilled scope creep**, tracked as it happens instead of discovered at write-off.

## 2. Who buys it

The **managing partner** of a 4–40 person CPA or bookkeeping firm, $500k–$6M revenue, running Karbon / Canopy / TaxDome with QBO or Xero underneath. They measure realization and WIP days and they know their write-offs come from two places: chasing and scope creep. Warm-network reachable through any business owner's own accountant, which makes this one of the best referral-density verticals on the list.

## 3. The bleeding neck

- **Document chase.** The PBC / open-items list is the firm's real bottleneck. It is worked by whoever remembers, in whatever tone they're in, at whatever interval.
- **Partner blindness.** "Where are we on the Hendersons?" has no answer without asking three people. Nobody can see the firm's blockers in one place, ranked by age or by deadline.
- **Document intake chaos.** Clients send photos of statements to a staff member's personal email, drop unnamed PDFs in a portal folder, and mislabel the year. Someone has to open, name, match and file every one.
- **Scope creep, unbilled.** The client asks one more question, sends one more entity, restructures mid-year — and none of it becomes an invoice, because nobody logged it at the moment it happened.
- **Season concentration.** All of the above at 4× volume for ten weeks, which is why the firm's capacity is set by its worst-organized clients.

## 4. What we build

**Pillars:** Operations (5) + Back Office (6) + Customer (4) + Company Brain (7). **Form factors:** headless automation (the chaser + classifier) + embedded surface (the partner board) + digital employee (the engagement assistant).

| Module | What it does | Autonomy start |
|---|---|---|
| **Engagement state machine** | Every engagement (monthly close, 1040, 1120S, audit prep) carries a structured request list: item, entity, period, responsible party, dependency, and status. Nothing is "in progress" without a named blocker. | — |
| **The chaser** | Per-client cadence and channel (email / SMS / portal), personalized to what is *actually* still missing — never a re-sent generic list. Escalation ladder ends at a partner task, not at infinite reminders. | R1 → R2 once evidence supports it |
| **Intake classifier** | Reads arriving documents, identifies type / entity / period, matches to the open request, renames and files to the firm's convention, and flags mismatches (wrong year, wrong entity, duplicate, illegible) rather than silently accepting them. | R2 for filing, R1 for anything ambiguous |
| **Partner board** | Every engagement, its current blocker, blocker age, deadline proximity, and who owns the next move — sortable by what will blow a deadline first. | — |
| **Scope ledger** | Detects out-of-scope requests as they arrive (new entity, new state, prior-year amendment, advisory question outside the letter), logs them against the engagement letter, and hands the partner a billable-or-forgive decision with the evidence attached. | R1, always |

**Integrations:** Karbon / Canopy / TaxDome (jobs, clients, requests), QBO / Xero (books), email + SMS, the firm's document store.

## 5. The ROI model (assumption-stated)

```
Chase time       = open items/wk × touches each × minutes per touch × loaded staff rate
Cycle time       = engagements × days of blocker age removed → WIP days → cash conversion
Intake time      = documents/wk × minutes to classify and file × loaded rate
Recovered scope  = out-of-scope events × capture% × avg billable value
```

Cycle-time value is a **cash-conversion** claim, not a revenue claim, and the build must say so on the panel. Recovered scope is the honest headline: it is new revenue, it is measurable, and it is invisible today.

## 6. The demo path (10 minutes)

1. Partner board mid-season: 34 engagements, blockers sorted by age, three deadline-critical.
2. One engagement: eleven open items, nine chased automatically at different cadences, two escalated to a partner task with the reason.
3. A client emails four photos of bank statements → classified, matched, renamed, filed; the fifth is last year's → flagged as a mismatch, not filed.
4. The scope ledger: a client's "quick question" about a new state registration, logged against the engagement letter with the thread attached, awaiting a bill-or-forgive call.
5. The event log, the counted automation rate, and the classifier's eval score including its false-match rate.

## 7. Guardrails

**No tax positions, no accounting judgments, no advice.** The system extracts, classifies, chases, and drafts; a CPA decides. Any client question touching a tax position or a treatment is routed to a human unanswered — visible in the demo. Client financial data is confidential (and IRS §7216 constrains use and disclosure of taxpayer information) — flag that a real deployment needs counsel review of data handling and consent language, and keep the prototype on synthetic data only. No document is deleted, ever; misfiled means re-filed with both states in the log.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for accounting, bookkeeping and tax firms. Working name: Close OS.**

Build it into `Pre Build Ideas/accounting-firms/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, never touching real client financial data. Read `CLAUDE.md`, `processes/ai-os-modules.md` and `processes/autonomy-matrix.md`, then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and honesty rules exactly.

**The business you are modelling.** A 14-person CPA firm: ~$2.2M revenue, ~230 clients, a monthly bookkeeping/close book of ~70 clients plus ~400 tax returns in season, three partners, six staff accountants, two admins, running Karbon over QBO. Model both rhythms — the monthly close cycle and the ten-week season spike — because the product has to survive the spike. Build engagement letters with real scope boundaries. A managing partner should recognize their own March in the seed.

**The chase is the entire product thesis. Build these five:**

1. **Engagement state machine.** Every engagement (monthly close, 1040, 1120S, audit prep) carries a structured open-items list: item, entity, period, responsible party, dependency, status. An engagement can never sit in a vague "in progress" — it must name its current blocker and the blocker's age. Make that structurally impossible to violate, in `core.py`.
2. **The chaser.** Per-client cadence and preferred channel, personalized to what is *actually* still outstanding — never a re-sent generic list, and never a chase for something already received. The ladder escalates and terminates at a partner task rather than looping forever. Drafts route through an approval gate until a recorded streak earns R2.
3. **Intake classifier.** For arriving documents, identify type / entity / period, match to the open request, rename to the firm's convention, and file. Mismatches — wrong year, wrong entity, duplicate, illegible, password-protected — are flagged with a reason and never silently accepted. The false-match rate is measured and reported separately, because a document filed to the wrong entity is worse than one not filed.
4. **Partner board.** Every engagement, its blocker, the blocker's age, deadline proximity, and who owns the next move, sortable by what blows a deadline first.
5. **Scope ledger.** Detect out-of-scope requests as they arrive — a new entity, a new state, a prior-year amendment, an advisory question outside the engagement letter — log them *against the letter's actual language*, attach the evidence thread, and present a bill-or-forgive decision to the partner. This is the revenue half of the product; give it real design attention.

**The licensure guardrail belongs in `core.py` as a rule, not a prompt string.** The system never takes a tax position, never makes an accounting judgment, and never gives advice. A client question touching treatment, deductibility, entity choice or a filing position is routed to a CPA *unanswered*, and that refusal must be visible in the demo. Also: no document is ever deleted — a misfile is corrected by a new event, with both states in the log.

**Architecture.** Python stdlib only. `core.py` holds every rule: the engagement and open-item model, deadline calendars, dependency logic, chase cadence and escalation, the document taxonomy and matching rules, engagement-letter scope evaluation, and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the firm at any scale (`--clients 230 --months 18`) including open items at every age, documents arriving misnamed and mis-yeared, clients with wildly different responsiveness, and out-of-scope requests buried in ordinary email threads. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>`; (2) every state change appends to an immutable event log with actor and rung, and the automation rate is counted from it.

**ROI panel:** chase time, cycle time, intake time, recovered scope — from the firm's own inputs, arithmetic on screen, labelled a MODEL. Cycle-time value must be labelled a **cash-conversion** effect, not revenue. Staff-time savings in hours *and* dollars, reported separately from recovered scope. Any line without a recorded input renders blank with its reason.

**Moat layer:** approval gate as the R1 floor on every client-facing message; an eval harness scoring document classification and request-matching against a labelled set you generate, with the false-match rate broken out; audit log view; rung promotion only on a recorded streak.

**Confidentiality posture:** note in the README that live deployment requires counsel review of taxpayer-information handling and consent (IRS §7216 constrains use and disclosure), and that this prototype avoids the question entirely by using synthetic records.

**Data:** synthetic only — invented client and entity names, 555 phone ranges, fake EINs that are obviously fake, no outbound network calls. Stub Karbon/Canopy/TaxDome, QBO/Xero, email/SMS and the document store behind adapter interfaces; a missing adapter reports `cannot-simulate`, a blocker, not a pass.

**White-label:** the demo firm's brand only — no yourco name, logo, or agent names on any client-facing surface.

**Tests:** `test_close_os.py`, stdlib asserts, pinning: an engagement cannot be "in progress" without a named blocker; the chaser never chases a received item; a wrong-year document is flagged and never filed; a tax-position question is always routed unanswered; a scope event cannot be logged without a citation to the engagement letter; an uncomputable ROI line returns `None` with a reason; the event log is append-only.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (partner board mid-season → one engagement's eleven open items → four statements classified and a fifth flagged → a scope event caught in an email thread → event log), and an honest "what this does not do yet." Report the test count and everything it refuses to compute.

Do not send anything, do not deploy, do not use a real firm's or client's name.
