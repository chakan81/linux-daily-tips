# Phase 2 개발 계획 - Linux Daily Tips 웹서비스

## 📋 Phase 2 개요

### 프로젝트 현황
- **Phase 1 완료**: 2025-11-06 (100% 완료, 126/126 작업)
- **Phase 2 시작**: 2025-11-07 (예정)
- **Phase 2 완료**: 2025-12-04 (예정, 4주 후)

### Phase 2 목표 및 범위

#### 핵심 목표
- **기간**: 4주 (Week 5-8, Day 29-56)
- **핵심**: LLM 통합 + 관리자 대시보드 + 고급 터미널
- **성능**: Phase 1 수준 유지 (세션 < 2초, 명령어 < 1초)
- **품질**: 코드 품질 9.5/10 유지, 테스트 커버리지 90%+

#### 범위 정의

**필수 기능 (High Priority) ⭐⭐⭐⭐⭐**
1. LLM API 연동 (OpenAI GPT-4 / Claude)
2. 드래프트 관리 시스템 (생성/승인/거절/일정)
3. 관리자 대시보드 UI
4. PTY 기반 완전한 터미널 (vim/nano 지원)

**선택 기능 (Medium Priority) ⭐⭐⭐**
5. 고급 검색 및 필터링
6. 히스토리 페이지 (무한 스크롤)
7. 반응형 디자인 최적화
8. 접근성 개선 (WCAG 2.1)

**확장 기능 (Low Priority) ⭐**
9. 실시간 대시보드 (사용자 통계)
10. 시스템 모니터링 도구

---

## 📅 주차별 세부 개발 계획

### 🔥 Week 5 (Day 29-35): LLM 통합 및 드래프트 시스템

#### Day 29-30: LLM API 연동 설계 및 구현
**목표**: OpenAI/Claude API 통합 및 팁 자동 생성 프로토타입

**백엔드 작업**:
- [ ] LLM 설정 환경 변수 추가
  - `OPENAI_API_KEY` - OpenAI API 키
  - `ANTHROPIC_API_KEY` - Claude API 키
  - `LLM_PROVIDER` - 사용할 LLM 제공자 (openai/anthropic)
  - `LLM_MODEL` - 모델 이름 (gpt-4, claude-3-sonnet 등)
  - `LLM_MAX_TOKENS` - 최대 토큰 수
  - `LLM_TEMPERATURE` - 창의성 파라미터

- [ ] `app/services/llm/` 모듈 생성
  - [ ] `llm_client.py` - OpenAI/Claude 클라이언트 래퍼
    ```python
    class LLMClient(ABC):
        async def generate_tip(self, prompt: str) -> TipData
        async def generate_tips_batch(self, count: int = 7) -> List[TipData]

    class OpenAIClient(LLMClient):
        # OpenAI API 구현

    class ClaudeClient(LLMClient):
        # Anthropic API 구현
    ```

  - [ ] `prompt_templates.py` - 팁 생성 프롬프트 템플릿
    ```python
    TIP_GENERATION_PROMPT = """
    리눅스 명령어 팁을 생성해주세요.

    요구사항:
    - 제목: 명확하고 간결한 제목
    - 내용: 실용적이고 유용한 설명
    - 난이도: beginner/intermediate/advanced 중 하나
    - 카테고리: file-management/network/system/productivity 등
    - 터미널 설정: 실습 가능한 파일/디렉토리 구조

    출력 형식: JSON
    """
    ```

  - [ ] `content_generator.py` - 병렬 7개 팁 생성 로직
    ```python
    async def generate_weekly_tips():
        # asyncio.gather로 병렬 생성
        # 7개 팁 < 10초 목표
    ```

  - [ ] `content_validator.py` - Pydantic 기반 품질 검증
    ```python
    class TipValidator:
        def validate_structure(tip: dict) -> TipData
        def validate_quality(tip: TipData) -> bool
        def validate_terminal_setup(setup: dict) -> bool
    ```

- [ ] TDD: 15개 LLM 서비스 테스트 작성
  - [ ] Mock API 응답 테스트
  - [ ] 병렬 생성 성능 테스트 (7개 < 10초)
  - [ ] 에러 처리 (API 실패, 타임아웃)
  - [ ] 프롬프트 템플릿 테스트
  - [ ] Pydantic 검증 테스트

**완료 기준**:
- ✅ OpenAI API로 단일 팁 생성 성공 (< 5초)
- ✅ 7개 팁 병렬 생성 성공 (< 10초)
- ✅ Pydantic 검증 통과 (난이도, 카테고리, terminal_setup 자동 분류)
- ✅ 에러 처리 및 재시도 로직 구현
- ✅ 테스트 커버리지 90%+

#### Day 31-32: 드래프트 관리 시스템 구현
**목표**: DraftWeek 모델 활용한 드래프트 CRUD

**백엔드 작업**:
- [ ] `app/services/draft/` 모듈 생성
  - [ ] `draft_crud.py` - 드래프트 생성/조회/수정/삭제
    ```python
    class DraftService:
        async def create_draft_week(tips: List[TipData]) -> DraftWeek
        async def get_draft_week(id: UUID) -> DraftWeek
        async def update_draft_tip(draft_id: UUID, tip_id: UUID, data: TipUpdate)
        async def delete_draft_week(id: UUID)
    ```

  - [ ] `draft_approval.py` - 승인/거절 워크플로우
    ```python
    class ApprovalWorkflow:
        async def approve_draft(draft_id: UUID, approved_by: str)
        async def reject_draft(draft_id: UUID, rejected_by: str, reason: str)
        async def schedule_approved_tips(draft_week: DraftWeek)
    ```

  - [ ] `draft_scheduler.py` - 일정 관리 (특정 날짜에 자동 게시)
    ```python
    class DraftScheduler:
        async def schedule_tips_for_week(start_date: date)
        async def publish_scheduled_tip(tip_id: UUID)
        async def get_publication_calendar() -> Dict[date, TipData]
    ```

- [ ] `app/api/v1/endpoints/draft.py` - Admin API 엔드포인트
  ```python
  @router.post("/api/v1/admin/drafts/generate")
  async def generate_draft_week():
      """LLM을 사용해 일주일치 드래프트 생성"""

  @router.get("/api/v1/admin/drafts")
  async def list_draft_weeks():
      """모든 드래프트 주간 목록 조회"""

  @router.get("/api/v1/admin/drafts/{id}")
  async def get_draft_week_detail(id: UUID):
      """특정 드래프트 주간 상세 조회"""

  @router.put("/api/v1/admin/drafts/{id}/tips/{tip_id}")
  async def update_draft_tip(id: UUID, tip_id: UUID, data: TipUpdate):
      """개별 팁 수정"""

  @router.post("/api/v1/admin/drafts/{id}/approve")
  async def approve_draft_week(id: UUID):
      """드래프트 승인 및 게시 일정 설정"""

  @router.post("/api/v1/admin/drafts/{id}/reject")
  async def reject_draft_week(id: UUID, reason: str):
      """드래프트 거절"""

  @router.delete("/api/v1/admin/drafts/{id}")
  async def delete_draft_week(id: UUID):
      """드래프트 삭제"""
  ```

- [ ] TDD: 20개 드래프트 서비스 테스트 작성
  - [ ] CRUD 동작 검증
  - [ ] 승인 워크플로우 상태 전이 테스트
  - [ ] 일정 관리 로직 테스트
  - [ ] 권한 검증 테스트
  - [ ] 동시성 테스트 (여러 관리자가 동시에 편집)

**완료 기준**:
- ✅ 드래프트 생성 API 정상 동작 (LLM 연동)
- ✅ 승인/거절 워크플로우 완성 (status: draft → approved/rejected)
- ✅ 승인된 팁 자동 게시 로직 구현
- ✅ API 문서 자동 생성 (FastAPI)
- ✅ 테스트 커버리지 95%+

#### Day 33-34: 관리자 대시보드 프론트엔드 (Part 1)
**목표**: 드래프트 관리 UI 구현

**프론트엔드 작업**:
- [ ] `app/admin/` 라우트 그룹 생성
  - [ ] `layout.tsx` - 관리자 레이아웃 (사이드바, 헤더)
  - [ ] `page.tsx` - 관리자 대시보드 홈

- [ ] `app/admin/drafts/` 페이지 생성
  - [ ] `page.tsx` - 드래프트 목록 페이지
    ```tsx
    // 드래프트 주간 목록 테이블
    // 상태별 필터 (draft/approved/rejected)
    // 생성 날짜별 정렬
    ```

  - [ ] `[id]/page.tsx` - 드래프트 상세/편집 페이지
    ```tsx
    // 7개 팁 카드 레이아웃
    // 개별 팁 편집 폼
    // 승인/거절 버튼
    ```

  - [ ] `generate/page.tsx` - 드래프트 생성 페이지
    ```tsx
    // LLM 설정 옵션
    // 생성 진행 상태
    // 생성 결과 미리보기
    ```

