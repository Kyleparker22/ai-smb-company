2026-06-17 — Prompt-the-prompter + rule sheets: two free generation practices to adopt now

Source: Brett Williams (DesignJoy, ~$1M/yr solo) interview, reviewed 2026-06-16 (`agents/brett/competitive-watch.md`). His two highest-leverage AI working practices — both free, both process-not-tool, both adoptable immediately across yourco's generation work.

Pattern:
1. **Prompt-the-prompter (meta-prompting).** Don't hand-write prompts for a creative/generation tool. Ask an LLM to *write the prompt for the target tool, naming the tool* — e.g. "write a Nano Banana Pro prompt that produces X," "write a Higgsfield/Seedance shot prompt for X," "write a Replit/Claude build prompt for X." The model knows the target tool's conventions (its parameters, ratios, style flags, the way it wants to be addressed) and outputs a more precise, tool-befitting prompt than a human writing blind. Brett: the prompt-engineer role is gone — use the AI to do the AI prompting. (Nuance he noted: ChatGPT tends to be stronger at *conversational/creative* prompt-writing, Claude at *technical/code* prompts — pick per task; both are fine.)
2. **Rule sheets (saved project rules the generation auto-references).** Keep a standing spec a project/tool references on *every* prompt, so house style is inherited automatically instead of re-typed. Brett's example: a Runway rule sheet with his default camera, lens, and color-grade — every video prompt picks it up. The yourco analogs already half-exist: Reed's standing Higgsfield character + palette + "text-in-post" rules, the scaffolder's golden build-pattern specs, `brand/writing-rules.md` for copy. Make them explicit, saved, and referenced every run.

Implication:
- **Reed (production):** before generating a Higgsfield/Seedance shot or a static image, have an LLM draft the *tool-specific* prompt naming the tool; and maintain an explicit "Reed rule sheet" (character ref, Midnight-Indigo/Cream/Brass palette, motion style, "all real text in post") that every shot prompt inherits — consistency across scenes for free.
- **Webb (design):** the screenshot-reference trick — attach a screenshot of a section you like and say "generate one like this" — beats describing it (Brett's simplest, most reliable design hack). Use it for site sections.
- **Kimi / scaffolder (build):** treat each off-the-shelf employee pattern as a rule sheet — a saved spec the build references so productized employees come out consistent and pre-evaled (`processes/off-the-shelf-employees.md`).
- **Every agent:** when delegating to a specialized tool/model, generate the tool's prompt with an LLM first. Cheap, repeatable quality lift.

Audience: Reed (production), Webb (design/site), Kimi + Kemba (scaffolder/build patterns), Katie (content generation), and generally any agent that drives a downstream generation tool.

Triggers: agent:Reed, agent:webb, agent:katie, agent:kimi, authoring a loop prompt, generation tool, rule sheet, prompt the prompter