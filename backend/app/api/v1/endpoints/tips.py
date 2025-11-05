"""
Tips API 엔드포인트

일일 리눅스 팁을 제공하는 API 엔드포인트입니다.
Day 12에서 Mock 데이터를 실제 데이터베이스 연동으로 교체했습니다.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy import inspect, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_async_session as get_db
from app.core.dependencies import get_tip_service
from app.core.id_prefixes import IDPrefix
from app.core.rate_limit import limiter
from app.core.ulid_helper import validate_id_type
from app.models.tip import DifficultyLevel, Tip as TipModel
from app.schemas.tip import Tip, TipList
from app.services.tip import TipService

router = APIRouter()


@router.get("/daily", summary="오늘의 팁 조회", tags=["tips"], response_model=Tip)
@limiter.limit("10/minute")
async def get_daily_tip(
    request: Request,
    db: AsyncSession = Depends(get_db),
    service: TipService = Depends(get_tip_service),
):
    """
    오늘의 일일 팁 조회 (캐싱 적용)

    메인 페이지에 표시될 오늘의 리눅스 팁을 반환합니다.
    Redis 캐싱을 통해 성능을 최적화합니다.

    Args:
        db: 데이터베이스 세션 (자동 주입)
        service: TipService (캐싱 포함, 자동 주입)

    Returns:
        Tip: 오늘의 팁 정보
            - id: 팁 ID
            - title: 제목
            - content: 내용
            - difficulty: 난이도 (beginner/intermediate/advanced)
            - category: 카테고리 배열
            - publish_date: 게시일
            - view_count: 조회수
            - created_at: 생성 시각
            - updated_at: 수정 시각

    Raises:
        HTTPException:
            - 404: 오늘의 팁이 없는 경우

    Example:
        ```
        GET /api/v1/tips/daily

        Response:
        {
            "id": "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
            "title": "ls 명령어 기본 사용법",
            "content": "ls는 디렉토리 내용을 나열합니다...",
            "difficulty": "beginner",
            "category": ["file-system"],
            "publish_date": "2025-10-15",
            "view_count": 150,
            "created_at": "2025-10-15T00:00:00Z",
            "updated_at": "2025-10-15T00:00:00Z"
        }
        ```

    Note:
        - 인증 불필요
        - 조회 시 view_count 자동 증가
        - Redis 캐싱 (24시간 TTL)
        - 데이터베이스 연동 (Day 12)
    """
    tip_model = await service.get_daily_tip(db, date.today())
    if not tip_model:
        raise HTTPException(status_code=404, detail="오늘의 팁이 없습니다")

    # 조회수 증가 (Atomic increment to prevent race condition)
    # Note: 캐시에서 로드한 Tip 객체는 세션에 attach되지 않아 직접 SQL UPDATE 실행
    # RETURNING 절로 DB에서 실제 증가된 값을 받아와 정확성 보장
    stmt = (
        update(TipModel)
        .where(TipModel.id == tip_model.id)
        .values(view_count=TipModel.view_count + 1)
        .returning(TipModel.view_count)  # DB의 실제 업데이트 값 반환
    )
    result = await db.execute(stmt)
    updated_view_count = result.scalar()  # DB에서 증가된 실제 값
    await db.commit()

    # Pydantic 모델로 변환하여 응답
    # Note: from_attributes=True로 SQLAlchemy 모델을 직접 변환
    # DB의 실제 값으로 동기화하여 정확성 보장
    tip_model.view_count = updated_view_count
    return Tip.model_validate(tip_model, from_attributes=True)


@router.get("", summary="팁 목록 조회", tags=["tips"], response_model=TipList)
@limiter.limit("30/minute")
async def get_tips(
    request: Request,
    skip: int = Query(0, ge=0, description="건너뛸 개수 (페이지네이션)"),
    limit: int = Query(10, ge=1, le=100, description="최대 개수 (1-100)"),
    difficulty: str | None = Query(
        None, description="난이도 필터 (beginner/intermediate/advanced)"
    ),
    category: str | None = Query(None, description="카테고리 필터"),
    q: str | None = Query(None, description="검색 쿼리 (제목/내용)"),
    sort_by: str = Query("publish_date", description="정렬 필드 (publish_date/title)"),
    order: str = Query("desc", description="정렬 순서 (asc/desc)"),
    db: AsyncSession = Depends(get_db),
    service: TipService = Depends(get_tip_service),
):
    """
    팁 목록 조회 (캐싱 적용)

    필터링 및 페이지네이션을 지원하는 팁 목록을 반환합니다.
    Redis 캐싱을 통해 성능을 최적화합니다.

    Args:
        skip: 건너뛸 개수 (페이지네이션, 기본값: 0)
        limit: 최대 개수 (1-100, 기본값: 10)
        difficulty: 난이도 필터 (beginner/intermediate/advanced)
        category: 카테고리 필터 (예: "file-system")
        q: 검색 쿼리 (제목 또는 내용에서 검색, 대소문자 무시)
        sort_by: 정렬 필드 (publish_date 또는 title, 기본값: publish_date)
        order: 정렬 순서 (asc 또는 desc, 기본값: desc)
        db: 데이터베이스 세션 (자동 주입)
        service: TipService (캐싱 포함, 자동 주입)

    Returns:
        TipList: 팁 목록 및 페이지네이션 정보
            - items: 팁 목록
            - total: 전체 팁 개수 (필터링 적용 후)
            - page: 현재 페이지 번호
            - page_size: 페이지 크기

    Raises:
        HTTPException:
            - 400: 잘못된 difficulty 값

    Example:
        ```
        GET /api/v1/tips/?skip=0&limit=10&difficulty=beginner&q=파일&sort_by=title&order=asc

        Response:
        {
            "items": [
                {
                    "id": "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
                    "title": "ls 명령어 기본 사용법",
                    ...
                },
                {
                    "id": "tip_01JCAW0V1UBCDEFGHIJKLMNOPQ",
                    "title": "chmod로 파일 권한 변경",
                    ...
                }
            ],
            "total": 2,
            "page": 1,
            "page_size": 10
        }
        ```

    Note:
        - 인증 불필요
        - Redis 캐싱 (10분 TTL)
        - 데이터베이스 연동 (Day 12)
        - 조회 시 view_count는 증가하지 않음 (목록 조회)
        - 검색 시 제목과 내용 모두 검색 (ILIKE 사용, 대소문자 무시)
        - 잘못된 sort_by 필드 → 기본값(publish_date desc) 적용 (보안: SQL Injection 방지)
    """
    # difficulty 문자열을 Enum으로 변환
    difficulty_enum = None
    if difficulty:
        try:
            difficulty_enum = DifficultyLevel(difficulty.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid difficulty: {difficulty}"
            )

    # TipService로 팁 목록 조회 (캐싱 적용)
    tips, total = await service.get_tips(
        db,
        skip=skip,
        limit=limit,
        difficulty=difficulty_enum,
        category=category,
        search_query=q,
        sort_by=sort_by,
        order=order,
    )

    # TipList 스키마로 반환
    return TipList(
        items=tips,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{tip_id}", summary="팁 상세 조회", tags=["tips"], response_model=Tip)
@limiter.limit("20/minute")
async def get_tip(
    request: Request,
    tip_id: str = Path(
        ...,
        description="팁 ID (tip_xxxx 형식)",
        pattern="^tip_[0-9A-Z]{26}$",
    ),
    db: AsyncSession = Depends(get_db),
    service: TipService = Depends(get_tip_service),
):
    """
    특정 팁 상세 정보 조회 (캐싱 적용)

    팁 ID를 기반으로 상세 정보를 반환합니다.
    Redis 캐싱을 통해 성능을 최적화합니다.

    Args:
        tip_id: 팁 ID (tip_ 프리픽스 + 26자 ULID)
        db: 데이터베이스 세션 (자동 주입)
        service: TipService (캐싱 포함, 자동 주입)

    Returns:
        Tip: 팁 상세 정보

    Raises:
        HTTPException:
            - 400: ID 형식이 올바르지 않은 경우
            - 404: 팁을 찾을 수 없는 경우 (TipService에서 발생)

    Example:
        ```
        GET /api/v1/tips/tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY

        Response:
        {
            "id": "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
            "title": "ls 명령어 기본 사용법",
            "content": "ls는 디렉토리 내용을 나열합니다...",
            "difficulty": "beginner",
            "category": ["file-system"],
            "publish_date": "2025-10-15",
            "view_count": 151,
            "created_at": "2025-10-15T00:00:00Z",
            "updated_at": "2025-10-15T00:00:00Z"
        }
        ```

    Note:
        - 인증 불필요
        - ID 타입 검증 포함 (tip_ 프리픽스 확인)
        - 조회 시 view_count 자동 증가
        - Redis 캐싱 (1시간 TTL)
        - 데이터베이스 연동 (Day 12)
    """
    # ID 타입 검증
    if not validate_id_type(tip_id, IDPrefix.TIP):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tip ID format. Expected 'tip_' prefix, got: {tip_id}",
        )

    # TipService로 팁 조회 (캐싱 적용, 404는 TipService에서 AppException으로 발생)
    tip_model = await service.get_tip_by_id(db, tip_id)

    # 조회수 증가 (Atomic increment to prevent race condition)
    # Note: 캐시에서 로드한 Tip 객체는 세션에 attach되지 않아 직접 SQL UPDATE 실행
    # RETURNING 절로 DB에서 실제 증가된 값을 받아와 정확성 보장
    stmt = (
        update(TipModel)
        .where(TipModel.id == tip_id)
        .values(view_count=TipModel.view_count + 1)
        .returning(TipModel.view_count)  # DB의 실제 업데이트 값 반환
    )
    result = await db.execute(stmt)
    updated_view_count = result.scalar()  # DB에서 증가된 실제 값
    await db.commit()

    # Pydantic 모델로 변환하여 응답
    # Note: from_attributes=True로 SQLAlchemy 모델을 직접 변환
    # DB의 실제 값으로 동기화하여 정확성 보장
    tip_model.view_count = updated_view_count
    return Tip.model_validate(tip_model, from_attributes=True)


@router.get("/categories/list", summary="카테고리 목록 조회", tags=["tips"])
@limiter.limit("30/minute")
async def get_categories(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    사용 가능한 카테고리 목록 조회 (데이터베이스 기반)

    팁 필터링에 사용할 수 있는 카테고리 목록을 반환합니다.
    실제 데이터베이스에서 활성화된 팁의 고유 카테고리를 동적으로 추출합니다.

    Args:
        db: 데이터베이스 세션 (자동 주입)

    Returns:
        dict: 고유 카테고리 목록 (알파벳 순 정렬)

    Example:
        ```
        GET /api/v1/tips/categories/list

        Response:
        {
            "categories": [
                "basics",
                "file-system",
                "networking",
                "text-processing"
            ]
        }
        ```

    Note:
        - 인증 불필요
        - PostgreSQL unnest() 함수로 배열 전개
        - is_active=True 팁만 조회
        - DISTINCT + ORDER BY로 중복 제거 및 정렬
    """
    from sqlalchemy import func, select

    # PostgreSQL jsonb_array_elements_text()로 JSONB 배열 요소 추출
    # → DISTINCT로 중복 제거
    stmt = (
        select(func.jsonb_array_elements_text(TipModel.category).label("category"))
        .where(TipModel.is_active == True)  # noqa: E712
        .distinct()
        .order_by("category")
    )

    result = await db.execute(stmt)
    categories = [row[0] for row in result.fetchall()]

    return {"categories": categories}
