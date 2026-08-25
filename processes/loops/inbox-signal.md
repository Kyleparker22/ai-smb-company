# Loop — inbox-signal (weekly, Brett)

**Owner:** Brett (external landscape). **Cadence:** Fridays 07:15 ET, before `source-watch` (07:30)
and `brett-ideas` (08:00). **Output:** `loops/inbox-signal/YYYY-MM-DD.md`.

## Why this exists

`source-watch` reads Brett's **named roster** — YouTube channels and RSS feeds we chose. It cannot
see the other half of the landscape: **the AI and business newsletters that arrive in the Founder's inbox**,
which are where most industry signal actually lands and which nothing has ever read. Jim's
`inbox-triage` reads that mailbox but is scoped to *the Founder's time* — what needs a reply, what is a
deadline — and routes nothing to Brett. So the mail is read daily and its *landscape* content is
thrown away.

This loop reads the same mailbox for the opposite thing: **not what the Founder must answer, but what the
industry is telling us.**

## The line against the two neighbouring loops — do not blur it

| Loop | Reads | Looking for |
|---|---|---|
| `inbox-triage` (Jim, daily) | the mailbox | what needs **the Founder** — replies, deadlines, decisions |
| **`inbox-signal`** (Brett, Fri) | the mailbox | what the **industry** is doing |
| `source-watch` (Brett, Fri) | named RSS/YouTube | the same, from sources we chose |

**Dedupe is mandatory and one-directional.** This loop runs first and writes its item URLs to
`loops/inbox-signal/state.json`. `source-watch` runs 15 minutes later and must skip anything already
listed there. Greg Isenberg's newsletter is *both* on the source roster and in the inbox — without
this rule Brett gets the same item twice and the digest looks busier than the week was.

## Inputs

1. **Gmail, last 7 days**, restricted to newsletter/industry mail. Start from this query and refine
   it into `state.json` as senders prove themselves:
   `newer_than:7d (category:updates OR category:promotions OR label:newsletters) -in:sent`
2. `loops/inbox-signal/state.json` — message IDs already reported, plus the learned sender allow-list
   and block-list.
3. The triage filter: `.claude/skills/tool-triage/` + the ledger `decisions/2026-07-05_tool-triage.md`.
4. The anti-library `rejections/` — **injected into your prompt** by `runtime/run-loop.sh`.

## Method

1. **Search, don't read everything.** Pull the week's candidates by query. Cap at **40 messages
   scanned**; if the mailbox has more, say so in the artifact and raise the block-list.
2. **Headline-filter first.** Most newsletter mail is a repackaged press release. Keep an item only
   if it names a *mechanism, a number, or a named product*, and is plausibly about: AI capability,
   agent/ops tooling, SMB operations, or a competitor in a vertical yourco has a prebuild for.
3. **Read the survivors properly.** Open the message; follow the primary link with WebFetch when the
   mail is only a teaser. **Never triage from a subject line** — that is the failure `source-watch`
   already names.
4. **Cap the deep work.** At most **3 deep-dives**; one line each for the rest; **name anything
   dropped and why.** A capped loop that says what it dropped is honest; an uncapped one is a
   week-long read.
5. **Clear the anti-library before proposing.** Every proposal carries the contract's verdict line:
   `not previously rejected`, or `previously rejected <date> (<file>) because <reason>; what has
   changed since is <X>`.
6. **Triage each survivor** — adopt / steal-the-pattern / trigger-gate / skip — with one honest
   sentence. Prior art in the ledger first; a re-triage must say what changed.
7. **Write state.json** — message IDs seen, senders promoted to the allow-list, senders blocked.
8. **Hand to Brett.** The artifact IS the handoff: `brett-ideas` (08:00) and the monthly advisor memo
   both read `loops/inbox-signal/`. Post the digest to `#yourco-brett`.

## Output format

```
# Inbox signal — YYYY-MM-DD
Scanned N messages · kept M · dropped N-M (reason)

## Worth Brett's attention (0-3)
### <item> — <verdict>
source · what it actually claims · what it would change for yourco · anti-library line

## One-liners (the rest)
- <item> — <verdict>, one sentence

## Dropped, and why
- <sender/pattern> — <reason>; blocked in state.json / left for next week

## Feedback for the next run
what I'd do differently
```

## Pre-revenue / empty handling

**A quiet week is a real result.** If nothing clears the filter, the artifact says
`No item cleared the filter this week (N scanned).` and lists what was scanned. **Do not pad.**
Reporting three weak items to look productive is the exact failure the loop contract's anti-spin
clause exists to stop, and it costs Brett more than silence does.

**If Gmail is unreachable** — no connector, auth expired, gate change — write the artifact saying
**that**, name the missing input, and stop. Never substitute web search for the inbox and call it an
inbox scrub.

## What this loop may NOT do

- **No sending, no replying, no forwarding, no deleting.** Read and label only — the host gate
  enforces this (`send_email`, `delete_email`, `batch_delete_emails` are denied) and so does this SOP.
- **No editing `decisions/`, the triage ledger, `rejections/`, or any agent's docs.** It proposes;
  the Founder disposes.
- **No archiving or moving the Founder's mail.** `modify_email` is technically allowed by the gate; this
  loop does not use it. Changing the state of an inbox a human is also working is not a read-only act.

## Failure modes to watch

- **Duplicate reporting with `source-watch`** — the state.json handshake above is the only guard.
- **Sender drift**: a marketing list that once carried signal turns into pure promotion. Block it in
  `state.json` and say so; do not silently keep scanning it.
- **Teaser mail**: subject promises a finding, body is a paywall. Fetch the link or drop the item —
  never report the subject line as the finding.

## Watchdog

A silent miss is caught by the row in `processes/loops/watchdog.md`. Cadence: weekly (Fri).
