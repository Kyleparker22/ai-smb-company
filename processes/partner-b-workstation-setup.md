# Partner B's workstation — operating yourco from his laptop

> Written 2026-08-11 for the Founder. Goal: Partner B sits down at his own machine and works the OS the way the Founder
> does — same second brain, same agents, same surfaces. This is the checklist and the honest list of
> what does *not* travel.

## The recommendation, in one place (2026-08-11)

**"Everything I can do, they can do" and "read-only on GitHub" cannot both be true.** Read-only means
Partner B can see and run everything and persist nothing: no commits, no writable local CRM, and every
agent that ends in a commit (`log-decision`, `log-build-cost`, the loops) runs and then fails at the
push. That is the right shape for a *review* phase and the wrong shape for an *operating* partner.

Resolve it by staging on an event that already exists rather than by picking one:

| Phase | GitHub | What they can do |
|---|---|---|
| **Now — OA unsigned, gate #14 🔴** | **Read** | See and run everything; work comes back through the Founder to land. Partner B is deciding whether to join, not yet operating. |
| **At OA signature** | **Write + branch protection on `main`** | Full parity. They commit and open PRs; nothing reaches `main` without review. Put the Founder and the VPS on the bypass list so the runtime keeps pushing on its timers. |

Mike is the sharper version of the same question: at 15% with his contribution still unrecorded (D12
open), full access is being granted for a role nobody has written down.

**Four separate axes — do not conflate them.** The Claude plan is the *tool*. The GitHub org is the
*brain*. Tailscale is the *live surfaces*. Credentials are their own axis and travel with none of the
others. Getting all four right is what "works exactly like the Founder" actually means.

**On the plan: separate individual subscriptions, not Team — decided 2026-08-11 (the Founder).** Partner B buys
his own; the Founder keeps Max 20x untouched.

The reason this beats Team here is specific to how yourco is built: **the shared context lives in the
repo, not in a Claude workspace.** `CLAUDE.md` is the boot context, the skills are in `.claude/skills/`,
the decisions and learnings are markdown. A shared Claude workspace would add shared *Projects* — which
yourco does not use as its system of record — so the thing Team is for is already solved by git. What
Team would still add is central billing, SSO, admin controls and one place to read usage: real, but
nice-to-have at three people, and not worth putting the Founder's 20x allowance at risk to get.

**Partner B does not need Max 20x.** He is reading, running agents and reviewing, not driving day-long
build sessions. Start him on the lowest tier that runs Claude Code comfortably and move up if he hits
limits — buying 20x on day one is buying an allowance for work he is not doing yet. Two Max 20x plans
is $400/mo against a company with $0 revenue.

Revisit Team when there is a reason that is not context-sharing: expensing it to the company rather
than personal cards, or a fourth person.

---

## The one thing to understand first

**The "Obsidian second brain" and the yourco repo are the same thing.** This workspace is a git repo
*and* an Obsidian vault — `.obsidian/` is committed, so the vault config, plugins and graph settings
travel with the clone. There is no separate Obsidian sync to set up, and **there must not be**: git is
already the sync layer between the Founder's Mac and the VPS runtime (`processes/git-sync.md`), and adding
Obsidian Sync on top would give two systems authority over the same files and guarantee conflicts.

**This is now enforced in the config, not just stated here (2026-08-09).** `.obsidian/core-plugins.json`
shipped with `"sync": true` — Obsidian's own default, never a decision anyone made — which meant the
committed config told every clone that Sync was on while this page said it must not be. It is now
`"sync": false`. Because that file is git-tracked, a future toggle shows up as a **diff** instead of
drifting silently, so the rule is checkable rather than merely written down.

**Why not just use Sync?** It buys three things and we already have two of them better: cross-machine
sync (git, with atomic commits, real history and the repo lock) and version history (git). The third —
reading and editing this markdown on a phone in Obsidian — is the only real gap, and it does not survive
the cost: Sync writes on its own schedule while the VPS runtime commits and pushes ~20 loop artifacts a
day into the same files, so you get races against `pull --rebase` and `file (conflicted copy).md`
siblings landing in the repo. The phone path we actually use is Slack (`runtime/slack-channels.md`, the
`#yourco-<agent>` channels) plus Tailscale/ssh (`runtime/phone-access.md`), with HQ as the readable view.
**If you want Obsidian Sync for personal notes, run it on a separate vault** — never on this repo.

