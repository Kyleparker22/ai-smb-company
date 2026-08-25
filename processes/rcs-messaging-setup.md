# RCS Business Messaging — implementation runbook (Phase-2 messaging)

> **What RCS is:** Rich Communication Services — the modern successor to SMS. For business ("RCS Business
> Messaging" / RBM) it gives a **verified, branded sender** (your name, logo, blue verified checkmark), **rich
> cards/images/carousels/buttons**, **read receipts + typing indicators**, longer messages, and encryption — and
> it's now supported on **both Android and iOS** (Apple added RCS in iOS 18). It's the legitimate, ToS-compliant
> "better than plain SMS" channel — the trusted, branded experience, *without* the Apple-iMessage-ToS / ban risk of
> third-party "blue bubble" senders (which we don't touch — Rafi). the Founder wants this (2026-06-17).

## ⚠️ The load-bearing correction (verified 2026-06-17): RCS is a WARM channel, NOT for cold outreach
Before any setup — two findings that change the plan:
1. **Instantly does NOT support RCS** (it's email + SMS + calling only). RCS would require a **separate RBM provider
   account — Twilio / Sinch / Vonage** — plus Google brand verification. Not a toggle.
2. **RCS Business Messaging is opt-in / existing-relationship ONLY**, by Google's own Acceptable Use Policy. *"You
   must obtain consent prior to soliciting any end user… only communicate with users who have explicitly opted in…
   do not send unsolicited content."* Cold, unsolicited promotional RCS is **explicitly banned** and grounds for
   **agent suspension (permanent for severe cases)** — on top of TCPA exposure. ([Google RBM AUP](https://developers.google.com/business-communications/rcs-business-messaging/terms-and-policies/aup))

**So: do NOT stand up Twilio to cold-prospect over RCS.** It's not allowed and it risks the sender. **Cold outreach
stays email-first (Instantly)** — that's the right channel and its compliance model is different.

**Where RCS *is* legit:** a **richer SMS upgrade for already-consented contacts** — appointment reminders, booking
confirmations, status updates, review requests, two-way support for existing customers. That maps to yourco's
**Reminder & Recall / Missed-Call Text-Back** SKUs and **client deliverables for warm/opted-in audiences**, NOT to
yourco's own cold pipeline. Revisit RCS when a real consented-audience use case (a client deployment, or messaging
opted-in leads/clients) justifies the provider account + the multi-week brand verification.

## The honest framing (for the warm use case only)
RCS is **not a quick toggle.** It needs (1) a separate RBM provider (Instantly won't do it), (2) **Google brand +
agent verification** (Twilio advises **4–6 weeks**; Sinch ~2–3 days after Google's questions), and (3) the **opt-in +
consent discipline above** (A2P, STOP/HELP, TCPA). It's a **Phase-2 warm-channel** upgrade — only worth it once
there's a consented audience to message; don't block the launch on it.

## The implementation path
1. **Pick the provider.** **Correction (2026-06-17): yourco does NOT have a Twilio account.** SMS is being set up
   through **Instantly** (it handles 10DLC + sending) — there is no standalone Twilio/RBM account today. So the path is:
   **(a) first check whether Instantly supports RCS** (if it does, it's the simplest — same tool, same numbers, no new
   vendor). **(b) Only if Instantly doesn't do RCS**, stand up a separate **Google RBM partner** account — **Twilio,
   Sinch, or Vonage** — which is a *new account the Founder sets up* (agent can't), with its own number/10DLC plumbing. RCS
   then rides that sender as a separate channel from the Instantly campaign tool. Don't assume Twilio is already in place.
2. **Register the RBM Agent** with Google through the provider — business name, logo, brand color, description,
   contact, sample use cases.
3. **Brand + agent verification** — Google reviews and approves the agent (the long-pole step; submit early).
4. **Carrier/launch** — once verified, the agent can message RCS-enabled devices; non-RCS devices **fall back to
   SMS automatically** (so you build once, degrade gracefully).
5. **Consent + compliance** — same as SMS: opt-in on file, STOP/HELP, A2P registration, TCPA. The SMS Terms page +
   privacy SMS clause already drafted (`processes/10dlc-sending-infra-setup.md`) cover the policy side.
6. **Send rich messages** via the provider API (branded cards with a "Book" button, etc.).

## ⚠️ Reality check (2026-06-17): RCS isn't startable on a trial account — PARK it
the Founder created the Twilio account, but the console shows **no "create RCS sender"** — because **RCS Business Messaging
is not available on a Twilio trial account.** It requires: (1) **upgrading** off trial to a paid account, (2) an
**RCS access request / onboarding** with Twilio (gated, not self-serve like SMS), and (3) **Google brand verification**,
which wants an *established* business identity. A fresh, pre-revenue trial can't productively do any of that.
The sender form also **hard-requires live public URLs for a Privacy Policy and a Terms of Service** — which yourco
doesn't have yet (`privacy.html` + `sms-terms.html` are drafted but **not deployed**, and need counsel/FTSA review
before going live). So the sender can't be completed until the site is live — another reason RCS is gated on launch.
**Decision: PARK RCS until there's a consented audience to message (post-launch).** Nothing is blocked by this —
cold outreach is Instantly (email + SMS); Twilio-for-voice only matters when a voice client signs. The "start the
4–6 wk clock now" advice only applies *once the account is upgraded + a real business profile exists* — revisit then.
The Twilio account exists (seed done) + the `twilio.py` connector + `.twilio.env` scaffold are ready for that day.

## Setup steps — Twilio RBM + Google brand verification (when un-parked: upgraded account + real business)
**For the warm/consented use case only.** Empty creds scaffold staged at `runtime/.twilio.env` (gitignored).
1. **Create/confirm a Twilio account** (twilio.com) + add billing. *(Agent can't — the Founder.)*
2. **Enable RCS** in the Twilio Console → Messaging → RCS, and **create an RCS Agent** (brand name, logo, color,
   description, contact info, sample use cases — the warm ones: reminders/confirmations/review-asks).
3. **Submit the agent for Google brand verification** (Twilio routes it to Google; Google contacts the brand to
   confirm identity). **Plan 4–6 weeks**; a Fast Track exists via a Twilio account manager. This is the wait — start it.
4. **Carrier launch** once verified; RCS-capable devices get rich messages, others **fall back to SMS automatically**.
5. **Wire it** (post-verification): paste `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_RCS_AGENT_ID` /
   `TWILIO_MESSAGING_SERVICE_SID` into `runtime/.twilio.env`. The connector is **already scaffolded**
   (`runtime/twilio.py`) — dry-run by default, and it **refuses to send to any number without a recorded
   `sms_consent`** (CRM). RCS rich content (cards/buttons via the Content API) is the one TODO it flags for when
   the agent is verified; SMS body is the fallback.
6. **Only message consented contacts** — the opt-in captured on the intake forms (`sms_consent` + the timestamped
   disclosure, now stored on the CRM contact) is the consent record. Counsel/Rafi review the disclosure copy + the
   consent flow before first send.

## What's the Founder's (the agent can't do these)
- Create/own the **Twilio (or Sinch/Vonage) account** + billing; **agent can't enter credentials or set up accounts.**
- Submit the **brand/agent for Google verification** (business identity).
- Counsel/FTSA sign-off (same review as SMS — it's the Phase-4 legal review anyway).

## What the OS does once it's live
- The branded RCS sender becomes the richer channel for **warm/consented** messaging (reminders, confirmations,
  booked-call nudges, review requests) — *not* cold blasts. Cold outreach stays **email-first**; SMS/RCS is for
  consented contacts (same rule as SMS).
- Connectors/sender config get an empty gitignored `*.env` scaffold when the Founder's ready to wire keys.

## Sequencing
Email-first (live channel) → **10DLC SMS** (in progress) → **RCS** (this doc, Phase-2). Don't block the launch on
RCS; it's an upgrade to layer on once SMS is proven and the brand is verified. Owner: the Founder (accounts/verification) +
Kemba (wiring) + Rafi/counsel (consent/legal).
