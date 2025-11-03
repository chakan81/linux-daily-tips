# SQLAlchemy Models Usage Guide

Quick reference for using the database models in the Linux Daily Tips backend.

---

## 🔌 Database Session

### Getting a Session (FastAPI)
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db

@app.get("/tips")
async def get_tips(db: AsyncSession = Depends(get_db)):
    # Use db session here
    pass
```

### Manual Session (Scripts)
```python
from app.db import AsyncSessionLocal

async def my_function():
    async with AsyncSessionLocal() as session:
        # Use session
        await session.commit()  # Manual commit
```

---

## 📝 Create Operations

### Create a Tip
```python
from app.models import Tip, DifficultyLevel

tip = Tip(
    title="Find Large Files",
    content="```bash\nfind / -type f -size +100M\n```",
    difficulty=DifficultyLevel.INTERMEDIATE,
    category=["file-system", "disk-management"],
    terminal_setup={
        "files": [
            {"path": "/tmp/largefile.dat", "content": "...large data..."}
        ],
        "directories": ["/tmp/logs"]
    }
)

db.add(tip)
await db.commit()
await db.refresh(tip)  # Get generated ID and timestamps

print(tip.id)  # tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY
```

### Create an AdminUser
```python
from app.models import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user = AdminUser(
    username="admin",
    email="admin@example.com",
    password_hash=pwd_context.hash("SecurePassword123!"),
    is_superuser=True
)

db.add(user)
await db.commit()
await db.refresh(user)
```

### Create a DraftWeek with Tips
```python
from app.models import DraftWeek, DraftTip, DraftStatus, DifficultyLevel
from datetime import date

draft_week = DraftWeek(
    week_start_date=date(2024, 1, 1),
    status=DraftStatus.DRAFT,
    generated_by="gpt-4"
)
db.add(draft_week)
await db.commit()
await db.refresh(draft_week)

# Add 7 draft tips
for day in range(1, 8):
    draft_tip = DraftTip(
        draft_week_id=draft_week.id,
        day_of_week=day,
        title=f"Tip for Day {day}",
        content=f"Content for day {day}",
        difficulty=DifficultyLevel.BEGINNER,  # ✅ Enum 사용 (리팩토링 수정)
        category=["basics"],
        llm_confidence_score=0.95
    )
    db.add(draft_tip)

await db.commit()
```

---

## 🔍 Read Operations

### Get Daily Tip
```python
from sqlalchemy import select
from app.models import Tip
from datetime import date

stmt = select(Tip).where(
    Tip.publish_date == date.today(),
    Tip.is_active == True
).limit(1)

result = await db.execute(stmt)
daily_tip = result.scalar_one_or_none()

if daily_tip:
    print(daily_tip.title)
```

### Get All Tips (Paginated)
```python
from sqlalchemy import select, func
from app.models import Tip

# Count total
count_stmt = select(func.count()).select_from(Tip).where(Tip.is_active == True)
total = await db.scalar(count_stmt)

# Get page
page = 1
page_size = 10
offset = (page - 1) * page_size

stmt = select(Tip).where(
    Tip.is_active == True
).order_by(
    Tip.publish_date.desc()
).offset(offset).limit(page_size)

result = await db.execute(stmt)
tips = result.scalars().all()

print(f"Page {page} of {total // page_size + 1}")
for tip in tips:
    print(f"- {tip.title}")
```

### Get Tip with Relationships
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Tip

stmt = select(Tip).where(
    Tip.id == "tip_01JCAW0V1QQ9KZ2F3XHBP8TGNY"
).options(
    selectinload(Tip.terminal_sessions),
    selectinload(Tip.analytics_events)
)

result = await db.execute(stmt)
tip = result.scalar_one_or_none()

if tip:
    print(f"Tip: {tip.title}")
    print(f"Active sessions: {len(tip.terminal_sessions)}")
    print(f"Total events: {len(tip.analytics_events)}")
```

### Search Tips by Category
```python
from sqlalchemy import select
from app.models import Tip

# JSONB array contains check
stmt = select(Tip).where(
    Tip.category.contains(["file-system"])
)

result = await db.execute(stmt)
tips = result.scalars().all()
```

