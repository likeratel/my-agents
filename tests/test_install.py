import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='my-agents-test-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'home with spaces'
        self.home.mkdir()
        self.custom = Path(self.temp.name) / 'custom'

    def install(self, *args):
        env = dict(os.environ, MY_AGENTS_HOME=str(self.home), CODEX_HOME=str(self.custom))
        return subprocess.run(['bash', str(ROOT / 'install.sh'), *args], env=env,
                              text=True, capture_output=True)

    def test_fresh_repeat_and_shared_skill(self):
        for _ in range(2):
            result = self.install()
            self.assertEqual(result.returncode, 0, result.stderr)
        a = self.home / '.claude/skills/delivery-loop'
        b = self.home / '.agents/skills/delivery-loop'
        self.assertEqual(a.resolve(), b.resolve())
        self.assertTrue((a / 'SKILL.md').is_file())
        self.assertTrue((self.home / '.codex/AGENTS.md').is_file())
        self.assertFalse(self.custom.exists())

    def test_preserve_files_foreign_links_and_broken_links(self):
        directory = self.home / '.claude'
        directory.mkdir()
        global_file = directory / 'CLAUDE.md'
        global_file.write_text('keep me')
        agents = directory / 'agents'
        agents.mkdir()
        foreign = Path(self.temp.name) / 'foreign'
        foreign.write_text('foreign')
        (agents / 'scout.md').symlink_to(foreign)
        (agents / 'auditor.md').symlink_to(foreign.parent / 'missing')
        self.assertEqual(self.install('--claude').returncode, 1)
        self.assertEqual(global_file.read_text(), 'keep me')
        self.assertEqual((agents / 'scout.md').readlink(), foreign)
        self.assertEqual((agents / 'auditor.md').readlink(), foreign.parent / 'missing')

    def test_legacy_migration_and_other_agent_preserved(self):
        directory = self.home / '.claude'
        directory.mkdir()
        (directory / 'CLAUDE.md').symlink_to(ROOT / '.claude/CLAUDE.md')
        (directory / 'rules').symlink_to(ROOT / '.claude/rules')
        agents = directory / 'agents'
        agents.mkdir()
        (agents / 'custom.md').write_text('custom')
        result = self.install('--claude')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((directory / 'rules').is_symlink())
        self.assertEqual((agents / 'custom.md').read_text(), 'custom')
        self.assertFalse((self.home / '.codex').exists())

    def test_codex_only(self):
        self.assertEqual(self.install('--codex').returncode, 0)
        self.assertFalse((self.home / '.claude').exists())

    def test_foreign_parent_link_not_written(self):
        foreign = Path(self.temp.name) / 'foreign_dir'
        foreign.mkdir()
        (self.home / '.claude').symlink_to(foreign)
        self.assertEqual(self.install('--claude').returncode, 1)
        self.assertEqual(list(foreign.iterdir()), [])

    def test_custom_codex_home(self):
        env = dict(os.environ, HOME=str(self.home), CODEX_HOME=str(self.custom))
        env.pop('MY_AGENTS_HOME', None)
        result = subprocess.run(['bash', str(ROOT / 'install.sh'), '--codex'], env=env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.custom / 'AGENTS.md').resolve(),
                         (self.home / '.codex/AGENTS.md').resolve())
        self.assertTrue((self.custom / 'agents/scout.toml').is_file())

    def test_custom_home_ancestor_link_is_preserved(self):
        foreign = Path(self.temp.name) / 'foreign'
        foreign.mkdir()
        alias = self.home / 'alias'
        alias.symlink_to(foreign)
        env = dict(os.environ, HOME=str(self.home), CODEX_HOME=str(alias / 'custom'))
        env.pop('MY_AGENTS_HOME', None)
        result = subprocess.run(['bash', str(ROOT / 'install.sh'), '--codex'], env=env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(list(foreign.iterdir()), [])
        self.assertTrue((self.home / '.codex/AGENTS.md').is_file())

    def test_file_parent_does_not_abort_other_destinations(self):
        (self.home / '.agents').write_text('keep')
        result = self.install()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual((self.home / '.agents').read_text(), 'keep')
        self.assertTrue((self.home / '.claude/CLAUDE.md').is_file())
        self.assertTrue((self.home / '.codex/AGENTS.md').is_file())

    def test_global_conflict_keeps_old_rules(self):
        directory = self.home / '.claude'
        directory.mkdir()
        (directory / 'CLAUDE.md').write_text('custom guidance')
        (directory / 'rules').symlink_to(ROOT / '.claude/rules')
        self.assertEqual(self.install('--claude').returncode, 1)
        self.assertTrue((directory / 'rules').is_symlink())

    def test_stray_generated_role_blocks_installation(self):
        fixture = Path(self.temp.name) / 'repo'
        fixture.mkdir()
        for name in ('scripts', 'shared', 'adapters'):
            shutil.copytree(ROOT / name, fixture / name)
        shutil.copy2(ROOT / 'install.sh', fixture / 'install.sh')
        subprocess.run([sys.executable, str(fixture / 'scripts/generate.py')],
                       check=True, capture_output=True)
        stray = fixture / 'generated/claude/agents/removed-role.md'
        stray.write_text('obsolete role')
        env = dict(os.environ, MY_AGENTS_HOME=str(self.home))
        result = subprocess.run(['bash', str(fixture / 'install.sh')], env=env,
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('UNEXPECTED', result.stderr)
        self.assertEqual(stray.read_text(), 'obsolete role')
        self.assertEqual(list(self.home.iterdir()), [])

    def test_invalid_option_has_no_install_effects(self):
        self.assertNotEqual(self.install('--unknown').returncode, 0)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
