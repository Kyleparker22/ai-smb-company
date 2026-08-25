#!/usr/bin/env python3
"""Sample Client — Installation Proposal Automation agent (DRY-RUN PROTOTYPE).

A runnable core of the agent on SAMPLE data. It does NOT touch Aspire, Twilio, email, a real
customer, or a real DB. It shows the real shape of the build:
  Aspire-signed proposal (sample file)  ->  parse (Claude)  ->  tier deposit (TESTED CODE, never AI)
  ->  draft client / supplier / sub messages (Claude writes words only)  ->  approval gate (nothing sent).

In production the trigger is an Aspire webhook, sends go through Twilio + the @sampleclient.example.com mailbox
after a human tap, dates come from Google Calendar, and runs are traced in Langfuse on a private server.
Here, the proposal is read from a file and every "send" is a DRAFT printed to the screen.

Run:  python3 clients/sample-client/prototype/agent.py
Needs ANTHROPIC_API_KEY (via dashboard/melanie.env) for the live drafts; without it, falls back to
clearly-marked template drafts so the flow still runs.
"""
import os, sys, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# Reuse the OS's Claude key loader (dashboard/melanie.env). Optional — degrades to templates.
sys.path.insert(0, os.path.join(REPO, "dashboard"))
try:
    import melanie
    import urllib.request
    _KEY = melanie._key("ANTHROPIC_API_KEY")
    _VER = melanie.ANTHROPIC_VERSION
    _MODEL = melanie.MODEL
except Exception:
    melanie, _KEY, _VER, _MODEL = None, "", "2023-06-01", "claude-opus-5"


