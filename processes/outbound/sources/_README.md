# `sources/` — where raw sourcing finds land before they are leads

A "source" is somewhere a batch of potential prospects was **observed** — a card wall, a chamber
directory, an association member list, a trade-show floor. It is not a lead list.

**The rule this folder exists to hold:** a name in here has not been verified, has not been contacted,
and is not in the CRM. Nothing moves from here into `crm/data.json` except one at a time, through
`.claude/skills/promote-warm-lead/`, after a human check. Bulk-loading a source into the pipeline is
how a CRM fills with rows nobody can call — and the CRM's own honesty reads (ghost, spread, the board)
all degrade the moment the pipeline contains things that were never real.

**Each file records, at minimum:** where it came from, when, what was legible **and what was not**,
the provenance (was this public? opt-in? invited?), and the next action that would make it usable.
An honest "180 of these 200 are unreadable" is the finding — not a caveat to be trimmed later.

**Provenance matters more than volume.** yourco's posture is licensed/public access only
(`agents/rafi/social-platform-scraping-assessment.md`), and cold outbound stays behind the OtherVenture
gate. The in-person St Pete/Tampa channel is the activated one
(`decisions/2026-07-20_in-person-local-gtm.md`), so a source gathered in person, from something
public and invitational, is the shape that is usable now.
