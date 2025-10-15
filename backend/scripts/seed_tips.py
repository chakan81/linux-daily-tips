#!/usr/bin/env python3
"""
Test Data Seeding Script for Linux Daily Tips

이 스크립트는 개발 및 테스트를 위한 7일치 팁 데이터를 데이터베이스에 삽입합니다.
"""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config.settings import get_settings
from app.models.tip import Tip, DifficultyLevel


async def seed_tips():
    """7일치 테스트 팁 데이터를 데이터베이스에 삽입합니다."""

    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=True)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # 7일치 팁 데이터 (오늘부터 과거 6일)
    tips_data = [
        {
            "title": "ls 명령어로 파일 목록 보기",
            "content": """ls 명령어는 디렉토리의 파일 목록을 보여주는 가장 기본적인 명령어입니다.

기본 사용법:
```bash
ls              # 현재 디렉토리의 파일 목록
ls -l           # 상세 정보와 함께 보기
ls -a           # 숨김 파일(.으로 시작)도 보기
ls -lh          # 파일 크기를 사람이 읽기 쉬운 형태로 (K, M, G)
ls -lt          # 수정 시간 순으로 정렬
```

유용한 조합:
```bash
ls -lah         # 숨김 파일 포함, 상세 정보, 읽기 쉬운 크기
ls -ltr         # 오래된 파일부터 보기 (시간 역순)
```""",
            "difficulty": DifficultyLevel.BEGINNER,
            "category": ["file-system", "basics"],
            "publish_date": date.today() - timedelta(days=6),
            "terminal_setup": {
                "files": [
                    {"path": "/home/user/documents/report.txt", "content": "Annual Report 2024"},
                    {"path": "/home/user/documents/data.csv", "content": "id,name\n1,Alice\n2,Bob"},
                    {"path": "/home/user/.bashrc", "content": "# Bash configuration"},
                ],
                "directories": ["/home/user/documents", "/home/user/downloads"]
            }
        },
        {
            "title": "cd 명령어로 디렉토리 이동하기",
            "content": """cd (Change Directory) 명령어는 작업 디렉토리를 변경하는 명령어입니다.

기본 사용법:
```bash
cd /path/to/directory    # 절대 경로로 이동
cd documents             # 상대 경로로 이동
cd ..                    # 상위 디렉토리로 이동
cd ~                     # 홈 디렉토리로 이동
cd -                     # 이전 디렉토리로 이동
```

실용 팁:
```bash
cd                       # 인수 없이 실행하면 홈으로 이동
cd ~/Documents           # 홈의 하위 디렉토리로 이동
cd ../../                # 두 단계 상위로 이동
```""",
            "difficulty": DifficultyLevel.BEGINNER,
            "category": ["file-system", "basics", "navigation"],
            "publish_date": date.today() - timedelta(days=5),
            "terminal_setup": {
                "directories": [
                    "/home/user/projects/web",
                    "/home/user/projects/mobile",
                    "/home/user/documents"
                ]
            }
        },
        {
            "title": "grep으로 텍스트 검색하기",
            "content": """grep은 파일 내용이나 출력에서 패턴을 검색하는 강력한 도구입니다.

기본 사용법:
```bash
grep "검색어" file.txt           # 파일에서 검색
grep -i "검색어" file.txt        # 대소문자 구분 없이 검색
grep -r "검색어" directory/      # 디렉토리 재귀 검색
grep -n "검색어" file.txt        # 줄 번호와 함께 표시
grep -v "검색어" file.txt        # 일치하지 않는 줄 표시
```

파이프와 함께 사용:
```bash
ps aux | grep python             # 실행 중인 Python 프로세스 찾기
cat log.txt | grep ERROR         # 로그에서 에러 찾기
ls -la | grep "txt"              # txt 파일만 필터링
```""",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "category": ["text-processing", "search"],
            "publish_date": date.today() - timedelta(days=4),
            "terminal_setup": {
                "files": [
                    {"path": "/home/user/logs/app.log", "content": "INFO: Application started\nERROR: Connection failed\nWARNING: Retry attempt 1\nERROR: Connection timeout"},
                    {"path": "/home/user/config.txt", "content": "database=localhost\nport=5432\nusername=admin"},
                ],
                "directories": ["/home/user/logs"]
            }
        },
        {
            "title": "파이프(|)로 명령어 연결하기",
            "content": """파이프(|)는 한 명령어의 출력을 다른 명령어의 입력으로 전달합니다.

기본 개념:
```bash
command1 | command2              # command1의 출력 → command2의 입력
```

실용 예제:
```bash
# 파일 개수 세기
ls | wc -l

# 가장 큰 파일 찾기
ls -lh | sort -k5 -h | tail -5

# 로그에서 에러 개수 세기
cat app.log | grep ERROR | wc -l

# 중복 제거하고 정렬
cat names.txt | sort | uniq

# 실행 중인 프로세스 검색
ps aux | grep python | grep -v grep
```

여러 파이프 연결:
```bash
cat file.txt | grep "pattern" | sort | uniq -c | sort -nr
```""",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "category": ["shell", "text-processing", "piping"],
            "publish_date": date.today() - timedelta(days=3),
            "terminal_setup": {
                "files": [
                    {"path": "/home/user/names.txt", "content": "Alice\nBob\nAlice\nCharlie\nBob\nDavid"},
                    {"path": "/home/user/numbers.txt", "content": "5\n2\n9\n1\n7\n3"},
                ]
            }
        },
        {
            "title": "find로 파일 찾기",
            "content": """find 명령어는 파일 시스템에서 조건에 맞는 파일을 찾습니다.

기본 사용법:
```bash
find /path -name "filename"      # 이름으로 찾기
find . -name "*.txt"             # 현재 디렉토리에서 txt 파일 찾기
find . -type f                   # 파일만 찾기
find . -type d                   # 디렉토리만 찾기
```

고급 검색:
```bash
# 크기로 찾기
find . -size +10M                # 10MB 이상 파일
find . -size -1k                 # 1KB 미만 파일

# 수정 시간으로 찾기
find . -mtime -7                 # 7일 이내 수정된 파일
find . -mtime +30                # 30일 이전 수정된 파일

# 권한으로 찾기
find . -perm 644                 # 특정 권한의 파일

# 찾은 파일에 명령 실행
find . -name "*.log" -exec rm {} \\;
find . -type f -exec chmod 644 {} \\;
```""",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "category": ["file-system", "search"],
            "publish_date": date.today() - timedelta(days=2),
            "terminal_setup": {
                "files": [
                    {"path": "/home/user/documents/report.txt", "content": "Report"},
                    {"path": "/home/user/documents/data.csv", "content": "Data"},
                    {"path": "/home/user/projects/README.md", "content": "# Project"},
                ],
                "directories": ["/home/user/documents", "/home/user/projects"]
            }
        },
        {
            "title": "chmod로 파일 권한 변경하기",
            "content": """chmod는 파일과 디렉토리의 접근 권한을 변경합니다.

권한의 의미:
- r (read, 4): 읽기 권한
- w (write, 2): 쓰기 권한
- x (execute, 1): 실행 권한

숫자 모드:
```bash
chmod 644 file.txt               # rw-r--r-- (소유자: 읽기+쓰기, 그룹: 읽기, 기타: 읽기)
chmod 755 script.sh              # rwxr-xr-x (소유자: 모두, 그룹: 읽기+실행, 기타: 읽기+실행)
chmod 600 secret.key             # rw------- (소유자만 읽기+쓰기)
chmod 777 public.sh              # rwxrwxrwx (모두 모든 권한)
```

문자 모드:
```bash
chmod u+x script.sh              # 소유자에게 실행 권한 추가
chmod g-w file.txt               # 그룹의 쓰기 권한 제거
chmod o+r document.txt           # 기타 사용자에게 읽기 권한 추가
chmod a+x program                # 모두에게 실행 권한 추가
```

재귀 적용:
```bash
chmod -R 755 directory/          # 디렉토리와 모든 하위 항목에 적용
```""",
            "difficulty": DifficultyLevel.ADVANCED,
            "category": ["file-system", "permissions", "security"],
            "publish_date": date.today() - timedelta(days=1),
            "terminal_setup": {
                "files": [
                    {"path": "/home/user/script.sh", "content": "#!/bin/bash\necho 'Hello World'"},
                    {"path": "/home/user/data.txt", "content": "Sample data"},
                ]
            }
        },
        {
            "title": "tar로 파일 압축 및 해제하기",
            "content": """tar는 여러 파일을 하나로 묶고 압축하는 도구입니다.

압축하기:
```bash
tar -czf archive.tar.gz directory/     # gzip으로 압축
tar -cjf archive.tar.bz2 directory/    # bzip2로 압축
tar -cJf archive.tar.xz directory/     # xz로 압축
```

압축 해제하기:
```bash
tar -xzf archive.tar.gz                # gzip 압축 해제
tar -xjf archive.tar.bz2               # bzip2 압축 해제
tar -xJf archive.tar.xz                # xz 압축 해제
tar -xzf archive.tar.gz -C /path       # 특정 디렉토리에 압축 해제
```

내용 확인:
```bash
tar -tzf archive.tar.gz                # 압축 파일 내용 보기
tar -tvzf archive.tar.gz               # 상세 정보와 함께 보기
```

옵션 설명:
- c: create (생성)
- x: extract (추출)
- z: gzip
- j: bzip2
- J: xz
- f: file (파일 지정)
- v: verbose (상세 출력)
- t: list (내용 보기)

실용 예제:
```bash
# 백업 생성
tar -czf backup_$(date +%Y%m%d).tar.gz /home/user/documents

# 특정 파일만 압축
tar -czf config.tar.gz config/*.conf

# 압축 해제 전 확인
tar -tzf archive.tar.gz | less
```""",
            "difficulty": DifficultyLevel.ADVANCED,
            "category": ["file-system", "compression", "backup"],
            "publish_date": date.today(),
            "terminal_setup": {
                "files": [
                    {"path": "/home/user/documents/file1.txt", "content": "File 1"},
                    {"path": "/home/user/documents/file2.txt", "content": "File 2"},
                    {"path": "/home/user/documents/file3.txt", "content": "File 3"},
                ],
                "directories": ["/home/user/documents", "/home/user/archives"]
            }
        },
    ]

    async with async_session_maker() as session:
        try:
            print(f"\n{'='*60}")
            print(f"Starting to seed {len(tips_data)} tips...")
            print(f"{'='*60}\n")

            for i, tip_data in enumerate(tips_data, 1):
                tip = Tip(**tip_data)
                session.add(tip)
                print(f"[{i}/{len(tips_data)}] Added: {tip.title}")
                print(f"  - Difficulty: {tip.difficulty.value}")
                print(f"  - Categories: {', '.join(tip.category)}")
                print(f"  - Publish Date: {tip.publish_date}")
                print()

            await session.commit()

            print(f"\n{'='*60}")
            print(f"✅ Successfully seeded {len(tips_data)} tips!")
            print(f"{'='*60}\n")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error while seeding tips: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║  Linux Daily Tips - Test Data Seeding Script            ║
║  This will create 7 sample tips in the database         ║
╚══════════════════════════════════════════════════════════╝
    """)

    asyncio.run(seed_tips())
