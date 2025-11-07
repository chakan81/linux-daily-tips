# 임시 수정: Anthropic 환경 변수명 변경 (BACKEND_ 접두사 추가)

**작성일**: 2025-11-07
**작성자**: Claude Code
**상태**: ⚠️ 임시 수정 (버그 수정 후 되돌려야 함)

---

## 📋 문제 상황

### Claude Code 버그
- **증상**: 프로젝트 루트의 `.env.development` 파일에 있는 `ANTHROPIC_MODEL` 환경 변수가 Claude Code 자체의 모델 설정에 영향을 줌
- **영향**: 백엔드 애플리케이션용 Anthropic 설정이 Claude Code의 동작을 간섭
- **버그 여부**: Claude Code의 버그로 추정

### 임시 해결 방법
Anthropic 관련 환경 변수에 `BACKEND_` 접두사를 추가하여 Claude Code와 구분

**변경 전**:
```bash
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=2000
```

**변경 후**:
```bash
BACKEND_ANTHROPIC_API_KEY=
BACKEND_ANTHROPIC_MODEL=claude-3-sonnet-20240229
BACKEND_ANTHROPIC_MAX_TOKENS=2000
```

---

## 📝 수정된 파일 목록

### 1. 백엔드 설정 코드
#### `backend/app/config/settings.py`

**변경 내용**:
```python
# 변경 전 (Line 173-175)
anthropic_api_key: Optional[str] = Field(default=None)
anthropic_model: str = Field(default="claude-3-sonnet-20240229")
anthropic_max_tokens: int = Field(default=2000)

# 변경 후
backend_anthropic_api_key: Optional[str] = Field(default=None)
backend_anthropic_model: str = Field(default="claude-3-sonnet-20240229")
backend_anthropic_max_tokens: int = Field(default=2000)
```

**위치**: Line 173-175
**영향**: Phase 2에서 LLM 연동 시 `settings.backend_anthropic_api_key`로 접근 필요

---

### 2. 환경 변수 파일

#### 루트 디렉토리
- `.env.development` (Line 94-96)
- `.env.template` (Line 94-96)
- `.env.example` (Line 36-37)

#### 백엔드 디렉토리
- `backend/.env.development` (Line 59-61)
- `backend/.env.template` (Line 59-61)
- `backend/.env.example` (Line 306-312)
- `backend/.env.production` (Line 60-62)

**모든 파일의 변경 내용**:
```bash
# 변경 전
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_TOKENS=2000

# 변경 후
BACKEND_ANTHROPIC_API_KEY=
BACKEND_ANTHROPIC_MODEL=claude-3-sonnet-20240229
BACKEND_ANTHROPIC_MAX_TOKENS=2000
```

---

### 3. Docker 설정

#### `docker-compose.dev.yml`

**변경 내용** (Line 45):
```yaml
# 변경 전
ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}

# 변경 후
BACKEND_ANTHROPIC_API_KEY: ${BACKEND_ANTHROPIC_API_KEY:-}
```

---

### 4. 스크립트

#### `scripts/dev-up.sh`

**변경 내용** (Line 82):
```bash
# 변경 전
ANTHROPIC_API_KEY=

# 변경 후
BACKEND_ANTHROPIC_API_KEY=
```

---

### 5. 문서

#### `docs/phase2-development-plan.md`

**변경 내용** (Line 48):
```markdown
# 변경 전
- `ANTHROPIC_API_KEY` - Claude API 키

# 변경 후
- `BACKEND_ANTHROPIC_API_KEY` - Claude API 키
```

---

## 🔧 추가로 발견 및 수정된 문제들

오늘 전체 서비스 재시작 과정에서 다음 문제들도 함께 해결되었습니다:

### 1. Redis AOF 손상
- **문제**: Redis AOF 파일에 알 수 없는 `FLUSHALL` 명령어 기록
- **증상**: Redis unhealthy 상태
- **해결**: `docker compose down -v`로 볼륨 클리어

