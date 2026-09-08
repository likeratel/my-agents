# my-agents

Claude Code와 Codex의 개인 작업 지침을 한 원본에서 관리합니다.
공통 지침·규칙·스킬·역할은 `shared/`에서 수정하고, 모델과 도구별 차이는 `adapters/`에서 관리합니다.
팀 프로젝트 설정은 이 설치기가 변경하지 않습니다.

## 구조

```text
shared/
  instructions.md          공통 작업 방식
  rules/common/            양쪽 글로벌 지침에 포함하는 공통 규칙
  rules/typescript/        TS·JS 작업 시 읽는 규칙
  skills/delivery-loop/    두 도구가 함께 읽는 스킬
  roles/                   역할별 책임·완료 조건
  templates/               선택적으로 사용하는 문서 템플릿
adapters/
  claude.json              Claude 모델·도구·전용 지침
  codex.json               Codex 모델·추론 강도·권한·전용 지침
scripts/generate.py        도구별 파일 생성·최신 상태 검사
scripts/install.py        기존 설정 보호와 링크 설치
generated/               자동 생성 결과 (직접 편집하지 않음)
install.sh                생성과 설치 진입점
```

`generated/`는 생성물입니다. 공통 규칙은 글로벌 지침에 직접 포함하므로 Claude의 `@import`나
`.claude/rules` 자동 발견에 의존하지 않습니다. TypeScript 규칙은 글로벌 지침이 필요한 때
`~/.agents/my-agents/rules/typescript/`에서 읽도록 안내합니다. 모델이 문서를 읽는 방식이며
도구 차원의 강제 차단 기능은 아닙니다.

역할 책임은 한 벌이고, 각 도구의 모델·도구 목록·권한 형식은 어댑터에서 지정합니다.
글로벌 라우팅 표와 실제 역할 설정은 같은 모델 원본에서 생성합니다.
`shared/roles/*.md`의 frontmatter는 `description: 한 줄 설명` 형식만 사용합니다.
설명에 YAML 블록 문법이나 따옴표 구문을 쓰지 않습니다.
Claude와 Codex 모델이 같은 성능이거나 실행 권한이 동일하다는 의미는 아닙니다.

## 설치와 업데이트

Python 3.9 이상과 Bash가 필요합니다. 별도 Python 패키지는 필요 없습니다.

```bash
./install.sh             # 공통 파일 생성 + 두 도구 설치
./install.sh --claude    # Claude만 설치
./install.sh --codex     # Codex만 설치
```

원본을 수정한 뒤 `./install.sh`를 다시 실행하고 새 에이전트 세션을 시작합니다.
스킬·템플릿·언어별 규칙은 원본에 직접 연결되고, 글로벌 지침·역할은 다시 생성해야 반영됩니다.
생성 경로의 링크·충돌 또는 예상 밖 파일이 발견되면 설치를 중단합니다. 삭제한 역할의 생성 파일이
남아 있으면 보고된 파일을 확인해 정리한 뒤 다시 설치하세요. 생성기는 해당 파일을 임의 삭제하지 않습니다.
설치기는 계정의 `config.toml`, `settings.json`, MCP, 플러그인 설정을 변경하지 않습니다.

| 설치 위치 | 원본 |
| --- | --- |
| `~/.claude/CLAUDE.md` | `generated/claude/CLAUDE.md` |
| `~/.codex/AGENTS.md` | `generated/codex/AGENTS.md` |
| `~/.claude/agents/*` | `generated/claude/agents/*` |
| `~/.codex/agents/*` | `generated/codex/agents/*` |
| `~/.claude/skills/<이름>` | `shared/skills/<이름>` |
| `~/.agents/skills/<이름>` | 같은 `shared/skills/<이름>` |
| `~/.agents/my-agents/rules` | `shared/rules` |
| `~/.agents/my-agents/templates` | `shared/templates` |

`CODEX_HOME`을 지정한 경우 그 디렉터리에도 Codex 글로벌 지침과 역할을 설치합니다.
`AGENTS.override.md` 등 우선순위가 높은 외부 지침이 있으면 생성된 지침을 덮어쓸 수 있습니다.
설치는 새 세션에서 해당 도구의 지침 로딩과 모델 사용 가능 여부까지 검증하지 않습니다.

## 기존 설치 이전과 보호