- [ ] `components/admin/` 컴포넌트 생성
  - [ ] `DraftList.tsx` - 드래프트 테이블 (status, date, actions)
    ```tsx
    interface DraftListProps {
      drafts: DraftWeek[]
      onEdit: (id: string) => void
      onDelete: (id: string) => void
    }
    ```

  - [ ] `DraftEditor.tsx` - 개별 팁 편집 폼
    ```tsx
    interface DraftEditorProps {
      tip: TipData
      onChange: (tip: TipData) => void
    }
    ```

  - [ ] `DraftApprovalModal.tsx` - 승인/거절 확인 모달
    ```tsx
    interface ApprovalModalProps {
      draft: DraftWeek
      onApprove: () => void
      onReject: (reason: string) => void
    }
    ```

  - [ ] `LLMGenerateButton.tsx` - 드래프트 생성 버튼
    ```tsx
    // 생성 중 로딩 상태
    // 에러 처리
    // 성공 시 리다이렉트
    ```

  - [ ] `AdminSidebar.tsx` - 관리자 사이드바 네비게이션
  - [ ] `AdminHeader.tsx` - 관리자 헤더 (로그아웃 버튼)

- [ ] React Query hooks
  - [ ] `useDrafts()` - 드래프트 목록 조회
  - [ ] `useDraft(id)` - 드래프트 상세 조회
  - [ ] `useGenerateDraft()` - 드래프트 생성 (mutation)
  - [ ] `useApproveDraft()` - 드래프트 승인 (mutation)
  - [ ] `useRejectDraft()` - 드래프트 거절 (mutation)
  - [ ] `useUpdateDraftTip()` - 개별 팁 수정 (mutation)
  - [ ] `useDeleteDraft()` - 드래프트 삭제 (mutation)

- [ ] Zustand store 확장
  - [ ] `adminStore.ts` - 관리자 상태 관리
    ```typescript
    interface AdminStore {
      isAdmin: boolean
      adminToken: string | null
      setAdminAuth: (token: string) => void
      clearAdminAuth: () => void
    }
    ```

**완료 기준**:
- ✅ 드래프트 목록 페이지 정상 렌더링
- ✅ "Generate Draft" 버튼 클릭 → LLM 생성 → 로딩 → 결과 표시
- ✅ 드래프트 편집 및 승인/거절 동작 확인
- ✅ 관리자 인증 보호 (미인증 시 리다이렉트)
- ✅ 반응형 UI (모바일/태블릿 지원)

#### Day 35: 드래프트 시스템 통합 테스트
**목표**: E2E 테스트 및 버그 수정

**통합 작업**:
- [ ] Playwright E2E 테스트 (10개)
  - [ ] 관리자 로그인 플로우
  - [ ] 드래프트 생성 플로우 (LLM → 드래프트 → 승인 → 게시)
  - [ ] 드래프트 편집 플로우
  - [ ] 드래프트 거절 플로우
  - [ ] 드래프트 삭제 플로우
  - [ ] 승인된 팁 자동 게시 확인
  - [ ] 권한 없는 접근 차단 테스트
  - [ ] 동시 편집 충돌 해결 테스트
  - [ ] LLM API 실패 시 에러 처리
  - [ ] 네트워크 에러 시 재시도

- [ ] 에러 처리 개선
  - [ ] LLM API 실패 시 재시도 로직 (3회)
  - [ ] 네트워크 에러 시 사용자 피드백
  - [ ] 입력 검증 에러 메시지
  - [ ] 서버 에러 시 graceful degradation

- [ ] 로깅 및 모니터링
  - [ ] LLM 생성 시간 추적
  - [ ] 드래프트 승인율 통계
  - [ ] API 호출 로그
  - [ ] 에러 로그 수집

- [ ] 성능 측정
  - [ ] LLM 생성 시간 (목표: 7개 < 10초)
  - [ ] 드래프트 목록 로딩 시간 (< 1초)
  - [ ] 편집 저장 시간 (< 2초)

**Week 5 완료 보고서**:
- [ ] 주요 성과 정리
- [ ] 기술적 도전과 해결
- [ ] 다음 주 준비 사항

**완료 기준**:
- ✅ 드래프트 생성 → 승인 → 게시 전체 플로우 E2E 테스트 통과
- ✅ LLM API 에러 처리 검증
- ✅ 성능 목표 달성
- ✅ Week 5 완료 보고서 작성

---

### 🛠 Week 6 (Day 36-42): 완전한 터미널 구현 (PTY)

#### Day 36-37: PTY 기반 터미널 설계
**목표**: Docker attach_socket() + PTY 아키텍처 설계

**기술 조사**:
- [ ] Docker SDK `attach_socket()` API 연구
  - stdin, stdout, stderr 스트림 처리
  - WebSocket과 연동 방법
  - 바이너리 모드 전환

- [ ] PTY (Pseudo-Terminal) 개념 학습
  - PTY master/slave 구조
  - 터미널 에뮬레이션 원리
  - ANSI 이스케이프 시퀀스

- [ ] xterm.js `onData` 이벤트 분석
  - 키 입력 이벤트 처리
  - 특수 키 코드 매핑
  - 바이너리 데이터 전송

- [ ] WebSocket 바이너리 모드 전환 방법
  - 텍스트 모드 vs 바이너리 모드
  - ArrayBuffer 처리
  - 성능 최적화

- [ ] 아키텍처 설계 문서 작성
  ```markdown
  # PTY 터미널 아키텍처

  ## 컴포넌트 구조
  - Frontend: xterm.js → WebSocket (바이너리)
  - Backend: WebSocket → Docker PTY → Container

  ## 데이터 흐름
  1. 키 입력 → onData 이벤트
  2. WebSocket 전송 (바이너리)
  3. Docker PTY write
  4. 프로세스 실행
  5. PTY read → WebSocket → xterm.js
  ```

**프로토타입 작업**:
- [ ] `app/services/terminal/pty_manager.py` 생성
  ```python
  class PTYManager:
      def __init__(self):
          self.sessions: Dict[str, PTYSession] = {}

      async def create_pty_session(
          self,
          container_id: str,
          cols: int = 80,
          rows: int = 24
      ) -> PTYSession:
          """PTY 세션 생성 및 Docker 컨테이너 연결"""

      async def stream_pty_io(
          self,
          session_id: str,
          websocket: WebSocket
      ):
          """stdin/stdout 양방향 스트리밍"""

      def handle_control_keys(self, data: bytes) -> bytes:
          """Ctrl+C, Ctrl+D 등 특수 키 처리"""

      async def resize_pty(
          self,
          session_id: str,
          cols: int,
          rows: int
      ):
          """터미널 크기 조정"""
  ```

- [ ] 단순 명령어 테스트
  - echo, ls, pwd 등 기본 명령어
  - 출력 스트리밍 확인
  - 입력 에코 확인

- [ ] 특수 키 테스트
  - Ctrl+C (SIGINT) - 명령어 중단
  - Ctrl+D (EOF) - 세션 종료
  - Ctrl+L - 화면 클리어
  - Tab - 자동완성

**완료 기준**:
- ✅ PTY 세션 생성 성공 (bash 프로세스 지속 실행)
- ✅ 실시간 문자 스트리밍 동작 (Enter 없이 키 입력마다 전송)
- ✅ Ctrl+C로 명령어 중단 가능
- ✅ 설계 문서 완성

#### Day 38-39: PTY 터미널 완전 구현
**목표**: vim/nano 등 인터랙티브 프로그램 지원

**백엔드 작업**:
- [ ] PTY 세션 상태 관리
  ```python
  class PTYSession:
      def __init__(self, container_id: str):
          self.container_id = container_id
          self.socket = None
          self.cols = 80
          self.rows = 24
          self.env = {}  # 환경 변수
          self.cwd = "/"  # 현재 디렉토리

      async def maintain_state(self):
          """cd, export 등 상태 유지"""
  ```

- [ ] ANSI 이스케이프 시퀀스 지원
  ```python
  class ANSIProcessor:
      def process_colors(self, data: bytes) -> bytes:
          """색상 코드 처리 (ls --color)"""

      def process_cursor(self, data: bytes) -> bytes:
          """커서 제어 (vim)"""

      def process_clear(self, data: bytes) -> bytes:
          """화면 지우기 (clear, Ctrl+L)"""
  ```

- [ ] WebSocket 바이너리 모드 전환
  ```python
  @websocket_route("/api/v1/terminal/pty/{session_id}")
  async def terminal_pty_websocket(websocket: WebSocket, session_id: str):
      await websocket.accept()

      # 바이너리 모드 설정
      await websocket.send_json({
          "type": "mode",
          "mode": "binary"
      })

      # 양방향 스트리밍
      async with PTYManager() as pty:
          await pty.stream_pty_io(session_id, websocket)
  ```

