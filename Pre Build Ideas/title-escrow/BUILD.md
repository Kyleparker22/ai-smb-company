# Closing OS — title & escrow (build 20)

**Working name:** Closing OS · **Launch:** `prebuild-closing-os` · **Port:** 8840

## The idea

A title agency is a message-routing business with a $400k wire in the middle. Business email
compromise — the "updated wiring instructions" email — is the industry's defining loss, and it
works because a busy processor treats a wire-change message as a task instead of an attack.
Closing OS treats every wire-touching message as a fraud signal by default, tracks curative items
as evidence, and never lets "clear to close" be asserted over an open item.

**Buyer:** the agency owner / escrow manager. Thinks in open files, closing dates, and the one
wire that must never go wrong.

## The bleeding neck

- One redirected wire is an agency-ending event. The scam is a *message*, so the defense is
  message discipline — which software can enforce and tired humans cannot.
- Curative chaos: payoffs, lien releases, HOA letters chased by memory; "clear to close" declared
  by vibe.
- The status-call flood: every party calls twice a week for "where are we."

## Modules

1. **The wire stop** (Intake) — any message touching wire instructions (new, changed, resend,
   different account, payoff bank change) is a **fraud signal**: routed to a human with the
   callback protocol shown verbatim — *call the known number on file, never the number in the
   message; never reply with instructions.* The system **never sends, changes, confirms, or
   restates wire instructions in any channel** — R0, twice over.
2. **Curative tracker** (Operations) — typed items (payoff, lien release, HOA estoppel, survey,
   POA) with requested/received records per file. **"Clear to close" cannot be asserted while any
   item is open** — the refusal lists the open items.
3. **Status desk** (Customer) — "where are we" drafts computed from recorded state only; a close
   *date* promise is R1 and never promotes.
4. **Document chase** (Operations) — bounded ladder per outstanding item, one touch per run.

## Guardrails (load-bearing)

- `send_wire_instructions` / `confirm_wire_change` — **R0, never, in any channel.**
- `assert_clear_to_close` — structurally refused over open curatives.
- `legal_opinion` — **R0.** Title issues draft for the underwriter or an attorney.
- `promise_close_date` — R1, never promotes.
- The eval's costly class is a missed wire signal.

## ROI model

Status-call hours → time saved · files per processor → their capacity number · chase-driven days
saved → cash timing (their number) · wire-fraud exposure → scenario (never a saving; the average
BEC loss is not our number to quote).

## 10-minute demo

Board → the "updated wiring instructions" email (fraud protocol verbatim, nothing restated) → ask
the system for wire instructions — refused → the curative board → try "clear to close" on the file
with an open payoff (refused, items listed) → clear it on the clean file (drafts R1) → ROI → trust.

## Build prompt (§8)

Build `Pre Build Ideas/title-escrow/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8840,
launch `prebuild-closing-os`. Seed "Cornerstone Title & Escrow": ~85 open files at every stage
with typed curative items, messages incl. every wire-signal shape and routine status asks. Eval
costly class = missed wire signal. Tests pin the two wire R0s, the clear-to-close refusal, the
bounded chase, ROI blanks, counted automation.
