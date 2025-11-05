# Backend Tests

Linux Daily Tips 백엔드 SQLAlchemy ORM 모델과 Pydantic 스키마에 대한 포괄적인 pytest 테스트 스위트입니다.

## 테스트 구조

```
tests/
├── conftest.py              # 공통 fixture 및 테스트 설정
├── test_models/             # SQLAlchemy 모델 테스트
│   ├── test_tip.py          # Tip 모델 (24개 테스트)
│   ├── test_admin_user.py   # AdminUser 모델 (18개 테스트)
│   ├── test_draft.py        # DraftWeek, DraftTip 모델 (17개 테스트)
│   ├── test_terminal.py     # TerminalSession 모델 (17개 테스트)
│   └── test_analytics.py    # AnalyticsEvent 모델 (14개 테스트)
└── test_schemas/            # Pydantic 스키마 테스트
    ├── test_tip_schema.py   # Tip 스키마 (23개 테스트)
    └── test_user_schema.py  # User 스키마 (21개 테스트)
```

**전체 테스트 수**: 134개

## 테스트 대상

### 모델 테스트 (test_models/)

#### 1. Tip 모델 (`test_tip.py`)
- ULID + Prefix ID 자동 생성 (tip_...)
- TimestampMixin 동작 (created_at, updated_at)
- CRUD 기본 동작 (Create, Read, Update, Delete)
- DifficultyLevel Enum 검증 (beginner/intermediate/advanced)
- JSON 필드 (category, terminal_setup)
- Relationship (TerminalSession, AnalyticsEvent)
- Cascade 삭제 동작

#### 2. AdminUser 모델 (`test_admin_user.py`)
- ULID + Prefix ID 자동 생성 (user_...)
- Unique 제약조건 (username, email)
- Boolean 필드 (is_active, is_superuser)
- 비밀번호 해시 저장
- last_login 타임스탬프
- Relationship (DraftWeek - approver)

#### 3. Draft 모델 (`test_draft.py`)
- ULID + Prefix ID 자동 생성 (draft_...)
- DraftStatus Enum 검증 (draft/approved/rejected)
- DraftWeek ↔ DraftTip 1:N 관계
- DraftWeek ↔ AdminUser 관계 (approver)
- 승인 워크플로우 테스트
- Cascade 삭제 동작

#### 4. TerminalSession 모델 (`test_terminal.py`)
- ULID + Prefix ID 자동 생성 (session_...)
- TerminalStatus Enum 검증 (active/terminated/expired)
- IP 주소 저장 (INET 타입, IPv4/IPv6)
- JSON 필드 (session_data)
- 만료 시간 관리 (expires_at, is_expired, remaining_time)
- Tip과의 관계

#### 5. AnalyticsEvent 모델 (`test_analytics.py`)
- ULID + Prefix ID 자동 생성 (evt_...)
- event_type 문자열 타입
- EventType 상수 클래스 (tip_view, terminal_start 등)
- IP 주소 저장 (INET 타입)
- JSON 필드 (event_data)
- 익명 이벤트 (tip_id=None)

### 스키마 테스트 (test_schemas/)

#### 1. Tip 스키마 (`test_tip_schema.py`)
- TipCreate, TipUpdate 필드 검증
- 필수 필드 및 선택적 필드 검증
- Custom validator:
  - category: 최대 5개, 중복 제거, 소문자 정규화
  - terminal_setup: 구조 검증 (files, directories)
- from_attributes=True (ORM → Pydantic 변환)
- JSON 직렬화

#### 2. User 스키마 (`test_user_schema.py`)
- UserCreate, UserUpdate 필드 검증
- 비밀번호 강도 검증 (8자 이상, 대문자+소문자+숫자)
- 이메일 형식 검증 (EmailStr)
- username 패턴 검증 (영문/숫자/언더스코어/하이픈만)
- 보안: password_hash는 응답 스키마(User)에서 제외
- from_attributes=True (ORM → Pydantic 변환)

## 실행 방법

### 전체 테스트 실행
```bash
docker compose exec backend pytest tests/
```

### 특정 디렉토리 테스트
```bash
# 모델 테스트만 실행
docker compose exec backend pytest tests/test_models/

# 스키마 테스트만 실행
docker compose exec backend pytest tests/test_schemas/
```

