# Instagram Publishing — build spec

> **Phase 3 of `listing-launch-module.md`.** Turns the generated social kit (`tools/flyer-builder.html`) into posts that
> schedule and publish themselves, with Kimi approving once per listing instead of copying, pasting and uploading eight times.
>
> **Status: SPEC — not built, not sold, no credentials held.** Sample Realty is a prospect; Stage 0 has not fired.
> Nothing here touches a live account until there's an engagement and Kimi's written authorization.
> Owner when built: Kemba (runtime) + Kimi (delivery) · Compliance: Rafi · Legal: Ray.

---

## 1 · What it does

**Trigger:** a listing goes live (photos delivered + features sheet written).

**Result:** the launch week's Instagram content — Just Listed post, 7-slide carousel, Reel, 5 story frames, open-house
post, price-improvement post — is written, assembled, scheduled, and published on the plan, with **one approval from
Kimi** standing between generation and the public.

**Her time per listing:** ~90 seconds (one approval screen) instead of 2–3 hours across the week.

---

## 2 · Prerequisites (client side)

| Requirement | Why | Effort |
|---|---|---|
| Instagram is a **Business or Creator** account | The Content Publishing API refuses personal accounts | 2 min in IG settings |
| Account **linked to a Facebook Page** | The API authenticates through the Page, not the IG login | 5 min |
| Kimi grants the yourco Meta app the **Instagram Tester** role | Lets us publish to *her* account without Meta App Review | 1 min, her side |
| Written authorization to post as the brokerage | She is a licensed broker; this is her advertising | Engagement paperwork |

**The App Review shortcut is load-bearing.** Publishing on behalf of *third parties* requires Meta App Review
(2–4 weeks, business verification, screencast). Publishing to **your own account** does not: the app runs in
development mode and the target account is added as an Instagram Tester. Because we publish only to Sample Realty's
own account, we skip App Review entirely. **If Sample Realty ever wants this resold to other agents, App Review
becomes mandatory** — that is a different product with a different timeline.

---

## 3 · Architecture

Everything runs on yourco's existing runtime. No new infrastructure class.

```
  Listing record (features sheet + photo set)
        │
        ▼
  [1] generator            claude API → captions, carousel copy, reel script, story text
        │                  (yourco runtime · systemd timer or on-demand)
        ▼
  [2] asset builder        composes carousel slides + story frames (text over photo)
        │                  → uploads to public asset host
        ▼
  [3] compliance gate      fair-housing scan · price-claim check · fact diff vs listing record
        │                  FAIL → never reaches Kimi, raises to the Founder
        ▼
  [4] approval queue       one screen: every asset, every caption, scheduled time
        │                  Kimi: Approve all · Approve item · Edit · Reject
        ▼  (approved only)
  [5] scheduler            systemd timer, minute resolution, fires at planned times
        │
        ▼
  [6] publisher            IG Graph API: create container → publish
        │
        ▼
  [7] verifier             re-reads the post back, confirms it landed, logs permalink
```

**Components and where they live:**

| # | Component | Runs where | Notes |
|---|---|---|---|
| 1 | `listing_social_gen.py` | runtime, on-demand | Claude API; the tool's templates become the *prompt scaffold*, not the output |
| 2 | `asset_builder.py` | runtime | Headless Chrome → PNG, same technique that renders the PDFs today |
| 3 | `compliance_gate.py` | runtime | Hard gate. Extends the tool's fair-housing screen |
| 4 | Approval surface | Slack `#yourco-<client>` + web view | Slack listener already exists (`runtime/slack-agent-listener.py`) |
| 5 | `social_scheduler.py` | systemd timer, every 5 min | Reads the approved queue, fires what's due |
| 6 | `ig_publisher.py` | runtime | The only module that talks to Meta |
| 7 | `post_verifier.py` | runtime, +5 min after publish | Confirms and records the permalink |

---

## 4 · Auth flow & token lifecycle

**One-time setup (the Founder + Kimi, ~20 minutes together):**

1. Create the Meta app (yourco-owned), add the **Instagram Graph API** product
2. Request scopes: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
3. Kimi accepts the **Instagram Tester** invite on her account
4. OAuth once → short-lived user token
5. Exchange for a **long-lived token** (~60 days)
6. Resolve and store the **IG User ID** (the Page-linked business account ID)
7. Secrets land in the gitignored env file per `.claude/skills/wire-credentialed-connector/` — **never in chat, never in the repo**

**Ongoing — the token-refresh watchdog** (`ig_token_watchdog.py`, daily timer):

