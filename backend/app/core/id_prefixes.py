"""
ID 프리픽스 상수 정의

ULID + 프리픽스 패턴을 사용하여 각 엔티티를 명확히 구분합니다.
예시: tip_01HGW5BQMF7XKQH9V0PNHJ8W3M

이 패턴은 다음과 같은 장점을 제공합니다:
- 로그 및 디버깅 시 ID만으로 엔티티 타입 즉시 식별
- API 레벨에서 잘못된 ID 타입 사용 방지
- 관리자 대시보드에서 직관적인 데이터 탐색
- 프론트엔드에서 클라이언트 측 타입 체크 가능
"""


class IDPrefix:
    """
    모든 엔티티의 ID 프리픽스를 정의하는 중앙 집중식 클래스

    프리픽스 네이밍 규칙:
    - 소문자만 사용
    - 3-8자 권장 (너무 짧으면 불명확, 너무 길면 공간 낭비)
    - 단수형 사용 (tip, user, session 등)
    - 약어 사용 가능 (cat = category, evt = event)
    """

    # Phase 1: MVP 엔티티
    TIP = "tip"  # 일일 팁
    DRAFT = "draft"  # LLM 생성 드래프트 (일주일치 묶음)
    USER = "user"  # 사용자 (관리자)
    CATEGORY = "cat"  # 카테고리 (파일시스템, 네트워킹 등)
    SESSION = "session"  # 터미널 세션

    # Phase 2: 고급 기능 (미래 확장용)
    COMMENT = "cmt"  # 댓글 (Phase 2)
    EVENT = "evt"  # 분석 이벤트 (Phase 2)
    BOOKMARK = "bkmk"  # 북마크 (Phase 2)
    TAG = "tag"  # 태그 (Phase 2)

    # Phase 3: 수익화 및 고급 분석 (미래 확장용)
    CAMPAIGN = "camp"  # 광고 캠페인 (Phase 3)
    ANALYTICS = "anlt"  # 분석 레포트 (Phase 3)

    @classmethod
    def get_all_prefixes(cls) -> list[str]:
        """
        모든 프리픽스를 리스트로 반환

        Returns:
            list[str]: 모든 프리픽스 리스트
        """
        return [
            value
            for key, value in cls.__dict__.items()
            if not key.startswith("_") and isinstance(value, str) and key.isupper()
        ]

    @classmethod
    def is_valid_prefix(cls, prefix: str) -> bool:
        """
        프리픽스가 유효한지 검증

        Args:
            prefix: 검증할 프리픽스

        Returns:
            bool: 유효하면 True, 아니면 False
        """
        return prefix in cls.get_all_prefixes()

    @classmethod
    def get_prefix_name(cls, prefix: str) -> str | None:
        """
        프리픽스에 해당하는 변수 이름 반환

        Args:
            prefix: 프리픽스 (예: "tip")

        Returns:
            str | None: 변수 이름 (예: "TIP") 또는 None
        """
        for key, value in cls.__dict__.items():
            if not key.startswith("_") and value == prefix:
                return key
        return None
