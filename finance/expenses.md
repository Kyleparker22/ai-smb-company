# expenses.md

Month-by-month expense log. Categories: `model_spend`, `tooling`, `professional_services`, `marketing`, `ops`, `other`.
See `/finance/README.md` for conventions.

## ⚠ OPEN — reconcile the pre-formation build spend against receipts

**Owner: Charles · Raised 2026-08-10 (the Founder) · Blocks: papering the founder loan**

The financial model now carries **~$3,000 of pre-formation build spend as part of a repayable founder
loan to the Founder** (`Assumptions!B141`, total repayable $53,000 — `decisions/2026-08-10_cash-structure-and-model-recalibration.md`).
**That $3,000 is the Founder's estimate, not a receipted figure**, and it is the one number in the loan block a
lawyer will ask for evidence of. Until it is reconciled, the Founder is scheduled to be repaid an amount nobody
in this workspace can defend from documents.

What exists today, and what doesn't:

| | |
|---|---|
| Receipted | June cash out **$405.73** (`readouts/2026-06.md`) |
| Inferred, not receipted | ~$614.22/mo of fixed subscriptions since June — the line items are known, the actual charges are not all matched to receipts |
| **Unknown** | **Anthropic API top-ups** — logged `TBD` in the 2026-06 row below; prepaid balance, no email receipt. Historically the largest single unknown in this ledger |
| Also unmatched | the June Instantly anomaly ($316 charged vs $97 logged — see the 2026-06 row) |

**To close it:** pull the card/bank statements for May–August 2026, match every charge to a row here,
supply the Anthropic top-up amounts, then set `Assumptions!B141` to the reconciled total, recalculate,
and re-sync. If the reconciled figure differs materially from $3,000, the change sweeps to
`06_business-plan.md`, `finance/model-assumptions.md` and the decision entry in the same commit.

---