### 2. CORS_ORIGINS 환경 변수 파싱 에러
- **문제**: `docker-compose.dev.yml`의 쉼표 구분 문자열 vs Pydantic의 JSON 파싱
- **파일**: `docker-compose.dev.yml` Line 38
- **해결**:
```yaml
# 변경 전
CORS_ORIGINS: "http://localhost:3000,http://127.0.0.1:3000"

# 변경 후
CORS_ORIGINS: '["http://localhost:3000","http://127.0.0.1:3000"]'
```

### 3. uvicorn 모듈 경로 오류
- **문제**: `docker-compose.dev.yml`의 command가 Dockerfile의 설정을 override
- **파일**: `docker-compose.dev.yml` Line 61
- **해결**:
```yaml
# 변경 전
uvicorn main:app

# 변경 후
uvicorn app.main:app
```

### 4. DATABASE_URL echo 파라미터 문제
- **문제**: asyncpg는 `echo` 파라미터를 지원하지 않음
- **파일**: `docker-compose.dev.yml` Line 40
- **해결**:
```yaml
# 변경 전
DATABASE_URL: postgresql+asyncpg://postgres:postgres_dev_password@postgres:5432/linux_daily_tips?echo=true

# 변경 후
DATABASE_URL: postgresql+asyncpg://postgres:postgres_dev_password@postgres:5432/linux_daily_tips
```

---

## 🔄 롤백 가이드 (버그 수정 후)

Claude Code 버그가 수정되면 다음 절차로 원래대로 되돌리세요:

### 1. 환경 변수명 일괄 변경

**명령어**:
```bash
# 루트 디렉토리
find . -type f \( -name ".env*" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" -o -name "*.md" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -exec sed -i '' 's/BACKEND_ANTHROPIC_/ANTHROPIC_/g' {} +

# 또는 개별 파일 수동 변경
```

### 2. Python 설정 파일 수정

**`backend/app/config/settings.py`** (Line 173-175):
```python
# BACKEND_ 접두사 제거
anthropic_api_key: Optional[str] = Field(default=None)
anthropic_model: str = Field(default="claude-3-sonnet-20240229")
anthropic_max_tokens: int = Field(default=2000)
```

### 3. 테스트 및 검증
```bash
# 서비스 재시작
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 백엔드 설정 로드 확인
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python -c "
from app.core.config import settings
print('✅ Anthropic API Key 필드 존재:', hasattr(settings, 'anthropic_api_key'))
"
```

### 4. Phase 2 코드 수정

Phase 2에서 LLM 연동 시 다음과 같이 변경:
```python
# 변경 전
settings.backend_anthropic_api_key
settings.backend_anthropic_model

# 변경 후
settings.anthropic_api_key
settings.anthropic_model
```

---

## 📌 주의사항

1. **Phase 2 개발 시**: 현재는 `backend_anthropic_*` 필드명을 사용해야 함
2. **Git Commit**: 이 변경사항은 별도 브랜치나 명확한 커밋 메시지로 관리 권장
3. **문서 업데이트**: 롤백 후 이 문서를 아카이브하고 관련 문서들도 업데이트 필요

---

## 🔗 관련 파일

- 이 문서: `docs/temporary-anthropic-env-fix.md`
- 백엔드 설정: `backend/app/config/settings.py`
- Phase 2 계획: `docs/phase2-development-plan.md`
- Docker 설정: `docker-compose.dev.yml`

---

## ✅ 체크리스트

**현재 상태** (2025-11-07):
- [x] 모든 환경 변수 파일 수정 완료
- [x] Python 설정 파일 수정 완료
- [x] Docker 설정 수정 완료
- [x] 문서 수정 완료
- [x] 전체 서비스 테스트 완료

**롤백 시 필요한 작업**:
- [ ] Claude Code 버그 수정 여부 확인
- [ ] 모든 파일에서 `BACKEND_` 접두사 제거
- [ ] `backend/app/config/settings.py` 필드명 원복
- [ ] Phase 2 LLM 연동 코드 수정 (해당 시)
- [ ] 전체 서비스 테스트
- [ ] 이 문서 아카이브

---

**마지막 업데이트**: 2025-11-07
