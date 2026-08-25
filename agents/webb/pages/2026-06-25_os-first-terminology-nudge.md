# Webb changelog — OS-first terminology nudge (2026-06-25)

A light alignment pass surfaced by the cross-workspace consistency audit. Goal: make the product-description surfaces lead **OS-first / "agents"** so they match the offering hierarchy (custom AI OS = unit of sale; the digital employee = smallest on-ramp module), without disturbing brand-core copy.

## Changed
- **positioning.html** — meta description "builds a digital employee" → "builds your custom AI OS"; section header "roles a digital employee fills" → "roles your AI OS can cover".
- **about.html** — close CTA "see what one digital employee does" → "see what one agent does" (matches the page's "Agents, not tools" reframe; keeps the concrete single-on-ramp framing).
- **glass-box.html** — H1 "the employees we build" → "the agents we build"; "a roster of digital employees" → "a roster of AI agents"; "mostly digital employees" → "mostly AI agents"; both meta/OG descriptions synced to "agents."
- **index.html** — schema.org description "AI employees and a full AI OS" → "a full AI OS built from coordinated AI agents"; knowsAbout "AI employees for small business" → "AI agents for small business".

## Deliberately NOT changed
- **manifesto.html** — left intact. "Hire, don't subscribe" / "hire a digital employee" is the page's central thesis (it's the page title and OG description) and it already arcs from one hire → added capability (the on-ramp→OS story). Per the offering decision the employee-as-on-ramp framing is correct, so this is a keep, not a gap.

## Also (same audit)
- `CLAUDE.md` roster parenthetical synced to the full 27-agent roster (had been missing Atlas, Melanie, Sadie, David, Luka, Polo).
- `START-HERE.html` + `processes/demo-recording-script.md` synced to the new `show.sh` behavior (website + HQ + CRM; auto-opens the website).

Audit verdict otherwise: documentation coverage complete, scaling story consistent across all four places, CRM data.json↔data.js in sync, site email/links clean.
