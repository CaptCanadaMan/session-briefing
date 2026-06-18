# Session Briefing

**Short version:** Your AI coding tool forgets where your project was between sessions. Session Briefing keeps a short file that says where things stand right now - what's done, what was decided, what's next - read at the start of a session and updated at the end. Working across lots of repos? Each one's file rolls up into a single overview, and you only load the part you're working on. That's the whole thing; the rest is detail.

---

A continuity layer for long-running AI agent work. It gives a project a place to record the state that changes over time, kept separate from the context that doesn't.

## The core idea

A normal `CLAUDE.md` or `AGENTS.md` holds persistent context: what the project is, how it's built, the conventions, the constraints. That's true whenever you read it, with no real sense of time. It's the right home for things that don't change from one session to the next.

What it handles badly is the part that changes constantly: where the work stands today, what got decided this week, what's blocking right now. That state is only true as of this moment. Stuff it into the persistent context file and the file bloats, goes stale, and the current status gets buried in it.

Session Briefing gives that timestamped state a file of its own. Persistent context stays in `CLAUDE.md`. Current state lives in `SESSION_BRIEFING.md`. Git keeps the history. Each kind of information sits where it belongs, and none of them has to do another's job.

That split is the core difference: a dedicated, time-aware status layer, which is something the traditional context file was never built to be.

## What goes where

**Persistent context** → `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`
- architecture, build/run/test, conventions, constraints, repo structure
- true regardless of when you read it

**Timestamped state** → `SESSION_BRIEFING.md`
- current status, active work, decisions and rationale, blockers, open questions, spec-vs-code drift
- true as of this session, updated every session

**History** → Git
- commits, diffs, the full trace of how it got here

## The briefing stays small

A briefing is maintained, not accumulated. At the end of a session you update it to reflect the new current state; you don't append to a log. So it always represents where things are now, not a transcript of every session that got you there. That matters at scale: a project can run for months across hundreds of sessions and its briefing is still a short, quick read. If you need the history, that's what Git is for.

## Scaling across many repos (constellations)

This is where it earns its keep on large, long-running systems.

A big project rarely lives in one repo. So each repo keeps its own briefing, and they link up to a parent. A rollup regenerates an overview in that parent: every component's version, status, and blockers, derived from the children rather than maintained by hand. When something in one repo is blocking another, you tag it and it surfaces in the parent's view.

Two things come out of that:

**Scoped sessions that don't lose the plot.** You can sit down and work on a single component in isolation, with its own standalone briefing as the context for that session, without holding the whole system in your head. The parent rollup keeps that piece connected to the bigger picture, so scoping down doesn't mean losing track of how it fits into the project.

**Context that scales with the task, not the project.** Starting a session on one part of the system loads that part's briefing, which is a focused, manageable amount of context, not the entire multi-repo project's state. The cross-cutting view sits one level up for when you want it. Information is released progressively, so opening a fresh session on a slice of work doesn't pull the whole project into the context window.

Together with briefings that stay current-state instead of growing into logs, that's what keeps a system coherent across many repos, many sessions, and long stretches of time, without the context bloat that scale usually brings.

## File structure

Each project has a single briefing, stored in a central hub:

```
~/.session-briefings/<project>/SESSION_BRIEFING.md
```

Each project's context file carries a pointer to its briefing.

## CLI

Managed by a small Python script (`briefing.py`, standard library only).

Create a briefing:
```
briefing new <project>
```
Increment the session version:
```
briefing bump <path>
```
Wire the context file to its briefing:
```
briefing pointer <project>
```
Validate structure:
```
briefing check <path>
```
Roll up multiple repos:
```
briefing rollup <parent>
```
Aggregates state across linked project briefings.

## Workflow

**Start of session** - load `SESSION_BRIEFING.md` and review current status, decisions, constraints, and open questions.

**During the session** - track new decisions, architecture changes, discrepancies between code and docs, and cross-system impacts.

**End of session** - update the briefing: replace the session section (§3), refresh status, decisions, open questions, blockers, and discrepancies, then run `briefing check`.

## Design principles

- State is transient; context is stable. Keep them in separate files.
- The briefing holds current truth, not a running log.
- Git is the record of what happened; the briefing is what's true now.
- Context scales with the scope you're working on, not the size of the whole project.
- Explicit structure stops a briefing from decaying into freeform narrative.
- Discrepancies between code and docs are tracked openly, not silently resolved.
- It's model-agnostic and platform-agnostic.

## What it isn't

- a notes app or running journal
- a memory system
- a chat summarizer
- a changelog generator
- a prompt framework
- a replacement for your docs

It just tracks current project state across sessions.

## Why this exists

On long-running projects, the model can usually do the work fine. What slips is the shared picture of where the system stands, so the agent ends up rebuilding context every session. Session Briefing keeps that picture in one place, and keeps it cheap to read even after a project has grown across many repos and sessions, so complex work can resume without reconstructing it first.

## Summary

Session Briefing fills the gap between your context files (what the system is) and Git (what happened): a single, maintained record of where the project stands right now, one that stays coherent and quick to read even across many repos and a long run of sessions.
