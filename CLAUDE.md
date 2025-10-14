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

### Phase 1 (MVP) 진행률: 32% (21/65 작업 완료)

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

#### 🔄 Week 2 진행 중 (Day 8-14)
**백엔드 API 개발**
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
- ⏳ Tips API 개발 (CRUD) (Day 12-13 예정 - TDD 적용)
- ⏳ Redis 캐싱 및 JWT 인증 (Day 14 예정)

#### ⏳ Week 3-4 예정
- 터미널 에뮬레이터 (xterm.js + WebSocket + Docker)
- 시스템 통합 및 성능 최적화
- 테스트 및 문서화

### 📂 주요 문서
- `docs/requirements.md`: 전체 서비스 요구사항 정의서
- `docs/service-planning.md`: 기술 설계 및 아키텍처
- `docs/phase1-tasks.md`: Phase 1 상세 개발 계획 (리팩토링 반영)
- `frontend/CLAUDE.md`: 프론트엔드 개발 가이드
- `backend/CLAUDE.md`: 백엔드 개발 가이드 (uv, TDD, Error Handling 포함)
- `frontend/docs/`: Day 7 완료 보고서
- `backend/docs/`: Day 8-9, 10-11 완료 보고서, 코드 리팩토링 보고서, 모델 사용 가이드

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