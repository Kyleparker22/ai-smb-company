2026-08-19 — A prose gate in a client folder is invisible until a human reads it — and by then it may already be crossed

Source: customer-health run 2026-08-19. `clients/sample-client/_README.md` carried an explicit gate — *"counsel gate on the signed 1-page agreement before any live-data/production wiring"* — written down and correct. It was crossed anyway: the Aspire integration went live and a schedule pull returned 1,224 production tickets while the engagement was still unsigned and no counsel was engaged. Nothing failed loudly; the gate was simply prose, and the only thing that ever evaluates prose is a human eye. The health loop caught it, but only because it happened to read the README line and cross-check it against a git commit — a week after the crossing.

Pattern: a "do X before Y" line living only in a client-folder README (or any narrative doc) has **no evaluator**. It reads as a control but behaves as a note. The OS already has the right mechanism — `runtime/client_tripwires.py` + `clients/_yourco-template/client-tripwires.md` (a client's own decisions watched for expiry against their `facts.json`) — but a gate isn't watched unless it's *registered* there. Sample Client's live-data gate never was, so it fired only by eye.

Implication (feed-forward):
- **When a client engagement writes a "before X, do Y" gate into any folder doc, register it as a client trip-wire the same commit** — with the observable fact that flips it (here: `aspire_live == true` AND `agreement_signed == false` → fire). A gate not backed by a checkable fact reads `unmeasured` and never fires — say so rather than trusting it.
- **Health runs should treat every folder-level prose gate as a check, not a note** — read the gate lines in the client `_README`, and verify each against live evidence (git, integration state, calendar), not against a status sentence.
- The distinction from `learnings/ops/2026-08-07_absence-is-invisible-to-this-os.md`: that one is "the CRM enum can't see the engagement." This one is narrower and sharper — *the control existed, in writing, and still wasn't enforced* because writing isn't enforcement.

Audience: Kortney (customer-health) · Ray (owns gates) · whoever seeds `client_tripwires` per engagement · scaffold-engagement (candidate: auto-register folder gates as trip-wires at Stage 0).

Triggers: loop:customer-health, agent:kortney, agent:ray, client gate, client trip-wire, live-data before signature, skill:scaffold-engagement, delivery gate crossed