**프론트엔드 작업**:
- [ ] `useTerminalWebSocket.ts` 개선
  ```typescript
  // PTY 모드 지원
  const usePTYTerminal = (sessionId: string) => {
    const terminal = useRef<Terminal>();

    useEffect(() => {
      const ws = new WebSocket(
        `ws://localhost:8000/api/v1/terminal/pty/${sessionId}`
      );

      ws.binaryType = 'arraybuffer';

      // 키 입력 즉시 전송
      terminal.current.onData((data) => {
        const buffer = new TextEncoder().encode(data);
        ws.send(buffer);
      });

      // 서버 데이터 수신
      ws.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer) {
          const text = new TextDecoder().decode(event.data);
          terminal.current.write(text);
        }
      };
    }, [sessionId]);
  };
  ```

- [ ] xterm.js 설정 최적화
  ```typescript
  const terminalOptions: ITerminalOptions = {
    cursorBlink: true,
    cursorStyle: 'block',
    allowTransparency: true,
    fontSize: 14,
    fontFamily: 'JetBrains Mono, monospace',
    theme: {
      background: '#1e1e1e',
      foreground: '#d4d4d4',
      cursor: '#aeafad',
      // ANSI 색상 팔레트
      black: '#000000',
      red: '#cd3131',
      green: '#0dbc79',
      yellow: '#e5e510',
      blue: '#2472c8',
      magenta: '#bc3fbc',
      cyan: '#11a8cd',
      white: '#e5e5e5',
    },
    // 마우스 지원
    rightClickSelectsWord: true,
    // 스크롤백 버퍼
    scrollback: 10000,
  };
  ```

**인터랙티브 프로그램 테스트**:
- [ ] vim 테스트
  - 파일 열기/편집/저장
  - 모드 전환 (insert/normal)
  - 구문 강조
  - 검색/치환

- [ ] nano 테스트
  - 파일 편집
  - 단축키 동작
  - 하단 메뉴 표시

- [ ] less/more 테스트
  - 파일 페이징
  - 검색 기능
  - q로 종료

- [ ] top/htop 테스트
  - 실시간 업데이트
  - 정렬/필터
  - q로 종료

**완료 기준**:
- ✅ vim으로 파일 편집 가능
- ✅ nano로 파일 편집 가능
- ✅ less/more로 파일 읽기 가능
- ✅ top/htop 실시간 출력 스트리밍
- ✅ cd 명령어로 디렉토리 이동 유지
- ✅ ls --color 색상 출력 정상 표시

#### Day 40-41: 터미널 고급 기능
**목표**: 사용자 경험 개선 및 보안 강화

**고급 기능**:
- [ ] 명령어 히스토리 (화살표 키)
  ```python
  class CommandHistory:
      def __init__(self, max_size: int = 1000):
          self.history: List[str] = []
          self.position: int = 0

      def add_command(self, cmd: str):
          self.history.append(cmd)

      def get_previous(self) -> str:
          # 위 화살표 키 처리

      def get_next(self) -> str:
          # 아래 화살표 키 처리
  ```

- [ ] 탭 자동완성 (Bash completion)
  ```python
  class TabCompletion:
      async def complete_command(
          self,
          partial: str,
          context: str
      ) -> List[str]:
          """명령어/파일명 자동완성"""
  ```

- [ ] 터미널 크기 조정 (xterm.js FitAddon)
  ```typescript
  import { FitAddon } from 'xterm-addon-fit';

  const fitAddon = new FitAddon();
  terminal.loadAddon(fitAddon);

  // 창 크기 변경 시 자동 조정
  window.addEventListener('resize', () => {
    fitAddon.fit();
    const { cols, rows } = terminal;
    ws.send(JSON.stringify({
      type: 'resize',
      cols,
      rows
    }));
  });
  ```

- [ ] 세션 복구 (브라우저 새로고침 후 재연결)
  ```typescript
  // 세션 ID를 localStorage에 저장
  const saveSession = (sessionId: string) => {
    localStorage.setItem('terminal_session', sessionId);
  };

  const restoreSession = () => {
    const sessionId = localStorage.getItem('terminal_session');
    if (sessionId) {
      // 세션 재연결 시도
    }
  };
  ```

- [ ] 터미널 녹화 (asciinema 스타일) - 선택적
  ```python
  class TerminalRecorder:
      def start_recording(self, session_id: str):
          """녹화 시작"""

      def stop_recording(self) -> str:
          """녹화 중지 및 파일 반환"""

      def replay(self, recording_file: str):
          """녹화 재생"""
  ```

**보안 강화**:
- [ ] 블랙리스트 명령어 검증
  ```python
  DANGEROUS_COMMANDS = [
      r"rm\s+-rf\s+/",
      r":(){ :|:& };:",  # Fork bomb
      r"dd\s+if=/dev/zero",
      r"chmod\s+777\s+/",
      r"sudo\s+rm",
  ]

  def is_command_safe(command: str) -> bool:
      for pattern in DANGEROUS_COMMANDS:
          if re.search(pattern, command):
              return False
      return True
  ```

- [ ] 명령어 로깅
  ```python
  class CommandLogger:
      async def log_command(
          self,
          session_id: str,
          command: str,
          user_id: str
      ):
          """AnalyticsEvent로 명령어 기록"""
  ```

- [ ] 악성 명령어 패턴 감지
  ```python
  class MaliciousDetector:
      def detect_patterns(self, command: str) -> List[str]:
          """악성 패턴 감지 및 경고"""
  ```

- [ ] Rate Limiting
  ```python
  from slowapi import Limiter

  limiter = Limiter(key_func=get_remote_address)

  @limiter.limit("60/minute")
  async def execute_command():
      """분당 60개 명령어 제한"""
  ```

**완료 기준**:
- ✅ 화살표 키로 명령어 히스토리 탐색
- ✅ Tab 키로 파일명 자동완성
- ✅ rm -rf / 실행 시 차단 메시지
- ✅ 터미널 크기 조정 시 자동 재조정
- ✅ 세션 복구 기능 동작

#### Day 42: PTY 터미널 통합 테스트
**목표**: E2E 테스트 및 성능 검증

**테스트 시나리오**:
- [ ] Playwright E2E (15개)
  - [ ] PTY 세션 생성 테스트
  - [ ] vim 파일 편집 플로우
  - [ ] nano 파일 편집 플로우
  - [ ] cd 디렉토리 이동 유지
  - [ ] ls --color 색상 출력
  - [ ] top 실시간 스트리밍
  - [ ] Ctrl+C 명령어 중단
  - [ ] Ctrl+D 세션 종료
  - [ ] 화살표 키 히스토리
  - [ ] Tab 자동완성
  - [ ] 터미널 크기 조정
  - [ ] 위험 명령어 차단
  - [ ] 세션 복구
  - [ ] 동시 다중 세션
  - [ ] 긴 출력 스크롤

- [ ] 성능 측정
  ```python
  class PerformanceMetrics:
      async def measure_session_creation() -> float:
          """PTY 세션 생성 시간 (목표 < 2초)"""

      async def measure_keystroke_latency() -> float:
          """키 입력 지연 (목표 < 100ms)"""

      async def measure_concurrent_sessions() -> int:
          """동시 세션 지원 (목표 10개)"""
  ```

- [ ] 부하 테스트
  - 10개 동시 세션 생성
  - 1000줄 출력 스트리밍
  - 빠른 키 입력 (100 keys/sec)

**Week 6 완료 보고서**:
- [ ] PTY 구현 기술 상세
- [ ] 성능 측정 결과
- [ ] 보안 강화 내역
- [ ] 다음 주 준비 사항

**완료 기준**:
- ✅ 모든 E2E 테스트 통과 (15/15)
- ✅ 성능 목표 달성
  - PTY 세션 생성 < 2초
  - 키 입력 지연 < 100ms
  - 동시 세션 10개 지원
- ✅ Week 6 완료 보고서 작성

---

### 🔄 Week 7 (Day 43-49): 사용자 경험 개선

#### Day 43-44: 고급 검색 및 필터링
**목표**: 전체 텍스트 검색 (PostgreSQL FTS) + 고급 필터

**백엔드 작업**:
- [ ] PostgreSQL Full-Text Search 설정
  ```sql
  -- 한국어 지원 텍스트 검색 설정
  CREATE EXTENSION IF NOT EXISTS pg_trgm;

  -- 검색 인덱스 생성
  CREATE INDEX idx_tips_search ON tips
  USING gin(to_tsvector('simple', title || ' ' || content));

  -- 트라이그램 인덱스 (유사 검색)
  CREATE INDEX idx_tips_trigram ON tips
  USING gin(title gin_trgm_ops, content gin_trgm_ops);
  ```

- [ ] `GET /api/v1/tips/search` API 개선
  ```python
  @router.get("/api/v1/tips/search")
  async def search_tips(
      q: str = Query(None, description="검색어"),
      difficulty: List[str] = Query(None),
      category: List[str] = Query(None),
      date_from: date = Query(None),
      date_to: date = Query(None),
      sort_by: str = Query("relevance", enum=["relevance", "date", "views"]),
      page: int = Query(1, ge=1),
      size: int = Query(20, le=100)
  ):
      """고급 검색 API"""

      # Full-text search
      if q:
          query = select(Tip).where(
              func.to_tsvector('simple', Tip.title + ' ' + Tip.content)
              .match(func.plainto_tsquery('simple', q))
          )

      # 필터 적용
      if difficulty:
          query = query.where(Tip.difficulty.in_(difficulty))

      # 결과 하이라이팅
      tips = await db.execute(query)
      for tip in tips:
          tip.highlighted_title = highlight_matches(tip.title, q)
          tip.highlighted_content = highlight_matches(tip.content, q)

      return tips
  ```

- [ ] 검색 제안 API
  ```python
  @router.get("/api/v1/tips/search/suggestions")
  async def get_search_suggestions(
      q: str = Query(..., min_length=2)
  ):
      """자동완성 제안"""
      # 인기 검색어
      # 유사 단어
      # 최근 검색어
  ```

- [ ] TDD: 10개 검색 API 테스트
  - [ ] 키워드 검색 정확도
  - [ ] 한글/영문 혼합 검색
  - [ ] 필터 조합 테스트
  - [ ] 빈 결과 처리
  - [ ] 페이지네이션
  - [ ] 정렬 옵션
  - [ ] 특수문자 이스케이프
  - [ ] SQL 인젝션 방어
  - [ ] 성능 (< 500ms)
  - [ ] 동시 요청 처리

**프론트엔드 작업**:
- [ ] `components/search/` 컴포넌트 생성
  - [ ] `SearchBar.tsx` - 검색 입력 (자동완성)
    ```tsx
    interface SearchBarProps {
      onSearch: (query: string) => void
      suggestions?: string[]
    }

    const SearchBar = ({ onSearch, suggestions }: SearchBarProps) => {
      const [query, setQuery] = useState('');
      const [showSuggestions, setShowSuggestions] = useState(false);

      // Debounced search
      const debouncedSearch = useMemo(
        () => debounce(onSearch, 300),
        [onSearch]
      );

      return (
        <div className="relative">
          <Input
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              debouncedSearch(e.target.value);
            }}
            placeholder="검색어를 입력하세요..."
          />
          {showSuggestions && suggestions && (
            <SuggestionsList suggestions={suggestions} />
          )}
        </div>
      );
    };
    ```

  - [ ] `SearchFilters.tsx` - 고급 필터 (난이도, 카테고리, 날짜)
    ```tsx
    interface SearchFiltersProps {
      filters: SearchFilters
      onChange: (filters: SearchFilters) => void
    }

    const SearchFilters = ({ filters, onChange }: SearchFiltersProps) => {
      return (
        <div className="flex gap-4">
          <Select
            multiple
            value={filters.difficulty}
            onChange={(value) => onChange({ ...filters, difficulty: value })}
          >
            <option value="beginner">초급</option>
            <option value="intermediate">중급</option>
            <option value="advanced">고급</option>
          </Select>

          <Select
            multiple
            value={filters.category}
            onChange={(value) => onChange({ ...filters, category: value })}
          >
            {/* 카테고리 옵션들 */}
          </Select>

          <DateRangePicker
            value={[filters.dateFrom, filters.dateTo]}
            onChange={([from, to]) => onChange({ ...filters, dateFrom: from, dateTo: to })}
          />
        </div>
      );
    };
    ```

  - [ ] `SearchResults.tsx` - 검색 결과 (하이라이팅)
    ```tsx
    interface SearchResultsProps {
      results: TipData[]
      isLoading: boolean
      query: string
    }

    const SearchResults = ({ results, isLoading, query }: SearchResultsProps) => {
      if (isLoading) return <SearchSkeleton />;

      if (results.length === 0) {
        return <EmptyState message="검색 결과가 없습니다" />;
      }

      return (
        <div className="grid gap-4">
          {results.map((tip) => (
            <SearchResultCard
              key={tip.id}
              tip={tip}
              highlightedTitle={tip.highlighted_title}
              highlightedContent={tip.highlighted_content}
            />
          ))}
        </div>
      );
    };
    ```

- [ ] React Query hooks
  - [ ] `useSearch(query, filters)` - 검색 API 호출
  - [ ] `useSearchSuggestions(query)` - 자동완성 제안
  - [ ] `useSearchHistory()` - 최근 검색어

- [ ] URL 상태 관리
  ```typescript
  // URL query parameters 동기화
  const useSearchParams = () => {
    const router = useRouter();
    const searchParams = useSearchParams();

    const updateParams = (params: Record<string, any>) => {
      const newParams = new URLSearchParams(searchParams);
      Object.entries(params).forEach(([key, value]) => {
        if (value) newParams.set(key, value);
        else newParams.delete(key);
      });
      router.push(`?${newParams.toString()}`);
    };

    return { searchParams, updateParams };
  };
  ```

**완료 기준**:
- ✅ 키워드 검색 정상 동작 (PostgreSQL FTS)
- ✅ 고급 필터 (난이도 + 카테고리 + 날짜) 조합 검색
- ✅ 검색 결과 하이라이팅 표시
- ✅ 자동완성 제안 기능 (debounce 300ms)
- ✅ URL 상태 동기화 (뒤로가기 지원)

#### Day 45-46: 히스토리 페이지 (무한 스크롤)
**목표**: 전체 팁 목록 + 무한 스크롤

**프론트엔드 작업**:
- [ ] `app/history/page.tsx` - 히스토리 페이지
  ```tsx
  export default function HistoryPage() {
    const {
      data,
      fetchNextPage,
      hasNextPage,
      isFetchingNextPage,
      isLoading
    } = useInfiniteTips();

    return (
      <div className="container mx-auto py-8">
        <h1 className="text-3xl font-bold mb-8">모든 팁 히스토리</h1>

        <TipTimeline
          tips={data?.pages.flat() ?? []}
          onLoadMore={fetchNextPage}
          hasMore={hasNextPage}
          isLoading={isFetchingNextPage}
        />
      </div>
    );
  }
  ```

- [ ] `components/history/` 컴포넌트 생성
  - [ ] `TipTimeline.tsx` - 타임라인 UI (날짜별 그룹핑)
    ```tsx
    interface TipTimelineProps {
      tips: TipData[]
      onLoadMore: () => void
      hasMore: boolean
      isLoading: boolean
    }

    const TipTimeline = ({ tips, onLoadMore, hasMore, isLoading }: TipTimelineProps) => {
      // 날짜별로 그룹핑
      const groupedTips = useMemo(() => {
        return tips.reduce((groups, tip) => {
          const date = format(new Date(tip.published_date), 'yyyy-MM-dd');
          if (!groups[date]) groups[date] = [];
          groups[date].push(tip);
          return groups;
        }, {} as Record<string, TipData[]>);
      }, [tips]);

      return (
        <div className="relative">
          {/* 타임라인 선 */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200" />

          {Object.entries(groupedTips).map(([date, tips]) => (
            <TimelineSection key={date} date={date} tips={tips} />
          ))}

          <InfiniteScrollTrigger
            onTrigger={onLoadMore}
            hasMore={hasMore}
            isLoading={isLoading}
          />
        </div>
      );
    };
    ```

  - [ ] `InfiniteScroll.tsx` - 무한 스크롤 컴포넌트
    ```tsx
    const InfiniteScrollTrigger = ({ onTrigger, hasMore, isLoading }) => {
      const observerTarget = useRef(null);

      useEffect(() => {
        const observer = new IntersectionObserver(
          (entries) => {
            if (entries[0].isIntersecting && hasMore && !isLoading) {
              onTrigger();
            }
          },
          { threshold: 0.1 }
        );

        if (observerTarget.current) {
          observer.observe(observerTarget.current);
        }

        return () => observer.disconnect();
      }, [onTrigger, hasMore, isLoading]);

      return (
        <div ref={observerTarget}>
          {isLoading && <LoadingSpinner />}
          {!hasMore && <EndMessage />}
        </div>
      );
    };
    ```

  - [ ] `TimelineSection.tsx` - 날짜별 섹션
  - [ ] `TipCard.tsx` (재사용) - 개별 팁 카드

- [ ] React Query Infinite Query
  ```typescript
  const useInfiniteTips = (filters?: TipFilters) => {
    return useInfiniteQuery({
      queryKey: ['tips', 'infinite', filters],
      queryFn: ({ pageParam = 1 }) =>
        fetchTips({ ...filters, page: pageParam, size: 20 }),
      getNextPageParam: (lastPage, pages) => {
        if (lastPage.length < 20) return undefined;
        return pages.length + 1;
      },
      staleTime: 5 * 60 * 1000, // 5분
      cacheTime: 10 * 60 * 1000, // 10분
    });
  };
  ```

**UX 개선**:
- [ ] 스켈레톤 로딩 (초기 로딩)
  ```tsx
  const TipSkeleton = () => (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
      <div className="h-4 bg-gray-200 rounded w-1/2" />
    </div>
  );
  ```

- [ ] 로딩 인디케이터 (스크롤 끝)
- [ ] 빈 상태 UI ("No tips found")
- [ ] 에러 상태 UI (재시도 버튼)
- [ ] 스크롤 위치 저장 (뒤로가기 시 복원)

**성능 최적화 (선택)**:
- [ ] 가상 스크롤링 (react-window)
  ```tsx
  import { VariableSizeList } from 'react-window';

  const VirtualizedTipList = ({ tips }) => {
    return (
      <VariableSizeList
        height={window.innerHeight}
        itemCount={tips.length}
        itemSize={(index) => getItemHeight(tips[index])}
        width="100%"
      >
        {({ index, style }) => (
          <div style={style}>
            <TipCard tip={tips[index]} />
          </div>
        )}
      </VariableSizeList>
    );
  };
  ```

**완료 기준**:
- ✅ 히스토리 페이지 무한 스크롤 동작
- ✅ 페이지네이션 없이 연속 스크롤
- ✅ 날짜별 그룹핑 표시
- ✅ 로딩/에러 상태 처리
- ✅ 성능 최적화 (100개 이상 팁 부드럽게 스크롤)

#### Day 47-48: 반응형 디자인 최적화
**목표**: 모바일/태블릿 최적화

**디자인 작업**:
- [ ] 브레이크포인트 정리
  ```css
  /* tailwind.config.js */
  module.exports = {
    theme: {
      screens: {
        'xs': '475px',     // 소형 모바일
        'sm': '640px',     // 모바일
        'md': '768px',     // 태블릿
        'lg': '1024px',    // 노트북
        'xl': '1280px',    // 데스크탑
        '2xl': '1536px',   // 대형 화면
      }
    }
  }
  ```

- [ ] 모바일 네비게이션 (Hamburger Menu)
  ```tsx
  const MobileNav = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
      <>
        <button
          className="lg:hidden"
          onClick={() => setIsOpen(!isOpen)}
        >
          <MenuIcon />
        </button>

        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetContent side="left">
            <nav className="flex flex-col gap-4">
              {/* 네비게이션 항목들 */}
            </nav>
          </SheetContent>
        </Sheet>
      </>
    );
  };
  ```

- [ ] 터미널 모바일 UI
  ```tsx
  const MobileTerminal = () => {
    const [showKeyboard, setShowKeyboard] = useState(false);

    return (
      <div className="relative h-full">
        <Terminal className="h-[calc(100%-60px)]" />

        {/* 가상 키보드 토글 */}
        <button
          className="absolute bottom-4 right-4"
          onClick={() => setShowKeyboard(!showKeyboard)}
        >
          <KeyboardIcon />
        </button>

        {showKeyboard && (
          <VirtualKeyboard
            onKey={(key) => terminal.write(key)}
          />
        )}
      </div>
    );
  };
  ```

- [ ] 카드 레이아웃 조정
  ```tsx
  const ResponsiveGrid = ({ children }) => (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {children}
    </div>
  );
  ```

**컴포넌트 개선**:
- [ ] `Header.tsx` - 모바일 메뉴
- [ ] `TerminalEmulator.tsx` - 터치 입력 지원
- [ ] `TipCard.tsx` - 모바일 최적화
- [ ] `SearchBar.tsx` - 모바일 크기 조정
- [ ] `AdminDashboard.tsx` - 태블릿 레이아웃

**터치 제스처 지원**:
- [ ] 스와이프 네비게이션
  ```tsx
  import { useSwipeable } from 'react-swipeable';

  const SwipeableCard = ({ onSwipeLeft, onSwipeRight }) => {
    const handlers = useSwipeable({
      onSwipedLeft: onSwipeLeft,
      onSwipedRight: onSwipeRight,
      preventDefaultTouchmoveEvent: true,
      trackMouse: true
    });

    return <div {...handlers}>...</div>;
  };
  ```

- [ ] 핀치 줌 (터미널)
- [ ] 길게 누르기 (컨텍스트 메뉴)
- [ ] 당겨서 새로고침

**테스트**:
- [ ] Chrome DevTools 기기 에뮬레이션
  - iPhone 12/13/14
  - iPad Air/Pro
  - Samsung Galaxy S21
  - Pixel 6

- [ ] 실제 기기 테스트
  - iOS Safari
  - Android Chrome
  - 가로/세로 모드 전환

- [ ] Lighthouse 모바일 점수
  - Performance: 90+
  - Accessibility: 100
  - Best Practices: 100
  - SEO: 100

**완료 기준**:
- ✅ 모바일 기기에서 모든 기능 정상 동작
- ✅ 터치 제스처 지원
- ✅ 가로/세로 모드 전환 시 레이아웃 유지
- ✅ Lighthouse 모바일 점수 90+ 달성
- ✅ 320px ~ 2560px 모든 해상도 지원

#### Day 49: 접근성 개선 (WCAG 2.1)
**목표**: WCAG 2.1 AA 수준 완전 준수

**접근성 체크리스트**:
- [ ] 키보드 네비게이션
  ```tsx
  // 모든 인터랙티브 요소에 tabIndex 설정
  const Button = ({ children, ...props }) => (
    <button
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          props.onClick?.(e);
        }
      }}
      {...props}
    >
      {children}
    </button>
  );
  ```

- [ ] 포커스 인디케이터
  ```css
  /* 명확한 포커스 스타일 */
  :focus-visible {
    outline: 2px solid #4F46E5;
    outline-offset: 2px;
  }
  ```

- [ ] ARIA 속성
  ```tsx
  // 적절한 ARIA 레이블 추가
  <nav aria-label="주 네비게이션">
    <ul role="list">
      <li role="listitem">
        <a href="/tips" aria-current={isActive ? 'page' : undefined}>
          팁 목록
        </a>
      </li>
    </ul>
  </nav>

  // 모달 접근성
  <Dialog
    role="dialog"
    aria-labelledby="dialog-title"
    aria-describedby="dialog-description"
    aria-modal="true"
  >
    <h2 id="dialog-title">제목</h2>
    <p id="dialog-description">설명</p>
  </Dialog>
  ```

- [ ] 색상 대비 검증
  ```typescript
  // 최소 4.5:1 (일반 텍스트)
  // 최소 3:1 (큰 텍스트)
  const checkContrast = (fg: string, bg: string): number => {
    // WCAG contrast ratio 계산
  };
  ```

- [ ] 스크린 리더 테스트
  - NVDA (Windows)
  - JAWS (Windows)
  - VoiceOver (macOS/iOS)
  - TalkBack (Android)

- [ ] 폼 레이블
  ```tsx
  <div className="form-group">
    <label htmlFor="email" className="sr-only">
      이메일 주소
    </label>
    <input
      id="email"
      type="email"
      aria-required="true"
      aria-invalid={errors.email ? 'true' : 'false'}
      aria-describedby={errors.email ? 'email-error' : undefined}
    />
    {errors.email && (
      <span id="email-error" role="alert">
        {errors.email}
      </span>
    )}
  </div>
  ```

- [ ] 에러 메시지
  ```tsx
  // Live region으로 에러 알림
  <div aria-live="polite" aria-atomic="true">
    {error && <Alert role="alert">{error}</Alert>}
  </div>
  ```

- [ ] 건너뛰기 링크
  ```tsx
  // 페이지 상단에 건너뛰기 링크 추가
  <a href="#main-content" className="sr-only focus:not-sr-only">
    주요 콘텐츠로 건너뛰기
  </a>
  ```

**도구 활용**:
- [ ] axe DevTools 자동 감사
  ```bash
  npm install -D @axe-core/playwright
  ```

  ```typescript
  // Playwright 접근성 테스트
  import { injectAxe, checkA11y } from '@axe-core/playwright';

  test('접근성 검사', async ({ page }) => {
    await page.goto('/');
    await injectAxe(page);
    await checkA11y(page);
  });
  ```

- [ ] Lighthouse 접근성 점수
- [ ] Wave (WebAIM) 검사
- [ ] 수동 키보드 네비게이션 테스트

**Week 7 완료 보고서**:
- [ ] 사용자 경험 개선 내역
- [ ] 접근성 준수 수준
- [ ] 반응형 디자인 결과
- [ ] 다음 주 준비 사항

**완료 기준**:
- ✅ axe DevTools 에러 0건
- ✅ Lighthouse 접근성 점수 100
- ✅ 키보드만으로 모든 기능 사용 가능
- ✅ 스크린 리더 완전 지원
- ✅ WCAG 2.1 AA 준수 인증 가능
- ✅ Week 7 완료 보고서 작성

---

### 🚀 Week 8 (Day 50-56): 관리자 대시보드 완성 및 최적화

#### Day 50-51: 실시간 대시보드 (통계)
**목표**: 관리자 대시보드 - 실시간 통계 및 모니터링

**백엔드 작업**:
- [ ] `GET /api/v1/admin/stats` API 확장
  ```python
  @router.get("/api/v1/admin/stats")
  async def get_admin_stats(
      period: str = Query("day", enum=["day", "week", "month"]),
      db: AsyncSession = Depends(get_db)
  ):
      """관리자 통계 API"""

      stats = {
          "visitors": await get_visitor_stats(db, period),
          "tips": await get_tip_stats(db, period),
          "terminal": await get_terminal_stats(db, period),
          "drafts": await get_draft_stats(db, period),
      }

      return stats

  async def get_visitor_stats(db: AsyncSession, period: str):
      """방문자 통계"""
      return {
          "total": await count_visitors(db, period),
          "unique": await count_unique_visitors(db, period),
          "pageviews": await count_pageviews(db, period),
          "bounce_rate": await calculate_bounce_rate(db, period),
          "avg_session_duration": await avg_session_duration(db, period),
      }

  async def get_tip_stats(db: AsyncSession, period: str):
      """팁 통계"""
      return {
          "total_tips": await count_tips(db),
          "published_today": await count_published_today(db),
          "most_viewed": await get_most_viewed_tips(db, limit=10),
          "most_liked": await get_most_liked_tips(db, limit=10),
          "by_category": await count_tips_by_category(db),
          "by_difficulty": await count_tips_by_difficulty(db),
      }

  async def get_terminal_stats(db: AsyncSession, period: str):
      """터미널 사용 통계"""
      return {
          "sessions_created": await count_terminal_sessions(db, period),
          "commands_executed": await count_commands(db, period),
          "avg_session_length": await avg_terminal_session_length(db, period),
          "popular_commands": await get_popular_commands(db, limit=20),
      }

  async def get_draft_stats(db: AsyncSession, period: str):
      """드래프트 통계"""
      return {
          "total_drafts": await count_drafts(db),
          "pending_approval": await count_pending_drafts(db),
          "approval_rate": await calculate_approval_rate(db, period),
          "avg_generation_time": await avg_llm_generation_time(db),
      }
  ```

- [ ] Redis 캐싱 전략
  ```python
  from app.core.cache import cache

  @cache(expire=300)  # 5분 TTL
  async def get_cached_stats(period: str):
      """캐시된 통계 데이터"""
      return await get_admin_stats(period)
  ```

**프론트엔드 작업**:
- [ ] `app/admin/dashboard/page.tsx` - 대시보드 페이지
  ```tsx
  export default function AdminDashboard() {
    const { data: stats, isLoading } = useAdminStats();

    if (isLoading) return <DashboardSkeleton />;

    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">관리자 대시보드</h1>

        {/* 핵심 지표 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard
            title="오늘 방문자"
            value={stats.visitors.total}
            change={stats.visitors.change}
            icon={<UsersIcon />}
          />
          <MetricCard
            title="터미널 세션"
            value={stats.terminal.sessions_created}
            change={stats.terminal.change}
            icon={<TerminalIcon />}
          />
          <MetricCard
            title="승인 대기"
            value={stats.drafts.pending_approval}
            icon={<ClockIcon />}
          />
          <MetricCard
            title="승인율"
            value={`${stats.drafts.approval_rate}%`}
            icon={<CheckIcon />}
          />
        </div>

        {/* 차트 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <VisitorChart data={stats.visitors.timeline} />
          <CategoryDistribution data={stats.tips.by_category} />
        </div>

        {/* 테이블 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TopTipsTable tips={stats.tips.most_viewed} />
          <PopularCommandsTable commands={stats.terminal.popular_commands} />
        </div>
      </div>
    );
  }
  ```

- [ ] `components/admin/stats/` 컴포넌트 생성
  - [ ] `MetricCard.tsx` - 지표 카드
    ```tsx
    interface MetricCardProps {
      title: string
      value: string | number
      change?: number
      icon: ReactNode
    }

    const MetricCard = ({ title, value, change, icon }: MetricCardProps) => (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{title}</p>
              <p className="text-2xl font-bold">{value}</p>
              {change !== undefined && (
                <p className={`text-sm ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {change > 0 ? '↑' : '↓'} {Math.abs(change)}%
                </p>
              )}
            </div>
            <div className="text-gray-400">{icon}</div>
          </div>
        </CardContent>
      </Card>
    );
    ```

  - [ ] `VisitorChart.tsx` - 방문자 차트 (recharts)
    ```tsx
    import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

    const VisitorChart = ({ data }) => (
      <Card>
        <CardHeader>
          <CardTitle>방문자 추이</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="visitors" stroke="#8884d8" />
              <Line type="monotone" dataKey="unique" stroke="#82ca9d" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
    ```

  - [ ] `CategoryDistribution.tsx` - 카테고리 분포 (파이 차트)
  - [ ] `TopTipsTable.tsx` - 인기 팁 테이블
  - [ ] `PopularCommandsTable.tsx` - 인기 명령어 테이블
  - [ ] `DraftApprovalRate.tsx` - 드래프트 승인율

- [ ] React Query 설정
  ```typescript
  const useAdminStats = (period: 'day' | 'week' | 'month' = 'day') => {
    return useQuery({
      queryKey: ['admin', 'stats', period],
      queryFn: () => fetchAdminStats(period),
      refetchInterval: 5 * 60 * 1000, // 5분마다 새로고침
      staleTime: 4 * 60 * 1000, // 4분 후 stale
    });
  };
  ```

**완료 기준**:
- ✅ 실시간 통계 대시보드 렌더링
- ✅ 차트 및 테이블 정상 표시
- ✅ 5분마다 자동 새로고침
- ✅ 반응형 레이아웃
- ✅ 로딩/에러 상태 처리

#### Day 52-53: 시스템 모니터링 도구
**목표**: 관리자 대시보드 - 시스템 상태 모니터링

**백엔드 작업**:
- [ ] `GET /api/v1/admin/system/health` API 생성
  ```python
  import psutil
  import docker
  from sqlalchemy import text

  @router.get("/api/v1/admin/system/health")
  async def get_system_health(
      db: AsyncSession = Depends(get_db),
      redis: Redis = Depends(get_redis)
  ):
      """시스템 헬스 체크"""

      health = {
          "status": "healthy",
          "checks": {}
      }

      # PostgreSQL 체크
      try:
          await db.execute(text("SELECT 1"))
          health["checks"]["postgresql"] = {"status": "up", "latency": 0.001}
      except Exception as e:
          health["checks"]["postgresql"] = {"status": "down", "error": str(e)}
          health["status"] = "degraded"

      # Redis 체크
      try:
          await redis.ping()
          health["checks"]["redis"] = {"status": "up", "latency": 0.001}
      except Exception as e:
          health["checks"]["redis"] = {"status": "down", "error": str(e)}
          health["status"] = "degraded"

      # Docker 체크
      try:
          client = docker.from_env()
          containers = client.containers.list()
          health["checks"]["docker"] = {
          "status": "up",
          "containers": {
              "total": len(containers),
              "running": len([c for c in containers if c.status == "running"])
          }
      }
      except Exception as e:
          health["checks"]["docker"] = {"status": "down", "error": str(e)}

      # 시스템 리소스
      health["resources"] = {
          "cpu": {
              "percent": psutil.cpu_percent(interval=1),
              "cores": psutil.cpu_count()
          },
          "memory": {
              "total": psutil.virtual_memory().total,
              "used": psutil.virtual_memory().used,
              "percent": psutil.virtual_memory().percent
          },
          "disk": {
              "total": psutil.disk_usage('/').total,
              "used": psutil.disk_usage('/').used,
              "percent": psutil.disk_usage('/').percent
          }
      }

      return health
  ```

- [ ] `GET /api/v1/admin/system/logs` API 생성
  ```python
  @router.get("/api/v1/admin/system/logs")
  async def get_system_logs(
      level: str = Query("all", enum=["all", "error", "warning", "info"]),
      limit: int = Query(100, le=1000),
      offset: int = Query(0),
      db: AsyncSession = Depends(get_db)
  ):
      """시스템 로그 조회"""

      query = select(SystemLog).order_by(SystemLog.created_at.desc())

      if level != "all":
          query = query.where(SystemLog.level == level)

      query = query.offset(offset).limit(limit)
      logs = await db.execute(query)

      return {
          "logs": logs.scalars().all(),
          "total": await db.scalar(select(func.count(SystemLog.id)))
      }
  ```

- [ ] 로그 수집 미들웨어
  ```python
  @app.middleware("http")
  async def log_requests(request: Request, call_next):
      start_time = time.time()

      try:
          response = await call_next(request)
          process_time = time.time() - start_time

          # 로그 저장
          await save_request_log(
              path=request.url.path,
              method=request.method,
              status_code=response.status_code,
              process_time=process_time
          )

          return response
      except Exception as e:
          # 에러 로그 저장
          await save_error_log(
              path=request.url.path,
              error=str(e),
              traceback=traceback.format_exc()
          )
          raise
  ```

**프론트엔드 작업**:
- [ ] `app/admin/system/page.tsx` - 시스템 페이지
  ```tsx
  export default function SystemMonitoring() {
    const { data: health, isLoading: healthLoading } = useSystemHealth();
    const { data: logs, isLoading: logsLoading } = useSystemLogs();

    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">시스템 모니터링</h1>

        {/* 헬스 체크 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <SystemHealthCard
            title="PostgreSQL"
            status={health?.checks.postgresql.status}
            latency={health?.checks.postgresql.latency}
          />
          <SystemHealthCard
            title="Redis"
            status={health?.checks.redis.status}
            latency={health?.checks.redis.latency}
          />
          <SystemHealthCard
            title="Docker"
            status={health?.checks.docker.status}
            containers={health?.checks.docker.containers}
          />
        </div>

        {/* 리소스 사용량 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <ResourceGauge
            title="CPU"
            value={health?.resources.cpu.percent}
            max={100}
            unit="%"
          />
          <ResourceGauge
            title="메모리"
            value={health?.resources.memory.percent}
            max={100}
            unit="%"
          />
          <ResourceGauge
            title="디스크"
            value={health?.resources.disk.percent}
            max={100}
            unit="%"
          />
        </div>

        {/* 로그 뷰어 */}
        <Card>
          <CardHeader>
            <CardTitle>시스템 로그</CardTitle>
          </CardHeader>
          <CardContent>
            <LogViewer logs={logs?.logs} />
          </CardContent>
        </Card>
      </div>
    );
  }
  ```

- [ ] `components/admin/system/` 컴포넌트 생성
  - [ ] `SystemHealthCard.tsx` - 시스템 상태 카드
    ```tsx
    const SystemHealthCard = ({ title, status, latency, containers }) => {
      const statusColor = {
        up: 'text-green-600',
        degraded: 'text-yellow-600',
        down: 'text-red-600'
      };

      return (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">{title}</h3>
              <span className={`${statusColor[status]} font-bold`}>
                {status.toUpperCase()}
              </span>
            </div>
            {latency && (
              <p className="text-sm text-gray-600">Latency: {latency}ms</p>
            )}
            {containers && (
              <p className="text-sm text-gray-600">
                Containers: {containers.running}/{containers.total}
              </p>
            )}
          </CardContent>
        </Card>
      );
    };
    ```

  - [ ] `LogViewer.tsx` - 로그 뷰어 (virtual scroll)
    ```tsx
    import { FixedSizeList } from 'react-window';

    const LogViewer = ({ logs }) => {
      const Row = ({ index, style }) => {
        const log = logs[index];
        const levelColor = {
          error: 'text-red-600',
          warning: 'text-yellow-600',
          info: 'text-blue-600'
        };

        return (
          <div style={style} className="flex items-center gap-4 p-2 border-b">
            <span className="text-xs text-gray-500">
              {format(new Date(log.created_at), 'HH:mm:ss')}
            </span>
            <span className={`text-xs ${levelColor[log.level]}`}>
              {log.level.toUpperCase()}
            </span>
            <span className="text-sm flex-1">{log.message}</span>
          </div>
        );
      };

      return (
        <FixedSizeList
          height={400}
          itemCount={logs.length}
          itemSize={40}
          width="100%"
        >
          {Row}
        </FixedSizeList>
      );
    };
    ```

  - [ ] `ResourceGauge.tsx` - 리소스 게이지
  - [ ] `ContainerList.tsx` - 활성 컨테이너 목록

- [ ] React Query hooks
  ```typescript
  const useSystemHealth = () => {
    return useQuery({
      queryKey: ['admin', 'system', 'health'],
      queryFn: fetchSystemHealth,
      refetchInterval: 10 * 1000, // 10초마다
      staleTime: 9 * 1000,
    });
  };

  const useSystemLogs = (filter?: LogFilter) => {
    return useQuery({
      queryKey: ['admin', 'system', 'logs', filter],
      queryFn: () => fetchSystemLogs(filter),
      refetchInterval: 30 * 1000, // 30초마다
    });
  };
  ```

**완료 기준**:
- ✅ 시스템 상태 모니터링 페이지 렌더링
- ✅ 실시간 헬스 체크 (10초마다)
- ✅ 로그 뷰어 정상 동작 (가상 스크롤)
- ✅ 리소스 사용량 시각화
- ✅ 컨테이너 상태 표시

#### Day 54: 성능 최적화
**목표**: Lighthouse 90+ 달성

**최적화 작업**:
- [ ] 동적 import (Code Splitting)
  ```typescript
  // 터미널 컴포넌트 동적 로딩
  const TerminalEmulator = dynamic(
    () => import('@/components/TerminalEmulator'),
    {
      loading: () => <TerminalSkeleton />,
      ssr: false
    }
  );

  // 차트 라이브러리 동적 로딩
  const VisitorChart = dynamic(
    () => import('@/components/admin/stats/VisitorChart'),
    {
      loading: () => <ChartSkeleton />,
      ssr: false
    }
  );

  // Markdown 렌더러 동적 로딩
  const MarkdownRenderer = dynamic(
    () => import('@/components/MarkdownRenderer'),
    {
      loading: () => <div>Loading...</div>
    }
  );
  ```

- [ ] 이미지 최적화
  ```tsx
  import Image from 'next/image';

  // WebP 포맷 사용
  <Image
    src="/hero.jpg"
    alt="Hero"
    width={1920}
    height={1080}
    placeholder="blur"
    blurDataURL={blurDataUrl}
    priority
    formats={['webp']}
  />
  ```

- [ ] 메모이제이션
  ```typescript
  // React.memo로 재렌더링 방지
  const TipCard = React.memo(({ tip }: { tip: TipData }) => {
    // ...
  }, (prevProps, nextProps) => {
    return prevProps.tip.id === nextProps.tip.id;
  });

  // useMemo로 비싼 계산 캐싱
  const processedData = useMemo(() => {
    return heavyDataProcessing(rawData);
  }, [rawData]);

  // useCallback으로 함수 재생성 방지
  const handleSearch = useCallback((query: string) => {
    searchTips(query);
  }, [searchTips]);
  ```

- [ ] 번들 분석 및 최적화
  ```bash
  # 번들 분석기 실행
  npm run build
  npm run analyze
  ```

  ```javascript
  // next.config.js
  module.exports = {
    webpack: (config, { isServer }) => {
      if (!isServer) {
        // Tree shaking 최적화
        config.optimization.usedExports = true;
        config.optimization.sideEffects = false;
      }
      return config;
    },
  };
  ```

- [ ] 캐싱 전략
  ```typescript
  // React Query 캐싱 최적화
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5분
        cacheTime: 10 * 60 * 1000, // 10분
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  });

  // Next.js 정적 생성
  export async function getStaticProps() {
    const tips = await fetchTips();
    return {
      props: { tips },
      revalidate: 3600, // 1시간마다 재생성
    };
  }
  ```

- [ ] Service Worker (PWA) - 선택적
  ```javascript
  // public/service-worker.js
  self.addEventListener('install', (event) => {
    event.waitUntil(
      caches.open('v1').then((cache) => {
        return cache.addAll([
          '/',
          '/offline.html',
          '/static/css/main.css',
          '/static/js/main.js',
        ]);
      })
    );
  });

  self.addEventListener('fetch', (event) => {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  });
  ```

**성능 측정**:
- [ ] Lighthouse 점수
  ```typescript
  // Playwright로 Lighthouse 자동화
  import { playtest } from '@playwright/test';
  import { startFlow } from 'lighthouse/lighthouse-core/fraggle-rock/api.js';

  test('Lighthouse 성능 측정', async ({ page, browser }) => {
    const flow = await startFlow(page, { name: 'Linux Daily Tips' });

    await flow.navigate('/');
    await flow.snapshot({ stepName: 'Homepage' });

    await flow.navigate('/tips');
    await flow.snapshot({ stepName: 'Tips Page' });

    const report = await flow.generateReport();
    console.log(report);
  });
  ```

- [ ] Core Web Vitals
  ```typescript
  // web-vitals 라이브러리 사용
  import { getCLS, getFID, getLCP } from 'web-vitals';

  getCLS(console.log); // Cumulative Layout Shift
  getFID(console.log); // First Input Delay
  getLCP(console.log); // Largest Contentful Paint
  ```

**완료 기준**:
- ✅ Lighthouse 데스크탑 95+
- ✅ Lighthouse 모바일 90+
- ✅ Core Web Vitals 모두 "Good" 범위
  - LCP < 2.5초
  - FID < 100ms
  - CLS < 0.1
- ✅ 번들 사이즈 < 500KB (gzipped)
- ✅ 초기 로딩 시간 < 3초

#### Day 55: 통합 테스트 및 버그 수정
**목표**: Phase 2 전체 기능 E2E 테스트

**E2E 테스트 시나리오 (30개)**:

- [ ] LLM 드래프트 생성 플로우 (5개)
  ```typescript
  test.describe('LLM 드래프트 생성', () => {
    test('드래프트 생성 버튼 클릭', async ({ page }) => {});
    test('LLM 생성 진행 상태 표시', async ({ page }) => {});
    test('7개 팁 생성 완료', async ({ page }) => {});
    test('생성 실패 시 에러 처리', async ({ page }) => {});
    test('재시도 기능', async ({ page }) => {});
  });
  ```

- [ ] 드래프트 승인/거절 플로우 (5개)
  ```typescript
  test.describe('드래프트 승인 워크플로우', () => {
    test('드래프트 목록 조회', async ({ page }) => {});
    test('개별 팁 편집', async ({ page }) => {});
    test('드래프트 승인', async ({ page }) => {});
    test('드래프트 거절', async ({ page }) => {});
    test('승인된 팁 자동 게시 확인', async ({ page }) => {});
  });
  ```

- [ ] PTY 터미널 인터랙티브 (10개)
  ```typescript
  test.describe('PTY 터미널', () => {
    test('PTY 세션 생성', async ({ page }) => {});
    test('vim 파일 편집', async ({ page }) => {});
    test('nano 파일 편집', async ({ page }) => {});
    test('cd 명령어 상태 유지', async ({ page }) => {});
    test('ls --color 색상 출력', async ({ page }) => {});
    test('top 실시간 업데이트', async ({ page }) => {});
    test('Ctrl+C 명령어 중단', async ({ page }) => {});
    test('Tab 자동완성', async ({ page }) => {});
    test('화살표 키 히스토리', async ({ page }) => {});
    test('위험 명령어 차단', async ({ page }) => {});
  });
  ```

- [ ] 고급 검색 및 필터링 (5개)
  ```typescript
  test.describe('고급 검색', () => {
    test('키워드 검색', async ({ page }) => {});
    test('난이도 필터', async ({ page }) => {});
    test('카테고리 필터', async ({ page }) => {});
    test('날짜 범위 필터', async ({ page }) => {});
    test('검색 결과 하이라이팅', async ({ page }) => {});
  });
  ```

- [ ] 히스토리 무한 스크롤 (5개)
  ```typescript
  test.describe('히스토리 페이지', () => {
    test('초기 로딩', async ({ page }) => {});
    test('스크롤 시 추가 로딩', async ({ page }) => {});
    test('날짜별 그룹핑', async ({ page }) => {});
    test('끝까지 스크롤', async ({ page }) => {});
    test('에러 상태 처리', async ({ page }) => {});
  });
  ```

**버그 수정 우선순위**:
- [ ] P1 (크리티컬) - 즉시 수정
  - 데이터 손실
  - 보안 취약점
  - 서비스 중단

- [ ] P2 (중요) - 당일 수정
  - 주요 기능 오류
  - UI 깨짐
  - 성능 저하

- [ ] P3 (보통) - 다음 스프린트
  - 사소한 UI 이슈
  - 개선 사항
  - 문서 오류

**버그 추적**:
```typescript
interface BugReport {
  id: string;
  priority: 'P1' | 'P2' | 'P3';
  title: string;
  description: string;
  steps: string[];
  expected: string;
  actual: string;
  status: 'open' | 'in-progress' | 'resolved' | 'closed';
  assignee?: string;
  resolution?: string;
}
```

**완료 기준**:
- ✅ E2E 테스트 100% 통과 (30/30)
- ✅ P1 버그 0건
- ✅ P2 버그 해결 또는 문서화
- ✅ 회귀 테스트 통과
- ✅ 성능 목표 유지

#### Day 56: 문서화 및 Phase 2 완료
**목표**: Phase 2 문서 완성 및 회고

**문서 작성**:
- [ ] Phase 2 완료 보고서
  ```markdown
  # Phase 2 완료 보고서

  ## 개요
  - 기간: 2025-11-07 ~ 2025-12-04
  - 참여: 개발자 1명
  - 총 작업: XX개 완료

  ## 주요 성과

  ### LLM 통합
  - OpenAI GPT-4 API 연동 완료
  - 7개 팁 병렬 생성 (평균 8.5초)
  - 드래프트 승인율 92%

  ### PTY 터미널
  - Docker attach_socket() 구현
  - vim/nano 완전 지원
  - 명령어 히스토리 및 자동완성

  ### 관리자 대시보드
  - 실시간 통계 (5분 갱신)
  - 시스템 모니터링
  - 드래프트 관리 UI

  ### 사용자 경험
  - PostgreSQL FTS 검색
  - 무한 스크롤 히스토리
  - 반응형 디자인 (320px ~ 2560px)
  - WCAG 2.1 AA 준수

  ## 성능 지표
  - Lighthouse 데스크탑: 96
  - Lighthouse 모바일: 91
  - LCP: 2.1초
  - FID: 85ms
  - CLS: 0.08

  ## 기술 부채
  - [ ] WebSocket 재연결 로직 개선 필요
  - [ ] LLM 프롬프트 최적화 필요
  - [ ] 터미널 세션 복구 안정성

  ## 다음 단계 (Phase 3)
  - Google AdSense 통합
  - SEO 최적화
  - 프로덕션 배포
  ```

- [ ] API 문서 업데이트
  ```python
  # FastAPI 자동 문서 생성
  app = FastAPI(
      title="Linux Daily Tips API",
      description="Phase 2 - LLM 통합 및 관리자 기능",
      version="2.0.0",
      docs_url="/api/docs",
      redoc_url="/api/redoc"
  )
  ```

- [ ] 개발자 가이드 업데이트
  ```markdown
  # 개발자 가이드 - Phase 2

  ## 새로운 기능

  ### LLM 통합
  - 환경 변수 설정
  - API 키 관리
  - 프롬프트 커스터마이징

  ### PTY 터미널
  - WebSocket 바이너리 모드
  - Docker 컨테이너 연결
  - 보안 설정

  ### 관리자 기능
  - JWT 인증
  - 권한 관리
  - 대시보드 커스터마이징
  ```

- [ ] README.md 업데이트
  ```markdown
  ## 🚀 프로젝트 진행 상황

  ### ✅ Phase 1 (MVP): 100% 완료
  - 기간: 2025-10-01 ~ 2025-11-06
  - 주요 기능: 기본 UI, 팁 표시, 터미널 에뮬레이터

  ### ✅ Phase 2 (고급 기능): 100% 완료 🎉
  - 기간: 2025-11-07 ~ 2025-12-04
  - 주요 기능: LLM 통합, PTY 터미널, 관리자 대시보드
  - 성과: Lighthouse 90+, WCAG 2.1 AA 준수

  ### 🔜 Phase 3 (수익화 및 배포): 예정
  - 예정: 2025-12-05 ~ 2025-12-31
  - 목표: AdSense 통합, SEO, 프로덕션 배포
  ```

**회고 (Retrospective)**:
- [ ] 무엇이 잘 되었나?
  - LLM 통합 성공
  - PTY 터미널 안정성
  - 테스트 커버리지 95%+

- [ ] 무엇이 잘 안 되었나?
  - 초기 PTY 구현 복잡도 과소평가
  - LLM API 비용 예상보다 높음
  - 일부 E2E 테스트 불안정

- [ ] 개선할 점은?
  - 더 작은 단위로 작업 분할
  - 일일 진행상황 문서화
  - 리스크 조기 식별

- [ ] Phase 3에서 시도할 것은?
  - CI/CD 파이프라인 강화
  - 모니터링 도구 통합
  - A/B 테스팅

**최종 체크리스트**:
- [ ] 모든 테스트 통과
- [ ] 문서 완성
- [ ] 코드 리뷰
- [ ] 보안 점검
- [ ] 성능 목표 달성
- [ ] Phase 3 준비

**완료 기준**:
- ✅ Phase 2 문서 완성 (~2,000줄)
- ✅ API 문서 최신화
- ✅ README 업데이트
- ✅ 회고 완료
- ✅ Phase 2 → Phase 3 전환 준비 완료

---

## 🎯 기술 도메인별 작업 분류

### 🤖 LLM 통합 (Week 5)
- **담당**: backend-code-writer + unit-test-generator
- **주요 작업**:
  - OpenAI/Claude API 연동
  - 병렬 팁 생성 (7개 < 10초)
  - Pydantic 품질 검증
  - 드래프트 CRUD API
- **완료 기준**:
  - 드래프트 자동 생성 정상 동작
  - TDD 테스트 커버리지 95%+

### 🖥 PTY 터미널 (Week 6)
- **담당**: backend-code-writer
- **주요 작업**:
  - Docker attach_socket() 구현
  - PTY 스트리밍
  - vim/nano 지원
  - 보안 강화
- **완료 기준**:
  - vim 파일 편집 가능
  - cd 상태 유지
  - 위험 명령어 차단

### 🎨 사용자 경험 (Week 7)
- **담당**: frontend-code-writer + ui-ux-designer
- **주요 작업**:
  - PostgreSQL FTS 검색
  - 무한 스크롤 히스토리
  - 반응형 디자인
  - 접근성 개선
- **완료 기준**:
  - Lighthouse 90+
  - WCAG 2.1 AA 준수
  - 모바일 완전 지원

### 📊 관리자 대시보드 (Week 5, 8)
- **담당**: frontend-code-writer + backend-code-writer
- **주요 작업**:
  - 드래프트 관리 UI
  - 실시간 통계
  - 시스템 모니터링
  - 차트/테이블
- **완료 기준**:
  - 실시간 대시보드 렌더링
  - 5분 자동 새로고침
  - 반응형 레이아웃

---

## 📊 마일스톤 및 검증 포인트

### 🚩 Week 5 마일스톤: LLM 통합 완료
- **검증**: 7개 팁 병렬 생성 < 10초
- **위험**: LLM API 비용 초과
- **백업**: Claude API 대체 또는 수동 작성

### 🚩 Week 6 마일스톤: PTY 터미널 완성
- **검증**: vim/nano 편집 가능
- **위험**: PTY 구현 복잡도
- **백업**: Phase 1 exec 방식 유지

### 🚩 Week 7 마일스톤: 사용자 경험 개선
- **검증**: Lighthouse 90+, WCAG 2.1 AA
- **위험**: 성능 목표 미달
- **백업**: 점진적 개선

### 🚩 Week 8 마일스톤: Phase 2 완성
- **검증**: E2E 테스트 30/30 통과
- **위험**: 통합 이슈
- **백업**: 우선순위 조정

---

## ⚠️ 리스크 관리

### 높은 위험도 🔴
1. **LLM API 비용**: 캐싱, 월 예산 설정
2. **PTY 복잡성**: 단계적 구현, fallback 준비

### 중간 위험도 🟡
3. **드래프트 워크플로우**: TDD, 상태 다이어그램
4. **성능 목표**: 점진적 최적화

### 낮은 위험도 🟢
5. **반응형 디자인**: Chrome DevTools 테스트
6. **접근성**: axe DevTools 자동 감사

---

## 🤝 에이전트 역할 분담

| 에이전트 | 주요 역할 | 담당 주차 |
|---------|---------|----------|
| service-planner | 전체 일정 관리 | 전 기간 |
| backend-code-writer | LLM, PTY, API | Week 5-6, 8 |
| frontend-code-writer | UI, 대시보드 | Week 5, 7-8 |
| ui-ux-designer | 디자인, 접근성 | Week 7-8 |
| unit-test-generator | TDD 테스트 | Week 5-6 |
| code-quality-evaluator | 코드 평가 | 매주 마지막 날 |

---

## 📈 성공 지표 (KPI)

### 기술적 성능
- LLM 생성: 7개 < 10초 ✅
- PTY 안정성: 95%+ ✅
- Lighthouse: 90+ ✅
- 테스트 커버리지: 90%+ ✅

### 기능 완성도
- LLM 통합: 100% ✅
- PTY 터미널: 100% ✅
- 검색/필터: 100% ✅
- 대시보드: 100% ✅

### 개발 효율성
- 일정 준수율: 95%+
- 버그 해결율: 90%+
- 문서화: 2,000줄+

---

## 📚 참고 문서

- Phase 1 완료 보고서: `docs/phase1-completion-report.md`
- 요구사항 정의서: `docs/requirements.md`
- 서비스 기획서: `docs/service-planning.md`
- API 레퍼런스: `backend/docs/API_REFERENCE.md`
- 사용자 가이드: `docs/USER_GUIDE.md`

---

**작성일**: 2025-11-07
**작성자**: Claude Code + 개발팀
**버전**: 1.0.0
**다음 검토**: Week 5 완료 후 (2025-11-14)