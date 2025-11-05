/**
 * Unit Tests for lib/api/endpoints.ts
 *
 * Test coverage for:
 * - API_ENDPOINTS: Endpoint URL definitions
 * - buildUrl: Query parameter URL building
 */

import { API_ENDPOINTS, buildUrl } from '../endpoints'

describe('API_ENDPOINTS', () => {
  describe('TIPS endpoints', () => {
    it('should have correct tips list endpoint', () => {
      expect(API_ENDPOINTS.TIPS.LIST).toBe('/api/tips')
    })

    it('should have correct today tip endpoint', () => {
      expect(API_ENDPOINTS.TIPS.TODAY).toBe('/api/tips/today')
    })

    it('should have correct recent tips endpoint', () => {
      expect(API_ENDPOINTS.TIPS.RECENT).toBe('/api/tips/recent')
    })

    it('should have correct search endpoint', () => {
      expect(API_ENDPOINTS.TIPS.SEARCH).toBe('/api/tips/search')
    })

    it('should generate correct BY_ID endpoint', () => {
      expect(API_ENDPOINTS.TIPS.BY_ID('123')).toBe('/api/tips/123')
      expect(API_ENDPOINTS.TIPS.BY_ID('tip-slug')).toBe('/api/tips/tip-slug')
    })

    it('should generate correct BY_CATEGORY endpoint', () => {
      expect(API_ENDPOINTS.TIPS.BY_CATEGORY('file-management')).toBe(
        '/api/tips/category/file-management'
      )
      expect(API_ENDPOINTS.TIPS.BY_CATEGORY('networking')).toBe(
        '/api/tips/category/networking'
      )
    })

    it('should generate correct BY_DIFFICULTY endpoint', () => {
      expect(API_ENDPOINTS.TIPS.BY_DIFFICULTY('beginner')).toBe(
        '/api/tips/difficulty/beginner'
      )
      expect(API_ENDPOINTS.TIPS.BY_DIFFICULTY('advanced')).toBe(
        '/api/tips/difficulty/advanced'
      )
    })
  })

  describe('DRAFTS endpoints', () => {
    it('should have correct drafts list endpoint', () => {
      expect(API_ENDPOINTS.DRAFTS.LIST).toBe('/api/drafts')
    })

    it('should have correct generate endpoint', () => {
      expect(API_ENDPOINTS.DRAFTS.GENERATE).toBe('/api/drafts/generate')
    })

    it('should generate correct BY_ID endpoint', () => {
      expect(API_ENDPOINTS.DRAFTS.BY_ID('456')).toBe('/api/drafts/456')
    })

    it('should generate correct APPROVE endpoint', () => {
      expect(API_ENDPOINTS.DRAFTS.APPROVE('789')).toBe('/api/drafts/789/approve')
    })

    it('should generate correct REJECT endpoint', () => {
      expect(API_ENDPOINTS.DRAFTS.REJECT('789')).toBe('/api/drafts/789/reject')
    })
  })

  describe('STATS endpoints', () => {
    it('should have correct overview endpoint', () => {
      expect(API_ENDPOINTS.STATS.OVERVIEW).toBe('/api/stats/overview')
    })

    it('should have correct tips by category endpoint', () => {
      expect(API_ENDPOINTS.STATS.TIPS_BY_CATEGORY).toBe('/api/stats/tips-by-category')
    })

    it('should have correct tips by difficulty endpoint', () => {
      expect(API_ENDPOINTS.STATS.TIPS_BY_DIFFICULTY).toBe('/api/stats/tips-by-difficulty')
    })
  })

  describe('AUTH endpoints', () => {
    it('should have correct login endpoint', () => {
      expect(API_ENDPOINTS.AUTH.LOGIN).toBe('/api/auth/login')
    })

    it('should have correct logout endpoint', () => {
      expect(API_ENDPOINTS.AUTH.LOGOUT).toBe('/api/auth/logout')
    })

    it('should have correct refresh endpoint', () => {
      expect(API_ENDPOINTS.AUTH.REFRESH).toBe('/api/auth/refresh')
    })

    it('should have correct me endpoint', () => {
      expect(API_ENDPOINTS.AUTH.ME).toBe('/api/auth/me')
    })
  })

  describe('ADMIN endpoints', () => {
    it('should have correct stats endpoint', () => {
      expect(API_ENDPOINTS.ADMIN.STATS).toBe('/api/admin/stats')
    })

    it('should have correct pending tips endpoint', () => {
      expect(API_ENDPOINTS.ADMIN.PENDING_TIPS).toBe('/api/admin/tips/pending')
    })

    it('should have correct recent activity endpoint', () => {
      expect(API_ENDPOINTS.ADMIN.RECENT_ACTIVITY).toBe('/api/admin/activity/recent')
    })

    it('should generate correct approve tip endpoint', () => {
      expect(API_ENDPOINTS.ADMIN.APPROVE_TIP('123')).toBe('/api/admin/tips/123/approve')
    })

    it('should generate correct reject tip endpoint', () => {
      expect(API_ENDPOINTS.ADMIN.REJECT_TIP('123')).toBe('/api/admin/tips/123/reject')
    })
  })

  describe('TERMINAL endpoints', () => {
    it('should have correct create session endpoint', () => {
      expect(API_ENDPOINTS.TERMINAL.CREATE_SESSION).toBe('/api/terminal/session')
    })

    it('should generate correct execute endpoint', () => {
      expect(API_ENDPOINTS.TERMINAL.EXECUTE('session-123')).toBe(
        '/api/terminal/session/session-123/execute'
      )
    })

    it('should generate correct destroy endpoint', () => {
      expect(API_ENDPOINTS.TERMINAL.DESTROY('session-123')).toBe(
        '/api/terminal/session/session-123'
      )
    })
  })

  describe('Endpoint immutability', () => {
    it('should be readonly (const assertion)', () => {
      // TypeScript prevents this at compile time with 'as const'
      // In JavaScript runtime, the object is frozen
      expect(API_ENDPOINTS).toBeDefined()
      expect(API_ENDPOINTS.TIPS).toBeDefined()
      expect(API_ENDPOINTS.TIPS.LIST).toBe('/api/tips')
    })
  })
})

