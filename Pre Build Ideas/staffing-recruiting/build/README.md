# Redeploy OS — build 9 of 10

Pre-built vertical AI OS for staffing and recruiting agencies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # 11,000 candidates, 865 assignments, 16,500 credentials
python3 test_redeploy_os.py          # 73 assertions, every one a refusal
```

Launch name **`prebuild-redeploy-os`** (port 8829, 127.0.0.1 only).

## What it is

"Ironline Staffing" — 19 people, $14M, light industrial and skilled trades. Six modules:
**database-first shortlist**, **screen & schedule**, **submission packet**, **redeploy watchtower**,
**credential tracker**, **desk board**.

## The load-bearing guardrail

**The system never rejects a candidate and never makes a hiring decision.** `reject_candidate` is
declared **R0 / never promotes**; so are `shortlist`, `submit_to_client` and `screen_evaluative` —
a shortlist shapes who gets *considered*, which is a human's call however good the streak gets.
There is no code path in `agents.py` that sets a candidate to rejected, and a test asserts no
candidate record ever carries a rejected state.

## Excluded factors cannot reach the arithmetic

`_permitted()` strips a candidate record down to twelve job-related factors **before** scoring, so
an excluded field cannot influence a ranking even if somebody adds it to the data later. Twenty-two
factors are named as excluded — including the proxies that get missed: graduation year, ZIP code,
neighborhood, language at home, employment gaps, credit score, arrest record, prior salary history.
Even the candidate's **name** is stripped.

The audit runs in the product, not just in the tests: the Trust panel writes every excluded factor
into a candidate record, re-scores, and shows both numbers side by side — **clean 6.47, poisoned
6.47, influence detected: none**. That side-by-side is the artifact a plaintiff's lawyer would ask
for, which is why it lives on a screen rather than in a comment.

## Ranked, never rejected — and the gap statement

Every ranked candidate carries its reasons, including the *absences*: "verified experience not
recorded", "no performance notes recorded", "commute to this site not recorded". A candidate the
system will not place is **blocked with the blocker named** — an expired forklift cert, 90 minutes
from the site — so a recruiter can overrule it.

When the database genuinely cannot fill a req, the honest output is better than a padded list:

> *"We have nobody on file with cnc_setup, welding_tig, quality_inspect, maintenance and a current
> welding_cert within 45 minutes of west. That is a sourcing job, not a search job."*

## Other refusals

- **A credential with no issue date is unknowable, never current.** ~8% of the seeded credentials
  have none, and they appear in their own list.
- **The redeployment rate is counted**, not asserted — 5.8% on the seeded book (16 of 277 ended
  assignments followed by a new one inside 30 days). A low number is the sales argument.
- **Speed-to-submit is a scenario with no number**, because whether being first actually wins is
  answerable from the agency's own submission history and nobody else's.
- **No silent caps.** The req sweep is capped at 15 per run and reports *"capped at 15 per run; 35
  still waiting"*.
- **The system never messages a worker about their next assignment** — that conversation is a
  recruiter's, and the redeploy outreach is drafted at R1.

## The Present module — the branded submittal (added 2026-08-17)

The single most repeated document task on a staffing desk: take the candidate's résumé and re-render
it into the agency's own brand, presentation-grade, before it goes to the client. The market proved
demand for this as a standalone product category; here it is a module of the desk, with the honesty
contract the "AI resume enhancer" junk doesn't have — **a render is a reformat, never an
enhancement**:

- **Nothing is invented — structurally.** The renderer reads only `RENDER_FIELDS` from the recorded
  source résumé; a skill on the CRM record that the source doesn't carry cannot appear, a missing
  date renders as *"not recorded"*, and `provenance_check` re-derives all of that from the output so
  a renderer bug is caught rather than shipped. `add_unsourced_claim` is declared **R0,
  never-promote** — fabrication with the agency's name on it.
- **Contact routes are withheld by construction.** Candidate email/phone/address/LinkedIn are not on
  the render whitelist, and a second regex pass redacts anything contact-shaped pasted into free
  text — a submittal that leaks the candidate's number is how a client goes direct. The scrub is
  **reported** ("4 contact fields withheld"), never silent.
- **Wording is a human's.** Polish suggestions ("responsible for" → "led") are drafted and queued
  **R1** with the original beside each line; until a recruiter approves, the render ships the
  source's own words. Rewording somebody's professional history is a claim about them.
- **No source, no render.** A candidate with no résumé on file gets a refusal on the record, not an
  improvised document.
- The **render-honesty eval** poisons a source with contact routes in five fields plus two pasted
  into free text and asserts zero leaks and zero unsourced claims, live at `/api/eval`.

Demo: the **Present** tab → "Render the demo submittal" (`sb_demo_present` — a source résumé that
deliberately carries a phone number inside the summary text, so the scrub is visible working).

## Three bugs found by running it

1. **O(n²) credential lookup** — `blocking_credentials` reloaded all 16,500 credential rows for
   every one of 11,000 candidates, per req. Indexed once per pass; a shortlist went from minutes to
   0.14s.
2. **The evals could not run without store state**, which meant the scorer could only be audited
   against a live database. Credentials are now injectable.
3. **The compliance sweep wrote 4,202 individual events**, making the audit log unreadable and each
   write slower than the last. Only actionable warnings (on-assignment) get their own row now; the
   rest are one summary event. Log went from 4,200+ rows to 178.

## 10-minute demo

1. **The desk** — open reqs, median time to submit, assignments ending in 21 days, redeployment rate.
2. **Open reqs** — the 4:50pm forklift req: **25 ranked from 11,000**, each with reasons, and 30
   blocked with their blockers.
3. The **gap req** — zero ranked, and the sentence that is worth more than a list.
4. **Redeploy** — 33 opened at T-21, each with the open reqs that fit and a draft for the recruiter.
5. **Credentials** — expiring and expired, with the billing impact spelled out for anyone on
   assignment; then the unknowable ones.
6. **Trust & audit** — the excluded-factor audit with both scores, the permitted/excluded lists,
   `reject_candidate` at R0.

## What this does not do yet

- **No integrations.** Bullhorn/JobDiva/Crelate, SMS, calendar and the background/credential vendor
  are adapter seams.
- **No résumé parsing.** Skills and experience are structured fields; a real deployment reads
  documents and that is where most of the excluded-factor risk actually enters.
- **Matching is deterministic scoring, not a model** — deliberately, because every factor has to be
  printable next to the candidate.
- **An adverse-impact review and counsel sign-off are required before live use**, and automated
  employment decision tools are regulated in a growing number of jurisdictions. This build does not
  substitute for either.
- **Nothing is sent.**
