"""
Tip Pydantic 스키마

API 요청/응답에 사용되는 Tip 데이터 검증 스키마입니다.
- TipBase: 공통 필드
- TipCreate: 생성 요청
- TipUpdate: 수정 요청
- TipInDB: 데이터베이스 내부 표현
- Tip: 응답 스키마 (클라이언트에 반환)
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.tip import DifficultyLevel


def to_camel(string: str) -> str:
    """
    snake_case 문자열을 camelCase로 변환합니다.

    프론트엔드(TypeScript)와 백엔드(Python) 간 네이밍 규칙 차이 해결용.

    Args:
        string: 변환할 snake_case 문자열

    Returns:
        camelCase로 변환된 문자열

    Examples:
        >>> to_camel("publish_date")
        'publishDate'
        >>> to_camel("view_count")
        'viewCount'
        >>> to_camel("created_at")
        'createdAt'
    """
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def validate_category_tags(categories: list[str] | None) -> list[str] | None:
    """
    카테고리 태그 검증 및 정규화 (공통 함수)

    - 소문자 변환 및 공백 제거
    - 중복 제거 (순서 유지)
    - 최대 5개 제한

    Args:
        categories: 카테고리 태그 리스트 (None 허용)

    Returns:
        list[str] | None: 정규화된 카테고리 리스트 또는 None

    Raises:
        ValueError: 카테고리가 5개를 초과하는 경우

    Example:
        >>> validate_category_tags(["File-System", "SEARCH", "file-system"])
        ['file-system', 'search']
    """
    if categories is None:
        return None

    # 소문자 변환 및 공백 제거
    normalized = [cat.strip().lower() for cat in categories if cat.strip()]

    # 순서를 유지하면서 중복 제거 (dict.fromkeys 사용)
    unique_categories = list(dict.fromkeys(normalized))

    # 최대 5개 카테고리 제한
    if len(unique_categories) > 5:
        raise ValueError("카테고리는 최대 5개까지 지정 가능합니다")

    return unique_categories


class TipBase(BaseModel):
    """
    Tip 공통 필드

    모든 Tip 스키마가 상속받는 베이스 클래스입니다.
    """

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="팁 제목 (5~255자)",
        examples=["파일 검색 마스터하기"],
    )

    content: str = Field(
        ...,
        min_length=20,
        description="팁 내용 (Markdown 형식)",
        examples=[
            "```bash\nfind . -name '*.log' -mtime -7\n```\n\n"
            "최근 7일 이내에 수정된 `.log` 파일을 모두 찾습니다."
        ],
    )

    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.BEGINNER,
        description="난이도 (beginner/intermediate/advanced)",
        examples=[DifficultyLevel.BEGINNER],
    )

    category: list[str] = Field(
        default_factory=list,
        description="카테고리 태그 배열",
        examples=[["file-system", "search"]],
    )

    terminal_setup: dict[str, Any] = Field(
        default_factory=dict,
        description="터미널 사전 구성 (files, directories)",
        examples=[
            {
                "files": [
                    {"path": "/home/user/test.txt", "content": "Hello World"}
                ],
                "directories": ["/home/user/logs"],
            }
        ],
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: list[str]) -> list[str]:
        """카테고리 태그 검증 및 정규화 (공통 함수 사용)"""
        result = validate_category_tags(v)
        return result if result is not None else []

    @field_validator("terminal_setup")
    @classmethod
    def validate_terminal_setup(cls, v: dict[str, Any]) -> dict[str, Any]:
        """터미널 설정 구조 검증"""
        if not v:
            return {}

        # files 필드 검증
        if "files" in v:
            if not isinstance(v["files"], list):
                raise ValueError("terminal_setup.files는 배열이어야 합니다")
            for file_obj in v["files"]:
                if not isinstance(file_obj, dict):
                    raise ValueError("각 파일은 객체여야 합니다")
                if "path" not in file_obj:
                    raise ValueError("파일 객체에는 path 필드가 필요합니다")

        # directories 필드 검증
        if "directories" in v:
            if not isinstance(v["directories"], list):
                raise ValueError("terminal_setup.directories는 배열이어야 합니다")

        return v


class TipCreate(TipBase):
    """
    Tip 생성 요청 스키마

    새로운 팁을 생성할 때 사용합니다.
    publish_date는 선택적으로 지정 가능 (기본값: 오늘)
    """

    publish_date: date | None = Field(
        default=None,
        description="게시 날짜 (미지정 시 오늘 날짜)",
        examples=["2024-01-15"],
    )

    is_active: bool = Field(
        default=True,
        description="활성화 여부",
    )


class TipUpdate(BaseModel):
    """
    Tip 수정 요청 스키마

    모든 필드가 선택적(Optional)이며, 제공된 필드만 업데이트됩니다.
    """

    title: str | None = Field(
        default=None,
        min_length=5,
        max_length=255,
        description="팁 제목",
    )

    content: str | None = Field(
        default=None,
        min_length=20,
        description="팁 내용",
    )

    difficulty: DifficultyLevel | None = Field(
        default=None,
        description="난이도",
    )

    category: list[str] | None = Field(
        default=None,
        description="카테고리 태그",
    )

    publish_date: date | None = Field(
        default=None,
        description="게시 날짜",
    )

    terminal_setup: dict[str, Any] | None = Field(
        default=None,
        description="터미널 사전 구성",
    )

    is_active: bool | None = Field(
        default=None,
        description="활성화 여부",
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: list[str] | None) -> list[str] | None:
        """카테고리 검증 (공통 함수 사용)"""
        return validate_category_tags(v)


class TipInDB(TipBase):
    """
    데이터베이스 내부 표현

    SQLAlchemy 모델과 직접 매핑되는 스키마입니다.
    모든 필드를 포함하며, 내부 처리용으로만 사용됩니다.
    """

    id: str = Field(
        ...,
        description="ULID 기반 ID (tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY)",
        examples=["tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY"],
    )

    publish_date: date = Field(
        ...,
        description="게시 날짜",
    )

    is_active: bool = Field(
        ...,
        description="활성화 여부",
    )

    view_count: int = Field(
        ...,
        ge=0,
        description="조회수",
    )

    created_at: datetime = Field(
        ...,
        description="생성 시각 (UTC)",
    )

    updated_at: datetime = Field(
        ...,
        description="수정 시각 (UTC)",
    )

    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemy 모델에서 직접 변환 허용
        alias_generator=to_camel,  # snake_case → camelCase 자동 변환
        populate_by_name=True,  # snake_case와 camelCase 둘 다 허용
        json_schema_extra={
            "example": {
                "id": "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
                "title": "파일 검색 마스터하기",
                "content": "```bash\nfind . -name '*.log'\n```",
                "difficulty": "beginner",
                "category": ["file-system", "search"],
                "publish_date": "2024-01-15",
                "terminal_setup": {
                    "files": [
                        {"path": "/home/user/test.log", "content": "log data"}
                    ]
                },
                "is_active": True,
                "view_count": 42,
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
            }
        },
    )


class Tip(TipInDB):
    """
    Tip 응답 스키마 (클라이언트 반환용)

    API 응답으로 클라이언트에게 반환되는 스키마입니다.
    TipInDB와 동일하지만, 향후 추가 필드나 계산된 필드를 포함할 수 있습니다.
    """

    pass


class TipList(BaseModel):
    """
    Tip 리스트 응답 스키마 (페이지네이션)

    여러 팁을 목록으로 반환할 때 사용합니다.
    """

    items: list[Tip] = Field(
        ...,
        description="팁 목록",
    )

    total: int = Field(
        ...,
        ge=0,
        description="전체 팁 개수",
    )

    page: int = Field(
        ...,
        ge=1,
        description="현재 페이지 번호",
    )

    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="페이지 크기",
    )

    model_config = ConfigDict(
        alias_generator=to_camel,  # snake_case → camelCase 자동 변환
        populate_by_name=True,  # snake_case와 camelCase 둘 다 허용
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY",
                        "title": "파일 검색하기",
                        "content": "find 명령어 사용법...",
                        "difficulty": "beginner",
                        "category": ["file-system"],
                        "publish_date": "2024-01-15",
                        "terminal_setup": {},
                        "is_active": True,
                        "view_count": 100,
                        "created_at": "2024-01-15T00:00:00Z",
                        "updated_at": "2024-01-15T00:00:00Z",
                    }
                ],
                "total": 50,
                "page": 1,
                "page_size": 10,
            }
        },
    )
