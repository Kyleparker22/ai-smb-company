# Peptide & Telehealth OS — vertical scope (four buyers, one spine)

**Working name:** Peptide & Telehealth OS
**Author:** the Founder (scoped 2026-08-23)
**Status:** **BUILT as prototypes 2026-08-24** — `Pre Build Ideas/` builds 72–75 (`prebuild-assay-os` 8895 · `prebuild-provenance-os` 8896 · `prebuild-protocol-os` 8897 · `prebuild-encounter-os` 8898), 335 assertions, all green. Still **no client and no engagement**: synthetic data, nothing sold, nothing shipped externally. Live prospect in the family: `d21` Sample Contact — Peptide Testing (pre-convo, **gone-cold since 2026-06-16**).
**Pillars:** 1 Intake · 2 Sales · 3 Marketing · 4 Customer · 5 Operations · 6 Back Office · 7 Company Brain (varies by buyer, below)
**Form factors:** all three, and the differentiator in three of the four is **form factor 3** (embedded AI surface).
**Precedent to reuse:** **Sample Product** (`clients/prospect-a/`) — a hosted verification product with public lookup is the same architecture as the Verified COA layer below.

---

## 0. Are "peptide clinics" and "telehealth clinics" the same thing?

**No — but they overlap about 60–70%, and the relationship is precise:**

> **Telehealth Clinic OS + the product-trust module = Peptide Clinic OS.**

A *peptide clinic* is a **therapy category** (usually cash-pay, usually delivered by telehealth).
A *telehealth clinic* is a **delivery modality** spanning weight/GLP-1, hormone/TRT, derm, mental
health, primary care. Most peptide clinics *are* telehealth clinics. Three real differences:

1. The peptide clinic has a **product-trust problem** — *is what I'm being sold real, and is it
   safe* — that a general telehealth clinic does not carry.
2. The telehealth clinic has a **multi-state licensure and throughput problem** that a
   single-location peptide clinic does not.
3. The **buyer differs**: peptide clinics are often solo or small cash-pay operators; telehealth is
   a platform business whose scarce resource is clinician supply.

So they are scoped separately below, sharing most modules.

## 1. The spine — why these four are one family

Every business here sells into a category where **the buyer's default assumption is that someone is
cutting corners.** Testing labs exist because that assumption is often correct. So the through-line
is not lead capture — it is **provenance: proving a claim, continuously, in a form a skeptic can
check.** That is yourco's moat layer (reliability · eval · approval · audit log) pointed at the
*client's own product* instead of at the OS, and it is the reason this is one offering family
rather than four unrelated verticals.

| Buyer | What provenance means to them |
|---|---|
| Testing lab | The verified COA **is** the product |
| Compounder / supplier | Batch + upstream-supplier chain of custody |
| Peptide clinic | What the patient is getting, and why |
| Telehealth clinic | Documentation defensibility of every encounter |

---