### 특정 파일 테스트
```bash
docker compose exec backend pytest tests/test_models/test_tip.py -v
```

### 커버리지 포함 실행
```bash
docker compose exec backend pytest tests/ --cov=app --cov-report=html
```

커버리지 리포트는 `htmlcov/index.html`에서 확인 가능합니다.

### 테스트 마커 사용
```bash
# unit 테스트만 실행
docker compose exec backend pytest -m unit

# slow 테스트 제외
docker compose exec backend pytest -m "not slow"
```

## Fixtures

### conftest.py 주요 Fixtures

#### 데이터베이스 Fixtures
- `event_loop`: 세션 스코프 이벤트 루프
- `async_db_engine`: 테스트용 비동기 DB 엔진 (세션 스코프)
- `async_db_session`: 테스트용 비동기 DB 세션 (함수 스코프, 자동 rollback)

#### 샘플 데이터 Fixtures
- `sample_tip_data`: Tip 샘플 데이터 dict
- `sample_admin_user_data`: AdminUser 샘플 데이터 dict
- `sample_draft_week_data`: DraftWeek 샘플 데이터 dict
- `sample_draft_tip_data`: DraftTip 샘플 데이터 dict
- `sample_terminal_session_data`: TerminalSession 샘플 데이터 dict
- `sample_analytics_event_data`: AnalyticsEvent 샘플 데이터 dict

#### 모델 인스턴스 Fixtures
- `tip_instance`: DB에 저장된 Tip 인스턴스
- `admin_user_instance`: DB에 저장된 AdminUser 인스턴스
- `draft_week_instance`: DB에 저장된 DraftWeek 인스턴스
- `terminal_session_instance`: DB에 저장된 TerminalSession 인스턴스
- `analytics_event_instance`: DB에 저장된 AnalyticsEvent 인스턴스

## 주요 테스트 패턴

### 1. CRUD 테스트
```python
async def test_create_tip(async_db_session: AsyncSession) -> None:
    tip = Tip(title="테스트", content="내용")
    async_db_session.add(tip)
    await async_db_session.commit()
    assert tip.id.startswith("tip_")
```

### 2. Relationship 테스트
```python
async def test_tip_terminal_sessions_relationship(
    tip_instance: Tip, terminal_session_instance: TerminalSession
) -> None:
    await async_db_session.refresh(tip_instance, ["terminal_sessions"])
    assert len(tip_instance.terminal_sessions) == 1
```

### 3. Pydantic Validator 테스트
```python
def test_category_max_5_items() -> None:
    data = {"category": ["cat1", "cat2", "cat3", "cat4", "cat5", "cat6"]}
    with pytest.raises(ValidationError) as exc_info:
        TipCreate(**data)
    assert "최대 5개까지" in str(exc_info.value)
```

## 알려진 이슈

### PostgreSQL Enum 타입 문제
현재 PostgreSQL에 이미 생성된 Enum 타입(`difficulty_level`, `draft_status`, `terminal_status`)이
대문자 값("BEGINNER")으로 저장되어 있어 일부 테스트가 실패합니다.

**해결 방법**:
1. Alembic 마이그레이션으로 Enum 타입을 재생성
2. 또는 수동으로 Enum 타입 삭제 후 재생성:
```sql
DROP TYPE IF EXISTS linux_tips.difficulty_level CASCADE;
DROP TYPE IF EXISTS linux_tips.draft_status CASCADE;
DROP TYPE IF EXISTS linux_tips.terminal_status CASCADE;
```

## 개발 가이드

### 새 테스트 추가하기
1. 적절한 디렉토리에 테스트 파일 생성
2. `@pytest.mark.unit` 마커 추가
3. `conftest.py`의 fixture 활용
4. 테스트 함수명은 `test_`로 시작
5. 한국어 주석으로 테스트 의도 명시

### 테스트 작성 원칙
- **격리성**: 각 테스트는 독립적이어야 함
- **반복성**: 동일한 결과를 보장
- **명확성**: 테스트 이름만으로 의도 파악 가능
- **포괄성**: Happy path + Edge cases + Error cases

## 참고 자료
- [pytest 공식 문서](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic](https://docs.pydantic.dev/)
