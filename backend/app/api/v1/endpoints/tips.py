"""
Tips API 엔드포인트 (Mock 데이터)

일일 리눅스 팁을 제공하는 API 엔드포인트입니다.
Day 10-11에서 실제 데이터베이스 연동으로 대체될 예정입니다.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

# Mock 데이터 (Day 10-11에서 데이터베이스로 대체)
MOCK_TIPS = [
    {
        "id": 1,
        "title": "ls 명령어 기본 사용법",
        "content": "ls는 디렉토리 내용을 나열합니다. ls -l로 상세 정보를, ls -a로 숨김 파일을 볼 수 있습니다.",
        "difficulty": "beginner",
        "category": "file-system",
        "published_date": "2025-10-14",
        "views": 150,
        "likes": 12,
    },
    {
        "id": 2,
        "title": "grep으로 텍스트 검색하기",
        "content": "grep 'pattern' file.txt로 파일에서 패턴을 검색합니다. -r 옵션으로 재귀 검색이 가능합니다.",
        "difficulty": "intermediate",
        "category": "text-processing",
        "published_date": "2025-10-13",
        "views": 230,
        "likes": 18,
    },
    {
        "id": 3,
        "title": "find 명령어로 파일 찾기",
        "content": "find /path -name 'filename'으로 파일을 검색합니다. -type, -mtime 등 다양한 옵션을 사용할 수 있습니다.",
        "difficulty": "intermediate",
        "category": "file-system",
        "published_date": "2025-10-12",
        "views": 180,
        "likes": 15,
    },
    {
        "id": 4,
        "title": "sed로 텍스트 치환하기",
        "content": "sed 's/old/new/g' file.txt로 파일의 텍스트를 치환합니다. -i 옵션으로 파일을 직접 수정할 수 있습니다.",
        "difficulty": "advanced",
        "category": "text-processing",
        "published_date": "2025-10-11",
        "views": 120,
        "likes": 10,
    },
    {
        "id": 5,
        "title": "chmod로 파일 권한 변경",
        "content": "chmod 755 file로 파일 권한을 변경합니다. rwx(읽기/쓰기/실행) 권한을 숫자로 표현할 수 있습니다.",
        "difficulty": "beginner",
        "category": "permissions",
        "published_date": "2025-10-10",
        "views": 200,
        "likes": 20,
    },
]

router = APIRouter()


@router.get("/daily", summary="오늘의 팁 조회", tags=["tips"])
async def get_daily_tip():
    """
    오늘의 일일 팁 조회

    메인 페이지에 표시될 오늘의 리눅스 팁을 반환합니다.

    Returns:
        dict: 오늘의 팁 정보
            - id: 팁 ID
            - title: 제목
            - content: 내용
            - difficulty: 난이도 (beginner/intermediate/advanced)
            - category: 카테고리
            - published_date: 게시일
            - views: 조회수
            - likes: 좋아요 수

    Example:
        ```
        GET /api/v1/tips/daily

        Response:
        {
            "id": 1,
            "title": "ls 명령어 기본 사용법",
            "content": "ls는 디렉토리 내용을 나열합니다...",
            "difficulty": "beginner",
            "category": "file-system",
            "published_date": "2025-10-14",
            "views": 150,
            "likes": 12
        }
        ```

    Note:
        - 인증 불필요
        - 현재는 Mock 데이터 반환
        - Day 10-11에서 실제 DB 쿼리로 변경 (today() 기준)
    """
    # Mock: 첫 번째 팁 반환
    return MOCK_TIPS[0]


@router.get("/", summary="팁 목록 조회", tags=["tips"])
async def get_tips(
    skip: int = Query(0, ge=0, description="건너뛸 개수 (페이지네이션)"),
    limit: int = Query(10, ge=1, le=100, description="최대 개수 (1-100)"),
    difficulty: Optional[str] = Query(
        None, description="난이도 필터 (beginner/intermediate/advanced)"
    ),
    category: Optional[str] = Query(None, description="카테고리 필터"),
):
    """
    팁 목록 조회

    필터링 및 페이지네이션을 지원하는 팁 목록을 반환합니다.

    Args:
        skip: 건너뛸 개수 (페이지네이션, 기본값: 0)
        limit: 최대 개수 (1-100, 기본값: 10)
        difficulty: 난이도 필터 (beginner/intermediate/advanced)
        category: 카테고리 필터

    Returns:
        dict: 팁 목록 및 메타데이터
            - total: 전체 팁 개수 (필터링 적용 후)
            - skip: 건너뛴 개수
            - limit: 최대 개수
            - items: 팁 목록

    Example:
        ```
        GET /api/v1/tips/?skip=0&limit=10&difficulty=beginner

        Response:
        {
            "total": 2,
            "skip": 0,
            "limit": 10,
            "items": [
                {
                    "id": 1,
                    "title": "ls 명령어 기본 사용법",
                    ...
                },
                {
                    "id": 5,
                    "title": "chmod로 파일 권한 변경",
                    ...
                }
            ]
        }
        ```

    Note:
        - 인증 불필요
        - Day 10-11에서 실제 DB 쿼리로 변경
    """
    tips = MOCK_TIPS

    # 난이도 필터링
    if difficulty:
        tips = [t for t in tips if t["difficulty"] == difficulty]

    # 카테고리 필터링
    if category:
        tips = [t for t in tips if t["category"] == category]

    # 페이지네이션
    paginated_tips = tips[skip : skip + limit]

    return {"total": len(tips), "skip": skip, "limit": limit, "items": paginated_tips}


@router.get("/{tip_id}", summary="팁 상세 조회", tags=["tips"])
async def get_tip(tip_id: int = Path(..., description="팁 ID", ge=1)):
    """
    특정 팁 상세 정보 조회

    팁 ID를 기반으로 상세 정보를 반환합니다.

    Args:
        tip_id: 팁 ID (1 이상)

    Returns:
        dict: 팁 상세 정보

    Raises:
        HTTPException: 팁을 찾을 수 없는 경우 404

    Example:
        ```
        GET /api/v1/tips/1

        Response:
        {
            "id": 1,
            "title": "ls 명령어 기본 사용법",
            "content": "ls는 디렉토리 내용을 나열합니다...",
            "difficulty": "beginner",
            "category": "file-system",
            "published_date": "2025-10-14",
            "views": 150,
            "likes": 12
        }
        ```

    Note:
        - 인증 불필요
        - 조회 시 views 카운트 증가 (Day 10-11에서 구현)
    """
    # Mock: ID로 팁 검색
    tip = next((t for t in MOCK_TIPS if t["id"] == tip_id), None)

    if not tip:
        raise HTTPException(
            status_code=404, detail=f"Tip with id {tip_id} not found"
        )

    # TODO: Day 10-11에서 조회수 증가 로직 추가
    # await db.execute(update(Tip).where(Tip.id == tip_id).values(views=Tip.views + 1))

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
        - Day 10-11에서 실제 DB 쿼리로 변경
    """
    # Mock: 카테고리 통계 계산
    category_counts = {}
    for tip in MOCK_TIPS:
        category = tip["category"]
        category_counts[category] = category_counts.get(category, 0) + 1

    categories = [
        {
            "name": cat,
            "display_name": cat.replace("-", " ").title(),
            "count": count,
        }
        for cat, count in category_counts.items()
    ]

    return {"categories": categories}
