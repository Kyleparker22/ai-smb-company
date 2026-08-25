# 10DLC + Sending Domain Setup — Step-by-Step

> **Status update (2026-06-08, late):** The cold-email portion of this runbook is **done** via Instantly's done-for-you flow. Sending domain is now **`getteamyourco.com`** (not the originally planned `mail.yourco.com`); two mailboxes provisioned; automated 30-day warmup running. Decision doc: `/decisions/2026-06-08_cold-email-infrastructure.md`. **The steps below in Phases 1–2 referencing `mail.yourco.com` and registrar DNS work are now obsolete for email** — Instantly manages all of that. What's still on critical path: **10DLC SMS brand + campaign registration (Phase 3+)**, **FTSA legal review (Phase 4)**, and **warmup completion** (~ends 2026-07-08).

**Goal (revised):** Complete 10DLC SMS registration for Reilly's SMS channel and FTSA legal review for Florida sends. Wait out automated warmup on `getteamyourco.com` before first cold email.

**Remaining critical-path lead time: 2–4 weeks** (10DLC brand approval + campaign approval + FTSA memo).

> **Status (2026-06-09):** 10DLC is blocked on an orphaned Twilio bundle conflict. Instantly support **has replied** (via their Messenger/Intercom) and followed up twice (latest 06-09) — so the ball is in **the Founder's court**, not Instantly's. Next action: the Founder opens the Instantly support chat, reads their previous message (resolution steps live there), and sends the chase reply drafted in Gmail. This is the long-pole gate for SMS in the first wave (~June 22 target); email is unaffected.

