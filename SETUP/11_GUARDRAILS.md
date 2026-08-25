# 11 — The guardrails

> **Build step 11.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

Built last, and the reason anything above can be trusted. If you copy one layer of this system, copy
this one — it is what separates an OS from a pile of scripts.


## Your first run — what a fresh clone reports, and why

Run it now, before you change anything:

```bash
python3 runtime/consistency-check.py
```

You will see **95 checks passing and 5 warnings.** That is the correct starting state,
not a broken repo. The warnings are your onboarding list:

| Warning | What it means | Clears when |
|---|---|---|
| **connector counts disagree with the CRM** | you have zero referral partners and the docs describe a program | you add one, or delete the connector program |
| **launch-gate tracker — fields unrecorded** | you have not defined what "ready to go public" means for you | you fill in `processes/launch-gate.md` |
| **untagged Calendly links** | the site's booking links carry no UTM, so bookings will not be attributable | you swap in your own links with tracking |
| **HQ finance mirror is stale** | the dashboard's numbers do not match the workbook | you fill the model and run `python3 dashboard/refresh.py` |
| **HQ data.json is old** | placeholder dates ship with the template | your first real `refresh.py` run |

**Do not "fix" these by weakening the checks.** Each one is asking a real question about your
business, and a check you softened to get a clean board is worse than no check at all — it reports
green forever.

**The one thing to do on day one:** add an invariant of your own. Anything you have already caught by
eye twice is a candidate. That is the whole growth mechanism — *when a human catches drift by eye,
add it so it is never caught by eye twice* — and it is why the source repo went from ~44 checks to
94.

## The four machines

| Machine | What it catches | When |
|---|---|---|
| `runtime/consistency-check.py` | **83 invariants** — cross-surface drift, stale trackers, structural breakage | Mon 07:40 ET, and on demand |
| `runtime/doc_claims.py` | **documents that declare their own checks** — a number carries its verification inline; also every dead citation | on demand, and inside the check above |
| `runtime/test_evidence.py` | **228 assertions** pinning HQ's honesty rules — each guards a *refusal*, not a feature | on demand |
| the governance watchdog | agents/loops running that the sanctioned registry does not know about | Mon 07:45 ET |

## The rule that makes them grow

**When a human catches drift by eye, add it as an invariant so it is never caught by eye twice.**
That is the entire growth mechanism, and it is why the count went from ~44 to 83.

## Prove a check by breaking what it guards

A check nobody has seen fail is not a check. Every invariant added here is **sabotage-tested**: break
the thing it guards, watch it fire, restore, watch it pass. On the day this guide was written that
practice caught **two bugs inside newly-written checks themselves** — one crashed instead of
reporting, and one was tautological and passed a deliberately broken file.

## The honesty rules the machines enforce

- **Refuse rather than guess.** Every HQ panel declines to state a number its inputs do not support and
  **names what is missing instead**. `kb.py` reports a genuine miss as a miss. `doc_claims.py` reports
  a wrong number and never silently corrects it — because the number might be right and the glob wrong.
- **Propose, never apply.** `inbox_triage.py`, `vacancies.py`, agent expiry, and failure-trace skill
  patches all stop at a proposal. A human commits.
- **One fact, one guard.** Two checks on the same fact is a bug: improving one breaks the other. It
  happened twice in a single day.
- **Verify the effect, not the invocation.** `cmd | tail` reports *tail's* exit status, so a failed
  check piped anywhere exits 0 and reads as success. Check the artifact
  (`learnings/ops/2026-08-24_pipe-to-tail-hides-exit-status.md`).

## The values underneath

`06_business-plan.md` §"The company's core principles" — 12 principles, each citing what enforces it.
Two are worth quoting because they are routinely misread:

- **#11 Never apologize for what we are** — covers the price, the size, the standard. It **still
  requires apologising for real failures**; Principle 1 outranks it. Internally it is a tone rule:
  state a shortfall, do not apologise for it; name an error once, fix it, move on, no rumination.
- **#12 Loyalty runs both ways** — **earned and revocable on evidence, never tribal.** Structurally:
  authority is the form loyalty takes; a bad outcome from a correct in-rung action is the *rung's*
  failure, not the actor's; and **surface bad news early, because hiding a problem is the breach, not
  the problem.**

Both halves are enforced in `runtime/prompts/_loop-contract.md` §Honest completion, which every loop
reads.

## Where to start reading if you only have an hour

`00_README.md` → `CLAUDE.md` → this file → `processes/autonomy-matrix.md`. That is the shape of the
thing: what exists, how it boots, what keeps it honest, and how control moves off a human onto a
system without being lost.

## Done when

**the consistency check runs clean, and you have added one invariant of your own.**

If you cannot point at that, the step is not finished — do not move on.
