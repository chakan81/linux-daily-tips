"""
Redis JSON 직렬화 모듈

datetime 객체를 포함한 Python 객체를 JSON으로 직렬화/역직렬화합니다.
"""

import json
from datetime import datetime
from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    """
    datetime 객체를 처리하는 커스텀 JSON 인코더

    datetime 객체를 ISO 8601 형식 문자열로 변환합니다.
    """

    def default(self, obj: Any) -> Any:
        """datetime 객체를 ISO 8601 문자열로 변환"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
