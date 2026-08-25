# receipts/ — evidence-grade dispute packets (The Receipts substrate)

**What this is:** the per-client packet template + assembler for `offerings/the-receipts/SPEC.md` — on a dispute (chargeback, "you never told me that," false review, insurance question), the OS assembles the full interaction chain from records the moat layer was writing anyway. **Zero new capture**: this is a *view* over the existing audit trail + `../ledger/`, on from day one of every engagement.

**Files**
- `packet-template.md` — the structure of an evidence packet (chain-of-events narrative · exhibits · gap report · integrity note). White-label: client brand only.
- `assemble.py` — stdlib-python assembler stub: walks this engagement's `ledger/*.jsonl` and `audit-trail/` locations for a date range (+ optional keyword), orders the chain chronologically, and emits a packet **skeleton** from the template. Narrative summary + review are human/LLM steps after — the stub never paraphrases records.

## Integrity rules (the hard lines — spec §1/§8)
- **Append-only.** A record you can edit is not evidence. Corrections are new entries that reference the old — nothing is retroactively altered, re-worded, or deleted inside retention. No admin path rewrites history, including for yourco.
- **No fabricated or reconstructed records.** If an interaction predates the OS or happened off-channel, the packet reports the gap as a gap ("no record of this interaction in the system") — never inferred, backfilled, or plausibly-reconstructed, no matter how sure the client is it happened or what's at stake. One reconstructed entry poisons every packet the system will ever produce.
- **No selective assembly presented as complete.** A packet includes the **full responsive chain — including entries unhelpful to the client's position**. The assembler filters by responsiveness (date range / job / customer), never by favorability. The client chooses what to *do* with the packet; the packet doesn't curate.
- **Verbatim stays verbatim.** The LLM summarizes and organizes up top, labeled as summary; it never paraphrases *into* the record.
- **No legal advice, no merit opinions, no admissibility claims.** The integrity note says what the system captures and how — nothing more. Legal questions route to the client's attorney.
- **Reply drafting (review responses, dispute correspondence) is R1 permanently** — human-approved before anything posts or sends.
- **Recording consent:** v1 evidence scope is written artifacts + system events only; call summaries only where the consent posture is counsel-cleared (rides gate #1, `processes/counsel-gates.md`).
- **White-label:** no yourco branding on packets or the console surface.

## Usage (on a dispute request from the client)
```
python3 receipts/assemble.py --from 2026-09-01 --to 2026-09-30 [--match "keyword"] [--out receipts/packets/]
```
Output: a timestamped packet-skeleton markdown under `receipts/packets/` (gitignored per client posture if it contains customer PII — packets are released only to the client). Then: human/LLM pass fills the narrative summary from the exhibits, Kolby evals, the Founder (or the named approver) reviews before anything leaves the tenant.
