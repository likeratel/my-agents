#!/usr/bin/env python3
"""Install owned links and Codex role files while preserving user changes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def owned(path):
    if not path.is_symlink():
        return False
    # Inspect the immediate target as well: legacy paths may be dangling.
    target = Path(os.path.abspath(path.parent / os.readlink(path)))
    return target == ROOT or ROOT in target.parents


def atomic_write(path, content):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.flush()
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def install_codex_roles(directory, conflicts, counts):
    """Codex opens role files with O_NOFOLLOW; symlinks cannot be executed."""
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / '.my-agents-installed.json'
    if manifest.is_symlink() or (manifest.exists() and not manifest.is_file()):
        conflicts.append(str(manifest))
        return
    try:
        previous = json.loads(manifest.read_text()) if manifest.exists() else {}
        if not isinstance(previous, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in previous.items()
        ):
            raise ValueError('잘못된 설치 기록')
    except (ValueError, OSError):
        conflicts.append(str(manifest) + ' (설치 기록을 읽을 수 없음)')
        return
    installed = dict(previous)
    for source in sorted((ROOT / 'generated/codex/agents').glob('*.toml')):
        dest = directory / source.name
        content = source.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if dest.is_symlink():
            if not owned(dest):
                conflicts.append(str(dest))
                continue
        elif dest.exists():
            if not dest.is_file():
                conflicts.append(str(dest))
                continue
            current = hashlib.sha256(dest.read_bytes()).hexdigest()
            if current == digest:
                installed[source.name] = digest
                counts['already'] += 1
                continue
            if previous.get(source.name) != current:
                conflicts.append(str(dest) + ' (사용자 파일 또는 설치 후 수정됨)')
                continue
        atomic_write(dest, content)
        installed[source.name] = digest
        counts['copied'] += 1
        print('파일 설치:', dest)
    atomic_write(manifest, (json.dumps(installed, indent=2) + '\n').encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true')
    group.add_argument('--claude', action='store_true')
    group.add_argument('--codex', action='store_true')
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / 'scripts/generate.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/generate.py'), '--check'], check=True)
    home = Path(os.environ.get('MY_AGENTS_HOME') or Path.home()).expanduser().absolute()
    shared = home / '.agents/my-agents'
    conflicts = []
    counts = {'linked': 0, 'copied': 0, 'already': 0}

    def safe_parents(path, boundary):
        for parent in path.parents:
            if parent == boundary:
                break
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                conflicts.append(str(path) + ' (상위 경로가 링크 또는 일반 파일)')
                return False
        return True

    def link(source, dest, boundary=home):
        if not safe_parents(dest, boundary):
            return False
        if dest.is_symlink() and dest.resolve() == source.resolve():
            counts['already'] += 1
            return True
        if dest.is_symlink() and owned(dest):
            dest.unlink()
        elif dest.exists() or dest.is_symlink():
            conflicts.append(str(dest))
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(source)
        counts['linked'] += 1
        print('연결:', dest)
        return True

    for name in ('rules', 'templates'):
        link(ROOT / 'shared' / name, shared / name)
    if not args.codex:
        # Old Claude automatic rules would duplicate the generated common rules.
        global_installed = link(ROOT / 'generated/claude/CLAUDE.md', home / '.claude/CLAUDE.md')
        old_rules = home / '.claude/rules'
        if global_installed and safe_parents(old_rules, home) and owned(old_rules):
            old_rules.unlink()
            print('이전 자동 규칙 링크 해제:', old_rules)
        elif old_rules.exists() or old_rules.is_symlink():
            print('유지: 사용자 Claude rules (추가 규칙이 함께 적용될 수 있음)')
        for source in sorted((ROOT / 'generated/claude/agents').glob('*.md')):
            link(source, home / '.claude/agents' / source.name)
        for source in sorted((ROOT / 'shared/skills').iterdir()):
            if source.is_dir():
                link(source, home / '.claude/skills' / source.name)
        # Keep old template references usable.
        link(ROOT / 'shared/templates', home / '.claude/templates')
        link(ROOT / 'shared/templates/PROJECT_TEMPLATE.md', home / '.claude/PROJECT_TEMPLATE.md')
    if not args.claude:
        codex_homes = [home / '.codex']
        custom = os.environ.get('CODEX_HOME')
        if not os.environ.get('MY_AGENTS_HOME') and custom:
            custom_path = Path(custom).expanduser().absolute()
            if custom_path not in codex_homes:
                codex_homes.append(custom_path)
        for codex_home in codex_homes:
            boundary = Path(os.path.commonpath([home, codex_home]))
            link(ROOT / 'generated/codex/AGENTS.md', codex_home / 'AGENTS.md', boundary)
            if safe_parents(codex_home / 'agents' / 'role.toml', boundary):
                install_codex_roles(codex_home / 'agents', conflicts, counts)
        for source in sorted((ROOT / 'shared/skills').iterdir()):
            if source.is_dir():
                link(source, home / '.agents/skills' / source.name)
    print('완료: 연결 {linked}, 파일 설치 {copied}, 기존 설치 {already}, 충돌 {n}'.format(**counts, n=len(conflicts)))
    for conflict in conflicts:
        print('건너뜀 (사용자 설정 보존):', conflict, file=sys.stderr)
    return 1 if conflicts else 0


if __name__ == '__main__':
    sys.exit(main())