- 이 저장소 내부를 직접 가리키는 기존 링크만 새 링크로 전환합니다.
- 실제 파일·폴더, 다른 저장소를 가리키는 링크와 깨진 외부 링크는 보존합니다.
- 설치 경로의 상위 디렉터리가 링크이면 그 안에 쓰지 않고 충돌로 보고합니다.
- 충돌은 건너뛰고 나머지를 설치하되 종료 코드 1을 반환합니다. 출력의 충돌 경로를 확인하세요.
- 기존 `~/.claude/rules`가 이 저장소의 링크일 때만 해제합니다. 공통 규칙이 생성된 글로벌 지침에
  포함되어 중복 적용되는 것을 막습니다. 사용자가 별도로 만든 rules는 그대로 유지합니다.
- 기존 `.claude/`, `.codex/`, `.agents/skills/` 경로는 저장소 안의 호환 링크로 유지합니다.
  그곳의 생성 파일을 직접 편집하지 말고 `shared/` 또는 `adapters/`를 수정하세요.
- 다른 스킬·에이전트·사용자 설정은 삭제하지 않습니다. 역할/스킬 이름을 나중에 삭제하거나 변경하면
  기존 설치 링크 정리는 별도로 확인해야 합니다.

개인 홈을 건드리지 않는 설치 확인:

```bash
MY_AGENTS_HOME=/tmp/my-agents-check ./install.sh
```

이 변수는 설치 테스트용입니다. 설정에 적힌 `~`는 실제 실행 계정의 홈을 뜻합니다.
테스트 모드에서는 `CODEX_HOME`에 쓰지 않습니다.

## 공통 작업 방식

개발 변경은 요청 이해와 완료 조건을 확인한 뒤 계획을 제시하고, 큰 설계·데이터·공개 인터페이스 영향이 있으면
설계도 제시합니다. 사용자가 계획 또는 설계에 명시적으로 동의한 뒤 구현·검증을 진행하고, 구현자와 분리된
reviewer가 독립 리뷰합니다. 결함은 수정한 뒤 관련 검증과 리뷰를 반복하며, 같은 실패가 반복되거나 외부 블로커가
있으면 근거와 가능한 결정을 보고해 무한 반복하지 않습니다. 기존에 같은 범위로 승인했거나 사용자가 명시적으로
즉시 진행을 지시한 경우에는 재승인을 요구하지 않습니다. 승인 전 읽기 전용 조사와 준비는 가능하지만 Full Access
같은 실행 권한은 계획 승인을 대신하지 않습니다.
구현 중 기존 승인 범위를 바꾸는 계획·설계 변경이 필요하면 영향받은 단위를 멈추고 변경 내용과 근거를 제시한 뒤,
사용자가 명시적으로 동의한 후 재개합니다.

전체 완료 조건을 대조해 변경·검증·리뷰 결과와 남은 문제를 보고하고 현재 턴을 종료해 사용자 최종 검수와 피드백을
받습니다. 구현·검증 완료와 사용자 검수 완료를 구분하며, 검수를 자동 통과로 처리하지 않습니다. 이를 위해 완료한
작업을 능동적으로 대기·sleep·poll하지 않습니다. 순수 질문과 읽기 전용 조사는 이 흐름의 대상이 아니고, HTML
문서와 퀴즈는 필수 단계가 아닙니다.

메인은 요청 이해·계획·설계·통합 판단을 맡고 현재 세션 모델을 유지합니다. scout은 탐색, implementer는 일반 구현,
implementer_deep은 어려운 구현, reviewer는 독립 리뷰를 담당합니다. 관련 보안 위험에는 auditor를, 문서 갱신에는
scribe를 사용합니다. 역할별 모델·추론 강도·권한은 `adapters/`와 생성된 글로벌 라우팅에서 관리합니다.

하위 에이전트는 메인이 전달한 승인 범위 안에서 실행하며 승인 대화를 다시 시작하지 않습니다. 도구·모델 또는
독립 reviewer를 사용할 수 없으면 그 한계와 직접 수행한 검토를 공개합니다.

기존 HTML 도식은 `docs/legacy-agent-workflow.html`에 과거 자료로 보존하며 현재 규칙으로 사용하지 않습니다.
`shared/templates/PROJECT_TEMPLATE.md`도 기존 Claude 프로젝트 템플릿을 보존한 자료입니다.
팀 프로젝트의 공유 규칙 구조는 별도 논의 후 정합니다. 설치 중 프로젝트를 생성하거나 수정하지 않습니다.

## 검증

```bash
python3 scripts/generate.py --check
python3 -m unittest discover -s tests -v
bash -n install.sh
```

생성 검사는 원본 대비 누락·변경·예상 밖 생성 파일을 확인합니다. 테스트는 양쪽 공통 내용 전파,
모델 연결, 설치 반복 실행, 기존 링크 이전, 사용자 파일·외부 링크 보호와 설치 대상 분리를 확인합니다.
