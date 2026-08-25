# Service Level Agreement — DRAFT TEMPLATE

> ⚠️ **Draft. Not legal advice. NOT YET COUNSEL-REVIEWED (Ray).** Added 2026-08-24 at the Founder's direction.
> Attaches to the **Engagement Agreement** and is incorporated by reference; where they conflict, the
> Agreement controls except on the subjects below. Fill every `[[ ]]`. Targets are a **proposal until
> the Founder locks them** — the same posture as pricing.
>
> 🔴 **DO NOT SEND THIS TO A CLIENT YET.** §7 lists what must exist first. The short version: yourco
> currently has **no uptime monitoring** — no health check, no heartbeat, no alerting anywhere in
> `runtime/`. An availability commitment that nobody measures is the exact failure the SOW's acceptance
> rule forbids: *if we cannot measure it, it does not go in the table.* Offering it before §7 is done
> would mean promising a number and then asking the client to take our word for it.

**This SLA** applies to **"[[EMPLOYEE NAME]]"** operated for **[[CLIENT LEGAL NAME]]** under the
Engagement Agreement dated **[[DATE]]**.

---

## 1. What is being measured

**"The Service"** means the parts of the employee that **yourco controls and operates**: the
orchestration, the workflows, the integrations yourco built, and yourco's own infrastructure.

**"Available"** means the Service accepts and processes work as configured. **"Downtime"** is any full
minute in which it does not, measured from yourco's own logs (§6), excluding §5.

Availability is measured **per calendar month**, as:

> `Available minutes ÷ (Total minutes in the month − Excluded minutes) × 100`

## 2. Availability target

| Target | Monthly downtime it allows |
|---|---|
| **[[99.5%]]** of each calendar month | ~3 hours 39 minutes |

*Why this number and not 99.9%.* [[the Founder locks — but read this before raising it.]] 99.9% allows 43
minutes a month and is only meetable with redundancy and someone on call. yourco today is a single
operator on a single host with no automatic failover, so **99.9% would be a number we intend rather
than a number we can hold**, and the first bad month would be a broken contract instead of a bad week.
99.5% is the honest ceiling until §7.3 (failover) exists. Raise it when the architecture earns it, not
when a prospect asks.

## 3. Response times

Severity is set by **impact on the client's business**, not by how hard it is to fix. yourco assigns it
on first response and will raise it on the client's reasonable request.

| Severity | What it means | yourco responds within | Then |
|---|---|---|---|
| **P1 — Down or harmful** | The employee is not working, or it is producing output that reaches customers and should not | **[[1 business hour]]** | Continuous effort during business hours until mitigated; status to the client's named contact at least every **[[2]] hours** |
| **P2 — Degraded** | Working, but materially worse — slow, partial, or a workaround is needed | **[[4 business hours]]** | Fix or a stated plan within **[[2 business days]]** |
| **P3 — Question or request** | A question, a small change, a report | **[[1 business day]]** | Handled in the normal weekly cycle |

**Business hours** are **[[Monday–Friday, 9:00–18:00 ET]]**, excluding US federal holidays. "Responds"
means a human being at yourco has acknowledged and started work — **not** an automated receipt.

**Outside business hours.** yourco does not staff an overnight rotation and will not pretend to. Two
things are true instead, and both are worth more than a promise nobody can keep:
- The client holds a **kill switch** (Agreement §8 · `processes/autonomy-matrix.md`) and can stop the
  employee themselves, immediately, without waiting for yourco.
- Anything customer-facing that the client has gated **cannot go out unapproved** in the first place —
  so the overnight failure mode is *nothing happens*, not *the wrong thing happens*.

P1s raised outside business hours are answered **best-effort**, and the clock in the table starts at the
next business hour. [[the Founder: if a client needs genuine 24/7, that is a different engagement with a
different price — do not promise it here.]]

## 4. Service credits

If yourco misses a target, the client may claim a credit against the **following** month's retainer.

| Miss | Credit |
|---|---|
| Availability below target | **[[10%]]** of that month's retainer per full 1% below, up to **[[50%]]** |
| P1 response missed | **[[5%]]** of that month's retainer per occurrence, up to **[[25%]]** |
| P2 response missed | **[[2%]]** of that month's retainer per occurrence, up to **[[10%]]** |

