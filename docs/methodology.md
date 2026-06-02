# The Session Briefing Method

_Continuity for AI-assisted work — and why a markdown file beats a better memory._

## Cold starts are a tax you pay every session

Every time you open a fresh session with an AI assistant on a real, multi-week project, you pay a tax. You re-explain what the project is. You re-derive what's already been decided. The assistant, helpfully and confidently, reopens a question you closed three sessions ago. Work gets duplicated. Worst of all, a change made today quietly contradicts a constraint locked last week — and nobody notices, because the constraint lived only in a conversation that's now scrolled off.

The instinct is to wait for the tooling to fix this — bigger context windows, better memory features. But the problem isn't really capacity. It's that **project state is a distinct thing that deserves a distinct home**, maintained deliberately, in a form a fresh session can absorb in seconds. That home is a session briefing.

## The deeper failure mode: forgetting what a change _touched_

Here's the observation that shaped this whole method. Across dozens of multi-session projects, the most damaging failure was never "the assistant forgot what we did." That's recoverable — you can see the diffs. The damaging failure was **forgetting what a change touched**: the downstream view that depended on the data model you just altered, the content authored against the validation rule you just relaxed, the decision in session 3 that the change in session 12 silently violated.

A good briefing is built to catch exactly this. It doesn't just record _what happened_; it records _decisions and their rationale_, _open questions and what they block_, and _discrepancies between what the docs say and what the code does_. Those are the load-bearing pieces of continuity, and they're precisely what gets lost when state lives in conversation.

## One boundary keeps everything lean

The method rests on a single rule: every fact about a project is either **timeless** or **timestamped**.

- **Timeless** — what the project is, how to build and run it, conventions, environment quirks, load-bearing gotchas. True whenever you read it. This belongs in the **context file** your harness already auto-loads (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`).
- **Timestamped** — current status, what changed this session, decisions and why, next priorities, open questions, spec-vs-code drift. True _as of now_. This belongs in the **briefing**.

That's the whole trick, and it's load-bearing in both directions. If "how to run the tests" drifts into the briefing, the briefing rots into a second README. If a "current status — do not relitigate" block accumulates in the context file, that file balloons until it's too heavy to auto-load usefully. Keep the seam clean and both documents stay sharp.

(A third category — your personal working style, how _you_ like to collaborate — belongs in neither. It goes in the assistant's persistent memory, written once. Re-narrating it per project is how you end up with stale, half-localized clones that actively mislead.)

## The iron rule: never drop a section

AI assistants have a strong, well-meaning instinct to "tighten up" a document — to drop a section that seems irrelevant to the task in front of them. In a session briefing, that instinct is destructive. The onboarding decision that looks irrelevant while you're deep in a payments integration is exactly the context a future session will need.

So the method enforces an iron rule: **every section carries forward, every version.** Only one section — "This Session" — is replaced wholesale each update; everything else is updated in place or left untouched, never removed. In the agent variant this is machine-checked: a validator diffs the new briefing against the last committed version and _fails_ if a section vanished. The discipline doesn't depend on anyone remembering it.

## From chat to agent: how the method evolved

The method started in chat. With no repo, no context file, and no git, a claude.ai briefing had to be **one self-contained document** carrying everything — thirteen sections, including a file inventory, working-style notes, and operational notes, because there was nowhere else for them to live. It worked, but it carried weight that a richer environment makes redundant.

Moving into coding agents changed the calculus. Now the project _has_ a context file (so timeless reference offloads there) and _has_ git (so version history is free, and the briefing can be plain markdown whose diffs read cleanly session-to-session). The agent variant is, in effect, the chat briefing **minus what the environment now provides** — thirteen sections collapse to nine — **plus** one thing the environment made newly possible: the constellation.

(One small but real lesson from that move: the chat variant historically produced `.docx`. It shouldn't anymore. Markdown is token-cheap, diffable, and editable in place — and chat interfaces convert uploaded `.docx` to markdown on ingest anyway, so the binary format bought nothing but a stale file extension and wasted turns. Both variants are markdown now.)

## The constellation: from one project to a portfolio

A single briefing solves cold starts for one project. The leverage shows up when you run _many_ related projects — a platform and its services, a product and its app, a monorepo of packages.

Maintaining a hand-written "where does everything stand" document across a portfolio is a losing game; it's stale the day after you write it. So the method derives it instead. Each child briefing declares a **parent**. A `rollup` step scans every child and regenerates a **component matrix** inside the parent — each component's version, status, layer, and a link — so the parent view is correct _by construction_, not by anyone remembering to update it. And a lightweight `[surface]` tag lets a child push a specific blocker or decision up into the parent's attention list, so working head-down inside one service still keeps the portfolio's view honest.

This is the part worth keeping front and center. Cross-session continuity is table stakes. **Cross-_project_ continuity** — a live, derived map of a whole constellation of work — is the real differentiator, and it costs almost nothing once the per-project briefings exist.

Crucially, you don't start here. You start with one briefing for one repo. You add a parent when a second project appears. You grow into the constellation. The on-ramp is gentle on purpose; the ceiling is high on purpose.

## The disciplines that don't automate

A script can scaffold a briefing, stamp a version, wire a pointer, and regenerate a matrix. It cannot do the part that actually matters, which stays with the human-and-assistant pair:

- **Downstream-impact checking** — before a change, trace what it touches, and flag the ripples _before_ acting.
- **Discrepancy tracking** — when the docs and the code disagree, name the conflict and let a human adjudicate; never silently pick a value.
- **Decision-deadline flagging** — name a pending decision, identify the dependency it actually blocks, and say whether it can wait. Don't pressure for premature calls; don't let a blocking one slide.

The script handles the clerical, drift-prone mechanics so they execute identically regardless of which model is driving. The judgment is yours. That division — deterministic anchor, human judgment — is why the method holds up across models and harnesses instead of decaying into whatever the assistant felt like writing that day.

## What this is, and isn't

It isn't a platform, a service, or a dependency. It's a markdown document, a small dependency-free script, and a boundary you hold to. That's deliberate: the lightest thing that solves the problem is the thing you'll actually keep doing. Continuity is a habit before it's a tool, and the method is designed to make the habit cheap.

If you take one idea from this: **stop letting project state live in conversations.** Give it a home that's separate from your timeless docs, keep the boundary between them clean, never drop what a future session will need — and once you have that per project, roll it up across the constellation.
