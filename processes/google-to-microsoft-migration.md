# Google Workspace → Microsoft 365 migration (yourco.com)

> Started 2026-08-09 (the Founder). **Status: step 0 complete (survey), step 1 is the Founder's and not yet done.**
> Owner: the Founder (tenant, billing, DNS) · Kemba (connectors + runtime rewiring) · Rafi (approval gate).
> Rule of the whole document: **mail never breaks.** Every step before the MX cutover is reversible and
> zero-risk; the cutover itself is the only irreversible moment, and it happens *after* data is already moved.

## Step 0 — what's actually wired to Google (survey, done 2026-08-09)

**Verified at DNS:**
| Record | Current state |
|---|---|
| **MX** | `1 smtp.google.com` → **Google Workspace confirmed** |
| **DNS host** | `dns1/dns2.registrar-servers.com` → **Namecheap** (this is where every change below happens) |
| **DKIM** | ✅ present (`google._domainkey`, 2048-bit) |
| **SPF** | ❌ **MISSING — no `v=spf1` record on the domain at all** |
| **DMARC** | ❌ **MISSING — no `_dmarc` record** |

**Wired in the repo:**
| Surface | What depends on Google |
|---|---|
| `.mcp.json` | 3 servers: `slack`, **`gmail`**, **`calendar`** — two of three are Google |
| `runtime/headless-settings.reference.json` | The **approval gate** — allows 8 `mcp__gmail__*` tools, denies `send_email` / `delete_email` / `batch_delete_emails` |
| `runtime/prompts/` | **8 loop prompts name Gmail**: monday-briefing · inbox-triage · crm-autolog · open-loops-chaser · finance · finance-close · sales · advisor |
| `runtime/connectors.md` | Documents Gmail (read/draft/label, send+delete denied) and Calendar (read + write-holds, **verified live 2026-06-25** — Jim placed a real hold) |
| `clients/_internal-rollout.md` | Agent mailboxes on the corporate domain (e.g. `contact@yourco.example.com` — to provision) |

