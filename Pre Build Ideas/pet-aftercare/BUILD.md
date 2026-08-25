# Ember OS — pet aftercare & cremation (build 60)

**Working name:** Ember OS · **Launch:** `prebuild-ember-os` · **Port:** 8880
**Synthetic operator:** "Willow Creek Pet Aftercare" — serves 40 vet clinics + direct families;
private, individual, and communal service lines.

## Why this industry (the overlooked test)
Pet aftercare is a real industry (every vet clinic needs a partner) that no software company —
let alone AI vendor — has ever courted. It is logistics wearing grief: pickups from clinics,
chain of custody through the facility, and returns to families who will remember one mistake
forever.

## The bleeding neck
The chain of custody. Returning the wrong ashes is the industry-ending catastrophe — it has
shuttered real crematories — and it happens through exactly one mechanism: a transfer without
tag verification. The fix is structural: every pet carries an ID tag from intake, and **every
custody transfer (clinic → van → facility → chamber → urn → return) requires the recorded tag
check; a transfer without it has no code path.** The quiet leaks: service level mix-ups
(a communal cremation performed on a paid-private pet is irreversible), clinic pickups on
memory, urn/paw-print add-on orders dropped, and grief comms that read like shipping updates.

## Modules
1. **Chain of custody** (Operations) — append-only transfer log, tag verified at every step;
   the pet's page shows the unbroken chain; a gap reads as a HOLD, never assumed.
2. **The service-level wall** (Operations) — private/individual/communal recorded at intake
   with the family's signed election ref; `change_service_level` is human-only with the family's
   recorded consent; a chamber load mixing a private pet with others is structurally refused.
3. **Clinic desk** (Sales/Intake) — pickup routes from recorded clinic requests; each clinic's
   preferences (paperwork, urn defaults) recorded and cited; status asks answered from the
   chain.
4. **Family comms** (Customer) — updates drafted grief-appropriate (forbidden: logistics-speak
   like "shipment/unit/processed" — tone-checked structurally), R1 always; add-on offers
   (paw print, urn) offered once, gently, never re-pitched.
5. **Return & keepsake pipeline** (Back Office) — urn engraving proofs (name spelling — the
   Stone OS lesson), return method recorded, unreturned remains aged with a bounded, gentle
   ladder and a human-only final disposition per the recorded policy clock.

## Guardrails (load-bearing)
- `transfer_without_tag_check` — **R0, structural**: no path.
- `change_service_level` — human-only with the family's recorded consent; software drafts.
- `mix_private_chamber_load` — structural refusal.
- `logistics_language_to_family` — **R0**; tone check on every family draft (tested).
- `final_disposition` — human-only after the recorded policy clock, like Garment/Consign.

## ROI (typed)
Clinic retention (counted active clinics; the trust story) · add-on attach rate (counted,
operator lift) · the wrong-ashes file (scenario — never a number) · route/office hours
(time_saved).

## Demo path
Chain page (unbroken, tag-verified) → transfer without tag refused → private/communal wall →
grief-tone draft vs logistics-speak refusal → engraving proof → aged-remains policy clock →
trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the wrong-ashes / identity worry
from a family ("are these really Max's ashes?") — the record answers, verbatim chain cited.
