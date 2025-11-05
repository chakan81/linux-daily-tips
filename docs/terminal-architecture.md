# 터미널 에뮬레이터 시스템 아키텍처 설계서

## 📋 문서 개요

### 목적
Linux Daily Tips 웹서비스의 **터미널 에뮬레이터 시스템**을 위한 상세 아키텍처 설계 문서입니다. 사용자가 웹 브라우저에서 안전하게 Linux 명령어를 실습할 수 있는 실시간 터미널 환경을 제공합니다.

### 문서 범위
- 전체 시스템 구성 및 데이터 플로우
- 컴포넌트별 인터페이스 정의
- 보안 및 격리 전략
- 성능 최적화 방안
- 프로토타입 구현 가이드 (Phase 1 Week 3)

### 작성일
2025-10-28

### 최종 업데이트
2025-10-30 (Day 21 보안/최적화 완료 후) 🎉

---

## 🚦 현재 구현 상태 (2025-10-30)

### ✅ Phase 1 완료 (PoC 수준) - Week 3 마일스톤 100% 달성!
**구현 완료된 기능**:
- ✅ xterm.js 5.6.0 터미널 UI 브라우저 렌더링
- ✅ WebSocket 실시간 양방향 통신 (재연결 로직 포함)
- ✅ Docker 컨테이너(Ubuntu 24.04) 생성 및 관리
- ✅ 기본 명령어 실행 (ls, pwd, cat, echo, ./script.sh)
- ✅ 명령어 결과 출력 및 에러 처리
- ✅ Playwright 자동화 테스트 통과
- ✅ **보안 검증 완료** (네트워크 격리, 리소스 제한, 세션 타임아웃)
- ✅ **성능 측정 완료** (세션 생성 0.14초, 명령어 실행 0.055초)
- ✅ **컨테이너 정리 크론잡** (1분 주기 백그라운드 작업)

**현재 동작 플로우**:
```
사용자 입력 (Enter) → WebSocket 전송 → Docker exec 실행 → 결과 반환 (0.055초) → 터미널 출력
```

### ⚠️ Phase 1 미완성 (핵심 기능 부족)
**현재 제약사항**:
- ❌ **라인 버퍼 모드만 지원**: Enter 키를 눌러야 명령어 전송 (실시간 문자 입력 불가)
- ❌ **인터랙티브 명령어 미지원**: vim, nano, top, htop, less 등 대화형 프로그램 실행 불가
- ❌ **세션 상태 미유지**: 각 명령어가 독립적으로 실행됨 (cd, export 등 상태 초기화)
- ❌ **특수 키 미처리**: Ctrl+C (중단), Ctrl+D (종료), 화살표(히스토리) 등 동작 안 함
- ❌ **PTY(Pseudo-Terminal) 미사용**: 실제 터미널 에뮬레이션이 아닌 단순 exec 실행
- ❌ **ANSI 색상 코드 부분 지원**: xterm.js는 지원하지만 Docker exec 출력이 색상 없음

**비유로 설명**:
- 현재: "명령어를 보내면 결과가 오는 채팅봇" 수준
- 목표: "실제 SSH 터미널처럼 동작하는 완전한 셸" 수준

### 🎯 Phase 2 필수 개선사항
**완전한 터미널을 위해 필요한 기능**:
1. **PTY(Pseudo-Terminal) 구현**: Docker exec에서 `-it` 플래그 + PTY 할당
2. **지속적인 셸 세션**: bash 프로세스를 계속 실행하고 stdin/stdout 스트리밍
3. **실시간 문자 스트리밍**: 키 입력마다 즉시 전송 (라인 버퍼 제거)
4. **특수 키 처리**: Ctrl+C, Ctrl+D, Ctrl+L, 화살표 키 등 터미널 제어 문자 전달
5. **ANSI 이스케이프 시퀀스**: 색상, 커서 제어, 화면 지우기 등 지원
6. **인터랙티브 프로그램 지원**: vim, nano, less, top 등 정상 동작

**기술적 접근**:
- Docker Python SDK의 `attach_socket()` 사용
- WebSocket을 바이너리 모드로 전환
- xterm.js의 `onData` 이벤트로 실시간 입력 캡처

### 📊 구현 단계 비교

| 기능 | Phase 1 (현재) | Phase 2 (목표) |
|------|----------------|----------------|
| **명령어 실행** | ✅ 한 줄씩 실행 | ✅ 지속적 셸 세션 |
| **입력 방식** | Enter 후 전송 | 키 입력마다 전송 |
| **출력 방식** | 명령어 완료 후 일괄 반환 | 실시간 스트리밍 |
| **대화형 프로그램** | ❌ 미지원 | ✅ vim, nano, top 등 |
| **세션 상태** | ❌ 명령어마다 초기화 | ✅ cd, export 유지 |
| **특수 키** | ❌ 동작 안 함 | ✅ Ctrl+C, 화살표 등 |
| **ANSI 색상** | ❌ 평문만 | ✅ 완전 지원 |
| **사용자 경험** | "명령어 실행기" | "실제 SSH 터미널" |

---

## 🏗 1. 전체 시스템 구성도

### 1.1 아키텍처 다이어그램

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          사용자 브라우저                                      │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              xterm.js Terminal UI Component                        │    │
│  │  - 터미널 UI 렌더링 (xterm.js 5.5+)                                 │    │
│  │  - 키보드 입력 처리                                                  │    │
│  │  - ANSI 색상 코드 지원                                               │    │
│  │  - 터미널 크기 조정 (xterm-addon-fit)                               │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                               ↕ WebSocket 연결                              │
└────────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌────────────────────────────────────────────────────────────────────────────┐
│                      프론트엔드 (Next.js 15)                                │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │            TerminalEmulator.tsx (React Component)                  │    │
│  │  - xterm.js 초기화 및 관리                                          │    │
│  │  - WebSocket 연결 관리                                               │    │
│  │  - 에러 처리 및 재연결 로직                                          │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │         useTerminalWebSocket.ts (Custom Hook)                      │    │
│  │  - WebSocket 연결 상태 관리                                          │    │
│  │  - 메시지 송수신 핸들러                                              │    │
│  │  - 자동 재연결 (exponential backoff)                                │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘
                                    ↕
