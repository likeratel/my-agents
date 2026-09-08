# 프로젝트별 Claude Code 규칙 템플릿

이 템플릿을 사용하여 프로젝트별 `.claude/PROJECT_RULES.md` 파일을 생성하세요.

## 사용 방법

1. 프로젝트 루트에 `.claude` 디렉토리 생성
2. 이 템플릿을 복사하여 `.claude/PROJECT_RULES.md` 생성
3. 프로젝트에 맞게 섹션 커스터마이즈
4. 프로젝트의 `CLAUDE.md`에서 참조:
   ```markdown
   @.claude/PROJECT_RULES.md
   ```

---

# PROJECT_RULES.md 템플릿

```markdown
# [프로젝트명] Claude Code 규칙

**프로젝트 타입**: [Backend API / Frontend React / Mobile App / CLI Tool / Library]
**메인 언어**: [TypeScript / Python / Go / Rust]
**프레임워크**: [NestJS / Next.js / FastAPI / Express]

---

## 🚫 절대 금지 (NEVER)

### 배포 관련
- ❌ **Claude는 절대 배포하지 않음**
  - `yarn deploy:*` 명령 실행 금지
  - `cdk deploy` 실행 금지
  - CI/CD 트리거 금지
  - 배포는 개발자만 직접 실행

### 코드 품질
- ❌ **[프로젝트 특화 금지사항]**
  - 예: 테스트에서 모킹 금지 (FAKE 사용)
  - 예: any 타입 사용 금지
  - 예: console.log 프로덕션 코드에 사용 금지

### 데이터 안전성
- ❌ **[프로젝트 특화 데이터 규칙]**
  - 예: 프로덕션 DB 직접 접근 금지
  - 예: 민감 정보 로그 출력 금지
  - 예: 환경 변수 하드코딩 금지

---

## ✅ 필수 규칙 (MUST)

### 코딩 컨벤션
**타입 시스템**:
- [프로젝트 타입 규칙]
- 예: 모든 함수에 명시적 타입 지정
- 예: DTO 클래스 사용 필수

**네이밍 컨벤션**:
- [프로젝트 네이밍 규칙]
- 예: camelCase (TypeScript)
- 예: snake_case (Python)
- 예: PascalCase (컴포넌트/클래스)

**파일 구조**:
```
[프로젝트 디렉토리 구조]
예:
src/
├── controllers/     # API 엔드포인트
├── services/        # 비즈니스 로직
├── repositories/    # 데이터 접근
└── models/          # 데이터 모델
```

### 테스트 규칙
**테스트 전략**:
- [프로젝트 테스트 규칙]
- 예: 테스트 스켈레톤만 생성, 내용은 개발자가 작성
- 예: 모킹 대신 FAKE 구현 사용
- 예: 최소 커버리지: 80%

**테스트 위치**:
- 유닛 테스트: `__tests__/` 또는 `*.test.ts`
- 통합 테스트: `tests/integration/`
- E2E 테스트: `tests/e2e/`

### 에러 처리
**에러 패턴**:
- [프로젝트 에러 처리 방식]
- 예: neverthrow Result 패턴 사용
- 예: ts-pattern으로 exhaustive 검사
- 예: 커스텀 ErrorCode enum 사용

### 로깅
**로깅 규칙**:
- [프로젝트 로깅 전략]
- 예: 외부 API 호출 시 항상 로그
- 예: 구조화된 JSON 로깅
- 예: 민감 정보 마스킹
- 예: correlation ID 포함

---

## 🔧 프로젝트 특화 패턴

### 아키텍처 패턴
**디자인 패턴**:
- [프로젝트에서 사용하는 패턴]
- 예: Hexagonal Architecture
- 예: Domain-Driven Design
- 예: Event-Driven Architecture

**계층 구조**:
```
[프로젝트 계층 설명]
예:
Controller → Service → Repository → Database
         ↓
    Event Publisher → Message Queue
