# The Connector Console — step 2 of the Connector OS (**v2**)

> **STAGED / counsel-gated.** The connector program has not launched. Every page this renders says so on
> its face. Nothing here is sent to a connector until §A/§B of
> `processes/partnerships/legal/counsel-review-checklist.md` and the launch gate clear.
> Spec: `processes/partnerships/connector-os.md` §2 · Decision: `decisions/2026-08-07_connector-os.md`.
> Owner: **Bird** (program) · Kimi (build) · David (CRM/data) · Charles (payouts) · Ray (legal).

The connector-facing half of the glass ledger. One page per connector, in this order:

| Section | What it is |
|---|---|
| Your rung | R0–R4, live progress to the next one, what each rung unlocks |
| **Your referrals** | **v2:** working records — yourco's fields read-only, *their* next action + notes editable. **v3:** each carries its **mode** — *Your introduction* or *yourco is calling* |
| **Submit a contact** | **v3:** Sourcer mode — the form (provenance + consent **required**), the bounty ledger ($25 verified + $25 booked call), and every submission's real status incl. rejected. Renders *accrued, not payable* |
| **What we say to the people you send us** | **v3.1:** the first-contact draft, before it goes anywhere. Approve · edit · stop. The **A0→A1→A2** gate is earned on evidence and **reset to A0 by any complaint** |
| What you're owed | commission with the arithmetic shown, per client |
| **How fast we moved your referrals** | **v3.1: this section grades yourco, not the connector.** Where each referral would be at yourco's own median pace, denominated in *their* commission. Refuses a figure below 3 referrals, on unmeasured stages, or with no board history — and reports yourco being fast too |
| **When we let you down** | **v3.1:** the escrow — yourco's own SLA misses and mishandling, computed from the same timestamps that prove the promise. Explicitly **not** a guarantee that referrals close |
| **How good your read is** | **v3.1:** their calibration (Brier + bias + the said-vs-actual bands). **No score at all** below 5 resolved; a good read earns queue priority that volume cannot buy |
| **Your own AI OS** | **v3.1:** the grant at 5 live referred clients, with *earned* and *running* shown separately so the gap is a visible commitment |
| **Your commission tier** | **v2:** 10 / 12.5 / 15%, what earns the next tier, and what it is worth **on today's book** |
| **Your goals** | **v2:** targets they set; current values computed from the CRM; pace against the quarter |
| **Your reporting** | **v2:** funnel, referrals by month, commission by month, downline contribution — from the log |
| Downline override | informational · counsel-gated · **not payable**, excluded from every total |
| **Your downline** | **v2:** the upline view — production, pipeline, goals (**editable**), reporting per member |
| **Learnings** | **v2:** rung-aware training rendered from `processes/partnerships/connector-training/` |
| **Resources** | **v2:** documents + assets with per-item availability; nothing uncleared is ever linked |
| **Phantom share track** | **v2: DARK BY DEFAULT** — renders only for connectors in `meta.phantomTrack` |
| Your history | every event on their account from the append-only attribution log |

> **Two agents' numbers are computed from the connector records this console reads** (added
> 2026-08-25): **Bird** owns *active connectors* and **Kori** owns *connectors onboarded*
> (`runtime/agent-registry.json` → `agent_metrics`, computed by `dashboard/northstar.py`, rendered on
> HQ → Agents). Both come straight from `crm/data.json` contacts with `teamRole: connector` — the
> console keeps **no second copy**, and nothing here changed for this. If how a connector is counted
> ever changes, those two metrics change with it and no third surface needs sweeping.

## Files
| File | What it is |
|---|---|
| `server.py` | The whole console — data assembly, renderer, CLI, local preview server, POST write routes |
| `index.html` | The page template (brand tokens + layout). `{{TITLE}}` / `{{BODY}}` are substituted |
| `_out/` | Generated pages (`--render` / `--all` / `--sample`). Disposable — gitignored |
| `../../../crm/connector_writes.py` | **v2:** the one scoped write path (`can_write` + the locked CRM write). **v3:** `submit_contact` · `verify_submission` · `duplicate_of` · `cap_state` |
| `../../../crm/connector_statements.py` | **v3:** `bounties()` + `BOUNTY_VERIFIED` / `BOUNTY_BOOKED` / `BOUNTY_PAYABLE` — the amounts live here and nowhere else |
| `../../../crm/test_connector_bounty.py` | **v3:** 49 assertions over the bounty, the Sourcer scope, and the R1 move |
| `../../../crm/connector_ghost.py` | **v3.1:** yourco graded against its own median — filters `ghost.compute()`, never re-derives a median |
| `../../../crm/connector_approvals.py` | **v3.1:** the first-contact gate + the A0/A1/A2 rung |
| `../../../crm/connector_calibration.py` | **v3.1:** predictions, Brier scoring, queue priority |
| `../../../crm/connector_escrow.py` | **v3.1:** yourco's bond against its own conduct |
| `../../../crm/connector_perks.py` | **v3.1:** the own-OS grant at 5 live referred clients |
| `../../../runtime/connector_intake.py` | **v3.1:** text/email → submission. The console stops being the only door |
| `../../../crm/test_connector_v3.py` | **v3.1:** 70 assertions, weighted at the refusals |
| `../connector-training/` | **v2:** the connector-facing content library — lessons + `_resources.json` |