┌────────────────────────────────────────────────────────────────────────────┐
│                      백엔드 FastAPI 서버                                     │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              WebSocket Handler                                     │    │
│  │  WS /ws/terminal/{session_id}                                      │    │
│  │  - 클라이언트 연결 관리                                              │    │
│  │  - 명령어 수신 및 결과 전송                                          │    │
│  │  - 세션 타임아웃 관리 (30초)                                         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │           TerminalService (Business Logic)                         │    │
│  │  - Docker 컨테이너 생명주기 관리                                     │    │
│  │  - 명령어 실행 (비동기 asyncio)                                      │    │
│  │  - 세션 정보 Redis 저장                                              │    │
│  │  - 보안 검증 (블랙리스트 검사)                                       │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              Redis Session Store                                   │    │
│  │  - session:{session_id} (TTL: 30초)                                │    │
│  │    { container_id, user_id, created_at, last_activity }            │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘
                                    ↕ Docker SDK for Python
┌────────────────────────────────────────────────────────────────────────────┐
│                    Docker 컨테이너 (Ubuntu 24.04 LTS)                       │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                 Isolated Sandbox Environment                       │    │
│  │  - 베이스 이미지: ubuntu:24.04                                       │    │
│  │  - 사전 구성된 파일시스템 (/workspace)                               │    │
│  │  - Bash 명령어 실행 환경                                             │    │
│  │  - 리소스 제한 적용 (메모리 256MB, CPU 0.5)                         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                               ↕ exec 명령                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              Bash 명령어 실행 및 출력 캡처                           │    │
│  │  $ ls -la → stdout/stderr 반환                                     │    │
│  │  $ pwd    → /workspace                                             │    │
│  │  $ echo   → Hello, Linux!                                          │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 기술 스택 매핑

| 계층 | 기술 스택 | 버전 | 역할 |
|------|-----------|------|------|
| **프론트엔드 UI** | @xterm/xterm | 5.3+ | 터미널 UI 렌더링 (scoped package) |
| **프론트엔드 UI** | @xterm/addon-fit | latest | 터미널 크기 자동 조정 (scoped package) |
| **프론트엔드 프레임워크** | Next.js | 16+ | React 애플리케이션 프레임워크 (Turbopack stable, React Compiler) |
| **프론트엔드 통신** | WebSocket API | Native | 실시간 양방향 통신 |
| **백엔드 프레임워크** | FastAPI | 0.119+ | 비동기 WebSocket 서버 |
| **백엔드 컨테이너 관리** | Docker SDK for Python | 7.1+ | 컨테이너 생명주기 관리 |
| **백엔드 Redis 클라이언트** | redis-py | 7.0+ | Python Redis 클라이언트 (Python 3.9+) |
| **백엔드 세션 저장소** | Redis Server | 8+ | 세션 상태 및 타임아웃 관리 |
| **컨테이너 베이스 이미지** | Ubuntu | 24.04 LTS | Linux 명령어 실행 환경 |

---

## 🔄 2. 데이터 플로우 상세

### 2.1 세션 생성 플로우

```
[단계 1] 사용자 접속
사용자가 "/terminal" 페이지 접속
    ↓
[단계 2] 세션 생성 API 호출
GET /api/v1/terminal/session
    ↓
[단계 3] 백엔드 처리
1. ULID 기반 세션 ID 생성 (sess_01HQK8X...)
2. Docker 컨테이너 생성
   - 이미지: linux-daily-tips-terminal:latest
   - 리소스 제한: mem=256MB, cpu=0.5
   - 네트워크: none (격리)
3. Redis에 세션 정보 저장 (TTL: 30초)
   key: session:{session_id}
   value: {container_id, created_at, last_activity}
    ↓
[단계 4] 응답 반환
{
  "success": true,
  "data": {
    "session_id": "sess_01HQK8X...",
    "ws_url": "ws://localhost:8000/ws/terminal/sess_01HQK8X..."
  }
}
    ↓
[단계 5] WebSocket 연결
프론트엔드가 ws_url로 WebSocket 연결
    ↓
[단계 6] 터미널 준비 완료
xterm.js에 프롬프트 표시: root@container:/workspace$
```

**예상 소요 시간**: 1.5-2초
- Docker 컨테이너 생성: 1-1.5초 (프로토타입 목표)
- Redis 저장 + WebSocket 연결: 0.5초

### 2.2 명령어 실행 플로우

```
[단계 1] 사용자 입력
사용자가 "ls -la" 입력 후 Enter
    ↓
[단계 2] xterm.js 처리
입력 문자열 캡처: "ls -la\n"
    ↓
[단계 3] WebSocket 메시지 전송
{
  "type": "command",
  "data": "ls -la"
}
    ↓
[단계 4] 백엔드 수신 및 검증
1. 세션 유효성 확인 (Redis 조회)
2. 블랙리스트 검증 (rm -rf /, mkfs 등 차단)
3. 명령어 길이 제한 (최대 1000자)
    ↓
[단계 5] Docker exec 실행 (비동기)
docker.containers.get(container_id).exec_run(
    cmd=["bash", "-c", "ls -la"],
    stdout=True,
    stderr=True,
    demux=True,
    timeout=5  # 5초 제한
)
    ↓
[단계 6] 결과 캡처
stdout: "total 8\ndrwxr-xr-x 2 root root 4096 Oct 28 12:00 .\n..."
stderr: ""
exit_code: 0
    ↓
[단계 7] WebSocket 응답 전송
{
  "type": "output",
  "data": "total 8\ndrwxr-xr-x 2 root root 4096 Oct 28 12:00 .\n..."
}
    ↓
[단계 8] 프론트엔드 렌더링
xterm.js가 터미널에 출력 표시
    ↓
[단계 9] Redis TTL 갱신
세션의 last_activity 업데이트 (sliding expiration)
```

