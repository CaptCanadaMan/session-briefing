# Session Briefing

**Cross-session project continuity for AI coding agents and chat assistants — with a cross-project _constellation_ rollup.**

AI sessions start cold. Between them, context evaporates: what's done, what was decided and _why_, what's next, what your last change quietly touched. So you re-explain, the assistant re-litigates settled decisions, and downstream effects slip through. Session Briefing fixes that with one disciplined habit:

> A **timestamped briefing** that pairs with your project's **timeless context file**, so any fresh session resumes in seconds — and a **constellation** layer that rolls many project briefings up into one parent view.

It's not a heavyweight tool. It's a markdown document, a ~500-line stdlib Python helper, and a method — that scales from a single repo to a whole portfolio of related projects.

---

## The one boundary that makes it work

Every fact about a project is either **timeless** or **timestamped**. Put each where it belongs and both documents stay lean:

| | Lives in… | Holds | Lifecycle |
|---|---|---|---|
| **Timeless** | your **agent context file** (`AGENTS.md` / `CLAUDE.md` / `GEMINI.md`) | what the project is, repo layout, how to build/run/test, conventions, gotchas | overwritten in place; auto-loaded every session |
| **Timestamped** | the **session briefing** | current status, what changed, decisions + rationale, next steps, open questions, spec-vs-code drift | versioned; the briefing _is_ the project's memory |

If "how to run the tests" creeps into the briefing, it belongs in the context file. If a "current status / do not relitigate" block bloats the context file, it belongs in the briefing. Keep the seam clean and neither balloons.

(Personal working style is _neither_ — that lives in your assistant's memory, written once, not re-narrated per project.)

## The headline: the constellation

A single briefing is useful. The payoff is **cross-project awareness**.

When you run several related projects (a platform and its services, a monorepo of packages, a product and its app), each gets its own briefing and declares a **parent**. Then:

- **`rollup`** scans every child and regenerates a **component matrix** in the parent — _component · version · layer · status · updated · link_ — derived, never hand-maintained. The parent is correct by construction.
- **`[surface]`** tags bubble a child's blocker or decision up into the parent's "Surfaced from components" list, so working deep inside one service keeps the whole portfolio's view current.

```
parent (umbrella briefing)
├── component-a   v1.2  ·  status  ·  [↗ briefing]
├── component-b   v0.9  ·  status  ·  [↗ briefing]   ← [surface] "blocked on shared auth"  ──┐
└── component-c   v2.0  ·  status  ·  [↗ briefing]                                            │
        the parent's "Surfaced from components" list shows that blocker ───────────────────────┘
```

## The on-ramp: start small, grow into it

You don't adopt the whole thing on day one. The model is a gentle gradient:

1. **One repo.** `briefing.py new myproject` → a v1.0 briefing + a pointer wired into your context file. Keep it updated as you work. That alone kills cold starts.
2. **Add a parent.** When a second related project appears, give them a shared parent (`--parent`) and run `rollup`. Now you have a two-node constellation.
3. **Full constellation.** Add briefings as projects appear; `[surface]` the things that need portfolio attention. The parent view stays current on its own.

Stop at any rung. The value is real at rung 1; the leverage compounds upward.

## Two variants — pick by where you work

The method is one idea; it ships as two skills because the runtimes differ:

| | [`agent-session-briefing`](agent-skills/agent-session-briefing/) | [`chat-session-briefing`](chat-skills/chat-session-briefing/) |
|---|---|---|
| **For** | coding agents in a repo (Claude Code & any `AGENTS.md`-style harness) | chat assistants (claude.ai web / desktop) |
| **Output** | markdown briefings in a git-backed **hub** | one self-contained markdown document |
| **Pairs with** | your context file + git (offloads timeless reference there) | nothing — the briefing holds everything (13 sections) |
| **Mechanics** | `briefing.py` CLI + the **constellation** rollup | prompt-driven, drop-in |
| **Setup** | guided ([`setup-session-briefing`](agent-skills/setup-session-briefing/)) | none — just add the skill |

The chat variant is the original; the agent variant evolved from it once a repo gave us a context file and git to lean on. See [`docs/methodology.md`](docs/methodology.md) for that story.

## Install

**Agent harnesses (e.g. Claude Code):** copy the skill into your skills directory.

```sh
# Claude Code
cp -r agent-skills/agent-session-briefing ~/.claude/skills/
cp -r agent-skills/setup-session-briefing ~/.claude/skills/   # optional guided onboarding
```

Other harnesses read a context file too (`AGENTS.md`, etc.) — `briefing.py` is plain `python3` and works anywhere; wire it into your harness however it invokes tools. The pointer auto-detects `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` (or creates `AGENTS.md`), or force one with `--context-file`.

**Chat (claude.ai):** add [`chat-skills/chat-session-briefing/`](chat-skills/chat-session-briefing/) as a skill, or attach its `SKILL.md` + `references/` to your Project. No local setup.

## Quickstart (agent)

```sh
# from inside your project repo:
python3 ~/.claude/skills/agent-session-briefing/scripts/briefing.py new myproject
#   → creates ~/.session-briefings/myproject/SESSION_BRIEFING.md
#   → wires a continuity pointer into your context file (creates AGENTS.md if none)

# ...do a session of work, then:
python3 .../briefing.py bump  ~/.session-briefings/myproject/SESSION_BRIEFING.md
# fill in §3 (this session) + update §2/§4/§5/§6, then:
python3 .../briefing.py check ~/.session-briefings/myproject/SESSION_BRIEFING.md
```

Or just run the **`setup-session-briefing`** skill, which walks you through hub location, single-vs-constellation, and pointer wiring interactively. Full command reference: [`docs/cli.md`](docs/cli.md).

## How it works

- **The hub** — one git repo at `~/.session-briefings/` (override with `$SESSION_BRIEFING_HUB`), one directory per project. Markdown, so diffs stay readable; git holds the version history.
- **`briefing.py`** — stdlib-only, no dependencies, so the deterministic anchor can't drift:

  | command | does |
  |---|---|
  | `new` | scaffold a v1.0 briefing, record the project dir, wire the context-file pointer |
  | `bump` | increment version + stamp today's date |
  | `pointer` | (re)wire the continuity pointer into the context file |
  | `rollup` | regenerate a parent's constellation matrix + surfaced items |
  | `check` | validate structure (all sections present, none dropped, version/date stamped) |

- **You do the judgment** — assessing status, writing the narrative, capturing decisions and rationale. The script only does the clerical, drift-prone parts.

## Works with any `AGENTS.md`-style harness

`AGENTS.md` is the cross-tool open standard for agent instructions (stewarded by the Linux Foundation; used by Codex, OpenCode, Aider, RooCode, OpenClaw, …). Session Briefing is **context-file-agnostic**: it pairs the briefing with whatever your harness auto-loads — `AGENTS.md`, `CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini CLI), or a name you pass with `--context-file`. The method and the CLI are harness-neutral; only the auto-triggering `SKILL.md` packaging assumes a skill-aware harness.

## Repo layout

```
session-briefing/
├── README.md                  ← you are here
├── LICENSE                    ← MIT
├── docs/
│   ├── methodology.md         ← the method + the chat→agent evolution
│   ├── example-constellation.md
│   └── cli.md
├── agent-skills/
│   ├── agent-session-briefing/   ← SKILL.md, scripts/briefing.py, references/, tests/
│   └── setup-session-briefing/   ← guided onboarding
└── chat-skills/
    └── chat-session-briefing/    ← SKILL.md, references/
```

## License

[MIT](LICENSE).
