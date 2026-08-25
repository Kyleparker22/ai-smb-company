# Partner B — day one

> Hand this to Partner B. Written 2026-08-11, verified against the live docs the same day.
> the Founder's side of the setup is `processes/partner-b-workstation-setup.md`; this is only what Partner B does.
>
> **macOS.** GitHub username `Klin10p`, invited with **Read** on `yourco/yourco-os`.
> Tailscale invite sent to his **Gmail** — he must sign in to Tailscale with that same Gmail.
>
> Everything below is run in **Terminal** (⌘-Space, type "Terminal", Enter). About 30 minutes,
> most of it waiting on downloads.

## What you're getting

The yourco repo is two things at once: a **git repository** and an **Obsidian vault**. It holds the
whole company — strategy, the financial model, client work, every decision and why it was made, and
the agents that run the business. Cloning it gives you all of it.

You have **read access**: see everything, run everything, ask Claude anything about the company. You
cannot push changes back — anything worth keeping, send to the Founder and he lands it. That is deliberate for
now and changes when the operating agreement is signed.

---

## 1 · Accept the GitHub invite

Check email for the GitHub invitation, or go to https://github.com/notifications.
**The invite expires in 7 days.** You need a free GitHub account first if you don't have one.

## 2 · Install the command-line basics

**Git** — paste this and press Enter. A dialog appears; click **Install** and wait a few minutes:

```bash
xcode-select --install
```

If it says *"command line tools are already installed"*, you're done with this step.

**Homebrew** — the package manager the next steps use. It will ask for your Mac password and print
two extra commands at the end under "Next steps":

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

⚠️ **Run the two commands Homebrew prints at the end.** They add `brew` to your PATH. Skipping them
is the single most common way this step appears to work and then doesn't. Verify:

```bash
brew --version
```

## 3 · Clone the repo

GitHub's CLI handles private-repo login without you generating any tokens:

```bash
brew install gh
```

```bash
gh auth login
```

Answer the prompts: **GitHub.com** → **HTTPS** → **Yes** (authenticate Git with your GitHub
credentials) → **Login with a web browser**. Copy the one-time code it shows, press Enter, and approve
in the browser that opens.

Then clone — this is ~380 MB of history, so give it a few minutes:

```bash
cd ~/Documents && gh repo clone yourco/yourco-os
```

**To get updates later**, run this at the start of any working session:

```bash
cd ~/Documents/yourco-os && git pull --rebase
```

## 4 · Open it in Obsidian

Download and install Obsidian: https://obsidian.md/download

Open it → **Open folder as vault** → choose `~/Documents/yourco-os` → **Open**.

If it warns about trusting the vault, choose **Trust author and enable plugins**.

Nothing to configure. The vault settings are in the repo, so it opens looking the way the Founder's does.

## 5 · Claude Code

**First, a paid plan.** Go to claude.ai → Settings → Billing. **Claude Code requires at least Pro —
the free plan does not include it.** Start on the smaller tier; moving up later takes a minute, and
there's no reason to buy a large allowance before you know your usage.

**Install it:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Close Terminal and open a new window, then confirm it worked:

```bash
claude --version
```

You should see a version number. If you get `command not found`, run `claude doctor` — but a fresh
Terminal window fixes it most of the time.

**Start it inside the repo** — this part matters, it must be run from that folder:

```bash
cd ~/Documents/yourco-os && claude
```

The first run opens a browser to log in with your Claude account. After that you're in.

That's the whole setup. `CLAUDE.md` at the repo root loads automatically as Claude's boot context, so
it already knows what yourco is, how it operates, and every rule it works under. Ask it anything:

- *"What is yourco's pricing?"*
- *"Why did we choose the audit-first motion?"*
- *"Where does Sample Client stand and what's blocking it?"*
- *"What are the biggest risks in the business plan?"*

It answers from the repo, not from guesswork.

## 6 · Tailscale — the live CRM and dashboard

Tailscale is a private network. It is how you reach yourco's live systems without any of it being
exposed to the internet.

Download and install: https://tailscale.com/download/mac

Sign in **with the Gmail address the Founder sent the invite to** — not any other account, or you'll create
a separate empty network. Accept the invitation.

Once connected, open these in a browser:

- **CRM** → http://10.0.0.1:8790
- **yourco HQ dashboard** → http://10.0.0.1:8791

These are the *shared, live* copies on yourco's server. Use these rather than starting local ones, so
there is one set of data and one writer.

---

## What to read, in order

1,033 markdown files is not a reading list. This is:

1. **`START-HERE.html`** — in the repo root, open in a browser. The one-page tour.
2. **`CLAUDE.md`** — the company in one page: what yourco is, the moat, how it operates.
3. **`01_company.md`** — the long version of the same.
4. **`loops/_audit/2026-08-09_full-business-audit.md`** — read this third, deliberately. It is the
   company's own account of what is *not* working. The house rule is that bad news leads; this is that
   rule applied to the whole business.
5. **`06_business-plan.md`** — the plan and the numbers, every assumption stated.
6. **`decisions/`** — skim the filenames, read whatever you want the reasoning behind. Every settled
   call is here with its alternatives and what would reverse it.

Then `processes/partner-b-walkthrough-schedule.md` — the session-by-session arc the Founder is walking you
through, with what to open for each domain.

---

## What won't work, and why that's expected

- **Connectors are dead on your machine.** Slack, Gmail, Twilio, the outreach tools — those
  credentials are deliberately not in the repo. You can read every agent that uses them and run
  nothing that reaches the outside world. Ask the Founder if you need one wired.
- **Anything ending in a commit will fail at the last step.** Some agents finish by saving to the
  repo; with read access that push is refused. The work still exists in your folder — send it to the Founder.
- **Don't run the CRM locally.** It saves by committing, which will fail. Use the hosted one above.

None of these mean you've broken something.

---

## The one rule that matters most

Nothing in this repo goes outside yourco. It holds client work, an unsigned operating agreement,
financial models, and a pipeline of real people at real companies. The company's external launch is
still gated and **none of this is public.** If something looks worth sending to someone, that's a
conversation with the Founder, not a judgment call.