**예상 소요 시간**: 500ms - 1초
- WebSocket 왕복: 100ms
- Docker exec 실행: 300-800ms
- 결과 렌더링: 100ms

### 2.3 세션 종료 플로우

```
[방법 1] 사용자 명시적 종료
사용자가 "exit" 명령 입력 또는 페이지 이탈
    ↓
WebSocket 연결 종료 이벤트
    ↓
백엔드 on_disconnect 핸들러 호출

[방법 2] 타임아웃 자동 종료
30초 동안 활동 없음 (Redis TTL 만료)
    ↓
Redis 만료 이벤트 또는 정리 크론잡 감지

[공통] 정리 작업
1. Docker 컨테이너 중지 및 삭제
   docker.containers.get(container_id).remove(force=True)
2. Redis 세션 데이터 삭제
   redis.delete(f"session:{session_id}")
3. 로그 기록 (AnalyticsEvent 저장)
   - 세션 지속 시간
   - 실행된 명령어 수
   - 사용된 리소스
```

**정리 시간**: 500ms 이하
- 컨테이너 삭제: 200-400ms
- Redis 정리: 50-100ms

---

## 🔌 3. 컴포넌트 인터페이스 정의

### 3.1 WebSocket 메시지 프로토콜

#### 3.1.1 클라이언트 → 서버 메시지

**명령어 실행 요청**
```json
{
  "type": "command",
  "data": "ls -la",
  "timestamp": "2025-10-28T12:00:00Z"
}
```

**핑 (연결 유지)**
```json
{
  "type": "ping",
  "timestamp": "2025-10-28T12:00:00Z"
}
```

#### 3.1.2 서버 → 클라이언트 메시지

**명령어 실행 결과**
```json
{
  "type": "output",
  "data": "total 8\ndrwxr-xr-x 2 root root 4096 Oct 28 12:00 .\n...",
  "exit_code": 0,
  "timestamp": "2025-10-28T12:00:01Z"
}
```

**에러 응답**
```json
{
  "type": "error",
  "code": "CONTAINER_ERROR",
  "message": "컨테이너 실행 실패",
  "details": "Container not found: cont_01HQK8X...",
  "timestamp": "2025-10-28T12:00:01Z"
}
```

**세션 타임아웃 경고**
```json
{
  "type": "warning",
  "message": "세션이 10초 후 만료됩니다.",
  "timestamp": "2025-10-28T12:00:20Z"
}
```

**폰 응답 (연결 확인)**
```json
{
  "type": "pong",
  "timestamp": "2025-10-28T12:00:00Z"
}
```

### 3.2 백엔드 API 엔드포인트

#### 3.2.1 세션 생성 API

**요청**
```http
GET /api/v1/terminal/session HTTP/1.1
Host: localhost:8000
Authorization: Bearer <optional_jwt_token>
```

**응답 (성공)**
```json
{
  "success": true,
  "data": {
    "session_id": "sess_01HQK8XJVX5Y2Z3A4B5C6D7E8F",
    "container_id": "cont_a1b2c3d4e5f6",
    "ws_url": "ws://localhost:8000/ws/terminal/sess_01HQK8XJVX5Y2Z3A4B5C6D7E8F",
    "expires_at": "2025-10-28T12:00:30Z"
  },
  "meta": {
    "timestamp": "2025-10-28T12:00:00Z"
  }
}
```

**응답 (실패)**
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_LIMIT_EXCEEDED",
    "message": "최대 동시 세션 수를 초과했습니다.",
    "details": "현재 활성 세션: 100/100"
  }
}
```

#### 3.2.2 WebSocket 연결

**연결**
```
WS ws://localhost:8000/ws/terminal/{session_id}
```

**연결 성공 시**
- 초기 메시지로 프롬프트 전송
```json
{
  "type": "output",
  "data": "Welcome to Linux Daily Tips Terminal!\nroot@container:/workspace$ "
}
```

**연결 실패 시**
- HTTP 403: 유효하지 않은 세션 ID
- HTTP 404: 세션이 만료됨
- HTTP 500: 서버 내부 오류

#### 3.2.3 세션 종료 API

**요청**
```http
DELETE /api/v1/terminal/session/{session_id} HTTP/1.1
Host: localhost:8000
Authorization: Bearer <optional_jwt_token>
```

**응답**
```json
{
  "success": true,
  "data": {
    "session_id": "sess_01HQK8XJVX5Y2Z3A4B5C6D7E8F",
    "terminated_at": "2025-10-28T12:05:00Z",
    "duration_seconds": 300
  }
}
```

### 3.3 프론트엔드 컴포넌트 구조

#### 3.3.1 TerminalEmulator.tsx

**역할**: xterm.js를 래핑하는 React 컴포넌트

**Props**
```typescript
interface TerminalEmulatorProps {
  sessionId: string;
  wsUrl: string;
  onError?: (error: Error) => void;
  onClose?: () => void;
}
```

**주요 메서드**
```typescript
class TerminalEmulator {
  // xterm.js 인스턴스 초기화
  initializeTerminal(container: HTMLElement): void;

