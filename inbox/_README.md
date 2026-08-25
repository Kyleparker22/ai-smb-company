# inbox — drop it here, decide later

**The contract: capture is frictionless, routing is proposed, filing is a human call.**

## Why this exists

Every other folder in this repo requires you to know the answer *before* you capture. Is this a
`decision/`? a `learning/`? a `rejection/`? a client artifact? an `offering/`? There are **20 top-level
destinations**, and choosing between them is real judgment — which means at the moment you have
something worth keeping, the workspace asks you a question you may not be able to answer yet.

So things don't get captured. The evidence is in the repo's own history:

- `Pre Build Ideas/` entered on 2026-08-15 inside an automated backup commit and **went a week
  unmapped** — CLAUDE.md names this as a failure mode and it is a routing failure, not a capture one.
- Three PDFs were reviewed on 2026-08-24 straight out of `~/Downloads`. None ever entered the repo.
- `southern_cut_workflow.pdf` — a **client** artifact — sat in `~/Downloads` for **80 days** before
  anything moved it here. That is the number this folder exists to stop producing.

An inbox removes the question at capture time and asks it later, once, in a place where it is visible.

## The rule that makes this safe

**Nothing here is auto-filed.** `runtime/inbox_triage.py` inventories what is here and *proposes* a
destination with its reasoning; a human commits the move. This is deliberate and it is the whole design:

> Filing into `decisions/` vs `learnings/` vs `rejections/` vs `offerings/` is not clerical work. Those
> folders mean different things, and `00_README.md` opens by warning that treating one as another is how
> you "treat a prototype as a product." An auto-filer would manufacture exactly that confusion at scale,
> quietly, in the one place nobody re-reads.

So the triage proposes, and it **says "undetermined" rather than guessing** when the signal is weak.
That is the same posture as `vacancies.py`, agent expiry, and failure-trace skill patches: propose, never
apply.

## How to use it

1. **Drop anything in.** PDF, note, screenshot, transcript, link dump, half-formed idea. No naming
   convention. No subfolder. Do not sort — sorting is what this folder exists to defer.
2. **Run the triage** when you want to clear it:
   ```
   python3 runtime/inbox_triage.py
   ```
   It writes a dated proposal to `loops/_inbox/` listing every item, its age, a content snippet, and
   either a proposed destination *with the signal that suggested it* or an honest `undetermined`.
3. **Move what you agree with.** By hand, or tell an agent to act on specific lines. The triage never
   moves anything itself.

## Duplicates are caught, not routed

The triage md5s every item against every file in the repo. If a byte-identical copy is already filed it
says so — with the path — and proposes **nothing**. This was added on the folder's first real run, which
proposed `clients/sample-client/` for a PDF that was already sitting there under a better name. Acting on
that proposal would have created the exact duplicate the inbox exists to prevent, so a dupe is reported
as a *delete*, never as a route.

## What does NOT belong here

- **Secrets.** Same rule as everywhere: straight into the gitignored env file, never a file in the repo.
- **Anything already filed.** The inbox is for things without a home, not a staging copy of things that
  have one.
- **Large binaries you want kept.** PDFs, video and images in here are **gitignored** — the inbox is a
  local staging area, not storage. If an artifact should be preserved, its *destination* folder is where
  it gets committed, after routing. Text notes (`.md`, `.txt`) ARE tracked so a dropped thought survives
  a machine.

## The failure mode to watch

An inbox that never empties is a graveyard with a nicer name. A consistency invariant warns when items
sit here past **14 days** — not to nag, but because an item aging in the inbox means the routing question
is genuinely hard, and a hard routing question is usually a sign the thing needs a decision, not a folder.