### Get User by Email
```python
from sqlalchemy import select
from app.models import AdminUser

stmt = select(AdminUser).where(AdminUser.email == "admin@example.com")
result = await db.execute(stmt)
user = result.scalar_one_or_none()
```

---

## ✏️ Update Operations

### Update a Tip
```python
from sqlalchemy import select, update
from app.models import Tip

# Method 1: Fetch and update
stmt = select(Tip).where(Tip.id == "tip_01JCAW0V...")
result = await db.execute(stmt)
tip = result.scalar_one()

tip.title = "Updated Title"
tip.view_count += 1
await db.commit()

# Method 2: Direct update (faster, no fetch)
stmt = update(Tip).where(
    Tip.id == "tip_01JCAW0V..."
).values(
    view_count=Tip.view_count + 1
)
await db.execute(stmt)
await db.commit()
```

### Approve a DraftWeek
```python
from sqlalchemy import select, update
from app.models import DraftWeek, DraftStatus
from datetime import datetime, timezone

stmt = update(DraftWeek).where(
    DraftWeek.id == "draft_01JCAW0V..."
).values(
    status=DraftStatus.APPROVED,
    approved_by="user_01JCAW0V...",
    approved_at=datetime.now(timezone.utc),
    approval_notes="Looks good!"
)

await db.execute(stmt)
await db.commit()
```

---

## 🗑️ Delete Operations

### Delete a Tip (Cascade)
```python
from sqlalchemy import delete
from app.models import Tip

stmt = delete(Tip).where(Tip.id == "tip_01JCAW0V...")
await db.execute(stmt)
await db.commit()

# Cascade behavior:
# - Related terminal_sessions: CASCADE (완전 삭제)
# - Related analytics_events: SET NULL (이벤트는 보존, tip_id만 NULL)
```

### Soft Delete (Deactivate)
```python
from sqlalchemy import update
from app.models import Tip

stmt = update(Tip).where(
    Tip.id == "tip_01JCAW0V..."
).values(is_active=False)

await db.execute(stmt)
await db.commit()
```

---

## 📊 Analytics Operations

### Track Tip View
```python
from app.models import AnalyticsEvent
from ipaddress import IPv4Address

event = AnalyticsEvent(
    event_type="tip_view",
    tip_id="tip_01JCAW0V...",
    ip_address=IPv4Address("192.168.1.1"),
    user_agent="Mozilla/5.0...",
    event_data={
        "referrer": "https://google.com",
        "device": "mobile"
    }
)

db.add(event)
await db.commit()
```

### Get Tip View Count
```python
from sqlalchemy import select, func
from app.models import AnalyticsEvent

stmt = select(func.count()).select_from(AnalyticsEvent).where(
    AnalyticsEvent.tip_id == "tip_01JCAW0V...",
    AnalyticsEvent.event_type == "tip_view"
)

view_count = await db.scalar(stmt)
print(f"Views: {view_count}")
```

---

## 🖥️ Terminal Session Operations

### Create Terminal Session
```python
from app.models import TerminalSession, TerminalStatus
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address

session = TerminalSession(
    tip_id="tip_01JCAW0V...",
    container_id="abc123def456",
    status=TerminalStatus.ACTIVE,
    ip_address=IPv4Address("192.168.1.1"),
    user_agent="Mozilla/5.0...",
    session_data={"terminal_size": {"rows": 24, "cols": 80}},
    expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)
)

db.add(session)
await db.commit()
await db.refresh(session)

print(f"Session ID: {session.id}")
print(f"Expires in: {session.remaining_time}")
```

### Terminate Session
```python
from sqlalchemy import update
from app.models import TerminalSession, TerminalStatus
from datetime import datetime, timezone

stmt = update(TerminalSession).where(
    TerminalSession.id == "session_01JCAW0V..."
).values(
    status=TerminalStatus.TERMINATED,
    terminated_at=datetime.now(timezone.utc)
)

await db.execute(stmt)
await db.commit()
```

