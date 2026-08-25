# Video editing for Sample Realty — who does what

> **Decision (2026-08-20): yourco runs the footage editing. Kimi does not touch Descript.**
> Sample Realty is still a prospect — see `_README.md`. This describes how it would work.

## The split that matters

There are two kinds of video here and they are **not** the same job:

| | Who does it | Tool |
|---|---|---|
| **Photos → cinematic tour** | **Kimi, herself** | Listing Kit Builder — exports MP4 directly |
| **Filmed footage → edited video** | **yourco** | Descript |

The builder makes the tour from her photos and clips and now saves it as an MP4 she can post. She needs nothing else for that, and nobody else has to be involved.

Descript only earns its keep on footage of **someone talking** — a walkthrough, a piece to camera, a phone tour. That is where a transcript exists to edit, and it is the half yourco runs.

**The builder cannot call Descript, and should not.** It is a single HTML file with no server. Descript needs an API credential, and a credential cannot live in a file that gets emailed around — the same reason the publish token is pasted in rather than baked in. Uploading a video into the builder's Photos panel stores it locally for the tour. It sends nothing anywhere.

## The handoff: one shared folder

1. Kimi drops the footage into a shared Google Drive folder and says it's there.
2. yourco imports it into Descript **by URL** — Descript's importer takes Google Drive links directly, so there is no upload step, no file-size declaration, no PUT.
3. yourco prompts the edit in plain English and exports.
4. yourco sends back the finished file.

Setup is one folder and one link. No server, no scheduled loop, no credentials for Kimi.

## Running it (verified 2026-08-20 on the 2304 walkthrough)

```
import_media          → project_id + upload_urls   (or pass a Drive url and skip the upload)
wait_for_job          → transcription completes
prompt_project_agent  → natural-language edit, returns a job
wait_for_job          → agent finishes
export_transcript     → txt / srt, with timecodes
export_timeline       → the finished media
```

**Gotchas that cost time the first run:**

- **`file_size` must be the exact byte count.** Guessing it gets the upload rejected — read it with `stat -f%z`. Passing a Drive URL avoids the problem entirely.
- **One job at a time per project.** A second import while one is running is refused; `cancel_job` first.
- **Imported media is not on the timeline** unless you pass `add_compositions`, or ask the agent to place it. Until it is, `export_transcript` returns nothing.
- **`export_transcript` truncates** its response on long recordings even when the composition is full length. Pull SRT in ranges if you need all of it.
- Agent edits **cost AI credits** — the first placement call used 7.2.

## What this is genuinely good at

Anything the transcript can express:

- "Trim the silences." · "Remove the filler words."
- "Cut the last sentence, it trails off." · "End it where she finishes the sentence about the kitchen."
- "Make a 30-second version." · "Pull the three strongest lines."

**The first real run answered a question that had been handed back to the Founder unanswered:** where Kimi finishes saying *"…this stunning John Wieland estate"* — **00:00:17.567**. That could not be found by ear and it set the audio cut on the reel to the exact word boundary.

## What it is not good at

Judgement about **pictures**, which no API turns into five minutes:

- A better frame of her face — she is mid-word in most of them
- A stutter in a slow-motion shot
- "Show more of the golf simulator"

Those stay a person's eye. That is accepted, not a gap to close.

## ⚠️ Found by the transcript, still open

Kimi says **"Marvin, Your State"** on camera. Every document built so far says **Yourtown** — twelve files, plus the pamphlet, MLS copy, listing page and social captions. The zip 28173 is Yourtown; Marvin is the adjacent town and often the better-regarded name. This was already an open question in `_README.md`; the transcript proved the video and the paperwork disagree. **Kimi picks one, then it sweeps everywhere.**

## If this ever needs to be zero-touch

Wire it as a runtime loop per `.claude/skills/add-runtime-loop/`: watch the Drive folder, import on arrival, run the standard cleanup, post the link to Slack. Worth doing only once the volume justifies it — at a few listings a month, the shared folder is enough.
