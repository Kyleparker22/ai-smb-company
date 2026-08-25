# outreach-eval — pre-send eval gate artifacts

One artifact per staged Instantly batch, before it may send (`processes/outbound/pre-send-eval-gate.md`):
- `YYYY-MM-DD_<campaign-slug>.mechanical.json` — M1–M5 pre-pass from `runtime/instantly.py --eval-batch` (Reilly/the Founder, Cowork/local — needs Bash)
- `YYYY-MM-DD_<campaign-slug>.md` — Kolby's judgment pass (`runtime/prompts/outreach-eval.md`), **Verdict: PASS / FAIL** top line

The send rule: no dated PASS artifact for the exact staged batch → no send. Edits after a PASS void it.
