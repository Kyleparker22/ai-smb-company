# Reed — Asset Registry

The lookup other employees query for a demo asset. Reilly reads this in its outbound loop to embed the right demo in **touch 2** (as a thumbnail/GIF + tracked link — never an embedded/attached video). Reed appends a row when an asset is **published and approved**.

## Conventions
- One row per published asset. Add only after the Founder approves the final cut (creative approval gate).
- `vertical` = the targeting key Reilly matches on (use `generic` for a reusable founder/exec-ops demo).
- `page URL` = hosted landing page; `thumbnail` = animated GIF/still for email; `tracked link` = the click-tracked URL Reilly uses.
- Keep `status` = `script` | `in-production` | `published`.

## Registry
| vertical | asset | status | page URL | thumbnail | tracked link | production record | published |
|----------|-------|--------|----------|-----------|--------------|-------------------|-----------|
| generic (founder / exec-ops) | Atlas: The Monday Briefing | script | _TBD_ | _TBD_ | _TBD_ | `agents/Reed/productions/2026-06-07_atlas-monday-briefing.md` | — |
| landscaping / hardscaping | Lead intake + estimator coordinator (Email 2 demo) | **published** | https://share.descript.com/view/L6EdW0JYGQJ | Preview = workflow clip (Higgsfield); email GIF generated in Instantly from it at send time (standalone GIF export via Canva MCP was unreliable) | https://share.descript.com/view/L6EdW0JYGQJ | `productions/2026-06-08_landscaping-intake-demo.md` | 2026-06-09 |
| generic (founder / exec-ops) | **YourCo explainer (homepage hero)** | **published** | https://share.descript.com/view/mIvvSqQZ5xk | word-free animated (Higgsfield) + VO "Grace" (Descript); no on-screen text | https://share.descript.com/view/mIvvSqQZ5xk | `productions/2026-06-10_yourco-explainer.md` | 2026-06-10 (the Founder-approved) |
| generic (employee at work) | **Generic "digital employee at work" demo** | **published** | https://share.descript.com/view/cYRYnooGi4Y | word-free animated + VO "Grace"; no on-screen text | https://share.descript.com/view/cYRYnooGi4Y | `productions/2026-06-10_yourco-explainer.md` | 2026-06-10 (the Founder-approved) |

## In-flight requests
- `requests/2026-06-08_landscaping_email2-demo.md` — ✅ **CLOSED.** Reilly's request; the Founder approved 2026-06-08; script approved 2026-06-08; format resolved to ANIMATED 2026-06-09; produced via Higgsfield + Descript; **the Founder approved the final cut 2026-06-09 → published + registered above.** Production record: `productions/2026-06-08_landscaping-intake-demo.md`. (One follow-up: generate the 3-5s inline GIF preview from the cut — `thumbnail` currently pending.)

## Notes
- First asset (Atlas: The Monday Briefing) is scripted; not yet built/published, so Reilly should treat it as "none available" until `status` = `published` and URLs are filled.
- When an asset is published, fill the URLs here and flip `status`; that's the signal Reilly needs to start using it.
