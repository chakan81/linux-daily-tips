# Frontend - Linux Daily Tips

이 디렉토리는 Linux Daily Tips 웹서비스의 프론트엔드 애플리케이션을 포함합니다.

## 기술 스택
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: Shadcn/ui
- **Terminal**: xterm.js
- **State Management**: Zustand

## 주요 기능
- 일일 리눅스 팁 표시
- 웹 터미널 에뮬레이터
- 팁 히스토리 및 검색
- 관리자 대시보드 (Phase 2)
- 반응형 UI 디자인

## 개발 계획
- **Phase 1**: 기본 UI 컴포넌트, 팁 표시, 간단한 터미널
- **Phase 2**: 고급 터미널 기능, 관리자 대시보드
- **Phase 3**: 성능 최적화, 애드센스 연동

## 설치 및 실행
```bash
# 패키지 설치 (향후)
npm install

# 개발 서버 실행 (향후)
npm run dev
```

## 폴더 구조 (예정)
```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   ├── components/       # 재사용 가능한 컴포넌트
│   ├── lib/             # 유틸리티 함수
│   └── types/           # TypeScript 타입 정의
├── public/              # 정적 파일
└── package.json         # 프로젝트 설정
```