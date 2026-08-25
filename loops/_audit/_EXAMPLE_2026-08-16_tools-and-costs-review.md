> ⚠️ **EXAMPLE OUTPUT — not yours.** This is one run of this loop from the company this
> template was extracted from, kept so you can see the shape of what the loop produces.
> The dates, numbers, and findings describe **someone else's business**. Delete this file
> the first time your own loop writes a real one.

# Software, tools, expenses and costs — the review before the lock

> Built 2026-08-16 for the Partner B walkthrough. Reviewed Wed 8/19, **locked Thu 8/20**. Read from
> `finance/expenses.md`, `token_spend.md`, the connector state and the live loop artifacts.

## The stack and what each thing is actually doing

| Tool | $/mo | Evidence of use | Verdict |
|---|---|---|---|
| **Anthropic Max 20x** | 200.00 | the Founder's daily driver; every Cowork session | **Essential** |
| **Instantly** (3 subs) | 291.00 | warmup **0/2**, campaign `accounts-unhealthy`, gated from sending | **Cut to one seat** |
| **Hostinger VPS** | 24.49 | the runtime; its lapse caused a 5-day outage | **Essential — auto-renew** |
| **Descript** | 35.00 | video production paused; already failing to bill | **Cut** |
| **Canva** | 18.00 | brand kit, end-frames; paid Aug 16 | Keep |
| **Granola** | 14.00 | still **Business** tier despite a 06-09 "staying free" note | **Downgrade to free** |
| **Plausible** | 9.00 | **script never installed on the site** | Cut *or* install |
| **Google Workspace** | 8.73 | mail — but Microsoft migration decided 08-09 | Pending migration |
| **Tailscale** | 8.00 | private access to the VPS; free tier covers 6 users | Likely **free tier** |
| **ElevenLabs** | 6.00 | Reed voice stack; production paused | Cut with Descript |
| **Calendly** | **TBD** | tier unresolved since **2026-06-09** | Resolve |
| | **614.22** | | **→ ~$356/mo floor** |

**~$258/mo of cuts have been identified and none executed.** The burn triage was written 2026-08-05 —
eleven days ago — and the August ledger shows Granola still on Business, the Instantly duplicate
"unconfirmed," and Plausible still billing for a script that was never installed. This is the single
cleanest finding in the domain: **the analysis was done, the decision was made, and nobody cancelled
anything.**

## Costs beyond the subscriptions

- **API / token spend** — auto-recharge is now **ENABLED** (receipt-confirmed). $35.70 purchased,
  ~$10.23 August-to-date. That closes the failure that killed the runtime twice.
- **Per-run cost is now measured for the first time**: the 08-16 watchdog run booked **$4.42**
  (40 turns, 6m31s, 2.1M cache reads). One data point, and watchdog is likely among the heaviest —
  but it is the first real number the OS has ever had about its own economics.
- ⚠️ **Two meters disagree.** The Admin cost API and the run journal "do not yet agree on coverage"
  (`token_spend.md`). Until they reconcile, no cost-per-client figure is defensible — which matters,
  because the financial model assumes **$300/client/month** absorbed cost and nothing has yet
  measured against it.
- **Untracked credits**: Higgsfield and Vibe are both logged as TBD. Neither appears in the fixed
  subtotal.

## The process for deciding on tools — and it is good

`.claude/skills/tool-triage/` is the standing procedure, and it is better than most companies manage:
check prior art in `decisions/` first · positively identify the thing (a past mis-identification is
cited as the reason) · **verify against the repo/docs, never the marketing** · route content-shaped
inputs by naming the one transferable mechanism · and log the verdict without being asked.

The record backs it up — ten tool decisions on file, including **stances** rather than just picks:
no-code tooling, no-n8n, paid-ads deferred, and a reversal (`Higgsfield not OpenMontage`) written up
when the first pick underdelivered. Deciding *not* to adopt things, in writing, is the rarer discipline.

**The gap is not the decision process. It is that nothing carries a decision through to the invoice.**
Triage decides, `expenses.md` records, and no step in between cancels a subscription or checks that a
paid tool was installed. Plausible has been billing for months for a script that was never added to a
page; Granola has been on the wrong tier since June.

## What to reconsider, cut, and add

**Cut now (~$258/mo):**
1. **Instantly → one seat.** $194/mo recoverable. It cannot send today and is gated even when it can.
   Keeping one preserves the domain and staged campaigns.
2. **Descript ($35)** — video production is paused and the card is already failing.
3. **ElevenLabs ($6)** — same stack, same reason.
4. **Granola → free ($14).**
5. **Plausible ($9)** — *decide*: install the script this week or cancel. Paying for uninstalled
   analytics is the purest waste on the list.

**Reconsider:**
6. **Tailscale → free tier.** Personal covers 6 users; yourco has 3. Verify the current plan is not
   already free before assuming a saving.
7. **Google Workspace** — the Microsoft migration was decided 08-09 and hasn't happened. Running both
   during the transition doubles the line; running neither properly is why `contact@yourco.example.com`
   still doesn't exist and is blocking his setup.
8. **Calendly** — unresolved for **68 days**. It is either free or ~$10/mo and nobody knows which.
9. **A second Claude subscription for Partner B** (~$20–200/mo depending on tier) is the one *addition*
   already committed. Pro is the floor; he does not need Max 20x.

**Add — and only these:**
10. **An off-box dead-man's-switch.** The runtime was paused 12 days and the watchdog blind 5 weeks
    with nothing outside the box noticing. A ~$0–5/mo uptime pinger is the cheapest control in this
    review and directly prevents the most expensive failure the company has had.
11. **Auto-renew on Hostinger.** The lapse cost 5 days of runtime. Auto-recharge on Anthropic is done;
    this is its twin and isn't confirmed.

**Do not add anything else.** The stack is not missing capability — it is missing execution on
decisions already made.

## What to decide at the lock

1. **Execute the 08-05 triage.** It is eleven days old and worth ~$258/mo against a company with $0
   revenue and a Conservative case that already breaches its $50k injection by $3,900. Cutting this
   changes the model's trough materially.
2. **Give cancellation an owner and a date.** Charles books the ledger; nobody executes. A decision to
   cut that survives eleven days without execution is not a decision, it is a note.
3. **Reconcile the two cost meters** before any cost-per-client claim is made externally.
4. **Resolve Calendly and Google/Microsoft** — both are small money and both are blocking something
   larger (booking flow; Partner B's mailbox and every connector behind it).

## The honest sentence for Partner B

The tool-selection *process* is genuinely disciplined — ten written decisions including four
deliberate refusals and one documented reversal. What has no process at all is the other end:
**nothing turns a decision into a cancelled subscription.** ~$258/mo of agreed cuts sat unexecuted for
eleven days, and the company is paying $9/mo for analytics that were never installed on a site that
was never published. Fixing that is not a tooling problem, it is a five-minute admin habit with an
owner attached.
