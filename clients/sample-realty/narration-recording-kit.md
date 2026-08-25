# Narrated tours — Kimi's recording kit

The site plays a ~60-second voiceover over each listing's cinematic tour. The scripts are
written and live on each listing page ("Read the 60-second script" — it doubles as a
teleprompter). This is how a recording gets from Kimi's phone onto the site.

## How Kimi records (5 minutes per listing)

1. **Open the listing page on your phone** → tap "Read the 60-second script."
2. **Open Voice Memos** (iPhone) — phone 6–8 inches from your mouth, quiet room, car
   parked with the engine off is honestly a great booth.
3. **Read the script like you're on the phone with a buyer** — warm, unhurried.
   A small stumble is fine; natural beats polished. Aim for 55–65 seconds.
4. Record it **twice**, keep the better take.
5. **Send the voice memo to the Founder** (AirDrop, text, or email — the file will be
   called something like "New Recording 3.m4a"). Feel free to edit the script
   first — your words beat our words.

## How it gets on the site (the Founder, ~30 seconds)

Rename the file to **`narration.m4a`** and drop it into that listing's photo folder:

```
site/assets/listings/<listing-slug>/narration.m4a
```

e.g. `site/assets/listings/1208-high-brook-drive/narration.m4a`

That's it — no conversion, no code. The player checks for `narration.m4a`, then
`.mp3`, then `.wav`; the moment the file exists, the "Play the narrated tour"
button appears on that listing. Until then the page shows "Narration coming
soon" with the readable script.

**At engagement (the operated version):** Kimi texts the voice memo to the intake
number; the runtime renames, drops, and publishes it — the whole step above
disappears.

## The five scripts

The canonical copies live in `site/listings-data.js` (`voScript` on each listing)
and render on each listing page. Word counts target ~60s at a relaxed pace.
Facts only — every number is from the Canopy listing.

1. **1208 High Brook Drive** — porch hook, refinished hardwoods, main-level guest
   suite, half acre, Cuthbertson, open house Aug 8, "launching at seven twenty-four nine."
2. **12727 Bullock Greenway Blvd** — walk-to-Blakeney hook, three stories, LVP,
   flexible lower-level suite, "listed at four thirty-five."
3. **9725 Mattforest Circle** — Ballantyne move-in-ready, granite → fireplace flow,
   renovated primary bath, Ardrey Kell zone, "three fifty-nine nine."
4. **1210 Sheldon Brook Lane** — Indian Land value story, quartz + fresh updates,
   paver patio, 10/10 elementary, SC taxes, "two seventy-three five."
5. **11264 Hyde Pointe Court** — first-floor living, covered patio, first-home-or-
   investment angle, PM division close, "at two twenty."

Retired: the AI demo voice (Maya/seed_audio) — the Founder 2026-08-04: "too robotic."
Real voice only on this surface from here.
