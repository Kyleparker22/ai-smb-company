# Exit Radar — the platform for the exit-flip lane

**Built 2026-08-17 (the Founder: "a platform that will research and find me SMBs
that people are trying to sell, and we can then prospect them and pitch
AI/yourco").** The platform behind the already-decided lane
`decisions/2026-07-29_exit-flip-targeting-lane.md` — that decision designed
the targeting; this folder is the machine that runs it.

## What it is
A sourcing → triage → pitch-staging engine for SMBs in ownership transition.
An owner listing their business for sale has published a timestamped
"I want out" — the purest owner-drain signal there is. The pitch is
**three-sided** (third side added 2026-08-17,
`decisions/2026-08-17_succession-three-play-map.md`): *don't sell* (the OS
removes the reason you're selling) / *sell for more* (the OS removes the
owner-dependence discounting your multiple) / *hand it off without selling*
(a business that runs without you is one a successor can actually take).
Every conversation has a win condition. Exit planners / succession advisors
are **partner category 10** (`processes/partnerships/target-list.md`) — they
own the legal/financial half of a succession plan; the OS is the operational
half they can't produce. The buy-them-ourselves play is **parked at Holdco**
with named reopen conditions — see the decision.

```
python3 server.py                       # console on :8814
# or by launch name:  yourco-exit-radar
python3 radar.py --board                # CLI triage view
python3 radar.py --export               # staged → sadie-json for the cold pipeline
python3 test_radar.py                   # 36 honesty assertions
```

## The rails (structural, pinned by test)
- **No scraping — there is no fetcher in this codebase.** BizBuySell and
  peers are ToS-gated (Rafi posture; the scraper-family rejection is a
  standing bound). A candidate citing a gated platform is refused unless it
  carries `human_read: true` — the attestation that a PERSON read the page.
- **Never a fake buyer.** Every draft states plainly that yourco is not a
  buyer; the pitch screen refuses buying-interest phrasing outright.
- **Routing by construction:** anonymized listings → **Bird** (partner
  category 9, "send us your unsellable listings") and can NEVER be staged
  for outreach; sold/under-contract → the **ETA lane** (the buyer is the
  prospect; drafts nothing here); only qualified, owner-reachable,
  non-DNC candidates export.
- **The export IS the existing pipeline** — Sadie's hand-off schema →
  `runtime/sourcing.py --sadie-json … --campaign "Exit-flip"` → Reilly
  stages, Michelle's copy, CRM on reply. No parallel rail, no second CRM.
- **The decision's guardrails as refusals:** no "walk away day one" (the
  canonical framing is *"a few hours of approvals, trending toward zero as
  the system earns it"*), no growth promises pre-proof, no numbers about
  their business they didn't publish. DNC is permanent.
- **Nothing sends.** All outbound is OtherVenture-gated; the Founder sends, agents draft.

## How candidates get in (the compliant sourcing stack)
1. **Google Alerts RSS** (the workhorse — set up per
   `runtime/intent-alerts-setup.md`): alerts on "selling the business" /
   "retiring after * years" / "business for sale" + metro names, collected
   by Sadie's `runtime/intent_collect.py`, imported here.
2. **WebSearch sweeps** (Cowork, on demand): public news for
   retirement/succession announcements. Record with the article URL.
3. **A human reading listing sites** — legitimate and expected; record with
   `human_read: true` and the facts the listing itself stated.
4. **Brokers** (the main door per the decision): category-9 partners send
   their owner-dependent inventory; those arrive as `broker` contact-path
   candidates with the broker named.

## First sweep findings (2026-08-17 — market context, no candidates yet)
The store starts EMPTY and is not backfilled — same doctrine as the agentops
stores. What the first compliant sweep established:
- **Discovery routes overwhelmingly to the ToS-gated platforms** (BizBuySell
  et al. dominate every query) — confirming the decision's read that Google
  Alerts RSS + human-read sessions + brokers are the compliant paths, and
  the broker door is the volume door.
- **The market tailwind is sourced and current** (for Michelle's copy and
  Bella's stats, 12–18mo recency rule satisfied): Axios Raleigh 2026-02-24 —
  roughly **half of ST small businesses have an owner 55+, and ~85% of
  those have no succession plan**; millennial/Gen-Z buyers are riding the
  "silver tsunami" into boomer businesses. WRAL 2026-03: Raleigh's
  employee-ownership initiative for retiring owners. Sources:
  https://www.axios.com/local/raleigh/2026/02/24/why-young-north-carolina-entrepreneurs-are-buying-up-boomer-businesses
  https://www.wral.com/business/raleigh-employee-ownership-initiative-march-2026/
- The ETA lane (`decisions/2026-06-16_eta-company-os-offering.md`) is the
  same seam's other side — the Axios piece is evidence the buyer side is
  real and growing.

## Next steps (each needs the Founder's go, in rough order of value)
1. **Google Alerts feeds** for exit phrases × target metros → the daily
   collector picks them up (5 minutes of setup, the recurring supply line).
2. **Bird's category-9 broker list** — the decision named brokers the main
   door; Exit Radar gives Bird the "what we do with your dead inventory"
   story and the intro draft.
3. **Runtime loop** (add-runtime-loop skill) — a weekly Sadie sweep that
   collects exit signals into an import file for triage here. Registry-gated.
4. At launch (OtherVenture): first staged export → the exit-flip Instantly
   campaign.

## Ownership
Sadie sources (this folder lives in her workspace) · the Founder triages/qualifies ·
Michelle owns the campaign copy the drafts feed · Bird works the broker
bucket · Reilly stages the export · David's CRM receives on reply.