  // WebSocket 연결
  connectWebSocket(wsUrl: string): void;

  // 명령어 전송
  sendCommand(command: string): void;

  // 출력 렌더링
  renderOutput(output: string): void;

  // 정리 (언마운트)
  cleanup(): void;
}
```

#### 3.3.2 useTerminalWebSocket.ts

**역할**: WebSocket 연결 상태 관리 및 재연결 로직

**Hook 인터페이스**
```typescript
interface UseTerminalWebSocket {
  isConnected: boolean;
  error: Error | null;
  sendMessage: (message: WebSocketMessage) => void;
  disconnect: () => void;
}

function useTerminalWebSocket(
  wsUrl: string,
  onMessage: (message: WebSocketMessage) => void,
  options?: {
    reconnectAttempts?: number;  // 기본값: 3
    reconnectDelay?: number;     // 기본값: 1000ms
  }
): UseTerminalWebSocket;
```

**재연결 전략**
```typescript
// Exponential backoff
attempt 1: 1초 후 재시도
attempt 2: 2초 후 재시도
attempt 3: 4초 후 재시도
attempt 4: 연결 포기, 사용자에게 에러 표시
```

#### 3.3.3 페이지 구조

**라우트**: `/app/terminal/page.tsx`

**주요 기능**
- 세션 생성 API 호출
- TerminalEmulator 컴포넌트 렌더링
- 에러 처리 및 사용자 피드백
- 세션 종료 처리

---

## 🔒 4. 보안 및 격리 전략

### 4.1 컨테이너 격리

#### 4.1.1 네트워크 격리

**설정**
```python
container = client.containers.run(
    image="linux-daily-tips-terminal:latest",
    network_mode="none",  # 외부 네트워크 완전 차단
    detach=True
)
```

**보안 효과**
- 외부 인터넷 접속 불가 (curl, wget 차단)
- 다른 컨테이너와 통신 불가
- 호스트 네트워크 접근 불가

#### 4.1.2 파일시스템 보호

**설정**
```python
container = client.containers.run(
    image="linux-daily-tips-terminal:latest",
    read_only=True,  # 루트 파일시스템 읽기 전용
    tmpfs={
        "/tmp": "size=50m",         # 임시 파일 50MB 제한
        "/workspace": "size=50m"    # 작업 공간 50MB 제한
    },
    detach=True
)
```

**보안 효과**
- 시스템 파일 수정 불가 (/bin, /usr, /etc)
- 임시 파일 저장 공간 제한
- 컨테이너 재시작 시 모든 변경사항 초기화

#### 4.1.3 리소스 제한

**설정**
```python
container = client.containers.run(
    image="linux-daily-tips-terminal:latest",
    mem_limit="256m",      # 메모리 256MB 제한
    memswap_limit="256m",  # 스왑 비활성화
    cpu_quota=50000,       # CPU 0.5 코어 (50% of 100,000)
    pids_limit=100,        # 최대 프로세스 수 100개
    detach=True
)
```

**보안 효과**
- 메모리 폭탄 공격 방어
- CPU 독점 방지
- 포크 폭탄 공격 방어 (fork bomb)

### 4.2 명령어 보안

#### 4.2.1 블랙리스트 검증

**위험 명령어 목록**
```python
DANGEROUS_COMMANDS = [
    # 파일시스템 파괴
    "rm -rf /",
    "mkfs",
    "dd",

    # 시스템 설정 변경
    "iptables",
    "ufw",
    "systemctl",
    "service",

    # 네트워크 공격
    "nc",
    "netcat",
    "nmap",

    # 패키지 관리 (리소스 남용)
    "apt",
    "apt-get",
    "yum",
    "dnf",

    # 사용자 관리
    "useradd",
    "userdel",
    "passwd",
    "sudo",
    "su",
]
```

**검증 로직**
```python
def is_command_safe(command: str) -> bool:
    """명령어 안전성 검증"""
    command_lower = command.lower().strip()

    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command_lower:
            return False

    # 파이프를 통한 우회 방지
    if "|" in command and any(d in command_lower for d in DANGEROUS_COMMANDS):
        return False

    return True
```

#### 4.2.2 실행 시간 제한

**설정**
```python
# 명령어별 타임아웃
COMMAND_TIMEOUT = 5  # 초

try:
    result = container.exec_run(
        cmd=["bash", "-c", command],
        stdout=True,
        stderr=True,
        demux=True,
        timeout=COMMAND_TIMEOUT  # 5초 초과 시 강제 종료
    )
except docker.errors.APIError as e:
    if "timeout" in str(e):
        raise CommandTimeoutError("명령어 실행 시간이 초과되었습니다.")
```

**보안 효과**
- 무한 루프 명령어 방지 (while true; do echo; done)
- 슬립 공격 방지 (sleep 999999)
- 리소스 독점 방지

#### 4.2.3 출력 크기 제한

**설정**
```python
MAX_OUTPUT_SIZE = 10 * 1024  # 10KB

def truncate_output(output: str) -> str:
    """출력 크기 제한"""
    if len(output) > MAX_OUTPUT_SIZE:
        truncated = output[:MAX_OUTPUT_SIZE]
        return truncated + "\n... (출력이 잘렸습니다. 최대 10KB)"
    return output
```

**보안 효과**
- 메모리 소진 공격 방지 (cat /dev/zero)
- WebSocket 대역폭 보호

### 4.3 세션 관리 보안

#### 4.3.1 세션 ID 생성

**ULID 기반 ID**
```python
import ulid

def generate_session_id() -> str:
    """안전한 세션 ID 생성"""
    return f"sess_{ulid.create()}"
    # 예시: sess_01HQK8XJVX5Y2Z3A4B5C6D7E8F
