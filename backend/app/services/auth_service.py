"""
Google OAuth 2.0 인증 서비스 (하위 호환성 레이어)

**중요**: 이 파일은 하위 호환성을 위해 유지됩니다.
실제 구현은 `app/services/auth/` 모듈로 분리되었습니다.

기존 코드:
    from app.services.auth_service import AuthService

는 계속 동작합니다.

새로운 코드에서는 다음과 같이 사용하세요:
    from app.services.auth import AuthService

모듈 구조:
    app/services/auth/
    ├── __init__.py              # AuthService (통합 인터페이스)
    ├── oauth_client.py          # Google OAuth HTTP 통신
    ├── session_manager.py       # Redis 세션 관리
    ├── oauth_state_validator.py # OAuth state 검증
    └── user_service.py          # 데이터베이스 사용자 관리
"""

# 하위 호환성: 기존 import 경로 유지
from app.services.auth import AuthService  # noqa: F401

__all__ = ["AuthService"]
