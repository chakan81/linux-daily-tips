/**
 * MSW (Mock Service Worker) API Handlers
 *
 * 개발 환경에서 백엔드 API를 목업하여 프론트엔드 독립 개발 가능
 */

import { http, HttpResponse } from 'msw'
import type { TipData } from '@/lib/types/tip'
import type { AdminStats } from '@/lib/hooks/useAdmin'
import type { Activity } from '@/lib/types/common'

const API_BASE_URL = 'http://localhost:8000'

// ============================================================================
// Mock 데이터
// ============================================================================

/**
 * 오늘의 팁 - 파일 권한 관리
 */
const mockTodayTip: TipData = {
  id: 1,
  title: 'Master File Permissions with chmod',
  description: 'Understanding Linux file permissions is crucial for system security and proper access control. Learn how to use chmod effectively.',
  content: `# Understanding File Permissions

File permissions in Linux control who can read, write, or execute files. This is fundamental for system security.

## Basic Concepts

Every file has three permission sets:
- **Owner (u)**: The user who owns the file
- **Group (g)**: Users in the file's group
- **Others (o)**: Everyone else

Each set has three permissions:
- **Read (r)**: View file contents
- **Write (w)**: Modify file contents
- **Execute (x)**: Run the file as a program

## Numeric Notation

Permissions can be represented as numbers:
- Read = 4
- Write = 2
- Execute = 1

Add them together for combinations:
- 7 (4+2+1) = rwx (full permissions)
- 6 (4+2) = rw- (read and write)
- 5 (4+1) = r-x (read and execute)
- 4 = r-- (read only)

## Common Examples

\`\`\`bash
# Make file executable for owner
chmod u+x script.sh

# Set permissions to 755 (rwxr-xr-x)
chmod 755 script.sh

# Remove write permission for group and others
chmod go-w file.txt

# Set read/write for owner, read-only for others
chmod 644 document.txt
\`\`\`

## Best Practices

1. **Never use 777**: This gives everyone full access (security risk)
2. **Scripts**: Usually 755 (executable by all, writable by owner)
3. **Config files**: Usually 600 or 644 (protect sensitive data)
4. **Directories**: Need execute permission to access contents

## Symbolic vs Numeric

Both methods work, choose based on preference:

\`\`\`bash
# Symbolic: More readable
chmod u=rwx,g=rx,o=rx file.sh

# Numeric: More concise
chmod 755 file.sh
\`\`\``,
  command: 'chmod',
  difficulty: 'Beginner',
  category: 'File Management',
  estimatedTime: '5 min',
  tags: ['permissions', 'security', 'chmod', 'files'],
  publishDate: new Date().toISOString(),
  lastUpdated: new Date().toISOString(),
  viewCount: 1234,
  likeCount: 89,
  isPublished: true,
  slug: 'master-file-permissions-chmod',
  metaDescription: 'Learn how to manage Linux file permissions using chmod command with practical examples',
  socialImageUrl: '/images/tips/chmod-tutorial.jpg',
}

/**
 * 최근 팁 목록
 */
const mockRecentTips: TipData[] = [
  {
    ...mockTodayTip,
    id: 2,
    title: 'Efficient Text Search with grep',
    description: 'Master the powerful grep command for searching text patterns in files',
    command: 'grep',
    difficulty: 'Intermediate',
    category: 'Text Processing',
    slug: 'efficient-text-search-grep',
    viewCount: 956,
    likeCount: 67,
  },
  {
    ...mockTodayTip,
    id: 3,
    title: 'Process Management with ps and top',
    description: 'Monitor and manage system processes effectively',
    command: 'ps',
    difficulty: 'Advanced',
    category: 'Process Management',
    slug: 'process-management-ps-top',
    viewCount: 834,
    likeCount: 54,
  },
  {
    ...mockTodayTip,
    id: 4,
    title: 'Network Diagnostics with netstat',
    description: 'Analyze network connections and routing tables',
    command: 'netstat',
    difficulty: 'Intermediate',
    category: 'Networking',
    slug: 'network-diagnostics-netstat',
    viewCount: 723,
    likeCount: 43,
  },
]

/**
 * 통계 데이터
 */
interface Stats {
  totalTips: number
  publishedTips: number
  draftTips: number
  totalViews: number
  todayViews: number
  averageReadTime: number
  activeUsers: number
  completionRate: number
  popularCategories: Array<{
    name: string
    count: number
  }>
}

const mockStats: Stats = {
  totalTips: 150,
  publishedTips: 120,
  draftTips: 30,
  totalViews: 45678,
  todayViews: 1234,
  averageReadTime: 4.5,
  activeUsers: 5432,
  completionRate: 87.5,
  popularCategories: [
    { name: 'File Management', count: 35 },
    { name: 'Text Processing', count: 28 },
    { name: 'System Monitoring', count: 22 },
    { name: 'Networking', count: 18 },
  ],
}

/**
 * 관리자 통계
 */
const mockAdminStats: AdminStats = {
  totalTips: 150,
  pendingApproval: 12,
  activeUsers: 5432,
  completionRate: 67.5,
}

/**
 * 승인 대기 팁 목록
 */
