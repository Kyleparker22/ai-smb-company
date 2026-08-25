# 05 — Operating Rhythm (how the Founder runs YourCo with this OS)

> The cockpit manual. The OS is built and running on its own; this is how you *fly* it. **Your job is not to do the work — it's to conduct and approve.** The agents do the work and hand you decisions. Your scarce, high-value input is strategic taste + the handful of approvals only you can give. Minimize your time, maximize your leverage.

## The principle: you conduct, the agents play
Operating model: *"siblings, the Founder conducts."* The agents run the work and surface what needs a human. **Trust the gates** — the runtime physically can't send, delete, or pay without you (`runtime/headless-settings.reference.json`). So you can let it run all week and just review the queue. As the autonomy ladder earns it (`decisions/2026-06-12_autonomy-ladder.md`), even that review shrinks.

## Your cockpit — where to look
| Surface | What it gives you | Where |
|---|---|---|
| **The app** ⭐ | **One sign-in in front of all three.** Start here — HQ, the CRM and the Connector Console behind a single login, role-scoped, installable to your phone's home screen. The `● yourco` pill bottom-right switches between them. | `./show.sh` → **`:8820`** · built 2026-08-23, `app/_README.md` |
| **YourCo HQ → `Today`** | agent health · pipeline · finance · what needs you — one pane of glass | inside the app at `/hq/` (direct: `:8791`) |
| **#all-yourco (Slack)** | the live feed — every loop posts its summary here | Slack |
| **The CRM** | the pipeline, source of truth | inside the app at `/crm/` (direct: `:8790`) |
| **`loops/`** | the full dated artifact behind any summary, when you want depth | repo |
| **Your phone** | all of the above, anywhere, private | Tailscale (`runtime/phone-access.md`). ⚠️ Today the app runs on your Mac — it is only reachable while that is on. Putting the gateway on the VPS as a systemd daemon is what makes it phone-first. |

### HQ's twelve<!--#count: match dashboard/index.html /data-v="([a-z-]+)"/--> doors (added 2026-08-07 → 08-13 — this section is why the manual was refreshed)
`Today` is the front page, but four newer doors answer questions the daily scan can't:

| Door | The question it answers |
|---|---|
| **`The Board`** | **"What still needs doing?"** Every open item in the OS in one list — needs-you · blocked · missing · backlog · parked. **Start here when you have time rather than a trigger.** Check its freshness strip; a stale source is shown, never silently trusted. |
| **`WBR`** | "Am I moving the inputs I actually control?" Conversations held, deliverables shipped, companies touched — counted from the CRM, in a fixed row order, with a trailing 6-week / 12-month view. Includes **the case against** — HQ arguing against its own headline numbers. |
| **`Evidence`** | "What can this OS prove about itself?" The trust ledger, decision trip-wires, the time machine, the DRI twin, vacancies. Each refuses to state a number its inputs don't support. |
| **`Partners`** | "Where does the three-partner structure actually stand?" Governance vs the OA, the lock-in run, the connector flywheel, and who owns which open item. |
| `Clients` · `Commercial` · `Financial Model` · `System` · `Agents` | Per-engagement readiness · pipeline · the model · runtime health · the roster. |
| `Skills` | "Which of the 18 skills am I actually using?" Usage measured from the artifact each skill *creates*, never from a file being edited. A skill with no trace reads *unmeasurable*, not *unused*. |

Deep links work: `#board?state=needs-you&owner=the Founder` opens the door *and* applies the filter. Build them with `runtime/hqlink.py`.

## The daily rhythm (~10–15 min)
**Morning:**
1. **`./show.sh`, then open the app** (`:8820`) — sign in once; scan agent health + any "needs the Founder" tile.
2. **Read the latest line in #all-yourco** — Jim's inbox-triage / the day's briefing → the **needs-the Founder short list**.
3. **Clear the approval queue** — the Gmail drafts the agents staged (approve + send the ones you want), and the flagged decisions. ~5–10 min.
4. Anything time-sensitive → handle or hand back.

That's the whole morning. The rest runs itself.

**Through the day:** the loops fire on their own. You only re-engage when something's flagged *for you* — a real prospect reply, a booked call, a decision.

## The weekly rhythm
- **Sunday PM** — Kolby's eval review lands (the quality scoreboard). Skim for any **fails**.
- **Monday AM** — the stack fires: David's pipeline (06:50) → sales (07:00) → Charles's finance (07:15) → **Atlas's briefing (07:55)** → watchdog (08:15). **Read the briefing — it's your whole week in one page** (what changed, what needs you, the recommended actions). When Melanie runs, her **CEO read** is the prioritized "what to focus on."
- **Wednesday** — customer-health (once you have clients).
- **Friday** — Katie's content brief.
- **Monthly / quarterly** — Brett's advisory memo, Charles's close, Luka's brand audit, Polo's pricing review. Read, react, move on.

## What only YOU can do (the irreducible founder inputs)
- **Strategy + taste** — the calls the OS *proposes* but you *decide* (Melanie predicts; you decide and the gap trains her).
- **The gated approvals** — external sends, go-lives, moving money, granting client-tenant access, publishing. **Connected ≠ auto.** You are the gate (until eval earns it down the autonomy ladder).
- **The standing "needs the Founder" items** the agents keep surfacing — counsel review of the legal suite, the **2FA sweep**, the **launch decision**, the **CAN-SPAM postal-address** call. Only you can clear these. *(Cash-on-hand came off this list 2026-08-05 — you supplied it and `runway.md` carries the answer. It still needs re-supplying at each monthly close, which is a recurring approval, not an outstanding item.)*
- **Feedback** — fill the *"what I'd do differently"* line on the loop artifacts. That single line is how the loops improve themselves (the feed-forward into `learnings/`).

## What to ignore (don't micromanage)
- Routine loop output that isn't flagged "needs the Founder" — **skim, don't audit.** If it needed you, it'd say so.
- The inbox noise (vendor/onboarding mail) — Jim triages it; trust the triage.
- The agents' internal steps — you review **outcomes and the gate**, not every move.

## The 10-minute morning checklist
- [ ] Dashboard — any red agent-health or a "needs the Founder" tile?
- [ ] #all-yourco — read the latest briefing / triage line.
- [ ] Approval queue — approve + send the drafts you want; make the flagged decisions.
- [ ] One glance at the pipeline — any reply or booked call needing you?
- [ ] *(when you have slack, not daily)* **The Board** — pick one open item and close it.
- [ ] Done. Close the laptop.

## As the company grows
Same rhythm, more leverage. The dashboard + the briefing **scale the synthesis, not your reading** — Melanie and Atlas roll more up as there's more to roll up. The autonomy ladder steadily shrinks your approval load as eval evidence accrues. **The goal: the business runs itself between your approval taps.**

> See also: the agents + their triggers (`04_agent_roster.md`), the loops (`runtime/agent-registry.json` — the canonical list; the old table in `00_README.md` was removed because it drifted), the cockpit (`/dashboard/`), phone access (`runtime/phone-access.md`).
