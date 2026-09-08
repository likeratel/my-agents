import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate.py"


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="my-agents-generate-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        for name in ("adapters", "shared"):
            shutil.copytree(ROOT / name, self.root / name)

    def generate(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *args],
            text=True,
            capture_output=True,
        )

    def test_generation_is_idempotent(self):
        first = self.generate()
        self.assertEqual(first.returncode, 0, first.stderr)
        outputs = {
            path.relative_to(self.root): path.read_bytes()
            for path in (self.root / "generated").rglob("*")
            if path.is_file()
        }
        second = self.generate()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(
            outputs,
            {
                path.relative_to(self.root): path.read_bytes()
                for path in (self.root / "generated").rglob("*")
                if path.is_file()
            },
        )
        checked = self.generate("--check")
        self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_shared_change_reaches_both_global_outputs(self):
        self.assertEqual(self.generate().returncode, 0)
        marker = "\nShared generator propagation marker.\n"
        instructions = self.root / "shared" / "instructions.md"
        instructions.write_text(instructions.read_text(encoding="utf-8") + marker, encoding="utf-8")
        self.assertEqual(self.generate().returncode, 0)
        self.assertIn(marker.strip(), (self.root / "generated/claude/CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn(marker.strip(), (self.root / "generated/codex/AGENTS.md").read_text(encoding="utf-8"))

    def test_model_preservation_and_toml_parse(self):
        self.assertEqual(self.generate().returncode, 0)
        claude = json.loads((self.root / "adapters/claude.json").read_text(encoding="utf-8"))
        codex = json.loads((self.root / "adapters/codex.json").read_text(encoding="utf-8"))
        for role, config in claude["roles"].items():
            agent = (self.root / "generated/claude/agents" / (role + ".md")).read_text(encoding="utf-8")
            self.assertIn("model: %s" % config["model"], agent)
        try:
            import tomllib
        except ModuleNotFoundError:
            tomllib = None
        if tomllib is not None:
            for role, config in codex["roles"].items():
                data = tomllib.loads(
                    (self.root / "generated/codex/agents" / (role + ".toml")).read_text(encoding="utf-8")
                )
                self.assertEqual(data["model"], config["model"])
                self.assertEqual(data["model_reasoning_effort"], config["model_reasoning_effort"])
                self.assertEqual(data["sandbox_mode"], config["sandbox_mode"])
                self.assertIn("~/.agents/my-agents/rules/common/*.md", data["developer_instructions"])

    def test_claude_description_is_yaml_quoted(self):
        spec = importlib.util.spec_from_file_location("my_agents_generate", SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = module.claude_agent(
            "role",
            {"tools": ["Read"], "model": "sonnet"},
            module.Role("description: with a newline\nand quotes \"here\"", "body"),
            "adapter instructions",
        )
        self.assertIn(
            'description: "description: with a newline\\nand quotes \\"here\\""', output
        )

    def test_check_detects_stale_file_without_rewriting_it(self):
        self.assertEqual(self.generate().returncode, 0)
        target = self.root / "generated/claude/CLAUDE.md"
        target.write_text("stale\n", encoding="utf-8")
        result = self.generate("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("STALE generated/claude/CLAUDE.md", result.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), "stale\n")

    def test_check_detects_unexpected_generated_file_and_dangling_symlink(self):
        self.assertEqual(self.generate().returncode, 0)
        stray = self.root / "generated/claude/agents/unmanaged.md"
        stray.write_text("do not delete me\n", encoding="utf-8")
        dangling = self.root / "generated/claude/agents/dangling.md"
        dangling.symlink_to(self.root / "missing-target.md")
        result = self.generate("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("UNEXPECTED generated/claude/agents/unmanaged.md", result.stderr)
        self.assertIn("UNEXPECTED generated/claude/agents/dangling.md", result.stderr)
        self.assertEqual(stray.read_text(encoding="utf-8"), "do not delete me\n")
        self.assertTrue(dangling.is_symlink())

    def test_rejects_output_symlink_before_any_write(self):
        output = self.root / "generated/claude/agents/implementer.md"
        output.parent.mkdir(parents=True)
        external = Path(self.temp.name) / "external-settings.md"
        external.write_text("protected\n", encoding="utf-8")
        output.symlink_to(external)

        checked = self.generate("--check")
        self.assertEqual(checked.returncode, 2)
        self.assertIn("generated/claude/agents/implementer.md is a symbolic link", checked.stderr)
        self.assertEqual(external.read_text(encoding="utf-8"), "protected\n")

        generated = self.generate()
        self.assertEqual(generated.returncode, 2)
        self.assertEqual(external.read_text(encoding="utf-8"), "protected\n")
        self.assertFalse((self.root / "generated/codex/AGENTS.md").exists())

    def test_rejects_symlinked_generated_parent_before_any_write(self):
        generated = self.root / "generated"
        generated.mkdir()
        external = Path(self.temp.name) / "external-claude"
        external.mkdir()
        (generated / "claude").symlink_to(external, target_is_directory=True)

        result = self.generate()
        self.assertEqual(result.returncode, 2)
        self.assertIn("generated/claude is a symbolic link", result.stderr)
        self.assertFalse((external / "CLAUDE.md").exists())
        self.assertFalse((self.root / "generated/codex/AGENTS.md").exists())

    def test_rejects_symlinked_generated_root_before_any_write(self):
        external = Path(self.temp.name) / "external-generated"
        external.mkdir()
        (self.root / "generated").symlink_to(external, target_is_directory=True)

        result = self.generate()
        self.assertEqual(result.returncode, 2)
        self.assertIn("generated is a symbolic link", result.stderr)
        self.assertFalse((external / "claude/CLAUDE.md").exists())
        self.assertFalse((external / "codex/AGENTS.md").exists())

    def test_rejects_non_directory_output_ancestor_before_any_write(self):
        generated = self.root / "generated"
        generated.mkdir()
        ancestor = generated / "claude"
        ancestor.write_text("protected\n", encoding="utf-8")

        result = self.generate()
        self.assertEqual(result.returncode, 2)
        self.assertIn("generated/claude is an output ancestor but is not a directory", result.stderr)
        self.assertEqual(ancestor.read_text(encoding="utf-8"), "protected\n")
        self.assertFalse((self.root / "generated/codex/AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