**Not affected — worth knowing before you worry about it:** cold outbound is insulated. Instantly sends from
**separate warmed sending domains**, not `yourco.com` (`clients/_internal-rollout.md`, `processes/outbound/sequence-copy.md`).
Nothing in this migration touches cold-email deliverability or warmup progress. Google-*data* dependencies
(YouTube Data API, Google News/Alerts RSS, Outscraper's Maps data) are unrelated to Workspace and stay as they are.

---

## The five traps (read before step 1)

1. **⚠️ The approval gate is provider-specific — this is the one that actually matters.** The deny rules name
   `mcp__gmail__send_email`, `mcp__gmail__delete_email`, `mcp__gmail__batch_delete_emails` *by exact tool name*.
   Add an Outlook MCP without rewriting them and the runtime gains **send and delete with no deny rule** — the
   always-on-≠-auto-send property that CLAUDE.md calls "proven in production" would be silently gone. **The
   deny-list must be rewritten and verified BEFORE any Outlook tool is enabled, not after.** Rafi signs off.
2. **⚠️ SPF and DMARC are missing today.** DKIM alone is not enough, and this is already hurting the domain
   before any migration. **Do not port the gap.** Exchange Online cutover is the moment to stand up all three
   correctly. This is worth doing *even if the migration stalls*.
3. **Sign-in-with-Google is the classic migration killer.** Any third-party service the Founder signed up for using
   "Sign in with Google" on a `@yourco.com` identity loses its login path when Workspace is cancelled —
   *after* the mail already works, so it surfaces late and looks unrelated. **Inventory these before step 6**
   (candidates to check: Slack, Granola, Instantly, Namecheap, Higgsfield, Descript, Vapi, Twilio, Hostinger,
   Outscraper, Canva, DocuSign, GitHub). Convert each to email+password or Microsoft SSO first.
4. **8 loop prompts break quietly.** A loop that can't reach Gmail doesn't necessarily fail loudly — it may
   just skip the inbox step and still post a briefing. Rewrite all 8 in the same pass, and watch the first
   Monday briefing after cutover specifically.
5. **Jim's calendar write access is live and verified.** Holds are being placed on the Founder's real calendar today.
   That capability has to be re-established against Microsoft Calendar, and re-verified the same way it was
   originally (place one real hold, confirm no email/no delete), not assumed.

---

## The runbook

Labels per CLAUDE.md: **[M365]** = Microsoft admin center · **[Namecheap]** = DNS · **[Mac]** / **[VPS]** = shell ·
**[Claude]** = mine, in this repo.

### Step 1 — stand up the tenant (the Founder only; nothing breaks)
- **[M365]** Buy a Microsoft 365 Business plan for `yourco.com`. **Business Standard** is the right tier
  (desktop Office + Exchange Online + Teams); Business Basic is web-only. Start with **1 seat** — agent
  mailboxes come later and each is a paid seat, so decide that when you get there, not now.
- **[M365]** Add `yourco.com` as a custom domain and take the **TXT verification record**.
- **[Namecheap]** Add that TXT record. **Do not touch MX yet.** Verification is invisible to mail flow.
- **Stop here and tell me it's verified.** Everything after this point has an order that matters.

> **I cannot do this step.** Creating the account and buying the licenses are actions I don't take on your
> behalf — and I have no Namecheap credentials. It's ~15 minutes of your time and it's the gate for everything else.

### Step 2 — mailboxes, before any mail moves (the Founder)
- **[M365]** Create `founder@yourco.example.com` in the new tenant. **The address does not change** — which is why
  the git-identity and hard-separation rules in CLAUDE.md are unaffected (still never `hello@`, never an
  OtherVenture address, on the Mac and the VPS both).
- Do **not** create the agent mailboxes yet (`reilly@`, etc.) — they're unprovisioned today and each is a seat.

### Step 3 — move the data while Google is still live (the Founder)
- Migrate mail, calendar, contacts. For a single mailbox the **Exchange Online IMAP migration** or a one-off
  PST export/import is enough; a third-party tool is overkill at this size.
- **Google Drive → OneDrive/SharePoint** is a separate job from mail. Google Takeout → upload is fine at this
  scale. Note what's actually in Drive first — this workspace is the system of record, so Drive may hold less
  than you'd assume.
- Verify the new mailbox looks right *before* cutover. Nothing is live yet; Google is still receiving.

### Step 4 — the cutover (the Founder; the only irreversible step, ~30 min of propagation)
- **[Namecheap]** Replace MX with Exchange Online's (`yourco-com.mail.protection.outlook.com`, priority 0
  — take the exact value from the M365 admin center, don't copy it from here).
- **[Namecheap]** Set all three auth records — this is the fix for trap #2:
  - **SPF:** `v=spf1 include:spf.protection.outlook.com -all` (one SPF record only, ever)
  - **DKIM:** enable in M365, add the two CNAMEs it gives you
  - **DMARC:** start at `v=DMARC1; p=none; rua=mailto:founder@yourco.example.com` — **`p=none` first**, read reports
    for two weeks, then tighten to `quarantine`. Going straight to `reject` is how people silently lose mail.
- **[Namecheap]** Remove the old Google MX and the `google._domainkey` DKIM record. Leave the
  `google-site-verification` TXT until step 6 (it may be load-bearing for Search Console).
- Send a test in **and** out, and confirm both. Then tell me — step 5 is mine.

### Step 5 — rewire the OS (mine, ~1 session, after step 4)
In this order, because the gate has to be correct before the capability exists:
1. **`runtime/headless-settings.reference.json`** — rewrite allow/deny for the Outlook tool names first.
   Deny `send`/`delete` equivalents explicitly. **Rafi verifies before anything else runs.**
2. **`.mcp.json`** — swap the `gmail` and `calendar` servers for the Microsoft equivalents.
3. **[VPS]** Provide auth on the host under the runtime user — host-only, can't be done from Cowork, and
   **the OAuth authorization itself needs an interactive session** (this one is currently non-interactive).
4. **8 loop prompts** rewritten in one pass.
5. **`runtime/connectors.md`** rewritten to the new reality; **CLAUDE.md** swept for "Gmail" (change-one-sweep-all).
6. Re-verify Jim's calendar write with one real hold, exactly as it was verified on 2026-06-25.
7. Watch the **first Monday briefing** after cutover before calling it done.

### Step 6 — decommission (the Founder, ≥30 days after cutover)
- Work the sign-in-with-Google inventory from trap #3 **first**.
- Keep Workspace paid and dormant for at least a month — it's cheap insurance and the only real rollback.
- Cancel, then remove the `google-site-verification` TXT.

---

## Open questions for the Founder (none block step 1)
- **Why now?** Not a challenge — it changes the plan. If it's cost, one Workspace seat vs one M365 seat is
  roughly a wash and this isn't worth a day. If it's because a client or the partners run on Microsoft, or
  because Conduit's spec already assumes **MS Graph** (`offerings/conduit/SPEC.md` names it in the stack),
  that's a real strategic reason and it argues for doing it properly rather than minimally.
- **Agent mailboxes:** every `@yourco.com` agent address is a paid M365 seat. Shared mailboxes are free
  and may be the better shape for agents that only draft. Decide at step 2, not before.
- **Timing against the beachhead:** this is a half-day of the Founder-time plus a session of mine, against one
  unsigned proposal. It is genuinely reversible up to step 4 — so starting step 1 today costs nothing and
  commits to nothing.
