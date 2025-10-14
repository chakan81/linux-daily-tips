"""
데이터베이스 모델 패키지

SQLAlchemy 모델을 관리합니다.
모든 모델은 Base를 상속받아 생성됩니다.

Available Models:
- Tip: 승인된 일일 Linux 팁
- AdminUser: 관리자 사용자
- DraftWeek: LLM 생성 주간 드래프트
- DraftTip: 개별 드래프트 팁
- TerminalSession: 웹 터미널 세션
- AnalyticsEvent: 사용자 행동 분석 이벤트
"""

from app.db.base import Base
from app.models.analytics import AnalyticsEvent, EventType
from app.models.draft import DraftStatus, DraftTip, DraftWeek
from app.models.terminal import TerminalSession, TerminalStatus
from app.models.tip import DifficultyLevel, Tip
from app.models.user import AdminUser

__all__ = [
    # Base
    "Base",
    # Models
    "Tip",
    "AdminUser",
    "DraftWeek",
    "DraftTip",
    "TerminalSession",
    "AnalyticsEvent",
    # Enums
    "DifficultyLevel",
    "DraftStatus",
    "TerminalStatus",
    "EventType",
]
