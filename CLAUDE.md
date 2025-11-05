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

### Phase 1 (MVP) 진행률: 91% (87/96 작업 완료)

#### ✅ Week 1 완료 (Day 1-7)
**프론트엔드 인프라 100% 완료**
- 프로젝트 초기 설정 (Docker Compose, CI/CD)
- Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
- 상태 관리 시스템 (Zustand + React Query)
- API 클라이언트 (Axios + 25+ endpoints)
- 에러 처리 및 로딩 컴포넌트
- 다크모드 및 반응형 레이아웃

**추가 완료: 백엔드 인프라 최적화**
- Poetry → **uv** 전환 완료 (10-100배 빠른 패키지 설치)
- Docker 가상환경 최적화 (불필요한 venv 제거)
- FastAPI 기본 앱 실행 확인

#### ✅ Week 2 완료 (Day 8-14)
**백엔드 API 개발 100% 완료**
- ✅ FastAPI 프로젝트 구조 설계 (Day 8-9 완료!)
  - 완전한 프로젝트 구조 (core, api, models, schemas, services)
  - 보안 아키텍처 (JWT + OAuth 준비)
  - Mock Tips API 구현 (daily, list, detail)
  - Swagger UI 자동 문서
- ✅ PostgreSQL 데이터베이스 스키마 및 ORM (Day 10-11 완료!)
  - SQLAlchemy 2.0 Async 완전 구현
  - 6개 모델 + Pydantic 스키마
  - **129개 pytest 테스트 100% 통과** ✨
  - ULID + 프리픽스 ID 시스템
  - **코드 품질 평가 및 리팩토링 완료** (8.3 → 9.0/10)
  - AppException + 구조화 로깅 시스템
- ✅ Tips API 개발 (Day 12-13 완료!)
  - TDD 방식 개발 (21개 테스트 100% 통과)
  - Service 계층 완성, Alembic 마이그레이션
  - 성능 인덱스 추가 (3개)
  - **코드 품질: 9.2/10** (Day 10-11 대비 +0.2)
- ✅ Redis 캐싱 및 JWT 인증 (Day 14 완료!)
  - Redis 캐싱 (90% 성능 개선)
  - Google OAuth 2.0 + JWT 인증 시스템
  - API Rate Limiting (slowapi)
  - 234개 테스트 98.3% 통과 (230/234)
  - 코드 품질: 9.1/10
- ✅ 코드 품질 이슈 수정 (2025-11-03 완료!)
  - Redis 에러 처리 표준화 (30+ print → logger)
  - 환경 변수 기반 설정 강화 (HTTP/세션 TTL)
  - EncryptionService 예외 처리 추가 (InvalidToken)
  - 타임아웃 처리 일관성 개선
  - **코드 품질: 9.5/10** (9.1 → 9.5, +4.4% 개선) ✨

#### ✅ Week 3 완료 (Day 15-21) 🎉
**터미널 에뮬레이터 100% 완료 (PoC 수준)**
- ✅ Day 15-16: 프론트엔드 터미널 UI
  - xterm.js 5.6.0 터미널 UI 브라우저 렌더링
  - 기본 입력/출력 테스트 완료
- ✅ Day 17-18: WebSocket 실시간 통신
  - 프론트엔드-백엔드 WebSocket 연결
  - 메시지 송수신, 재연결 로직 (3회 시도)
- ✅ Day 19-20: Docker 컨테이너 통합
  - Docker 컨테이너 명령어 실행 (ls, pwd, cat, echo)
  - 세션 생성/종료 API 구현
  - Playwright 자동화 테스트 통과
- ✅ Day 21: 보안 강화 및 최적화 **[오늘 완료!]**
  - **보안 검증**: 네트워크 격리, 리소스 제한 (256MB, CPU 0.5코어) 실제 동작 확인
  - **성능 측정**: 세션 생성 0.14초, 명령어 실행 0.055초 (목표 초과 달성!)
  - **컨테이너 정리 크론잡**: 1분 주기 백그라운드 작업 구현
  - **동시 세션 테스트**: 5개 0.32초, 10개 0.42초 (모두 < 2초 달성)
  - **완료 보고서**: backend/docs/day21-security-optimization.md

**Week 3 성과 요약**:
- ✅ PoC 수준 터미널 완성 (라인 버퍼 모드)
- ✅ 보안: 네트워크 격리, 리소스 제한, 세션 타임아웃 30분
- ✅ 성능: 모든 목표 초과 달성 (세션 생성 < 2초, 명령어 < 1초)
- ⚠️ 제약: vim/nano 미지원, 실시간 입력 불가, 특수 키 미처리 → Phase 2에서 개선

