#!/usr/bin/env python3
"""hqlink — build a URL that opens the exact HQ screen a notification is about.

The 2026 observability consensus is that **most dashboards should be linked to by alerts**;
browsing is directed. HQ was the opposite: its exception signals — the sidebar dots and counts —
only fire for somebody already looking at HQ. Every Slack post and briefing said *something
happened* and left the reader to go find the screen.

This closes that. Loops import it and paste the link into whatever they were already posting:

    from hqlink import board, partners, evidence
    board(state="needs-you", owner="the Founder")     -> http://…/#board?state=needs-you&owner=the Founder
    partners(panel="lockin")                   -> http://…/#partners?panel=lockin
    evidence(panel="tripwires")                -> http://…/#evidence?panel=tripwires

WHAT THIS IS NOT. A link is not an alert. Something still has to decide what is worth
interrupting for, and that decision belongs to the loop that has the finding — not here. This
module only makes the destination addressable.

The base URL comes from `YOURCO_HQ_URL`, falling back to the Tailscale address in
`runtime/phone-access.md` conventions. A link that points at localhost is useless in a Slack
message read on a phone, so the fallback is the box, not 127.0.0.1.
"""
import os
from urllib.parse import urlencode

DEFAULT_BASE = os.environ.get("YOURCO_HQ_URL", "http://10.0.0.1:8791")

# Doors and the params each one understands. A param not listed here is dropped rather than
# passed through — a link carrying a filter the UI ignores looks broken to whoever clicks it.
DOORS = {
    "today": (),
    "board": ("state", "lane", "owner"),
    "clients": ("client",),
    "partners": ("panel",),
    "commercial": ("panel",),
    "system": ("panel",),
    "evidence": ("panel",),
    "wbr": ("panel",),
    "agents": ("agent",),
}


def link(door, base=None, **params):
    if door not in DOORS:
        raise ValueError(f"unknown HQ door {door!r} — one of {sorted(DOORS)}")
    allowed = DOORS[door]
    clean = {k: v for k, v in params.items() if k in allowed and v not in (None, "")}
    dropped = sorted(k for k in params if k not in allowed)
    url = f"{(base or DEFAULT_BASE).rstrip('/')}/#{door}"
    if clean:
        url += "?" + urlencode(clean)
    return url if not dropped else url  # dropped params are silently unusable by design


def board(**kw):
    return link("board", **kw)


def partners(**kw):
    return link("partners", **kw)


def evidence(**kw):
    return link("evidence", **kw)


def wbr(**kw):
    return link("wbr", **kw)


def clients(**kw):
    return link("clients", **kw)


if __name__ == "__main__":
    print("Examples — paste these into a Slack line or a briefing artifact:\n")
    for u in (board(state="needs-you", owner="the Founder"),
              board(state="blocked", lane="Legal"),
              partners(panel="lockin"),
              evidence(panel="tripwires"),
              wbr(panel="prosecution"),
              clients()):
        print("  " + u)
    print(f"\nBase URL: {DEFAULT_BASE}  (override with YOURCO_HQ_URL)")
    print("A link is not an alert — the loop still decides what is worth interrupting for.")
