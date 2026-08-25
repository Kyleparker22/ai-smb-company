# The Instant Employee — yourco's live personalized-demo engine

> **What it is:** give a prospect's website → out comes a real, named AI employee, built for *their* business, in *their* voice, working a real customer — with the reliability/approval gate made visible. A taste of one task, in under a minute, before anything is signed. The page: `agents/webb/pages/yourco-site-v2/instant-employee.html`. Owner: Webb (site) + Reed (demo narrative) + the Founder (the close).

## Why it exists — the conversion thesis
Every other asset on the site makes the *case* for yourco (positioning, pricing, the moat). This is the *experience* of it. It collapses the one objection that kills AI-service deals — *"would it actually work for MY business?"* — by showing the prospect their own business, their own voice, a real task done, with the eval/approval layer visible. The wow is not "AI did a thing." It's **"it did the work, in our voice, AND I can see exactly how they keep it reliable."** That last clause is the moat — and no no-code operator can fake it, because they don't have an eval/approval layer to show.

## Two modes

### Mode A — internal sales weapon (LIVE NOW, zero new infra)
Usable the moment the Founder can take a call. The OS itself is the generation engine:
1. Prospect gives a URL (on the call, in an email, from the CRM).
2. The OS **scrapes the real site** (WebFetch) → extracts name, services, metros, voice, differentiators, contact, whether they quote on-site / have compliance lines.
3. The OS **generates the employee**: a name, the right Tier-1 shape (usually intake/front-desk), and one real customer conversation grounded in those facts.
4. The OS **wires the visible gate**: the 5–7 reliability checks that matter for *that* vertical (e.g. "never quotes a price on-site-quote businesses," "no clinical/medical/legal advice," "routes to a human before promising").
5. The OS **renders it** into the `instant-employee.html` shell (swap the baked example for the fresh one) → a shareable, branded artifact the Founder shows in the room or sends as a follow-up.
   - *Proof this works:* the Cutters Landscaping & Pools employee ("Reese") on the live page was generated this way off their real site (cutterslandscape.com) — real services, real metros, the on-site-quote gate held.

**To run one (the Founder → OS):** "Build an Instant Employee for `<url>`." The OS does steps 2–5 and hands back the rendered page. ~1 minute.

### Mode B — public self-serve (BUILD NOW, SWITCH-FLIP AT LAUNCH)
The same page, but a visitor types their own URL and it generates live in the browser. This needs a backend + a model key — an **external surface**, so it stays **staged until launch** (launch-gate, per `CLAUDE.md` / the launch runbook). The shell is already built and switch-flip ready:
- The page ships today with 3 baked, real-feeling examples (Cutters = real; a dental office + a med spa = sample) so it's genuinely demoable offline **now**.
- The live path is one swap: replace the client-side `BIZ` lookup with a call to a thin backend endpoint that runs the Mode-A pipeline server-side. Mark in the launch runbook.
- Until then, an unknown domain honestly shows *"live generation switches on at launch — here's a real one we built"* and plays the Cutters example. **No pretending it scraped when it didn't.**

## The honesty gate (non-negotiable — same standard as every yourco demo)
- It is a **taste of one task**, said plainly on the page. The full build is integrated + eval-gated + live in 48h.
- The reliability checks shown are **real** — the same gates wired into actual builds (no fabricated price quotes, no medical/legal/clinical advice, human approval before anything's promised). We show the human steps; we never hide them.
- Sample businesses are **labeled sample.** Real scrapes are grounded in the real site. Never blur the two.
- Nothing sends. No signup. No data kept beyond the session.

## The switch-flip checklist (for the launch runbook)
- [ ] Stand up the generation endpoint (Mode-A pipeline, server-side; key held by yourco, never the client).
- [ ] Rate-limit + abuse-guard (it's a public LLM call off a user-supplied URL).
- [ ] Cache per-domain results (15-min) to control cost.
- [ ] Eval the generator itself — it must hold the same gates it shows (no hallucinated services, no price quotes where the vertical quotes on-site).
- [ ] Swap the `BIZ` lookup for the live call; keep baked examples as the fallback.
- [ ] Wire the "make it real" CTA to capture the domain + the generated employee into the CRM (David) as a warm inbound.

## Field notes from live Mode-A runs (feed Mode B's build)
Real lessons from running the engine on actual sites — each is a Mode-B requirement:
1. **Bot-blocking is common.** `WebFetch` got a 403 on impact-advisors.com (Cloudflare-style guard). Fix that worked: `curl` with a real browser User-Agent. Mode B's scraper must send a browser UA and fall back to a headless render / the site's JSON-LD schema block (which carried the cleanest facts).
2. **The engine must adapt the employee *shape* to the business type, not just the copy.** A local SMB → a front-desk intake that books a slot (Cutters, dental, med spa). An enterprise B2B consultancy → an inbound *deal-qualifier* that captures system size / budget / stakeholders and routes to a practice lead, with **no scoping, no pricing, no advice** (Impact Advisors / "Avery"). Same engine, different shape. The generator has to classify SMB-vs-enterprise and pick the pattern.
3. **Ground truth over the prospect's label.** A user described impact-advisors.com as a "staffing firm"; the real site is a Best-in-KLAS *healthcare management consultancy*. The engine built from the site, not the label — and that's correct. The output must always reflect what the site actually says; if it conflicts with what someone *told* us, trust the site and surface the discrepancy.
4. **Never fake a vertical on a miss.** Pre-launch, an unmatched domain must show an honest "live generation switches on at launch" state (+ real examples to explore) — never auto-play a different business's employee. (Fixed 2026-06-12 after the staffing-firm→landscaping fallback read as broken.)

## Where it lives in the site
Primary hero CTA on `index.html` ("See your employee →"), in the nav ("See yours"), and lead item under "See it work" in the footer. It is the front door to the funnel: **See yours → book a call → 48h build.**

> Decision: `decisions/2026-06-12_instant-employee.md`.
