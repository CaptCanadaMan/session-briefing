#!/usr/bin/env python3
"""Tests for briefing.py — stdlib unittest, no third-party deps.

Run from the skill directory:
    python3 -m unittest discover -s tests
or directly:
    python3 tests/test_briefing.py
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
BP = SCRIPTS / "briefing.py"
sys.path.insert(0, str(SCRIPTS))
import briefing  # noqa: E402


def run(*args, cwd=None):
    return subprocess.run([sys.executable, str(BP), *args],
                          capture_output=True, text=True, cwd=cwd)


class PureFunctions(unittest.TestCase):
    def test_parse_meta_all_fields(self):
        m = briefing.parse_meta(
            "<!-- meta: parent=acme | layer=OPEN-MIT | projectdir=~/x | status=hi there -->")
        self.assertEqual(m["parent"], "acme")
        self.assertEqual(m["layer"], "OPEN-MIT")
        self.assertEqual(m["projectdir"], "~/x")
        self.assertEqual(m["status"], "hi there")

    def test_section_set(self):
        self.assertEqual(briefing.section_set("## §1 — A\nbody\n## §2 — B\n"), {1, 2})

    def test_store_dir_home_relative(self):
        self.assertEqual(briefing.store_dir(Path.home() / "code" / "acme"), "~/code/acme")

    def test_store_dir_absolute_outside_home(self):
        out = briefing.store_dir(Path("/opt/somewhere"))
        self.assertFalse(out.startswith("~"))
        self.assertTrue(out.startswith("/"))

    def test_detect_context_file_default_is_agents(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(briefing.detect_context_file(Path(d), None).name, "AGENTS.md")

    def test_detect_context_file_prefers_existing_claude(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "CLAUDE.md").write_text("ops\n")
            self.assertEqual(briefing.detect_context_file(Path(d), None).name, "CLAUDE.md")

    def test_detect_context_file_explicit_override(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(briefing.detect_context_file(Path(d), "HERMES.md").name, "HERMES.md")


class CliRoundTrip(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.hub = self.base / "hub"
        self.proj = self.base / "proj"
        self.proj.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _briefing(self, name):
        return self.hub / name / "SESSION_BRIEFING.md"

    def test_new_creates_briefing_pointer_and_records_projectdir(self):
        r = run("new", "myproj", "--hub", str(self.hub), "--project-dir", str(self.proj))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self._briefing("myproj").exists())
        agents = self.proj / "AGENTS.md"            # none existed → AGENTS.md created
        self.assertTrue(agents.exists())
        self.assertIn("agent-session-briefing", agents.read_text())
        self.assertIn("projectdir=", self._briefing("myproj").read_text())

    def test_new_defaults_project_dir_to_cwd(self):
        r = run("new", "cwdproj", "--hub", str(self.hub), cwd=str(self.proj))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("agent-session-briefing", (self.proj / "AGENTS.md").read_text())

    def test_detects_existing_claude_md(self):
        (self.proj / "CLAUDE.md").write_text("# ops\n")
        run("new", "myproj", "--hub", str(self.hub), "--project-dir", str(self.proj))
        self.assertIn("agent-session-briefing", (self.proj / "CLAUDE.md").read_text())
        self.assertFalse((self.proj / "AGENTS.md").exists())

    def test_new_refuses_overwrite(self):
        run("new", "myproj", "--hub", str(self.hub), "--project-dir", str(self.proj))
        r = run("new", "myproj", "--hub", str(self.hub), "--project-dir", str(self.proj))
        self.assertNotEqual(r.returncode, 0)

    def test_bump_then_check_ok(self):
        run("new", "myproj", "--hub", str(self.hub), "--project-dir", str(self.proj))
        br = self._briefing("myproj")
        r = run("bump", str(br))
        self.assertEqual(r.stdout.strip(), "v1.1", r.stderr)
        r = run("check", str(br))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_check_fails_on_missing_section(self):
        run("new", "myproj", "--hub", str(self.hub), "--project-dir", str(self.proj))
        br = self._briefing("myproj")
        br.write_text(br.read_text().replace("## §7 — Discrepancies (spec vs code)", "## gone"))
        r = run("check", str(br))
        self.assertEqual(r.returncode, 1)
        self.assertIn("§7", r.stderr)

    def test_rollup_builds_matrix_and_surfaces(self):
        run("new", "parent", "--hub", str(self.hub), "--project-dir", str(self.base / "p"))
        (self.base / "c").mkdir()
        run("new", "child", "--hub", str(self.hub), "--project-dir", str(self.base / "c"),
            "--parent", "parent", "--layer", "OPEN-MIT")
        cbr = self._briefing("child")
        cbr.write_text(cbr.read_text().replace(
            "## §4 — Next Steps / Priorities\n",
            "## §4 — Next Steps / Priorities\n[surface] needs the shared schema\n", 1))
        r = run("rollup", "parent", "--hub", str(self.hub))
        self.assertEqual(r.returncode, 0, r.stderr)
        pt = self._briefing("parent").read_text()
        self.assertIn("| child |", pt)
        self.assertIn("OPEN-MIT", pt)
        self.assertIn("needs the shared schema", pt)

    def test_doctor_healthy_then_break_then_fix(self):
        run("new", "myproj", "--hub", str(self.hub), "--project-dir", str(self.proj))
        self.assertEqual(run("doctor", "--hub", str(self.hub)).returncode, 0)
        agents = self.proj / "AGENTS.md"
        agents.write_text(re.sub(
            r"<!-- agent-session-briefing -->.*?<!-- /agent-session-briefing -->\n?",
            "", agents.read_text(), flags=re.S))
        self.assertEqual(run("doctor", "--hub", str(self.hub)).returncode, 1)
        run("doctor", "--hub", str(self.hub), "--fix")
        self.assertIn("agent-session-briefing", agents.read_text())
        self.assertEqual(run("doctor", "--hub", str(self.hub)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
