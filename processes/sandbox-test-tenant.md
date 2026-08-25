# Sandbox Test-Tenant — spec

> **Why:** the eval can score an employee's *reasoning + gates* from its logic alone, but it can't verify that the **downstream actions actually fire** (the calendar event is created, the confirmation sends, the record is logged) without a live environment. The sandbox is an **YourCo-owned throwaway tenant** that Kimi builds + tests against **before** touching the client's real systems. It closes the gap the Northside dry-run surfaced (`clients/_fixture-northside-dental/_findings.md` #2) and **strengthens the autonomy gate** — the more of the eval we can run pre-tenant, the more we trust "eval-pass → ship." Owner: **Kemba** (provisions + maintains); **Kimi** uses it per build.

## What it is
A dedicated, isolated YourCo test environment with **synthetic data only** — never real client data or PHI:
| Component | Purpose | Notes |
|---|---|---|
| **Test Google Workspace** (e.g. `contact@yourco.example.com` or a separate test account) | test **Calendar** (booking) + test **Gmail** inbox (intake/confirmations) | the workhorse for text-intake + scheduling builds |
| **Test CRM / Sheet** | a stand-in system-of-record to verify "the lead/record logged" | a Google Sheet or a free CRM seat |
| **Test Twilio number + phone** | for **voice** builds — place real test calls, verify SMS | only provisioned when a voice build needs it |
| **Test ElevenLabs voice** | voice rendering for voice builds | reuse YourCo's existing seat |

## How Kimi uses it (in the build loop)
1. **Build against the sandbox first** — wire the employee's connectors to the sandbox Calendar/inbox/CRM (not the client's).
2. **Run the live-integration eval** — execute the `03_eval` test set end-to-end and verify **every downstream action actually fires**: the event appears on the sandbox calendar, the confirmation lands in the sandbox inbox, the record writes to the sandbox sheet, the booking/draft/answer truly happens.
3. **Fix + re-run** until the live half passes alongside the reasoning half.
4. **Then re-point at the client's real tenant** (the Founder-approved access) for final verification + go-live. The client's real systems get touched **last**, with a build already proven against the sandbox.

This splits the eval into two halves that the autonomy ladder cares about:
- **Reasoning/logic eval** — runnable anytime (the dry-run did this).
- **Live-integration eval** — runnable in the **sandbox** pre-client (this spec), then confirmed once in the real tenant.

## Safety / hygiene
- **Synthetic data only.** No real client data, no PHI, ever, in the sandbox. (PHI builds still need the BAA + a real tenant for final go-live, but the *integration mechanics* are proven on synthetic data first.)
- **Isolated** from production + from any client tenant.
- **Reset between engagements** — wipe test events/records so one build's data never bleeds into the next.

## Status — v1 PROVISIONED (2026-06-12)
- ✅ **Live calendar booking proven** — Sage (the demo employee) created a real, confirmed calendar event end-to-end via the connector ("[YOURCO SANDBOX] Paver patio estimate — Jordan," 6/21). The **booking downstream-action fires for real.**
- ✅ **Lead log proven** — logged to a repo file (`agents/Reed/demos/home-services-intake-sage/sandbox-leads.md`); needs no extra connector (file R/W is in the gate).
- ⚠️ **Isolation note:** the calendar connector is currently authed to the **personal** account (you@example.com), so the test event landed there. Fine for proving the mechanism; for clean ongoing use, see below.
- ⏳ Email-confirmation step needs a sandbox inbox (below).

## To finish (clean isolation — Kemba / the Founder)
- [ ] Create a **dedicated "YourCo Sandbox" calendar** (Google Calendar → create new calendar) so test bookings never mix with a real calendar. Point the build at it by calendar ID.
- [ ] *(Optional, fuller isolation)* a separate **sandbox Google account** (`contact@yourco.example.com`) for a test inbox too — enables the email-confirmation half.
- [ ] (When the first voice build lands) a **test Twilio number**.
- [ ] Document any sandbox creds in `~/.yourco/` (gitignored). Reset checklist: clear test events + the lead log between runs.

> **Bottom line:** the sandbox's core promise — *verify the live downstream actions fire before touching a client's real systems* — is **proven** (booking + log). The remaining items are isolation + the email/voice channels, not the core capability.