- **Combined cap: [[50%]] of that month's retainer.**
- Credits are the client's **sole financial remedy** for missed service levels, and are claimed in
  writing within **[[30]] days** of the monthly report.
- **The teeth that matter more than the credit:** if yourco misses the availability target in
  **[[three consecutive months]]**, or misses a P1 response **[[three times in any rolling quarter]]**,
  the client may terminate **for cause immediately**, without the cure period in Agreement §3, and
  without liability for the notice period. A credit is compensation; this is the exit. Both exist
  because a discount on a service that does not work is not a remedy.

## 5. What is excluded

Downtime does **not** count against the target where it is caused by:
- **Third-party services** yourco does not control — model providers, telephony/voice, the client's own
  CRM, calendar or systems, and any client-procured service. yourco will still **notify, mitigate where
  it can, and report the cause**; it simply cannot warrant somebody else's uptime.
- **The client** — revoked or changed access, credentials, plan downgrades, or changes to the client's
  own systems made without notice.
- **Scheduled maintenance**, with at least **[[48 hours]]** notice, capped at **[[4 hours]]** per month
  and scheduled outside the client's business hours where practicable.
- **Emergency maintenance** to address a security or safety risk — notified as soon as practicable.
- **Force majeure** (Agreement §16).
- Any period the client has **paused the employee** or used the kill switch.

⚠️ **The exclusion that will get argued about.** Most of a client's felt outage will be a third-party
outage — a model provider degrading, a phone network dropping. Say this in the sale, not in a dispute:
yourco commits to *its own* layer, and to telling the truth about the rest. If a client needs a
warranty covering the whole chain, no honest operator can sell them one.

## 6. Measurement and reporting

- yourco reports **availability and response performance monthly**, from the system's own records, in
  the monthly report. Not from recollection.
- The client may ask for the underlying log for any month.
- **If yourco cannot measure a month, yourco says so — and the target is treated as missed.** A month
  yourco failed to instrument is not a month yourco gets the benefit of the doubt on. This inverts the
  usual arrangement deliberately: the party holding the logs carries the burden of proving the number.

## 7. 🔴 Preconditions — what must exist before this SLA is offered to anyone

None of §2 or §3 is measurable today. Before this document goes into a proposal:

1. **Uptime monitoring + alerting on the client's employee** — an external health check, a heartbeat,
   and a page/alert to the Founder on failure. **Half closed 2026-08-25: the mechanism now exists, its
   subject does not.** `runtime/heartbeat.sh` + `yourco-heartbeat.timer` write one beat every 15
   minutes to `loops/_health/heartbeat.jsonl`, and `dashboard/uptime.py` computes availability as
   *beats received ÷ beats expected* — so a missing line is the outage rather than a hole in the
   record. It is pure shell with no model call, so it survives the dead-credit failure that took the
   runtime down twice. **Two things still block this precondition:** (a) the timer is a **host**
   install and is not yet enabled on the VPS, and (b) what exists measures **yourco's own runtime**,
   not a client deployment — there is no client OS to watch. The alerting half is also unbuilt;
   `runtime/runtime-alarm.sh` pages on a *failed run*, which is a different event from an outage.
   **Until a client deployment is instrumented, the availability clock for a client is unmeasured,
   and under §6 that reads as a miss every month.**
2. **A logged incident record** — severity, first response, mitigation, resolution — so P1/P2 response
   times are computed rather than remembered. No incident process document exists yet.
3. **Decide the failover posture** before raising §2 above 99.5%. Single host, no failover, one operator.
4. **A named contact and channel** on both sides, in the SOW, so "responded" has an address.

*Owners:* Kemba (monitoring + alerting) · Kolby (the incident record — it is eval/observability work) ·
Ray (this document) · the Founder (locks the numbers and the failover call).

---

> **Honesty footer.** Targets here are a proposal until the Founder locks them. yourco commits to the layer it
> operates and reports honestly on the layer it does not. Nothing in this SLA is a guarantee of business
> outcomes — those live in the SOW's acceptance criteria, which measure whether the employee did its
> job, not whether it was switched on.