| Token age | Action |
|---|---|
| < 45 days | Nothing |
| ≥ 45 days | Refresh; log the new expiry |
| Refresh fails | Retry ×3 with backoff → then alert the Founder in Slack + email |
| ≤ 7 days and still unrefreshed | **Escalate loudly** — Slack, email, and the Monday briefing |
| Expired | Scheduler **pauses all publishing**, queue holds, nothing is lost |

The failure to avoid is silent expiry: the token dies, posts stop, and nobody notices for a week. Hence the
staircase above, and hence the paused-not-dropped behaviour — a queue that holds is recoverable, a queue that
discards is not.

---

## 5 · The publishing calls

Two-step for every post type. Containers are cheap; publishing is rate-limited.

```
Single image / Reel / Story
  POST /{ig-user-id}/media          image_url=… | video_url=…, caption=…, media_type=REELS|STORIES
    → creation_id
  POST /{ig-user-id}/media_publish  creation_id=…
    → post id

Carousel (up to 10)
  POST /{ig-user-id}/media          image_url=…, is_carousel_item=true      ×N  → child ids
  POST /{ig-user-id}/media          media_type=CAROUSEL, children=[…], caption=…  → parent id
  POST /{ig-user-id}/media_publish  creation_id=parent
```

**Constraints that shape the design:**

- **Images must be at a public URL.** The API fetches them; you cannot upload bytes. So the asset host is not optional.
- **Rate limit: 100 published posts / 24h**, counted at `media_publish`. A carousel counts as **one**. A boutique
  brokerage will never approach this; the limiter exists anyway so a retry loop can't burn the quota.
- **Video containers process asynchronously.** Reels must poll `status_code` until `FINISHED` before publishing.
  Budget 30–90 seconds; treat `ERROR` as a failed item, not a failed run.
- **No native scheduling.** Meta publishes when you call it — *our* scheduler owns timing. This is an advantage:
  the approval gate sits in front of our scheduler, not Meta's.

---

## 6 · The approval screen

One screen per listing. Phone-first — she will use it in a car between showings.

```
┌──────────────────────────────────────────────┐
│  2304 Highland Forest Drive                  │
│  8 posts · launch week of Mar 3              │
│  ✓ Fair-housing screen clear                 │
│  ✓ Facts match the listing record            │
├──────────────────────────────────────────────┤
│  Mon 9:00a   Just Listed        [img]  ✎ ✕  │
│  Tue 11:00a  Carousel · 7       [img]  ✎ ✕  │
│  Wed 5:00p   Reel · 0:28        [vid]  ✎ ✕  │
│  Thu 8:00a   Stories · 5        [img]  ✎ ✕  │
│  Fri 4:00p   Open house         [img]  ✎ ✕  │
├──────────────────────────────────────────────┤
│      [ Approve all ]    [ Hold everything ]  │
└──────────────────────────────────────────────┘
```

**Rules:**
- Nothing publishes without an explicit approval. Silence is **not** consent — an unapproved queue expires quietly rather than posting.
- **Edit** opens the caption inline; edits re-run the compliance gate before they can be approved.
- **Hold everything** freezes the listing's whole queue — one tap, useful when a deal wobbles.
- Approving is logged with timestamp and content hash. If a post is ever questioned, there is a record of exactly what she approved.

---

## 7 · What fires autonomously vs. what waits

Per `processes/autonomy-matrix.md`: every action starts at the **approval floor** and earns autonomy on evidence.

| Action | Launch | Can earn autonomy | Ceiling |
|---|---|---|---|
| Write captions / assemble carousel & reel | Autonomous | — | Already autonomous; output is gated downstream |
| Publish **Just Listed** | Approve first | ✅ after 20 clean approvals with zero edits | Autonomous |
| Publish **carousel / reel / stories** | Approve first | ✅ same bar | Autonomous |
| Publish **open house** | Approve first | ✅ once day/time comes from the calendar rather than a human | Autonomous |
| Publish **price improvement** | Approve first | ❌ | **Always gated.** Price is the highest-liability field in real estate |
| Anything naming a **buyer, seller, or offer** | Blocked | ❌ | **Never.** Confidentiality |
| **Under contract / Sold** post | Approve first | ❌ | Gated — status claims must match the MLS record |
| Reply to a comment or DM | Not in scope | — | Separate module; conversation ≠ publishing |

**"Clean approval" means:** approved without edits, no compliance flag, and the post verified as landed.
The streak resets on any edit — an edit means the draft was wrong, which is exactly the signal autonomy should respect.

---