```

### 데이터 액세스
**데이터베이스**:
- [데이터베이스 종류 및 ORM]
- 예: PostgreSQL + TypeORM
- 예: DynamoDB + 싱글 테이블 패턴
- 예: MongoDB + Mongoose

**쿼리 규칙**:
- [쿼리 작성 규칙]
- 예: Raw Query 금지, ORM 사용
- 예: N+1 쿼리 방지
- 예: 트랜잭션 사용 원칙

### API 설계
**API 스타일**:
- [API 컨벤션]
- 예: RESTful API
- 예: GraphQL
- 예: gRPC

**요청/응답 패턴**:
```
[프로젝트 API 패턴]
예:
Request:
{
  "data": { ... },
  "metadata": { "requestId": "..." }
}

Response:
{
  "success": true,
  "data": { ... },
  "error": null
}
```

---

## 🛠️ 개발 워크플로우

### 브랜치 전략
**브랜치 규칙**:
- [Git 브랜치 전략]
- 예: `main` - 프로덕션
- 예: `develop` - 개발
- 예: `feature/*` - 기능 개발
- 예: `hotfix/*` - 긴급 수정

### 커밋 메시지
**커밋 포맷**:
```
[프로젝트 커밋 컨벤션]
예: Conventional Commits
feat: 새 기능 추가
fix: 버그 수정
docs: 문서 변경
refactor: 리팩토링
test: 테스트 추가/수정
```

### 코드 리뷰
**리뷰 체크리스트**:
- [ ] [프로젝트 리뷰 항목들]
- [ ] 타입 안전성 확인
- [ ] 테스트 커버리지 확인
- [ ] 에러 처리 확인
- [ ] 로깅 적절성 확인

---

## 📚 프로젝트 참조 자료

### 필수 문서
- [프로젝트 문서 링크]
- 예: API 문서: https://api-docs.example.com
- 예: 아키텍처 가이드: /docs/architecture.md
- 예: 개발 가이드: /docs/development.md

### 외부 의존성
**주요 라이브러리**:
- [핵심 라이브러리 목록]
- 예: NestJS (프레임워크)
- 예: TypeORM (ORM)
- 예: neverthrow (에러 처리)

**버전 정책**:
- [버전 관리 전략]
- 예: package.json 정확한 버전 고정
- 예: 메이저 업데이트 전 검증 필수

---

## 🎯 작업 프로세스

### 새 기능 추가
1. [프로젝트 기능 추가 절차]
2. 예:
   - 브랜치 생성: `feature/[기능명]`
   - 계획 문서화 (Planning Mode)
   - 구현 (TDD 권장)
   - 테스트 작성
   - 코드 리뷰
   - 머지

### 버그 수정
1. [프로젝트 버그 수정 절차]
2. 예:
   - 재현 가능한 테스트 작성
   - 근본 원인 파악
   - 수정 구현
   - 회귀 테스트 추가
   - 문서화

### 리팩토링
1. [프로젝트 리팩토링 절차]
2. 예:
   - 기존 테스트 확인 (모두 통과해야 함)
   - 점진적 변경
   - 각 단계마다 테스트
   - 성능 측정 (before/after)

---

## 🔍 디버깅 가이드

### 로그 위치
```
[프로젝트 로그 위치]
예:
- 로컬: `logs/app.log`
- 개발: CloudWatch `/aws/lambda/dev-*`
- 운영: CloudWatch `/aws/lambda/prd-*`
```

### 디버깅 도구
- [프로젝트 디버깅 도구]
- 예: VS Code Debugger 설정
- 예: AWS X-Ray (분산 추적)
- 예: Datadog (모니터링)

### 자주 발생하는 이슈
**[이슈 타입 1]**:
- 증상: [설명]
- 원인: [원인]
- 해결: [해결 방법]

**[이슈 타입 2]**:
- 증상: [설명]
- 원인: [원인]
- 해결: [해결 방법]

---

## 💡 프로젝트 특화 Best Practices

### DO ✅
- [프로젝트 권장 사항들]
- 예: 항상 DTO 타입 사용
- 예: 비동기 작업은 Queue 사용
- 예: 캐싱 전략 고려

### DON'T ❌
- [프로젝트 비권장 사항들]
- 예: 동기 API 호출 금지
- 예: 글로벌 상태 변경 금지
- 예: 하드코딩 금지

---

## 🚀 배포

### 배포 전 체크리스트
- [ ] [배포 전 확인 사항]
- [ ] 모든 테스트 통과
- [ ] 린트/포맷 통과
- [ ] 환경 변수 확인
- [ ] 문서 업데이트

### 배포 명령 (개발자만 실행)
```bash
# [프로젝트 배포 명령어들]
# 개발 환경
yarn deploy:dev

# 스테이징 환경
yarn deploy:stg

# 운영 환경 (주의!)
yarn deploy:prd
```

### 롤백 절차
1. [프로젝트 롤백 방법]
2. 예:
   - 이전 버전 확인
   - 롤백 명령 실행
   - 동작 검증
   - 이슈 문서화

---

## 📞 팀 연락처 및 리소스

### 주요 담당자
- Tech Lead: [이름/연락처]
- DevOps: [이름/연락처]
- QA: [이름/연락처]

### 유용한 링크
- Slack: #[channel-name]
- Jira: [프로젝트 보드]
- Confluence: [위키]
- Monitoring: [모니터링 대시보드]

---

## 업데이트 로그

**[YYYY-MM-DD]**: [초기 생성 또는 주요 변경 사항]
```

---

## 실제 프로젝트 적용 예시

### Backend API (NestJS) 프로젝트
```markdown
**프로젝트 타입**: Backend API
**메인 언어**: TypeScript
**프레임워크**: NestJS

## 🚫 절대 금지
- ❌ 테스트에서 Mock 사용 금지 (FAKE 구현만 허용)
- ❌ any 타입 사용 절대 금지
- ❌ console.log 사용 금지 (Logger 서비스 사용)

## ✅ 필수 규칙
### 에러 처리
- neverthrow Result 패턴 필수
- 모든 외부 호출은 Result<T, E> 반환

### 로깅
- 모든 외부 API 호출 로그 필수
- 요청/응답 데이터 포함
- correlation ID 필수
```

### Frontend React 프로젝트
```markdown
**프로젝트 타입**: Frontend SPA
**메인 언어**: TypeScript
**프레임워크**: React + Next.js

## 🚫 절대 금지
- ❌ 인라인 스타일 금지 (Tailwind 또는 CSS Modules 사용)
- ❌ localStorage에 민감 정보 저장 금지
- ❌ useEffect 무한 루프 주의

## ✅ 필수 규칙
### 컴포넌트 구조
- atomic 디자인 패턴
- atoms/ molecules/ organisms/ templates/ pages/

### 상태 관리
- Zustand 사용
- 전역 상태 최소화
```

### Mobile App (React Native) 프로젝트
```markdown
**프로젝트 타입**: Mobile App
**메인 언어**: TypeScript
**프레임워크**: React Native + Expo

## 🚫 절대 금지
- ❌ iOS/Android 동시 빌드 전 양쪽 테스트 필수
- ❌ 네이티브 모듈 직접 수정 금지

## ✅ 필수 규칙
### 플랫폼 대응
- Platform.select 사용
- Android/iOS 차이 문서화
```

---

## 템플릿 커스터마이즈 가이드

### 1. 프로젝트 타입별로 불필요한 섹션 제거
- CLI 도구면 API 설계 섹션 제거
- 라이브러리면 배포 섹션 간소화

### 2. 팀 컨벤션 반영
- 실제 사용하는 브랜치 전략
- 실제 커밋 메시지 포맷
- 실제 코드 리뷰 체크리스트

### 3. 프로젝트 히스토리 추가
- 자주 발생하는 이슈와 해결법
- 아키텍처 결정 이유
- 트레이드오프 선택 배경

### 4. 지속적 업데이트
- 새로운 패턴 발견 시 추가
- 안티패턴 발견 시 경고 추가
- 버전 업데이트 시 변경사항 반영

---

## 글로벌 vs 프로젝트별 규칙 구분

### 글로벌 규칙 (`~/.claude/`)
- ✅ 모든 프로젝트 공통
- ✅ 범용 엔지니어링 원칙
- ✅ 도구 사용법
- ✅ 개인 작업 스타일

### 프로젝트별 규칙 (`.claude/PROJECT_RULES.md`)
- ✅ 프로젝트 특화 컨벤션
- ✅ 팀 규칙 및 워크플로우
- ✅ 아키텍처 패턴
- ✅ 배포 절차