## 2. Peptide **testing lab** OS — *sample to verified COA*
*Buyer: lab owner (this is Sample Contact's business). The sharpest fit of the four.*

| # | Module | Pillar | Form factor | Note |
|---|---|---|---|---|
| 1 | Sample intake + chain of custody | 5 Ops | 3 surface + 1 employee | Customer submits online, gets a tracking state; lot/barcode carried through. Kills the "where's my result?" queue at source. |
| 2 | Instrument data → COA generation | 5 Ops | 2 headless | Parse instrument output → render to template → QC checks → **human sign-off**. |
| 3 | **Verified COA surface** | 5 Ops | **3 surface** | *The differentiator.* QR/lookup: anyone holding a certificate can confirm it is genuine, unaltered and matches the lab's record. Tamper-evident. Directly reuses the Sample Product pattern. |
| 4 | Result explainer | 4 Customer | 1 + 3 | Cited Q&A bounded to that customer's own COA; refuses anything outside the record. |
| 5 | Invoicing / AR | 6 Back Office | 2 headless | |

**Tier:** Suite (~5 agents, ~3 pillars) — **$2,500–3,500 impl · $4,500–6,000/mo**. Module 3 alone can
justify Operation if the lab sells verification as its own differentiator.

**The expansion story:** module 3 is not just internal efficiency — it is a **product the lab can
market on**, and the thing its competitors cannot fake. That is the land-and-expand hook.

**Autonomy note:** a COA is a high-stakes public claim. Module 2 stays at the **R1 approval floor**
— sign-off never leaves a human, regardless of streak. Same shape as the Care rule.

## 3. Peptide **lab / compounder / supplier** OS — *provenance and a moving rulebook*
*Buyer: owner or QA lead. Heaviest compliance load of the four.*

| # | Module | Pillar | Form factor | Note |
|---|---|---|---|---|
| 1 | **Regulatory-change watcher** | 7 Company Brain | 2 headless | *The standout.* Watches the rule sources, maps a change onto **their specific SKU list**, and flags what is affected. In a category whose rules move under the business, nobody sells this. |
| 2 | Batch record + document assembly | 5 Ops | 2 headless | Batch records, stability data, supplier COAs → one audit-ready packet on demand. |
| 3 | Upstream supplier verification | 5 Ops | 2 + 3 | Incoming certificates validated rather than filed. Consumes §2's verification layer from the other side. |
| 4 | Wholesale / reseller account ops | 2 Sales | 1 employee | Order intake, reorder cadence, terms. |
| 5 | Complaint + adverse-event intake | 4 Customer | 1 employee, **hard gate** | Captures, logs, routes. **Never** interprets, advises, or triages clinically. |

**Tier:** Operation (~7 agents, 4–5 pillars) — **$3,500–4,500 impl · $6,500–8,000/mo**.

## 4. Peptide **clinic** OS — *book, educate, keep*
*Buyer: clinic owner / medical director. Cash-pay, considered purchase.*

| # | Module | Pillar | Form factor | Note |
|---|---|---|---|---|
| 1 | Intake / front desk | 1 Intake | 1 employee | Answers every call, books, runs intake. The classic on-ramp — and genuinely the bleeding wound. |
| 2 | Consult pre-brief + education | 4 Customer | 3 surface | The same thirty questions, answered before the visit. Clinician time goes to medicine, not explanation. |
| 3 | **Program adherence + refill engine** | 4 Customer | 2 headless | *The retention module, and the real money.* Titration check-ins, refill windows, lapse detection. **In this business revenue is retention, not acquisition** — which is exactly what the generic "you miss calls" pitch misses. |
| 4 | Labs coordination | 5 Ops | 2 headless | Baseline draw → results in → protocol review queued. |
| 5 | Owned-channel marketing | 3 Marketing | 1 + 2 | Ad platforms restrict this category, so email/SMS/referral **is** the channel, not a supplement. |

**Tier:** Suite → Operation — **$2,500–4,500 impl · $4,500–8,000/mo**.

## 5. **Telehealth clinic** OS — *multi-state throughput*
*Buyer: platform operator. Scarce resource is clinician time, not leads.*

Shares modules 1, 3, 4 above. What is **specific to telehealth**:

| # | Module | Pillar | Form factor | Note |
|---|---|---|---|---|
| 1 | **Licensure-aware routing** | 5 Ops | 2 headless | Patient's state → which clinicians may see them → who has capacity. The module a single-state peptide clinic never needs and a multi-state platform cannot operate without. |
| 2 | Async visit triage | 5 Ops | 1 + 2 | Questionnaire → completeness and coherence check → clinician opens a *prepared chart*, not a raw form. Directly multiplies clinician throughput, which is the P&L. |
| 3 | Signup→first-visit recovery | 2 Sales | 2 headless | Telehealth funnels leak hardest between paying and actually attending. |
| 4 | Documentation defensibility | 7 Company Brain | 2 headless | Every encounter's record complete and audit-ready by construction. |
| 5 | Eligibility / payer vs cash routing | 6 Back Office | 2 headless | Only if they take insurance; many do not. |

**Tier:** Operation → Command — **$3,500–5,000 impl · $6,500–10,000/mo**.

---

## 6. Gates and compliance — read before any approach

**This is a gated vertical, in the same class as yourco Care (gate #8) and Conduit (gate #9).** Not a
reason to avoid it — the constraint *is* the moat, exactly as UPL guardrails are for Conduit — but
nothing here goes to a real client without counsel.

- **AI never gives medical advice, dosing, or clinical interpretation.** Existing house rule (Care);
  applies unchanged to every module above. §3 module 5 and §4 module 2 are where it binds hardest.
- **Health claims / FTC substantiation** on anything patient- or buyer-facing.
- **HIPAA** wherever PHI is touched (§4, §5) — BAA required, and it shapes the stack.
- **State licensure and scope of practice**, including any controlled-substance rules that apply.
- **Verification liability** — the §2 module 3 surface makes a *claim about a claim*. Sample Product
  already carries this question at gate #10 (E&O on verification features); the same question lands
  here and the answer should be reused, not re-derived.
- **Platform ad restrictions** are a *client* constraint that shapes §4 module 5 — a marketing plan
  built on paid social would be dead on arrival.

⚠️ **Regulatory specifics in this space move fast and are NOT stated as fact anywhere in this spec.**
Compounding eligibility, "research use only" enforcement and telehealth prescribing rules have all
shifted in recent cycles. **Verify current guidance before any of it appears in a deck or a
proposal** — the credibility cost of being wrong in front of a lab owner who lives this is total.

## 7. Honest status

- **n=0 in this vertical.** No client, no engagement, no pilot. Every module above is a scope, not a
  build, and the tier prices are the standard ladder applied to it — not a quote.
- **The per-vertical marketing funnel is PARKED** (`decisions/2026-06-22_website-dial-back.md`). This
  is a *delivery scope*, deliberately not a vertical landing page, and nothing here should become one
  without un-parking that decision.
- **The parked peptide-clinics page pitches only "you miss calls."** True but generic; §4 module 3
  (retention) is the sharper wedge and is missing from it. Worth fixing if that page is ever revived.
- **The live move is §2**, because there is a warm relationship attached to it: Sample Contact, a friend,
  who owns a peptide testing company and has been cold for two months.
