"""
ULID 생성 및 검증 헬퍼 함수

ULID (Universally Unique Lexicographically Sortable Identifier)는
UUID의 대안으로 다음과 같은 장점을 제공합니다:

- 시간순 정렬 가능 (앞 48비트가 타임스탬프)
- DB 인덱스 효율성 (순차 삽입으로 페이지 분할 최소화)
- URL-safe (Base32 인코딩)
- 충돌 방지 (80비트 무작위성)
- 대소문자 구분 (가독성 향상)

프리픽스 패턴과 결합하여 사용:
- tip_01HGW5BQMF7XKQH9V0PNHJ8W3M
- user_01HGW5CTNR8YKP3M4VNZJ2F5QX
"""

import re
from typing import Optional

from ulid import ULID

from app.core.id_prefixes import IDPrefix

# ULID 형식: 26자의 Base32 인코딩 문자열
ULID_PATTERN = re.compile(r"^[0-9A-Z]{26}$")

# 프리픽스 포함 ID 형식: prefix_ULID
PREFIXED_ID_PATTERN = re.compile(r"^([a-z]+)_([0-9A-Z]{26})$")


def generate_ulid() -> str:
    """
    새로운 ULID 생성

    Returns:
        str: 26자의 ULID 문자열 (예: "01HGW5BQMF7XKQH9V0PNHJ8W3M")

    Example:
        >>> ulid = generate_ulid()
        >>> len(ulid)
        26
        >>> ulid.isupper()  # Base32는 대문자만 사용
        True
    """
    return str(ULID())


def generate_id(prefix: str) -> str:
    """
    프리픽스가 포함된 ULID 생성

    Args:
        prefix: 엔티티 타입 프리픽스 (예: "tip", "user", "session")

    Returns:
        str: 프리픽스 + ULID 조합 (예: "tip_01HGW5BQMF7XKQH9V0PNHJ8W3M")

    Raises:
        ValueError: 유효하지 않은 프리픽스인 경우

    Example:
        >>> from app.core.id_prefixes import IDPrefix
        >>> tip_id = generate_id(IDPrefix.TIP)
        >>> tip_id.startswith("tip_")
        True
        >>> len(tip_id)  # "tip_" (4자) + ULID (26자) = 30자
        30
    """
    if not IDPrefix.is_valid_prefix(prefix):
        raise ValueError(
            f"Invalid prefix '{prefix}'. "
            f"Valid prefixes: {', '.join(IDPrefix.get_all_prefixes())}"
        )
    return f"{prefix}_{generate_ulid()}"


def parse_id(id_with_prefix: str) -> tuple[str, str]:
    """
    프리픽스 포함 ID를 프리픽스와 ULID로 분리

    Args:
        id_with_prefix: 프리픽스 포함 ID (예: "tip_01HGW5BQMF...")

    Returns:
        tuple[str, str]: (prefix, ulid) 튜플

    Raises:
        ValueError: ID 형식이 잘못된 경우

    Example:
        >>> prefix, ulid = parse_id("tip_01HGW5BQMF7XKQH9V0PNHJ8W3M")
        >>> prefix
        'tip'
        >>> len(ulid)
        26
    """
    match = PREFIXED_ID_PATTERN.match(id_with_prefix)
    if not match:
        raise ValueError(
            f"Invalid ID format: '{id_with_prefix}'. "
            f"Expected format: prefix_ULID (e.g., tip_01HGW5BQMF...)"
        )
    return match.group(1), match.group(2)


def validate_id_format(id_with_prefix: str) -> bool:
    """
    ID 형식이 유효한지 검증 (정규식 매칭만 수행)

    Args:
        id_with_prefix: 검증할 ID

    Returns:
        bool: 형식이 유효하면 True

    Example:
        >>> validate_id_format("tip_01HGW5BQMF7XKQH9V0PNHJ8W3M")
        True
        >>> validate_id_format("invalid_id")
        False
        >>> validate_id_format("tip_123")  # ULID 길이 부족
        False
    """
    return PREFIXED_ID_PATTERN.match(id_with_prefix) is not None