## 8 · Failure modes

| # | Failure | Detection | Behaviour | Who hears |
|---|---|---|---|---|
| 1 | Token expired | Publish returns 190 | **Pause all publishing**, hold queue, no data loss | the Founder: Slack + email, immediate |
| 2 | Token nearing expiry | Daily watchdog | Auto-refresh; escalate at ≤7 days | the Founder if refresh fails |
| 3 | Asset host down | Container creation fails | Retry ×3 (1m/5m/15m), then hold the item | the Founder after 3rd failure |
| 4 | Reel still processing | `status_code != FINISHED` | Poll to 5 min, then reschedule +1h, then hold | the Founder on second slip |
| 5 | Rate limit hit | Publish returns 4 / 32 | Back off, requeue for the next window | Log only, unless recurring |
| 6 | Compliance gate FAILS | Pre-approval scan | **Never reaches Kimi.** Item held, reason logged | the Founder — this is a content bug to fix |
| 7 | Facts drifted from the listing record | Fact diff at generation | Regenerate; if still mismatched, hold the listing | Kimi + the Founder |
| 8 | Listing status changed (withdrawn / under contract) | Pre-publish status re-check | **Cancel every pending post for that listing** | Kimi — confirmation it was caught |
| 9 | Post published but not verifiable | Verifier finds no permalink | Flag as `uncertain`; **never auto-retry** (double-post risk) | the Founder, manual check |
| 10 | Duplicate publish attempt | Idempotency key per item | Second attempt rejected before the API call | Log only |
| 11 | Kimi never approves | Queue age > scheduled time | Expires silently. Nothing posts. | Digest at week's end |
| 12 | Meta API version deprecated | Version-pin check, monthly | Warn ahead of the sunset date | Kemba |

**#8 is the one that matters most.** A "Just Listed" post firing the day after a property goes under contract is the
kind of error that costs a broker credibility. The pre-publish status re-check is the last gate before every single call.

**#9 deserves its own note:** on ambiguity we do *nothing* and ask a human. An auto-retry that double-posts is worse
than a post that didn't land — one is embarrassing, the other is invisible until a person looks.

---

## 9 · Compliance guardrails

- **Fair-housing scan** on every generated caption — the tool's screen, extended, run server-side as a hard gate
- **No price** in any generated copy unless the price is read from the listing record *and* the post type permits it
- **Brokerage identification** appended per ST/SC advertising rules — not optional, not editable away
- **Photo rights**: only assets from the listing's own delivered set; no portal or map imagery can physically enter the pipeline
- **AI-imagery disclosure** if a cinematic tour clip is used, per the tour module's rule
- **Audit log**: every generation, approval, publish, and verification, with content hashes — reconstructable for a board complaint
- **Kill switch**: one command halts all publishing for a client, immediately

---

## 10 · Build phases

| Phase | Ships | Est. |
|---|---|---|
| **0** | Account setup, Meta app, tester role, tokens, asset host | ~½ day, mostly waiting on Kimi |
| **1** | Generator + compliance gate + approval screen. **Publishes nothing** — she approves and copies. Proves the content is good before it can go wrong. | ~2 days |
| **2** | Publisher + scheduler + verifier, single images only | ~2 days |
| **3** | Carousels, reels, stories | ~2 days |
| **4** | Token watchdog, failure handling, audit log, kill switch | ~1 day |
| **5** | Autonomy promotions on evidence | ongoing |

**Phase 1 before Phase 2 is deliberate.** Content quality is the risk; publishing is the easy part. Running a full
launch week through approval-only, with nothing able to reach the public, is how we find out whether the writing
is good enough to trust — cheaply, and without an audience.

---

## 11 · What has to be true first

- ⚠️ **Stage 0 has not fired.** No audit, no proposal, no engagement.
- Kimi's written authorization to publish as the brokerage, and her account access.
- Ray + Rafi sign-off on the fair-housing gate and the advertising-identification rule before a single live post.
- Confirm her MLS's rules on automated syndication and on AI-generated imagery — board rules bind us regardless of what the API allows.
- A decision on asset hosting (yourco-hosted vs. her site) — it determines who owns the photo URLs long-term.

## 12 · Honest scope note

Everything above is buildable with tools yourco already runs — the VPS, systemd timers, the Slack control surface,
the approval gate, the Claude API. Nothing here is speculative technology.

What it is **not** is a file on Kimi's laptop. The current builder generates the content and always will; publishing
requires credentials, an always-on server, and someone accountable when a post fires wrong at 9am on a Sunday.
That accountability is the product.
