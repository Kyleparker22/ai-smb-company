# Key OS — locksmiths & access control (build 54)

**Working name:** Key OS · **Launch:** `prebuild-key-os` · **Port:** 8874
**Synthetic operator:** "Ironclad Lock & Access" — 4 vans, residential/commercial, ~30 managed
master-key systems.

## Why this industry (the overlooked test)
Locksmithing is a trust business that no AI vendor touches — probably because the liability
scares them, which is exactly why the reliability layer is the product. Every job is an
authorization question wearing a work order's clothes.

## The bleeding neck
Authorization. Rekeying a house, cutting a key, or opening a door for the wrong person is a
break-in with an invoice — the industry's defining scandal. Today "the guy on the phone said he
owns it" is the record. The quiet leaks: master-key system charts kept in a binder (lost = every
tenant's security), unlock jobs with no ID record, key blanks and codes discussed over text,
and the after-hours crush mispriced.

## Modules
1. **The authorization gate** (Operations) — every rekey/cut/unlock carries a recorded authority:
   for an address, the recorded owner/manager of record; for a master system, the system's named
   authorizers. No recorded authority → the job is drafted as *unverifiable* and a human decides
   with the gap named. Verification steps (ID seen, deed/lease shown) are recorded acts.
2. **Master-key registry** (Company Brain) — systems, doors, keyways, holders — append-only;
   a change is a new record, never an edit; key codes never appear in outbound copy (structural
   scrub, like PHI).
3. **Dispatch & the after-hours book** (Intake/Sales) — lockout triage (car/home/commercial,
   safety first: "child locked in car" is the costly label read first); pricing from the
   recorded rate card incl. after-hours multipliers — quoted, never haggled by software.
4. **Job proof** (Operations) — unlock/rekey jobs close with the authorization reference +
   photo; the invoice cites the rate card line.
5. **Access-control service clocks** (Back Office) — batteries, firmware, audit-trail exports on
   recorded intervals; bounded reminder ladder.

## Guardrails (load-bearing)
- `perform_without_authorization` — **R0, structural**: no dispatch path exists for an
  unverified rekey/unlock; the draft names what's missing.
- `disclose_key_code` — **R0**; codes are scrubbed from every outbound draft (regex + field
  whitelist, tested).
- `authorize_by_phone_claim` — **R0**; a phone claim is recorded as a claim, never as authority.
- `quote_off_rate_card` — refused; outward replies R1.

## ROI (typed)
After-hours capture (counted calls × recorded card) · master-system contracts renewed (counted)
· the lawsuit file (scenario, never a number) · dispatch hours (time_saved).

## Demo path
Board → "I'm locked out of my house" flow: authority check → verified path vs unverifiable
draft → master-key registry (append-only, codes scrubbed) → rate-card quote → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the child/person-locked-in
emergency (read before everything).
