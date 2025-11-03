"""
Tip 서비스 모듈

TipService를 재export하여 backward compatibility를 보장합니다.

사용법:
    from app.services.tip import TipService
"""

from app.services.tip.tip_service import TipService

__all__ = ["TipService"]
