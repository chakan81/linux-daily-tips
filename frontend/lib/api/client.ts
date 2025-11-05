import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { CustomError } from '@/lib/types/common';
import { env } from '@/lib/env';

/**
 * API Error Types
 */
export interface ApiErrorResponse {
  message: string;
  statusCode: number;
  errors?: Record<string, string[]>;
}

/**
 * API Client Configuration
 */
const API_BASE_URL = env.NEXT_PUBLIC_API_URL;
const API_TIMEOUT = 30000; // 30 seconds

/**
 * Create Axios Instance
 */
const createAxiosInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request Interceptor
  instance.interceptors.request.use(
    (config) => {
      // Add authentication token if available
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('auth-token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }

      // Log request in development
      if (env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log('🚀 API Request:', {
          method: config.method?.toUpperCase(),
          url: config.url,
          data: config.data,
        });
      }

      return config;
    },
    (error) => {
      console.error('❌ Request Error:', error);
      return Promise.reject(error);
    }
  );

  // Response Interceptor
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      // Log response in development
      if (env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log('✅ API Response:', {
          status: response.status,
          url: response.config.url,
          data: response.data,
        });
      }

      return response;
    },
    (error: AxiosError<ApiErrorResponse>) => {
      // Handle different error scenarios
      if (error.response) {
        // Server responded with error status
        const { status, data } = error.response;

        console.error('❌ API Error Response:', {
          status,
          message: data?.message || 'An error occurred',
          errors: data?.errors,
        });

        // Handle specific status codes
        switch (status) {
          case 401:
            // Unauthorized - clear auth and redirect to login
            if (typeof window !== 'undefined') {
              localStorage.removeItem('auth-token');
              // Optionally redirect to login page
              // window.location.href = '/login';
            }
            break;
          case 403:
            console.error('🚫 Access forbidden');
            break;
          case 404:
            console.error('🔍 Resource not found');
            break;
          case 500:
            console.error('💥 Server error');
            break;
        }
      } else if (error.request) {
        // Request was made but no response received
        console.error('📡 Network Error: No response received', error.message);
      } else {
        // Something else happened
        console.error('⚠️ Error:', error.message);
      }

      return Promise.reject(error);
    }
  );

  return instance;
};

/**
 * API Client Instance
 */
export const apiClient = createAxiosInstance();

/**
 * Generic API Request Function
 */
export async function apiRequest<T>(
  config: AxiosRequestConfig
): Promise<T> {
  try {
    const response = await apiClient.request<T>(config);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * Error Handler
 */
export function handleApiError(error: unknown): Error {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;

    if (axiosError.response?.data) {
      const { message, statusCode, errors } = axiosError.response.data;

      // Create detailed error message
      let errorMessage = message || 'An error occurred';

      if (errors) {
        const errorDetails = Object.entries(errors)
          .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
          .join('; ');
        errorMessage += ` - ${errorDetails}`;
      }

      const error: CustomError = new Error(errorMessage);
      error.statusCode = statusCode;
      return error;
    }

    return new Error(axiosError.message || 'Network error occurred');
  }

  return error instanceof Error ? error : new Error('Unknown error occurred');
}
