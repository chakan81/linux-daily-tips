"""
Docker 컨테이너 설정 및 보안 규칙

터미널 에뮬레이터용 Docker 컨테이너의 설정 값과 보안 블랙리스트를 정의합니다.
"""

# 보안 블랙리스트: 위험한 명령어 차단
DANGEROUS_COMMANDS = [
    # 파일시스템 파괴
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd",
    # 시스템 설정 변경
    "iptables",
    "ufw",
    "systemctl",
    "service",
    "reboot",
    "shutdown",
    "poweroff",
    # 네트워크 공격
    "nc",
    "netcat",
    "nmap",
    "curl",
    "wget",
    "ping",
    # 패키지 관리 (리소스 남용)
    "apt",
    "apt-get",
    "yum",
    "dnf",
    "pacman",
    # 사용자 관리
    "useradd",
    "userdel",
    "passwd",
    "sudo",
    "su",
    # 프로세스 조작
    "kill -9 1",  # init 프로세스 종료
    "killall",
    # 무한 루프 (포크 폭탄)
    ":(){ :|:& };:",
    "fork",
]

# 컨테이너 설정
CONTAINER_IMAGE = "linux-daily-tips-terminal:latest"
CONTAINER_MEMORY_LIMIT = "256m"
CONTAINER_CPU_QUOTA = 50000  # 50% of 100,000 (0.5 core)
CONTAINER_PIDS_LIMIT = 100
COMMAND_TIMEOUT = 5  # 초
CONTAINER_STOP_TIMEOUT = 5  # 초
MAX_OUTPUT_SIZE = 10 * 1024  # 10KB

# 컨테이너 라벨
DEFAULT_CONTAINER_LABEL = "app=linux-daily-tips"

# 작업 디렉토리
CONTAINER_WORKDIR = "/home/linuxuser"
