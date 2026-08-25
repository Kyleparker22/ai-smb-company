# 07 — CRM, HQ, and the app

> **Build step 07.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

Three surfaces, all internal, all reading what the loops write. Start them with `./show.sh`.


## Turning them on

Everything here is **stdlib-only and runs cold** — no install, no credentials, no build step.

```bash
./show.sh          # starts all five surfaces and opens the app's sign-in
```

`show.sh` reads ports from `.claude/launch.json`, which is the single registry of every local server.
**Never guess a port** — a moved port with a hardcoded caller is the failure that looks like "the
server is broken."

To run one on its own, the port comes from a `PORT` env var, not a flag:

```bash
PORT=8790 python3 crm/server.py          # then open http://127.0.0.1:8790
PORT=8791 python3 dashboard/server.py
```

⚠️ **Keep these bound to `127.0.0.1`.** The CRM and dashboard have **no authentication of their own** —
an unauthenticated GET to the CRM's API returns everything in it. The app gateway (`app/`) is the only
piece meant to face outward, and it prints a warning if you bind it anywhere else. That is a deliberate
single point of failure, not an oversight.

**Verified on a cold clone:** CRM and HQ both return HTTP 200 with an empty `crm/data.json`.

## The CRM (`crm/`, David owns it)

Companies, contacts, deals, activity. The ordinary half is ordinary on purpose.

**The differentiated half is the insight layer** (`decisions/2026-08-07_crm-insight-layer.md`) — seven
reads a CRM row cannot produce, each a script *and* an API endpoint:

| | What it answers |
|---|---|
| **ghost** | where every deal would be at your own median velocity — the counterfactual board, reconstructed from git history |
| **spread** | two opposed readers, one evidence bundle. The prosecution counts only *buyer-side* action, so a wide spread means **you** are the only party moving it |
| **calibration** | your own forecasting bias, measured against predictions captured at each stage move |
| **warmpath** | which single relationship, warmed this week, unlocks the most pipeline |
| **promises** | sold-vs-delivered drift, as promise debt |
| **mirror** | the buyer's own ladder, and where your stage overreaches it |
| **autonomy** | % of *pipeline-moving* work running without you |

**Every one refuses to produce a number it cannot defend.** That refusal is the feature; the thresholds
are in the decision. Built as Sales-pillar product IP and dogfooded here first.

## HQ (`dashboard/`, Atlas owns it)

Twelve doors. The ones to understand:

- **The Board** — every open item in the OS in one list (needs-you · blocked · missing · backlog ·
  parked). **Start here when the question is "what still needs doing?"** Note its freshness strip: a
  stale source is shown, never silently trusted.
- **Evidence** — five views on "what can this OS prove about itself." The **trust ledger** audits the
  hand-written streak table against recorded evidence and the ledger outranks the prose. **Trip-wires**
  are decisions reporting their own expiry. The **DRI twin** measures how much of the Founder's judgment the
  OS has learned — and starts empty by construction.
- **WBR** — Amazon discipline: inputs above outputs. All nine goal metrics were outputs the Founder cannot move
  on a Tuesday, so the panel counts *inputs he controls*, in a **fixed row order** — the unchanging
  layout IS the mechanism. **The case against** argues against HQ's own headline numbers from the same
  data, and *no case to answer* is a real verdict.
- **Skills** — which procedures have gone quiet. Built because the Founder said *"I feel like I just forget to
  use the skills."*
- **Agents** — the roster, and under it **the one number**. `liveClients` is the north star (declared
  once, in `dashboard/goals.json`, the Founder's), rendered first and larger on the goal band; the other eight
  metrics are still tracked and explicitly *supporting*, because nine co-equal goals is zero goals.
  Below it, **what number each agent owns** and — the useful half — **why the blanks are blank**,
  clustered by root cause rather than listed as N separate problems.
- **Commercial → Finance** carries **the nine KPIs** (NRR · LTV · CAC · LTV:CAC · churn · burn multiple
  · EBITDA · OCF · retention). Seven are undefined at n=0, so each states its refusal *and* the
  precondition that clears it — burn multiple with no new ARR is **undefined, not infinite**.
  Definitions: `finance/kpi-definitions.md`; inputs: `finance/actuals.json`.

**Neither of those is a new door**, on purpose: HQ's own panel-usefulness audit argues it should get
*smaller*, and adding a door to announce a simplification would be the joke writing itself.

Honesty rules are guarded by `runtime/test_evidence.py` (228 assertions) and
`runtime/test_numbers.py` (154 more, each pinning one refusal in the metric layer).

## The app (`app/`)

One sign-in in front of HQ + CRM + Connector Console. Three roles: **partner** (all three),
**advisor** (CRM + console — no HQ, because HQ carries runway and partner splits), **connector**
(console only). Installable as a PWA.

Built as a **reverse-proxy gateway, not a rewrite** — both dashboards reach their APIs only via
absolute-path `fetch()`, so a three-line shim makes an app mounted at `/crm` behave as if it were at
the root. 7,500 lines of UI untouched.

⚠️ **HQ and the CRM have no auth of their own.** An unauthenticated GET to `:8790/api/data` returns the
entire CRM. **The backends must stay on `127.0.0.1`**, and this gateway is the only thing that may ever
face outward — a deliberate single point of failure. Binding elsewhere prints a warning saying so.
Contract: `app/_README.md`.

## Done when

**your CRM has one real company in it and HQ renders without errors.**

If you cannot point at that, the step is not finished — do not move on.
