# yourco-template — the golden engagement scaffold

**What this is:** the template every client engagement is cloned from. The moment a deal is signed, copy this whole folder to `clients/<client>/` and fill it in. Client logic is **overlay only** — never fork the method, just fill the blanks.

**Owner:** Kemba (Platform/Template Engineer — *not yet built*; the Founder holds). After each engagement, the repeatable parts get folded back here so the next one is faster.

**Maps to:** the delivery loop (`02_delivery_loop.md`) and the build rails (`processes/discovery-to-48h-build.md`). Onboarding runbook (Hour 0): `processes/onboarding.md`.

## How to use
1. Deal signed → `cp -r clients/_yourco-template clients/<client>` (Janice, at onboarding).
2. Work the files in order: `01_discovery` (capture) → `02_build` (overlay) → `03_eval` (prove) → `go-live` → ongoing. Track spend in `cost.md` throughout.
3. Every `[[PLACEHOLDER]]` must be filled before go-live. Don't ship a placeholder.

## What's in here — grouped

30 entries, and until 2026-08-23 the list below covered 14 of them, which is why the folder read as a
grab-bag. **The files are deliberately NOT nested into subfolders**: ~50 places across the repo reference
these paths directly, `runtime/client_tripwires.py` and `runtime/counterfactual.py` read them out of live
client folders, and the template gets *cloned* — nesting would deepen every engagement folder to buy
tidiness. The grouping is here, in the doc, where it costs nothing.

### 1 · The engagement spine — the delivery stages
| File | What it is |
|---|---|
| `_README.md` | This overview. Replace with the engagement summary once cloned. |
| `01_discovery.md` | What the discovery call captures — the build inputs. |
| `02_build.md` | The build checklist (overlay on the stack; detailed steps in the playbook). |
| `03_eval.md` | The eval set + the hard gates that must pass before go-live. |
| `go-live.md` | Go-live steps + the weekly-iteration / expansion cadence. |
| `weekly-readout.md` | The exec one-pager template for the weekly cadence. |
| `CHANGELOG.md` | Versioned changes to this template (Kemba owns). |

### 2 · Client-facing deliverables — things the client actually receives
| File | What it is |
|---|---|
| `audit-report/` | The branded Audit report. Config-driven; print-styled → PDF. **the Founder approves before send.** |
| `demo-kit/` | The config-driven "see yours" walkthrough, shown *before* they sign. |
| `client-console.html` | The daily client-facing view of the moat — the project-status band. |
| `client-console-leak-meter.html` | The Leak Meter band for that console. |
| `contract.md` | The executed-contract register: what was signed, the term, what it commits yourco to. |

### 3 · The moat instrumentation — what proves the work
| File | What it is |
|---|---|
| `autonomy-matrix.md` | This client's rungs — which actions are gated, which have earned autonomy. |
| `client-tripwires.md` | The client's own decisions, watched for expiry against `facts.json`. |
| `ledger/` | Append-only outcome ledger — the self-proving-invoice substrate. |
| `receipts/` | Evidence-packet template + assembler over the audit trail. |
| `outcomes.jsonl` | The outcome record the ledger and receipts read. |
| `learnings/` | Client-scoped learnings + `pattern-candidates/` (immune-system hooks). |

### 4 · Config and data — read by code, not by people
| File | Read by |
|---|---|
| `facts.json` | `runtime/client_tripwires.py` — the measured facts trip-wires evaluate against |
| `baseline.json` | `runtime/counterfactual.py` — the pre-OS baseline for the counterfactual twin |
| `audit.json` | The audit report's config |
| `leak-config.json` · `leak-events.jsonl` | The Leak Meter console |
| `model-routing.json` · `model.py` | Per-client model routing |

### 5 · Frontier hooks — installed ahead of clients, deliberately
| File | What it is |
|---|---|
| `understudy/` | Quit-proofing kit per role — handbook template + consent form (⚠️ counsel gate #1 on the language) |
| `exit-asset/` | Buyer/broker diligence-pack skeleton that fills over the engagement's life |
| `employee-patterns.md` · `employee-patterns-tier2.md` | Reusable employee patterns by tier |

⚠️ **§5 exists because hooks predate clients by design** (`CHANGELOG.md` v1/v1.1). Nothing in it has been
exercised on a real engagement — treat it as scaffolding, not proven practice.

## Engagement summary (fill on clone)
- **Client:** [[CLIENT NAME]]
- **Vertical / use case:** [[e.g. landscaping — intake + estimator coordinator]]
- **Named employee:** [[EMPLOYEE NAME]] · [[employee@client-domain or yourco alias]]
- **Signed:** [[DATE]] · **48h target go-live:** [[DATE+2]]
- **Owner (delivery):** Kimi (the Founder holds until built)
- **Status:** [[onboarding | discovery | build | eval | live | iterating]]

## How the OS works this client (agents across the whole process — fill on clone)
Agents help end-to-end on every engagement (the Founder 2026-08-07; pattern: `clients/sample-client/_README.md`). Internal names — never on client-facing surfaces:
- **David / CRM** — company + deal + activity log stay current; every session that ships something logs an activity row
- **Bella** — the Audit (diagnosis → the scaffolder's inputs)
- **Polo** — pricing posture ([[tier/band]]; no prices on public surfaces)
- **Janice** — onboarding at signature (start items, credentials, access)
- **Kimi** — delivery loop once live (the Founder holds until the playbook hardens)
- **Kolby** — eval on every client-facing surface + the engagement's accuracy/quality loop
- **Reed** — visual production (demos, videos, renders); credibility gate applies
- **Rafi** — guardrails: approval gates, client-safe boundaries, [[vertical-specific compliance]]
- **Ray** — counsel gates: [[signed agreement / vertical legal items]]
- **Charles** — `cost.md` roll-up at weekly pulse + monthly close
- **Atlas + runtime loops** — activation-gated at go-live per `runtime/activation-triggers.md`: [[which loops]]
