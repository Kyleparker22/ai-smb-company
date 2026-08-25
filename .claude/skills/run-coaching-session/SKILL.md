---
name: run-coaching-session
description: Run a live practice session with a connector or advisor — pull their plan, put them through drills, judge each answer against the authored rubric, record it. Use when the Founder says "coach X", "run a session with X", "let's practice", or when onboarding someone into a role.
---

# run-coaching-session — you are the judge, the engine is the scorekeeper

## When
the Founder asks to coach or practise with a named person in a role. **NOT** for writing new curriculum
(that's editing the role's `*-training/` folder) and **NOT** for partners — `coach.py` refuses that
role and the refusal is correct; see its `why_not`.

## The split, and why it matters
`crm/coach.py` decides **what to practise and in what order**, and stores **what happened**. It never
judges. **You judge** — reading a free-text answer against an authored rubric is the one part that
needs a model, and everything around it is deterministic on purpose.

## Steps (Cowork or the Slack control surface — needs Bash)
1. **Get the plan.**
   ```
   python3 crm/coach.py session --role <connector|advisor> --who "<name>"
   ```
   Returns: the role's definition, an ordered plan (re-practise first, then new), and `cannotSee` —
   the list of things this coach cannot know. **Read `cannotSee` before you open your mouth**; it is
   what stops you inventing a benchmark.
2. **Run one drill at a time.** Give them the `prompt` and nothing else. **Do not read out
   `looks_like` first** — that is the answer key, and showing it turns practice into recitation.
3. **Make them actually say it.** For anything that is a spoken move — an intro, an objection, a
   price refusal — require the words, out loud or typed verbatim. "I'd explain that we don't quote"
   is not an answer; *"I genuinely don't quote — that's the Founder's side"* is.
4. **Judge against the rubric, not your taste.** `looks_like` is the bar, `fails_if` is the
   disqualifier. If `fails_if` is triggered it is a **missed**, no matter how good the rest was —
   those clauses encode rules that do not bend (quoting a price, inventing a client, sending directly).
5. **Say the hard thing.** Then record it:
   ```
   python3 crm/coach.py record --role <role> --who "<name>" --drill "<id>" \
     --verdict <solid|shaky|missed> --note "<what the answer did>"
   ```
   **Do not soften a missed into a shaky.** The whole value of this is the sentence a polite coach
   would not say — and the record is what makes the next session sharper than the last.
6. **Close on one thing.** Name the single move to work on before next time. Not three.

## The rules that make the record safe to keep
- **Write the note as what the answer DID, never as a judgement of the person.** "Quoted a price" is
  a record; "doesn't listen" is not, and this file persists in the repo (`loops/_coach/_README.md`).
- **Never invent a benchmark.** n=0 connectors, n=0 advisors, n=0 signed clients. You cannot say
  "most connectors get this", "that's above average", or "top performers do X" — there is no
  population. Coach against the *documented rule*, which is the only thing that is actually true.
- **A drill is not a test they can fail out of.** Nothing here gates a rung; `connector_training.py`
  does that separately, on lessons and CRM evidence. Say so if they ask, because they will.

## Gotchas
- **Reading the rubric aloud.** The most common way to waste a session.
- **Coaching material the curriculum does not teach.** Every drill maps to a lesson; if you find
  yourself teaching something with no lesson behind it, that is a curriculum gap to write up, not a
  drill to improvise.
- **Headless loops cannot run this** — the approval gate denies Bash, and a coaching session is a
  conversation anyway. Cowork or a Slack channel; never a timer.
- **Partner sessions.** `coach.py` exits non-zero and explains why. Do not work around it by running
  advisor drills on a partner — the refusal is about who may author partner duties, not about content.

## Canonical docs
`crm/coach.py` (the engine and its refusals) · each role's `*-training/_drills.json` (the rubrics) ·
`loops/_coach/_README.md` (what the record is and why it is committed).
