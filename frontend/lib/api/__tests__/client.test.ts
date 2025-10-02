/**
 * Unit Tests for lib/api/client.ts
 *
 * Test coverage for:
 * - handleApiError: Error handling for various error types
 * - apiRequest: Generic API request wrapper
 * - Axios instance configuration and interceptors
 */

import axios, { AxiosError } from 'axios'
import type { ApiErrorResponse } from '../client'

// Mock env module before importing client
jest.mock('@/lib/env', () => ({
  env: {
    NEXT_PUBLIC_API_URL: 'http://localhost:8000',
    NEXT_PUBLIC_BASE_URL: 'http://localhost:3000',
    NODE_ENV: 'test',
  },
}))

// Mock axios before importing client
jest.mock('axios', () => {
  const mockInstance = {
    request: jest.fn(),
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() },
    },
  }

  return {
    __esModule: true,
    default: {
      create: jest.fn(() => mockInstance),
      isAxiosError: jest.fn((error: any) => error && error.isAxiosError === true),
    },
    isAxiosError: jest.fn((error: any) => error && error.isAxiosError === true),
  }
})

// Import after mocks
import { handleApiError, apiRequest, apiClient } from '../client'

// Access the mock instance through apiClient
const mockAxiosInstance = apiClient as any

describe('handleApiError', () => {
  describe('Axios errors with response', () => {
    it('should handle error with message and statusCode', () => {
      const axiosError: AxiosError<ApiErrorResponse> = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Not found',
            statusCode: 404,
          },
          status: 404,
          statusText: 'Not Found',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request failed with status code 404',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toBe('Not found')
      expect((error as any).statusCode).toBe(404)
    })

    it('should handle validation errors with field details', () => {
      const axiosError: AxiosError<ApiErrorResponse> = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Validation failed',
            statusCode: 400,
            errors: {
              email: ['Invalid email format', 'Email is required'],
              password: ['Password is too short'],
            },
          },
          status: 400,
          statusText: 'Bad Request',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request failed with status code 400',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toContain('Validation failed')
      expect(error.message).toContain('email')
      expect(error.message).toContain('Invalid email format')
      expect(error.message).toContain('password')
      expect(error.message).toContain('Password is too short')
    })

    it('should handle error without message field', () => {
      const axiosError: AxiosError<any> = {
        isAxiosError: true,
        response: {
          data: {},
          status: 500,
          statusText: 'Internal Server Error',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request failed with status code 500',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toBe('An error occurred')
    })

    it('should handle multiple validation errors for same field', () => {
      const axiosError: AxiosError<ApiErrorResponse> = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Validation failed',
            statusCode: 400,
            errors: {
              username: ['Too short', 'Contains invalid characters', 'Already taken'],
            },
          },
          status: 400,
          statusText: 'Bad Request',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request failed with status code 400',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toContain('username')
      expect(error.message).toContain('Too short')
      expect(error.message).toContain('Contains invalid characters')
      expect(error.message).toContain('Already taken')
    })

    it('should handle 401 Unauthorized error', () => {
      const axiosError: AxiosError<ApiErrorResponse> = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Unauthorized access',
            statusCode: 401,
          },
          status: 401,
          statusText: 'Unauthorized',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request failed with status code 401',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toBe('Unauthorized access')
      expect((error as any).statusCode).toBe(401)
    })

    it('should handle 403 Forbidden error', () => {
      const axiosError: AxiosError<ApiErrorResponse> = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Access forbidden',
            statusCode: 403,
          },
          status: 403,
          statusText: 'Forbidden',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request failed with status code 403',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toBe('Access forbidden')
      expect((error as any).statusCode).toBe(403)
    })

    it('should handle 500 Internal Server Error', () => {
      const axiosError: AxiosError<ApiErrorResponse> = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Internal server error',
            statusCode: 500,
          },
          status: 500,
          statusText: 'Internal Server Error',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request failed with status code 500',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toBe('Internal server error')
      expect((error as any).statusCode).toBe(500)
    })
  })

  describe('Axios errors without response', () => {
    it('should handle network error (no response)', () => {
      const axiosError: AxiosError = {
        isAxiosError: true,
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Network Error',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toBe('Network Error')
    })

    it('should handle timeout error', () => {
      const axiosError: AxiosError = {
        isAxiosError: true,
        code: 'ECONNABORTED',
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'timeout of 30000ms exceeded',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toContain('timeout')
    })

    it('should handle request cancelled error', () => {
      const axiosError: AxiosError = {
        isAxiosError: true,
        code: 'ERR_CANCELED',
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request canceled',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toBe('Request canceled')
    })
  })

  describe('Non-Axios errors', () => {
    it('should handle standard Error object', () => {
      const standardError = new Error('Something went wrong')
      const error = handleApiError(standardError)
      expect(error).toBe(standardError)
      expect(error.message).toBe('Something went wrong')
    })

    it('should handle string error', () => {
      const error = handleApiError('String error')
      expect(error).toBeInstanceOf(Error)
      expect(error.message).toBe('Unknown error occurred')
    })

    it('should handle null/undefined', () => {
      const error1 = handleApiError(null)
      expect(error1).toBeInstanceOf(Error)
      expect(error1.message).toBe('Unknown error occurred')

      const error2 = handleApiError(undefined)
      expect(error2).toBeInstanceOf(Error)
      expect(error2.message).toBe('Unknown error occurred')
    })

    it('should handle object without Error prototype', () => {
      const error = handleApiError({ custom: 'error' })
      expect(error).toBeInstanceOf(Error)
      expect(error.message).toBe('Unknown error occurred')
    })
  })

  describe('Edge cases', () => {
    it('should handle empty error object', () => {
      const axiosError: AxiosError<ApiErrorResponse> = {
        isAxiosError: true,
        response: {
          data: {
            message: '',
            statusCode: 400,
          },
          status: 400,
          statusText: 'Bad Request',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: '',
      }

      const error = handleApiError(axiosError)
      expect(error.message).toBe('An error occurred')
    })

    it('should handle error with empty validation errors', () => {
      const axiosError: AxiosError<ApiErrorResponse> = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Validation failed',
            statusCode: 400,
            errors: {},
          },
          status: 400,
          statusText: 'Bad Request',
          headers: {},
          config: {} as any,
        },
        config: {} as any,
        toJSON: () => ({}),
        name: 'AxiosError',
        message: 'Request failed with status code 400',
      }

      const error = handleApiError(axiosError)
      // Empty errors object adds " - " separator
      expect(error.message).toBe('Validation failed - ')
    })
  })
})

