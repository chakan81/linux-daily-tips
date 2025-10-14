"""
데이터베이스 세션 관리

SQLAlchemy 2.0 async 패턴을 사용하여 PostgreSQL 연결을 관리합니다.
- AsyncEngine: 비동기 데이터베이스 엔진
- AsyncSessionLocal: 비동기 세션 팩토리
- get_db(): FastAPI 의존성 주입용 세션 생성기
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings

# SQLAlchemy 2.0 비동기 엔진 생성
# - asyncpg 드라이버 사용 (postgresql+asyncpg://)
# - echo=True: SQL 쿼리 로깅 (개발 환경에서만 활성화)
# - pool_pre_ping: 연결 풀에서 연결을 가져오기 전에 유효성 검사
# - connect_args: 데이터베이스 연결 옵션
#   - search_path: 기본 스키마를 linux_tips로 설정
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 개발 환경에서만 SQL 로깅
    pool_pre_ping=True,  # 연결 재사용 전 유효성 검사
    pool_size=settings.MAX_CONNECTIONS_COUNT,  # 연결 풀 크기
    max_overflow=10,  # 최대 추가 연결 수
    connect_args={
        "server_settings": {
            "search_path": "linux_tips,public",  # 기본 스키마 설정
        }
    },
)

# 비동기 세션 팩토리 생성
# - class_: AsyncSession 사용
# - expire_on_commit=False: 커밋 후에도 객체 상태 유지
# - autocommit=False, autoflush=False: 명시적 트랜잭션 관리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 의존성 주입용 데이터베이스 세션 생성기

    각 요청마다 새로운 세션을 생성하고, 요청 완료 후 자동으로 닫습니다.
    트랜잭션 관리는 서비스 레이어에서 수동으로 처리합니다.

    Usage:
        ```python
        from fastapi import Depends
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.db import get_db

        @app.get("/tips")
        async def get_tips(db: AsyncSession = Depends(get_db)):
            # db 세션 사용
            result = await db.execute(select(Tip))
            return result.scalars().all()
        ```

    Yields:
        AsyncSession: 비동기 데이터베이스 세션

    Note:
        - FastAPI의 의존성 주입 시스템이 자동으로 세션을 닫습니다.
        - 예외 발생 시 자동으로 롤백됩니다.
        - 서비스 레이어에서 명시적으로 commit()을 호출해야 합니다.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