def _claude(system, user, schema=None, max_tokens=700):
    """Minimal Claude call. Returns text, or parsed JSON if schema given. None on no-key/error."""
    if not _KEY:
        return None
    body = {"model": _MODEL, "max_tokens": max_tokens, "system": system,
            "messages": [{"role": "user", "content": user}]}
    if schema:
        body["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "x-api-key": _KEY, "anthropic-version": _VER},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
        txt = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
        return json.loads(txt) if schema else txt
    except Exception as e:
        print(f"   [claude error: {e}]")
        return None


def money(n):
    return "${:,.2f}".format(n)


# ---- TESTED CODE: the money math. Never touched by AI. ------------------------------------
# SAMPLE tier rules — REPLACE with Client Owner's real deposit rules from the system spec.
DEPOSIT_TIERS = [
    (10_000, 0.50, "small (≤$10K)"),       # total ≤ 10k  -> 50% deposit
    (150_000, 0.35, "mid"),                # 10k–150k     -> 35%
    (float("inf"), 0.25, "large (≥$150K)"),  # ≥ 150k      -> 25%
]


def deposit_for(total):
    """Return (deposit_amount, pct, tier_label) by project total. Pure, tested, deterministic."""
    for ceiling, pct, label in DEPOSIT_TIERS:
        if total <= ceiling:
            return round(total * pct, 2), pct, label
    raise ValueError("no tier matched")


def route_material(desc):
    """Shop (small/packaged) vs job site (bulk/pallets). SAMPLE heuristic — real rules per Client Owner."""
    d = desc.lower()
    if any(k in d for k in ("pallet", "ton", "bulk", "yard", "screening", "load")):
        return "job site"
    return "shop"


# ---- PARSE (Claude reads the proposal the way it would the Aspire payload) ------------------
PARSE_SCHEMA = {
    "type": "object",
    "properties": {
        "division": {"type": "string"}, "client": {"type": "string"}, "property": {"type": "string"},
        "client_email": {"type": "string"}, "client_phone": {"type": "string"},
        "project": {"type": "string"}, "window_start": {"type": "string"}, "window_end": {"type": "string"},
        "total": {"type": "number"},
        "line_items": {"type": "array", "items": {"type": "object", "properties": {
            "description": {"type": "string"}, "qty": {"type": "string"},
            "cost_category": {"type": "string"}, "supplier": {"type": "string"}},
            "required": ["description", "qty", "cost_category", "supplier"], "additionalProperties": False}},
    },
    "required": ["division", "client", "property", "client_email", "client_phone", "project",
                 "window_start", "window_end", "total", "line_items"],
    "additionalProperties": False,
}


def _regex_parse(raw):
    """No-key fallback: parse the Aspire export from its actual text so the demo reflects the real
    proposal — same field shape as PARSE_SCHEMA. Critically, `division` comes from the input (not
    hardcoded), so the Installation-only STOP filter in run() actually engages; and line_items are
    read from the table so the supplier/sub sections populate. Missing fields degrade to empty, and
    a missing/unreadable division defaults to 'unknown' (which run() STOPs on) — never a false pass."""
    def field(label, default=""):
        m = re.search(rf"^{label}:\s*(.+)$", raw, re.I | re.M)
        return m.group(1).strip() if m else default

    total_raw = re.search(r"total:\s*\$?([\d,]+(?:\.\d+)?)", raw, re.I)
    win = field("Project window")
    win_start, _, win_end = (win.partition(" to ") if " to " in win else (win, "", ""))

    line_items = []
    for ln in raw.splitlines():
        if "|" not in ln:
            continue
        parts = [c.strip() for c in ln.split("|")]
        if len(parts) < 5 or not parts[0].isdigit():  # skip header (#) + separator (---) rows
            continue
        line_items.append({"description": parts[1], "qty": parts[2],
                           "cost_category": parts[3], "supplier": parts[4]})

    return {
        "division": field("Division", "unknown"),
        "client": field("Client"), "property": field("Property"),
        "client_email": field("Email"), "client_phone": field("Phone"),
        "project": field("Project"),
        "window_start": win_start.strip(), "window_end": win_end.strip(),
        "total": float(total_raw.group(1).replace(",", "")) if total_raw else 0.0,
        "line_items": line_items,
    }


def parse_proposal(raw):
    out = _claude(
        "Extract the fields from this signed Aspire proposal export exactly as written. Numbers as numbers.",
        raw, schema=PARSE_SCHEMA, max_tokens=900)
    if out:
        return out
    return _regex_parse(raw)  # no key — parse the real text (see _regex_parse)


# ---- DRAFT (Claude writes words only; every dollar figure is injected from code) ------------
DRAFT_SYS = ("You write short, professional, friendly messages for Sample Client, a hardscape design-build "
             "company, to send to a {audience}. Plain text. Use the EXACT figures, names, and dates given — "
             "never invent or change a number, price, or date. No placeholders. Keep it tight.")


def draft(audience, instruction):
    txt = _claude(DRAFT_SYS.format(audience=audience), instruction, max_tokens=450)
    return txt or "[draft unavailable — no ANTHROPIC_API_KEY; in production Claude writes this message]"


# ---- ORCHESTRATE -------------------------------------------------------------------------
_SEEN = set()  # duplicate-proofing: one signed proposal never double-sends


def run(raw, proposal_id):
    print("=" * 86)
    print("Sample Client — Installation Proposal Automation  ·  DRY RUN (sample data, nothing is sent)")
    print("=" * 86)

    if proposal_id in _SEEN:
        print(f"\n⛔ Proposal {proposal_id} already processed — duplicate ignored (no double-send).")
        return
    _SEEN.add(proposal_id)

    p = parse_proposal(raw)
    if p.get("division", "").lower() != "installation":
        print(f"\n⏹  Division is '{p.get('division')}', not Installation — STOP (ignored).")
        return

    print(f"\nProposal {proposal_id}  ·  {p['client']}  ·  {p['project']}")
    print(f"Total {money(p['total'])}  ·  window {p['window_start']} → {p['window_end']}")

    # 1) CLIENT — deposit (math in code, words by Claude, gated on Charlene)
    dep, pct, tier = deposit_for(p["total"])
    print("\n" + "-" * 86)
    print(f"① CLIENT DEPOSIT   tier={tier}  →  {int(pct*100)}% of {money(p['total'])} = {money(dep)}  (computed in code)")
    print("-" * 86)
    email = draft("homeowner client",
                  f"Write a deposit-request email. Client: {p['client']}. Project: {p['project']}. "
                  f"Deposit due now: EXACTLY {money(dep)} ({int(pct*100)}% of the {money(p['total'])} total). "
                  f"Payment options: Zelle, check, or card. Warm but professional. Sign 'Sample Client'.")
    sms = draft("homeowner client",
                f"Write a 1-2 sentence SMS to {p['client']} that their Sample Client deposit of EXACTLY {money(dep)} "
                f"is ready and a detailed email is on the way. Friendly.")
    print("\nEMAIL DRAFT:\n" + email)
    print("\nSMS DRAFT:\n" + sms)
    print("\n⏳ awaiting CHARLENE's approval — nothing sends until she taps approve.")

    # 2) SUPPLIERS — one order per supplier (gated on Client Owner)
    mats = [li for li in p.get("line_items", []) if li.get("cost_category", "").upper() == "MATERIAL"]
    suppliers = {}
    for li in mats:
        suppliers.setdefault(li["supplier"], []).append(li)
    print("\n" + "-" * 86)
    print(f"② SUPPLIER ORDERS   {len(suppliers)} supplier(s)")
    print("-" * 86)
    for sup, items in suppliers.items():
        lines = [f"{li['qty']} — {li['description']} → deliver to {route_material(li['description'])}" for li in items]
        order = draft(f"material supplier ({sup})",
                      "Write a short material-order email. Supplier: " + sup +
                      f". Needed by {p['window_start']} (project start). Deliver per item routing. Items:\n" +
                      "\n".join(lines) + "\nAsk them to confirm availability and the delivery date. Sign 'Sample Client'.")
        print(f"\n→ {sup}:\n{order}")
    print("\n⏳ awaiting CLIENT_OWNER's approval on supplier orders.")

    # 3) SUBS — one notice per sub (gated on Client Owner)
    subs = [li for li in p.get("line_items", []) if li.get("cost_category", "").upper() == "SUB"]
    print("\n" + "-" * 86)
    print(f"③ SUBCONTRACTOR NOTICES   {len(subs)} sub item(s)")
    print("-" * 86)
    for li in subs:
        notice = draft(f"subcontractor ({li['supplier']})",
                       f"Write a short job-notice email to sub {li['supplier']} for: {li['description']}. "
                       f"Project window {p['window_start']} → {p['window_end']} at {p['property']}. "
                       f"Ask them to confirm availability and their rate. Sign 'Sample Client'.")
        print(f"\n→ {li['supplier']} ({li['description']}):\n{notice}")
    print("\n⏳ awaiting CLIENT_OWNER's approval on sub notices.")

    # 4) ALL-CLEAR gate
    print("\n" + "=" * 86)
    print("④ ALL-CLEAR GATE")
    print("   Greenlit email to Charlene + Client Owner fires only when ALL of these confirm:")
    print("     [ ] deposit received     [ ] all suppliers confirmed     [ ] all subs confirmed")
    print("   Anything still open after the threshold is flagged daily. (Pending in this dry run.)")
    print("=" * 86)


if __name__ == "__main__":
    with open(os.path.join(HERE, "sample_proposal.txt")) as f:
        raw = f.read()
    print(f"[brain: {'Claude live' if _KEY else 'templates (no key)'}]\n")
    run(raw, "SC-2026-0488")
