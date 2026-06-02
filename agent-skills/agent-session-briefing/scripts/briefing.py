#!/usr/bin/env python3
"""agent-session-briefing — deterministic helpers for session briefings.

The skill (SKILL.md) does the judgment — assessing status, capturing decisions,
prioritising next steps. This script does the clerical, drift-prone mechanics so they
execute identically regardless of which model or harness is driving:

    new      scaffold a hub dir + v1.0 skeleton briefing, wire the context-file pointer
    bump     increment the version and stamp the real date (header + version-history row)
    pointer  idempotently insert/update the context-file pointer block
    rollup   regenerate a parent briefing's constellation block from its children
             (component matrix + layer + surfaced blockers/decisions)
    check    validate a briefing's structure (the iron rule, version/date, status vocab)
    doctor   scan the hub; re-verify/repair pointers + project dirs, flag stale/missing/dupes

stdlib only — no third-party deps, so the anchor itself can't drift.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

# The hub holds one briefing per project. Default to a neutral, harness-agnostic
# location; override with $SESSION_BRIEFING_HUB or --hub.
HUB_DEFAULT = os.environ.get(
    "SESSION_BRIEFING_HUB",
    str(Path.home() / ".session-briefings"),
)

# Agent context file — the timeless operational-reference doc the briefing pairs with.
# AGENTS.md is the cross-tool open standard (stewarded by the Linux Foundation; used by
# Codex, OpenCode, Aider, RooCode, OpenClaw, …). CLAUDE.md (Claude Code) and GEMINI.md
# (Gemini CLI) are recognized when already present. Auto-detect an existing one; create
# AGENTS.md when none exists. Override with --context-file or $SESSION_BRIEFING_CONTEXT_FILE.
CONTEXT_FILE_DEFAULT = "AGENTS.md"
CONTEXT_FILE_CANDIDATES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]
CONTEXT_FILE_ENV = os.environ.get("SESSION_BRIEFING_CONTEXT_FILE")

# Canonical section set. `check` enforces presence; the iron rule additionally forbids
# dropping any section that existed in the prior committed version.
SECTIONS = [
    (1, "Project Context"),
    (2, "Current Status"),
    (3, "This Session — What Was Done"),
    (4, "Next Steps / Priorities"),
    (5, "Design Decisions Log"),
    (6, "Open Questions"),
    (7, "Discrepancies (spec vs code)"),
    (8, "Session Opening Prompt"),
    (9, "Version History"),
]
CANONICAL = {n for n, _ in SECTIONS}

STATUS_TOKENS = {
    "COMPLETE", "IN PROGRESS", "NOT STARTED", "PENDING",
    "BLOCKED", "DEFERRED", "IN REVIEW",
}

POINTER_OPEN = "<!-- agent-session-briefing -->"
POINTER_CLOSE = "<!-- /agent-session-briefing -->"
POINTER_BLOCK = """{open}
## Session continuity
Live state, decisions, next steps, and open questions live in the session briefing, **not here**:
`{briefing}`
Read it when resuming. This file is operational reference only.
{close}"""

# Constellation block (parent rollup) — script-managed region, idempotent via markers.
CONSTELLATION_START = "<!-- constellation:start (managed by agent-session-briefing rollup — do not hand-edit) -->"
CONSTELLATION_END = "<!-- constellation:end -->"

SECTION_RE = re.compile(r"^##\s+§(\d+)\b")
VERSION_RE = re.compile(r"\bv(\d+)\.(\d+)\b")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
STATUS_TAG_RE = re.compile(r"\s+(?:UPDATED|NEW|RESOLVED)\s+v\d+\.\d+$", re.I)
META_RE = re.compile(r"<!--\s*meta:\s*(.*?)\s*-->")
SURFACE_RE = re.compile(r"\[surface\]\s*(.+)", re.I)

SKELETON_TEMPLATE = """# {{PROJECT}} — Session Briefing

**{{VERSION}} — {{DATE}}** · _agent-session-briefing_
<!-- meta: parent={{PARENT}} | layer={{LAYER}} | projectdir={{PROJECTDIR}} | status={{STATUS}} -->
Operational reference lives in the project's agent context file (AGENTS.md / CLAUDE.md); this briefing holds state, decisions, and trajectory.

---

## §1 — Project Context
<!-- 1-2 lines + current phase. The "what/how" lives in the agent context file; don't duplicate it here. -->
_Phase:_

