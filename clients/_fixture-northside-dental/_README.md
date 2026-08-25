# 🧪 DRY RUN — Northside Dental (fictional)

> **Not a real client.** This is a delivery-machine dry-run (2026-06-12) — exercising Janice + Kimi + the generalized templates end-to-end against a *different vertical and employee type than the landscaping-voice default*, to prove the generalized rails work and surface gaps **before** a real client tests them. Gaps found → `_findings.md`.

## Engagement summary (mock)
- **Client:** Northside Dental — 2-dentist family practice, suburban.
- **Vertical:** Healthcare / dental (deliberately *not* home services).
- **Employee:** **"Remy"** — new-patient intake + scheduling. **Type: text-intake + scheduling** (deliberately *not* voice).
- **Signed (mock):** 2026-06-12 · **+48h target:** 2026-06-14.
- **The pain:** new-patient inquiries (web form + email) pile up at a slammed front desk; some sit overnight, some never get a callback, and the practice that replies first wins the patient.

## Lifecycle trace (who did what)
- **Janice** (Hour 0) → folder + intake + identity + kickoff. ✅ this folder.
- **Kimi** (discovery → build → eval → go-live) → `01_discovery` · `02_build` (Remy's actual logic) · `03_eval` (real sample runs scored) · `go-live`.
- **Kolby** → scored the eval (§ in `03_eval`).
- **Findings** → `_findings.md` (the point of the exercise).

> Delete this folder anytime — it's a test artifact, not a real engagement, and is not in the CRM.