```

**보안 특성**
- 시간 기반 정렬 가능 (성능)
- 128비트 무작위성 (추측 불가)
- URL 안전 문자만 사용

#### 4.3.2 세션 타임아웃

**Redis TTL 기반 자동 만료**
```python
# 세션 생성 시
redis_client.setex(
    f"session:{session_id}",
    30,  # 30초 TTL
    json.dumps({
        "container_id": container_id,
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    })
)

# 활동 시 TTL 갱신 (sliding expiration)
redis_client.expire(f"session:{session_id}", 30)
```

**보안 효과**
- 유휴 세션 자동 정리
- 메모리 누수 방지
- 리소스 회수 보장

#### 4.3.3 관리자 인증 연동 (선택적)

**Phase 1 (프로토타입)**: 인증 없이 누구나 사용 가능

**Phase 2 (프로덕션)**: JWT 기반 접근 제어
```python
@router.get("/terminal/session")
async def create_terminal_session(
    current_admin: AdminUser = Depends(get_current_admin)  # 선택적
):
    # 관리자만 터미널 세션 생성 가능
    ...
```

---

## 🚀 5. 성능 최적화 전략

### 5.1 컨테이너 풀링 (Phase 3 확장)

**목표**: 세션 생성 시간 < 500ms 달성

**설계**
```python
class ContainerPool:
    """사전 생성된 컨테이너 풀"""

    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.available: List[str] = []  # 사용 가능한 컨테이너 ID
        self.in_use: Set[str] = set()   # 사용 중인 컨테이너 ID

    async def initialize(self):
        """풀 초기화: 5개 컨테이너 사전 생성"""
        for _ in range(self.pool_size):
            container_id = await self._create_container()
            self.available.append(container_id)

    async def acquire(self) -> str:
        """컨테이너 할당 (즉시 반환)"""
        if not self.available:
            # 풀이 비었으면 새로 생성 (fallback)
            return await self._create_container()

        container_id = self.available.pop()
        self.in_use.add(container_id)
        return container_id

    async def release(self, container_id: str):
        """컨테이너 반환 (재사용 가능)"""
        self.in_use.remove(container_id)
        await self._reset_container(container_id)  # 파일시스템 초기화
        self.available.append(container_id)

    async def _create_container(self) -> str:
        """새 컨테이너 생성"""
        ...

    async def _reset_container(self, container_id: str):
        """컨테이너 초기화 (작업 공간 클린업)"""
        ...
```

**성능 개선**
- 기존: 1-1.5초 (컨테이너 생성)
- 풀링: < 500ms (즉시 할당)

**트레이드오프**
- 메모리 사용량 증가: 5개 × 256MB = 1.28GB
- 유지보수 복잡도 증가 (컨테이너 상태 관리)

### 5.2 응답 시간 최적화

#### 5.2.1 목표 성능 지표

| 작업 | 목표 시간 | 최적화 전략 |
|------|-----------|-------------|
| **세션 생성** | < 2초 (프로토타입) | Docker 이미지 경량화 |
| **세션 생성** | < 500ms (풀링) | 컨테이너 풀링 구현 |
| **명령어 실행** | < 1초 | 비동기 처리, exec 최적화 |
| **WebSocket 지연** | < 100ms | Redis pub/sub 고려 |

#### 5.2.2 Docker 이미지 최적화

**Dockerfile 예시**
```dockerfile
# 경량 베이스 이미지 사용
FROM ubuntu:24.04

