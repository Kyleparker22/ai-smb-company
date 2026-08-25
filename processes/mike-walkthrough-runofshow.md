# Mike walkthrough — run of show

> For the Founder, 2026-08-17. ~35 minutes. Companion to the explainer page
> (artifact `3717ff77-1511-4848-a83a-2b013c2a104d`). Mike is a 15% member who has never been walked
> through the company; his lane is the open item in the OA.

## Before he arrives (5 min)

```bash
cd "/Users/you/Documents/Claude/Projects/YourCo LLC - AI" && ./show.sh
```

Then confirm all three actually answer — **do not trust that they're up**, they were down earlier today:

```bash
for p in 8790 8791 8807; do printf "%s " $p; curl -s -o /dev/null -w "%{http_code}\n" http://localhost:$p/; done
```

`200 · 200 · 303` is correct (the console redirects to its login). Open tabs in this order:
explainer page → HQ (8791) → CRM (8790) → Connector Console (8807).

Close Slack and mail. Notifications off.

## The arc (~35 min)

| | Show | Say |
|---|---|---|
| **1. The business** (5) | Explainer page, top | Audit first, then we build and *operate* the system. We're an operator, not a vendor — the client never touches a token. Then land the honest half immediately: **zero audits delivered, one unsigned proposal.** |
| **2. Why it's defensible** (4) | Explainer, "moat" section | Anyone can wire a workflow; almost nobody can *prove* it worked to the owner. We charge for the proof. Say the caveat yourself: it's a design running on our own operation, unproven on paying clients. |
| **3. The numbers** (6) | Explainer figures → workbook if he pushes | Target case, then go straight to the downside: three salaries from month 1 against $0 in the bank, Conservative breaches by $11,155, the second $50k is what makes it solvent. **Don't let him find that himself.** |
| **4. The machine** (8) | **HQ (8791)** — Overview → Board → Evidence → Partners | The Board is every open item in the company. Evidence is the door that asks what the system can prove about itself. Partners is the three-way split and the OA's open questions — including his. Then: **it was switched off for 12 days and the watchdog slept for five weeks.** |
| **5. The CRM** (5) | **CRM (8790)** — pipeline, then an insight read | 21 deals, $24k, 18 never contacted. Show one insight read — ghost or spread — because that's the thing a normal CRM can't do and it's product IP we dogfood. |
| **6. The growth engine** (4) | **Connector Console (8807)** | People refer, earn a rising share, and can recruit other connectors. Then: zero connectors, counsel-gated, and the packet marketing it is already in use. |
| **7. His lane** (5) | Explainer, last section | The OA blank is what *his* contribution is. Nobody can fill it but him. End on that question, not on the tour. |

## Three things to say out loud, unprompted

1. **"Nothing is signed and no lawyer has read any of it."** Thirteen legal gates open, no counsel engaged,
   and there's no NDA with him either. He will find this; say it first.
2. **"The launch gate has never been defined."** Its resolution condition is a blank field in our own
   tracker. It's the biggest unforced problem in the company and it's ours, not the market's.
3. **"The constraint isn't the product."** Every review this week landed in the same place: the apparatus
   is built to an unusual standard and nobody has asked anyone to buy anything.

## What not to do

- **Don't lead with the 27 agents.** The machine is the most impressive thing here and the least
  relevant to whether the business works. Product → market → machine, same order that worked for Partner B.
- **Don't demo anything that needs the runtime to be live.** It resumed yesterday and Monday's loops are
  the first real test — if they haven't fired by the meeting, say so rather than explaining it away.
- **Don't quote the $50k as the cost of getting to profitable.** It's a loan, it's junior to
  distributions, and the Conservative case needs more than it.

## If he asks the four hard questions

- *"Why has nobody bought it?"* — Nobody has been asked. A yes couldn't be invoiced today either; Stripe
  is specified and untested.
- *"What do I have to put in?"* — Cash: nothing. the Founder funds it alone. Time and a defined lane: that's the
  actual ask, and it's undefined on purpose until he defines it.
- *"What's my 15% worth?"* — On the model, a three-year total near $1.05M in the Target case. On the
  evidence, a share of a company with $0 revenue. Both are true; give him both.
- *"Is this real or is it a very good deck?"* — Open the CRM and the runtime logs. The honest answer is
  that the software is real and the business hasn't started.