#### ✅ Week 4 완료 (Day 22-27) 🎉
**프론트엔드-백엔드 통합 92% 완료**
- ✅ Day 22-24: MSW 제거 및 API 통합 **[완료!]**
  - **MSW 완전 제거**: 596줄 Mock 코드 삭제, 33개 패키지 제거
  - **실제 백엔드 API 연동**: 홈페이지에서 실제 데이터 표시 확인
  - **버그 수정**: 카테고리 배열 표시, 터미널 레이스 컨디션
  - **통합 테스트 성공**: 홈페이지, 터미널 WebSocket 완전 작동

- ✅ Day 25: 코드 품질 개선 **[완료!]**
  - **API 네이밍 완전 해결**: Pydantic alias_generator (snake_case → camelCase)
  - **Frontend cleanup**: 모든 `any` 타입 제거
  - **타입 안전성 100%**: TypeScript 컴파일 에러 없음

- ✅ Day 26: Tips 페이지 구현 **[완료!]**
  - 팁 상세/목록 페이지 완성 (`/tips`, `/tips/[id]`)
  - 검색/정렬/필터 기능 구현
  - URL 상태 관리 (query parameters)

- ✅ Day 27 Part 1: 검색/정렬 API + Node.js 22 **[완료!]** (2025-11-05)
  - **검색 API**: ILIKE 패턴, 대소문자 무시
  - **정렬 API**: publish_date/title, asc/desc
  - **보안**: Whitelist 기반 SQL Injection 방지
  - **TDD**: 11개 테스트 100% 통과
  - **Node.js 22 LTS**: @types/node 22.19.0, 2027년까지 지원
  - **Next.js 16 Suspense**: useSearchParams() 감싸기 완료
  - 📊 완료 보고서: `backend/docs/day27-search-sort-completion-report.md`

- ✅ Day 27 Part 2: E2E 테스트 & Docker 완전 통합 **[완료!]** (2025-11-05) 🎉
  - **E2E 테스트**: 22/22 통과 (100%, 50.5초) - 이전 8/22 (36%)에서 개선
  - **브라우저 API**: 오늘의 팁 + 최근 팁 5개 정상 표시
  - **Next.js rewrites 프록시**: `/api/*` → `backend:8000/api/*` 완성
  - **환경 변수 수정**: `next.config.js` env 섹션 (`!== undefined` 체크)
  - **Docker 통합**: Frontend + Backend + DB 완전 작동
  - 📊 완료 보고서: `docs/day27-part2-completion-report.md`

**Week 4 성과 요약**:
- ✅ MSW → 실제 백엔드 API 전환 완료
- ✅ Tips 페이지 완전 구현 (검색/정렬/필터 포함)
- ✅ 검색/정렬 백엔드 API TDD 구현
- ✅ Node.js 22 LTS 업그레이드 완료
- ✅ 터미널 시스템 WebSocket 완전 작동
- ✅ **E2E 테스트 100% 통과** (22/22) ⭐
- ✅ **Docker 환경 완전 통합** ⭐

#### ⏳ Week 4 남은 작업 (Day 28)
- 성능 최적화 (Lighthouse 90+)
- 문서화 (사용자 가이드, API 문서, 배포 가이드)

### 📂 주요 문서

**프로젝트 기획**:
- `docs/requirements.md`: 전체 서비스 요구사항 정의서
- `docs/service-planning.md`: 기술 설계 및 아키텍처
- `docs/terminal-architecture.md`: 터미널 시스템 아키텍처 설계서
- `docs/phase1-tasks.md`: Phase 1 상세 개발 계획

**개발 가이드**:
- `frontend/CLAUDE.md`: 프론트엔드 개발 가이드
- `backend/CLAUDE.md`: 백엔드 개발 가이드 (uv, TDD, Error Handling 포함)
- `backend/docs/models-usage-guide.md`: SQLAlchemy 사용 가이드
- `backend/docs/environment-variables.md`: 환경 변수 설정 가이드 ✨ 신규

**완료 보고서**:
- `frontend/docs/`: Day 7 완료 보고서
- `backend/docs/`: Day 8-9, 10-11, 12-13, 14, 21, 27 Part 1 완료 보고서
- `backend/docs/day27-search-sort-completion-report.md`: 검색/정렬 API TDD 완료
- `backend/docs/issue-fixes-completion-report.md`: 코드 품질 이슈 수정
- `backend/docs/redis-module-architecture.md`: Redis 모듈 아키텍처
- `backend/docs/code-refactoring-report.md`: 코드 리팩토링 보고서
- `docs/tips-pages-implementation-plan.md`: Day 23-24 통합 완료 분석
- `docs/framework-update-plan.md`: Node.js 22 LTS 업그레이드
- `docs/day27-part2-completion-report.md`: E2E 테스트 & Docker 통합 완료 ✨ 신규
- `docs/day27-part2-session-resume.md`: 세션 중단/재개 가이드

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