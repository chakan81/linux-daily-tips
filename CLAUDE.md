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