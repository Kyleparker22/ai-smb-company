# Post OS — security guard services (build 42)

**Working name:** Post OS · **Launch:** `prebuild-post-os` · **Port:** 8862
**Synthetic operator:** "Granite Shield Security" — ~120 guards, 40 posts, courts + corporate +
construction.

## The bleeding neck
An open post is a contract breach discovered by the client; an incident report edited after the
fact is a career-ending deposition exhibit; a guard on post with an expired license is a
liability the client is paying to avoid. Coverage, verbatim records, credentials — all three are
record problems.

## Modules
1. **Report triage** (Intake) — incident (injury/police/use-of-force adjacent) · callout (post
   going open) · coverage request · credential question.
2. **Verbatim incident discipline** (Operations) — the guard's statement is append-only and
   verbatim (the drift-complaint pattern); software never summarizes, edits, or "cleans up" an
   incident narrative. A client's request to adjust one is refused and logged.
3. **The credential gate** (Operations) — a post fills only with a guard whose recorded license/
   cert set matches the post's requirements (armed, state card, site-specific). RUP pattern.
4. **Coverage board** (Operations) — open posts tonight, keyed-qualified candidates proposed
   (Crew OS pattern), the fill drafts at R1.
5. **Credential calendar** (Company Brain) — expiries as DATE ALERTS per guard; an expired-cert
   guard drops from candidate lists by construction.

## Guardrails (load-bearing)
- `edit_incident_narrative` — **R0, logged.** Append-only, both versions kept if corrected.
- `fill_post_unqualified` — **R0.** The gate names the missing credential.
- `advise_use_of_force` — **R0.** Policy questions go to a human supervisor.
- Injury/police incidents → supervisor now at R2 with a logistics-only brief.

## ROI (typed)
Open posts filled (counted) · credential lapses caught before post (counted) · scheduling hours
(time_saved) · the unedited-incident file (scenario).

## Demo path
Board (open posts, expiring certs) → incident report (verbatim, append-only) → client asks to
adjust it (refused + logged) → fill with the expired-cert guard (refused) → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the incident report.
