# Linux Daily Tips - 배포 가이드

이 문서는 Linux Daily Tips 서비스를 스테이징 및 프로덕션 환경에 배포하는 방법을 안내합니다.

---

## 📚 목차

1. [프로덕션 준비 체크리스트](#-프로덕션-준비-체크리스트)
2. [Docker Compose 배포](#-docker-compose-배포)
3. [클라우드 배포](#-클라우드-배포)
4. [CI/CD 파이프라인](#-cicd-파이프라인)
5. [모니터링 및 로깅](#-모니터링-및-로깅)
6. [백업 및 복구](#-백업-및-복구)
7. [보안 강화](#-보안-강화)

---

## ✅ 프로덕션 준비 체크리스트

배포 전 다음 항목들을 반드시 확인하세요:

### 1. 환경 변수 설정

```bash
# ⚠️ 필수: 프로덕션 환경 변수 파일 생성
cp .env.example .env.production

# 다음 값들을 반드시 변경하세요:
# - SECRET_KEY: 강력한 랜덤 문자열 (32+ 글자)
# - JWT_SECRET_KEY: 강력한 랜덤 문자열 (32+ 글자)
# - POSTGRES_PASSWORD: 강력한 비밀번호
# - REDIS_PASSWORD: 강력한 비밀번호
# - ENVIRONMENT: production
```

**프로덕션 환경 변수 예시** (`.env.production`):

```bash
# === 환경 설정 ===
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# === 데이터베이스 (변경 필수!) ===
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_THIS_SECURE_PASSWORD_123!@#
POSTGRES_DB=linux_daily_tips

# === Redis (변경 필수!) ===
REDIS_PASSWORD=CHANGE_THIS_SECURE_REDIS_PASSWORD_456!@#

# === 보안 키 (변경 필수!) ===
SECRET_KEY=CHANGE_THIS_TO_RANDOM_32_CHAR_STRING_789!@#
JWT_SECRET_KEY=CHANGE_THIS_TO_RANDOM_32_CHAR_JWT_KEY_012!@#
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# === 백엔드 URL ===
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# === CORS 설정 ===
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# === 프론트엔드 ===
NEXT_PUBLIC_API_URL=  # 빈 문자열 = rewrites 사용 (권장)
NEXT_PUBLIC_APP_ENV=production

# === OAuth (선택) ===
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback

# === 모니터링 (선택) ===
SENTRY_DSN=your-sentry-dsn-here
```

### 2. 보안 키 생성 방법

```bash
# Python으로 랜덤 키 생성
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL로 랜덤 키 생성
openssl rand -base64 32

# Node.js로 랜덤 키 생성
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### 3. Docker 이미지 빌드 확인

```bash
# 프로덕션 이미지 빌드 테스트
docker build --target production -t linux-tips-backend:prod ./backend
docker build --target production -t linux-tips-frontend:prod ./frontend

# 이미지 크기 확인 (최적화 확인)
docker images | grep linux-tips
```

### 4. 데이터베이스 마이그레이션 준비

```bash
# 마이그레이션 파일 확인
ls -la backend/alembic/versions/

# 현재 마이그레이션 상태 확인
docker compose exec backend alembic current

# 최신 마이그레이션으로 업그레이드 테스트 (개발 환경)
docker compose exec backend alembic upgrade head
```

### 5. 보안 점검

- [ ] 모든 기본 비밀번호 변경 완료
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] HTTPS/TLS 인증서 준비 (Let's Encrypt 또는 CloudFlare)
- [ ] 방화벽 규칙 설정 (포트 80, 443만 외부 노출)
- [ ] CORS 설정 확인 (허용된 도메인만)
- [ ] SQL Injection, XSS 방어 확인
- [ ] Rate Limiting 설정 확인

### 6. 백업 계획

- [ ] 데이터베이스 백업 스크립트 준비
- [ ] 백업 스토리지 준비 (S3, GCS 등)
- [ ] 백업 주기 설정 (일일, 주간)
- [ ] 복구 절차 문서화

---

## 🐳 Docker Compose 배포

### 배포 아키텍처

```
┌─────────────────────────────────────────┐
│         Reverse Proxy (Nginx)           │
│       (HTTPS, 포트 80/443)              │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼─────────┐
    │                   │
    ▼                   ▼
┌─────────┐      ┌─────────────┐
│Frontend │      │   Backend   │
│Next.js  │      │   FastAPI   │
│(3000)   │      │   (8000)    │
└─────────┘      └──────┬──────┘
                        │
            ┌───────────┼───────────┐
            │                       │
            ▼                       ▼
      ┌──────────┐           ┌─────────┐
      │PostgreSQL│           │  Redis  │
      │  (5432)  │           │ (6379)  │
      └──────────┘           └─────────┘
```

### Step 1: 서버 준비

**최소 권장 사양**:
- **CPU**: 2 코어 이상
- **RAM**: 4GB 이상
- **디스크**: 20GB 이상 SSD
- **OS**: Ubuntu 22.04 LTS (권장)

```bash
# 1. 서버 접속 (SSH)
ssh user@your-server-ip

# 2. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 3. Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Docker Compose 설치
sudo apt install docker-compose-plugin -y

# 5. Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER
newgrp docker

# 6. 설치 확인
docker --version
docker compose version
```

### Step 2: 프로젝트 배포

```bash
# 1. 프로젝트 디렉토리 생성
sudo mkdir -p /opt/linux-daily-tips
sudo chown $USER:$USER /opt/linux-daily-tips
cd /opt/linux-daily-tips

# 2. Git 저장소 클론
git clone <repository-url> .
git checkout main  # 또는 배포할 브랜치

# 3. 환경 변수 설정
cp .env.example .env.production
nano .env.production  # 프로덕션 값 설정

# 4. Docker Compose 프로덕션 설정 생성
cat > docker-compose.prod.yml <<EOF
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    env_file:
      - .env.production
    restart: always
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    environment:
      - NODE_ENV=production
    env_file:
      - .env.production
    restart: always
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:18-alpine
    env_file:
      - .env.production
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:8-alpine
    command: redis-server --requirepass \${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "\${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: always

volumes:
  postgres_data:
  redis_data:
EOF

# 5. Nginx 설정 파일 생성
mkdir -p nginx
cat > nginx/nginx.conf <<EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        # HTTP to HTTPS 리다이렉트
        return 301 https://\$host\$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL 인증서 (Let's Encrypt 또는 CloudFlare)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 백엔드 API 프록시
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # 프론트엔드 프록시
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # 헬스 체크
        location /health {
            access_log off;
            return 200 "OK";
            add_header Content-Type text/plain;
        }
    }
}
EOF
```

### Step 3: 배포 실행

```bash
# 1. 이미지 빌드 (첫 배포 시)
docker compose -f docker-compose.prod.yml build

# 2. 서비스 시작
docker compose -f docker-compose.prod.yml up -d

# 3. 서비스 상태 확인
docker compose -f docker-compose.prod.yml ps

# 4. 로그 확인
docker compose -f docker-compose.prod.yml logs -f

# 5. 헬스 체크
curl http://localhost:8000/health
curl http://localhost:3000
```

### Step 4: 데이터베이스 초기화

```bash
# 1. 데이터베이스 마이그레이션 실행
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 2. 초기 데이터 로드 (선택)
docker compose -f docker-compose.prod.yml exec backend python -m app.scripts.seed_data

# 3. 관리자 계정 생성 (선택)
docker compose -f docker-compose.prod.yml exec backend python -m app.scripts.create_admin \
  --email admin@yourdomain.com \
  --password SecurePassword123!
```

### Step 5: SSL/TLS 인증서 설정 (Let's Encrypt)

```bash
# 1. Certbot 설치
sudo apt install certbot python3-certbot-nginx -y

# 2. SSL 인증서 발급
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos

# 3. 인증서 복사
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
sudo chown $USER:$USER nginx/ssl/*.pem

# 4. Nginx 재시작
docker compose -f docker-compose.prod.yml restart nginx

# 5. 자동 갱신 설정 (cron)
sudo crontab -e
# 추가: 0 3 * * * certbot renew --quiet && docker compose -f /opt/linux-daily-tips/docker-compose.prod.yml restart nginx
```

---

## ☁️ 클라우드 배포

### AWS ECS/Fargate 배포

**장점**: 서버리스, 자동 스케일링, 관리형 서비스

**주요 단계**:
1. ECR에 Docker 이미지 푸시
2. ECS 클러스터 생성
3. 태스크 정의 작성
4. RDS (PostgreSQL) + ElastiCache (Redis) 생성
5. ALB (Application Load Balancer) 설정
6. Route 53로 도메인 연결

**예상 비용** (us-east-1 기준):
- Fargate (2 vCPU, 4GB RAM): ~$60/월
- RDS (db.t4g.micro): ~$20/월
- ElastiCache (cache.t4g.micro): ~$15/월
- ALB: ~$20/월
- **총 예상**: ~$115/월

---

### Google Cloud Run 배포

**장점**: 완전 서버리스, 사용량 기반 과금, 쉬운 배포

**주요 단계**:
1. Cloud Build로 이미지 빌드
2. Artifact Registry에 푸시
3. Cloud Run 서비스 배포
4. Cloud SQL (PostgreSQL) + Memorystore (Redis) 연결
5. Cloud Load Balancing 설정
6. Cloud DNS로 도메인 연결

**예상 비용** (asia-northeast3 기준):
- Cloud Run (월 100만 요청): ~$10/월
- Cloud SQL (db-f1-micro): ~$10/월
- Memorystore (M1): ~$40/월
- **총 예상**: ~$60/월

---

### DigitalOcean App Platform 배포

**장점**: 간단한 설정, 합리적 가격, 관리 편의성

**주요 단계**:
1. GitHub 저장소 연결
2. 앱 설정 (Frontend + Backend)
3. Managed PostgreSQL + Redis 생성
4. 도메인 연결 및 SSL 자동 설정

**예상 비용** (USD 기준):
- App Platform (Basic): $12/월
- Managed PostgreSQL (1GB RAM): $15/월
- Managed Redis (1GB RAM): $15/월
- **총 예상**: ~$42/월

---

## 🔄 CI/CD 파이프라인

### GitHub Actions 자동 배포

프로젝트에 이미 구성된 CI/CD 파이프라인 (`.github/workflows/deploy.yml`):

```yaml
# main 브랜치 푸시 시 자동 배포
on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker Images
      - name: Push to GitHub Container Registry
      - name: Deploy to Production
```

**수동 배포 트리거**:
```bash
# GitHub CLI로 워크플로우 실행
gh workflow run deploy.yml

# 또는 Git 태그로 릴리즈 배포
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 📊 모니터링 및 로깅

### 1. 헬스 체크 설정

```bash
# 백엔드 헬스 체크
curl http://localhost:8000/health
# 응답: {"status": "healthy"}

# 프론트엔드 헬스 체크
curl http://localhost:3000
# 응답: 200 OK

# 데이터베이스 헬스 체크
docker compose exec postgres pg_isready -U postgres
```

### 2. 로그 모니터링

```bash
# 실시간 로그 확인
docker compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend

# 에러 로그만 필터링
docker compose -f docker-compose.prod.yml logs backend | grep ERROR

# 로그 파일로 저장
docker compose -f docker-compose.prod.yml logs > /var/log/linux-tips.log
```

### 3. 리소스 모니터링

```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
df -h
docker system df

# 메모리 사용량
free -h
```

### 4. Sentry 에러 추적 (선택)

```bash
# .env.production에 추가
SENTRY_DSN=your-sentry-dsn-here

# 백엔드에서 자동으로 Sentry로 에러 전송
# 프론트엔드에서도 @sentry/nextjs 사용 가능
```

---

## 💾 백업 및 복구

### 데이터베이스 백업

```bash
# 1. 수동 백업 스크립트 생성
cat > /opt/linux-daily-tips/scripts/backup-db.sh <<EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/linux-daily-tips/backups"
mkdir -p \$BACKUP_DIR

docker compose -f /opt/linux-daily-tips/docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres linux_daily_tips | gzip > \$BACKUP_DIR/backup_\$DATE.sql.gz

# 7일 이상 된 백업 삭제
find \$BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_\$DATE.sql.gz"
EOF

chmod +x /opt/linux-daily-tips/scripts/backup-db.sh

# 2. Cron으로 자동 백업 설정 (매일 새벽 3시)
crontab -e
# 추가: 0 3 * * * /opt/linux-daily-tips/scripts/backup-db.sh
```

### 데이터베이스 복구

```bash
# 1. 백업 파일 목록 확인
ls -lh /opt/linux-daily-tips/backups/

# 2. 복구 실행
gunzip < /opt/linux-daily-tips/backups/backup_20250105_030000.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres -d linux_daily_tips

# 3. 복구 확인
docker compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d linux_daily_tips -c "SELECT COUNT(*) FROM tips;"
```

---

## 🔒 보안 강화

### 1. 방화벽 설정 (UFW)

```bash
# UFW 설치 및 활성화
sudo apt install ufw -y

# 기본 정책 설정
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 필수 포트 열기
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# UFW 활성화
sudo ufw enable

# 상태 확인
sudo ufw status verbose
```

### 2. Fail2Ban 설정

```bash
# Fail2Ban 설치
sudo apt install fail2ban -y

# SSH 보호 활성화
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 상태 확인
sudo fail2ban-client status sshd
```

### 3. Docker 보안

```bash
# 1. Docker 소켓 권한 제한
sudo chmod 660 /var/run/docker.sock

# 2. Docker Compose 파일 권한
chmod 600 .env.production
chmod 600 docker-compose.prod.yml

# 3. 비밀번호가 포함된 파일 암호화 (선택)
# git-crypt 또는 ansible-vault 사용
```

### 4. 정기 보안 업데이트

```bash
# 시스템 업데이트 자동화
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades

# Docker 이미지 정기 업데이트
crontab -e
# 추가: 0 4 * * 0 cd /opt/linux-daily-tips && docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d
```

---

## 🚀 무중단 배포 (롤링 업데이트)

```bash
# 1. 새 버전 이미지 빌드
docker compose -f docker-compose.prod.yml build

# 2. 롤링 업데이트 (한 번에 하나씩)
docker compose -f docker-compose.prod.yml up -d --no-deps --build backend
sleep 10  # 헬스 체크 대기
docker compose -f docker-compose.prod.yml up -d --no-deps --build frontend

# 3. 이전 이미지 정리
docker image prune -f
```

---

## 📞 추가 도움

- **문제 발생 시**: [트러블슈팅 가이드](./USER_GUIDE.md#-트러블슈팅)
- **백업 복구**: [백업 섹션](#-백업-및-복구)
- **보안 이슈**: security@yourdomain.com

---

**문서 버전**: Day 28 (2025-11-05)
**마지막 업데이트**: Week 4 완료

**⚠️ 주의사항**:
- 프로덕션 배포 전 반드시 스테이징 환경에서 테스트하세요
- 모든 비밀번호와 키를 변경하세요
- 백업을 정기적으로 확인하세요
- 모니터링 알림을 설정하세요