| month | vendor | category | description | amount | date | status |
|-------|--------|----------|-------------|--------|------|--------|
| 2026-05 | Apollo.io (ZenLeads Inc.) | tooling | Professional monthly plan — receipt #2506-0100 | $50.00 | 2026-05-10 | **cancelled — plan ended 2026-06-06; no further charges** |
| 2026-06 | Google Workspace | tooling | Business Starter — invoice #5580728454 | $8.73 | 2026-06-07 | paid (card decline Jun 1 resolved Jun 7) |
| 2026-06 | Instantly | tooling | Hyper CRM tier — SMS + sourcing + cold email infra (`getteamyourco.com`) | $97.00 | 2026-06-08 | recurring monthly |
| 2026-06 | Canva | tooling | Canva Pro + Sites — Reed's animation stack + Webb's site hosting + brand kit | $18.00 | 2026-06-08 | recurring monthly (reconciled $15→$18 at June close; invoice 04914-1698354, Jun 16) |
| 2026-06 | Plausible | tooling | Hobby tier — analytics for `getteamyourco.com` | $9.00 | 2026-06-09 | recurring monthly (script install pending Webb) |
| 2026-06 | Calendly | tooling | Booking link `calendly.com/the Founder-yourco/30min` — tier TBD (free or Standard $10/mo) | TBD | 2026-06-09 | active — confirm tier |
| 2026-06 | Outscraper | tooling | Google Maps sourcing — $10 deposit added | $10.00 | 2026-06-09 | active (pay-as-you-go) |
| 2026-06 | Vibe Prospecting (Explorium) | tooling | Lead sourcing + enrichment — credit-based; 150 credits used on landscaping batch 1 | TBD — confirm credit plan/tier | 2026-06-09 | active (usage) |
| 2026-06 | Higgsfield | tooling | AI video generation — Reed demos; Plus plan + credits (~135 credits used 2026-06-09) | TBD — confirm Plus plan $/mo | 2026-06-09 | active (usage) |
| 2026-06 | Descript | tooling | AI video editing + voiceover — Reed assembly (VO + stitch); plan + AI credits | TBD — confirm tier | 2026-06-09 | active (usage) |
| 2026-06 | Custom SaaS Data | tooling | Data/enrichment — $10 via PayPal | $10.00 | 2026-06-09 | confirm — one-time or recurring |
| 2026-06 | Hostinger | tooling | VPS (KVM 2, Ubuntu) — always-on runtime host for the Claude Code agent OS | $24.59/mo ($13.99 first mo) | 2026-06-09 | recurring, month-to-month — consider 12–24mo term → ~$15/mo |
| 2026-06 | Eleven Labs | tooling | ElevenLabs Starter — Reed voice stack; receipt #2187-5473-2435, billing Jun 9–Jul 9, card ••2296 | $6.00 | 2026-06-09 | recurring monthly (logged at June close) |
| 2026-06 | Twilio | tooling | Account funding deposit — voice/SMS (ties to Instantly 10DLC); card ••2296 | $20.00 | 2026-06-17 | usage-based deposit (logged at June close) |
| 2026-06 | Anthropic | model_spend | Claude API credit top-up — the model spend the business model runs on; balance hit $0 Jun 16–18 (silent runtime death), topped up Jun 18 | TBD — the Founder to supply top-up $ + auto-reload threshold | 2026-06-18 | active — **amount unsupplied; no email receipt (prepaid balance)**; largest go-forward burn unknown |
| 2026-06 | Tailscale | tooling | Standard – Self Serve — VPS runtime network access; receipt #2289-5403, billing Jun 25–Jul 25, card ••2296 | $8.00 | 2026-06-25 | recurring monthly (trial auto-converted Jun 25; logged at June close) |
| 2026-06 | Instantly | tooling | **Actual Jun 8 charge = $316** (2× Hypergrowth $97 + Hyper CRM $97 + $25 setup, receipt #2709-9750) vs the single $97 line above | see note | 2026-06-08 | ⚠ **anomaly — needs the Founder's audit**: cancel duplicates (~$194/mo recoverable) or confirm all 3 subs intentional, then reconcile |
| 2026-07 | Instantly | tooling | Hypergrowth Plan — receipt #2072-9349, Jul 8–Aug 8, card ••2296 | $97.00 | 2026-07-08 | paid |
| 2026-07 | Instantly | tooling | Hypergrowth Plan (2nd) — receipt #2771-3082, Jul 8–Aug 8, card ••2296 | $97.00 | 2026-07-08 | paid — ⚠ **DUPLICATE of the row above (two identical Hypergrowth Plans); cancel → ~$97/mo recoverable** |
| 2026-07 | Instantly | tooling | Hyper CRM — receipt #2841-2087, Jul 8–Aug 8, card ••2296 | $97.00 | 2026-07-08 | paid |
| 2026-07 | Granola | tooling | Granola **Business** — receipt #2093-2483, Jul 8–Aug 8 (Link) | $14.00 | 2026-07-08 | paid — ⚠ **contradicts the 2026-06-09 "staying free, no charge expected" note; confirm intentional or downgrade to free** |
| 2026-07 | Eleven Labs | tooling | Starter (Reed voice stack) — receipt #2076-1920-0686, Jul 9–Aug 9, card ••2296 | $6.00 | 2026-07-09 | paid (recurring monthly) |
| 2026-07 | Hostinger | tooling | KVM 2 VPS renewal (the always-on runtime host) — **PAYMENT FAILED "insufficient balance," Jul 9** | $24.49 | 2026-07-09 | ⚠ **UNPAID — failed payment; VPS suspension = whole-OS-dark risk. Renew immediately.** |
| 2026-07 | Descript | tooling | AI video editing (Reed assembly) — tier now **confirmed $35/mo** (was TBD); **PAYMENT FAILING, card ••2296, 3 attempts Jul 10–12** | $35.00 | 2026-07-10 | ⚠ **UNPAID — card declining; decide fix-card-and-keep or cancel** (no new Descript emails as of 07-27 pulse — resolution unknown) |
| 2026-07 | Hostinger | tooling | KVM 2 VPS renewal — **2nd FAILED attempt Jul 20 ("balance was insufficient")**; first failure was Jul 9. Still unpaid as of 07-27 pulse — 18 days | $24.49 | 2026-07-20 | ⚠ **STILL UNPAID — 2 failures; VPS suspension = whole-OS-dark risk. Renew immediately.** |
| 2026-07 | Tailscale | tooling | Standard – Self Serve (VPS runtime network) — receipt #2735-2648, Jul 25–Aug 25 | $8.00 | 2026-07-25 | paid (recurring monthly) |
| 2026-07 | Canva | tooling | Canva Pro — invoice 04944-0807325, card ••2296; **failed Jul 21 + Jul 24 ("insufficient funds") before clearing Jul 26** | $18.00 | 2026-07-26 | paid (after 2 failed attempts) |
| 2026-07 | Anthropic | model_spend | **Claude Max plan – 20x** — receipt #2700-4256-4000, Jul 27–Aug 27, paid via Link. **NEW recurring line, never previously logged.** This is the subscription that powers Cowork/desktop sessions (the API metering in `token_spend.md` does NOT cover it) — so it is real yourco compute cost, and it is the single largest fixed line in the book. | $200.00 | 2026-07-27 | paid (recurring monthly) |
| 2026-07/08 | Anthropic | model_spend | **API org credit balance hit $0 → Claude API access DISABLED for org "YourCo."** Two notices: Jul 30 + Aug 1. No top-up receipt since. Runtime loops corroborate (no artifacts after Jul 28). | $0 (no top-up) | 2026-07-30 | ⚠ **RUNTIME DARK — top up + enable auto-reload** |
| 2026-08 | Granola | tooling | Granola Business — receipt #2011-3092, Aug 8–Sep 8, paid via Link | $14.00 | 2026-08-08 | paid (recurring monthly — still Business tier; **not downgraded to free** despite the 06-09 "staying free" note) |
| 2026-08 | Eleven Labs | tooling | Starter (Reed voice stack) — receipt #2643-9600-5666, Aug 9–Sep 9, card ••2296 | $6.00 | 2026-08-09 | paid (recurring monthly) |
| 2026-08 | Canva | tooling | Canva Pro — invoice 04975-0768908, card ••2296 | $18.00 | 2026-08-16 | paid — **cleared on first attempt** (vs 2 failed attempts in July; card ••2296 appears funded again) |

## Notes
- **Google Workspace:** Mastercard •••9281 declined Jun 1 ("insufficient funds"); payment of **$8.73** received Jun 7, 2026 (confirmed via Google payment receipt). Invoice #5580728454 now closed/paid.
- **Apollo:** Professional monthly plan was **cancelled** — confirmation email states the plan ended **June 6, 2026**. Last charge was $50.00 on May 10. Treat Apollo as a discontinued tool, not a recurring expense. If outbound restarts and Apollo is reactivated, add a new row.
- **HighLevel (GoHighLevel):** $297/mo agency subscription cancelled Jun 7, 2026 — never logged in this ledger for the months it was active. Backfill pending the Founder's supply of charge history (months + card). Charles flagged this in the 2026-06-08 finance pulse.
- **Plausible:** account provisioned 2026-06-09 — tracking script saved, awaiting Webb to install on the existing live site.
- **Calendly:** URL `calendly.com/the Founder-yourco/30min` is the 30-min discovery call event Reilly's CTAs point to. Tier (free vs Standard $10/mo) TBD — the Founder to confirm so the recurring cost is accurate.
- **Granola:** the Founder confirmed 2026-06-09 staying on the **free version** when the 30-day trial converts ~Jul 7. No charge expected. Atlas/Charles can stop flagging.
- **HighLevel backfill:** the Founder indicated 2026-06-09 he's not supplying historical charge data right now ("that should be it"). Backfill remains an open Charles item — flagged in finance pulses until resolved, but no further chase by agents until the Founder voluntarily supplies the data.
- **New tools added 2026-06-09 (Reed video + Reilly sourcing stack):** Vibe Prospecting, Higgsfield, Descript (all credit/usage-based), Outscraper ($10 deposit), Custom SaaS Data ($10). **Amounts/tiers are TBD — the Founder to confirm the plan $/mo for Vibe, Higgsfield, Descript** so go-forward burn is accurate. These are the new off-books risk to watch (same pattern as HighLevel).
- **Trial watch items (not yet charges):** Loom Business + AI trial (started ~06-08, converts ~06-22 — decide before then) and a Slack Pro trial. Cancel or convert deliberately; don't let either auto-charge.

## Recurring monthly costs (active — reconciled at June close; July charges confirmed 2026-07-13 pulse)
- **Google Workspace Business Starter:** $8.73/mo (single seat; agent aliases ride free on this seat)
- **Instantly:** **$291/mo CONFIRMED** — July receipts prove 3 live subscriptions (2× Hypergrowth $97 [#2072-9349, #2771-3082] + Hyper CRM $97 [#2841-2087], all Jul 8). The two Hypergrowth Plans are duplicates → **~$97/mo recoverable** on cancel (more if only one sub is truly needed).
- **Canva Pro:** $18/mo (reconciled from $15; Reed + Webb + brand kit)
- **Plausible Hobby:** $9/mo (analytics)
- **ElevenLabs Starter:** $6/mo (Reed voice stack; Jul 9 charge confirmed #2076-1920-0686)
- **Tailscale Standard:** $8/mo (VPS runtime network access; trial converted Jun 25)
- **Hostinger KVM 2 (VPS runtime host):** **$24.49/mo — FAILED TWICE (Jul 9 + Jul 20, "insufficient balance"); still UNPAID as of Jul 27 → runtime suspension risk**
- **Descript:** **$35/mo tier now confirmed** (was TBD) — but **payment FAILING (card ••2296) Jul 10–12; UNPAID**
- **Granola Business:** **$14/mo — NEW/unexpected** (Jul 8 charge; contradicts the 2026-06-09 "staying free" note)
- **Anthropic Claude Max – 20x:** **$200.00/mo — NEW, first receipt seen 2026-07-27** (#2700-4256-4000, Jul 27–Aug 27). Powers Cowork/desktop sessions; **not** captured by the API metering in `token_spend.md`. Largest single fixed line in the book.
- **Calendly:** TBD ($0–$10/mo)
- **Outscraper:** $0/mo at idle (pay-as-you-go on actual sourcing)
- **Fixed subtotal, all confirmed active subs (incl. the paid-if-fixed Hostinger + Descript, excl. Calendly TBD):** **~$614.22/mo** = Google $8.73 + Instantly $291 + Canva $18 + Plausible $9 + ElevenLabs $6 + Tailscale $8 + Hostinger $24.49 + Descript $35 + Granola $14 + **Anthropic Max $200**. **Drops to ~$517/mo if the duplicate Instantly Hypergrowth is cancelled**, ~$503/mo if Granola also downgrades to free. *(Was published as ~$414/mo through the 07-27 pulse — that figure was understated by ~48% because the Max subscription was off-book.)*
- **Plus per-engagement variable:** Anthropic model/token spend (metered ~$83/mo / $82.80 trailing-30d as of Jul 6 — see `token_spend.md`); Twilio/Outscraper usage; Vibe/Higgsfield credits (TBD).

## Running totals
- **Expenses (2026-06), confirmed receipt-sourced:** **$405.73** = Google $8.73 + Instantly $316 (actual) + Canva $18 + Plausible $9 + ElevenLabs $6 + Tailscale $8 + Outscraper $10 + Custom SaaS Data $10 + Twilio $20. (Excludes Anthropic top-up [amount TBD], Calendly TBD, Vibe/Higgsfield tiers TBD, HighLevel backfill.)
- **Expenses (2026-07), receipt-confirmed to date (as of 08-03 pulse):** **$537.00 paid** = Instantly $291 (3× $97) + **Anthropic Max $200 (Jul 27, #2700-4256-4000)** + Granola $14 + ElevenLabs $6 + Tailscale $8 (Jul 25, #2735-2648) + Canva $18 (Jul 26, after 2 failed attempts). **Plus $59.49 attempted-but-UNPAID** (Hostinger $24.49 — failed Jul 9 AND Jul 20, no payment-confirmation email ever received; Descript $35 — failing Jul 10–12, no resolution email since). Excludes Anthropic *API* spend (metering stale at Jul 22: $129.28 trailing-30d — and now $0/day because the org credit balance is exhausted), Plausible/Google July lines (not yet seen), Calendly TBD, usage tools.
- **Expenses (2026-08), receipt-confirmed to date (as of 08-17 pulse):** **$38.00 paid** = Granola $14 (Aug 8, #2011-3092) + ElevenLabs $6 (Aug 9, #2643-9600-5666) + Canva $18 (Aug 16, inv 04975-0768908, cleared first attempt). **Partial month** — the larger recurring lines are not yet receipt-seen for August: Anthropic Max $200 (next ~Aug 27), Instantly $291 (Aug 8 charge not yet in inbox — cancellation of the duplicate remains unconfirmed), Hostinger $24.49, Google, Tailscale, Plausible. Excludes Anthropic API/token spend (runtime resumed 08-16; a $4.42 metered watchdog run booked in `token_spend.md`; fresh trailing-30d pull needed now the feed is live again).
- Expenses (2026-05, logged): $50.00 (Apollo, cancelled — ended Jun 6, not a June cost)
- Expenses YTD (2026): **≥ $1,030.73 logged to date** ($50 May + $405.73 Jun + $537 Jul paid + $38 Aug partial; real number higher pending Anthropic API spend + unpaid/failed charges + TBD tiers + HighLevel backfill)