### Cleanup Expired Sessions
```python
from sqlalchemy import select, update
from app.models import TerminalSession, TerminalStatus
from datetime import datetime, timezone

stmt = update(TerminalSession).where(
    TerminalSession.status == TerminalStatus.ACTIVE,
    TerminalSession.expires_at < datetime.now(timezone.utc)
).values(
    status=TerminalStatus.EXPIRED,
    terminated_at=datetime.now(timezone.utc)
)

result = await db.execute(stmt)
await db.commit()

print(f"Expired {result.rowcount} sessions")
```

---

## 🔐 Authentication Operations

### Verify Password
```python
from passlib.context import CryptContext
from sqlalchemy import select
from app.models import AdminUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get user by username or email
stmt = select(AdminUser).where(
    (AdminUser.username == "admin") | (AdminUser.email == "admin@example.com")
)
result = await db.execute(stmt)
user = result.scalar_one_or_none()

if user and pwd_context.verify("password123", user.password_hash):
    print("Login successful!")

    # Update last_login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
else:
    print("Invalid credentials")
```

---

## 📈 Advanced Queries

### Get Most Viewed Tips
```python
from sqlalchemy import select
from app.models import Tip

stmt = select(Tip).where(
    Tip.is_active == True
).order_by(
    Tip.view_count.desc()
).limit(10)

result = await db.execute(stmt)
top_tips = result.scalars().all()

for i, tip in enumerate(top_tips, 1):
    print(f"{i}. {tip.title} ({tip.view_count} views)")
```

### Get Tips by Difficulty and Category
```python
from sqlalchemy import select
from app.models import Tip, DifficultyLevel

stmt = select(Tip).where(
    Tip.difficulty == DifficultyLevel.BEGINNER,
    Tip.category.contains(["file-system"]),
    Tip.is_active == True
).order_by(Tip.publish_date.desc())

result = await db.execute(stmt)
tips = result.scalars().all()
```

### Get Draft Weeks Pending Approval
```python
from sqlalchemy import select
from app.models import DraftWeek, DraftStatus

stmt = select(DraftWeek).where(
    DraftWeek.status == DraftStatus.DRAFT
).order_by(DraftWeek.created_at.desc())

result = await db.execute(stmt)
pending_drafts = result.scalars().all()

for draft in pending_drafts:
    print(f"Week {draft.week_start_date}: {len(draft.draft_tips)} tips")
```

---

## 🛡️ Transaction Management

### Manual Transaction
```python
async with db.begin():
    # All operations in this block are in one transaction
    tip = Tip(title="...", content="...")
    db.add(tip)

    event = AnalyticsEvent(tip_id=tip.id, event_type="tip_created")
    db.add(event)

    # Auto-commit on exit, auto-rollback on exception
```

### Rollback on Error
```python
try:
    tip = Tip(title="...", content="...")
    db.add(tip)
    await db.commit()
except Exception as e:
    await db.rollback()
    print(f"Error: {e}")
    raise
```

---

## ⚠️ Error Handling (리팩토링 추가)

### Using AppException
```python
from app.core.exceptions import AppException
from sqlalchemy import select
from app.models import Tip

async def get_tip_or_fail(db: AsyncSession, tip_id: str) -> Tip:
    """Tip 조회, 없으면 예외 발생"""
    stmt = select(Tip).where(Tip.id == tip_id)
    result = await db.execute(stmt)
    tip = result.scalar_one_or_none()

    if not tip:
        raise AppException(
            message=f"Tip with id {tip_id} not found",
            status_code=404
        )

    return tip
```

### SQLAlchemy Error Handling
```python
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)

try:
    # Database operation
    tip = Tip(title="...", content="...")
    db.add(tip)
    await db.commit()
except IntegrityError as e:
    await db.rollback()
    logger.error(f"Integrity constraint violation: {e}")
    raise AppException(
        message="Duplicate entry or constraint violation",
        status_code=409
    )
except SQLAlchemyError as e:
    await db.rollback()
    logger.error(f"Database error: {e}", exc_info=True)
    raise AppException(
        message="Database operation failed",
        status_code=500
    )
```

