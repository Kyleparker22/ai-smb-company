# 02 — Identity: domain, email, workspace

> **Build step 02.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

## What you need (the source company's values are shown as examples)

| Thing | Value | Note |
|---|---|---|
| Domain | **yourco.com** | the site is staged, not deployed — see `08_GTM-MACHINE.md` |
| Founder email | **founder@yourco.example.com** | the git identity on every machine, including the VPS |
| Agent email | each live agent gets its own address in the tenant | that is what makes a "digital employee" an employee |
| Brand | lowercase `yourco`, indigo/brass/cream | `brand/DESIGN.md` is the source of truth for values |

## Do this before any connector, not after

Every connector below authenticates *as somebody*. Wire the domain and the mailbox first, or you will
authenticate Slack, Gmail, and Calendar as the wrong identity and redo all of them. This is the
cheapest step to get right and one of the more annoying to reverse.

## ⚠️ The hard separation, learned by leaking it three times

the Founder runs other ventures (OtherVenture, OtherVenture2). **Nothing yourco may reference them, and no yourco surface,
commit, or email may carry an OtherVenture address.** All yourco git identity and contact email is
`founder@yourco.example.com` — never `hello@`, never an OtherVenture address — **on every machine, including the
VPS**.

This is written down in `CLAUDE.md` because it leaked three separate times before anyone wrote it
down. When you set up a new machine, the git identity is the thing to check first:

```bash
git config user.email
```

If that returns anything other than the yourco address, fix it before your first commit, not after.

## Brand, and why it is locked

`brand/DESIGN.md` holds the palette and type; `brand/writing-rules.md` holds the voice, including the
banned-phrase list and **the em-dash cap** (at most one per paragraph — it is the strongest AI tell in
written copy). Both are re-read rather than remembered: the `visual-brand-qa` and `design-surface`
skills explicitly forbid copying values out of `DESIGN.md` into another file, because a duplicated
palette drifts.

⚠️ **Worth knowing about your own brand if you copy this:** warm cream + a serif display + a warm
accent is *specifically* the combination that reads as machine-generated to a trained eye, and it is
almost exactly yourco's palette. The brand is a deliberate ratified choice and it stands — but the
differentiation has to come from execution (the indigo primary, oxblood reserved for signature
moments, one brass moment per view), not from the palette itself.

## External-surface rules that attach to identity

These bind anything a person outside yourco can see, and several were learned by violating them:

- **Agent names are internal-only.** External surfaces describe agents by *function*, never by name.
- **No prices on the public site.** Pricing bands are Polo's and appear in proposals only.
- **Client-facing surfaces are white-label** — the client's brand only, unless the engagement
  explicitly co-brands. This one bit on Sample Product.
- **Public stats must be sourced from the last 12–18 months**, cited.
- **No fabricated endorsement.** The internal advisory-panel exercise simulates named real people;
  it may never be stated or implied externally as those people advising yourco.

Full list in `CLAUDE.md` §External-surface rules.

## Done when

**you own the domain, mail arrives at your work address, and `git config user.email` returns it.**

If you cannot point at that, the step is not finished — do not move on.
