# Setup — native Instantly connector (Reilly's outbound)

> **Status: SETUP DONE — the connector is LIVE.** Evidence: `loops/_instantly/` has artifacts through 2026-08-21. Keep this page for re-keying or a rebuild; you do not need to run it again.

> Wires `runtime/instantly.py` so Reilly can stage leads into Instantly campaigns from the OS (CRM → campaign), instead of a CSV hand-off. **Owned, no third-party MCP.** the Founder does these steps (the API key is yours — the assistant never sees it). **Staging only — it never sends.**

## Why native (not a Cowork connector)
There's no Instantly MCP in the connector registry, and a community one would mean handing your Instantly key to an unvetted third party — against the compliance moat. This is a thin first-party wrapper on Instantly's API v2, same pattern as the Slack listener. It lives on the runtime where Reilly + the Instantly Hyper CRM tier already run; it's also callable from a Cowork session with the same key.

## Step 1 — get your Instantly API key
Instantly → **Settings → Integrations → API** (v2 key). Requires a plan with API access (the Hyper CRM tier has it). Confirm v2, not the legacy v1 key.

## Step 2 — put it on the runtime (gitignored)
```bash
ssh claudeops@<host> && cd ~/yourco-os
echo 'INSTANTLY_API_KEY=<your-v2-key>' > runtime/.instantly.env   # *.env is gitignored
```
(For local use in Cowork, drop the same file in `runtime/.instantly.env` on the Mac.)

## Step 3 — sanity check (no network)
```bash
python3 runtime/instantly.py --self-check        # API key: True, staging-only guard
python3 runtime/instantly.py --campaigns         # lists your live campaigns (confirms auth + endpoint)
```
If `--campaigns` errors, the v2 endpoint shape may have changed — adjust the path in `instantly.py` against the current API docs (functions are small and isolated).

## Step 4 — stage a batch (still no send)
1. Create the campaign in Instantly (named, e.g. "Landscaping — FL — v1").
2. Source + enrich prospects so the CRM has contacts **with emails** (Reilly via Vibe → David's CRM → Enrich).
3. Dry-run, then stage:
```bash
python3 runtime/instantly.py --stage "Landscaping — FL — v1" --vertical landscaping --dry-run
python3 runtime/instantly.py --stage "Landscaping — FL — v1" --vertical landscaping
```
This loads the leads into the campaign. **It does not start sending.**

## The gates (unchanged — staging ≠ sending)
The actual send is a separate, human action in Instantly, and it stays blocked by: the **OtherVenture launch gate** (nothing external yet), **domain warmup** (~90% before first send), **Polo's per-vertical pricing lock** (Reilly can't run a vertical Polo hasn't priced — landscaping/hardscaping is the only locked one), and **Reilly's batch approval** (the Founder okays the batch). The connector deliberately has no "start campaign" call — by design.

## Compliance
Sending is CAN-SPAM / TCPA / FTSA-gated (Rafi + the `processes/10dlc-sending-infra-setup.md` flow). The connector only stages; it changes none of that.
