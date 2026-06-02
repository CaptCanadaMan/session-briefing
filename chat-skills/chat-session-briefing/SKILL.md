---
name: chat-session-briefing
description: >
  Maintain continuity across multi-session projects in a chat interface (claude.ai web or
  desktop) using a single structured markdown session briefing. Use this skill whenever the user
  is working on a project that spans multiple conversations, whenever they ask to create or update
  a session briefing, project status document, or context handoff note, or whenever they mention
  resuming work from a previous session. Also trigger when the user starts a new multi-step project
  and needs a system for tracking progress across sessions — even if they don't explicitly say
  "session briefing." If the user references prior sessions, version histories, or asks to "pick up
  where we left off," this skill applies. Covers both creating the first briefing for a new project
  and updating an existing one. For coding agents that run in a repo with a context file
  (AGENTS.md/CLAUDE.md) and git, use agent-session-briefing instead.
---

# Chat Session Briefing

A system for maintaining project continuity across Claude sessions. Session briefings are
structured documents that serve as the primary source of truth when resuming work — they
tell a fresh Claude instance everything it needs to know to be productive immediately.

This is the **chat variant** — for claude.ai (web or desktop), where there's no repo, no
`CLAUDE.md`/`AGENTS.md`, and no git, so the briefing is a single self-contained markdown document
that holds everything. (For a coding agent that runs in a repo with a context file + git, use
`agent-session-briefing` instead — it offloads timeless reference to the context file and adds a
cross-project *constellation* rollup.)

## Why this matters

Claude has no memory between sessions. Without a well-maintained briefing, every new session
starts cold — context is lost, decisions get revisited, work gets duplicated, and downstream
effects get missed. A good session briefing eliminates this. It is the project's institutional
memory.

## Two modes

This skill operates in two modes:

1. **Cold start** — The user is beginning a new multi-session project. Create the first
   briefing document (v1.0) by interviewing for context, then producing a structured doc.

2. **Continuation** — The user has an existing briefing. When updating, follow the carry-forward
   rules precisely and produce an incremented version.

Detect which mode applies from context. If the user loads a briefing document or references
a prior version, you are in continuation mode. If they are starting something new, you are
in cold start mode.

---

## Cold start: creating the first briefing

When starting a new project, gather enough context to produce a useful v1.0. Do not interview
exhaustively — get the essentials and produce a first draft quickly. The document will be
iterated.

### Minimum information needed

- What is the project? (one-paragraph summary)
- What is the broader context? (ecosystem, platform targets, constraints)
- What are the major workstreams or phases? (even a rough list)
- What is the current status of each? (not started / in progress / complete)
- Are there any decisions already made that should be locked in?
- Are there known dependencies between workstreams?
- What files or specs already exist?

### Producing the first briefing

Read `references/briefing-template.md` for the canonical section structure.
Produce the briefing as a markdown (`.md`) file. Use the template structure exactly —
every numbered section must be present even if some are minimal at v1.0.

For a brand new project, several sections will be thin:
- §3 (This Session) captures what was discussed/decided in the current conversation
- §7 (Discrepancies) may be empty — include the section header with "None identified."
- §8 (File Inventory) lists whatever exists so far
- §9 (Working Style Notes) starts with observations from this first interaction
- §10 (Operational Notes) captures any tooling or environment constraints mentioned

The Session Opening Prompt (§12) is especially important at v1.0 — it is what the user will
paste into the next session to get Claude oriented.

---

## Continuation: updating an existing briefing

This is the more common mode. The user has completed work in the current session and wants
the briefing updated.

### The iron rule: every section carries forward

When producing an updated briefing, EVERY numbered section from the prior version must
appear in the new version. This is non-negotiable. Sections may be updated, but they are
never removed or consolidated.

The only section that gets fully replaced is **§3 (This Session)**. All other sections
are carried forward — updated where relevant, unchanged where not.

This rule exists because Claude has a tendency to "tighten up" documents by dropping sections
it considers redundant or less relevant to the current task. In a session briefing, this
destroys context that future sessions will need. Every section earned its place. Carry it.

### Update procedure

1. **Increment the version number.** Follow the project's versioning convention. If the
   prior version was v2.7, the new version is v2.8.

2. **Update the subtitle** with a brief description of what this session focused on.
   Example: `v2.8 — Updated at close of pre-submission cleanup & notification wiring session`

3. **Update §2 (Current Status)** — Refresh the status table. Be unambiguous: use
   COMPLETE, IN PROGRESS, NOT STARTED, PENDING, or UPDATED vX.X. Never use vague
   phrasing like "mostly done" or "nearly there."

4. **Replace §3 (This Session)** — Document what was produced, what changed, what
   decisions were made, and what files were affected. Use sub-sections (§3.1, §3.2, etc.)
   for each distinct piece of work. Be specific: name files, describe changes, note
   implementation details that a future session would need to know.

5. **Update §4 (Next Steps)** — What should the next session focus on? What is the
   recommended priority order? Are there any blockers?

