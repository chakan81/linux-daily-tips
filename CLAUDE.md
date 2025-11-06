# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**CRITICAL**:
Before performing ANY file operations (read, write, edit, delete, create) in a subdirectory, you MUST FIRST automatically read any "CLAUDE.md' file present in that target directory. This is a mandatory first step, not optional. If a 'CLAUDE. md exists in the subdirectory, read it immediately before processing the requested file operation understand the context-specific instructions and information.

## 프로젝트 개요

이 프로젝트는 **Linux Daily Tips Web Service**로, 매일 리눅스 사용 팁을 제공하고 실습 가능한 웹 터미널 환경을 제공하는 교육용 웹서비스입니다.

### 핵심 특징
- 일일 리눅스 팁 자동 게시 시스템
- 웹 기반 터미널 에뮬레이터 통합
- LLM 기반 콘텐츠 자동 생성 및 분류
- 관리자 승인 워크플로우
- 구글 애드센스 수익화

## 아키텍처 구조

### 전체 시스템 구성
```
Frontend (사용자 인터페이스)
├── 메인 페이지 (일일 팁 표시)
├── 터미널 에뮬레이터 컴포넌트
├── 히스토리/검색 페이지
└── 관리자 대시보드

Backend API 서버
├── 팁 관리 API
├── LLM 연동 서비스
├── 터미널 샌드박스 관리
└── 사용자 인증 (관리자)

데이터베이스
├── 팁 콘텐츠 (승인된 팁)
├── 드래프트 관리 (대기/승인/거절)
├── 사용자 활동 로그
└── 터미널 세션 데이터
```

### 핵심 데이터 모델
- **TipData**: 개별 팁 정보 (제목, 내용, 난이도, 카테고리, 터미널 설정)
- **DraftWeek**: 일주일치 드래프트 묶음 (LLM 생성 → 관리자 승인)
- **TerminalSetup**: 각 팁별 사전 구성 파일/디렉토리 구조

## 문서 구조

### docs/ 디렉토리
프로젝트 기획 및 설계 문서 저장소
- `requirements.md`: 전체 서비스 요구사항 정의서
- 향후 추가될 문서: 기술 스택 선정서, API 설계서, UI/UX 가이드

## 개발 워크플로우

### 3단계 개발 계획
1. **Phase 1 (MVP)**: 기본 UI, 팁 표시, 간단한 터미널
2. **Phase 2 (고급 기능)**: LLM 연동, 관리자 대시보드, 히스토리
3. **Phase 3 (수익화)**: 애드센스 연동, 성능 최적화, 배포

### 보안 고려사항
- 터미널 에뮬레이터는 안전한 샌드박스 환경에서 실행
- XSS/CSRF 공격 방어 필수
- 관리자 인증 시스템 강화 필요

### 성능 목표
- 페이지 로딩: 3초 이하
- 터미널 응답: 1초 이하
- 동시 접속자: 1000명 지원

## 특별 요구사항

### LLM 통합
- 일주일치(7개) 팁 드래프트 자동 생성
- 난이도 분류 (초급/중급/고급) 자동화
- 카테고리 태깅 자동화
- 터미널 테스트 예제 자동 생성

### 터미널 에뮬레이터
- 각 팁마다 사전 구성된 파일 시스템
- 실시간 명령어 실행 환경
- 안전한 샌드박스 격리

### 수익화 전략
- 구글 애드센스 최적 배치
- 사용자 경험 저해 최소화
- 월 방문자 10,000명, 수익 $500+ 목표

## 📊 현재 개발 상태

### Phase 1 (MVP): 100% 완료! 🎉🏆

**개발 기간**: 2025-10-01 ~ 2025-11-06 (37일)
**완료 작업**: 111/111 (100%)
**상세 진행 상황**: [docs/phase1-tasks.md](docs/phase1-tasks.md) 참조

#### 주요 성과

**Week 1 (프론트엔드)**:
- Next.js 16 + React 19.2 + TypeScript 5.9
- Zustand + React Query 상태 관리
- shadcn/ui 디자인 시스템

**Week 2 (백엔드)**:
- FastAPI + PostgreSQL 18 + Redis 8
- SQLAlchemy 2.0 Async (234개 테스트 98.3% 통과)
- JWT + OAuth 인증 시스템

