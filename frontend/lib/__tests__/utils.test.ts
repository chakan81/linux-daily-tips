/**
 * Unit Tests for lib/utils.ts
 *
 * Test coverage for all utility functions including:
 * - cn: Tailwind class name merging
 * - formatDate: Date formatting
 * - formatRelativeTime: Relative time formatting
 * - slugify: Text to URL slug conversion
 * - truncate: Text truncation
 * - getDifficultyColor: Difficulty badge colors
 * - getCategoryColor: Category badge colors
 * - debounce: Function debouncing
 * - throttle: Function throttling
 * - copyToClipboard: Clipboard operations
 * - generateId: Unique ID generation
 * - isValidEmail: Email validation
 * - formatFileSize: File size formatting
 * - getInitials: Name to initials conversion
 */

import {
  cn,
  formatDate,
  formatRelativeTime,
  slugify,
  truncate,
  getDifficultyColor,
  getCategoryColor,
  debounce,
  throttle,
  copyToClipboard,
  generateId,
  isValidEmail,
  formatFileSize,
  getInitials,
} from '../utils'

describe('cn (className merger)', () => {
  it('should merge class names correctly', () => {
    expect(cn('foo', 'bar')).toContain('foo')
    expect(cn('foo', 'bar')).toContain('bar')
  })

  it('should handle conditional classes', () => {
    expect(cn('foo', false && 'bar')).not.toContain('bar')
    expect(cn('foo', true && 'bar')).toContain('bar')
  })

  it('should handle undefined and null values', () => {
    expect(cn('foo', undefined, null)).toContain('foo')
    expect(cn('foo', undefined, null)).not.toContain('undefined')
    expect(cn('foo', undefined, null)).not.toContain('null')
  })

  it('should handle empty strings', () => {
    expect(cn('', 'foo')).toContain('foo')
  })

  it('should handle arrays of class names', () => {
    const result = cn(['foo', 'bar'])
    expect(result).toContain('foo')
    expect(result).toContain('bar')
  })
})

describe('formatDate', () => {
  it('should format Date object correctly', () => {
    const date = new Date('2025-01-15T10:30:00Z')
    const result = formatDate(date)
    expect(result).toContain('January')
    expect(result).toContain('15')
    expect(result).toContain('2025')
  })

  it('should format string date correctly', () => {
    const result = formatDate('2025-01-15')
    expect(result).toContain('January')
    expect(result).toContain('15')
    expect(result).toContain('2025')
  })

  it('should handle different date formats', () => {
    const result1 = formatDate('2025-12-31')
    expect(result1).toContain('December')
    expect(result1).toContain('31')

    const result2 = formatDate(new Date('2025-06-15T00:00:00Z'))
    expect(result2).toContain('June')
  })

  it('should handle invalid dates gracefully', () => {
    // Invalid dates will throw or return Invalid Date
    expect(() => formatDate('invalid-date')).toThrow()
  })
})

