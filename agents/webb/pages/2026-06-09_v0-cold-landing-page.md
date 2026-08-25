# Webb — v0 Cold Landing Page + Booking CTA

**Owner:** Webb · **Date:** 2026-06-09 · **Status:** 🟡 DRAFT — awaiting Luka brand review + the Founder approval before deploy
**Triggered by:** Reilly campaign launch dependency — every Email/SMS CTA points to `getteamyourco.com` + "Book 30 min", but that destination isn't live yet.

## Domain decision — ✅ CONFIRMED by the Founder 2026-06-09
**Cold CTAs point to `getteamyourco.com`; Webb stands up the v0 cold landing page + `/book` redirect there.** Built v0 page (single-file HTML): `agents/webb/pages/v0-landing/index.html` — deploy to `getteamyourco.com`. Rationale:
- It matches Reilly's existing copy (no rewrite of the email/SMS signatures + SMS links).
- It isolates all cold-outbound web traffic on the secondary/sending domain, keeping `yourco.com` (the primary brand site, already on Vercel) clean.
- Email DNS on `getteamyourco.com` (Instantly-managed SPF/DKIM/MX) and web DNS (A/CNAME → Vercel) coexist without conflict.

*Alternative if you prefer:* point CTAs to `yourco.com/book` and reuse the existing site — but that means editing every signature + SMS link in Reilly's copy, and mixes cold-click traffic onto the primary. Not recommended.

## What ships (v0 one-pager)
A single page at `getteamyourco.com`: hero → demo video → 3-line value → Book-30-min CTA → footer. Plus `getteamyourco.com/book` → `calendly.com/the Founder-yourco/30min`.

### Copy (brand v0.2 voice — lowercase `yourco`, outcomes-framed, no buzzwords)

**Hero**
> # a digital employee for your business — live in 48 hours
> yourco designs, deploys, and runs a named AI employee inside your company. It does the work. You own the outcome — never the tokens, the models, or the infrastructure.
>
> [ Book 30 min → ]   (→ /book)

**Demo (embed)**
> Reed's landscaping intake demo — https://share.descript.com/view/L6EdW0JYGQJ
> Caption: *"sixty seconds — what an yourco intake employee does on day one."*

**Three-line value (outcomes, not features)**
> - Live on your first use case in **48 hours** from a signed agreement.
> - Its own email, inside your business. It answers every call, qualifies the lead, books the estimate, and follows up — like a hire that doesn't sleep.
> - We own reliability, security, and improvement. You get the outcome, not a tool to manage.

**Closing CTA**
> [ Book 30 min → ]

**Footer**
> yourco · getteamyourco.com
>
> We learn your business. AI does the work.   ← primary tagline (brass final period when HTML permits)

## Build steps (Webb)
1. **Decision:** the Founder confirms CTAs → `getteamyourco.com` (above).
2. **DNS:** add web records for `getteamyourco.com` (root + www → Vercel) alongside the existing Instantly email records. *the Founder-approve before propagation.*
3. **Vercel:** add `getteamyourco.com` as a domain on the project (or a tiny dedicated one-pager project); deploy the v0 page.
4. **Redirect:** `getteamyourco.com/book` → `calendly.com/the Founder-yourco/30min` (via `next.config.js` redirect or host-level redirect).
5. **Analytics:** install the Plausible script (already provisioned) on the page.
6. **Embed** the demo video; **footer** carries the signature line.
7. **Luka brand review** (hard gate) on the preview deploy.
8. **the Founder approves preview** → publish. (No publish without approval — Webb's hard gate.)

## Eval (per Webb 03_eval)
- Page resolves 24/7 at `getteamyourco.com` (99.9% uptime).
- `/book` resolves to Calendly and a test booking completes (100%).
- Mobile load < 1.5s, Lighthouse ≥ 90.
- Luka brand pass before publish; 0 unapproved publishes.

## Dependencies / notes
- This is the destination for Reilly's first campaign — must be live before the ~June 22 first send.
- Calendly tier (free vs $10/mo) still TBD in `expenses.md` — confirm so booking limits aren't hit during a campaign.
- Fallback if Calendly is down: `mailto:founder@yourco.example.com?subject=Booking`.

— Webb, YourCo Ops
