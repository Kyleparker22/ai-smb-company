# loops/_build-journal — how long a build actually took, and what it was actually made of

The evidence base behind "how long will this take and what will it cost?" — the Founder's ask, 2026-08-07.
Written and read by **`runtime/build_journal.py`**. Nothing here is hand-maintained.

## What's in here
- **`sessions.jsonl`** — the journal itself. **Append-only**, one JSON object per line, monotonic
  `seq`, never edited — the same discipline as `crm/_attribution-log.jsonl`. Event types:
  `session.started` · `session.step` · `session.stopped` · `session.backfill` · `session.correction`.
  A mistake is fixed by appending a `session.correction` citing the session; the wrong line **stays**.
  That property is the audit trail — do not "clean up" this file.
- Dated `--estimate` reports land here **only when someone asks for one in writing**; the live answer
  is always `python3 runtime/build_journal.py --estimate "<kind>"`, computed from the journal on the
  spot. A saved report is a snapshot, never the source.

## The three questions this answers (that the cost ledger can't)
`clients/<client>/cost.md` (via the `log-build-cost` skill) captures **dollars, roughly, after the
fact**. This journal adds:
1. **time** — measured wall duration per session, marked `wall` / `stated` / `unknown`;
2. **process** — the ordered steps a build consisted of, so it reads as a playbook for the next one;
3. **queryable history** — `--estimate` reports median/range hours, median cost, the typical step
   sequence, and the sample size.

## How to use it
```
python3 runtime/build_journal.py --start <client> --phase <discovery|build|tools|run> \
    --kind "quote platform" --what "what you're building"
python3 runtime/build_journal.py --step "what you just did"        # as you go
python3 runtime/build_journal.py --stop --cost 22 --tokens 1200000 --notes "..."
python3 runtime/build_journal.py --list-open
python3 runtime/build_journal.py --report [--json]
python3 runtime/build_journal.py --estimate "quote platform" [--json]
```
Procedure and when to invoke it: `.claude/skills/log-build-session/SKILL.md`.
`YOURCO_BUILD_JOURNAL=<path>` redirects the journal — use it for tests so this file stays clean.

## The honesty rules (why you can trust a number that comes out of here)
- **A session's tokens are not isolable from org-wide spend.** Any `--cost` is recorded as
  `est. — session self-report` unless `--metered` is passed with a console/invoice number behind it.
  An estimate is never presented as metered.
- The org's metered day spend (`loops/_anthropic/latest.json`, already converted from cents by
  `dashboard/server.py anthropic_cost()`) is stored as **context only**, labelled org-wide, never
  allocated to a session.
- **A forgotten session does not become 14 hours of work.** `--stop` past the 8h staleness threshold
  refuses and asks for the real number (`--hours`), or records the elapsed time explicitly flagged
  unreliable (`--accept-stale`).
- **Below 3 timed sessions, `--estimate` refuses to estimate** and prints the raw sessions instead.
  A confident median of n=1 is worse than no number — that refusal is the feature, not a limitation.
- Backfilled sessions carry `hours_precision: "unknown"` and are excluded from every hours median
  while still being listed, so a reader sees them and judges.
