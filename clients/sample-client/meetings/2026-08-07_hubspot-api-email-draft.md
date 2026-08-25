# HubSpot private-app setup email — the Founder sends to Client Owner

**Status:** DRAFT — the Founder reviews and sends from founder@yourco.example.com.

---

**To:** Client Owner
**Subject:** 5-minute HubSpot thing — needs your admin login

Client Owner —

One quick thing I need from your side so the platform can talk to your HubSpot — takes about 5 minutes and needs whoever has admin access (probably you). This creates an "app key" for me; it doesn't change anything about how you guys use HubSpot.

1. Log into HubSpot, click the **gear icon** (Settings) in the top right.
2. In the left sidebar, scroll down to **Integrations** → click **Private Apps**.
3. Click the orange **Create a private app** button.
4. On the **Basic Info** tab, name it: **Sample Client Design Studio**. Description can be blank.
5. Click the **Scopes** tab → click **Add new scope** (or just use the search box). Search for and check these — exactly these, nothing else:
   - **crm.objects.contacts** — check both **Read** and **Write**
   - **crm.objects.deals** — check both **Read** and **Write**
   - **crm.objects.companies** — check **Read** only
6. Click **Create app** (top right) → it'll warn you about keeping the token safe → click **Continue creating**.
7. It shows you an **access token** (starts with "pat-"). Click **Show token**, then **Copy**.
8. **Text me the token** — don't email it (tokens in email threads live forever). Just paste it in a text to me and I'll take it from there.

That's it. If HubSpot won't show you the Private Apps page, it means your login isn't a Super Admin — tell me whose is and I'll send them this same list.

While you're in the texting mood: the SiteOne, Ewing, Latham, and Kirk Davis logins too if you haven't sent them yet, and I still need the Aspire one from that list I sent — in Aspire it's **Administration → Configuration → Integrations → API**, create an API credential, and text me the Client ID and Secret it gives you.

the Founder

---
*Notes for the Founder: (a) token arrives by text → goes straight into `clients/sample-client/platform/.env` as `HUBSPOT_TOKEN=pat-...`, then delete the text; (b) after landing it, hit Test on the Integrations tab — it verifies both the token AND the scopes, so if Client Owner missed a checkbox you'll know exactly which one.*