## Run it
```bash
python3 processes/partnerships/connector-console/server.py --list           # who has a console
python3 processes/partnerships/connector-console/server.py --render "Sample Contact"
python3 processes/partnerships/connector-console/server.py --all            # every connector → _out/
python3 processes/partnerships/connector-console/server.py --sample         # the FIXTURE pages → _out/_SAMPLE-*
python3 crm/connector_writes.py                                             # scope refusal matrix (read-only)
python3 crm/test_connector_bounty.py                                        # the v3 bounty/scope suite
python3 runtime/pixel_contrast.py                                           # ⭐ RUN AFTER ANY CSS CHANGE
```

**`pixel_contrast.py` is the check that catches the bug class this console kept shipping.** Four times
in two days a section went out with text that was present, correctly worded, and *invisible* — cream on
cream, on-dark on light, muted on a dark table, and finally the approval gate's A0/A1/A2 rung labels
computing to `rgb(22,27,51)` on an `rgb(22,27,51)` tile. Markup right, copy right, tests green, watchdog
silent, and every time the sentence that vanished was the one saying a number is **not** real.

It renders each page twice in headless Chrome — once normally, once with every glyph transparent — and
any pixel that differs is a pixel where text actually painted. That composites alpha, overlaps and
antialiasing for free, because the browser does it. Zero ink, or a glyph-to-surface ratio under 1.4:1,
**fails** (exit 1); under 3:1 is reported as *faint*. Proven against a deliberately re-planted bug
before it was trusted. ~70s for all four fixtures.

Known faint-but-accepted: `span.n` and `.flag` (brass on cream) and summaries on dark tiles
(`--on-dark-muted`) sit at 2.4–2.7:1. Those are brand tokens, not defects — do not "fix" them by
inventing off-brand colours.

**It is NOT part of `runtime/consistency-check.py`** — that watchdog is stdlib-only and runs headless on
the VPS, where there is no Chrome. This is a pre-ship gate you run on the Mac after touching CSS.
**Why `--sample` exists (added 2026-08-11).** Every real connector is at "not joined" — the program is
pre-launch — so a real render only ever exercises the gate page. `--sample` builds a synthetic connector
with a book, a downline, and submissions in every state, and renders the populated console, the gate, a
downline member's page, and the operator verification queue. It reads and writes **no CRM record**. The
`_SAMPLE-*.html` files in `_out/` previously had no generator behind them at all; a sample nobody can
rebuild is a stale artifact, not a fixture.

Local preview (house rule — always by launch.json name, never a guessed port):
**`yourco-connector-console`** → http://127.0.0.1:8807/ ·  a connector's page is `/c/<slug>`.
The index at `/` is an **operator** surface (so the Founder can page through the staged consoles); no
connector is ever given it — each person only ever gets their own page. **`/verify` is the operator's
submission queue** — the one place an operator session may write, and only its own act under its own
name (it can never verify a submission it made). The 24–48h promise is measured on that page.
A page exported to `_out/` renders fully but cannot save: the save controls say so plainly rather than
pretending. Saving requires the served console.

## The four rules this code exists to hold
1. **One source of truth, never forked.** Rungs come from `crm/connector_ladder.compute()`; every dollar
   comes from `crm/connector_statements.books()` + `_tier()`. The console's number, the CRM Referrals
   cockpit's number, and the money Charles pays are the same computation or it is a bug. If you ever
   find yourself re-deriving commission here, stop — import it. Rung gates come from
   `connector_ladder.UNLOCKS` via `can()` — including which *lessons* open, so the curriculum cannot
   drift from the policy.