**Week 3 (터미널)**:
- xterm.js 5.6.0 + WebSocket 실시간 I/O
- Docker 샌드박스 (보안 격리, 리소스 제한)
- 성능: 세션 생성 0.14초, 명령어 실행 0.055초

**Week 4 (통합)**:
- MSW 제거, 실제 API 연동
- Tips 페이지 완성 (검색/정렬/필터)
- E2E 테스트 22/22 통과 (100%)
- Docker 환경 완전 통합

**최종 결과**:
- 코드 품질: 9.5/10
- 문서화: ~4,000줄 (USER_GUIDE, DEPLOYMENT, API_REFERENCE)
- 기술 스택: Node.js 22 LTS, Python 3.14, PostgreSQL 18

**Phase 2 예정**:
- LLM 연동 (팁 자동 생성)
- 관리자 대시보드
- 고급 터미널 기능 (vim/nano 지원)

### 📂 주요 문서

**프로젝트 기획**:
- `docs/requirements.md`: 전체 서비스 요구사항 정의서
- `docs/service-planning.md`: 기술 설계 및 아키텍처
- `docs/terminal-architecture.md`: 터미널 시스템 아키텍처 설계서
- `docs/phase1-tasks.md`: Phase 1 상세 개발 계획

**개발 가이드**:
- `frontend/CLAUDE.md`: 프론트엔드 개발 가이드 + Day 27 Part 3 리팩토링 완료
- `backend/CLAUDE.md`: 백엔드 개발 가이드 (uv, TDD, Error Handling 포함)

**완료 보고서**:
- `docs/phase1-completion-report.md`: **Phase 1 MVP 완료 보고서** (Day 1-28, 전체 요약) ⭐
- `frontend/docs/DAY7_COMPLETION_REPORT.md`: Week 1 프론트엔드 완료 (17KB)
- `backend/docs/issue-fixes-completion-report.md`: 코드 품질 개선 (18KB)
- `backend/docs/redis-module-architecture.md`: Redis 아키텍처 (14KB)

**사용 가이드**:
- `docs/USER_GUIDE.md`: 사용자 가이드 (~1,200줄)
- `docs/DEPLOYMENT.md`: 배포 가이드 (~1,300줄)
- `backend/docs/API_REFERENCE.md`: API 레퍼런스 (~1,500줄)
- `backend/docs/models-usage-guide.md`: SQLAlchemy 모델 사용 가이드 (20KB)
- `backend/docs/environment-variables.md`: 환경 변수 설정 (11KB)
- `frontend/docs/DAY_7_STATE_MANAGEMENT_GUIDE.md`: 상태 관리 가이드 (9.4KB)
- `frontend/docs/USAGE_EXAMPLES.md`: React Query/Zustand 예제 (23KB)

**최근 작업 (2025-11-06)**:
- Next.js 16 빌드 이슈 해결 (Providers Client Component 분리)
- API 설계 개선 (최신 팁 반환 방식)
- UX 개선 (BackButton 브라우저 히스토리 사용)
- Dockerfile 코드 스타일 통일

---

## 🧪 테스트 전략 (도메인별 차별화)

### 백엔드: TDD 필수 ⭐⭐⭐⭐⭐

**Day 12-13부터 엄격한 TDD 적용**
- **RED → GREEN → REFACTOR** 사이클 준수
- Day 10-11에서 129개 테스트 100% 통과로 효과 검증
- API, 비즈니스 로직, 데이터베이스 계층 모두 TDD

**이유**:
- 명확한 입출력과 API 계약
- 버그 비용이 높음 (데이터 손실, 보안 이슈)
- 순수 함수가 많아 테스트 작성 용이

**상세 가이드**: `backend/CLAUDE.md` 참조

### 프론트엔드: 선택적 TDD ⭐⭐⭐

**영역별 차별화**:
- ✅ **유틸리티 함수/hooks**: TDD 권장
  - 날짜 포맷팅, 데이터 변환, 커스텀 hooks 등
- ✅ **복잡한 상태 관리**: 복잡한 로직만 TDD
  - Zustand store의 복잡한 액션/selector