describe('apiRequest', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should make successful API request and return data', async () => {
    const mockData = { id: 1, name: 'Test' }
    const mockResponse = { data: mockData }

    // Mock the apiClient.request method
    mockAxiosInstance.request.mockResolvedValue(mockResponse)

    const result = await apiRequest<typeof mockData>({
      url: '/api/test',
      method: 'GET',
    })

    expect(result).toEqual(mockData)
    expect(mockAxiosInstance.request).toHaveBeenCalledWith({
      url: '/api/test',
      method: 'GET',
    })
  })

  it('should handle POST request with data', async () => {
    const requestData = { name: 'New Item' }
    const responseData = { id: 1, ...requestData }
    const mockResponse = { data: responseData }

    mockAxiosInstance.request.mockResolvedValue(mockResponse)

    const result = await apiRequest<typeof responseData>({
      url: '/api/items',
      method: 'POST',
      data: requestData,
    })

    expect(result).toEqual(responseData)
    expect(mockAxiosInstance.request).toHaveBeenCalledWith({
      url: '/api/items',
      method: 'POST',
      data: requestData,
    })
  })

  it('should handle PUT request', async () => {
    const updateData = { name: 'Updated Item' }
    const mockResponse = { data: { id: 1, ...updateData } }

    mockAxiosInstance.request.mockResolvedValue(mockResponse)

    const result = await apiRequest({
      url: '/api/items/1',
      method: 'PUT',
      data: updateData,
    })

    expect(result).toEqual({ id: 1, ...updateData })
  })

  it('should handle DELETE request', async () => {
    const mockResponse = { data: { success: true } }

    mockAxiosInstance.request.mockResolvedValue(mockResponse)

    const result = await apiRequest({
      url: '/api/items/1',
      method: 'DELETE',
    })

    expect(result).toEqual({ success: true })
  })

  it('should throw handled error on API failure', async () => {
    const axiosError: AxiosError<ApiErrorResponse> = {
      isAxiosError: true,
      response: {
        data: {
          message: 'Not found',
          statusCode: 404,
        },
        status: 404,
        statusText: 'Not Found',
        headers: {},
        config: {} as any,
      },
      config: {} as any,
      toJSON: () => ({}),
      name: 'AxiosError',
      message: 'Request failed with status code 404',
    }

    mockAxiosInstance.request.mockRejectedValue(axiosError)

    await expect(
      apiRequest({ url: '/api/missing', method: 'GET' })
    ).rejects.toThrow('Not found')
  })

  it('should handle network errors', async () => {
    const networkError: AxiosError = {
      isAxiosError: true,
      config: {} as any,
      toJSON: () => ({}),
      name: 'AxiosError',
      message: 'Network Error',
    }

    mockAxiosInstance.request.mockRejectedValue(networkError)

    await expect(
      apiRequest({ url: '/api/test', method: 'GET' })
    ).rejects.toThrow('Network Error')
  })

  it('should handle validation errors', async () => {
    const validationError: AxiosError<ApiErrorResponse> = {
      isAxiosError: true,
      response: {
        data: {
          message: 'Validation failed',
          statusCode: 400,
          errors: {
            email: ['Invalid email'],
          },
        },
        status: 400,
        statusText: 'Bad Request',
        headers: {},
        config: {} as any,
      },
      config: {} as any,
      toJSON: () => ({}),
      name: 'AxiosError',
      message: 'Request failed with status code 400',
    }

    mockAxiosInstance.request.mockRejectedValue(validationError)

    await expect(
      apiRequest({ url: '/api/test', method: 'POST' })
    ).rejects.toThrow(/Validation failed.*email.*Invalid email/)
  })

  it('should handle timeout errors', async () => {
    const timeoutError: AxiosError = {
      isAxiosError: true,
      code: 'ECONNABORTED',
      config: {} as any,
      toJSON: () => ({}),
      name: 'AxiosError',
      message: 'timeout of 30000ms exceeded',
    }

    mockAxiosInstance.request.mockRejectedValue(timeoutError)

    await expect(
      apiRequest({ url: '/api/test', method: 'GET' })
    ).rejects.toThrow(/timeout/)
  })

  it('should pass custom headers', async () => {
    const mockResponse = { data: { success: true } }
    mockAxiosInstance.request.mockResolvedValue(mockResponse)

    await apiRequest({
      url: '/api/test',
      method: 'GET',
      headers: {
        'X-Custom-Header': 'custom-value',
      },
    })

    expect(mockAxiosInstance.request).toHaveBeenCalledWith({
      url: '/api/test',
      method: 'GET',
      headers: {
        'X-Custom-Header': 'custom-value',
      },
    })
  })

  it('should handle empty response', async () => {
    const mockResponse = { data: null }
    mockAxiosInstance.request.mockResolvedValue(mockResponse)

    const result = await apiRequest({
      url: '/api/test',
      method: 'DELETE',
    })

    expect(result).toBeNull()
  })
})
