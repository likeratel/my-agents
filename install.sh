#!/usr/bin/env bash
# ai-dotfiles 설치 — 스킬을 에이전트가 읽는 위치로 심볼릭 링크한다.
# 여러 번 실행해도 안전하다. 기존의 "실제 폴더"는 절대 건드리지 않는다.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME}/.claude/skills"

mkdir -p "$DEST"

linked=0 skipped=0 already=0

for src in "$ROOT"/claude/skills/*/; do
  [ -d "$src" ] || continue
  name="$(basename "$src")"
  target="$DEST/$name"

  if [ -L "$target" ]; then
    if [ "$(readlink "$target")" = "${src%/}" ]; then
      already=$((already + 1))
      continue
    fi
    echo "  교체: $name (다른 곳을 가리키고 있었음)"
    rm "$target"
  elif [ -e "$target" ]; then
    # 실제 폴더/파일이 있으면 남의 것일 수 있으므로 건드리지 않는다
    echo "  건너뜀: $name — 실제 폴더가 이미 있음 ($target)"
    skipped=$((skipped + 1))
    continue
  fi

  ln -s "${src%/}" "$target"
  echo "  연결: $name"
  linked=$((linked + 1))
done

echo
echo "완료 — 연결 $linked · 이미 연결됨 $already · 건너뜀 $skipped"
[ "$skipped" -gt 0 ] && echo "건너뛴 항목은 직접 확인 후 옮기거나 지우세요."
exit 0
