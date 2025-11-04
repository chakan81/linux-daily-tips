"""
테스트 팁 데이터 추가 스크립트

Week 4 프론트엔드-백엔드 통합 테스트를 위한 샘플 데이터 생성
"""

import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.tip import DifficultyLevel, Tip


async def add_test_tips():
    """테스트용 팁 데이터 추가"""
    print("🚀 테스트 팁 데이터 추가 시작...")

    async with AsyncSessionLocal() as session:
        # 기존 데이터 확인
        result = await session.execute(select(Tip))
        existing_tips = result.scalars().all()
        if existing_tips:
            print(f"⚠️  기존 팁 {len(existing_tips)}개 발견. 삭제 후 진행합니다.")
            for tip in existing_tips:
                await session.delete(tip)
            await session.commit()
            print("✅ 기존 데이터 삭제 완료")

        # 오늘의 팁 (초급)
        today_tip = Tip(
            title="ls 명령어로 파일 목록 보기",
            content="""# ls 명령어 사용법

가장 기본적인 리눅스 명령어 중 하나인 `ls`는 현재 디렉토리의 파일과 폴더를 보여줍니다.

## 기본 사용법

```bash
ls
```

## 자주 사용하는 옵션

- `ls -l`: 자세한 정보 표시 (권한, 소유자, 크기, 날짜)
- `ls -a`: 숨김 파일 포함 (`.`으로 시작하는 파일)
- `ls -lh`: 파일 크기를 읽기 쉬운 형식으로 표시 (KB, MB, GB)

## 조합 예시

```bash
ls -lah
```

이 명령어는 숨김 파일을 포함한 모든 파일의 자세한 정보를 읽기 쉬운 형식으로 표시합니다.""",
            difficulty=DifficultyLevel.BEGINNER,
            category=["file-system", "basics"],
            publish_date=date.today(),
            terminal_setup={
                "files": [
                    {"path": "/home/user/example.txt", "content": "Hello World\n"},
                    {"path": "/home/user/.bashrc", "content": "# Bash configuration\n"},
                ],
                "directories": ["/home/user/Documents", "/home/user/Downloads"],
            },
            is_active=True,
        )

        # 어제의 팁 (중급)
        yesterday_tip = Tip(
            title="파이프(|)로 명령어 연결하기",
            content="""# 파이프를 사용한 명령어 연결

파이프(`|`)는 한 명령어의 출력을 다른 명령어의 입력으로 전달합니다.

## 예시 1: 파일 내용 검색

```bash
cat file.txt | grep "error"
```

`file.txt`의 내용 중 "error"가 포함된 줄만 표시합니다.

## 예시 2: 프로세스 찾기

```bash
ps aux | grep nginx
```

실행 중인 모든 프로세스 중 nginx와 관련된 것만 필터링합니다.

## 예시 3: 여러 파이프 연결

```bash
cat access.log | grep "404" | wc -l
```

로그 파일에서 404 에러가 몇 번 발생했는지 카운트합니다.""",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=["command-line", "piping"],
            publish_date=date.today() - timedelta(days=1),
            terminal_setup={
                "files": [
                    {
                        "path": "/home/user/file.txt",
                        "content": "This is a test\nerror: something went wrong\ninfo: all good\n",
                    },
                    {
                        "path": "/home/user/access.log",
                        "content": "GET /index.html 200\nGET /missing.html 404\nGET /about.html 200\nGET /notfound.html 404\n",
                    },
                ],
                "directories": [],
            },
            is_active=True,
        )

        # 2일 전 팁 (고급)
        two_days_ago_tip = Tip(
            title="find와 xargs로 파일 일괄 처리하기",
            content="""# find와 xargs를 조합한 고급 파일 처리

`find` 명령어로 파일을 찾고 `xargs`로 일괄 처리할 수 있습니다.

## 예시 1: 특정 확장자 파일 삭제

```bash
find . -name "*.tmp" -type f | xargs rm
```

현재 디렉토리 이하의 모든 `.tmp` 파일을 삭제합니다.

## 예시 2: 파일 내용 일괄 검색

```bash
find . -name "*.log" -type f | xargs grep "ERROR"
```

모든 `.log` 파일에서 "ERROR" 문자열을 검색합니다.

## 안전한 사용법 (-print0와 -0)

```bash
find . -name "*.txt" -type f -print0 | xargs -0 chmod 644
```

공백이 포함된 파일명도 안전하게 처리할 수 있습니다.""",
            difficulty=DifficultyLevel.ADVANCED,
            category=["file-system", "scripting", "automation"],
            publish_date=date.today() - timedelta(days=2),
            terminal_setup={
                "files": [
                    {"path": "/home/user/test1.tmp", "content": "temporary file 1\n"},
                    {"path": "/home/user/test2.tmp", "content": "temporary file 2\n"},
                    {"path": "/home/user/app.log", "content": "INFO: Starting\nERROR: Failed to connect\n"},
                    {"path": "/home/user/data.txt", "content": "Some data\n"},
                ],
                "directories": ["/home/user/backup"],
            },
            is_active=True,
        )

        # 3일 전 팁 (초급)
        three_days_ago_tip = Tip(
            title="cd 명령어로 디렉토리 이동하기",
            content="""# cd 명령어 사용법

`cd`(Change Directory)는 현재 작업 디렉토리를 변경합니다.

## 기본 사용법

```bash
cd /home/user/Documents
```

## 특수 디렉토리

- `cd ~`: 홈 디렉토리로 이동
- `cd ..`: 상위 디렉토리로 이동
- `cd -`: 이전 디렉토리로 돌아가기

## 예시

```bash
cd ~/Documents
cd ../Downloads
cd -
```""",
            difficulty=DifficultyLevel.BEGINNER,
            category=["navigation", "basics"],
            publish_date=date.today() - timedelta(days=3),
            terminal_setup={
                "files": [],
                "directories": [
                    "/home/user/Documents",
                    "/home/user/Downloads",
                    "/home/user/Pictures",
                ],
            },
            is_active=True,
        )

        # 4일 전 팁 (중급)
        four_days_ago_tip = Tip(
            title="grep으로 파일 내용 검색하기",
            content="""# grep 명령어 마스터하기

`grep`은 파일이나 출력에서 패턴을 검색하는 강력한 도구입니다.

## 기본 사용법

```bash
grep "search_term" file.txt
```

## 유용한 옵션

- `grep -i "term" file.txt`: 대소문자 구분 없이 검색
- `grep -r "term" /path`: 디렉토리 재귀 검색
- `grep -n "term" file.txt`: 줄 번호 표시
- `grep -v "term" file.txt`: 매칭되지 않는 줄만 표시

## 정규표현식 예시

```bash
grep "^ERROR" log.txt  # ERROR로 시작하는 줄
grep "[0-9]\\{3\\}" file.txt  # 3자리 숫자 찾기
```""",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=["search", "text-processing"],
            publish_date=date.today() - timedelta(days=4),
            terminal_setup={
                "files": [
                    {
                        "path": "/home/user/log.txt",
                        "content": "ERROR: Failed\nWARNING: Low memory\nINFO: Started\nERROR: Connection lost\n",
                    },
                    {"path": "/home/user/data.txt", "content": "User 123\nUser 456\nUser 789\n"},
                ],
                "directories": [],
            },
            is_active=True,
        )

        # 데이터 추가
        session.add_all(
            [today_tip, yesterday_tip, two_days_ago_tip, three_days_ago_tip, four_days_ago_tip]
        )
        await session.commit()

        print("✅ 테스트 팁 5개 추가 완료!")
        print(f"   - 오늘: {today_tip.title} (초급)")
        print(f"   - 어제: {yesterday_tip.title} (중급)")
        print(f"   - 2일 전: {two_days_ago_tip.title} (고급)")
        print(f"   - 3일 전: {three_days_ago_tip.title} (초급)")
        print(f"   - 4일 전: {four_days_ago_tip.title} (중급)")


if __name__ == "__main__":
    asyncio.run(add_test_tips())
