# Website Visitors → multi-channel outreach (post-launch to-do)

> **Status: queued for when the website goes live.** Not actionable until `yourco.com` is deployed and getting traffic. Owner: **Reilly** (ops) + **Michelle** (copy) + **Rafi** (compliance gate). Captured 2026-06-15 so it's not forgotten.

## What it is
Instantly's **Website Visitors** feature de-anonymizes a portion of your site traffic — it identifies the company *and the person*, and returns **email + LinkedIn + (often) phone** for a large share of visitors who never filled out a form. Combined with Instantly's **"Views"** (which visitors looked at which pages, how engaged), you can reach only the genuinely-interested and skip the tire-kickers.

## Why it's worth doing (once live)
- **Highest-intent cold source there is.** Someone who visited our pricing/demo page is warmer than any scraped list — they came looking. (Still *cold* by our rule: no prior contact → Instantly campaign, promote to CRM on reply. Per `decisions/2026-06-15_prospect-data-architecture.md`.)
- **Multi-channel doubles the touchpoints.** Email **and** LinkedIn on the same lead → more likely to be seen, more likely to reply. This is the one place we get LinkedIn data *compliantly* (Instantly sources it; we don't scrape it).
- **"Views" qualification** keeps it lean — only work the leads who actually engaged.

## How it plugs into what we built
1. **Visitor identified** (Instantly) → email + LinkedIn + phone, with the pages they viewed.
2. Treated as a **cold, intent-qualified lead** → its own **"Site Visitors"** Instantly campaign. The intent signal = *"visited [page]"* → rides as a merge var (same pattern as Sadie's intent — `processes/outbound/intent-outreach.md`).
3. **Michelle** writes the site-visitor sequence: email opener references the visit ("saw you were looking at how we handle missed calls…"); the LinkedIn touch is a separate, lighter note.
4. **David** dedups against the CRM (never re-touch an existing relationship); **promote to CRM on reply.**

## The LinkedIn touch — stays compliant
Instantly *surfacing* a visitor's LinkedIn is fine (it provides the data). The LinkedIn *outreach* still follows Rafi's posture (`agents/rafi/social-platform-scraping-assessment.md`): no automation against LinkedIn — connection requests / DMs are sent **manually or via LinkedIn's own approved tooling**, human-paced, help-first. Email is the automated channel; LinkedIn is the manual second touch.

## Compliance gate (Rafi — must clear before turning this on)
- **De-anonymizing visitors is identifying people who didn't opt in.** GDPR/CCPA: needs a **lawful basis (legitimate interest)**, a **privacy-policy disclosure** that we use visitor-identification, and **honored opt-outs/deletion**. (Our staged privacy page must say this before we enable it.)
- **CAN-SPAM/CASL/ePrivacy** apply to the outreach (the existing send gate).
- EU/UK visitors: extra care — consider excluding or higher-bar consent.

## Cost + trigger
- Requires a **paid Instantly Visitors subscription** (upgrade when live).
- **Trigger to activate:** website deployed + getting real traffic + sending domains warmed + Rafi's privacy-disclosure clears. Until then: parked here.

## When the time comes (checklist)
- [ ] Website live + tracking installed (Webb).
- [ ] Privacy policy updated to disclose visitor identification (Rafi + Ray).
- [ ] Upgrade to paid Visitors tier.
- [ ] Create the "Site Visitors" Instantly campaign; Michelle writes the visit-aware sequence.
- [ ] Wire visitor leads → David dedup → campaign (same `--sadie-json`-style intent handoff).
- [ ] LinkedIn second-touch SOP (manual, help-first) for high-"Views" leads.
