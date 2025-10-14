"""
Tip Pydantic 스키마 테스트

테스트 항목:
- TipBase, TipCreate, TipUpdate 필드 검증
- Pydantic validator 동작 (category 최대 5개, 중복 제거)
- terminal_setup 구조 검증
- from_attributes=True 동작 (ORM → Pydantic 변환)
- 필수 필드 및 선택적 필드 검증
"""

from datetime import date, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.tip import DifficultyLevel, Tip
from app.schemas.tip import TipCreate, TipInDB, TipUpdate, Tip as TipSchema


@pytest.mark.unit
class TestTipBaseSchema:
    """TipBase 스키마 기본 검증 테스트"""

    def test_tip_create_with_valid_data(self) -> None:
        """유효한 데이터로 TipCreate 생성"""
        data = {
            "title": "파일 검색하기",
            "content": "find 명령어를 사용하여 파일을 검색합니다. 최소 20자 이상.",
            "difficulty": DifficultyLevel.BEGINNER,
            "category": ["file-system", "search"],
            "terminal_setup": {"files": [], "directories": []},
        }
        tip = TipCreate(**data)

        assert tip.title == data["title"]
        assert tip.content == data["content"]
        assert tip.difficulty == data["difficulty"]
        assert tip.category == data["category"]

    def test_tip_create_title_too_short(self) -> None:
        """title이 5자 미만일 경우 검증 실패"""
        data = {
            "title": "짧음",  # 4자
            "content": "내용은 20자 이상이어야 합니다. 더 긴 내용을 작성합니다.",
        }
        with pytest.raises(ValidationError) as exc_info:
            TipCreate(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("title",) for e in errors)

    def test_tip_create_content_too_short(self) -> None:
        """content가 20자 미만일 경우 검증 실패"""
        data = {
            "title": "유효한 제목입니다",
            "content": "너무 짧음",  # 20자 미만
        }
        with pytest.raises(ValidationError) as exc_info:
            TipCreate(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("content",) for e in errors)

    def test_tip_create_default_values(self) -> None:
        """기본값 테스트"""
        data = {
            "title": "최소 필드만 있는 팁",
            "content": "필수 필드인 title과 content만 제공합니다. 최소 20자 이상.",
        }
        tip = TipCreate(**data)

        assert tip.difficulty == DifficultyLevel.BEGINNER
        assert tip.category == []
        assert tip.terminal_setup == {}
        assert tip.is_active is True


@pytest.mark.unit
class TestTipCategoryValidator:
    """category 필드 validator 테스트"""

    def test_category_duplicate_removal(self) -> None:
        """중복된 카테고리는 자동으로 제거됨"""
        data = {
            "title": "중복 카테고리 테스트",
            "content": "중복된 카테고리를 테스트합니다. 최소 20자 이상.",
            "category": ["file-system", "search", "file-system", "search"],
        }
        tip = TipCreate(**data)

        # 중복 제거됨 (set 변환 후 list로)
        assert len(tip.category) == 2
        assert "file-system" in tip.category
        assert "search" in tip.category

    def test_category_lowercase_normalization(self) -> None:
        """카테고리는 소문자로 정규화됨"""
        data = {
            "title": "카테고리 정규화 테스트",
            "content": "대소문자 혼용 카테고리를 테스트합니다. 최소 20자 이상.",
            "category": ["File-System", "SEARCH", "Permissions"],
        }
        tip = TipCreate(**data)

        # 모두 소문자로 변환됨
        assert all(cat.islower() for cat in tip.category)
        assert "file-system" in tip.category
        assert "search" in tip.category
        assert "permissions" in tip.category

    def test_category_whitespace_removal(self) -> None:
        """카테고리 앞뒤 공백은 제거됨"""
        data = {
            "title": "공백 제거 테스트",
            "content": "카테고리의 공백을 제거하는지 테스트합니다. 최소 20자 이상.",
            "category": ["  file-system  ", " search ", "permissions"],
        }
        tip = TipCreate(**data)

        assert "file-system" in tip.category
        assert "search" in tip.category
        assert all(" " not in cat for cat in tip.category)

    def test_category_max_5_items(self) -> None:
        """카테고리는 최대 5개까지만 허용"""
        data = {
            "title": "카테고리 개수 제한 테스트",
            "content": "카테고리 개수 제한을 테스트합니다. 최소 20자 이상.",
            "category": ["cat1", "cat2", "cat3", "cat4", "cat5", "cat6"],
        }
        with pytest.raises(ValidationError) as exc_info:
            TipCreate(**data)

        errors = exc_info.value.errors()
        assert any("최대 5개까지" in str(e["msg"]) for e in errors)

    def test_category_empty_strings_filtered(self) -> None:
        """빈 문자열 카테고리는 필터링됨"""
        data = {
            "title": "빈 카테고리 필터링 테스트",
            "content": "빈 문자열 카테고리를 필터링하는지 테스트합니다. 최소 20자.",
            "category": ["file-system", "", "  ", "search"],
        }
        tip = TipCreate(**data)

        assert len(tip.category) == 2
        assert "" not in tip.category