def validate_id_type(id_with_prefix: str, expected_prefix: str) -> bool:
    """
    ID의 프리픽스가 예상 타입과 일치하는지 검증

    Args:
        id_with_prefix: 검증할 ID
        expected_prefix: 예상되는 프리픽스 (예: "tip")

    Returns:
        bool: 프리픽스가 일치하면 True

    Example:
        >>> from app.core.id_prefixes import IDPrefix
        >>> validate_id_type("tip_01HGW5BQMF...", IDPrefix.TIP)
        True
        >>> validate_id_type("user_01HGW5BQMF...", IDPrefix.TIP)
        False
    """
    try:
        prefix, _ = parse_id(id_with_prefix)
        return prefix == expected_prefix
    except ValueError:
        return False


def extract_timestamp(id_with_prefix: str) -> Optional[int]:
    """
    ULID에서 타임스탬프 추출 (밀리초 단위 Unix timestamp)

    Args:
        id_with_prefix: 프리픽스 포함 ID

    Returns:
        Optional[int]: 타임스탬프 (밀리초) 또는 None (형식 오류 시)

    Example:
        >>> from datetime import datetime
        >>> timestamp_ms = extract_timestamp("tip_01HGW5BQMF7XKQH9V0PNHJ8W3M")
        >>> if timestamp_ms:
        ...     dt = datetime.fromtimestamp(timestamp_ms / 1000)
        ...     print(dt.year >= 2024)
        True
    """
    try:
        _, ulid_str = parse_id(id_with_prefix)
        ulid_obj = ULID.from_str(ulid_str)
        # timestamp는 초 단위 float, 밀리초로 변환
        return int(ulid_obj.timestamp * 1000)
    except (ValueError, AttributeError):
        return None


def get_id_info(id_with_prefix: str) -> dict[str, str | int | None]:
    """
    ID의 전체 정보를 딕셔너리로 반환 (디버깅용)

    Args:
        id_with_prefix: 프리픽스 포함 ID

    Returns:
        dict: ID 정보
            - prefix: 프리픽스
            - ulid: ULID 부분
            - timestamp_ms: 타임스탬프 (밀리초)
            - prefix_name: 프리픽스 변수 이름 (예: "TIP")
            - valid: 형식 유효성

    Example:
        >>> info = get_id_info("tip_01HGW5BQMF7XKQH9V0PNHJ8W3M")
        >>> info['prefix']
        'tip'
        >>> info['prefix_name']
        'TIP'
        >>> info['valid']
        True
    """
    info: dict[str, str | int | None] = {
        "prefix": None,
        "ulid": None,
        "timestamp_ms": None,
        "prefix_name": None,
        "valid": False,
    }

    try:
        prefix, ulid = parse_id(id_with_prefix)
        info["prefix"] = prefix
        info["ulid"] = ulid
        info["timestamp_ms"] = extract_timestamp(id_with_prefix)
        info["prefix_name"] = IDPrefix.get_prefix_name(prefix)
        info["valid"] = True
    except ValueError:
        pass

    return info


# 편의를 위한 엔티티별 ID 생성 함수
def generate_tip_id() -> str:
    """Tip 엔티티 ID 생성"""
    return generate_id(IDPrefix.TIP)


def generate_draft_id() -> str:
    """Draft 엔티티 ID 생성"""
    return generate_id(IDPrefix.DRAFT)


def generate_user_id() -> str:
    """User 엔티티 ID 생성"""
    return generate_id(IDPrefix.USER)


def generate_category_id() -> str:
    """Category 엔티티 ID 생성"""
    return generate_id(IDPrefix.CATEGORY)


def generate_session_id() -> str:
    """Terminal Session 엔티티 ID 생성"""
    return generate_id(IDPrefix.SESSION)