2. **A connector sees only their own data.** `render(name)` takes one connector. It never emits another
   connector's book, client, or earnings; no yourco margin; no client internals; no CRM-wide totals; no
   yourco service prices (a referred client's own retainer appears only because it is the basis of that
   connector's commission). The attribution log renders through a **field whitelist** (`EVENT_FIELDS`).
   **Downline scope (v2):** an upline sees a downline member's rung, production (client count + active
   MRR), pipeline **as stage counts**, goals, and referral counts — deliberately **not** that person's
   client names, per-client retainers, or commission/payout figures. Production and pipeline are what
   an upline coaches on; another person's client roster and pay are not theirs.
3. **One database, scoped writes — never a second CRM that syncs.** the Founder's "data flows both ways" is
   satisfied *by construction*: `crm/data.json` is the only store, the console is a scoped view onto it,
   so there is no sync, no divergence, no conflict resolution. Every write goes through
   `crm/connector_writes.py`:
   - `can_write(actor, target)` is the single gate — own goals · downline's goals · `note` /
     `nextAction` on their **own** referrals. Everything else is refused, and **a refusal writes
     nothing at all** (no CRM change, no activity, no log event).
   - the write itself runs inside `melanie.crm_lock()` with the load **inside** the lock, then
     `_atomic_dump` + `write_mirror` — the same path `runtime/site_intake.py` uses.
   - connector-authored fields live under `meta.connectorNotes` / `meta.connectorGoals`, never on the
     company or deal record, so a connector write cannot overwrite an yourco field even if the
     allowlist were bypassed.
   - every accepted write appends an attribution-log event naming who made it. An upline editing a
     downline member's goal logs `connector: <them>, by: <upline>, onBehalf: true`.
   - **renders are still never logged** — a page view is not an attribution event.
4. **Nothing uncleared is ever shown or linked.** The Resources index links a document only when its
   manifest entry says `clearedExternally: true` *and* it is available now. Everything else is listed
   and marked ("available at launch", "in counsel review") — a connector is never handed a draft
   agreement or an uncleared income disclosure to treat as the real terms. Lesson frontmatter carries a
   `source:` for internal traceability and it is **never rendered** — no yourco file paths on a
   connector-facing page.

## Identity — real per-connector authentication (v3, 2026-08-07)
**The URL is no longer identity.** v2 derived the acting connector from the path, which made a link a
credential: anyone who could type `/c/<someone-else>` read and wrote that person's account. That path is
**removed, not demoted to a fallback**. `auth.py` is now the only source of identity, and every route
resolves *session → identity* before it resolves anything else.

**Credentials — yourco never learns a passphrase.** An operator issues a single-use, 72-hour setup link
(`--issue-setup-token "<name>"`); the connector sets their own passphrase at `/setup?token=…`. Only a
`hashlib.scrypt` hash (per-user random salt, n=2¹⁵/r=8/p=1, dklen=32) is stored. A lost passphrase is
**re-issued, never recovered** — there is nothing to look up. Tokens are stored hashed too, are single-use
(`usedAt` stamped in the same locked write that stores the hash), and expire.

**Store** — `_auth.json` + `_sessions.json`, both **gitignored**, `0600`, written atomically under an
`flock` so the CLI and the server cannot tear each other's writes. **A missing or unreadable store means
nobody can sign in, never everybody.** Sessions are persisted (a restart does not sign everyone out) and
only the SHA-256 of each session id is stored, so a leaked `_sessions.json` is not a set of live tokens.

**Sessions** — 256-bit `secrets.token_urlsafe` id; cookie `HttpOnly; SameSite=Strict; Path=/; Max-Age`,
with `Secure` added automatically whenever the Host is not loopback; 12h idle / 30d absolute expiry;
per-session CSRF token required on every POST, alongside an Origin check and a JSON content-type
requirement on the write endpoints.

**Brute force** — 5 failures locks the account 15 min, doubling per lockout to a 24h cap; a correct
passphrase does **not** unlock it early. Per-IP failure window stops spraying across accounts.
`secrets.compare_digest` throughout, and exactly one scrypt derivation runs on every failure path
(including unknown-account) so timing does not reveal who exists. One generic sentence for every failure.

**Authorization on every route, from the session, recomputed per request:**

| request | operator | self | ancestor of target | anyone else |
|---|---|---|---|---|
| `GET /c/<name>` full console | allow | allow | — | **403** |
| `GET /c/<name>` bounded downline view | — | — | allow | **403** |
| `POST …/goal` | 403 (read-only) | allow | allow (their goals) | **403** |
| `POST …/referral` | 403 (read-only) | allow | **403** | **403** |

