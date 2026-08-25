# Evidence — claims and their checks

> Every claim on the site is bound to a check that runs. Past its ttlDays the value is withheld and what is missing is named in its place. Nothing here falls back to a cached number.

Bound to: Reliability and process only. Volume claims — clients, revenue, hours saved — are refused at generation time, not by review.

Evidence written: 2026-08-13

## Our agents cannot send email.
- State: PROVEN (verified 2026-08-13, valid 45 days)
- Check: deny rule mcp__gmail__send_email
- Source: `runtime/headless-settings.reference.json`
- Why it matters: Drafting and sending are different permissions. Sending is denied at the configuration layer, so it is not a policy an agent can be talked out of.

## Our agents cannot run shell.
- State: PROVEN (verified 2026-08-13, valid 45 days)
- Check: deny rule Bash
- Source: `runtime/headless-settings.reference.json`
- Why it matters: The load-bearing one. An agent that can reach a shell can step around every other control here, so it is denied outright.

## Deny rules that have survived a live attack — UNPROVEN
- State: UNPROVEN. Do not quote a number for this.
- What is missing: none of the 4 deny rules has been attacked yet — the canary-injection drill is defined but has never been armed, so there is no survival to report
- Source that would prove it: `loops/_trust/drills.jsonl`
- Why it matters: A rule nobody has attacked is a claim, not a control. This counts only the ones something has actually tried to break. The rest are listed as untested, on purpose.

## 221 automated checks stop this system from stating what it cannot prove.
- State: PROVEN (verified 2026-08-13, valid 21 days)
- Check: assertions that stop the OS stating what its inputs do not support
- Source: `runtime/test_evidence.py`
- Why it matters: The same discipline this page runs on. If any of them fail, the number here is withheld rather than rounded.

## 43 facts are re-checked across every surface each week.
- State: PROVEN (verified 2026-08-13, valid 21 days)
- Check: cross-surface invariants checked 2026-08-13; 1 drifting
- Source: `runtime/consistency-check.py`
- Why it matters: A number changed in one place and left stale everywhere else is the most common way a company starts lying by accident. A machine checks, not a person.

## 30 scheduled jobs run this company with no human present.
- State: PROVEN (verified 2026-08-13, valid 30 days)
- Check: scheduled jobs that run with no human present
- Source: `runtime/agent-registry.json`
- Why it matters: Not a demo. This is the system we sell, running the business that sells it.

## Last checked 2026-08-13: everything running is on the sanctioned list.
- State: PROVEN (verified 2026-08-13, valid 30 days)
- Check: last diff of what is running against what is sanctioned
- Source: `loops/_governance/`
- Why it matters: A weekly diff of what is actually running against what is approved to run. Unapproved automation is how an AI system quietly becomes something nobody chose.

## Last fault injected 2026-08-07 — caught.
- State: PROVEN (verified 2026-08-13, valid 60 days)
- Check: silent-schema-drift injected and caught
- Source: `loops/_trust/drills.jsonl`
- Why it matters: We break it on purpose, on a schedule, and record whether we noticed. A control with no drill behind it is not evidence of anything.

# Controls

0 of 4 deny rules have a fault-injection drill behind them. The rest read `untested` — a rule nothing has attacked is a claim, not a control.

- `Bash` — UNTESTED — The agents cannot run shell commands. This is the load-bearing one: an agent that can shell can bypass every other control on this page. (canary-injection defined but never armed)
- `mcp__gmail__batch_delete_emails` — UNTESTED — The agents cannot bulk-delete email. (canary-injection defined but never armed)
- `mcp__gmail__delete_email` — UNTESTED — The agents cannot delete email. (canary-injection defined but never armed)
- `mcp__gmail__send_email` — UNTESTED — The agents cannot send email. They draft; a human sends. (canary-injection defined but never armed)
