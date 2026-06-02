---
name: setup-session-briefing
description: One-time guided setup for agent-session-briefing — creates the briefings hub, scaffolds your first briefing, and wires the continuity pointer into this repo's context file. Run this before first use of agent-session-briefing, or when you want to add a project to the constellation. Walks you through hub location, single-vs-constellation, and the context file, then scaffolds it for you.
disable-model-invocation: true
---

# Set up Session Briefing

Get from zero to a working session briefing for this project — and, if you want it, a multi-project
constellation. This is a **prompt-driven** skill: explore, present what you find, confirm with the
user, then run the scaffolding. Don't dump every question at once; walk through them one at a time.

Assume the user is new to the method. Each decision below opens with a short explainer.

> The mechanics are in the sibling `agent-session-briefing` skill's `scripts/briefing.py`
> (Claude Code: `~/.claude/skills/agent-session-briefing/scripts/briefing.py`). Call it `BP` below.

## 1. Explore

Read the current state — don't assume:

- **Hub** — is `$SESSION_BRIEFING_HUB` set? Does `~/.session-briefings/` exist? Is it a git repo?
- **Project repo** — what's the current directory? `git remote -v` and `git status`. Is there a
  context file (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) at the root? Does it already contain an
  `<!-- agent-session-briefing -->` pointer block?
- **Existing briefing** — does `<hub>/<project>/SESSION_BRIEFING.md` already exist? (If so, this is
  an update, not a setup — point the user at the `agent-session-briefing` skill instead.)
- **Constellation hint** — are there sibling repos that look related (a monorepo, a platform +
  services)? Note them; you'll offer a parent in Section B.

## 2. Present findings, then walk the decisions one at a time

Summarise what's present and what's missing. Then go section by section — present, get the answer,
move on. Don't pick for the user where a real choice exists.

**Section A — Hub location.**

> Explainer: The "hub" is one git repo that holds all your session briefings, one folder per
> project, separate from your code. Keeping it separate (not inside each repo) is what lets one
> parent briefing roll up many projects. Default: `~/.session-briefings/`.

- **Default** `~/.session-briefings/` — fine for almost everyone.
- **Custom path** — offer if they want it elsewhere (e.g. a synced/backup location). It's set via
  the `$SESSION_BRIEFING_HUB` env var or `--hub`; mention they'll want it consistent across sessions.
- Recommend they `git init` the hub (and add a remote) so they get version history + hook validation.
  Offer to do it.

**Section B — Single project or a constellation?**

> Explainer: If you're tracking one project, you just need one briefing. If you have several
> related projects (a platform and its services, a monorepo of packages), you can give them a shared
> **parent** briefing that auto-aggregates their status into one view. You don't have to decide
> forever — you can add a parent later.

- **Single** — just scaffold this project's briefing. (Most people start here.)
- **Part of a constellation** — ask for the parent's name. If the parent has no briefing yet, offer
  to create it too. This project will declare `--parent <name>`; optionally a `--layer` tag (a
  free-form dimension like visibility/ownership/maturity — leave unset if unsure).

**Section C — Context file.**

> Explainer: The briefing pairs with your project's "agent context file" — the timeless doc your
> harness auto-loads (`AGENTS.md` is the cross-tool standard; Claude Code uses `CLAUDE.md`; Gemini
> CLI uses `GEMINI.md`). Timeless reference (build/run/conventions) lives there; timestamped state
> (status/decisions/next steps) lives in the briefing. The setup wires a one-line pointer from the
> context file to the briefing so a cold session knows where to look.

- If exactly one context file exists, use it (confirm).
- If several exist, ask which one the harness they use actually reads.
- **If none exists**, the scaffolder creates `AGENTS.md` (the standard) with the pointer. Offer that,
  or let them pick a name with `--context-file`.

**Section D — Stop-hook validator (optional, Claude Code).**

> Explainer: An optional Stop-hook runs `briefing.py check` at the end of each turn and warns if a
> changed briefing is malformed (e.g. a section got dropped). Warn-mode by default; can be a hard gate.

- Offer to register `agent-skills/agent-session-briefing/scripts/stop-validate.sh` in `settings.json`
  under `hooks.Stop`. Skip if they'd rather not touch settings. (This one's Claude-Code-specific.)

## 3. Confirm, then scaffold

Show the user exactly what you'll run, then do it:

1. Ensure the hub exists; `git init` it if new and they agreed.
2. Scaffold the briefing — from the project repo (or pass `--project-dir`):
   - Single: `python3 BP new <project> [--hub <hub>] [--context-file <name>]`
   - Constellation: add `--parent <parent> [--layer <tag>]` (and `new` the parent first if needed).
3. Confirm the pointer landed in the context file (or that `AGENTS.md` was created with it).
4. If a parent is involved: `python3 BP rollup <parent>` and show the matrix.
5. `python3 BP check <hub>/<project>/SESSION_BRIEFING.md` — fix anything it flags.
6. If they opted in, register the Stop-hook.

Then help them fill the v1.0 briefing with real content (§1 context, §2 status, decisions already
locked) — several sections will be thin at v1.0, which is fine.

## 4. Done

Tell them what now exists and the ongoing loop:

- The briefing lives at `<hub>/<project>/SESSION_BRIEFING.md`; the pointer is in their context file.
- Going forward they use the **`agent-session-briefing`** skill (not this one): after a work
  session, `bump` → replace §3 → update §2/§4/§5/§6 → `pointer` → `rollup` (if a parent) → `check`.
- Re-run this setup only to onboard another project into the constellation.