## §2 — Current Status
| Area | Status | Notes |
|------|--------|-------|
|  | NOT STARTED |  |
<!-- Status: COMPLETE / IN PROGRESS / NOT STARTED / PENDING / BLOCKED / DEFERRED / IN REVIEW. No vague phrasing. -->
<!-- Umbrella/parent briefings: `rollup` injects a component matrix here automatically. -->

## §3 — This Session — What Was Done
<!-- Replaced in full each update. Reference commit SHAs; capture the why/decisions/ripples. -->
- (initial briefing)

## §4 — Next Steps / Priorities
<!-- Dependency-ordered. Note blockers. Tag an item [surface] to bubble it to the parent. -->
1.

## §5 — Design Decisions Log
<!-- Append-only. The rationale behind locked choices. Tag [surface] to bubble a decision up. -->
| # | Decision | Rationale | Since |
|---|----------|-----------|-------|
| 1 |  |  | {{VERSION}} |

## §6 — Open Questions
<!-- Tag a question [surface] to bubble it into the parent's constellation block. -->
| # | Question | Blocks / deadline | Context |
|---|----------|-------------------|---------|
|  |  |  |  |

## §7 — Discrepancies (spec vs code)
<!-- Where docs/specs diverge from code. Code is authoritative unless stated; verify against source. -->
None identified.

## §8 — Session Opening Prompt
<!-- Short paste-to-resume payload. The agent context file auto-loads the operational context. -->
```
Resuming {{PROJECT}}. Read the agent context file (auto-loaded) and this briefing's §2-§4.
Last session: <one line>. Next: <ordered priorities>.
```

## §9 — Version History
| Version | Date | Summary |
|---------|------|---------|
| {{VERSION}} | {{DATE}} | Initial briefing. |
"""


def today() -> str:
    return datetime.date.today().isoformat()


def section_set(text: str) -> set[int]:
    return {int(m.group(1)) for line in text.splitlines()
            for m in [SECTION_RE.match(line)] if m}


def section_body(text: str, n: int) -> str | None:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if m and int(m.group(1)) == n:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if SECTION_RE.match(lines[j]):
            end = j
            break
    return "\n".join(lines[start + 1:end])


def strip_constellation(text: str) -> str:
    """Remove the script-managed constellation block so linters don't scan its rows."""
    if CONSTELLATION_START in text and CONSTELLATION_END in text:
        return (text[:text.index(CONSTELLATION_START)]
                + text[text.index(CONSTELLATION_END) + len(CONSTELLATION_END):])
    return text


