# The Connector OS — yourco's product, pointed at its own connectors

> **STAGED / counsel-gated.** Nothing here is offered to any connector until the program clears §A/§B of
> `processes/partnerships/legal/counsel-review-checklist.md` and the launch gate. Decision:
> `decisions/2026-08-07_connector-os.md`. Owner: **Bird** (program) · Kimi (build) · David (CRM/data) ·
> Charles (payouts) · Ray (legal) · the Founder (approves everything).

## The idea in one line
Every other referral program hands you a link and a spreadsheet. yourco hands you **agents, a ledger you
can audit, and a ladder you climb on evidence** — because yourco is the only referral program run by a
company whose product is exactly those three things.

Four parts, built in this order:

---

## 1. The connector's agents (their own AI, free)

**Two tiers, deliberately split** — one is a work tool given at join, one is a real digital employee
earned by producing. The split exists for two reasons: cost (a full build per connector, pre-revenue,
across 25 people is real money) and compliance (see §Counsel questions — anything valuable given *for
enrolling* muddies the pyramid analysis; anything earned by *producing* does not).

| | Given at | What it is |
|---|---|---|
| **The referral-spotter** (work tool) | R0 — join | A lightweight agent that helps them do the connector work: watches their world *with explicit permission* (their inbox/calendar, opt-in), notices referral-shaped moments ("your accountant just complained about missed calls"), **drafts the intro in their voice**, and waits for their approval. Never sends. Their job becomes approve-or-decline instead of remember-to-refer. |
| **Their own digital employee** (the real thing) | R1 — first referral reaches a real conversation | A working agent for *their* business or side hustle, built and operated free while they're active. Makes them a genuine user of what they refer — "I use this myself" is the most powerful sentence in this program, and no referral program on earth can offer it. |

**Why it's unprecedented:** the downline is powered by agents instead of hustle. Nobody selling AI
agents has ever thought to arm their referrers with them.

**Constraints:** the spotter is read-only + draft-only, permission-scoped, and bound by the same
approval gate as every yourco agent (no send / no delete). Connector data stays the connector's; it is
never mined for yourco's own outreach.

---

## 2. The glass ledger — the first referral program with an audit log

**Architecture decision (the Founder asked): a separate connector-facing console, NOT the CRM.** The CRM is
David's internal system of record — it shows every connector's book, every deal, margin, and internal
notes, none of which a connector may see. Same split yourco already runs: CRM (internal) vs client
console (client-facing).

- **One source of truth, never forked.** The console renders from the same `buildRepPayouts` /
  `crm/connector_statements.py` computation the Referrals cockpit uses. The tree a connector browses,
  the number the console shows, and the money Charles pays are the same math or they are a bug.
- **The new data: an append-only attribution log** (`crm/_attribution-log.jsonl`) — every attribution
  event, timestamped and immutable: referral registered → stage moved → first payment collected →
  payout computed → payout paid. Nothing is ever edited, only appended (corrections are new entries
  citing the old). This is the audit trail no commission program has ever offered.
- **What the connector sees:** every referral they've made and exactly where it sits · what it's worth ·
  what they're owed **to the penny with the math shown** · their rung and what earns the next one ·
  their downline and its override contribution · every event in their own history.
- **What they never see:** other connectors' books, yourco's margin, client internals, the CRM.

**Why it's unprecedented:** opacity is where the abuse lives in this category, so nobody removes it.
"The referral program you can audit" is a category-defining claim in a category people distrust.

---

## 3. The trust ladder — connectors earn autonomy, not just rate

yourco's agents earn autonomy per-action on eval evidence (`processes/autonomy-matrix.md`). Connectors
climb the same way. The commission escalator (10/12.5/15%) is **money**; this ladder is **agency** —
and it is self-policing, because a connector who sends junk never climbs and nobody has to police them.

| Rung | Earned by (evidence, not vibes) | Unlocks |
|---|---|---|
| **R0 · Joined** | Signed agreement + W-9 on file | Warm intros · **submitting contacts (Sourcer mode, §5)** · the Connector Console · the referral-spotter agent |
| **R1 · Proven** | 1 referral that reaches a real conversation (audit booked or discovery held) | **Demo generation — the give-first arsenal (§4)** · their own digital employee, free while active · **eligibility to recruit connectors (downline), moved here 2026-08-11** |
| **R2 · Producing** | First referred client live and retained 90 days | Quote Polo-locked prices · co-branded materials |
| **R3 · Trusted** | 3+ live referred clients, retention holding, zero conduct flags | Run the audit conversations with oversight (Bella supports + reviews the report) · deeper co-brand |
| **R4 · Advisor track** | Sustained book + the Founder's judgment | Carry their own book with yourco delivering underneath — the Connector→Advisor conversion the packet already invites |

**Demotion is real, same as the agents:** evidence reverses (a churned book, a bad-fit pattern, a
conduct flag) and the rung drops. Rungs are computed from CRM data, not granted by mood.

**⚠️ The recruiting gate moved to R1 on 2026-08-11, and the guardrail it was carrying is now gone.**
(`decisions/2026-08-11_connector-program-v2.md`.) Two facts, both of which have to be held at once:

- **Why it moved, and it is a good reason.** R2 requires a client live *and retained 90 days*. With
  zero signed clients, R2 was unreachable — the gate was not limiting *some* connectors, it was
  limiting **all** of them, indefinitely. A connector with a strong network could never build one.
