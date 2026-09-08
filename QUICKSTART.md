# Quick Start — Set Up Your AI SMB Company from Scratch

This guide walks you through cloning the template repo, configuring it for your business, and deploying your first agents.

**Timeline:** ~4-6 weeks end-to-end (most time is LLC filing + waiting for approvals; the technical setup is 2-3 days).

---

## Phase 1: Prerequisites & Repo Setup (1-2 hours)

### 1.1 Install required software

You'll need:

- **Git** — version control. [Download](https://git-scm.com/download)
- **Claude Code CLI** — the interactive development environment. [Install guide](https://docs.anthropic.com/claude-code/install)
- **Node.js** (v18+) — for frontend dev and tools. [Download](https://nodejs.org/)
- **Python** (3.9+) — for backend/automation. [Download](https://www.python.org/)
- **A text editor** — VS Code recommended, or use Claude Code
- **GitHub account** — to fork/clone the repo

Verify installations:

```bash
git --version
claude --version
node --version
python --version
```

### 1.2 Clone the repo with submodules

Clone this template repo to your machine:

```bash
git clone --recurse-submodules https://github.com/Kyleparker22/ai-smb-company.git my-company
cd my-company
```

Replace `my-company` with your business name (lowercase, no spaces).

### 1.3 Open in Claude Code

```bash
claude code
```

This opens the interactive development environment. Claude Code is where you'll:
- Edit files and write code
- Run the local dev server
- Test agents and loops
- Manage the repo

---

## Phase 2: Define Your Business (1-2 weeks)

Before you file your LLC or wire any infrastructure, lock in what you're actually building.

### 2.1 Answer the five core questions

In Claude Code, open `CLAUDE.md` and fill in the "What this business is" section:

1. **Company name** — Legal name for your LLC (e.g., "Acme Operations LLC")
2. **What you sell** — One sentence. Who do you serve, and what problem do you solve?
3. **The defensible part** — Why can't someone else just copy this? What's your edge?
4. **Who is the Founder** — Your name, email, location
5. **Co-founders/partners** — Names and ownership % (if any)

Example:

```markdown
## What this business is

**Status: MVP in development.** We are building an AI-powered sales assistant for small landscaping companies.

| Layer | Status | Notes |
|---|---|---|
| Entity / EIN / bank | ☐ in progress | Filing 2026-09-15 |
| Domain / email | ☐ planning | sales.ai domain reserved |
| Repo renamed, this file written | ✅ done | 2026-09-08 |
...

## What you sell

We deliver an AI agent that integrates with HubSpot and your supplier APIs to automate lead qualification, pricing, and proposal generation for landscape design firms.

## The defensible part

Integration depth with industry-specific supplier ecosystems (SiteOne, Ewing, Landscape Supply). Nobody else is wiring this for that vertical.

## Founder

Kyle Parker · kyle@sales-ai.com · Florida
```

### 2.2 Read the example company docs

Look at `_ORIGINAL-CLAUDE.md` (the source company that this template came from). It shows how detailed CLAUDE.md should be. **Don't copy it** — it's someone else's business — but use it as a template for density and specificity.

---

## Phase 3: File Your LLC (2-4 weeks)

Your business needs a legal entity before you can open a bank account, get an EIN, or sign vendor contracts. Use `SETUP/01_ENTITY-AND-MONEY.md` as your detailed guide.

### 3.1 Choose your state and registered agent

- **State:** Where are you based? (Typically where the founder lives)
- **Registered agent:** A real address in the state for legal service. Can be you (your address goes public) or a commercial agent ($50–300/yr for privacy)

### 3.2 File your LLC online

**For Florida (example):**

1. Go to [Florida's eSunbiz portal](https://dos.fl.gov/sunbiz/start-business/efile/fl-llc/)
2. File "Articles of Organization" online
3. Include your registered agent designation
4. Total cost: ~$125 (Articles $100 + Agent $25). Optional: certified copy ($30) and certificate ($5) — usually worth it.
5. You'll get confirmation by email within 1-2 business days

**For other states:** Search "[YourState] LLC formation" and follow the same pattern.

### 3.3 Get your EIN (Employer Identification Number)

Free, takes 10 minutes:

1. Go to [IRS EIN application](https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online)
2. Fill in your LLC info
3. You'll get your EIN immediately
4. **Save the CP-575 letter** — banks and vendors will ask for it

### 3.4 Open a business bank account

Take to your bank:
- EIN letter (CP-575)
- LLC formation document (from your state filing)
- Personal ID
- Your business name and address

Set up the account with your business name, NOT personal funds. This is critical for liability protection.

### 3.5 Document in the repo

Update `finance/legal-docs/business-info.md` with:

```markdown
# Business Entity Information

| Item | Value |
|------|-------|
| Legal Name | My Company LLC |
| State | Florida |
| Formed | 2026-09-15 |
| EIN | [your EIN] |
| Bank | Chase Business Checking, Account ending in 1234 |
| Domain | mycompany.com |
```

Commit this to git:

```bash
git add finance/legal-docs/business-info.md
git commit -m "Document LLC formation and banking info"
```

---

## Phase 4: Domain & Email Identity (1-2 days)

Your domain and email are how agents identify themselves. Wire these before any connectors.

Use `SETUP/02_IDENTITY-AND-EMAIL.md` as your guide.

### 4.1 Register a domain

Pick a domain and register it:

- **Registrar:** Namecheap, GoDaddy, Route 53, Cloudflare, or your preference
- **Recommendation:** Use Cloudflare for DNS (free, fast, integrates with email)
- **Cost:** $10–15/yr

For this example, we'll use `mycompany.com`.

### 4.2 Set up email

Two options:

**Option A: Gmail for Business (recommended for small teams)**

1. Get a business Gmail account: `founder@mycompany.com`
2. Configure forwarding to your personal email if you want
3. Use Gmail's SMTP for agents to draft emails

**Option B: Your domain's email provider**

If your registrar offers email hosting, use that instead. The key is that your *sender email* is `founder@mycompany.com`, not a personal address.

### 4.3 Update your git identity

On your machine, set your git user to your business email:

```bash
git config --global user.email "founder@mycompany.com"
git config --global user.name "Founder"
```

This ensures every commit carries your business identity.

### 4.4 Update CLAUDE.md

Add to the Founder section:

```markdown
## Founder

Your Name · founder@mycompany.com · [City, State]
```

And update the top of the file with your actual domain:

```markdown
# MY COMPANY — AI OS Workspace

> Your company description. Replace this.
```

Commit:

```bash
git add CLAUDE.md
git commit -m "Configure domain and email identity"
```

---

## Phase 5: Configure the Repo for Your Business (2-3 hours)

Now that you have a legal entity and domain, configure this template for YOUR company.

Use `SETUP/03_THE-REPO.md` as your guide.

### 5.1 Rename the repo folder

```bash
# If you haven't already
cd ..
mv ai-smb-company my-company
cd my-company
```

### 5.2 Update CLAUDE.md completely

Fill in these sections:

```markdown
# MY COMPANY — AI OS Workspace

## What this business is

[Your description + status table]

## What you sell

[Your product/service + ICP]

## The defensible part

[What's your competitive advantage?]

## How to work in this OS

[Keep the existing rules — they are the ones worth keeping]

## External-surface rules

[Keep these — they protect your brand]

## Folder map

[This is auto-generated; skip it]

## Founder

[Your name, email, location]
```

### 5.3 Delete example/template files

Remove files that don't apply to you:

```bash
# Remove the original company's material
rm -rf clients/sample-client
rm -rf Pre\ Build\ Ideas
rm -rf offerings/

# Keep the _EXAMPLE_ folders as reference, but don't use them
```

### 5.4 Create your first agent folder

Agents live in `agents/`. Create one for your first agent:

```bash
mkdir -p agents/my-first-agent
```

For now, just create a placeholder. We'll populate it in Phase 6.

### 5.5 Commit everything

```bash
git add -A
git commit -m "Configure repo for My Company: set domain, email, business details"
git push origin main
```

---

## Phase 6: Set Up Claude Code Environment (2-3 hours)

Your local development environment is where you build agents, test surfaces, and wire connectors.

Use `SETUP/04_CLAUDE-CODE-AND-MCP.md` as your guide.

### 6.1 Configure Claude Code settings

In Claude Code, check your settings:

```bash
claude config
```

This opens your configuration. Set:

- **Model:** Claude Opus 5 (recommended for agents)
- **Max tokens:** 4096 (default is fine)
- **Permissions:** Allow Bash, file ops, but review MCP connectors

### 6.2 Install Claude Code CLI globally

If not already done:

```bash
curl https://install.anthropic.com/claude-code | sh
```

### 6.3 Set up `.claude/launch.json`

This file registers all your local dev servers. It's already in the repo with ~100+ entries from the example company.

For your first surface, add an entry:

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "website",
      "runtimeExecutable": "python",
      "runtimeArgs": ["-m", "http.server", "8000"],
      "port": 8000,
      "url": "http://localhost:8000"
    }
  ]
}
```

This lets you start the dev server with `./show.sh` later.

### 6.4 Wire your first MCP connectors

MCPs (Model Context Protocol) are integrations with external services. Start with the three core ones defined in `.mcp.json`:

- **Slack** — post updates to a channel
- **Gmail** — draft emails
- **Calendar** — read/write calendar events

These are already in `.mcp.json`. To activate them, you'll need:

1. **Slack bot token** — create a bot in your Slack workspace
2. **Gmail API key** — enable Gmail API in Google Cloud
3. **Calendar OAuth** — enable Calendar API in Google Cloud

For now, **skip this** — we'll do it in Phase 8 when you deploy the runtime.

---

## Phase 7: Build Your First Agent (3-5 days)

Agents are the "digital employees" that run your business. Start with one.

Use `SETUP/06_THE-AGENTS.md` as your guide.

### 7.1 Define your first agent's job

Pick ONE job:

- Sales outreach
- Customer support triage
- Invoice processing
- Lead qualification
- Content generation

Write it down in `agents/my-first-agent/README.md`:

```markdown
# My First Agent

**Job:** Qualify inbound leads for our sales team.

**Inputs:**
- Lead form submissions
- LinkedIn profile links

**Outputs:**
- Qualified/unqualified decision
- Summary for sales team (draft email)

**Schedule:** Runs every morning at 9 AM ET

**Constraints:**
- Never sends emails (drafts only)
- Must include source + reasoning
```

### 7.2 Write the agent prompt

Create `agents/my-first-agent/prompt.md`:

```markdown
# Lead Qualification Agent

You are the lead qualification agent for My Company. Your job is to evaluate inbound leads and decide if they fit our ICP.

## Your ICP (Ideal Customer Profile)

- Landscaping companies with 5–50 employees
- Annual revenue $500K–$5M
- Using HubSpot or similar CRM
- Pain point: manual proposal generation

## Process

1. Read the lead form submission
2. Check the company size, industry, and tech stack
3. Score 1–10 on fit
4. Write a brief summary for the sales team
5. DRAFT (never send) an intro email if qualified

## Examples of qualified leads

[Include 2–3 real examples]

## Examples of unqualified leads

[Include 2–3 real examples]

## Rules

- If you're unsure, ask for clarification rather than guessing
- Always cite your sources (e.g., "from their website" or "from the form")
- Be respectful of leads even if unqualified
```

### 7.3 Test locally in Claude Code

Test your agent prompt in Claude Code:

```bash
claude -p agents/my-first-agent/prompt.md
```

This runs your prompt against the Claude model. Refine it until you're happy with the output.

---

## Phase 8: Deploy the Always-On Runtime (2-3 days)

The runtime is a VPS that runs your agents 24/7 on a schedule. Use `SETUP/05_THE-RUNTIME.md` as your detailed guide.

### 8.1 Get a VPS

Choose a provider:

- **Hostinger** — $4–8/mo (what the example company uses)
- **DigitalOcean** — $5–12/mo
- **Linode** — $5–24/mo
- **AWS** — $20–100+/mo

Requirements:

- Ubuntu 22.04 or 24.04 LTS
- 2GB RAM minimum
- SSH access
- Static IP

### 8.2 Connect to your VPS

```bash
ssh user@your-vps-ip
```

(If you set up Tailscale, use that for private network access.)

### 8.3 Set up the runtime environment

On the VPS, clone your repo:

```bash
git clone --recurse-submodules https://github.com/YourGithub/my-company.git ~/my-company-os
cd ~/my-company-os
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Claude Code CLI on the VPS:

```bash
curl https://install.anthropic.com/claude-code | sh
```

### 8.4 Configure the approval gate

The approval gate is a safety layer that prevents agents from sending emails, deleting files, or running arbitrary shell commands.

Copy the reference settings to your VPS:

```bash
cp runtime/headless-settings.reference.json ~/.claude/settings.json
sudo chown root:root ~/.claude/settings.json
```

Verify it denies dangerous operations:

```bash
cat ~/.claude/settings.json | grep -A5 "deny"
```

### 8.5 Add your first loop to systemd

A loop is a scheduled task that runs your agent repeatedly. Use the `add-runtime-loop` skill:

In Claude Code:

```bash
cd ~/my-company-os
claude -c "Use the add-runtime-loop skill to add my-first-agent"
```

This creates:

- `runtime/prompts/my-first-agent.md` — the stable prompt
- A systemd timer that runs it on your schedule
- Log output at `loops/_runtime/my-first-agent.log`

### 8.6 Verify the loop runs

```bash
sudo systemctl start my-first-agent.timer
sudo systemctl status my-first-agent.timer
journalctl -u my-first-agent.timer -f
```

---

## Phase 9: Wire Connectors (1-2 days)

Connectors are integrations with external services (Slack, Gmail, HubSpot, etc.). Wire them as needed.

Use `SETUP/04_CLAUDE-CODE-AND-MCP.md` and `.claude/skills/wire-credentialed-connector/` as your guides.

### 9.1 Slack connector

So your agents can post to Slack:

1. Create a Slack workspace (or use existing)
2. Create a bot: Workspace settings → Build → Create App → "From scratch"
3. Name it `my-company-bot`
4. Add OAuth scopes: `chat:write`, `channels:read`
5. Install the app to your workspace
6. Copy the Bot Token (starts with `xoxb-`)

Save it to your VPS:

```bash
echo "SLACK_BOT_TOKEN=xoxb-your-token-here" > ~/.acme/env
```

### 9.2 Gmail connector

So your agents can draft emails:

1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials (type: Desktop app)
3. Download the JSON credentials

This is auto-wired in Claude Code via the MCP in `.mcp.json`.

### 9.3 HubSpot connector (if you sell to HubSpot users)

1. Get a HubSpot account (free tier is fine)
2. Create a private app: Settings → Integrations → Private apps
3. Add scopes: `crm.objects.contacts.read`, `crm.objects.deals.read/write`
4. Copy your token

Save it:

```bash
echo "HUBSPOT_TOKEN=pat-your-token-here" >> ~/.acme/env
```

---

## Phase 10: Build Your First Dashboard (1-2 days)

Dashboards are how you monitor your business. The repo includes examples in `dashboard/`.

### 10.1 Check existing dashboards

Look at:

- `dashboard/uptime.py` — checks if loops are running
- `dashboard/spend.py` — tracks model costs
- `dashboard/leads.py` — shows your pipeline (example)

### 10.2 Create your first dashboard

Create `dashboard/my-company.py`:

```python
#!/usr/bin/env python3
"""
My Company Dashboard — status at a glance.
"""

import json
from datetime import datetime
from pathlib import Path

def main():
    print("\n=== MY COMPANY STATUS ===\n")
    
    # Check if first loop ran
    loop_log = Path("loops/_runtime/my-first-agent.log")
    if loop_log.exists():
        print(f"✅ My First Agent: last ran {loop_log.stat().st_mtime}")
    else:
        print("⏳ My First Agent: not yet run")
    
    # Check spend
    spend_file = Path("finance/token_spend.md")
    if spend_file.exists():
        with open(spend_file) as f:
            lines = f.readlines()
            print(f"\n💰 Model spend:\n{''.join(lines[-5:])}")

if __name__ == "__main__":
    main()
```

Run it:

```bash
python dashboard/my-company.py
```

---

## Phase 11: Set Up CRM & Tracking (1 week)

Once you have leads/customers, you need a CRM to track them.

Use `SETUP/07_CRM-HQ-AND-APP.md` as your guide.

### 11.1 Choose a CRM

- **HubSpot** — free tier, good for SMBs
- **Pipedrive** — sales-focused
- **Notion** — lightweight, free
- **Custom** — build on top of SQLite/CSV

### 11.2 Create your deal pipeline

If using HubSpot:

1. Create a deal board with stages:
   - Prospect
   - Qualified
   - Proposal
   - Won / Lost

2. Create custom fields:
   - Deal size
   - Industry
   - Pain point
   - AI agent recommended? (Yes/No)

### 11.3 Connect your CRM to the runtime

Wire HubSpot (or your CRM) as an MCP connector so agents can read/write deals.

---

## Phase 12: Launch! 🚀

### 12.1 Final checklist

- [ ] LLC formed and EIN obtained
- [ ] Domain registered and email configured
- [ ] CLAUDE.md filled in completely
- [ ] First agent prompt written and tested
- [ ] VPS deployed and runtime running
- [ ] First loop scheduled and executing
- [ ] Slack connector wired
- [ ] CRM set up and connected
- [ ] Dashboard showing status
- [ ] Git repo up to date on GitHub

### 12.2 Go live

1. Enable your first loop on production:

```bash
sudo systemctl enable my-first-agent.timer
```

2. Test it manually:

```bash
sudo systemctl start my-first-agent.timer
```

3. Verify output:

```bash
ls -ltr loops/my-first-agent/  # see the latest run
```

### 12.3 Monitor & iterate

Every morning, check:

- Dashboard status
- Loop logs for errors
- Slack posts from your agents
- Draft emails they've created
- Learnings written (if any)

Refine the agent prompt based on output.

---

## Troubleshooting

### "git clone fails with permission denied"

```bash
# Use HTTPS instead of SSH
git clone --recurse-submodules https://github.com/YourGithub/my-company.git
```

### "Claude Code can't find Python"

```bash
# Install Python and add to PATH, or use full path
/usr/local/bin/python3 -m pip install -r requirements.txt
```

### "Systemd timer won't run"

```bash
# Check timer status
sudo systemctl status my-first-agent.timer

# View logs
sudo journalctl -u my-first-agent.timer -f

# Verify the script exists
cat runtime/prompts/my-first-agent.md
```

### "My agent is drafting but not doing anything useful"

1. Read the prompt again carefully
2. Test in Claude Code with real data: `claude -p agents/my-first-agent/prompt.md`
3. Add examples to the prompt
4. Review the output logs in `loops/my-first-agent/`

---

## Next Steps

Once you have one agent running:

1. **Add a second agent** — follow the same pattern
2. **Wire more connectors** — integrate with your tools (Stripe, HubSpot, etc.)
3. **Build a client-facing surface** — dashboard, console, or white-label app
4. **Monitor & optimize** — track costs, latency, quality
5. **Scale to production** — handle more volume, more complexity

---

## Support

- **SETUP guide:** Read `SETUP/00_START-HERE.md` for the full architectural rationale
- **Skills library:** `.claude/skills/` has reusable procedures
- **Example company:** `_ORIGINAL-CLAUDE.md` shows how detailed things can get
- **Decisions log:** `decisions/` records why choices were made

Good luck! 🚀
