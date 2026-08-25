# loops/connector-spotter — dated run notes from Bird's referral-spotter loop

Weekdays 09:10 ET (`yourco-connector-spotter.timer` — **STAGED, not installed on the VPS**).
SOP: `processes/loops/connector-spotter.md` · prompt: `runtime/prompts/connector-spotter.md`.

**What the loop does:** for each connector who is joined (R0+, `referral_spotter` unlocked in
`crm/connector_ladder.py`) **and** holds an un-revoked, scoped consent record in
`crm/data.json` → `meta.connectorConsent`, it reads only that granted source, only within that
granted window, and **drafts a warm intro in the connector's own voice** for any referral-shaped
moment it finds. Drafts land in `crm/_pending-intros.json` with `status: "pending"` — the connector
approves or declines, and **the Founder sends**.

**It never sends anything.** Read-only, draft-only, no third-party contact, and connector data is
never mined for yourco's own outreach.

**Today, every run is empty — by design.** No connector has signed (the Connector OS is counsel- +
launch-gated), so there is nothing lawful to read. The correct, complete run writes a dated note
saying *"no opted-in connectors — nothing to scan"* with the real counts, and stops. It does not
substitute another inbox, invent example drafts, or pad. Empty is a valid result.

One dated note per run: eligible connectors (and why each was excluded), sources opened, moments
seen, drafts proposed, skips + reasons. Real counts only.