- ⚠️ **UI 컴포넌트**: 시각적 개발 우선, 필요시 테스트 추가
  - 디자인 변경이 잦아 TDD 효율 낮음
- ⚠️ **E2E 테스트**: 주요 기능 완성 후 작성 (Playwright)

**이유**:
- UI는 시각적 피드백이 중요
- 디자인 반복이 많아 테스트 선작성 비효율적
- Week 1 경험: TDD 없이도 빠른 프론트엔드 구축 성공

### 터미널/WebSocket: 선택적 TDD ⭐⭐⭐⭐

**영역별 차별화**:
- ✅ **메시지 파싱/상태 관리**: TDD 권장
- ✅ **WebSocket 프로토콜 로직**: TDD 권장
- ⚠️ **xterm.js UI 연동**: 통합 테스트만
- ⚠️ **Docker 샌드박스**: 실행 확인으로 충분

### 인프라/설정: 테스트 불필요 ⭐

- Docker, CI/CD: 실행 확인이 테스트보다 직관적
- 환경 설정: 한 번 설정하고 끝

---

**핵심 원칙**: 효율과 품질의 균형. 백엔드는 엄격한 TDD, 프론트엔드는 실용적 접근.

---

## 📚 Git 워크플로우

### 브랜치 전략

| 브랜치 | 역할 | 사용 시점 |
|--------|------|-----------|
| **dev** | 개발 브랜치 | 모든 개발 작업 (일상적 커밋) |
| **main** | 배포 브랜치 | MVP/Phase 완성 후 병합 |

**핵심 원칙**:
- ✅ 개발은 항상 `dev` 브랜치에서
- ✅ `main`은 완성된 안정 버전만
- ✅ 혼자 개발 시 PR 불필요 (바로 푸시)

### 일상 워크플로우

```bash
# 1. 작업 시작
git checkout dev
git pull origin dev

# 2. 개발 후 커밋
git add .
git commit -m "타입: 간결한 제목

- 상세 내용 1
- 상세 내용 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 3. 푸시 (PR 없이 바로)
git push origin dev
```

### 커밋 타입

- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `refactor`: 리팩토링
- `test`: 테스트 추가
- `chore`: 빌드/설정 변경

### Phase 완료 시 (Main 병합)

```bash
# 1. Dev 최종 테스트 완료 후
git checkout main
git merge dev

# 2. 버전 태그 생성
git tag -a v1.0.0-mvp -m "Phase 1 MVP Release

- 주요 기능 목록
- 테스트 결과
- 성능 지표"

# 3. Main 푸시
git push origin main
git push origin v1.0.0-mvp

# 4. Dev로 복귀
git checkout dev
```

### 자주 사용하는 명령어

```bash
# 상태 확인
git status
git log --oneline -10

# 브랜치 확인
git branch
git branch -vv

# 실수 복구 (푸시 전)
git reset --soft HEAD~1  # 커밋 취소 (변경사항 유지)
git commit --amend       # 커밋 메시지 수정
```

---

## 🤖 에이전트(Agent) 적극 활용 가이드

### 복잡한 작업은 에이전트에게 위임하세요

**에이전트 사용이 필수인 상황**:
- 여러 파일에 걸친 검색/수정 작업
- 전문 도메인 지식이 필요한 코드 작성 (UI/UX, 백엔드, 프론트엔드)
- 코드 품질 평가 및 리팩토링
- 종합적인 테스트 작성
- 시스템 레벨 아키텍처 설계

**주요 에이전트**:
- `general-purpose`: 코드 검색, 분석, 다단계 작업
- `ui-ux-designer`: UI/UX 설계, 디자인 시스템
- `frontend-code-writer`: React/Next.js 코드 작성
- `backend-code-writer`: FastAPI/Django 코드 작성
- `code-quality-evaluator`: 코드 품질 평가
- `code-refactoring-specialist`: 리팩토링
- `unit-test-generator`: 테스트 작성
- `service-planner`: 아키텍처 설계

**활용 원칙**:
- 독립적인 작업은 여러 에이전트를 병렬 실행
- 구체적인 작업 설명으로 자율적 실행 유도
- 에이전트 완료 후 결과 검토 필수