### EncryptionService Error Handling
```python
from app.core.encryption import EncryptionService
from app.core.exceptions import AppException
from cryptography.fernet import InvalidToken
import logging

logger = logging.getLogger(__name__)

# 암호화 서비스 초기화
encryption_service = EncryptionService()

# 안전한 암호화
try:
    encrypted_data = encryption_service.encrypt(session_data)
except AppException as e:
    # 암호화 실패 (500 에러)
    logger.error(f"Encryption failed: {e.detail}")
    raise

# 안전한 복호화
try:
    decrypted_data = encryption_service.decrypt(encrypted_session)
except AppException as e:
    if e.status_code == 401:
        # InvalidToken: 세션이 손상되었거나 키가 잘못됨
        logger.warning(f"Invalid session token, user needs to re-login")
        # 사용자에게 재로그인 요청
    elif e.status_code == 500:
        # 예상치 못한 복호화 오류
        logger.error(f"Unexpected decryption error: {e.detail}")
    raise
```

### Redis Error Handling
```python
from redis.exceptions import RedisError
from app.config.redis import RedisClient
import logging

logger = logging.getLogger(__name__)

redis_client = RedisClient()

# 모든 Redis 에러는 자동으로 logger.error()로 기록됨
# Fail-Open 정책: Redis 장애 시에도 서비스 계속 작동

try:
    # Redis 작업
    await redis_client.set("key", "value", ttl=3600)
    cached_value = await redis_client.get("key")
except Exception as e:
    # Redis 에러는 이미 내부에서 로깅됨
    # 필요 시 fallback 로직 구현
    logger.warning("Redis unavailable, using fallback")
    cached_value = None  # 캐시 미스로 처리
```

---

## 📝 Logging (리팩토링 추가)

### Basic Logging
```python
import logging

logger = logging.getLogger(__name__)

async def create_tip(db: AsyncSession, tip_data: dict) -> Tip:
    """팁 생성 with 로깅"""
    logger.info(f"Creating new tip: {tip_data.get('title')}")

    try:
        tip = Tip(**tip_data)
        db.add(tip)
        await db.commit()
        await db.refresh(tip)

        logger.info(f"Tip created successfully: {tip.id}")
        return tip
    except Exception as e:
        logger.error(f"Failed to create tip: {e}", exc_info=True)
        await db.rollback()
        raise
```

### Performance Logging
```python
import logging
import time
from sqlalchemy import select

logger = logging.getLogger(__name__)

async def get_tips_with_logging(db: AsyncSession) -> list[Tip]:
    """쿼리 성능 로깅"""
    start_time = time.time()

    stmt = select(Tip).where(Tip.is_active == True)
    result = await db.execute(stmt)
    tips = result.scalars().all()

    elapsed = time.time() - start_time
    logger.info(f"Fetched {len(tips)} tips in {elapsed:.3f}s")

    if elapsed > 1.0:
        logger.warning(f"Slow query detected: {elapsed:.3f}s")

    return tips
```

### Analytics Event Logging
```python
import logging
from app.models import AnalyticsEvent

logger = logging.getLogger(__name__)

async def track_event_with_logging(
    db: AsyncSession,
    event_type: str,
    tip_id: str,
    event_data: dict
) -> AnalyticsEvent:
    """이벤트 추적 with 로깅"""
    event = AnalyticsEvent(
        event_type=event_type,
        tip_id=tip_id,
        event_data=event_data
    )

    db.add(event)
    await db.commit()

    logger.info(
        f"Event tracked: {event_type}",
        extra={
            "event_id": event.id,
            "tip_id": tip_id,
            "event_type": event_type
        }
    )

    return event
```

---

## 📝 Pydantic Integration

### Convert Model to Schema
```python
from app.models import Tip
from app.schemas import Tip as TipSchema

# Fetch from DB
stmt = select(Tip).where(Tip.id == "tip_01JCAW0V...")
result = await db.execute(stmt)
tip_model = result.scalar_one()

# Convert to Pydantic schema
tip_schema = TipSchema.model_validate(tip_model)

# Return in FastAPI (auto JSON serialization)
return tip_schema
```

