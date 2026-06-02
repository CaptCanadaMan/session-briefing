---
name: agent-session-briefing
description: >
  Maintain project continuity across coding-agent sessions (Claude Code and any
  AGENTS.md-style harness) using a markdown session briefing that pairs with the project's
  agent context file (AGENTS.md, CLAUDE.md, GEMINI.md). Use when working in a local repo or
  project that spans multiple sessions, when the user asks to create or update a session
  briefing, status doc, or handoff note, when resuming prior work, or at the end of a
  session/context window to capture state for the next one. The briefing holds timestamped
  state — current status, decisions, next steps, open questions; the context file holds
  timeless operational reference. Briefings live in the session-briefings hub, one per
  project, with a pointer wired into each project's context file. For chat-based (claude.ai)
  projects that have no context file, use chat-session-briefing instead.
---

# Agent Session Briefing

A system for carrying project state across coding-agent sessions. The briefing is a markdown
document — the source of truth for *where a project is, what's been decided, and what's next* —
that a fresh session reads to resume cold without relitigating settled work.

This is the **agent variant** of the briefing method — for coding agents that run in a repo with
an **agent context file** (AGENTS.md, CLAUDE.md, GEMINI.md, …) and a git repo. It deliberately
offloads half of the old chat-era briefing to those. (The chat variant — `chat-session-briefing`
— keeps everything in one document because a chat project has no context file and no git.)

> **Context file = the timeless operational doc your harness auto-loads.** `AGENTS.md` is the
> cross-tool open standard (Codex, OpenCode, Aider, RooCode, OpenClaw, …); Claude Code uses
> `CLAUDE.md`; Gemini CLI uses `GEMINI.md`. The skill works with whichever you have — the scripts
> auto-detect an existing one and otherwise create `AGENTS.md`.

## Relationship to the context file — the boundary that keeps both lean

One rule decides where every fact goes:

- **Timeless → the agent context file** (AGENTS.md / CLAUDE.md / GEMINI.md — whatever your harness
  auto-loads). True regardless of when you read it: what the project is, repo layout, how to
  build/run/test, conventions, environment constraints, load-bearing gotchas. Living, overwritten
  in place, auto-loaded every session.
- **Timestamped → the briefing.** True *as of this session*: current status, what changed,
  next priorities, decisions and their rationale, open questions, spec-vs-code drift.

If you find yourself writing "how to run the tests" in the briefing, it belongs in the context
file. If you find a "current status" or "do not relitigate" block bloating the context file, it
belongs in the briefing. Keeping the boundary clean is what stops the context file from ballooning
and stops the briefing from drifting into a second README.

Personal working style and cross-project preferences are **neither** — they live in file-based
memory, written once. Do not re-narrate them per project (that is how stale clones happen).

## Where briefings live

One markdown briefing per project, in the hub:

```
~/.session-briefings/        ← its own git repo, pushed to your git remote (override: $SESSION_BRIEFING_HUB)
  <project>/
    SESSION_BRIEFING.md
    refs/                     ← linked visuals: mockups (.html), screenshots (.png), diagrams (.svg)
```

The briefing is markdown so its git diffs stay readable session-to-session. Visual/design
references are *linked*, not embedded — keep the state doc diffable; let an HTML mockup or PNG
live beside it in `refs/` and reference it from the relevant section.

Each project's context file carries a pointer to its briefing so a cold session is told where to
look. The `pointer` script keeps that wired automatically (below) — it auto-detects the context
file (AGENTS.md / CLAUDE.md / GEMINI.md) or creates `AGENTS.md` if none exists.

## The scripts do the mechanics; you do the judgment

`scripts/briefing.py` (Python stdlib, no deps) handles the clerical, drift-prone steps so they
execute identically regardless of which model or harness is driving. **Call it — don't do these
by hand:**

| Command | What it does |
|---|---|
| `python3 scripts/briefing.py new <project> [--parent P --layer L]` | Scaffold the hub dir + a v1.0 skeleton briefing, record the project dir in the briefing meta, wire the context-file pointer, and (if `--parent`) refresh the parent's matrix. |
| `python3 scripts/briefing.py bump <path>` | Increment the version and stamp the real date (header + a Version-History row). |
| `python3 scripts/briefing.py pointer <project>` | Idempotently insert/update the pointer block in the project's context file (auto-detected, or `--context-file`). |
| `python3 scripts/briefing.py rollup <parent>` | Regenerate the parent's constellation block — component matrix (version · layer · status · link) + surfaced blockers/decisions — from every child that declares it. |
| `python3 scripts/briefing.py check <path>` | Validate structure: all sections present, none dropped vs the prior committed version, version+date stamped, opening prompt non-empty, status tokens sane. |

You own everything the scripts don't: assessing status, writing the §3 narrative, capturing
decisions and rationale, prioritising next steps, detecting discrepancies, tracing downstream
impact. Those are judgment; scripting them would be brittle and miss the point.

The project dir defaults to your **current directory**; `new` records it in the briefing meta so
`pointer` keeps working even if the repo later moves. Pass `--project-dir` to point elsewhere,
`--context-file NAME` to force a specific context filename, and `--hub` (or `SESSION_BRIEFING_HUB`)
if the hub isn't at `~/.session-briefings`.

## Constellation tracking — parent, rollup & surfacing

A project made of sub-products (e.g. a platform + its services, or a monorepo of packages) tracks
as a **parent briefing + one briefing per segment**, so you can work inside a single sub-product and
the parent stays current without maintaining two docs by hand.

