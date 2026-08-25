# Loop — connector-spotter (Bird): referral-shaped moments → a warm intro drafted in the connector's voice

**Cadence:** weekdays 09:10 ET (`yourco-connector-spotter.timer`) · **Owner:** Bird (program) · David (CRM/data) · Ray (consent language) · the Founder approves everything
**Output:** a dated note in `loops/connector-spotter/` on **every** run + (only when there is something to propose) draft records appended to `crm/_pending-intros.json`.

> **STAGED — counsel- + launch-gated, and consent-gated on top of that.** This is step 3 of the Connector OS
> build sequence (`processes/partnerships/connector-os.md` §1, `decisions/2026-08-07_connector-os.md`).
> **No connector has signed.** Today, and until one does *and* grants scoped consent in writing, the correct
> and complete behavior of this loop is: **report "no opted-in connectors — nothing to scan" and stop.**
> That is the primary path below, not a fallback.

---

## The one-line job
A connector's world is full of business owners complaining about missed calls, drowning in paperwork, or
hiring for a role an agent could do. The connector forgets, or feels weird pitching. The spotter notices the
moment and **hands them a warm intro already written in their own voice** — so their job is
**approve-or-decline**, never remember-to-refer.

**That approval IS the product.** The loop drafts; the connector decides; the Founder sends. Nothing else.

## What it may NEVER do (read this before the method)
1. **Never sends anything. Ever.** No email, no SMS, no DM, no calendar invite, no reply, no label, no delete.
   The drafted intro goes to a pending file a human confirms. The runtime approval gate (`~/.claude/settings.json`:
   deny send/delete/Bash) is the machine backstop; this rule is the policy that must hold even if the gate changed.
2. **Never reads a connector who has not granted consent** — see §Consent. Absent consent record ⇒ that connector
   does not exist to this loop.
3. **Never reads outside the granted scope** (named mailbox/calendar, named window, named purpose).
4. **Never mines connector data for yourco's own outreach** (`connector-os.md` §1 constraint). A business the
   spotter notices in a connector's inbox does **not** become an yourco lead, a CRM company, a Sadie signal, an
   Instantly contact, or an entry in any outbound list. It exists only inside that connector's own draft.
   *If a run is ever tempted to "also add this to the CRM" — that is the violation. Don't.*
5. **Never writes `crm/data.json`.** Never edits or deletes anything in `crm/_pending-intros.json` that a human
   has already confirmed or declined — append only.
6. **Never contacts the third party** whose complaint was noticed, in any way, for any reason.
7. **Never infers consent** from a connector being friendly, from a prior verbal yes, or from the Founder saying it's fine
   in chat. Consent lives in the record described below or it does not exist.

## Consent — explicit, per-connector, scoped, revocable
**Where the state lives (proposed field — this loop does not create it):**
`crm/data.json` → `meta.connectorConsent` — a name-keyed map, mirroring `meta.repRecruiters` / `meta.connectorLadder`:

```jsonc
"connectorConsent": {
  "Jane Connector": {
    "scopes": ["gmail.read"],            // explicit; "calendar.read" is a SEPARATE grant
    "account": "jane@herdomain.com",     // the exact mailbox granted — no others
    "purpose": "referral spotting only", // the only purpose the data may serve
    "grantedAt": "2026-09-01",
    "grantedVia": "connector consent addendum, countersigned — <doc id>",
    "windowDays": 7,                     // how far back a run may look
    "revokedAt": null                    // set → the connector is invisible to this loop, immediately
  }
}
```