6. **Update §5 (Design Decisions)** — If any new decisions were made this session,
   add them. Never remove prior decisions.

7. **Update §7 (Discrepancies)** — See discrepancy tracking below.

8. **Update §8 (File Inventory)** — Add or update entries for any files created or
   modified this session.

9. **Update §9–§10** — Only if new working style observations or operational notes
   emerged this session.

10. **Update §11 (Quick-Start)** — Refresh the verification steps to reflect current
    project state.

11. **Update §12 (Session Opening Prompt)** — Rewrite to reflect the new status and
    next priorities.

12. **Append to §13 (Version History)** — Add a one-line entry for this version.

---

## Downstream impact checking

This is a core discipline, not an optional extra. Before proposing or implementing any
change during a session:

1. **Identify what the change touches.** Which files, which specs, which design decisions?

2. **Trace downstream.** If this change alters a data model, what views depend on it?
   If it changes a pricing tier, what copy references that price? If it changes a validation
   rule, what content was authored against the old rule?

3. **Flag before acting.** Tell the user what the change will affect downstream before
   making it. Do not optimise for the current task at the expense of the broader system.
   The user may still want to proceed — but they should see the full picture first.

4. **Record in the briefing.** If downstream effects were identified and accepted, note
   them in §3 so future sessions know what rippled.

This matters because the most common failure mode in multi-session projects is not
forgetting what was done — it is forgetting what a change *touched*. A decision made in
Session 12 that contradicts a design locked in Session 3 is invisible to a fresh Claude
instance unless the briefing tracks it.

---

## Discrepancy tracking

When multiple spec documents exist, they will eventually contradict each other. This is
normal and expected — specs are written at different times and not always updated in sync.

### Rules

- When you encounter a conflict between documents, **flag it explicitly** in §7 with
  both sources named, the conflicting values stated, and which is authoritative.
- The most recently updated document is assumed correct unless the user says otherwise.
- Carry the full discrepancy table forward across all briefing versions. Only remove
  an entry when the discrepancy has been resolved (both docs now agree or one has been
  formally superseded).
- Do not silently resolve discrepancies by picking a value. Name the conflict and let
  the user confirm.

### Discrepancy entry format

| Discrepancy | Incorrect (source) | Correct | Resolution status |
|---|---|---|---|
| Free tier weekly cap | UX Flow v1.0: '5 missions/week' | 3 missions/week — Core Data Model v1.3 | Carried — code uses correct value |

---

## Decision-deadline flagging

Not every decision needs to be made immediately. When a question arises during a session:

1. **Name the decision** clearly.
2. **Identify the actual deadline** — when does this decision block progress? Name the
   specific dependency. Example: "This needs to be resolved before the StoreKit integration
   begins, which is Step 7."
3. **If it can be deferred, say so.** Do not pressure for premature decisions. Record the
   open question in §6 with its deadline.
4. **If it blocks the current task, say so.** Make clear that progress cannot continue
   without a call on this.

---

## Quick-start prompts

Every briefing must end with a session opening prompt (§12). This is a pre-written message
that the user can paste into a new Claude session to get oriented immediately. It should:

- State the project name and what it is (one sentence)
- Reference which briefing version to load
- Summarise current status in 1–2 sentences
- State next priorities
- List the key context documents to load

The prompt should be self-contained enough that a Claude instance reading it knows exactly
what to do without further instruction.

---

## File format and conventions

- Produce session briefings as **markdown (`.md`) files.** Markdown keeps the briefing
  token-cheap, diff-friendly, and editable in place; claude.ai converts uploaded `.docx` to
  markdown on ingest anyway, so authoring `.docx` only adds a stale-extension mismatch and wasted
  turns. (Earlier versions of this method produced `.docx`; markdown supersedes it.)
- Use supplementary formats (HTML, interactive visualisations, spreadsheets, code files)
  when they communicate more effectively than a document — but the briefing itself is
  always markdown.
- The briefing is the **primary source of truth** for project state. Supplementary
  documents provide deep-dive detail. The briefing summarises what matters and points
  to the detailed docs when needed.
- *(Optional)* If you keep briefings private, add a `Confidential — Internal Use Only` line to
  the header — it's optional, not part of the method.

---

## What NOT to do

These are failure modes observed across 20+ sessions of real use:

- **Do not silently drop sections** when updating a briefing. Even if a section seems
  irrelevant to the current task, it contains context a future session will need.

- **Do not "tighten up" the document** by consolidating sections. The structure is
  intentional. Every section has a purpose.

- **Do not optimise the briefing for the current task.** The briefing serves ALL future
  sessions, not just the next one. A section about onboarding decisions still matters
  even when you're deep in StoreKit integration.

- **Do not propose changes without checking downstream.** This is the single most
  common quality failure in multi-session work.

- **Do not resolve discrepancies silently.** Always flag, always let the user confirm.

- **Do not make the Quick-Start prompt generic.** It should be specific enough that
  following it step-by-step verifies the project is in the state the briefing claims.