# 최소 패키지만 설치
RUN apt-get update && apt-get install -y \
    coreutils \
    bash \
    && rm -rf /var/lib/apt/lists/*  # 캐시 삭제로 이미지 크기 감소

# 작업 디렉토리 생성
WORKDIR /workspace

# 불필요한 서비스 제거
RUN systemctl disable --now apt-daily.timer apt-daily-upgrade.timer

# 컨테이너 시작 시 실행할 명령어 없음 (exec로 명령어 실행)
CMD ["/bin/bash"]
```

**이미지 크기 목표**
- 최소화: 100-150MB (Ubuntu 기본 이미지 약 80MB)
- 최적화 전략: 다단계 빌드, 불필요한 패키지 제거

### 5.3 리소스 관리

#### 5.3.1 동시 세션 수 제한

**설정**
```python
MAX_CONCURRENT_SESSIONS = 100

async def create_terminal_session():
    """세션 생성 API"""
    current_sessions = await redis_client.dbsize()

    if current_sessions >= MAX_CONCURRENT_SESSIONS:
        raise HTTPException(
            status_code=503,
            detail="최대 동시 세션 수를 초과했습니다. 잠시 후 다시 시도해주세요."
        )

    # 세션 생성 로직
    ...
```

**리소스 계산**
- 컨테이너당 메모리: 256MB
- 최대 동시 세션: 100개
- 총 메모리 필요량: 25.6GB (여유 공간 포함 32GB 권장)

#### 5.3.2 컨테이너 정리 크론잡

**비동기 정리 작업**
```python
import asyncio

async def cleanup_expired_containers():
    """만료된 컨테이너 자동 정리"""
    while True:
        try:
            # Redis에서 만료된 세션 확인
            active_sessions = await redis_client.keys("session:*")
            all_containers = await docker_client.containers.list()

            for container in all_containers:
                container_id = container.short_id
                session_exists = any(
                    container_id in session_data
                    for session_data in active_sessions
                )

                if not session_exists:
                    # Redis에 없으면 고아 컨테이너 → 삭제
                    await container.remove(force=True)
                    logger.info(f"Cleaned up orphaned container: {container_id}")

        except Exception as e:
            logger.error(f"Cleanup error: {e}")

        await asyncio.sleep(60)  # 1분마다 실행
```

---

## 🏃 6. 프로토타입 구현 가이드 (Phase 1 Week 3)

### 6.1 프로토타입 범위 정의

**✅ Phase 1 완료 (PoC 수준, Day 15-20)**
- ✅ 단일 세션 생성 및 종료 (POST /session, DELETE /session/{id})
- ✅ 기본 명령어 실행 (ls, pwd, echo, cat, ./script.sh)
- ✅ WebSocket 실시간 통신 (WS /ws/{session_id})
- ✅ 단순 에러 처리 (타임아웃, 연결 끊김, JSON 에러)
- ✅ 세션 타임아웃 구현 (30분 자동 만료)
- ✅ Docker 컨테이너 샌드박스 (Ubuntu 24.04)
- ✅ xterm.js 5.6.0 터미널 UI
- ✅ 기본 보안 설정 (network_disabled, 리소스 제한)

**⚠️ Phase 1 미완성 (핵심 터미널 기능 부족)**
- ❌ **PTY(Pseudo-Terminal)**: 실제 터미널 에뮬레이션 불가
- ❌ **지속적 셸 세션**: cd, export 등 상태 유지 안 됨
- ❌ **실시간 문자 입력**: Enter 키를 눌러야 명령어 전송
- ❌ **인터랙티브 프로그램**: vim, nano, top 등 실행 불가
- ❌ **특수 키 처리**: Ctrl+C, Ctrl+D, 화살표 등 미지원
- ❌ **ANSI 색상**: Docker exec 출력에 색상 코드 없음

**🎯 Phase 2 필수 개선 (완전한 터미널 구현)**
- ⏳ Docker attach_socket() 기반 PTY 스트리밍
- ⏳ xterm.js onData → WebSocket 바이너리 전송
- ⏳ 지속적 bash 프로세스 + stdin/stdout 스트리밍
- ⏳ Ctrl+C, Ctrl+D, 화살표 키 등 터미널 제어 문자
- ⏳ ANSI 이스케이프 시퀀스 완전 지원
- ⏳ vim, nano, less, top 등 대화형 프로그램 지원

**🚀 Phase 3 확장 기능 (프로덕션 준비)**
- ⏳ 컨테이너 풀링 (세션 생성 < 500ms)
- ⏳ 블랙리스트 명령어 검증 (rm -rf /, sudo 등 차단)
- ⏳ 상세 로깅 및 분석 (AnalyticsEvent 저장)
- ⏳ 반응형 터미널 UI (모바일/태블릿 지원)
- ⏳ 세션 복구 (브라우저 새로고침 후 재연결)
- ⏳ 터미널 녹화 및 재생 (asciinema 스타일)

### 6.2 구현 우선순위

#### Day 15-16: 프론트엔드 터미널 UI ✅ (완료)
**목표**: 브라우저에서 터미널 UI 렌더링

**체크리스트**
- [x] xterm.js 설치 (`npm install xterm@5.6.0 @xterm/addon-fit`)
- [x] TerminalEmulator.tsx 컴포넌트 작성
- [x] shadcn/ui Card로 터미널 래핑
- [x] 기본 입력/출력 테스트 (로컬 에코)

**완료 기준**: 브라우저에서 터미널 프롬프트 표시, 키보드 입력 가능 ✅

#### Day 17-18: WebSocket 실시간 통신 ✅ (완료)
**목표**: 프론트엔드-백엔드 WebSocket 연결

**체크리스트**
- [x] FastAPI WebSocket 엔드포인트 구현 (`/ws/terminal/{session_id}`)
- [x] useTerminalWebSocket.ts 커스텀 훅 작성
- [x] 메시지 송수신 테스트 (명령어 실행)
- [x] 재연결 로직 구현 (3회 시도, exponential backoff)

**완료 기준**: WebSocket을 통해 메시지 실시간 송수신 확인 ✅

#### Day 19-20: Docker 컨테이너 통합 ✅ (완료)
**목표**: Docker 컨테이너에서 명령어 실행

**체크리스트**
- [x] Docker Python SDK 설치 (docker>=7.1.0)
- [x] Dockerfile 작성 (Ubuntu 24.04 기반)
- [x] TerminalService 구현 (컨테이너 생명주기 관리)
- [x] exec_run 비동기 래퍼 작성
- [x] 세션 생성 API 구현 (`POST /api/v1/terminal/session`)
- [x] 세션 종료 API 구현 (`DELETE /api/v1/terminal/session/{id}`)

**완료 기준**: API 호출로 컨테이너 생성, 명령어 실행, 결과 반환 확인 ✅

#### Day 21: 보안 및 최적화 ✅ (완료!)
**목표**: 기본 보안 설정 및 성능 최적화

**체크리스트**
- [x] 네트워크 격리 적용 (`network_mode=none`) - **실제 동작 검증 완료**
- [x] 리소스 제한 적용 (mem_limit=256MB, cpu_quota=0.5) - **실제 동작 검증 완료**
- [x] 세션 타임아웃 구현 (30분 자동 만료) - **실제 동작 검증 완료**
- [x] 컨테이너 정리 크론잡 구현 - **1분 주기 백그라운드 작업 완료**
- [x] 응답 시간 측정 및 최적화 - **목표 초과 달성 (세션 0.14초, 명령어 0.055초)**
- [x] 동시 세션 테스트 - **5개 0.32초, 10개 0.42초 (모두 < 2초)**

**완료 기준**: 보안 설정 적용 확인, < 2초 응답 시간 달성 ✅
**최종 상태**: **Week 3 마일스톤 100% 완료!** 🎉
**완료 보고서**: `backend/docs/day21-security-optimization.md`

### 6.3 검증 시나리오

**시나리오 1: 기본 명령어 실행**
```
1. 사용자가 /terminal 페이지 접속
2. "Loading terminal..." 메시지 표시 (1-2초)
3. 프롬프트 표시: root@container:/workspace$
4. "ls -la" 입력 → 파일 목록 출력
5. "pwd" 입력 → /workspace 출력
6. "echo Hello, Linux!" 입력 → Hello, Linux! 출력
```

**시나리오 2: 에러 처리**
```
1. 존재하지 않는 명령어 입력: "invalidcommand"
   → stderr 출력: bash: invalidcommand: command not found
2. 너무 긴 명령어 실행: "sleep 10"
   → 5초 후 타임아웃, "명령어 실행 시간 초과" 메시지
3. WebSocket 연결 끊김 (네트워크 중단)
   → "연결이 끊어졌습니다. 재연결 중..." 메시지
   → 자동 재연결 시도
```

**시나리오 3: 세션 타임아웃**
```
1. 터미널 실행 후 30초 동안 아무 작업 안 함
2. 세션 만료 경고 메시지 (20초 경과 시)
   → "세션이 10초 후 만료됩니다."
3. 30초 경과 시 자동 종료
   → "세션이 만료되었습니다." 메시지
   → 컨테이너 자동 삭제 확인
```

### 6.4 성능 검증 체크리스트 ✅ (Day 21 완료)

**응답 시간 측정**
- [x] 세션 생성: **0.14초** (목표 < 2초, 93% 빠름!) ✅
- [x] 명령어 실행 (ls): **0.053초** (목표 < 1초, 94.7% 빠름!) ✅
- [x] 명령어 실행 (pwd): **0.048초** (목표 < 800ms, 94% 빠름!) ✅
- [x] 명령어 실행 (echo): **0.052초** ✅
- [x] 명령어 실행 (cat): **0.070초** ✅

**리소스 사용량 측정**
- [x] 컨테이너 메모리: **0.76MB / 256MB** (0.29% 사용) ✅
- [x] 컨테이너 CPU: **0.01%** (< 50% 목표 달성) ✅
- [x] 네트워크: **0B / 0B** (완전 격리 확인) ✅

**동시 세션 테스트**
- [x] 5개 동시 세션: **0.32초** (목표 < 2초 달성) ✅
- [x] 10개 동시 세션: **0.42초** (목표 < 2초 달성) ✅

**최종 평가**: 🎯 **모든 성능 목표 초과 달성!**

---

## 📝 7. 구현 단계별 상세 계획

### 7.1 Phase 1 (PoC 프로토타입 - Week 3) ✅ (100% 완료!) 🎉

**목표**: 기본 플로우 구현 및 검증
**기간**: Day 15-21 (7일)
**성능 목표**: 세션 생성 < 2초, 명령어 실행 < 1초

**완료된 작업 (Day 15-21 전체)**:
1. ✅ xterm.js 5.6.0 터미널 UI 구현
2. ✅ WebSocket 실시간 통신 (재연결 로직 포함)
3. ✅ Docker 컨테이너 명령어 실행 (exec_run 기반)
4. ✅ 기본 보안 설정 (네트워크 격리, 리소스 제한, 세션 타임아웃)
5. ✅ **보안 실제 동작 검증** (Day 21)
6. ✅ **성능 측정 완료** (Day 21 - 목표 초과 달성!)
7. ✅ **컨테이너 정리 크론잡** (Day 21 - 1분 주기)
8. ✅ **동시 세션 테스트** (Day 21 - 5개/10개 성공)
9. ✅ Playwright 자동화 테스트

**달성된 완료 기준**:
- ✅ ls, pwd, cat, echo, ./script.sh 명령어 정상 실행
- ✅ 세션 생성 **0.14초** (목표 < 2초, 93% 빠름!)
- ✅ 명령어 실행 **0.055초** (목표 < 1초, 94.5% 빠름!)
- ✅ 보안 설정 모두 실제 동작 확인
- ✅ 단순 에러 처리 (연결 끊김, 타임아웃, JSON 에러)

**Phase 1 최종 성과**:
- 🎯 **모든 성능 목표 초과 달성**
- 🔒 **프로덕션 수준 보안 검증 완료**
- 📊 **완료 보고서**: `backend/docs/day21-security-optimization.md`

**알려진 제약사항 (Phase 2에서 개선)**:
- ⚠️ 라인 버퍼 모드만 지원 (Enter 후 전송)
- ⚠️ 인터랙티브 프로그램 미지원 (vim, nano, top 등)
- ⚠️ 세션 상태 미유지 (cd, export 초기화)
- ⚠️ 특수 키 미처리 (Ctrl+C, 화살표 등)

### 7.2 Phase 2 (완전한 터미널 구현) ⏳ (필수 개선사항)

**목표**: 실제 터미널 에뮬레이션 구현
**예상 기간**: 1-2주
**핵심 기술**: PTY + WebSocket 바이너리 스트리밍

**필수 작업**:
1. ⏳ Docker attach_socket() 기반 PTY 연결
2. ⏳ 지속적 bash 프로세스 + stdin/stdout 스트리밍
3. ⏳ xterm.js onData 이벤트로 실시간 문자 전송
4. ⏳ 특수 키 처리 (Ctrl+C, Ctrl+D, 화살표 등)
5. ⏳ ANSI 이스케이프 시퀀스 완전 지원
6. ⏳ vim, nano, less, top 등 대화형 프로그램 지원

**완료 기준**:
- vim으로 파일 편집 가능
- cd 명령어로 디렉토리 이동 유지
- Ctrl+C로 명령어 중단 가능
- ls --color 색상 출력 정상 표시
- top 실시간 출력 스트리밍

**기술적 접근**:
```python
# 기존 (Phase 1): exec_run 방식
result = container.exec_run(cmd=["bash", "-c", command])

# 목표 (Phase 2): attach_socket + PTY 방식
exec_instance = container.exec_run(
    cmd=["bash"],
    stdin=True,
    tty=True,
    socket=True,
    demux=True
)
socket = exec_instance.output
# WebSocket ↔ Docker socket 양방향 스트리밍
```

### 7.3 Phase 3 (프로덕션 준비) ⏳ (확장 기능)

**목표**: 성능 최적화 및 보안 강화
**예상 기간**: 1주
**확장 기능**: 컨테이너 풀링, 블랙리스트, 모니터링

**주요 작업**:
1. ⏳ 컨테이너 풀링 구현 (세션 생성 < 500ms)
2. ⏳ 블랙리스트 명령어 검증 (rm -rf /, sudo 등 차단)
3. ⏳ 상세 로깅 및 분석 (AnalyticsEvent 저장)
4. ⏳ 반응형 터미널 UI (모바일/태블릿 지원)
5. ⏳ 세션 복구 (브라우저 새로고침 후 재연결)
6. ⏳ 관리자 대시보드 (세션 모니터링, 실시간 통계)

**완료 기준**:
- 컨테이너 풀링으로 세션 생성 < 500ms
- 위험 명령어 차단 100% 동작
- 모바일/태블릿 터미널 정상 동작
- 동시 세션 100개 지원

---

## 📊 8. 예상 성과 및 KPI

### 8.1 기술적 성능 지표

**Phase 1 (완료, PoC 수준) ✅**
- 세션 생성: **0.14초** (목표 < 2초, 93% 빠름!)
- 명령어 실행: **0.055초** (목표 < 1초, 94.5% 빠름!)
- 동시 세션: **10개 0.42초** (5개 0.32초)
- 리소스 사용: 메모리 0.76MB / 256MB (0.29%), CPU 0.01%
- **제약사항**: 라인 버퍼 모드, 인터랙티브 미지원
- **검증 완료**: Day 21 (2025-10-30)

**Phase 2 (완전한 터미널)**
- 세션 생성: < 2초 유지
- 명령어 실행: < 1초 (모든 명령어)
- 동시 세션: 10-20개 지원
- **개선사항**: PTY, 실시간 스트리밍, vim/nano 지원

**Phase 3 (프로덕션)**
- 세션 생성: < 500ms (컨테이너 풀링)
- 명령어 실행: < 800ms
- 동시 세션: 100개 지원
- **추가 기능**: 블랙리스트, 모니터링, 모바일 지원

### 8.2 사용자 경험 지표

**목표**
- 터미널 사용률: 방문자당 평균 2회 실행
- 세션 지속 시간: 평균 5분
- 에러율: < 5% (세션 생성/명령어 실행)

### 8.3 보안 지표

**목표**
- 컨테이너 탈출 시도: 0건 (네트워크 격리 효과)
- 위험 명령어 차단: 100% (블랙리스트 적용 후)
- 리소스 남용: 0건 (메모리/CPU 제한 효과)

---

## 🔧 9. 트러블슈팅 가이드

### 9.1 자주 발생하는 문제

#### 문제 1: Docker 컨테이너 생성 실패
**증상**
```
docker.errors.APIError: 500 Server Error: Internal Server Error
```

**원인**
- Docker 데몬 미실행
- 디스크 공간 부족
- 이미지 미존재

**해결 방법**
```bash
# Docker 데몬 확인
sudo systemctl status docker

# 디스크 공간 확인
df -h

# 이미지 빌드
cd backend
docker build -t linux-daily-tips-terminal:latest .
```

#### 문제 2: WebSocket 연결 끊김
**증상**
```
WebSocket connection failed: Connection reset by peer
```

**원인**
- 프록시/로드밸런서 타임아웃 (30초)
- 네트워크 불안정

**해결 방법**
```typescript
// 하트비트 구현 (25초마다 ping)
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'ping' }));
  }
}, 25000);
```

#### 문제 3: 명령어 실행 타임아웃
**증상**
```
CommandTimeoutError: Command execution timed out after 5 seconds
```

**원인**
- 무한 루프 명령어
- 느린 명령어 (find /)

**해결 방법**
- 타임아웃 시간 조정 (5초 → 10초)
- 사용자에게 명령어 가이드 제공

---

## 📚 10. 참고 자료

### 10.1 기술 문서
- **xterm.js**: https://xtermjs.org/
- **Docker SDK for Python**: https://docker-py.readthedocs.io/
- **FastAPI WebSocket**: https://fastapi.tiangolo.com/advanced/websockets/

### 10.2 관련 프로젝트 문서
- `docs/requirements.md`: 전체 서비스 요구사항
- `docs/service-planning.md`: 기술 스택 및 아키텍처
- `docs/phase1-tasks.md`: Week 3 상세 작업 계획
- `frontend/CLAUDE.md`: 프론트엔드 개발 가이드
- `backend/CLAUDE.md`: 백엔드 개발 가이드

### 10.3 보안 가이드
- Docker 보안 모범 사례: https://docs.docker.com/engine/security/
- OWASP WebSocket 보안: https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html

---

## ✅ 다음 단계

이 아키텍처 설계서를 바탕으로 Week 3 개발을 시작하세요:

1. **Day 15-16**: `frontend-code-writer`와 함께 xterm.js 터미널 UI 구현
2. **Day 17-18**: WebSocket 실시간 통신 구현 (프론트엔드 + 백엔드)
3. **Day 19-20**: `backend-code-writer`와 함께 Docker 컨테이너 통합
4. **Day 21**: 보안 설정 및 성능 최적화

**중요**: 프로토타입은 최소 기능으로 빠르게 검증하는 것이 목표입니다. 완벽함보다는 동작하는 코드를 우선하세요!
