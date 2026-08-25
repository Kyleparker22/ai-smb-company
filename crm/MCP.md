# yourco CRM — MCP server

Exposes the CRM's insight layer (`crm/blocks.py`, 18 blocks) as **read-only** MCP tools, so
Claude Code sessions, the headless runtime loops, and any future client-side agent read the
SAME computed answers instead of re-deriving them from `data.json`.

Re-derivation is how two surfaces end up disagreeing — this repo has paid for that once
already (the payout-math incident, 2026-08-13).

## Wire it

Add to your MCP client config (Claude Code: `.mcp.json` or `claude mcp add`):

```json
{
  "mcpServers": {
    "yourco-crm": {
      "command": "python3",
      "args": ["/Users/you/Documents/Claude/Projects/YourCo LLC - AI/crm/mcp_server.py"]
    }
  }
}
```

Inspect without a client: `python3 crm/mcp_server.py --list`

## Safety posture — read-only, deliberately

- **Every tool is a READ.** Nothing writes to the CRM, sends anything, or spends money.
- **Enrichment is coverage/plan only.** The billable provider rungs in
  `crm/enrich_waterfall.py` are *not reachable through this server* — a billable call
  reachable from a loop is how an enrichment invoice arrives unannounced.
- **Rungs travel with the answer.** Every response carries the block's autonomy rung
  (`processes/autonomy-matrix.md`) so a calling agent can refuse work above its own tier
  rather than discovering the limit afterwards.
- **Refusals pass through verbatim.** An agent asking what the pipeline is worth receives
  *"there is no comparable prior, and here is why"* rather than a confident zero. Smoothing
  that away would defeat the point of the layer.

## What's exposed

18 blocks + `crm_conversation_signals` + `crm_enrichment_coverage`. Run `--list` for the
current set; the registry is the source of truth and this file does not restate it.
