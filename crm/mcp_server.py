#!/usr/bin/env python3
"""MCP server over yourco's insight layer — the CRM's reads, available to any AI tool.

Clari shipped an MCP server in 2026 to open live revenue intelligence to anything that
speaks the protocol. For yourco that is nearly free: `crm/blocks.py` already packages every
read behind one interface with an owner and an autonomy rung, so this is a protocol adapter
over a registry that exists — not new capability.

What it buys, concretely: Claude Code sessions, the headless runtime loops, and any future
client-side agent all read the SAME computed answers instead of re-deriving them from
data.json. Re-derivation is how two surfaces end up disagreeing, which this codebase has
already paid for once (the payout-math incident, 2026-08-13).

SAFETY POSTURE — read-only, deliberately and completely.
  · Every tool is a READ. Nothing here writes to the CRM, sends anything, or spends money.
    Enrichment is exposed as coverage/plan only; its billable rungs are not reachable.
  · Tools inherit their block's autonomy rung, and the rung is returned in every response so
    a calling agent can refuse work above its own tier rather than discovering the limit
    afterwards.
  · Refusals pass through verbatim. An agent asking "what is the pipeline worth" must receive
    "there is no comparable prior and here is why" rather than a confident zero — the whole
    value of this layer is that it declines to invent, and a protocol adapter that smoothed
    that away would be worse than no adapter.

Wire it (Claude Code / any MCP client):
    {"mcpServers": {"yourco-crm": {"command": "python3",
     "args": ["<repo>/crm/mcp_server.py"]}}}

Run directly to inspect:
    python3 crm/mcp_server.py --list
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PROTOCOL = "2024-11-05"
NAME, VERSION = "yourco-crm", "1.0.0"


def _blocks():
    import blocks
    return blocks


def tools():
    """One MCP tool per block, plus the two that are not blocks."""
    b = _blocks()
    out = []
    for key, meta in b.BLOCKS.items():
        out.append({
            "name": f"crm_{key.replace('-', '_')}",
            "description": (f"{meta['answers']} "
                            f"[owner: {meta['owner']} · autonomy rung: {meta['rung']}] "
                            f"Needs: {meta['needs']}. Read-only. Returns a refusal with a reason "
                            f"where the evidence does not support an answer."),
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        })
    out.append({
        "name": "crm_conversation_signals",
        "description": ("Candidate signals extracted from meeting transcripts awaiting human "
                        "confirmation — mirror evidence, objections, price mentions, buyer-side "
                        "commitments, each with the exact quote. [owner: David · rung: R1] "
                        "Read-only; confirming a candidate is a human action."),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    })
    out.append({
        "name": "crm_enrichment_coverage",
        "description": ("Field coverage across the book and the waterfall chain per field, with "
                        "per-provider cost. [owner: David · rung: R2] Read-only — the billable "
                        "provider rungs are NOT reachable through this server."),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    })
    return out


def call(name, args):
    b = _blocks()
    if name == "crm_conversation_signals":
        import conversation
        return conversation.compute()
    if name == "crm_enrichment_coverage":
        import enrich_waterfall
        return enrich_waterfall.compute()
    if not name.startswith("crm_"):
        return {"error": f"unknown tool {name}"}
    key = name[4:].replace("_", "-")
    if key not in b.BLOCKS:
        # try the underscore form too (pricing / win-loss etc.)
        key = next((k for k in b.BLOCKS if k.replace("-", "_") == name[4:]), None)
        if not key:
            return {"error": f"unknown tool {name}", "available": sorted(b.BLOCKS)}
    r = b.run_block(key)
    # The rung travels with the answer so a calling agent can check it against its own tier.
    meta = b.BLOCKS[key]
    return {"block": key, "owner": meta["owner"], "rung": meta["rung"], **r}


def _resp(rid, result=None, error=None):
    m = {"jsonrpc": "2.0", "id": rid}
    if error is not None:
        m["error"] = error
    else:
        m["result"] = result
    return m


def handle(msg):
    m = msg.get("method")
    rid = msg.get("id")
    if m == "initialize":
        return _resp(rid, {"protocolVersion": PROTOCOL,
                           "capabilities": {"tools": {}},
                           "serverInfo": {"name": NAME, "version": VERSION}})
    if m == "notifications/initialized":
        return None                       # notification — no reply
    if m == "tools/list":
        return _resp(rid, {"tools": tools()})
    if m == "tools/call":
        p = msg.get("params") or {}
        try:
            out = call(p.get("name", ""), p.get("arguments") or {})
        except Exception as e:
            # Surface the failure as CONTENT, not as a protocol error: a calling agent should
            # see "this read failed and here is why" in the same shape as a refusal, rather
            # than a transport-level error it cannot reason about.
            out = {"status": "refused", "why": f"{type(e).__name__}: {e}"}
        return _resp(rid, {"content": [{"type": "text",
                                        "text": json.dumps(out, indent=2, default=str)}]})
    return _resp(rid, error={"code": -32601, "message": f"method not found: {m}"})


def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        out = handle(msg)
        if out is not None:
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    if "--list" in sys.argv:
        t = tools()
        print(f"{NAME} v{VERSION} — {len(t)} read-only tools\n")
        for x in t:
            print(f"  {x['name']}")
            print(f"      {x['description'][:110]}")
        print("\n  Every tool is a READ. Nothing writes, sends, or spends.")
    else:
        serve()