@pytest.mark.unit
class TestTipTerminalSetupValidator:
    """terminal_setup 필드 validator 테스트"""

    def test_terminal_setup_valid_structure(self) -> None:
        """유효한 terminal_setup 구조"""
        data = {
            "title": "터미널 설정 테스트",
            "content": "터미널 설정 구조를 검증합니다. 최소 20자 이상.",
            "terminal_setup": {
                "files": [
                    {"path": "/home/user/test.txt", "content": "Hello"},
                    {"path": "/home/user/script.sh", "content": "#!/bin/bash"},
                ],
                "directories": ["/home/user/logs", "/tmp/data"],
            },
        }
        tip = TipCreate(**data)

        assert len(tip.terminal_setup["files"]) == 2
        assert len(tip.terminal_setup["directories"]) == 2

    def test_terminal_setup_files_must_be_list(self) -> None:
        """files 필드는 배열이어야 함"""
        data = {
            "title": "files 타입 검증",
            "content": "files 필드의 타입을 검증합니다. 최소 20자 이상.",
            "terminal_setup": {"files": "not a list"},
        }
        with pytest.raises(ValidationError) as exc_info:
            TipCreate(**data)

        errors = exc_info.value.errors()
        assert any("배열이어야" in str(e["msg"]) for e in errors)

    def test_terminal_setup_file_must_have_path(self) -> None:
        """각 파일 객체는 path 필드를 가져야 함"""
        data = {
            "title": "파일 path 검증",
            "content": "파일 객체의 path 필드를 검증합니다. 최소 20자 이상.",
            "terminal_setup": {"files": [{"content": "no path field"}]},
        }
        with pytest.raises(ValidationError) as exc_info:
            TipCreate(**data)

        errors = exc_info.value.errors()
        assert any("path 필드가 필요" in str(e["msg"]) for e in errors)

    def test_terminal_setup_directories_must_be_list(self) -> None:
        """directories 필드는 배열이어야 함"""
        data = {
            "title": "directories 타입 검증",
            "content": "directories 필드의 타입을 검증합니다. 최소 20자 이상.",
            "terminal_setup": {"directories": "not a list"},
        }
        with pytest.raises(ValidationError) as exc_info:
            TipCreate(**data)

        errors = exc_info.value.errors()
        assert any("배열이어야" in str(e["msg"]) for e in errors)

    def test_terminal_setup_empty_is_valid(self) -> None:
        """빈 terminal_setup도 유효함"""
        data = {
            "title": "빈 터미널 설정 테스트",
            "content": "빈 터미널 설정도 허용되는지 테스트합니다. 최소 20자.",
            "terminal_setup": {},
        }
        tip = TipCreate(**data)

        assert tip.terminal_setup == {}


@pytest.mark.unit
class TestTipUpdateSchema:
    """TipUpdate 스키마 테스트 (모든 필드 Optional)"""

    def test_tip_update_all_fields_optional(self) -> None:
        """TipUpdate는 모든 필드가 선택적"""
        tip_update = TipUpdate()

        assert tip_update.title is None
        assert tip_update.content is None
        assert tip_update.difficulty is None
        assert tip_update.category is None

    def test_tip_update_partial_update(self) -> None:
        """일부 필드만 업데이트 가능"""
        data = {"title": "업데이트된 제목"}
        tip_update = TipUpdate(**data)

        assert tip_update.title == "업데이트된 제목"
        assert tip_update.content is None
        assert tip_update.difficulty is None

    def test_tip_update_category_validation(self) -> None:
        """TipUpdate의 category도 동일한 검증 적용"""
        data = {"category": ["cat1", "cat2", "cat3", "cat4", "cat5", "cat6"]}
        with pytest.raises(ValidationError) as exc_info:
            TipUpdate(**data)

        errors = exc_info.value.errors()
        assert any("최대 5개까지" in str(e["msg"]) for e in errors)


@pytest.mark.unit
class TestTipInDBSchema:
    """TipInDB 스키마 테스트 (ORM 변환)"""

    def test_tip_indb_from_orm(self, tip_instance: Tip) -> None:
        """SQLAlchemy ORM 모델에서 Pydantic 스키마로 변환"""
        tip_schema = TipInDB.model_validate(tip_instance)

        assert tip_schema.id == tip_instance.id
        assert tip_schema.title == tip_instance.title
        assert tip_schema.content == tip_instance.content
        assert tip_schema.difficulty == tip_instance.difficulty
        assert tip_schema.category == tip_instance.category
        assert tip_schema.view_count == tip_instance.view_count
        assert tip_schema.is_active == tip_instance.is_active

    def test_tip_indb_all_required_fields(self) -> None:
        """TipInDB는 모든 필드가 필수"""
        with pytest.raises(ValidationError):
            TipInDB(title="제목만")

    def test_tip_indb_model_dump(self, tip_instance: Tip) -> None:
        """TipInDB를 dict로 직렬화"""
        tip_schema = TipInDB.model_validate(tip_instance)
        data = tip_schema.model_dump()

        assert isinstance(data, dict)
        assert data["id"] == tip_instance.id
        assert data["title"] == tip_instance.title
        assert isinstance(data["created_at"], datetime)


@pytest.mark.unit
class TestTipResponseSchema:
    """Tip 응답 스키마 테스트"""

    def test_tip_response_from_orm(self, tip_instance: Tip) -> None:
        """ORM 모델에서 응답 스키마로 변환"""
        tip_schema = TipSchema.model_validate(tip_instance)

        assert tip_schema.id == tip_instance.id
        assert tip_schema.title == tip_instance.title
        assert tip_schema.content == tip_instance.content

    def test_tip_response_json_serialization(self, tip_instance: Tip) -> None:
        """JSON 직렬화 테스트"""
        tip_schema = TipSchema.model_validate(tip_instance)
        json_data = tip_schema.model_dump_json()

        assert isinstance(json_data, str)
        assert tip_instance.id in json_data
        assert tip_instance.title in json_data