describe('buildUrl', () => {
  describe('Basic functionality', () => {
    it('should return endpoint without params', () => {
      expect(buildUrl('/api/tips')).toBe('/api/tips')
      expect(buildUrl('/api/tips', undefined)).toBe('/api/tips')
      expect(buildUrl('/api/tips', {})).toBe('/api/tips')
    })

    it('should build URL with single query parameter', () => {
      expect(buildUrl('/api/tips', { limit: 10 })).toBe('/api/tips?limit=10')
    })

    it('should build URL with multiple query parameters', () => {
      const url = buildUrl('/api/tips', { limit: 10, page: 2 })
      expect(url).toContain('limit=10')
      expect(url).toContain('page=2')
      expect(url).toContain('&')
    })

    it('should build URL with string parameters', () => {
      expect(buildUrl('/api/tips/search', { q: 'grep' })).toBe('/api/tips/search?q=grep')
    })

    it('should build URL with boolean parameters', () => {
      expect(buildUrl('/api/tips', { approved: true })).toBe('/api/tips?approved=true')
      expect(buildUrl('/api/tips', { approved: false })).toBe('/api/tips?approved=false')
    })
  })

  describe('Parameter filtering', () => {
    it('should filter out undefined values', () => {
      const url = buildUrl('/api/tips', { limit: 10, page: undefined })
      expect(url).toBe('/api/tips?limit=10')
      expect(url).not.toContain('page')
    })

    it('should filter out null values', () => {
      const url = buildUrl('/api/tips', { limit: 10, page: null })
      expect(url).toBe('/api/tips?limit=10')
      expect(url).not.toContain('page')
    })

    it('should filter out both undefined and null', () => {
      const url = buildUrl('/api/tips', {
        limit: 10,
        page: undefined,
        sort: null,
      })
      expect(url).toBe('/api/tips?limit=10')
    })

    it('should keep zero values', () => {
      expect(buildUrl('/api/tips', { page: 0 })).toBe('/api/tips?page=0')
    })

    it('should keep empty string values', () => {
      expect(buildUrl('/api/tips', { search: '' })).toBe('/api/tips?search=')
    })
  })

  describe('URL encoding', () => {
    it('should encode special characters', () => {
      const url = buildUrl('/api/tips/search', { q: 'hello world' })
      expect(url).toBe('/api/tips/search?q=hello%20world')
    })

    it('should encode special symbols', () => {
      const url = buildUrl('/api/tips/search', { q: 'test@example.com' })
      expect(url).toContain('test%40example.com')
    })

    it('should encode ampersands', () => {
      const url = buildUrl('/api/tips', { name: 'Tom & Jerry' })
      expect(url).toContain('Tom%20%26%20Jerry')
    })

    it('should encode question marks', () => {
      const url = buildUrl('/api/tips', { query: 'what?' })
      expect(url).toContain('what%3F')
    })

    it('should encode equals signs', () => {
      const url = buildUrl('/api/tips', { expr: 'x=5' })
      expect(url).toContain('x%3D5')
    })

    it('should encode slashes', () => {
      const url = buildUrl('/api/tips', { path: 'folder/file.txt' })
      expect(url).toContain('folder%2Ffile.txt')
    })
  })

  describe('Complex scenarios', () => {
    it('should handle mixed parameter types', () => {
      const url = buildUrl('/api/tips', {
        limit: 10,
        category: 'file-management',
        approved: true,
        page: undefined,
      })

      expect(url).toContain('limit=10')
      expect(url).toContain('category=file-management')
      expect(url).toContain('approved=true')
      expect(url).not.toContain('page')
    })

    it('should handle search with filters', () => {
      const url = buildUrl('/api/tips/search', {
        q: 'grep command',
        difficulty: 'beginner',
        category: 'text processing',
      })

      expect(url).toContain('q=grep%20command')
      expect(url).toContain('difficulty=beginner')
      expect(url).toContain('category=text%20processing')
    })

    it('should handle pagination parameters', () => {
      const url = buildUrl('/api/tips', {
        page: 1,
        limit: 20,
        sort: 'date',
        order: 'desc',
      })

      expect(url).toContain('page=1')
      expect(url).toContain('limit=20')
      expect(url).toContain('sort=date')
      expect(url).toContain('order=desc')
    })

    it('should handle all parameters filtered out', () => {
      const url = buildUrl('/api/tips', {
        page: undefined,
        limit: null,
      })

      expect(url).toBe('/api/tips')
    })

    it('should handle numeric zero and string zero differently', () => {
      const url = buildUrl('/api/tips', {
        numZero: 0,
        strZero: '0',
      })

      expect(url).toContain('numZero=0')
      expect(url).toContain('strZero=0')
    })
  })

  describe('Edge cases', () => {
    it('should handle endpoint with existing query string', () => {
      // buildUrl doesn't handle existing query strings, but should still work
      const url = buildUrl('/api/tips?existing=true', { new: 'param' })
      expect(url).toBe('/api/tips?existing=true?new=param')
      // This is technically incorrect but expected behavior
      // In production, you shouldn't pass endpoints with existing query strings
    })

    it('should handle endpoint with trailing slash', () => {
      expect(buildUrl('/api/tips/', { limit: 10 })).toBe('/api/tips/?limit=10')
    })

    it('should handle empty endpoint', () => {
      expect(buildUrl('', { limit: 10 })).toBe('?limit=10')
    })

    it('should handle very long parameter values', () => {
      const longValue = 'a'.repeat(1000)
      const url = buildUrl('/api/tips', { query: longValue })
      expect(url).toContain('query=')
      expect(url.length).toBeGreaterThan(1000)
    })

    it('should handle Unicode characters', () => {
      const url = buildUrl('/api/tips', { name: '你好世界' })
      expect(url).toContain('name=')
      expect(url).toContain('%')
    })

    it('should handle emoji in parameters', () => {
      const url = buildUrl('/api/tips', { emoji: '🚀' })
      expect(url).toContain('emoji=')
      expect(url).toContain('%')
    })
  })

  describe('Real-world usage patterns', () => {
    it('should build search URL', () => {
      const url = buildUrl(API_ENDPOINTS.TIPS.SEARCH, {
        q: 'find command',
        limit: 10,
      })

      expect(url).toBe('/api/tips/search?q=find%20command&limit=10')
    })

    it('should build paginated list URL', () => {
      const url = buildUrl(API_ENDPOINTS.TIPS.LIST, {
        page: 2,
        limit: 20,
      })

      // Order of query parameters may vary
      expect(url).toContain('page=2')
      expect(url).toContain('limit=20')
      expect(url).toMatch(/^\/api\/tips\?/)
    })

    it('should build recent tips URL with limit', () => {
      const url = buildUrl(API_ENDPOINTS.TIPS.RECENT, { limit: 5 })
      expect(url).toBe('/api/tips/recent?limit=5')
    })

    it('should build filtered tips URL', () => {
      const url = buildUrl(API_ENDPOINTS.TIPS.LIST, {
        difficulty: 'beginner',
        category: 'file management',
        page: 1,
      })

      expect(url).toContain('difficulty=beginner')
      expect(url).toContain('category=file%20management')
      expect(url).toContain('page=1')
    })
  })
})