describe('formatRelativeTime', () => {
  beforeEach(() => {
    jest.useFakeTimers()
    jest.setSystemTime(new Date('2025-01-15T12:00:00Z'))
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('should return "just now" for very recent dates', () => {
    const date = new Date('2025-01-15T11:59:30Z') // 30 seconds ago
    expect(formatRelativeTime(date)).toBe('just now')
  })

  it('should format minutes correctly', () => {
    const date = new Date('2025-01-15T11:55:00Z') // 5 minutes ago
    expect(formatRelativeTime(date)).toBe('5 minutes ago')
  })

  it('should handle singular minute', () => {
    const date = new Date('2025-01-15T11:59:00Z') // 1 minute ago
    expect(formatRelativeTime(date)).toBe('1 minute ago')
  })

  it('should format hours correctly', () => {
    const date = new Date('2025-01-15T09:00:00Z') // 3 hours ago
    expect(formatRelativeTime(date)).toBe('3 hours ago')
  })

  it('should handle singular hour', () => {
    const date = new Date('2025-01-15T11:00:00Z') // 1 hour ago
    expect(formatRelativeTime(date)).toBe('1 hour ago')
  })

  it('should format days correctly', () => {
    const date = new Date('2025-01-12T12:00:00Z') // 3 days ago
    expect(formatRelativeTime(date)).toBe('3 days ago')
  })

  it('should handle singular day', () => {
    const date = new Date('2025-01-14T12:00:00Z') // 1 day ago
    expect(formatRelativeTime(date)).toBe('1 day ago')
  })

  it('should fall back to formatted date for old dates', () => {
    const date = new Date('2025-01-01T12:00:00Z') // 14 days ago (more than a week)
    const result = formatRelativeTime(date)
    expect(result).toContain('January')
    expect(result).toContain('2025')
  })

  it('should handle string dates', () => {
    const date = '2025-01-15T11:55:00Z'
    expect(formatRelativeTime(date)).toBe('5 minutes ago')
  })
})

describe('slugify', () => {
  it('should convert text to lowercase slug', () => {
    expect(slugify('Master File Permissions')).toBe('master-file-permissions')
  })

  it('should replace spaces with hyphens', () => {
    expect(slugify('Hello World')).toBe('hello-world')
  })

  it('should handle multiple spaces', () => {
    expect(slugify('Too   Many    Spaces')).toBe('too-many-spaces')
  })

  it('should remove special characters', () => {
    expect(slugify('Hello @World! #123')).toBe('hello-world-123')
    expect(slugify('Test (2025)')).toBe('test-2025')
  })

  it('should handle underscores', () => {
    expect(slugify('hello_world_test')).toBe('hello-world-test')
  })

  it('should trim leading and trailing hyphens', () => {
    expect(slugify('  Hello World  ')).toBe('hello-world')
    expect(slugify('---Test---')).toBe('test')
  })

  it('should handle empty string', () => {
    expect(slugify('')).toBe('')
  })

  it('should handle only special characters', () => {
    expect(slugify('!@#$%^&*()')).toBe('')
  })

  it('should preserve hyphens in text', () => {
    expect(slugify('pre-existing-hyphens')).toBe('pre-existing-hyphens')
  })

  it('should handle numbers', () => {
    expect(slugify('Article 123 Test')).toBe('article-123-test')
  })
})

describe('truncate', () => {
  it('should not truncate text shorter than max length', () => {
    const text = 'Short text'
    expect(truncate(text, 20)).toBe('Short text')
  })

  it('should truncate text longer than max length', () => {
    const text = 'This is a very long text that needs to be truncated'
    const result = truncate(text, 20)
    expect(result.length).toBeLessThanOrEqual(23) // 20 + '...'
    expect(result).toContain('...')
  })

  it('should not break words', () => {
    const text = 'This is a test'
    const result = truncate(text, 10)
    expect(result).toBe('This is a...')
  })

  it('should handle exact length', () => {
    const text = 'Exact length'
    expect(truncate(text, 12)).toBe('Exact length')
  })

  it('should handle empty string', () => {
    expect(truncate('', 10)).toBe('')
  })

  it('should handle single word longer than max length', () => {
    const text = 'Supercalifragilisticexpialidocious'
    const result = truncate(text, 10)
    expect(result).toContain('...')
  })
})

describe('getDifficultyColor', () => {
  it('should return green for beginner', () => {
    expect(getDifficultyColor('beginner')).toBe('bg-green-100 text-green-700')
    expect(getDifficultyColor('Beginner')).toBe('bg-green-100 text-green-700')
    expect(getDifficultyColor('BEGINNER')).toBe('bg-green-100 text-green-700')
  })

  it('should return yellow for intermediate', () => {
    expect(getDifficultyColor('intermediate')).toBe('bg-yellow-100 text-yellow-700')
    expect(getDifficultyColor('Intermediate')).toBe('bg-yellow-100 text-yellow-700')
  })

  it('should return red for advanced', () => {
    expect(getDifficultyColor('advanced')).toBe('bg-red-100 text-red-700')
    expect(getDifficultyColor('Advanced')).toBe('bg-red-100 text-red-700')
  })

  it('should return gray for unknown difficulty', () => {
    expect(getDifficultyColor('expert')).toBe('bg-gray-100 text-gray-700')
    expect(getDifficultyColor('unknown')).toBe('bg-gray-100 text-gray-700')
    expect(getDifficultyColor('')).toBe('bg-gray-100 text-gray-700')
  })
})

describe('getCategoryColor', () => {
  it('should return blue for file management', () => {
    expect(getCategoryColor('file management')).toBe('bg-blue-100 text-blue-700')
    expect(getCategoryColor('File Management')).toBe('bg-blue-100 text-blue-700')
  })

  it('should return purple for system administration', () => {
    expect(getCategoryColor('system administration')).toBe('bg-purple-100 text-purple-700')
  })

  it('should return green for networking', () => {
    expect(getCategoryColor('networking')).toBe('bg-green-100 text-green-700')
  })

  it('should return orange for search', () => {
    expect(getCategoryColor('search')).toBe('bg-orange-100 text-orange-700')
  })

  it('should return pink for text processing', () => {
    expect(getCategoryColor('text processing')).toBe('bg-pink-100 text-pink-700')
  })

  it('should return indigo for system monitoring', () => {
    expect(getCategoryColor('system monitoring')).toBe('bg-indigo-100 text-indigo-700')
  })

  it('should return red for security', () => {
    expect(getCategoryColor('security')).toBe('bg-red-100 text-red-700')
  })

  it('should return cyan for development', () => {
    expect(getCategoryColor('development')).toBe('bg-cyan-100 text-cyan-700')
  })

  it('should return gray for unknown category', () => {
    expect(getCategoryColor('unknown')).toBe('bg-gray-100 text-gray-700')
    expect(getCategoryColor('')).toBe('bg-gray-100 text-gray-700')
  })
})

describe('debounce', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('should debounce function calls', () => {
    const func = jest.fn()
    const debouncedFunc = debounce(func, 100)

    debouncedFunc()
    debouncedFunc()
    debouncedFunc()

    expect(func).not.toHaveBeenCalled()

    jest.advanceTimersByTime(100)
    expect(func).toHaveBeenCalledTimes(1)
  })

  it('should only call function after delay', () => {
    const func = jest.fn()
    const debouncedFunc = debounce(func, 200)

    debouncedFunc()
    jest.advanceTimersByTime(100)
    expect(func).not.toHaveBeenCalled()

    jest.advanceTimersByTime(100)
    expect(func).toHaveBeenCalledTimes(1)
  })

  it('should reset timer on subsequent calls', () => {
    const func = jest.fn()
    const debouncedFunc = debounce(func, 100)

    debouncedFunc()
    jest.advanceTimersByTime(50)

    debouncedFunc()
    jest.advanceTimersByTime(50)

    expect(func).not.toHaveBeenCalled()

    jest.advanceTimersByTime(50)
    expect(func).toHaveBeenCalledTimes(1)
  })

  it('should pass arguments to debounced function', () => {
    const func = jest.fn()
    const debouncedFunc = debounce(func, 100)

    debouncedFunc('arg1', 'arg2')
    jest.advanceTimersByTime(100)

    expect(func).toHaveBeenCalledWith('arg1', 'arg2')
  })

  it('should work with zero delay', () => {
    const func = jest.fn()
    const debouncedFunc = debounce(func, 0)

    debouncedFunc()
    jest.advanceTimersByTime(0)

    expect(func).toHaveBeenCalledTimes(1)
  })
})

describe('throttle', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('should throttle function calls', () => {
    const func = jest.fn()
    const throttledFunc = throttle(func, 100)

    throttledFunc()
    throttledFunc()
    throttledFunc()

    expect(func).toHaveBeenCalledTimes(1)

    jest.advanceTimersByTime(100)
    throttledFunc()
    expect(func).toHaveBeenCalledTimes(2)
  })

  it('should call function immediately on first call', () => {
    const func = jest.fn()
    const throttledFunc = throttle(func, 100)

    throttledFunc()
    expect(func).toHaveBeenCalledTimes(1)
  })

  it('should ignore calls during throttle period', () => {
    const func = jest.fn()
    const throttledFunc = throttle(func, 100)

    throttledFunc()
    expect(func).toHaveBeenCalledTimes(1)

    throttledFunc()
    throttledFunc()
    throttledFunc()
    expect(func).toHaveBeenCalledTimes(1)
  })

  it('should allow calls after throttle period', () => {
    const func = jest.fn()
    const throttledFunc = throttle(func, 100)

    throttledFunc()
    expect(func).toHaveBeenCalledTimes(1)

    jest.advanceTimersByTime(100)

    throttledFunc()
    expect(func).toHaveBeenCalledTimes(2)

    jest.advanceTimersByTime(100)

    throttledFunc()
    expect(func).toHaveBeenCalledTimes(3)
  })

  it('should pass arguments to throttled function', () => {
    const func = jest.fn()
    const throttledFunc = throttle(func, 100)

    throttledFunc('arg1', 'arg2')
    expect(func).toHaveBeenCalledWith('arg1', 'arg2')
  })
})