> **Status (2026-06-16):** Instantly support (Joseph) now requires a **Privacy Policy URL** and a **Terms & Conditions URL** for the campaign registration, and noted they "could not find any" on yourco.com — because the site is staged/not deployed and there was no SMS terms page. **Action taken:** added an SMS clause (§3) to `agents/webb/pages/yourco-site-v2/privacy.html` (frequency, rates, **STOP**/**HELP**, the carrier-mandated "no sharing of mobile/SMS opt-in data with third parties for marketing" statement) and built a new staged **`agents/webb/pages/yourco-site-v2/sms-terms.html`** with all required A2P elements. Both are **DRAFT — pending counsel + FTSA review** and are **not yet live**. **Still on the Founder:** (1) counsel/FTSA review of both pages (this is the Phase-4 review anyway), (2) fill real support email/phone + registered address, (3) **deploy `/privacy` + `/sms-terms` live** so the URLs are reachable for carrier vetting, then (4) give Joseph the live URLs. A draft reply + paste-text were provided in-session. The 10DLC consent/opt-in story for *cold* B2B SMS remains the key FTSA risk to clear with counsel.

**This runbook is written assuming zero prior experience with DNS / 10DLC / TCPA.** If a step is unclear, that's a runbook bug — flag it.

---

## DAY 0 — Sunday tonight (30 min, gather info)

Before touching any tool, gather these and stash them in `finance/legal-docs/business-info.docx` (already exists as of 2026-06-08; built via the docx skill from IRS CP575G letter + FL Sunbiz receipt):

- [ ] **Legal business name:** must match exactly what's on the IRS letter. Probably "YourCo LLC." Check the EIN confirmation letter (Form CP-575) if you have it.
- [ ] **EIN (Employer Identification Number):** 9-digit number, format XX-XXXXXXX. On the IRS letter.
- [ ] **Business mailing address:** the address registered with the IRS for YourCo.
- [ ] **State of incorporation:** probably Florida.
- [ ] **Date of incorporation:** check your formation docs.
- [ ] **Business vertical category:** "Professional Services" or "Technology" — pick one.
- [ ] **Domain registrar for `yourco.com`:** where you bought the domain (GoDaddy, Namecheap, Cloudflare, Squarespace, etc.). Log in tonight to confirm you still have access — don't wait until tomorrow morning to find out you don't.

---

## DAY 1 — Monday morning (60–90 min): Instantly account + domain DNS

### Step 1: Sign up for Instantly Hyper CRM (~$97/mo)
1. Go to **https://instantly.ai/pricing**
2. Find the **"Hyper CRM"** tier ($97/mo). Click "Get started."
3. Create account with `founder@yourco.example.com`
4. Enter payment. Confirm subscription.

### Step 2: Add a sending domain inside Instantly
1. In Instantly, go to **Email Accounts** (left sidebar)
2. Click **"Add new"** → **"Add Email Account"**
3. Choose **"Add a domain + subdomain"** (or whatever Instantly calls their bulk-domain wizard)
4. Enter: `mail.yourco.com`
5. Instantly will generate a list of DNS records you need to add to your registrar. **Don't make these up — copy the exact values Instantly shows you.** They'll look like:
   - An **A record** or **MX record** pointing to Instantly's servers
   - An **SPF** record (TXT): something like `v=spf1 include:_spf.instantlymail.com -all`
   - A **DKIM** record (TXT): a long string starting with `v=DKIM1; k=rsa; p=...`
6. Keep the Instantly tab open. You'll come back to verify.

### Step 3: Add the DNS records at your registrar
1. Log into your registrar (GoDaddy / Namecheap / Cloudflare / etc.)
2. Find DNS management for `yourco.com` (usually called "DNS Settings," "DNS Management," or "Name Servers")
3. Add each record Instantly gave you. For each one:
   - **Type:** matches what Instantly says (A / MX / TXT / CNAME)
   - **Host / Name:** matches what Instantly says (often `mail` or `_dmarc.mail`)
   - **Value:** paste exactly what Instantly gave you
   - **TTL:** leave default (usually 3600 or "auto")
4. Also add a **DMARC** record manually (Instantly may give you this or may not):
   - **Type:** TXT
   - **Host / Name:** `_dmarc.mail`
   - **Value:** `v=DMARC1; p=none; rua=mailto:contact@yourco.example.com`
   - Why `p=none`: lenient during warmup; tighten to `p=quarantine` later
5. Save changes.

### Step 4: Wait + verify
1. DNS propagation takes 10–60 minutes. Don't panic if it's not instant.
2. After 30 min, go back to Instantly's setup tab and click **"Verify"** on the domain. Each record should turn green.
3. If any record is red after an hour, common fixes:
   - Did you paste the value exactly? (Stray spaces break DKIM.)
   - Did you put it on the right host? (DKIM lives at a specific selector, e.g., `instantly._domainkey.mail`.)
   - Wait another 30 minutes for propagation.

### Step 5: Create at least one inbox and start warmup
1. In Instantly, create at least one mailbox on the new subdomain: e.g., `the Founder@mail.yourco.com` or `outreach@mail.yourco.com`
2. Connect it (Instantly will sync via OAuth or SMTP).
3. Enable **automated warmup** — Instantly handles the rest. Your inbox will start sending tiny volumes to Instantly's warmup network for the next 30 days.
4. **Do not send any cold outreach yet.** The inbox isn't trusted by carriers until warmup completes.

---

## DAY 1 — Monday afternoon (60 min): 10DLC brand registration

### Step 6: Find the 10DLC / SMS section in Instantly
1. In Instantly, look for **"Phone Numbers"** or **"SMS"** or **"Calling & SMS"** in the sidebar (Hyper CRM tier unlocks this)
2. Click **"Set up SMS"** or **"Register for A2P / 10DLC"**

### Step 7: Submit Brand Registration
You'll see a form asking for:
- **Legal business name:** paste the exact value from Day 0
- **EIN:** paste it
- **Business address:** paste it
- **Phone number for the brand:** your business phone or your personal cell — anything you can answer
- **Website:** `yourco.com`
- **Vertical:** "Professional Services" (or "Technology" if Professional Services isn't an option)
- **Stock symbol:** leave blank / N/A
- **Brand alias:** "YourCo" (the short name people see)

Submit. Pay the **brand vetting fee** (~$15 one-time, charged by The Campaign Registry).

You'll see: **"Brand registration submitted."** Approval typically takes **1–7 business days**.

**Why it might fail:**
- EIN doesn't match legal name exactly. Triple-check the IRS letter.
- Address doesn't match what's on file with the state. Use the address from your Articles of Organization.
- Website not accessible. Make sure `yourco.com` loads (even a "coming soon" page is fine).

---

## DAY 2 — Tuesday (30 min): Engage a Florida attorney for FTSA review

This is the gate easiest to skip and most expensive to skip wrong. Do it before your first SMS goes to a Florida number.

### Step 8: Find a Florida TCPA / FTSA attorney
1. Search: *"Florida TCPA attorney"* or *"Florida FTSA defense attorney"*
2. Look for:
   - Florida-licensed
   - Specializes in TCPA / FTSA / telemarketing law
   - Has worked with B2B SaaS or services companies
3. Candidate firms (not endorsements, just well-known in the space):
   - **Holland & Knight** (FL big firm; has TCPA practice)
   - **Carlton Fields** (FL big firm; class-action defense)
   - **Akerman** (FL big firm; consumer protection group)
   - **Greenspoon Marder** (boutique-ish, FL-based)
   - Or any TCPA-focused boutique that's licensed in FL
4. Pick 2-3. Email each:

   > Subject: One-time FTSA compliance review — B2B AI services company, ~500–2000 SMS/mo
   >
   > Hi [name],
   >
   > I'm the founder of YourCo LLC, a Tampa-based AI implementation consultancy. We're standing up an outbound SMS program targeting B2B owner-operators (initially landscaping/hardscaping in FL). Volume will be ~500–2000 SMS/month, all B2B, sent via Instantly with 10DLC registration and STOP opt-out.
   >
   > I'm looking for a **one-time** review of our FTSA compliance posture before our first send. Specifically:
   > 1. Our reliance on the B2B carve-out when recipient phone is a mobile (common with owner-operators)
   > 2. Whether our STOP/opt-out mechanism is sufficient under FTSA
   > 3. Any specific filters or consent practices you'd recommend
   >
   > Can you scope a one-time engagement with a written deliverable? Approx. fee?
   >
   > Best, the Founder, YourCo LLC, founder@yourco.example.com

5. Expect quotes in the **$500–$2,000** range for a one-time written review. Pick the most responsive + clearest. Sign engagement letter, pay retainer, wait for the memo (usually 1–2 weeks).

---

## DAY 3 to ~DAY 10 — Wait for Brand Approval

While you wait:
- [ ] Warmup keeps running on the new inbox
- [ ] No cold sends from YourCo
- [ ] FTSA attorney does their review
- [ ] You can continue with Reilly's other build work

When Instantly notifies you **Brand: Approved**, move to next step.

---

## DAY ~10 (after Brand Approved) — Campaign Registration

### Step 9: Submit Campaign Registration
1. In Instantly's SMS section, you'll now see a **"Register Campaign"** button.
2. Pick **Campaign Type: "Mixed"** (covers outbound + inbound replies)
3. Use case: **"Lead Generation / Marketing"** (or whatever closest matches)
4. Provide **5–10 sample messages** that you'll actually send. Every sample MUST include:
   - **Sender identification** ("the Founder from YourCo —")
   - **STOP opt-out** ("Reply STOP to opt out")
   - **Real content** (the actual cadence text Polo / Reilly designed)
5. Monthly fee accepted ($1.50–$10/mo).
6. Submit. Approval takes **1–2 weeks**.

---

## DAY ~21+ (after Campaign Approved) — Test + Verify

### Step 10: Send a test SMS
1. In Instantly, send a single test SMS to your own phone.
2. Verify it arrives.
3. Reply **STOP** to your own message.
4. Confirm Instantly registers the STOP and marks your number as opted-out.

### Step 11: Wire the STOP handler
1. In Instantly, find the **Webhook** settings for SMS replies.
2. Add a webhook that fires on STOP / opt-out events to a URL Reilly can listen to (Instantly may have built-in support — check their docs first).
3. Reilly's job: when a STOP arrives, append the phone number to `agents/reilly/_suppression.md`.

### Step 12: Document the FTSA review
1. Save the attorney's written memo as `decisions/YYYY-MM-DD_ftsa-review.md`.
2. Note the date you can start FL sends and any constraints.

---

## After all this — Reilly's first real SMS

You're cleared. Reilly's first SMS send for landscaping can proceed, gated by:
- ✅ 10DLC brand approved
- ✅ 10DLC campaign approved
- ✅ FTSA written memo on file
- ✅ Warmup complete (30+ days of healthy sending)
- ✅ Test send verified
- ✅ STOP handler wired

---

## Status tracker (the Founder updates as he goes)

### Phase 1: Info gathering
- [ ] Legal business name confirmed
- [ ] EIN documented
- [ ] Business address documented
- [ ] State of incorporation documented
- [ ] Date of incorporation documented
- [ ] Domain registrar access confirmed

### Phase 2: Instantly + domain
- [ ] Instantly Hyper CRM subscription active
- [ ] `mail.yourco.com` subdomain added in Instantly
- [ ] SPF record live and verified
- [ ] DKIM record live and verified
- [ ] DMARC record live and verified
- [ ] First inbox created on `mail.yourco.com`
- [ ] Warmup running

### Phase 3: 10DLC Brand
- [ ] Brand registration submitted (date: _____)
- [ ] Brand vetting fee paid (~$15)
- [ ] Brand approved (date: _____)

### Phase 4: Florida FTSA legal review
- [ ] 2–3 attorney candidates emailed
- [ ] Engagement letter signed (firm: _____)
- [ ] Retainer paid
- [ ] Memo received (date: _____)
- [ ] Memo saved to `/decisions/`

### Phase 5: 10DLC Campaign
- [ ] Campaign registration submitted (date: _____)
- [ ] Sample messages submitted (5–10)
- [ ] Campaign approved (date: _____)

### Phase 6: Test + verification
- [ ] Test SMS sent and received
- [ ] STOP opt-out tested end-to-end
- [ ] STOP handler webhook wired to suppression list
- [ ] First Reilly SMS campaign cleared to launch

---

## Common failure modes
- **EIN ≠ legal name match:** brand vetting rejected. Fix: triple-check IRS letter, resubmit.
- **DNS propagation delay:** records show red. Fix: wait another 30 min, re-verify. Use [mxtoolbox.com](https://mxtoolbox.com) to confirm propagation independently.
- **DMARC too strict too soon:** your own legitimate sends get quarantined. Fix: keep `p=none` for 30+ days. Only tighten after reviewing aggregate reports.
- **Warmup interrupted:** if you stop and restart, you lose progress. Don't kill the inbox during the 30-day warmup.
- **Skipping FTSA review:** survive months without issue, then one plaintiff lawyer files class action. Not worth it. Do the review.

---

## Atlas integration

Atlas reads this file as part of his Monday-briefing workspace scan. Until all checkboxes are checked, the Monday briefing leads with "10DLC critical-path blocker" in the watchdog section. Update checkboxes as you complete steps.

---

## 10DLC Campaign content — registration answers (drafted 2026-06-13)

> Ready-to-paste answers for the campaign-content screens. Framed truthfully around **opt-in lead follow-up** (conversational/transactional), NOT cold marketing. Owner: the Founder (submits) + Rafi (compliance).

**Campaign description:**
> YourCo LLC uses this campaign to send conversational and transactional texts to leads and customers who contacted us or opted in through our website, yourco.com. Messages include replies to inquiries, demo links the user requested, confirmations and reminders for calls they booked, and follow-ups. Recipients provide their phone number and consent to receive texts. We do not send unsolicited marketing.

**Sample messages (brand + opt-out in each):**
1. `YourCo: Hi the Founder, thanks for requesting a demo. Here's the quick look at your AI front desk: https://yourco.com/d/abc — questions? Just reply. Reply STOP to opt out.`
2. `YourCo: Confirming your call with the Founder on Tue 6/24 at 10:00 AM ET. Reply C to confirm or R to reschedule. Reply STOP to opt out.`
3. `YourCo: Following up on your demo — happy to answer questions or set a quick call: https://yourco.com/call. Reply STOP to opt out.`
4. `YourCo: Reminder — your call with YourCo is tomorrow at 2:00 PM ET. Talk soon! Reply HELP for help, STOP to opt out.`
5. `YourCo: Thanks for reaching out! A team member will follow up shortly. Reply HELP for help, STOP to opt out.`

**Message contents:** ☑ embedded links · ☐ phone numbers · ☐ direct lending · ☐ age-gated.

**How do end-users consent? (the #1 rejection field):**
> End users opt in on yourco.com when they request a demo, book a call, or submit the contact form: they enter their phone number and check a box reading "I agree to receive text messages from YourCo about my request. Msg & data rates may apply; msg frequency varies. Reply STOP to opt out, HELP for help." Opt-in is not required to use the site or our services, and we never share or sell phone numbers. A screenshot of the opt-in form field is available at [URL].

**Opt-in keywords:** `START` (if supporting text-to-join; else blank).
**Opt-in message:** `YourCo: You're now opted in to receive messages about your request. Msg & data rates may apply; msg frequency varies. Reply HELP for help, STOP to opt out.`

### Compliance guardrails (do not skip)
1. **Consent description must match a real on-site checkbox.** ✅ Added to the Instant Employee capture form (`instant-employee.html`) — an unchecked SMS-consent box + the exact disclosure above, with consent recorded on the lead. Screenshot it for the `[URL]` reference at submission. (ROI calculator + configurator collect email only → no SMS consent needed.)
2. **This campaign = opt-in messaging only.** Cold SMS to sourced/scraped prospects (the outbound engine) is NOT covered and is a TCPA risk — keep cold outreach **email-first**; text only opted-in contacts. (Rafi gate.)
3. **Florida FTSA** is stricter than federal — the FTSA memo (Phase 4) stays on the critical path before FL sends.

---

> **Status (2026-08-25): blocked, root cause now diagnosed — and it is not what the file assumed.**
>
> The 2026-06-16 note said the pages were missing "because the site is staged/not deployed." That is
> **wrong in a way that matters: `yourco.com` IS live** (HTTP 200, verified 2026-08-25). What is
> live is a **separate, earlier single-page site this repo does not contain** — different `<title>`,
> different positioning, and **no privacy or terms page at all**. That is exactly why Joseph "could
> not find any."
>
> Probed the same day:
>
> | URL | Result |
> |---|---|
> | `/` | **200** — the earlier site |
> | `/privacy` · `/sms-terms` | **404** |
> | `/privacy.html` · `/sms-terms.html` | **308 → the extensionless path → 404** |
>
> The 308s are the host's global clean-URL rule firing on any `*.html` request. **They are not
> evidence the pages exist.** Nothing has been deployed for them to point at.
>
> **The drafted pages are real and nearly complete** — `agents/webb/pages/yourco-site-v2/privacy.html`
> and `sms-terms.html`, both carrying the required A2P elements (STOP, HELP, message-and-data-rates,
> frequency, and the carrier-mandated "not shared with third parties or affiliates for marketing"
> clause). They live in the **staged v2 site, which is not what is deployed.**
>
> **What was done 2026-08-25:** every remaining blank in both pages now names the person who must
> supply it (the Founder / Kemba / Ray), and the known-good contact email was filled.
>
> **What is left, and none of it is an agent's to do:**
> 1. **the Founder — the business address.** A2P vetting wants a physical address; the IRS-on-file one is
>    marked **SENSITIVE** in `business-info.md` ("treat like a partial SSN"). A registered-agent or
>    commercial-mailbox address is the usual remedy. **This is a privacy decision, not a form field.**
> 2. **the Founder — support phone**, and `privacy@` alias or swap to `the Founder@`.
> 3. **Kemba — hosting/analytics provider** and whether a cookie banner is needed.
> 4. **Ray/counsel — retention period, privacy regimes, the age threshold, and the FTSA review.** The
>    cold B2B SMS consent story remains the real FTSA risk.
> 5. **Deploy `/privacy` and `/sms-terms` so the URLs resolve**, then send Joseph the live URLs.
>    ⚠️ Publishing is the Founder's call and OtherVenture-gated; no agent deploys.
>
> ⚠️ **Deploying these two pages onto the current live site is worth a moment's thought**, because
> that site still says **"Two weeks. Fixed fee."** against the 2026-08-16 decision that the **Audit is
> free**. Attaching a fresh, counsel-reviewed privacy page to stale offer copy fixes the carrier
> blocker and leaves a live page contradicting current pricing.
