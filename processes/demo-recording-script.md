# Screen-recording script — "how yourco works" (for sending someone)

> A tight storyboard so you can record a clean 3–4 minute walkthrough in one take and send the video. **You record** (Mac: press `⌘⇧5` → "Record Entire Screen" or a selected portion → Record; stop from the menu bar; the .mov saves to your Desktop → AirDrop/text it). Below is exactly what to open and say. Owner: the Founder.

## Before you hit record (setup, ~30 sec)
1. Start the cockpits: in Terminal, from the repo root → `./show.sh` (starts the website + HQ dashboard + CRM; auto-opens the website).
2. Open these tabs in order so you can just click across:
   - `send-package/yourco-how-it-works.html` (the story + live demo)
   - http://127.0.0.1:8791 (HQ dashboard)
   - http://127.0.0.1:8790 (CRM)
   - `agents/webb/pages/yourco-site-v2/instant-employee.html` (the product demo)
3. Close noisy apps / notifications. Then `⌘⇧5` → Record.

## The script (~3–4 min)

**1 · The idea (30s) — on `send-package/yourco-how-it-works.html`**
> "This is yourco — the AI business I've been building. The simple version: most companies hire people to answer the phone, book jobs, do admin. We build a business one named *AI employee* that does that — live in their tools in 48 hours. They own the result; they never touch the tech."

Scroll to the diagram:
> "Here's how it runs. I point a task, an AI does it — either when I ask, or on a schedule with no human — and everything saves back to one system that compounds. The 'employees' are defined roles, not separate robots."

**2 · See the product work (45s) — scroll to the demo (or the Instant Employee tab)**
> "This is the actual product — an AI front desk for a landscaper. Watch it take a call." *(let it play)* "It books the job, and — this is the important part — it *won't* quote a price or go off-script. It routes anything tricky to a human and I approve anything before it sends. That reliability is the whole business."

**3 · It runs itself (60s) — the HQ dashboard tab (:8791)**
> "And here's the company running itself. This is the live cockpit — every AI employee, the pipeline, finance, the daily loops. One of these loops already runs 24/7 on a server with no human — it does my Monday briefing, checks itself, and commits the work."

Switch to the CRM tab (:8790):
> "This is the sales pipeline — and these aren't fake: those landscapers were sourced by the system from real data, and it even built each one a personalized demo."

**4 · Where it's at (30s) — back to the status section**
> "Honest status: the system works and part of it runs autonomously today. The public side is built but switched off — I can't fully launch until a legal thing clears. So everything's ready for the day I flip the switch. That's where it is."

**5 · Close (10s)**
> "That's yourco — one human, a team of AI employees, one system that gets smarter every time it runs. Happy to show you any part live."

## After recording
- The `.mov` is on your Desktop → AirDrop / Messages / email it.
- Pair it with `send-package/yourco-how-it-works.html` if you want them to click through the demo themselves.
- `./show.sh stop` when done to shut the servers down.

> Tip: if a full video feels like a lot, just record segment 2 (the product demo) — it's the strongest 45 seconds and stands alone.