describe('copyToClipboard', () => {
  beforeEach(() => {
    // Reset clipboard mocks
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn(),
      },
    })
  })

  it('should copy text to clipboard using modern API', async () => {
    // Mock navigator.clipboard and window.isSecureContext
    Object.defineProperty(window, 'isSecureContext', {
      writable: true,
      value: true,
    })
    const writeTextMock = jest.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', {
      writable: true,
      value: { writeText: writeTextMock },
    })

    const result = await copyToClipboard('test text')

    expect(writeTextMock).toHaveBeenCalledWith('test text')
    expect(result).toBe(true)
  })

  it('should return true on success', async () => {
    Object.defineProperty(window, 'isSecureContext', {
      writable: true,
      value: true,
    })
    const writeTextMock = jest.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', {
      writable: true,
      value: { writeText: writeTextMock },
    })

    const result = await copyToClipboard('test')
    expect(result).toBe(true)
  })

  it('should return false on clipboard API failure', async () => {
    const writeTextMock = jest.fn().mockRejectedValue(new Error('Clipboard error'))
    Object.assign(navigator.clipboard, { writeText: writeTextMock })

    const result = await copyToClipboard('test')
    expect(result).toBe(false)
  })

  it('should handle empty string', async () => {
    Object.defineProperty(window, 'isSecureContext', {
      writable: true,
      value: true,
    })
    const writeTextMock = jest.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', {
      writable: true,
      value: { writeText: writeTextMock },
    })

    const result = await copyToClipboard('')
    expect(writeTextMock).toHaveBeenCalledWith('')
    expect(result).toBe(true)
  })
})

