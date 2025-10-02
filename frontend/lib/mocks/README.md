# MSW (Mock Service Worker) 설정 가이드

## 개요

이 디렉토리는 개발 환경에서 Mock API 응답을 제공하는 MSW 설정을 포함합니다.
백엔드가 준비되지 않은 상태에서도 프론트엔드를 독립적으로 개발할 수 있습니다.

## 파일 구조

```
lib/mocks/
├── README.md          # 이 파일
├── handlers.ts        # Mock API 핸들러 정의
└── browser.ts         # MSW 브라우저 설정
```

## 작동 원리

MSW는 Service Worker를 사용하여 네트워크 수준에서 API 요청을 가로채고 Mock 응답을 반환합니다.

```
API Request → Service Worker → Mock Handler → Mock Response
```

## 핸들러 구조

### handlers.ts

모든 Mock API 엔드포인트를 정의합니다.

```typescript
// 예시: GET /api/tips/today
http.get(`${API_BASE_URL}/api/tips/today`, () => {
  return HttpResponse.json(mockTodayTip)
})
```

### 현재 구현된 엔드포인트

#### Tips API
- `GET /api/tips/today` - 오늘의 팁
- `GET /api/tips/recent?limit=3` - 최근 팁 목록
- `GET /api/tips/:id` - 특정 팁 조회
- `GET /api/tips` - 팁 목록 (페이지네이션)
- `GET /api/tips/search?q=keyword` - 팁 검색
- `POST /api/tips/:id/like` - 팁 좋아요

#### Stats API
- `GET /api/stats/overview` - 통계 개요

#### Admin API
- `GET /api/admin/stats` - 관리자 통계
- `GET /api/admin/tips/pending` - 승인 대기 팁
- `GET /api/admin/activity/recent` - 최근 활동
- `POST /api/admin/tips/:id/approve` - 팁 승인
- `POST /api/admin/tips/:id/reject` - 팁 거절

## Mock 데이터

### mockTodayTip
오늘의 팁으로 표시되는 샘플 데이터입니다.

```typescript
{
  id: 1,
  title: 'Master File Permissions with chmod',
  difficulty: 'Beginner',
  category: 'File Management',
  // ... 기타 필드
}
```

### mockRecentTips
최근 팁 목록 데이터 (3개)

### mockStats
전체 통계 데이터

### mockAdminStats
관리자 대시보드 통계

### mockPendingTips
승인 대기 중인 팁 목록

### mockRecentActivity
최근 활동 로그

## 새 엔드포인트 추가하기

1. `handlers.ts`에 새 핸들러 추가:

```typescript
// GET 요청 예시
http.get(`${API_BASE_URL}/api/new-endpoint`, () => {
  return HttpResponse.json({ data: 'example' })
})

// POST 요청 예시
http.post(`${API_BASE_URL}/api/new-endpoint`, async ({ request }) => {
  const body = await request.json()
  return HttpResponse.json({ success: true })
})

// 경로 파라미터 사용
http.get(`${API_BASE_URL}/api/items/:id`, ({ params }) => {
  const { id } = params
  return HttpResponse.json({ id })
})

// 쿼리 파라미터 사용
http.get(`${API_BASE_URL}/api/search`, ({ request }) => {
  const url = new URL(request.url)
  const query = url.searchParams.get('q')
  return HttpResponse.json({ query })
})
```

2. `handlers` 배열에 핸들러가 자동으로 포함됩니다.

## MSW 활성화/비활성화

### 개발 환경에서 자동 활성화
`lib/providers/QueryProvider.tsx`에서 자동으로 활성화됩니다:

```typescript
useEffect(() => {
  if (process.env.NODE_ENV === 'development') {
    import('@/lib/mocks/browser').then(({ worker }) => {
      worker.start({
        onUnhandledRequest: 'bypass', // 처리되지 않은 요청은 실제 서버로
      })
    })
  }
}, [])
```

### MSW 비활성화 방법

환경 변수를 사용하여 MSW를 비활성화할 수 있습니다:

1. `.env.local` 파일에 추가:
```bash
NEXT_PUBLIC_ENABLE_MSW=false
```

2. `QueryProvider.tsx` 수정:
```typescript
if (process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_ENABLE_MSW !== 'false') {
  // MSW 초기화
}
```

## 프로덕션 빌드

MSW는 개발 환경에서만 작동하며, 프로덕션 빌드에는 포함되지 않습니다.

```bash
# 개발 서버 (MSW 활성화)
npm run dev

# 프로덕션 빌드 (MSW 비활성화)
npm run build
npm start
```

## 디버깅

### 브라우저 콘솔 확인

1. 개발 서버 시작 시 콘솔 메시지:
```
🔶 MSW: Mock API enabled for development
```

2. Network 탭에서 확인:
   - Mock된 요청은 `(from service worker)` 라벨 표시
   - 실제 요청과 동일한 형식으로 표시됨

### 처리되지 않은 요청

`onUnhandledRequest: 'bypass'` 설정으로 처리되지 않은 요청은 실제 서버로 전달됩니다.

경고를 표시하려면:
```typescript
worker.start({
  onUnhandledRequest: 'warn', // 콘솔에 경고 표시
})
```

## 백엔드 연동 시

백엔드 API가 준비되면:

1. MSW를 비활성화 (환경 변수 사용)
2. 또는 특정 엔드포인트만 Mock 유지
3. `handlers.ts`에서 해당 핸들러 제거/주석 처리

## 참고 자료

- [MSW 공식 문서](https://mswjs.io/)
- [MSW Browser Integration](https://mswjs.io/docs/integrations/browser)
- [MSW API Reference](https://mswjs.io/docs/api)
