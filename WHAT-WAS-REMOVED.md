# What was removed, and how it was checked

Extracted **additively**: the target started empty and each file was copied only after passing an
automated check. A mistake leaves a **gap in the template**, not a private detail on the internet.

## Never copied — 11 files

Legal and tax records (EIN letter, business info, signed/unsigned agreements, counsel review,
valuation worksheet) · the live CRM database · every `.env` and session store · locally generated
sandbox data.

**Blank forms ship in their place.** You need the *shape* of a business-info sheet, not someone
else's filled-in copy. `finance/legal-docs/` and `crm/data.json` are templates and an empty store.

## Included but scrubbed — the client work

Three real engagements are here as **worked examples**, because the structure of a real proposal and
a real discovery doc is most of what a template is for.

⚠️ **Names were not enough.** After the name scrub the corpus still read *"hardscaping company in
[town], NC"* with the client's domain attached — which identifies one company. **Trade is kept**
(thousands of such firms; it is what makes the example instructive). **Domain, town, and state are
removed**, because trade + town is what narrows it to a single business.

## Refused by the checker — 138 files

All binaries. A PDF, spreadsheet, image, or video **cannot be inspected as text**, so none were
copied — including site photography, walkthrough videos, and design renders. This leaves visual gaps
in the client examples by design.

## Why the verifier is deliberately dumb

Plain case-insensitive substring matching, no clever word boundaries — learned the hard way. An
earlier version used `\bname\b` in **both** the replacer and the checker, and `\b` does not fire on
`_name-template` or `NAME_DATA_ROOT` because `_` is a word character. **217 files passed a check
that shared the replacer's blind spot.** A verifier that reasons like the thing it verifies cannot
catch it.

The same trap appeared in four more disguises, each found only by checking the *output*:

| Form | Why `\b` failed |
|---|---|
| `needsOwner`, `crmNonOwnerUsers` | camelCase — no boundary inside a token |
| `OWNER_SLACK_USER_ID` | `_` is a word character |
| `"\n\nOWNER ASKS:"` | the char before `K` is the letter `n` of the escape |
| `YourCoCoDesignStudio` | CamelCase compound |

And two failures that were not boundaries at all:

- **Prose replacement inside code.** A constant `OWNER = "..."` became `the Founder = "..."` — a space
  in an identifier. Caught by parsing every Python file in the output; 2 were broken.
- **Base64 image blobs** contain any four letters by chance. Encoded binary is not prose, so those
  payloads are now excluded from the scan rather than excepted by name.

Where a placeholder collided with a real string — a synthetic first name containing a partner's name,
an agent name resembling another — **the string was changed rather than an exception added.**
Exceptions accumulate; collisions do not.

## Verified before publication

Every Python file parses · every JSON file parses · clean across 18 identity patterns · zero EIN or
API-key shapes · zero `.env` files · no inherited git history · and the repo's own checkers run clean
**inside the copy**: 28/28 self-declared counts, 0 dead citations.

## What this does not promise

An automated check finds what it was told to look for. **It has not been read by a second pair of
human eyes.** Read what you are about to publish — start with `clients/`, `SETUP/`, and `decisions/`,
where an unlisted detail is likeliest to survive.
