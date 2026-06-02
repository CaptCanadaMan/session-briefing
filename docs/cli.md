# `briefing.py` — command reference

The deterministic helper behind `agent-session-briefing`. **Python 3.8+, standard library only** —
no install, no dependencies. The skill does the judgment (status, decisions, narrative); the script
does the clerical, drift-prone mechanics so they run identically under any model or harness.

```
python3 scripts/briefing.py <command> [args]
```

## Defaults & environment

| Thing | Default | Override |
|---|---|---|
| Hub (where briefings live) | `~/.session-briefings` | `$SESSION_BRIEFING_HUB` or `--hub` |
| Project dir (where the pointer goes) | current directory (`new`); the briefing's recorded `projectdir`, else cwd (`pointer`) | `--project-dir` |
| Context file | auto-detect `AGENTS.md` → `CLAUDE.md` → `GEMINI.md`; create `AGENTS.md` if none | `$SESSION_BRIEFING_CONTEXT_FILE` or `--context-file` |

## Commands

### `new <project>`
Scaffold a v1.0 skeleton briefing at `<hub>/<project>/SESSION_BRIEFING.md`, record the project dir
in the briefing meta, and wire the continuity pointer into the project's context file (creating
`AGENTS.md` if none exists). Refuses to overwrite an existing briefing.

```
python3 briefing.py new <project>
    [--hub PATH] [--project-dir DIR] [--context-file NAME]
    [--parent PARENT] [--layer TAG]
```

- `--parent PARENT` — declare an umbrella for constellation rollup (default `none`). If the parent
  briefing exists, its matrix is refreshed immediately.
- `--layer TAG` — optional free-form tag surfaced in the parent matrix (e.g. `OPEN-MIT`,
  `COMMERCIAL`, `CLOSED`, or your own dimension). Default `unset`.

```sh
# from inside your repo:
python3 briefing.py new acme-api --parent acme-platform --layer OPEN-MIT
```

### `bump <path>`
Increment the version and stamp today's date (header + a new Version-History row to fill in).
Minor by default; `--major` bumps `vX.0`.

```
python3 briefing.py bump <path-to-SESSION_BRIEFING.md> [--major]
```

### `pointer <project>`
Idempotently insert or update the `<!-- agent-session-briefing -->` pointer block in the project's
context file. Run it if the briefing moved, the context file was recreated, or the project dir
changed. Auto-detects the context file (or `--context-file`); resolves the project dir from the
briefing's recorded `projectdir` when `--project-dir` is omitted.

```
python3 briefing.py pointer <project> [--hub PATH] [--project-dir DIR] [--context-file NAME]
```

### `rollup <parent>`
Regenerate the parent briefing's constellation block (component matrix + "Surfaced from components")
from every child whose meta declares that parent. The block is fully script-managed — don't
hand-edit between its markers. Run after bumping any child.

```
python3 briefing.py rollup <parent> [--hub PATH]
```

### `check <path>`
Validate a briefing's structure: all canonical sections present, none dropped versus the prior
committed version (requires git in the hub), version + date stamped, opening prompt non-empty,
status tokens in vocabulary.

```
python3 briefing.py check <path-to-SESSION_BRIEFING.md>
```

- **Exit 0** — valid (warnings, e.g. an odd status token, print but don't fail).
- **Exit 1** — a structural error (missing/dropped section, no version/date).
- Without git in the hub, the no-dropped-sections guard degrades to presence-only — `git init` the
  hub for the full iron-rule check.

### `doctor`
Scan the whole hub and report (or repair) wiring problems: pointers that are missing or stale,
project dirs that moved or vanished, duplicate project dirs, and briefings created before path
tracking. Also warns if the hub isn't a git repo.

```
python3 briefing.py doctor [--hub PATH] [--fix]
```

- `--fix` — re-wire missing/stale pointers in place (from each briefing's recorded `projectdir`).
- **Exit 0** — all healthy. **Exit 1** — unresolved issues remain (e.g. a moved dir needs a manual
  `pointer <project> --project-dir <new path>`).

## Typical loops

```sh
# first briefing for a repo (run from the repo):
python3 briefing.py new myproject

# after a working session:
python3 briefing.py bump  ~/.session-briefings/myproject/SESSION_BRIEFING.md
#   ...edit §3 + update §2/§4/§5/§6...
python3 briefing.py pointer myproject          # keep the pointer current
python3 briefing.py rollup  myparent           # if this briefing declares a parent
python3 briefing.py check   ~/.session-briefings/myproject/SESSION_BRIEFING.md

# periodic health check across the whole hub:
python3 briefing.py doctor --fix
```

## Tests

```sh
python3 agent-skills/agent-session-briefing/tests/test_briefing.py
# or:  python3 -m unittest discover -s agent-skills/agent-session-briefing/tests
```
