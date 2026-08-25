# Aspire API credential setup email — the Founder sends to Client Owner

**Status:** DRAFT — the Founder reviews and sends from founder@yourco.example.com.
Click-path verified against Aspire's official KB article ("APIs", Evolution Administration) 2026-08-07.
⚠️ If the Founder already sent the earlier HubSpot email with the Aspire paragraph: that paragraph had the WRONG path (said Administration → Configuration → Integrations). This email has the correct one — send it as the correction.

---

**To:** Client Owner
**Subject:** Same deal for Aspire — 3 minutes, needs your admin login

Client Owner —

Same 5-minute favor as the HubSpot one, this time in Aspire. This generates the API credential that lets the platform read your estimates and push quotes in. Needs whoever's the designated system admin in Aspire (you or Colton, most likely).

1. Log into Aspire.
2. At the **bottom of the left sidebar**, click the **Settings icon** (the little gear/person at the bottom, above Log Out).
3. In the menu that opens, click **Evolution Administration**.
4. You'll land on the **Admin** tab. In the left panel under **APPLICATION**, click **API**.
5. Click the blue **GENERATE** button.
6. It creates two things:
   - **Client ID** — always visible on that page.
   - **Secret** — **shown only this once.** Click the little **copy icon** next to the Secret box right away.
7. **Text me both** — the Client ID and the Secret. Don't email them. If the Secret gets away from you before you copy it, no stress — there's a **Regenerate** button on the same page; just send me the new one.

If you don't see Evolution Administration in that menu, your login isn't set as a system administrator — tell me who is (Aspire calls it a "company-designated system administrator") and I'll send them this.

the Founder

---
*Notes for the Founder: (a) values land in `clients/sample-client/platform/.env` as `ASPIRE_CLIENT_ID=` and `ASPIRE_CLIENT_SECRET=`, then delete the text; (b) Test button on the Integrations tab does a live token issuance against cloud-api.youraspire.com — green = wired; (c) regenerating the Secret later kills the old one, so if Client Owner ever hits Regenerate we need the new value.*
