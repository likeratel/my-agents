#!/usr/bin/env bash
# 공통 원본에서 도구별 설정을 생성하고 개인 설정 경로에 연결한다.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$ROOT/scripts/install.py" "$@"