So: **share the GitHub repo and Partner B has the brain.** Everything else below is access to the things
the repo *points at* but does not contain.

---

## 1 · Claude — read this before buying anything

⚠️ **There is currently no Claude Enterprise account to add Partner B to.** The expense ledger
(`finance/expenses.md`, 2026-07-27, receipt #2700-4256-4000) shows the plan as **Claude Max 20x at
$200/mo**, which is an **individual** plan with no seat management. "Add Partner B to Enterprise" cannot be
done as stated — there is nothing to add him to.

Three ways forward, in the order they probably make sense:

**Claude Team's published shape** (claude.com/pricing, checked 2026-08-11): teams of **2–150**;
**Standard seat $20/mo annual, $25/mo monthly**; **Premium seat $100/mo annual, $125/mo monthly**;
seat types can be **mixed and matched**; includes **Claude Code and Claude Cowork**, central billing,
SSO, admin controls for connectors, enterprise deployment for the desktop app, and enterprise search.

⚠️ **Team Premium is not equivalent to Max 20x.** Max 20x is 20× Pro usage for $200/mo. Team Premium
is a materially smaller allowance per seat — third-party comparisons put it near 6× Pro, and Anthropic
does not publish the multiplier. **Moving the Founder from Max 20x to a Team Premium seat is a usage
downgrade**, and the Founder is the heaviest user in the company by a wide margin.

| Option | What it gets | What it costs |
|---|---|---|
| **Keep the Founder on Max 20x; Partner B buys his own** | the Founder's limits untouched. Fastest — Partner B works within the hour. No central billing, no admin, no SSO. | $200 + whatever Partner B's plan is |
| **Team, mixed seats** — the Founder Premium, Partner B Standard | Central billing (off the Founder's personal card), SSO, admin controls, one company account. Cheaper than today. | ~$120–150/mo total — but the Founder drops from 20× to roughly 6× |
| **Team + keep the Founder's Max** | the Founder keeps 20×; the company still gets seats, billing and admin. | ~$220–225/mo; two subscriptions to reconcile |
| **Enterprise** | See below — governance machinery for regulated orgs | Contact-sales; wrong shape at three people and $0 revenue |

**Enterprise — assessed 2026-08-11, and the answer is no, for now.** Anthropic lists it as
*contact sales* with no published price. What it adds **over Team** is, in their words: admin-set user
and org spend limits · role-based access with fine-grained permissioning · **SCIM** · **audit logs** ·
compliance API for observability and monitoring · custom data retention controls · network-level access
control · **IP allowlisting** · **HIPAA-ready offering** · Claude Security (beta). Everything else
yourco would actually use — SSO, domain verification, central billing, admin controls, enterprise
desktop deployment, usage analytics, org-wide skills — is **already in Team**.

That list is an IT department's list. SCIM provisions users from an identity provider yourco does not
have; IP allowlisting and network access control assume a corporate network; audit logs answer to a
compliance function that does not exist. Third-party sources put Enterprise at a **20-seat minimum**
(some say 50) at roughly **$60–150/seat** — call it **$1,200–3,000/mo floor**, against a company with
$614/mo of fixed burn, $0 revenue, and a Conservative case that already breaches its $50,000 injection
by $11,155. It would be the largest line in the book, for seventeen empty seats.

**What would change the answer** — and it is worth writing down, because yourco's own moat pitch is
built on exactly these controls: the first client engagement carrying **regulated data**. Conduit
(IEN immigration, heavy PII) and yourco Care (health-adjacent) are both specified, both counsel-gated,
and both would put a **BAA/DPA** and an audit trail on the table. On the day one of those signs,
HIPAA-readiness and audit logs stop being vanity and start being a contract requirement. Revisit then,
not before.

**Verify in the console before acting** — the ledger is a receipt, not the account: claude.ai →
Settings → Billing. Also confirm with Anthropic what happens to existing **chat history and Projects**
when a personal account joins a Team workspace; a Team workspace is a different space from a personal
one, and that is the concrete "will I lose anything" risk rather than features.

**the Founder must do this himself.** Buying plans, adding users and changing account settings are not things
an agent does on his behalf.

---

## 2 · The repo and the brain — the actual sharing step

⚠️ **Read-only is not possible on the repo as it stands.** `yourco-os` sits in the Founder's *personal* GitHub
account, and GitHub's own documentation is explicit: *"Collaborators can't have read-only access to
repositories owned by a personal account… In a private repository, repository owners can only grant
write access to collaborators."* Their stated remedy is the one below.

**Move the repo to a GitHub Organization first.** Free, ~10 minutes, and it is the right end state
anyway — an org-owned repo is *company* property rather than an asset sitting in one member's personal
account, which is a question the OA will otherwise have to answer.

> ✅ **DONE 2026-08-11.** The org is **yourco** and the repo is **yourco/yourco-os**
> (private). the Founder's Mac remote is updated and verified. **Still outstanding: the VPS remote (§4)
> and adding Partner B (§5).** Two traps this run actually hit, kept here because they will recur on
> the next repo: the transfer dialog silently renamed the repo to match the org (it landed as
> `yourco/yourco` and had to be renamed back with
> `gh repo rename yourco-os --repo yourco/yourco`), and the remote was updated *before*
> the transfer, which broke every push until it was pointed back.

**Do it at a quiet moment.** The runtime pushes on timers (the Monday cluster at 07:40–07:55 ET, plus
the weekday loops). A transfer mid-push is recoverable but noisy — pick a window when nothing is due.

1. **Create the organization.** github.com → **+** (top right) → **New organization** → **Free**.
   Name it something that is the *company*, not the repo — `yourco` reads correctly for years;
   `yourco-os` will look wrong the moment there is a second repo. Set the org email to
   `founder@yourco.example.com` — never a personal or OtherVenture address.
2. **Transfer the repo.** Go to `github.com/founder22/yourco-os` → **Settings** → scroll to
   **Danger Zone** → **Transfer ownership**. Type the new owner (the org) and the repo name to confirm.
   Issues, stars, watchers, and history all follow it.
   ⚠️ **Do steps 1 and 2 before touching any remote.** Pointing a clone at an org repo that does not
   exist yet just breaks the clone.

   ⚠️ **Never paste `<org>` into a shell.** `<` is input redirection in bash and zsh, so
   `https://github.com/<org>/...` aborts with `no such file or directory: org` before anything runs.
   Set a variable on its own line and edit that one word instead.

3. **Update the remote on the Founder's Mac** — replace `yourco` with the real org name:
   ```bash
   ORG=yourco
   cd "/Users/you/Documents/Claude/Projects/YourCo LLC - AI"
   git remote set-url origin "https://github.com/$ORG/yourco-os.git"
   git remote -v && git pull --rebase
   ```
4. **Update the remote on the VPS** — the step that gets forgotten, and the one that matters most,
   because the VPS pushes on a schedule with no human watching:
   ```bash
   ssh user@your-vps
   ```
   then, on the VPS:
   ```bash
   ORG=yourco
   cd ~/yourco-os
   git remote set-url origin "https://github.com/$ORG/yourco-os.git"
   git pull --rebase && git push        # prove the credential still works
   ```
   ⚠️ **Verify that push actually succeeds.** GitHub redirects the old URL for fetches, so a broken
   credential can hide for hours. If the VPS authenticates with a **fine-grained** personal access
   token scoped to `founder22/yourco-os`, that token stops working the moment the repo moves and
   must be reissued for the org. A classic token with `repo` scope keeps working as long as the Founder is an
   org owner.
5. **Add Partner B with the Read role.** Org → **People** → **Invite member** → choose **Member**, then
   repo → Settings → Collaborators and teams → set his access to **Read**. Alternatively add him
   directly on the repo as an **outside collaborator** with **Read** — that keeps him out of org-wide
   settings entirely and is the tighter option while the OA is unsigned.
6. **Verify from his side, not yours.** Have him clone and then attempt a push. The clone should
   succeed and the push should be refused. Access you have not seen fail is access you have not
   confirmed.

Then:

5. **Partner B clones it.** Note it is a ~380 MB history, so the first clone is not instant:
   ```bash
   git clone https://github.com/yourco/yourco-os.git
   ```
6. **He opens the clone as an Obsidian vault** — Obsidian → *Open folder as vault* → point at the
   cloned folder. The vault config is already in the repo; he configures nothing.
7. **He pulls to stay current**, and that is the whole of his git workflow:
   ```bash
   git pull --rebase
   ```
   the Founder's Mac and the VPS keep pushing; Partner B's clone follows. He never needs
   `commit-scoped.sh`, and the two-writer conflict problem never arises, because there is still only
   one writer at each end.

**Claude Code then works on his machine with zero extra setup**: `CLAUDE.md` is the boot context, it
loads automatically from the repo root, and every skill in `.claude/skills/` comes with the clone. He
can read everything, run every agent, and generate work locally — he simply cannot push it back.

**What read-only actually costs him, and how he gets around it.** Anything he wants to *keep* has to
come back through the Founder: he sends the file or the diff, the Founder commits it. For a review-and-decide phase
that is the correct shape. Two specific frictions to expect:

- **He cannot edit the CRM locally.** The CRM writes `crm/data.json` and commits on save, which will
  fail on his clone. He must use the **VPS-hosted CRM** over Tailscale (§4) — which is the right answer
  regardless, since it keeps one copy and one writer.
- **Any agent that commits will fail on his machine.** Loops and skills that end in a commit
  (`log-decision`, `log-build-cost`, the runtime loops) will run and then fail at the push. That is
  loud rather than silent, so nothing is lost — but he should know it is expected, not broken.

If he later needs to contribute directly, the smallest change is to raise him from **Read** to
**Write** in the org — at which point `processes/git-sync.md` becomes required reading, especially
`commit-scoped.sh` over `git add -A`.

---

## 3 · The surfaces — CRM, HQ, demos

They are served from the repo, so they work off the clone with `python3` installed:

```bash
./show.sh
```

or start a named server from `.claude/launch.json` (CRM :8790, HQ :8791). **Never guess a port** —
read `launch.json` or use the `show-surface` skill.

⚠️ **The CRM writes to `crm/data.json` and commits.** With two people editing it, whoever pulls last
wins a merge conflict on a JSON file, which is unpleasant. Two options: agree that only one person
edits the CRM at a time, or have Partner B use the **VPS-hosted** CRM over Tailscale (§4) so there is one
writer and one copy. **The hosted one is the better answer** and is what §4 sets up.

---

## 4 · The runtime — Tailscale and the VPS

> ✅ **Verified 2026-08-11 — tailnet access does NOT grant shell access.** The VPS binds the CRM
> (`:8790`) and dashboard (`:8791`) to the **Tailscale IP only**, so a tailnet member reaches exactly
> those two and nothing else useful. `sshd` listens on `:22`, but **Tailscale SSH is not enabled** and
> login is gated by `~/.ssh/authorized_keys`, which holds one key. Partner B on the tailnet cannot get a
> shell unless his key is deliberately added — which is the staging decision below, and it stays
> closed for now.
>
> Tailscale's **free Personal plan covers 6 users**, so the Founder + Partner B + Mike fit with room. Nothing to
> buy.

The always-on OS lives on the VPS, and the hosted CRM and dashboard are the shared, single-writer
copies. To reach them Partner B needs to be on the tailnet.

1. the Founder invites Partner B to the yourco **Tailscale** tailnet (admin console → Users → Invite). The
   tailnet identity today is `founder@yourco.example.com`; Partner B joins with his own yourco address.
2. Partner B installs Tailscale on his laptop and phone and signs in.
3. He then has:
   - **CRM** → `http://10.0.0.1:8790`
   - **Dashboard** → `http://10.0.0.1:8791`
   - **SSH** → `ssh user@your-vps` (keyless — Tailscale authenticates)
4. Full cheat-sheet: `runtime/phone-access.md`.

⚠️ Decide deliberately whether Partner B gets **SSH to the runtime box**. Tailnet access for the two web
apps is low-risk. Shell on the VPS is the machine that runs every loop, holds every credential, and
pushes to `main` — that is a different level of trust, and it is reasonable to stage it behind the OA.

---

## 5 · Email and identity

Partner B needs `contact@yourco.example.com` before steps 2.4 and 4.1 are correct.

⚠️ This collides with an open decision: `decisions/2026-08-09_google-to-microsoft-migration.md`.
Provisioning him a Google Workspace mailbox now means migrating it days later. **Check where that
migration stands before creating the account**, and create it in whichever tenant is going to survive.

---

## 6 · What does NOT travel with the clone — the honest list

A fresh clone is **not** a working copy of the Founder's machine. These are deliberately absent:

- **Every credential.** Twelve `runtime/*.env` files (Slack, Twilio, Instantly, Firecrawl, Anthropic
  admin, YouTube, Recraft, Yelp and more) are gitignored and stay that way. Without them Partner B can
  read and write every document and run the CRM and HQ, but **no connector will work** on his machine.
  If he needs one, it gets provisioned per `.claude/skills/wire-credentialed-connector/` —
  **secrets never go through chat**; anything pasted into a transcript gets rotated.
- **MCP connector authorizations.** Gmail, Calendar, Slack, Granola and the rest are authorized
  per-user. Partner B authorizes his own; the Founder's do not transfer.
- **The Claude subscription.** §1.
- **Tailnet membership.** §4.
- **`.obsidian/workspace.json`** — gitignored on purpose, since it is per-machine window state. His
  panes will look different; nothing is broken.

---

## 6b · "Claude + the repo" is most of it, but not all of it

The honest check on *"he'll have everything he needs, correct?"* — **information and context: yes,
completely.** The repo is the whole brain, `CLAUDE.md` boots automatically, and every skill comes with
the clone. He can read every document, run every agent, and ask anything about the company.

**Four things a Claude subscription plus a clone does not give him**, in the order he will hit them:

1. **Credentials** — twelve gitignored `runtime/*.env` files. Without them no connector functions:
   Slack, Twilio, Instantly, Firecrawl, YouTube, Recraft, Yelp, the Anthropic admin key. He can *read*
   every agent that uses them and run nothing that touches the outside world.
2. **MCP connector authorization** — Gmail, Calendar, Slack, Granola, Vibe, Descript, Higgsfield are
   authorized per person inside Claude. the Founder's do not transfer. And Partner B cannot authorize the yourco
   ones until he is a *member* of those services, which is a chain: `contact@yourco.example.com` exists →
   he is added to the Slack workspace and the mail tenant → then he authorizes.
3. **Tailscale** — without it, no hosted CRM, no hosted dashboard, no VPS.
4. **Write access** — by the Founder's own choice he is Read-only for now, so he can produce work but not
   land it. That is deliberate and staged on OA signature (see the table above), but it does mean
   "everything the Founder can do" is not yet literally true.

The first three are provisioning tasks with a clear owner and no blocker except sequence. The fourth
is a governance decision that is already made.

## 7 · Order of operations for today

1. Check the Claude plan in the console. If Max, decide Team vs. Partner B-buys-his-own.
2. Create `contact@yourco.example.com` — in the tenant that survives the Microsoft migration.
3. **Create the GitHub org and transfer `yourco-os` into it** — read-only is impossible until this is
   done. Update the remote on the Mac *and* the VPS.
4. Add Partner B with the **Read** role. He clones and opens it as an Obsidian vault.
5. Invite him to Tailscale so he uses the **hosted** CRM rather than a second local copy — with
   read-only he cannot run a writable local one anyway.
6. Defer VPS shell access and credential provisioning until there is a reason and a signed agreement.

---

## The governance note, stated once

There is **no NDA and no signed operating agreement** on file — `finance/legal-docs/` holds a v5 OA
draft with three unsigned blocks and Ray's review; counsel gate #14 is 🔴 and D10/D11/D12 are open.
This checklist hands a prospective partner the complete company: client data, financial model, pipeline,
strategy, and the path to every credential.

That may well be the right call — the Founder is walking Partner B through everything precisely so he can decide
whether to join, and a partner who cannot see the company cannot evaluate it. But it should be a
decision rather than a side effect of a setup checklist. The cheap mitigation, if wanted, is a one-page
mutual NDA signed before step 3, which does not slow anything down by more than an hour.