- **Declare the parent + layer.** Each child briefing carries a header meta line —
  `<!-- meta: parent=acme-platform | layer=OPEN-MIT | projectdir=~/code/acme-api | status=stable; v0.3.1 -->`.
  `new --parent acme-platform --layer OPEN-MIT` stamps it (and `projectdir` automatically); keep
  `status` (one-line headline) and `layer` current as you update.
- **The matrix is derived, never hand-maintained.** `rollup <parent>` scans the hub for every
  briefing declaring that parent and regenerates a script-managed **constellation block** in the
  parent's §2 — component · version · layer · status · updated · link. Run it after bumping any
  child. The parent is then correct by construction, not by anyone remembering.
- **Surface blockers/decisions upward.** Add a clean standalone line `[surface] <short note>` (prefix form — note *after* the tag, one line, never inside a table cell) in §4/§5/§6 of a child; the next
  `rollup` lists it under "Surfaced from components" in the parent. Untag when resolved — it drops on
  the next rollup.
- **`layer` is an optional free-form tag** for whatever cross-cutting dimension matters across your
  components — visibility, IP/open-core seam (e.g. OPEN-MIT / OPEN-Apache / COMMERCIAL / CLOSED),
  ownership, or maturity. It's surfaced in the matrix so the parent shows that dimension at a glance.
  Leave it `unset` if you don't need it.

Don't hand-edit between the `<!-- constellation:start -->` / `<!-- constellation:end -->` markers —
that region is regenerated wholesale on every rollup.

## Two modes

### Cold start — first briefing for a project
1. Gather the essentials (don't over-interview): what the project is, current phase, the major
   workstreams and their status, any decisions already locked, known dependencies.
2. `python3 scripts/briefing.py new <project>` to scaffold (run it from the project repo, or pass
   `--project-dir`). If the repo has no context file yet, it creates `AGENTS.md` with the pointer.
3. Fill the sections with real content. Several will be thin at v1.0 — that's fine; keep the
   headers.
4. `python3 scripts/briefing.py check <path>` and fix anything it flags.

### Continuation — updating after a working session
This is the common case.
1. Read the current briefing.
2. Apply the disciplines below (downstream-impact, discrepancy, decision-deadline) as you work.
3. `python3 scripts/briefing.py bump <path>` — version + date are now handled for you.
4. **Replace §3 (This Session)** with what was done this session — reference commit SHAs rather
   than re-narrating diffs; capture the *why*, the decisions, and anything that rippled.
5. Update §2 status, §4 next steps, §5 decisions (append-only), §6 open questions, §7
   discrepancies. Fill the Version-History summary that `bump` stubbed.
6. `python3 scripts/briefing.py pointer <project>` to ensure the context-file pointer is current.
7. If this briefing declares a `parent`, `python3 scripts/briefing.py rollup <parent>` to refresh the parent's constellation matrix + surfaced items.
8. `python3 scripts/briefing.py check <path>` — fix every error before declaring done.

### The iron rule
Every section carries forward. Only §3 (This Session) is replaced wholesale; all others are
updated in place or left unchanged — never dropped or "tightened up." `check` enforces this by
diffing against the prior committed version, so a dropped section *fails validation* rather than
relying on you to remember. (Without a git repo in the hub, `check` can only verify presence — it
can't diff against history; `git init` the hub to get the full guard.)

## Disciplines (these stay with you — runtime-agnostic)

**Downstream-impact checking.** Before a change, trace what it touches — data models, dependent
views, content authored against an old rule. Flag downstream effects to the user *before* acting;
record accepted ripples in §3. The most common multi-session failure isn't forgetting what was
done — it's forgetting what a change *touched*.

**Discrepancy tracking (spec vs code).** When docs and code disagree, the code is authoritative
unless the user says otherwise — and here you can *verify against the actual source*. Flag the
conflict in §7 with both sources named and the verdict; never silently resolve it. Carry the
entry until resolved.

**Decision-deadline flagging.** Name a decision, identify when it actually blocks progress (which
dependency), and say whether it can be deferred. Record deferred ones in §6 with their deadline.
Don't pressure for premature decisions; don't let a blocking one slide silently.

## Freshness / localization guard

When seeding a new project's briefing from another's, **localize every section** — never carry
another project's specifics. A briefing that still describes a different project's status,
directory, or decisions is worse than none: it actively misleads the next session. If you adapt
an existing briefing, rewrite each section for the new project and delete anything that doesn't
apply. (Stale, half-localized clones are a real, observed failure mode — don't create one.)

## What NOT to do

- **Don't put timeless/operational content in the briefing.** Build commands, repo layout,
  conventions → the context file (AGENTS.md/CLAUDE.md). The boundary is the whole point.
- **Don't re-narrate personal working style per project.** That lives in memory, written once.
- **Don't hand-edit the version or date.** Use `bump` — models miscount and misdate.
- **Don't drop or consolidate sections.** `check` will fail you; more importantly, future
  sessions need the context.
- **Don't embed large visuals in the briefing.** Link them from `refs/` so diffs stay readable.
- **Don't resolve discrepancies silently**, and **don't declare done without running `check`.**

## References

- `references/briefing-template.md` — the canonical section structure and what each section holds.
- `scripts/briefing.py` — the mechanics (new / bump / pointer / rollup / check).
- `scripts/stop-validate.sh` — optional Stop-hook validator (warn mode). Register it in
  settings.json to run `check` automatically at turn-end; flip its final `exit 1` to `exit 2`
  to turn warnings into a hard gate.
