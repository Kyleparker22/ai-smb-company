# Production — YourCo Explainer (homepage hero video)

**Owner:** Reed · **Date:** 2026-06-10 · **Status:** `script` — **awaiting the Founder's script approval before generation** (creative gate).
**Use:** the yourco.com homepage demo slot (replaces the landscaping-specific Descript video) + reusable for inbound / non-landscaping outreach.
**Format:** animated-only (Higgsfield scenes) + AI voiceover + captions (Descript). ~60–75 sec. Brand: indigo/cream/brass, calm/atelier, no buzzwords.
**Credibility gate:** animated faithfully — every capability shown is something yourco actually builds. No fabricated features.

## Script (VO + on-screen)
| # | Scene (Higgsfield, animated) | Voiceover | On-screen caption |
|---|------------------------------|-----------|-------------------|
| 1 | A small business: phone ringing unanswered, a quote half-written, an inbox filling. Calm, warm, not chaotic. | "Every business has work that eats the week. Calls you miss. Leads you mean to follow up. Drafts that pile up." | the work that eats your week |
| 2 | A nameplate / desk appears — a named "employee" takes a seat at the workshop. | "yourco builds you a digital employee. Named. Live in 48 hours." | a named digital employee · live in 48 hours |
| 3 | The employee answering, qualifying, booking, drafting — its own email inside the business. | "It does the job — answering, qualifying, booking, drafting, following up. Its own email, inside your business. Built around how *you* work." | built around your business — not a template |
| 4 | A small "approve" checkpoint — a draft held for a human's nod before it goes out. | "You approve what matters. It drafts and prepares; nothing customer-facing goes out without your say-so." | nothing goes out without your say-so |
| 5 | Behind-the-scenes gears (eval/watchdog/reliability) handled by yourco; the owner just sees the outcome. | "We own the reliability, the security, the keeping-it-good. You own the outcome — never the tokens, the models, or the infrastructure." | you own the outcome. we own the rest. |
| 6 | The brass Eval-Gate wordmark lockup resolves; tagline. | "We learn your business. AI does the work." | yourco · Book 30 min → yourco.com |

## Production steps (after script approval)
1. Generate scenes 1–6 via Higgsfield (Seedance/Veo/Kling), 16:9, brand palette, consistent animated style.
2. AI voiceover in Descript (calm, warm, male or neutral — match the landscaping demo's voice for consistency); assemble scenes + VO + captions; cream end-frame with the wordmark lockup.
3. Export; host (Descript share link, like the landscaping demo).
4. **the Founder approves the cut** (creative gate) → register in `_asset_registry.md` (vertical = `generic`).
5. Webb swaps the homepage demo embed to this URL (replaces `share.descript.com/view/L6EdW0JYGQJ`).

## Generation log (2026-06-10) — script approved by the Founder; full-send approved
Explainer scenes submitted to Higgsfield (seedance_2_0, 16:9, 15s, 720p, ~67.5 cr each):
- Scene 1 (work piling up): `8a8ecf3b-9c90-4970-a463-e36d4953883d`
- Scene 2 (new hire arrives): ~~`fc056e65`~~ nsfw false-positive → **regen people-free** `b1059b43-0839-4f1f-8d75-a07f3d276b69`
- Scene 3 (employee at work): `181430b4-ed36-4b94-8028-631dc540eb1c`
- Scene 4 (approval checkpoint): ~~`ad0b6aa6`~~ nsfw false-positive → **regen people-free** `fc00382b-1bc6-4bfd-bba3-3fc885e4ad5f`
- Scene 5 (reliability under the hood): `0aa6a044-fc6d-46fc-bd99-ba9c4fc08eee`
- Scene 6 (brass end-frame, wordmark overlaid in Descript): `3a1cb15b-75bd-435d-9ee0-799836314d7a`
Status: scenes 1,3,5,6 done; 2 & 4 regenerating (the original approval/figure phrasings tripped Higgsfield's nsfw filter — reworded to objects+light, no people; flagged gens were not charged). Next: Descript VO + assembly + captions → host → the Founder approves → register + Webb embeds. **Scene 4's regen (`fc00382b`) is reused as the generic demo's scene 4** (same beat). Generic reuses scene 6 as its end-frame.

## ✅ PUBLISHED (2026-06-10) — pending the Founder's final cut approval
**Explainer cut:** https://share.descript.com/view/mIvvSqQZ5xk · 39s · word-free, voiceover-only (Descript "Grace"), ambient music bed, 0.6s crossfades, **no on-screen text**.
- Descript project: `cfe7ee36-9c13-4d26-94c0-620d13331aaa`.
- **Word-free clip set:** 01 `6e78ee86` · 02 `82ec645f` · 03 `ef0ee3e3` · 04 `fc00382b` (reused — nsfw blocked the hardened re-render) · 05 `796b781e` · 06 `3a1cb15b` (reused — same).
- Big learning this run → folded into `agents/Reed/02_build.md`: **AI renders text as gibberish; hard-forbid all text in prompts, add real text only in post.** Word-free + VO-only is the new default.
- **Watch-item for the Founder:** scenes 4 (approval card) + 6 (end-frame) are reused NSFW-passed clips — confirm they read clean (no stray text) in the cut; if not, re-render with new wording.

## Generic demo — also published
**Cut:** https://share.descript.com/view/cYRYnooGi4Y · 27s · same treatment. Project `d75e5037-767b-47db-adf4-abd50496d00f`. Clips: 01 `df8698ec` · 02 `51c83034` · 03 `f858ef92` · 04 `fc00382b` · 05 `0f866925` · 06 `3a1cb15b`.

## Open for the Founder (approve to proceed)
1. **Watch both cuts** → approve (Reed's creative gate) or give notes.
2. On approval: register both in `_asset_registry.md` (vertical = `generic`); **Webb swaps the homepage demo embed** off the landscaping video to the explainer.
3. Decision held: explainer = homepage hero; generic demo = secondary "see it work."
