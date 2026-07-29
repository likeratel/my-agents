#!/usr/bin/env bash
# my-agents 설치 — 에이전트 설정을 각 에이전트가 읽는 위치로 심볼릭 링크한다.
# 저장소 안의 폴더명은 대상 위치와 같다 (.claude/ → ~/.claude/).
# 여러 번 실행해도 안전하다. 기존의 "실제 파일·폴더"는 절대 건드리지 않는다.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_CLAUDE="${HOME}/.claude"

linked=0 already=0 skipped=0

# 항목 하나를 링크한다. 이미 우리 링크면 그대로 두고, 실제 파일·폴더면 건너뛴다.
link_one() {
  local src="$1" target="$2" label="$3"

  if [ -L "$target" ]; then
    if [ "$(readlink "$target")" = "$src" ]; then
      already=$((already + 1))
      return
    fi
    echo "  교체: $label (다른 곳을 가리키고 있었음)"
    rm "$target"
  elif [ -e "$target" ]; then
    # 실제 파일·폴더가 있으면 남의 것일 수 있으므로 건드리지 않는다
    echo "  건너뜀: $label — 실제 파일·폴더가 이미 있음 ($target)"
    skipped=$((skipped + 1))
    return
  fi

  mkdir -p "$(dirname "$target")"
  ln -s "$src" "$target"
  echo "  연결: $label"
  linked=$((linked + 1))
}

# 디렉토리 안의 항목들을 대상 디렉토리에 하나씩 링크한다.
# 대상 디렉토리 자체는 링크하지 않으므로 남의 파일과 섞여 있어도 안전하다.
link_children() {
  local src_dir="$1" target_dir="$2" prefix="$3"
  [ -d "$src_dir" ] || return 0

  mkdir -p "$target_dir"
  local src name
  for src in "$src_dir"/*; do
    [ -e "$src" ] || continue
    name="$(basename "$src")"
    link_one "$src" "$target_dir/$name" "$prefix/$name"
  done
}

# 스킬·에이전트는 남의 것과 한 디렉토리를 공유하므로 항목별로 링크한다
link_children "$ROOT/.claude/skills" "$HOME_CLAUDE/skills" "skills"
link_children "$ROOT/.claude/agents" "$HOME_CLAUDE/agents" "agents"

# 규칙 트리는 통째로 우리 것이므로 디렉토리 하나로 링크한다
link_one "$ROOT/.claude/rules" "$HOME_CLAUDE/rules" "rules/"

# 최상위 문서
link_one "$ROOT/.claude/CLAUDE.md" "$HOME_CLAUDE/CLAUDE.md" "CLAUDE.md"
link_one "$ROOT/.claude/PROJECT_TEMPLATE.md" "$HOME_CLAUDE/PROJECT_TEMPLATE.md" "PROJECT_TEMPLATE.md"

echo
echo "완료 — 연결 $linked · 이미 연결됨 $already · 건너뜀 $skipped"
if [ "$skipped" -gt 0 ]; then
  echo "건너뛴 항목은 직접 확인 후 옮기거나 지우세요."
fi
exit 0