describe('generateId', () => {
  it('should generate unique IDs', () => {
    const id1 = generateId()
    const id2 = generateId()
    expect(id1).not.toBe(id2)
  })

  it('should generate ID without prefix', () => {
    const id = generateId()
    expect(id).toBeTruthy()
    expect(typeof id).toBe('string')
  })

  it('should generate ID with prefix', () => {
    const id = generateId('user_')
    expect(id).toMatch(/^user_/)
  })

  it('should generate ID with different prefixes', () => {
    const id1 = generateId('tip_')
    const id2 = generateId('draft_')

    expect(id1).toMatch(/^tip_/)
    expect(id2).toMatch(/^draft_/)
  })

  it('should generate alphanumeric IDs', () => {
    const id = generateId()
    expect(id).toMatch(/^[a-z0-9]+$/)
  })
})

describe('isValidEmail', () => {
  it('should validate correct email addresses', () => {
    expect(isValidEmail('test@example.com')).toBe(true)
    expect(isValidEmail('user.name@example.com')).toBe(true)
    expect(isValidEmail('user+tag@example.co.uk')).toBe(true)
    expect(isValidEmail('test123@test-domain.org')).toBe(true)
  })

  it('should reject invalid email addresses', () => {
    expect(isValidEmail('invalid')).toBe(false)
    expect(isValidEmail('invalid@')).toBe(false)
    expect(isValidEmail('@example.com')).toBe(false)
    expect(isValidEmail('invalid@example')).toBe(false)
    expect(isValidEmail('invalid example@test.com')).toBe(false)
  })

  it('should reject empty string', () => {
    expect(isValidEmail('')).toBe(false)
  })

  it('should reject emails without domain', () => {
    expect(isValidEmail('test@')).toBe(false)
    expect(isValidEmail('test@domain')).toBe(false)
  })

  it('should reject emails with spaces', () => {
    expect(isValidEmail('test @example.com')).toBe(false)
    expect(isValidEmail('test@ example.com')).toBe(false)
    expect(isValidEmail('test@example .com')).toBe(false)
  })

  it('should reject emails without @', () => {
    expect(isValidEmail('testexample.com')).toBe(false)
  })

  it('should handle edge cases', () => {
    expect(isValidEmail('a@b.c')).toBe(true)
    expect(isValidEmail('test..name@example.com')).toBe(true) // Simple regex allows this
  })
})