Rules that make the field mean something:
- **Written and countersigned, not clicked.** `grantedVia` must name a real signed addendum (Ray drafts it;
  counsel checklist item 4 — *"the spotter touching a connector's inbox/calendar — consent language, scope, and
  whether yourco becomes a processor of third-party data it never wanted"* — must clear first).
- **Per-scope.** Mail and calendar are separate grants. A missing scope is a denied scope.
- **Revocation is instant and self-serve.** `revokedAt` set (or the record removed) ⇒ the next run treats that
  connector as non-existent and says so in the artifact. Nothing about them is retained beyond drafts already
  in the pending file, which are dropped on the same run.
- **A consent record without a matching R0+ rung is not consent** — the connector must be joined
  (`crm/connector_ladder.py` → `can(rungN, "referral_spotter")`, an **R0** capability). Both must be true.
- **Data minimization.** The loop keeps no copy of anything it read. What persists is only the draft it wrote
  and the counts in the dated note.

## Inputs
1. `crm/connector_ladder.py` → `compute()` — who is joined, and at which rung. Filter to `can(rungN, "referral_spotter")`.
2. `crm/data.json` → `meta.connectorConsent` — who granted what, still un-revoked.
3. For each connector who passes **both**: their granted source(s), read-only, within `windowDays`.
4. `crm/_pending-intros.json` — what is already proposed, so nothing is proposed twice.
5. `brand/writing-rules.md` — only as a floor. **The draft is written in the connector's voice, not yourco's**
   (see §Voice).

## Method
1. **Step 0** per the loop contract (learnings + skills).
2. **Build the eligible set:** connectors who are (a) `R0+` with `referral_spotter` unlocked, **and** (b) hold an
   un-revoked consent record. **If the set is empty → jump to §The empty path. This is the expected outcome today.**
3. For each eligible connector, within their granted scope and window, look for **referral-shaped moments** — a
   business owner in their world saying something that maps to a pillar in `processes/ai-os-modules.md`:
   - missed calls / "we can't answer the phone" / voicemail full → Intake
   - drowning in paperwork, quotes, proposals, invoices → Sales / Back Office
   - hiring for a role an agent could do (front desk, scheduler, follow-up, dispatcher) → any pillar
   - leads going cold, no follow-up, reviews unanswered → Sales / Customer
4. **Qualify before drafting** (a bad intro costs the connector a relationship — this filter is the whole quality bar):
   - a **real business** the connector has a **real relationship** with (they'd say hi at a store, not a stranger)
   - the complaint is **theirs, recent, and in their own words** — not something the connector said about them
   - it maps to something yourco actually builds
   - not already a CRM company, not already proposed, not declined before
   - **Unsure → skip.** Under-proposing is free; a wrong intro is not.
5. **Draft the intro** (see §Voice) and append a record to `crm/_pending-intros.json`:
   ```jsonc
   { "id": "<uuid12>", "connector": "Jane Connector", "created": "2026-09-02",
     "business": "Bayside Dental", "who": "Dr. Amara Osei — owner",
     "moment": "one factual line: what they said, and when",
     "source": "spotter gmail 2026-09-01 · thread <id>",   // provenance, always
     "pillar": "Intake / Front Desk",
     "draft": "the intro, in the connector's voice, ready to send as-is",
     "status": "pending" }                                  // pending → approved | declined, by the connector
   ```
   Atomic write, valid JSON array, no duplicates (match on `connector` + `business`).
6. **Write the dated note** to `loops/connector-spotter/YYYY-MM-DD.md`: eligible connectors, sources read, moments
   seen, drafts proposed, skipped + why. Counts must be real; an unverifiable claim doesn't go in.

## The empty path (today's correct behavior, and it is a complete run)
When no connector is both joined and consented — **the state on every run until the program launches**:

- Do **not** open any mailbox, calendar, or connector surface. There is nothing lawful to read.
- Write the dated note with exactly this shape:

  ```
  # connector-spotter — 2026-08-07

  **No opted-in connectors — nothing to scan.**

  - Connectors at R0+ with `referral_spotter` unlocked: 0 (23 connector contacts in the CRM, 0 joined —
    the program is counsel- + launch-gated)
  - Consent records in `meta.connectorConsent`: 0
  - Sources read: none. Drafts proposed: 0.

  Nothing to do. This is the expected result until the Connector OS clears
  `processes/counsel-gates.md` and a connector signs + grants scoped consent.
  ```
- **Stop.** Do not go looking for something else to be useful about. Do not scan the Founder's inbox "as a stand-in."
  Do not generate example drafts to "prove the loop works." Do not propose connectors who *should* opt in.
  **Empty is a valid result** (`_loop-contract.md`); padding it is the failure.

## Voice — the draft is theirs, not ours
The single thing that makes this land: the connector reads the draft and thinks *"yeah, that's how I'd say it."*
- Match **their** register from their own prior messages in scope — length, greeting, sign-off, whether they use
  contractions or exclamation points. Do not imprint yourco's voice on a person.
- Give-first, never pitch: name the thing the owner said, offer the introduction, no product claims, **no prices**
  (Polo's rule), no invented results, no "we guarantee."
- Short. An intro that needs a paragraph of setup isn't warm.
- Never put words in the third party's mouth or quote them to a stranger without it being obviously their own words.
- Sensitive verticals (medical, legal, financial, caregiving, funeral) — no clinical/legal/financial framing at all;
  the intro is a person-to-person introduction, full stop.

## Failure / empty handling
| Situation | Behavior |
|---|---|
| No eligible connectors | §The empty path. Complete run. |
| Consent record present but source connector unavailable on the runtime | Say so by name in the note; read nothing; do not guess. |
| Consent revoked mid-window | Treat as never-granted; drop any pending drafts for them this run; note it. |
| A moment is ambiguous | Skip it and record the skip reason. Never draft on a maybe. |
| Same read fails twice | Stop (anti-spin), write a partial note naming the failure. |
| `crm/_pending-intros.json` missing | Create it as `[]` **only when there is a draft to write** — an empty run leaves the file absent. |
| Nothing found for an eligible connector | "quiet — nothing referral-shaped this window." Honest, and normal. |

## Verification the artifact must carry
Sources actually opened (named), window dates, eligible-connector count with the reason for each exclusion, drafts
proposed with their `source` provenance, skips with reasons. No count that wasn't counted.

## Open questions before this ever runs against real data (Ray → counsel)
Tracked in `processes/counsel-gates.md`; mirrors `connector-os.md` §Counsel questions 1 and 4.
1. Consent addendum language + scope wording (item 4) — and whether yourco becomes a **processor of third-party
   data it never wanted** by reading a connector's mailbox that contains other people's messages.
2. Retention: how long a proposed draft may sit in the pending file after revocation (current answer: zero — dropped
   on the next run).
3. Whether the spotter, as a benefit given at **join**, complicates §A of the pyramid analysis (item 1) — it is
   deliberately scoped as a **work tool**, not a thing of value for enrolling.
