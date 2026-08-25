# launch-gate — status tracker

> **The master launch gate.** Nothing external (site, outbound, partnerships, referral program, Sample Product public, **press pitching + social publishing** — `processes/local-media/`, the content engine's platform map) moves until this clears. Press is gated *harder* than most: a feature is maximum-visibility founder exposure. This file is the **only** place its status lives — when anything changes, update this file first, then `processes/launch-runbook.md`. Owner: **the Founder** (only the Founder has the facts; agents read, never guess). Created 2026-07-05 by the full OS audit (`loops/_audit/2026-07-04_full-os-audit.md`) because the gate was tracked nowhere.

## Current status

| Field | Value |
|---|---|
| Status | 🔴 **Open — blocking launch** |
| Open since | **2026-06-12** — the date the "~weeks out" estimate was given (`processes/launch-runbook.md`). *This page deliberately no longer states how long ago that was: the hand-typed version read "3+ weeks past" for seven weeks while the real figure passed ten, so the elapsed time is now computed — by `runtime/consistency-check.py` every Monday and on HQ → The Board, which renders the gate with a live age.* |
| What the gate is | 🟥 **UNRECORDED — the Founder only.** See "The two answers only the Founder has" below. Nothing in this repo states what the OtherVenture matter is; every one of the 220 files that mentions it treats it as a known blocker whose content lives outside the OS. `launch-runbook.md` calls it *"OtherVenture legal resolution"* and that is the entire recorded description. **No agent may fill this in** — a guessed sentence here would be indistinguishable from a fact, in the one file whose whole job is being the honest record of a blocker. |
| Resolution condition | 🟥 **UNRECORDED — the Founder only.** Same rule. Without it, "cleared" is not a testable state and nobody but the Founder can ever say the gate has lifted. |
| Last real update | **None — the status has never changed since it was recorded.** Verified from git: the file has four commits (2026-07-05 created · 2026-07-22 press added to scope · 2026-08-07 folder move · 2026-08-24 `send-package/` marked superseded) and **not one of them altered the status, the estimate, or the resolution condition.** The 2026-06-12 estimate has therefore stood unrevised the entire time. |
| Next check-in | **2026-09-01**, then every Monday until it clears. *Set as a default on 2026-08-25 by the sweep, not by the Founder — move it freely; the point is that a blank here is what produced 51 days of silence, and a date someone can change beats a field nobody owns.* Already nagged automatically: the consistency watchdog (Mon 07:40) fails when the log goes 30 days cold, and The Board carries the gate with a live age. |
| What fires when it clears | `processes/launch-runbook.md` Part 2 (the go-live sequence), in order |

## The two answers only the Founder has

Both blanks above are one sentence each. They are left blank rather than approximated because this
file is the single source for the gate, and an approximated blocker reads exactly like a real one.

**1. What is the OtherVenture matter, and why does it block yourco going external?**
One honest sentence. It does not need to be complete or flattering — it needs to be true enough that
a reader in six months knows what was being waited on. If it cannot be written down for a reason
(privilege, an NDA, a third party), **write that** instead: *"cannot be recorded here because X"* is a
real answer and closes the field honestly. A blank is the only wrong answer.

**2. What specifically has to happen for this to count as cleared?**
The shape that works: *signed X* / *dismissed Y* / *date Z passes* / *counsel says W in writing*.
Prose like "it gets resolved" is not a resolution condition — it is the same blank in longer form.
Until this exists, **nobody but the Founder can ever declare the gate lifted**, which makes the whole
external half of the company depend on one person remembering to say so.

⚠️ **A third thing worth writing down if it is true: whether this gate is still real.** It has stood
unrevised for 74 days against a "~weeks" estimate. Either the estimate was wrong, the matter changed,
or it has quietly resolved and nobody updated the file. All three are ordinary; only the silence is a
problem — and *"re-checked, still open, no new information"* is a perfectly good log entry.

## What the gate is holding — counted, 2026-08-25

Named in numbers because "nothing external" is easy to read as "the website." It is not. Every figure
here is computed from the repo, not estimated.

| Held | Amount |
|---|---|
| Staged site pages, built and undeployed | **26**<!--#count: files agents/webb/pages/yourco-site-v2/*.html--> |
| Booking links on them, tagged and unclickable by anyone | **61** |
| Outbound sequences staged | campaigns built · **0** deals ever sequenced |
| Agents whose owned number cannot be non-zero until this clears | **3** — Katie (conversations sourced by content) · Michelle (positive reply rate) · Webb (bookings from the site) |
| Companies sitting on the bench, unworked | **34** |
| Deals in motion | **3** |
| The connector program + console | built; parts *additionally* counsel-gated (20 counsel gates, 0 cleared) |

**The three agent metrics are the newest cost and the clearest one.** As of 2026-08-25 every agent
owns exactly one number (`decisions/2026-08-25_one-number-and-agent-metrics.md`); of the 27, the only
ones that cannot become real through work alone are these three, and they are waiting on this file.

## External material this gate covers

| Asset | State |
|---|---|
| The staged site (`agents/webb/pages/yourco-site-v2/`) | built, not deployed |
| Outbound campaigns (Instantly, sourced lists) | staged, unsent |
| The connector program + console | built; parts additionally counsel-gated |
| Sample Product public surfaces | built |
| **`send-package/`** — the sendable "how yourco works" bundle | ⛔ **built, and now superseded** — marked DO-NOT-SEND 2026-08-24; it describes the pre-Audit company. Added here 2026-08-24 because every pointer to it said "send this" and nothing said don't. |
| Press pitching + social publishing | held |

> ⚠️ **`yourco.com` is live and is not covered by this gate.** A separate, earlier single-page
> site — not in this repo — has been serving the whole time (verified 2026-08-25, HTTP 200). It still
> advertises *"Two weeks. Fixed fee."* against the 2026-08-16 decision that the Audit is **free**, and
> it has **no privacy or terms page**, which is what blocks 10DLC registration
> (`processes/10dlc-sending-infra-setup.md`). Read "nothing is deployed" as *nothing from this repo*.
> Correcting or replacing that page is arguably **not** gated by OtherVenture at all — it is already
> public and already wrong.

## Update log
*(newest first — one line per status change: date · what changed · new expected timeline)*

- 2026-08-25 — *no status change.* Swept during the metrics work. Confirmed from git that the status, estimate and resolution condition have been unrevised since the tracker was created; replaced the hand-typed "3+ weeks past" (wrong by 3×) with a computed age; filled every field that was derivable; quantified what the gate holds (26 pages · 61 links · 3 agent metrics · 34 bench companies); set a default next check-in of 2026-09-01. **The two the Founder-only fields remain blank and were deliberately not guessed.** Expected timeline: **still unrevised from 2026-06-12 — it needs re-estimating by someone who knows the matter.**
- 2026-07-05 — tracker created; status carried over from launch-runbook (2026-06-12): open, "~weeks out." No recorded update since.
