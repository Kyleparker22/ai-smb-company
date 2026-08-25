# Host (VPS) billing failure is a runtime-death vector the on-box alarm can't catch

**Date:** 2026-07-10 · **Area:** ops / runtime reliability

## What happened
The Fri 07-10 inbox-triage desk caught a Hostinger email (07-09 22:44 ET): *"Your payment for KVM 2 plan for `srv1745256.hstgr.cloud` didn't work… balance was insufficient"* — $24.49, the VPS that runs the entire always-on OS. The runtime was still up (grace window), but an unpaid VPS gets suspended and the whole OS goes dark. Surfaced only because it landed in the Founder's inbox and the desk pulled it out of the vendor-noise pile.

## Why it matters (the reusable point)
This is [[2026-06-18_runtime-silent-credit-death]] one layer down. That learning fixed the Anthropic-credit death with an **on-box shell alarm** (`runtime/runtime-alarm.sh`) that greps loop logs and pings Slack without using API credits. But that alarm **runs on the same VPS it's monitoring** — so a *host* billing lapse (or any host suspension) takes the alarm down with it. The exact rule from the credit-death learning — *"a monitor must not depend on the thing it monitors"* — is violated for the host-billing failure mode: the shell alarm survives a dead API balance but **not** a dead host.

So there are two distinct silent-death vectors, and the current design only covers one:
- **API-credit death** → on-box shell alarm catches it ✓
- **Host billing / VPS suspension** → nothing catches it (alarm dies with the box) ✗

## How to apply (feed-forward)
1. **Durable prevention:** enable **auto-renew / a funded payment method (or prepay) on Hostinger** for the runtime VPS — same fix shape as Anthropic credit auto-reload. Owner: Kemba/platform (the Founder holds until built). Watch for the annual/monthly renewal date.
2. **Off-box heartbeat:** the only monitor that can catch a host death is one **not on that host** — e.g. a free external uptime ping (healthchecks.io / UptimeRobot) hitting a runtime endpoint or a dead-man's-switch the box pings outbound every hour; miss = alert. Add to the reliability backlog.
3. **Desk-loop behavior (already applied this run):** treat any `from:hostinger`/host-provider **payment-failure / suspension** mail as top-of-desk needs-the Founder, never let it get swept with receipts + newsletters, and keep it out of any auto-archive filter's scope (exclude billing/invoice addresses — noted in the 07-10 artifact's filter spec).

Triggers: loop:watchdog, agent:kemba, agent:charles, vps billing, host payment, runtime liveness