### Create Model from Schema
```python
from app.models import Tip
from app.schemas import TipCreate

# Parse request body
tip_create = TipCreate(**request_data)

# Create model instance
tip = Tip(
    title=tip_create.title,
    content=tip_create.content,
    difficulty=tip_create.difficulty,
    category=tip_create.category,
    terminal_setup=tip_create.terminal_setup,
    publish_date=tip_create.publish_date or date.today(),
    is_active=tip_create.is_active
)

db.add(tip)
await db.commit()
await db.refresh(tip)

return tip
```

---

## 🔧 Common Patterns

### Upsert (Insert or Update)
```python
from sqlalchemy import select
from app.models import Tip

stmt = select(Tip).where(Tip.id == "tip_01JCAW0V...")
result = await db.execute(stmt)
tip = result.scalar_one_or_none()

if tip:
    # Update existing
    tip.title = "Updated Title"
else:
    # Insert new
    tip = Tip(id="tip_01JCAW0V...", title="New Title", ...)
    db.add(tip)

await db.commit()
```

### Bulk Insert
```python
from app.models import AnalyticsEvent

events = [
    AnalyticsEvent(event_type="tip_view", tip_id="tip_01..."),
    AnalyticsEvent(event_type="tip_view", tip_id="tip_02..."),
    AnalyticsEvent(event_type="tip_view", tip_id="tip_03..."),
]

db.add_all(events)
await db.commit()
```

### Exists Check
```python
from sqlalchemy import select, exists
from app.models import Tip

stmt = select(exists().where(Tip.id == "tip_01JCAW0V..."))
tip_exists = await db.scalar(stmt)

if tip_exists:
    print("Tip exists!")
```

---

## 🎯 Best Practices

### Database Operations
1. **Always use `await`** for async operations
2. **Use `selectinload()`** for eager loading relationships to avoid N+1 queries
3. **Commit explicitly** in service layer (not in route handlers)
4. **Use transactions** (`async with db.begin()`) for multi-step operations
5. **Always rollback** on exceptions to prevent partial commits
6. **Use `datetime.now(timezone.utc)`** instead of `datetime.utcnow()` (deprecated in Python 3.12+)

### Data Validation & Type Safety
7. **Validate with Pydantic** before creating models
8. **Use enums** for type-safe status/difficulty values (`DifficultyLevel`, `DraftStatus`)
9. **Import enums** from models instead of hardcoding strings
10. **Use type hints** consistently (`Mapped[str]`, `Mapped[list["Tip"]]`)

### Security
11. **Never store plaintext passwords** (always hash with bcrypt)
12. **Use AppException** for business logic errors with proper HTTP status codes
13. **Validate user input** at Pydantic schema level before database operations
14. **Use `ondelete="SET NULL"`** for analytics to preserve historical data

### Performance
15. **Index frequently queried fields** (done in schema: `publish_date`, `is_active`)
16. **Use JSONB** for flexible data structures (`category`, `terminal_setup`, `event_data`)
17. **Set expires_at** for time-sensitive data (TerminalSession) and clean up regularly
18. **Log slow queries** (> 1 second) for optimization

### Observability
19. **Add structured logging** to all database operations (creation, updates, deletions)
20. **Track analytics** for all user actions using `AnalyticsEvent`
21. **Use logger.info/warning/error** appropriately with contextual information
22. **Log exceptions with `exc_info=True`** for full stack traces

### Code Organization
23. **Separate concerns**: Models (ORM) → Schemas (Validation) → Services (Business Logic) → Routes (API)
24. **Use relationship lazy loading**: `selectin` for frequently accessed, `noload` for rare cases
25. **Cascade deletes carefully**: Use CASCADE for owned data (terminal_sessions), SET NULL for historical data (analytics_events)

---

## 📚 References

### Core Technologies
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [ULID Spec](https://github.com/ulid/spec)

### Error Handling & Logging (리팩토링 추가)
- [FastAPI Exception Handlers](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Structured Logging with python-json-logger](https://github.com/madzak/python-json-logger)

### Related Documentation
- `backend/docs/code-refactoring-report.md` - 리팩토링 상세 보고서
- `backend/docs/day10-11-completion-report.md` - 모델 및 스키마 구현 보고서
- `backend/CLAUDE.md` - 백엔드 개발 가이드

---

**Last Updated**: 2025-10-15 (리팩토링 반영)
**Test Coverage**: 129 tests / 100% passing