- **What it cost.** Requiring a live, retained client before recruiting was a classic legitimate-MLM
  guardrail ("active-book qualification"), and it was the specific **non-depth guardrail** offered to
  counsel once unlimited override depth was locked (`decisions/2026-08-07_override-depth-uncapped.md`,
  checklist item 4b). the Founder also chose to make the override **payable at R1**, so there is no
  active-book qualification left anywhere in the design. Counsel is now asked to price
  recruiting-at-R1 + uncapped depth + a bounty paid on non-revenue events **as a combination**
  (checklist item **4c**) — that is the honest question, and it is a harder one than the old §A.

*Do not restore the old framing in any surface. If it reappears in the packet or the training, it is
telling a connector something that is no longer true.*

---

## 4. The give-first arsenal (earned at R1 — the Founder's call)

A button that generates a real, personalized working demo for any business the connector just met:
walk into your dentist's office, say "watch this," and minutes later that dentist has a live agent
answering their own phone script. The connector never pitches — they **give**. It is the give-first
doctrine placed in 25 people's hands.

**Earned, not issued** (the Founder, 2026-08-07): a generated demo carries yourco's brand to a stranger — an
external surface — and each one costs real build/token spend. R1 evidence gates both risks.

**Guardrails:** demos are generated from the existing demo-kit template (`clients/_yourco-template/
demo-kit/`), carry no prices (Polo's rule), make no fabricated claims (credibility gate), are rate-
limited per connector, and every generation is logged to the attribution log — so a connector who
generates fifty demos and books nothing is visible immediately.

---

---

## 5. Referral modes + the submission bounty (v2, 2026-08-11)

**A referral carries a mode; a person does not.** The same connector introduces one owner and sources
another, and both are normal — so this is a per-referral field (`meta.referralMode[<companyId>]`,
default `introducer`), set by yourco, read-only to the connector like stage and retainer.

| Mode | What the connector did | Who makes the approach |
|---|---|---|
| **Introducer** | An actual introduction to an owner they know | The connector opens the door |
| **Sourcer** | Submitted a name + contact, no introduction | **yourco** |

*Naming note:* "Connector Partner" was rejected because **Partner already names the 11+ active-client
commission tier**. Don't reintroduce it.

**The bounty** — two steps, paid on top of any commission that later lands:

| Event | Pays |
|---|---|
| Contact submitted **and verified** real + reachable (yourco, within **24–48h**) | **$25** |
| That contact **books a real conversation** (the ladder's own R1 evidence) | **$25** |
| That contact becomes a paying client | the normal 10 / 12.5 / 15% escalator |

Amounts live once, in `crm/connector_statements.py` (`BOUNTY_VERIFIED` / `BOUNTY_BOOKED`); the ledger
is `bounties()`, next to `books()`, because there is one computation of what yourco owes.
**`BOUNTY_PAYABLE` is False** — every surface renders *accrued, not payable*, exactly as the override
does. Open, and the Founder's to set: the per-connector monthly cap (mechanism live, reads
`meta.connectorSubmissionCap`; unset renders as unset, never as a guessed default), what counts as
verified, and whether the booked-call step stacks with or nets against the first commission.

**Why a Sourcer submission is the compliance-heavy half.** yourco becomes the caller, so TCPA / FL
FTSA / CAN-SPAM attach to **us**, not the connector. The submission form therefore requires *how you
know them* and asks whether the person is expecting contact — those are the two questions the operator
judges before yourco picks up the phone, and a submission without them cannot be verified. Bought,
scraped, or copied lists are rejected on sight. Duplicate detection (business / email / phone) is in
`connector_writes.duplicate_of()` because a per-contact bounty's gaming surface is selling the same
owner twice. Nobody verifies their own submission — the queue is at `/verify`, operator-only,
**Bird owns it**, and the 24–48h is a promise to someone waiting to be paid.

## Counsel questions this raises (add to the checklist before any of it ships)
1. **The agents as benefits:** confirm the R0 spotter reads as a *work tool* and the R1 employee as
   compensation *for producing a referral* — neither as consideration for enrolling. Does giving
   anything of value at join, however small, complicate §A?
2. **The recruiting gate moved to R1 and the override is payable there too** — so the active-book
   qualification is gone entirely. Combined with uncapped depth and a bounty paid on non-revenue
   events, does §A still hold, and if not what is the minimum change that preserves the intent?
   (Checklist item **4c** — the second hard stop.)
2a. **The submission bounty** — yourco pays $25 on verification and $25 on a booked call, before any
   revenue. Is a bounty on a non-revenue event distinguishable from compensation for enrolling, given
   it is paid for producing a *contact* rather than for signing up? What must the disclosure say?
3. **Connector-generated demos:** who owns liability for a demo shown to a stranger by a non-employee?
   Does the arsenal create agency/apparent-authority exposure, and does the agreement cover it?
4. **Data handling:** the spotter touching a connector's inbox/calendar — consent language, scope, and
   whether yourco becomes a processor of third-party data it never wanted.
5. **The published earnings distribution** (if the anti-MLM covenant ships later) — required content
   and cadence.

## Build sequence (when the gate clears)
1. Attribution log + rung computation in the CRM (internal, buildable now — no connector sees it).
2. The Connector Console reading that log (connector-facing → gated).
3. The referral-spotter agent (permission-scoped → gated).
4. Demo generation wired to the R1 rung (→ gated).
5. Their-own-employee builds, one per R1 connector (cost-managed, one at a time).

*Steps 2–5 are launch + counsel gated. Step 1 is internal plumbing and can be built any time —
it is also what makes the rungs real rather than aspirational.*