An upline does **not** get the downline member's console — they get the same bounded card
`_downline_section` already renders on their own page (rung, production, pipeline as stage counts, goals),
reusing that one renderer so a looser second path cannot drift into existence. A 403 body is byte-identical
whether the requested connector exists or not, and never echoes the requested name. The downline set comes
from `connector_ladder.compute()` server-side (cycle-guarded), never from anything the client sends. A body
field naming an actor is **ignored** — post `actor=bob` on Alice's session and the write is Alice's.

**Audit** — `auth.login`, `auth.setup_issued`, `auth.setup_completed`, `auth.logout`, `auth.revoked` always
land on the attribution log. `auth.login_failed` is logged **only for accounts that exist**, and only on the
first failure and the one that trips the lockout: `log_event` re-reads the whole append-only log to compute
`seq`, so one line per attempt would be both an attacker-controlled pollution vector and an O(n²) DoS.
Everything else goes to the operator's stderr, which the client cannot read. No passphrase or token is ever
logged, printed, or stored in the clear.

**Still true, and still the reason this is staged:** the server speaks **HTTP on 127.0.0.1**. Authentication
is real; transport is not. Before this is served to a real connector — see `processes/launch-runbook.md`:
TLS in front of it (the cookie's `Secure` flag turns itself on, but only TLS makes it mean anything), a
bind address that is not loopback with a reverse proxy doing rate limiting, and a decision on session
storage if it ever runs on more than one process. `--render`/`--all` writes complete unauthenticated pages
to `_out/` (gitignored) — that export is an operator artifact and must not be published anywhere.

## Adding content (do this instead of editing the renderer)
**A lesson** — drop a `.md` file in `processes/partnerships/connector-training/` with frontmatter:
```
---
title: Give a demo instead of a pitch
order: 3
minutes: 3
rung: R1                 # the rung it opens at (used when `unlocks` is absent)
unlocks: demo_generation # PREFERRED — gates on connector_ladder.UNLOCKS, so policy can't drift
status: published        # or `stub` — stubs are labelled as stubs on the page
summary: One line shown even when the lesson is locked.
source: <internal provenance — never rendered>
---
```
Locked lessons are **shown, not hidden** (title, summary, length, and the rung that opens them) so a
connector can see what is ahead. Markdown is escaped before rendering — lesson content cannot inject
markup.

**A resource** — add an entry to `connector-training/_resources.json`. `clearedExternally` is the only
thing that decides whether a link renders; when in doubt, `false`.

## Honest empty states
Pre-launch, almost every connector has no referrals and is not signed (rung `null` → "Not joined").
Those pages say exactly that: zero referrals, `$0.00` owed, no goals set, an empty funnel, an empty
history, no demo kits, every lesson locked — and state plainly that nothing on the page is sample data.
Never add placeholder rows, fake demo numbers, or "coming soon" filler that implies activity.

## Phantom shares — the binding display rules
`decisions/2026-08-07_phantom-shares-supersede-equity-track.md` governs, and the code enforces it:
- **Dark by default.** Renders only when `meta.phantomTrack` (the Founder-set, per-connector, never computed,
  never auto-enabled) names this connector. Absent today → the section, the word "phantom", and every
  band number are absent from the HTML entirely.
- **Progress is factual, not projective.** Measured trailing-12-month **net-retained** referred revenue
  — for each referred client *still active today*, its months live within the trailing 12 — against the
  band thresholds carried over from `decisions/2026-06-30_rep-equity-track.md`.
- **Never** a projected payout, a valuation, or a dollar value for the units.
- Mandatory copy: discretionary · **no units exist** until a definitive plan document is executed ·
  nothing shown is a grant, an offer, or a guarantee.

## Validation performed 2026-08-07 (throwaway in-memory fixtures — nothing written to `crm/`)
Fixture: **Alice** (upline; 1 live @ $3,000/mo retained 200d, 1 at Audit) → **Dana** (downline; 1 live
@ $2,000/mo, 1 at Proposal), plus unrelated **Bob** (1 live @ $9,000/mo). 7 groups, ~120 assertions,
all passing.
1. **Renders + math** — rung R2 from evidence; direct commission **$300.00/mo**, identical to
   `books()` + `_tier()` on the same fixture; all v2 sections present; Bob (no recruits) gets no
   downline section; the live-CRM empty connector renders "Not joined / No referrals yet / $0.00 /
   history empty".
2. **Leak test v2** — Alice sees Dana's name, production, pipeline *stage label*, goals and the
   edit control, but **not** Dana's client names; Alice's page contains no trace of Bob (name, client,
   `$9,000`, event id); Dana's page contains no trace of Alice's book *or* Bob's; Bob's page contains
   neither. No page contains "margin", "gross", "profit", a CRM-wide total, or a non-whitelisted
   internal event field (checked against visible copy with tags stripped).
3. **Write scope** — a connector CAN set their own goal, their downline's goal (logged
   `onBehalf: true` with the upline named), and notes/next-action on their own referral (which also
   lands as a `connector-note` activity in the CRM's own feed). REFUSED, each leaving the fixture and
   the log byte-identical: editing Bob's goal · Bob's records · a **downline member's** records ·
   `retainer` / `stage` / `owner` on their own referral · a downline member editing their upline's goal
   · an invented goal metric · a non-connector acting at all. `can_write()` proven pure.
4. **Phantom** — with `meta.phantomTrack` absent (fixture *and* live CRM): zero regex hits for
   `phantom`, any band threshold, `0.5/1.0/1.5%`, `units`, `grant`, `equity`. Enabled for a *different*
   connector: still nothing. Enabled for Alice: renders with all six mandated disclaimers, the measured
   figure is real ($3,000 × 6 whole months live = **$18,000**), and every dollar figure in the section
   is either measured or a threshold — no unit value, no projection ("projected"/"valuation" appear
   exactly once each, inside the sentence promising never to show one).
5. **Learnings** — at R0 the two R0 lessons open and their bodies render; the R1 and R2 lessons are
   **visible but locked** with their unlock rung shown and their bodies absent; at R1 the demo lesson
   opens (gate read from `UNLOCKS`, not from the lesson file); at R2 the recruiting lesson opens
   carrying its counsel-gated warning; stubs are labelled; markdown is escape-safe against injection.
6. **Resources** — `rep-packet.md`, `referral-recruitment-onepager.md`, `referral-partner-agreement.md`,
   `income-disclosure-statement.md` and `partner-enablement-kit.md` appear **nowhere** in the HTML,
   while every one of those items is still *listed* and marked; W-9 reads "not on file" unless the CRM
   record says otherwise; demo kits read "none yet" (never invented) and "unlocks at R1" below R1.
7. **Served round trip** (real locked write path, against a temp CRM copy with the js mirror and the
   real log stubbed) — `GET /` 200, `GET /c/kori-manus` 200, unknown slug 404; `POST /c/<slug>/goal`
   200 and the target lands in the copied CRM plus the log; someone else's goal → **403**, a company
   they did not refer → **403**, unknown endpoint → 404, and every refusal left the CRM copy and the
   log unchanged.

**SHA-256 before and after the entire run — unchanged:**
`crm/data.json` `e8537675746934e91b95454e323656bc16e5b400eca147da06ce79fb27853fda` ·
`crm/_attribution-log.jsonl` `2eb5131b428d31561ab0f118c93cf679c513c3620fa4b72a7a0e1e58f2d7121b`

## Copy rules honored here
- Staged banner on every page (twice: hero + footer) — not an offer, not an agreement, not a promise
  of income, nothing payable until launch.
- Override block: `Informational · counsel-gated · not payable`, mirroring
  `connector_statements.py`'s wording, and excluded from every total on the page.
- No internal agent names, no yourco price list, no yourco file paths, no fabricated stats —
  `CLAUDE.md` §External-surface rules + `brand/DESIGN.md` §7.
- Brand tokens copied verbatim from `brand/DESIGN.md` §1; scroll-reveal is the single motion and
  honors `prefers-reduced-motion`.

## Not built here (next in the sequence)
Step 3 the referral-spotter agent, step 4 demo generation gated on R1, step 5 the per-connector digital
employee — all counsel- + launch-gated (`connector-os.md` §Build sequence). When they land, they gate on
`connector_ladder.can(rungN, capability)` — the same `UNLOCKS` map this console reads. No surface gets
its own copy of the policy.

## Practice (added 2026-08-24)

A **Practice** section sits under Learnings, serving drills from `processes/partnerships/connector-training/_drills.json`
via `crm/coach.py`. Three rules are enforced in code and covered by `crm/test_connector_v3.py`:

1. **A drill appears only once its lesson is complete.** Before that it is a quiz on material the
   console has not given you — the opposite of how the curriculum is gated.
2. **The rubric never ships to the browser before an attempt exists.** `looks_like`/`fails_if` are the
   answer key; if they travelled with the prompt, the page could reveal them early and practice would
   become recitation. `drills_for()` therefore returns two different shapes.
3. **A self-mark is recorded as `by="self"` and never becomes an outside judgement.** It cannot clear
   a work-on item a coach flagged. Merging the two would make both numbers meaningless.

`POST /c/<slug>/drill` is self-only, like `training` — nobody practises onto somebody else's record.
**Nothing here moves a rung**: rungs move on lessons plus CRM evidence, and the page says so.