def strip_html_comments(text: str) -> str:
    """Drop HTML comments so the surface scan ignores instructional + meta comments."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def parse_meta(text: str) -> dict[str, str]:
    m = META_RE.search(text)
    out: dict[str, str] = {}
    if m:
        for pair in m.group(1).split("|"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def header_version(text: str) -> str:
    m = VERSION_RE.search(text)
    return f"v{m.group(1)}.{m.group(2)}" if m else "?"


def header_date(text: str) -> str:
    m = DATE_RE.search(text)
    return m.group(0) if m else "?"


def bad_status_tokens(text: str) -> list[str]:
    body = section_body(strip_constellation(text), 2)
    if not body:
        return []
    bad = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        status = cells[1]
        if not status or set(status) <= set("-:") or status.lower() == "status":
            continue  # empty / separator / header row
        norm = STATUS_TAG_RE.sub("", status).strip().upper()
        if norm and norm not in STATUS_TOKENS:
            bad.append(status)
    return bad


def prior_section_set(path: Path) -> set[int] | None:
    """Section set of the prior committed version (HEAD), or None if untracked/new."""
    try:
        top = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if top.returncode != 0:
            return None
        root = Path(top.stdout.strip())
        rel = path.resolve().relative_to(root.resolve())
        show = subprocess.run(
            ["git", "-C", str(root), "show", f"HEAD:{rel.as_posix()}"],
            capture_output=True, text=True,
        )
        if show.returncode != 0:
            return None
        return section_set(show.stdout)
    except Exception:
        return None


def _append_table_row(text: str, row: str) -> str:
    lines = text.splitlines()
    last = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("|"):
            last = i
    if last is None:
        lines.append(row)
    else:
        lines.insert(last + 1, row)
    out = "\n".join(lines)
    return out + "\n" if text.endswith("\n") else out


def briefing_path(hub: str, project: str) -> Path:
    return Path(hub) / project / "SESSION_BRIEFING.md"


def store_dir(p: Path) -> str:
    """Serialise a project dir for the briefing meta — relative to $HOME (`~/…`) when
    possible so the hub stays portable across machines and leaks no absolute home path."""
    p = p.resolve()
    try:
        return "~/" + p.relative_to(Path.home().resolve()).as_posix()
    except ValueError:
        return str(p)


def detect_context_file(base: Path, context_file: str | None) -> Path:
    """Pick the agent context file in `base`. Explicit name (flag/env) wins; else the
    first existing candidate; else the AGENTS.md default (created on write)."""
    name = context_file or CONTEXT_FILE_ENV
    if name:
        return base / name
    for cand in CONTEXT_FILE_CANDIDATES:
        if (base / cand).exists():
            return base / cand
    return base / CONTEXT_FILE_DEFAULT


def resolve_project_dir(hub: str, project: str, project_dir: str | None) -> Path:
    """Where the project's context file lives. Explicit --project-dir wins; else the
    `projectdir` recorded in the briefing meta; else the current working directory."""
    if project_dir:
        return Path(project_dir)
    br = briefing_path(hub, project)
    if br.exists():
        pd = parse_meta(br.read_text()).get("projectdir")
        if pd and pd not in ("", "none"):
            return Path(pd).expanduser()
    return Path.cwd()


def skeleton(project: str, version: str, date: str,
             parent: str, layer: str, status: str, projectdir: str) -> str:
    return (SKELETON_TEMPLATE
            .replace("{{PROJECT}}", project)
            .replace("{{VERSION}}", version)
            .replace("{{DATE}}", date)
            .replace("{{PARENT}}", parent)
            .replace("{{LAYER}}", layer)
            .replace("{{PROJECTDIR}}", projectdir)
            .replace("{{STATUS}}", status))


# --- rollup core ------------------------------------------------------------

def do_rollup(hub: Path, parent: str) -> tuple[int, int]:
    parent_br = hub / parent / "SESSION_BRIEFING.md"
    if not parent_br.exists():
        raise SystemExit(f"rollup: parent briefing not found: {parent_br}")
    rows = []
    surfaced = []
    for child_dir in sorted(p for p in hub.iterdir() if p.is_dir() and p.name != parent):
        cb = child_dir / "SESSION_BRIEFING.md"
        if not cb.exists():
            continue
        t = cb.read_text()
        meta = parse_meta(t)
        if meta.get("parent") != parent:
            continue
        rows.append((child_dir.name, header_version(t), meta.get("layer", "—"),
                     meta.get("status", "—"), header_date(t)))
        for line in strip_html_comments(strip_constellation(t)).splitlines():
            if line.lstrip().startswith("|"):
                continue  # surfacing uses clean prefix lines, never table cells
            sm = SURFACE_RE.search(line)
            if sm:
                text = sm.group(1).strip().strip("*").strip(" :—-").strip()
                if text:
                    surfaced.append((child_dir.name, text))

    block = [CONSTELLATION_START, "**Components**", "",
             "| Component | Version | Layer | Status | Updated | Briefing |",
             "|---|---|---|---|---|---|"]
    for name, ver, layer, status, date in rows:
        block.append(f"| {name} | {ver} | {layer} | {status} | {date} | "
                     f"[↗](../{name}/SESSION_BRIEFING.md) |")
    block += ["", "**Surfaced from components** — blockers / decisions needing attention here"]
    if surfaced:
        block += [f"- **{name}:** {text}" for name, text in surfaced]
    else:
        block.append("- none")
    block.append(CONSTELLATION_END)
    block_text = "\n".join(block)

    pt = parent_br.read_text()
    had_nl = pt.endswith("\n")
    if CONSTELLATION_START in pt and CONSTELLATION_END in pt:
        pre = pt[:pt.index(CONSTELLATION_START)]
        post = pt[pt.index(CONSTELLATION_END) + len(CONSTELLATION_END):]
        pt = pre + block_text + post
    else:
        out, inserted = [], False
        for line in pt.splitlines():
            out.append(line)
            if not inserted and re.match(r"^##\s+§2\b", line):
                out += ["", block_text]
                inserted = True
        if not inserted:
            out += ["", block_text]
        pt = "\n".join(out) + ("\n" if had_nl else "")
    parent_br.write_text(pt)
    return len(rows), len(surfaced)


# --- commands ---------------------------------------------------------------

def cmd_new(args) -> None:
    pdir = Path(args.hub) / args.project
    (pdir / "refs").mkdir(parents=True, exist_ok=True)
    path = briefing_path(args.hub, args.project)
    if path.exists():
        sys.exit(f"new: {path} already exists — refusing to overwrite")
    proj_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    path.write_text(skeleton(args.project, "v1.0", today(),
                             args.parent, args.layer, "new — scaffolded",
                             store_dir(proj_dir)))
    print(f"created {path}")
    if not (Path(args.hub) / ".git").exists():
        print(f"note: {args.hub} is not a git repo yet — run `git init` there (and add a "
              f"remote) for version history + hook validation.", file=sys.stderr)
    _write_pointer(args.project, args.hub, str(proj_dir), args.context_file)
    if args.parent and args.parent != "none":
        if (Path(args.hub) / args.parent / "SESSION_BRIEFING.md").exists():
            n, s = do_rollup(Path(args.hub), args.parent)
            print(f"rollup: refreshed {args.parent} ({n} component(s), {s} surfaced)")
        else:
            print(f"note: parent '{args.parent}' has no briefing yet — run "
                  f"`briefing.py rollup {args.parent}` after creating it.", file=sys.stderr)


def cmd_bump(args) -> None:
    path = Path(args.path)
    text = path.read_text()
    m = VERSION_RE.search(text)
    if not m:
        sys.exit("bump: no vX.Y version found in the briefing")
    major, minor = int(m.group(1)), int(m.group(2))
    if args.major:
        major, minor = major + 1, 0
    else:
        minor += 1
    nv, d = f"v{major}.{minor}", today()
    text = VERSION_RE.sub(nv, text, count=1)   # header version
    text = DATE_RE.sub(d, text, count=1)       # header date
    text = _append_table_row(text, f"| {nv} | {d} | <!-- fill: what changed this session --> |")
    path.write_text(text)
    print(nv)
    meta = parse_meta(text)
    parent = meta.get("parent")
    if parent and parent != "none":
        print(f"reminder: run `briefing.py rollup {parent}` to refresh the parent matrix.",
              file=sys.stderr)


def _write_pointer(project: str, hub: str, project_dir: str | None,
                   context_file: str | None) -> None:
    base = resolve_project_dir(hub, project, project_dir)
    ctx = detect_context_file(base, context_file)
    briefing = briefing_path(hub, project)
    block = POINTER_BLOCK.format(open=POINTER_OPEN, close=POINTER_CLOSE, briefing=briefing)
    if not base.exists():
        print(f"pointer: project dir {base} does not exist — skipped "
              f"(pass --project-dir)", file=sys.stderr)
        return
    if not ctx.exists():
        ctx.write_text(f"# {project}\n\n{block}\n")
        print(f"pointer: created {ctx} with continuity pointer → {briefing}")
        return
    text = ctx.read_text()
    if POINTER_OPEN in text and POINTER_CLOSE in text:
        pre = text[:text.index(POINTER_OPEN)]
        post = text[text.index(POINTER_CLOSE) + len(POINTER_CLOSE):]
        text = pre + block + post
    else:
        sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
        text = text + sep + block + "\n"
    ctx.write_text(text)
    print(f"pointer: wired {ctx} → {briefing}")


def cmd_pointer(args) -> None:
    _write_pointer(args.project, args.hub, args.project_dir, args.context_file)


def cmd_rollup(args) -> None:
    n, s = do_rollup(Path(args.hub), args.parent)
    print(f"rollup: {n} component(s), {s} surfaced → {args.parent}/SESSION_BRIEFING.md")


def cmd_check(args) -> None:
    path = Path(args.path)
    if not path.exists():
        sys.exit(f"check: {path} not found")
    text = path.read_text()
    errors: list[str] = []
    warnings: list[str] = []

    present = section_set(text)
    missing = sorted(CANONICAL - present)
    if missing:
        errors.append("missing canonical sections: "
                      + ", ".join(f"§{n}" for n in missing))

    prior = prior_section_set(path)
    if prior:
        dropped = sorted(prior - present)
        if dropped:
            errors.append("sections dropped vs prior committed version: "
                          + ", ".join(f"§{n}" for n in dropped))

    if not VERSION_RE.search(text):
        errors.append("header missing a vX.Y version")
    if not DATE_RE.search(text):
        errors.append("header missing a YYYY-MM-DD date")

    op = section_body(text, 8)
    if op is not None and not op.strip(" \n#`<>-"):
        warnings.append("§8 Session Opening Prompt looks empty")

    for bad in bad_status_tokens(text):
        warnings.append(f"§2 non-standard status token: {bad!r}")

    for w in warnings:
        print(f"warn: {w}", file=sys.stderr)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if errors:
        sys.exit(1)
    print("ok" + (f" ({len(warnings)} warning(s))" if warnings else ""))


def cmd_doctor(args) -> None:
    hub = Path(args.hub)
    if not hub.exists():
        sys.exit(f"doctor: hub not found: {hub}")
    if not (hub / ".git").exists():
        print(f"warn: hub {hub} is not a git repo — `check` can only verify section presence, "
              f"not catch dropped sections (the iron rule needs git history).", file=sys.stderr)
    projects = sorted(p for p in hub.iterdir()
                      if p.is_dir() and (p / "SESSION_BRIEFING.md").exists())
    ok = issues = fixed = 0
    seen: dict[str, str] = {}
    for pdir in projects:
        proj = pdir.name
        meta = parse_meta((pdir / "SESSION_BRIEFING.md").read_text())
        recorded = meta.get("projectdir", "")
        if not recorded or recorded == "none":
            print(f"  {proj}: no projectdir recorded — run "
                  f"`briefing.py pointer {proj} --project-dir <repo>` to set it", file=sys.stderr)
            issues += 1
            continue
        base = Path(recorded).expanduser()
        key = str(base.resolve()) if base.exists() else str(base)
        if key in seen:
            print(f"  {proj}: project dir {recorded} also used by '{seen[key]}' (duplicate)",
                  file=sys.stderr)
            issues += 1
        else:
            seen[key] = proj
        if not base.exists():
            print(f"  {proj}: project dir missing: {recorded} (moved/renamed?) — run "
                  f"`briefing.py pointer {proj} --project-dir <new path>`", file=sys.stderr)
            issues += 1
            continue
        briefing = str(briefing_path(args.hub, proj))
        holder = None
        for cf in (base / c for c in CONTEXT_FILE_CANDIDATES):
            if cf.exists() and POINTER_OPEN in cf.read_text():
                holder = cf
                break
        correct = holder is not None and briefing in holder.read_text()
        if correct:
            ok += 1
        elif args.fix:
            _write_pointer(proj, args.hub, str(base), None)
            fixed += 1
        else:
            where = holder.name if holder else "the context file"
            state = "stale" if holder else "missing"
            print(f"  {proj}: pointer {state} in {where} — run `briefing.py doctor --fix`",
                  file=sys.stderr)
            issues += 1
    print(f"doctor: {len(projects)} project(s) — {ok} ok, {issues} issue(s), {fixed} fixed")
    if issues:
        sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser(prog="briefing.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pn = sub.add_parser("new", help="scaffold hub dir + v1.0 skeleton + wire pointer")
    pn.add_argument("project")
    pn.add_argument("--hub", default=HUB_DEFAULT)
    pn.add_argument("--project-dir", default=None,
                    help="project repo dir whose context file gets the pointer "
                         "(default: current directory)")
    pn.add_argument("--context-file", default=None,
                    help="context-file name to wire (default: auto-detect "
                         "AGENTS.md/CLAUDE.md/GEMINI.md, else create AGENTS.md)")
    pn.add_argument("--parent", default="none", help="parent project for rollup (e.g. acme-platform)")
    pn.add_argument("--layer", default="unset",
                    help="optional IP/visibility layer for the constellation matrix "
                         "(e.g. OPEN-MIT, COMMERCIAL, CLOSED — or your own)")
    pn.set_defaults(func=cmd_new)

    pb = sub.add_parser("bump", help="increment version + stamp date")
    pb.add_argument("path")
    pb.add_argument("--major", action="store_true", help="bump major (vX.0) instead of minor")
    pb.set_defaults(func=cmd_bump)

    pp = sub.add_parser("pointer", help="idempotently wire the context-file pointer")
    pp.add_argument("project")
    pp.add_argument("--hub", default=HUB_DEFAULT)
    pp.add_argument("--project-dir", default=None,
                    help="project repo dir (default: the briefing's recorded projectdir, "
                         "else current directory)")
    pp.add_argument("--context-file", default=None,
                    help="context-file name to wire (default: auto-detect, else AGENTS.md)")
    pp.set_defaults(func=cmd_pointer)

    pr = sub.add_parser("rollup", help="regenerate a parent's constellation block from its children")
    pr.add_argument("parent")
    pr.add_argument("--hub", default=HUB_DEFAULT)
    pr.set_defaults(func=cmd_rollup)

    pc = sub.add_parser("check", help="validate a briefing's structure")
    pc.add_argument("path")
    pc.set_defaults(func=cmd_check)

    pdoc = sub.add_parser("doctor", help="scan the hub; re-verify/repair pointers + project dirs")
    pdoc.add_argument("--hub", default=HUB_DEFAULT)
    pdoc.add_argument("--fix", action="store_true", help="repair stale/missing pointers in place")
    pdoc.set_defaults(func=cmd_doctor)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