describe('formatFileSize', () => {
  it('should format bytes correctly', () => {
    expect(formatFileSize(0)).toBe('0 Bytes')
    expect(formatFileSize(500)).toBe('500 Bytes')
    expect(formatFileSize(1023)).toBe('1023 Bytes')
  })

  it('should format kilobytes correctly', () => {
    expect(formatFileSize(1024)).toBe('1 KB')
    expect(formatFileSize(1536)).toBe('1.5 KB')
    expect(formatFileSize(10240)).toBe('10 KB')
  })

  it('should format megabytes correctly', () => {
    expect(formatFileSize(1048576)).toBe('1 MB')
    expect(formatFileSize(5242880)).toBe('5 MB')
    expect(formatFileSize(10485760)).toBe('10 MB')
  })

  it('should format gigabytes correctly', () => {
    expect(formatFileSize(1073741824)).toBe('1 GB')
    expect(formatFileSize(5368709120)).toBe('5 GB')
  })

  it('should format terabytes correctly', () => {
    expect(formatFileSize(1099511627776)).toBe('1 TB')
    expect(formatFileSize(2199023255552)).toBe('2 TB')
  })

  it('should handle decimal values', () => {
    expect(formatFileSize(1536)).toBe('1.5 KB')
    expect(formatFileSize(1572864)).toBe('1.5 MB')
  })

  it('should round to 2 decimal places', () => {
    const size = 1234567 // Should be ~1.18 MB
    const result = formatFileSize(size)
    expect(result).toBe('1.18 MB')
  })
})

describe('getInitials', () => {
  it('should get initials from full name', () => {
    expect(getInitials('John Doe')).toBe('JD')
    expect(getInitials('Jane Smith')).toBe('JS')
  })

  it('should handle single name', () => {
    expect(getInitials('John')).toBe('J')
  })

  it('should handle three or more names', () => {
    expect(getInitials('John Michael Doe')).toBe('JM')
    expect(getInitials('Mary Jane Watson Parker')).toBe('MJ')
  })

  it('should convert to uppercase', () => {
    expect(getInitials('john doe')).toBe('JD')
    expect(getInitials('jane smith')).toBe('JS')
  })

  it('should limit to 2 initials', () => {
    expect(getInitials('A B C D E F')).toBe('AB')
  })

  it('should handle empty string', () => {
    expect(getInitials('')).toBe('')
  })

  it('should handle names with extra spaces', () => {
    expect(getInitials('John  Doe')).toBe('JD')
    expect(getInitials('  John   Doe  ')).toBe('JD')
  })

  it('should handle special characters in names', () => {
    expect(getInitials("John O'Connor")).toBe('JO')
    // Hyphenated names split on spaces only, so 'Jean-Paul Sartre' becomes ['Jean-Paul', 'Sartre']
    // Taking first character of each word: 'J' from 'Jean-Paul' and 'S' from 'Sartre'
    expect(getInitials('Jean-Paul Sartre')).toBe('JS')
  })
})
