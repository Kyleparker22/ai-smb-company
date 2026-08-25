# Dry-run findings — gaps in the delivery machine (2026-06-12)

> What running Janice + Kimi + the templates against a *new vertical (dental) + new type (text-intake+scheduling)* exposed. This is the value of the dry-run: catch these before a real client does.

## 🔴 High — fix before serving these cases
1. ✅ **RESOLVED 2026-06-12 — HIPAA BAA drafted.** `processes/contracts/baa.md` (counsel-review-required) + the trigger lives in `agents/rafi/vertical-compliance-map.md` (discovery flags PHI → BAA blocks go-live until signed).
2. ✅ **RESOLVED 2026-06-12 — sandbox test-tenant spec'd.** `processes/sandbox-test-tenant.md` — Kimi builds + runs the live-integration eval against an YourCo-owned synthetic sandbox before the client's real tenant. (Still needs Kemba/the Founder to *provision* it.)

## 🟡 Medium
3. **`02_build.md` + `go-live.md` templates were still landscaping-voice-specific** — had to be improvised for a text/scheduling build. → generalized in this same change (now type-agnostic, matching `01_discovery` + `03_eval`).
4. **No PMS connectors.** Dental/medical run on Dentrix/Eaglesoft/Open Dental; YourCo has none, so v0 used a Sheet stand-in. **Action (Kemba/connector roadmap):** note vertical-specific systems-of-record per target vertical; a Sheet/email stand-in is the honest v0, PMS integration is an expansion.
5. ✅ **RESOLVED 2026-06-12 — vertical-compliance map built.** `agents/rafi/vertical-compliance-map.md` (healthcare→BAA, finance→GLBA, legal→privilege, outbound→CAN-SPAM/TCPA…), read at discovery.

## 🟢 What worked (the generalization holds)
- **The generalized discovery + stack table handled a non-voice, non-home-services case cleanly** — text-intake+scheduling stack selected correctly, no landscaping/voice assumptions leaked through.
- **The eval framework caught the safety-critical behaviors** — Remy escalated a clinical emergency instead of advising, and refused to guess on insurance. The per-type test set + six dimensions did their job.
- **The lifecycle handoffs flowed** — Janice (Hour 0) → Kimi (build) → Kolby (eval) with no dead-ends. The rails are real.

## Net
The generalized machine **works** for a brand-new vertical + type. The gaps are (a) a vertical-compliance layer (BAA + the checklist) and (b) a sandbox test-tenant for the live-integration eval — both concrete, both worth doing before the first real engagement.
