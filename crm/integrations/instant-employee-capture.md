# Integration — website tools → CRM (lead capture)

> Turns the site's **three high-intent interactive tools** into a **funnel** instead of dead ends. Each captures at the peak-intent moment → an inbound **prospect** in `crm/data.json`. Owner: **Webb** (the forms) + **David** (the CRM). Mirrors the `instantly_sync.py` integration pattern.
>
> **The three capture points (all use the same payload + endpoint):**
> 1. **Instant Employee** (`instant-employee.html`) — "Make it real" → business, name, email, phone, the employee of interest. `source: "Instant Employee (self-serve)"`.
> 2. **ROI calculator** (`roi-calculator.html`) — "Email me this breakdown" → email + the computed result (e.g. "$4,200 /mo, $50,400 /yr"). `source: "ROI calculator"`.
> 3. **Build-your-employee configurator** (`build-your-employee.html`) — "Email me this employee spec" → email + the built spec (employee name + role). `source: "Build-your-employee configurator"`.
>
> All three were pure leaks until 2026-06-12 (only "Book a call" links) — now each captures the high-intent context so a hot lead is never lost.

## The payload (what the form sends)
```json
{
  "source": "Instant Employee (self-serve)",
  "business": "Cedar Park Family Dental",
  "name": "Dr. Lena Ortiz",
  "email": "lena@cedarparkdental.com",
  "phone": "",
  "employee": "Remi",
  "interest": "Front desk & scheduling"
}
```

## The mapping (payload → CRM)
One captured lead → three records + an activity, all `source: "Instant Employee (self-serve)"`, `status/stage: "prospect"`, `owner: "David"` (inbound owner; reassigned on qualification):
- **company** — `name` = business, `vertical` inferred from `interest`, `source`, `status: "prospect"`.
- **contact** — `name`, `email`, `phone`, `companyId`, `role` (default "Owner/Contact"), `status: "inbound — Instant Employee"`.
- **deal** — `name` = "<business> — <employee>", `useCase` = the interest, `stage: "prospect"`, fees null (set at proposal), `nextAction: "Qualify inbound"`.
- **activity** — `type: "inbound"`, summary "Ran the <employee> demo on their site and requested a build."

## The two modes
- **Now (pre-launch, no backend):** the form builds the structured payload (inspectable at `window.__yourcoLeads` / console) and opens a **prefilled mailto to founder@yourco.example.com** so a lead is never lost. The site isn't public yet, so this is for internal testing.
- **At launch (switch-flip):** the form `action` POSTs the payload to `/api/capture`; a small endpoint (sibling to `crm/server.py`, pattern of `instantly_sync.py`) validates + appends the four records to `data.json` and regenerates `data.js`. The dashboard shows the new prospect instantly. Add rate-limit + a honeypot field (public form = spam target).

## Privacy
The prospect enters **their own** business contact info, voluntarily, to be contacted. No third-party data, no data in URLs except the mailto the user themselves triggers. Nothing else is collected.

## Switch-flip checklist (launch)
- [ ] Stand up `/api/capture` (validate, append 4 records, regen `data.js`).
- [ ] Point the form `action` at it (replace the mailto stopgap).
- [ ] Honeypot + rate-limit + basic email validation.
- [ ] Notify on capture (Slack ping to the Founder, via the runtime connector).
- [ ] David clears `example:true` records on first real lead (per `crm/_README.md`).

> A demonstration captured lead (`example:true`, Cedar Park Family Dental) is seeded in `data.json` so the pipeline shows the channel working end-to-end.