const mockPendingTips = [
  {
    id: 101,
    title: 'Advanced Git Rebase Techniques',
    author: 'John Doe',
    category: 'Version Control' as const,
    difficulty: 'Advanced' as const,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    submittedAt: '2 hours ago',
  },
  {
    id: 102,
    title: 'Docker Container Optimization',
    author: 'Jane Smith',
    category: 'System Administration' as const,
    difficulty: 'Intermediate' as const,
    createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
    submittedAt: '5 hours ago',
  },
  {
    id: 103,
    title: 'Bash Scripting Best Practices',
    author: 'Bob Johnson',
    category: 'Shell Scripting' as const,
    difficulty: 'Beginner' as const,
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
    submittedAt: '1 day ago',
  },
]

/**
 * 최근 활동 로그
 */
const mockRecentActivity: Activity[] = [
  {
    id: 1,
    type: 'tip_created',
    message: 'New tip "Advanced Git Commands" created',
    time: '2 minutes ago',
    status: 'pending',
  },
  {
    id: 2,
    type: 'tip_approved',
    message: 'Tip "Docker Basics" approved',
    time: '15 minutes ago',
    status: 'approved',
  },
  {
    id: 3,
    type: 'user_activity',
    message: 'User registration spike detected: +234 users today',
    time: '1 hour ago',
    status: 'success',
  },
  {
    id: 4,
    type: 'system',
    message: 'Database backup completed successfully',
    time: '2 hours ago',
    status: 'info',
  },
]

// ============================================================================
// API 핸들러
// ============================================================================

export const handlers = [
  // GET /api/tips/today - 오늘의 팁 조회
  http.get(`${API_BASE_URL}/api/tips/today`, () => {
    return HttpResponse.json(mockTodayTip)
  }),

  // GET /api/tips/recent - 최근 팁 목록 조회
  http.get(`${API_BASE_URL}/api/tips/recent`, ({ request }) => {
    const url = new URL(request.url)
    const limit = parseInt(url.searchParams.get('limit') || '3')
    return HttpResponse.json(mockRecentTips.slice(0, limit))
  }),

  // GET /api/tips/:id - 특정 팁 조회
  http.get(`${API_BASE_URL}/api/tips/:id`, ({ params }) => {
    const { id } = params
    const tip = mockRecentTips.find((t) => t.id === Number(id)) || mockTodayTip
    return HttpResponse.json(tip)
  }),

  // GET /api/tips - 팁 목록 조회 (페이지네이션)
  http.get(`${API_BASE_URL}/api/tips`, ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const limit = parseInt(url.searchParams.get('limit') || '10')
    const category = url.searchParams.get('category')
    const difficulty = url.searchParams.get('difficulty')

    let filteredTips = [mockTodayTip, ...mockRecentTips]

    // 카테고리 필터
    if (category) {
      filteredTips = filteredTips.filter((tip) => tip.category === category)
    }

    // 난이도 필터
    if (difficulty) {
      filteredTips = filteredTips.filter((tip) => tip.difficulty === difficulty)
    }

    // 페이지네이션
    const startIndex = (page - 1) * limit
    const endIndex = startIndex + limit
    const paginatedTips = filteredTips.slice(startIndex, endIndex)

    return HttpResponse.json({
      tips: paginatedTips,
      pagination: {
        page,
        limit,
        total: filteredTips.length,
        totalPages: Math.ceil(filteredTips.length / limit),
      },
    })
  }),

  // GET /api/stats/overview - 통계 개요
  http.get(`${API_BASE_URL}/api/stats/overview`, () => {
    return HttpResponse.json(mockStats)
  }),

  // GET /api/admin/stats - 관리자 통계
  http.get(`${API_BASE_URL}/api/admin/stats`, () => {
    return HttpResponse.json(mockAdminStats)
  }),

  // GET /api/admin/tips/pending - 승인 대기 팁
  http.get(`${API_BASE_URL}/api/admin/tips/pending`, () => {
    return HttpResponse.json(mockPendingTips)
  }),

  // GET /api/admin/activity/recent - 최근 활동
  http.get(`${API_BASE_URL}/api/admin/activity/recent`, () => {
    return HttpResponse.json(mockRecentActivity)
  }),

  // POST /api/admin/tips/:id/approve - 팁 승인
  http.post(`${API_BASE_URL}/api/admin/tips/:id/approve`, ({ params }) => {
    const { id } = params
    return HttpResponse.json({
      success: true,
      message: `Tip ${id} approved successfully`,
    })
  }),

  // POST /api/admin/tips/:id/reject - 팁 거절
  http.post(`${API_BASE_URL}/api/admin/tips/:id/reject`, async ({ params, request }) => {
    const { id } = params
    const body = (await request.json()) as { reason?: string } | null
    return HttpResponse.json({
      success: true,
      message: `Tip ${id} rejected: ${body?.reason || 'No reason provided'}`,
    })
  }),

  // POST /api/tips/:id/like - 팁 좋아요
  http.post(`${API_BASE_URL}/api/tips/:id/like`, ({ params }) => {
    const { id } = params
    return HttpResponse.json({
      success: true,
      likeCount: Math.floor(Math.random() * 100) + 50,
    })
  }),

  // GET /api/tips/search - 팁 검색
  http.get(`${API_BASE_URL}/api/tips/search`, ({ request }) => {
    const url = new URL(request.url)
    const query = url.searchParams.get('q') || ''

    const searchResults = [mockTodayTip, ...mockRecentTips].filter(
      (tip) =>
        tip.title.toLowerCase().includes(query.toLowerCase()) ||
        tip.description.toLowerCase().includes(query.toLowerCase())
    )

    return HttpResponse.json({
      results: searchResults,
      total: searchResults.length,
    })
  }),
]
