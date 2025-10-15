"""
Tips API 엔드포인트

일일 리눅스 팁을 제공하는 API 엔드포인트입니다.
Day 12에서 Mock 데이터를 실제 데이터베이스 연동으로 교체했습니다.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_async_session as get_db
from app.core.id_prefixes import IDPrefix
from app.core.ulid_helper import validate_id_type
from app.models.tip import DifficultyLevel
from app.schemas.tip import Tip, TipList
from app.services.tip_service import TipService

router = APIRouter()


@router.get("/daily", summary="오늘의 팁 조회", tags=["tips"], response_model=Tip)
async def get_daily_tip(db: AsyncSession = Depends(get_db)):
    """
    오늘의 일일 팁 조회

    메인 페이지에 표시될 오늘의 리눅스 팁을 반환합니다.

    Args:
        db: 데이터베이스 세션 (자동 주입)

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
        - 데이터베이스 연동 (Day 12)
    """
    tip = await TipService.get_daily_tip(db, date.today())
    if not tip:
        raise HTTPException(status_code=404, detail="오늘의 팁이 없습니다")

    # 조회수 증가
    await TipService.increment_view_count(db, tip.id)
    await db.commit()

    return tip


@router.get("/", summary="팁 목록 조회", tags=["tips"], response_model=TipList)
async def get_tips(
    skip: int = Query(0, ge=0, description="건너뛸 개수 (페이지네이션)"),
    limit: int = Query(10, ge=1, le=100, description="최대 개수 (1-100)"),
    difficulty: str | None = Query(
        None, description="난이도 필터 (beginner/intermediate/advanced)"
    ),
    category: str | None = Query(None, description="카테고리 필터"),
    db: AsyncSession = Depends(get_db),
):
    """
    팁 목록 조회

    필터링 및 페이지네이션을 지원하는 팁 목록을 반환합니다.

    Args:
        skip: 건너뛸 개수 (페이지네이션, 기본값: 0)
        limit: 최대 개수 (1-100, 기본값: 10)
        difficulty: 난이도 필터 (beginner/intermediate/advanced)
        category: 카테고리 필터 (예: "file-system")
        db: 데이터베이스 세션 (자동 주입)

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
        GET /api/v1/tips/?skip=0&limit=10&difficulty=beginner

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
        - 데이터베이스 연동 (Day 12)
        - 조회 시 view_count는 증가하지 않음 (목록 조회)
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

    # TipService로 팁 목록 조회
    tips, total = await TipService.get_tips(
        db, skip=skip, limit=limit, difficulty=difficulty_enum, category=category
    )

    # TipList 스키마로 반환
    return TipList(
        items=tips,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{tip_id}", summary="팁 상세 조회", tags=["tips"], response_model=Tip)
async def get_tip(
    tip_id: str = Path(
        ...,
        description="팁 ID (tip_xxxx 형식)",
        pattern="^tip_[0-9A-Z]{26}$",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 팁 상세 정보 조회

    팁 ID를 기반으로 상세 정보를 반환합니다.

    Args:
        tip_id: 팁 ID (tip_ 프리픽스 + 26자 ULID)
        db: 데이터베이스 세션 (자동 주입)

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
        - 데이터베이스 연동 (Day 12)
    """
    # ID 타입 검증
    if not validate_id_type(tip_id, IDPrefix.TIP):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tip ID format. Expected 'tip_' prefix, got: {tip_id}",
        )

    # TipService로 팁 조회 (404는 TipService에서 AppException으로 발생)
    tip = await TipService.get_tip_by_id(db, tip_id)

    # 조회수 증가
    await TipService.increment_view_count(db, tip.id)
    await db.commit()

    return tip


@router.get("/categories/list", summary="카테고리 목록 조회", tags=["tips"])
async def get_categories():
    """
    사용 가능한 카테고리 목록 조회

    팁 필터링에 사용할 수 있는 카테고리 목록을 반환합니다.

    Returns:
        dict: 카테고리 목록 및 각 카테고리별 팁 개수

    Example:
        ```
        GET /api/v1/tips/categories/list

        Response:
        {
            "categories": [
                {
                    "name": "file-system",
                    "display_name": "파일 시스템",
                    "count": 2
                },
                {
                    "name": "text-processing",
                    "display_name": "텍스트 처리",
                    "count": 2
                },
                ...
            ]
        }
        ```

    Note:
        - 인증 불필요
        - 현재는 Mock 데이터 반환 (향후 실제 DB 쿼리로 개선 예정)
        - PostgreSQL의 JSONB 집계 쿼리 필요 (jsonb_array_elements)
    """
    # TODO: 실제 DB 쿼리로 변경 (Day 14 이후)
    # SELECT DISTINCT jsonb_array_elements_text(category) as cat, COUNT(*)
    # FROM tips WHERE is_active = True GROUP BY cat
    #
    # 현재는 정적 Mock 데이터 반환
    categories = [
        {"name": "file-system", "display_name": "파일 시스템", "count": 0},
        {"name": "text-processing", "display_name": "텍스트 처리", "count": 0},
        {"name": "permissions", "display_name": "권한 관리", "count": 0},
        {"name": "networking", "display_name": "네트워킹", "count": 0},
        {"name": "process-management", "display_name": "프로세스 관리", "count": 0},
    ]

    return {"categories": categories}
