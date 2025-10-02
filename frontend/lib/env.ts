import { z } from 'zod';

/**
 * Environment Variable Schema
 *
 * Defines and validates all environment variables used in the application.
 * This ensures type safety and catches configuration errors at startup.
 */
const envSchema = z.object({
  /**
   * Backend API URL
   * @example http://localhost:8000
   * @example https://api.linuxdailytips.com
   */
  NEXT_PUBLIC_API_URL: z.string().url('Invalid API URL format').min(1, 'API URL is required'),

  /**
   * Frontend base URL (used for canonical URLs, OG images, etc.)
   * @example http://localhost:3000
   * @example https://linuxdailytips.com
   */
  NEXT_PUBLIC_BASE_URL: z.string().url('Invalid base URL format').min(1, 'Base URL is required'),

  /**
   * Google Search Console verification code (optional)
   * @example abc123xyz456
   */
  NEXT_PUBLIC_GOOGLE_VERIFICATION: z.string().optional(),

  /**
   * Node environment
   */
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

/**
 * Validated environment variables type
 */
export type Env = z.infer<typeof envSchema>;

/**
 * Validate and parse environment variables
 *
 * @throws {Error} If environment variables are invalid
 * @returns {Env} Validated environment variables
 */
function validateEnv(): Env {
  const rawEnv = {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL,
    NEXT_PUBLIC_GOOGLE_VERIFICATION: process.env.NEXT_PUBLIC_GOOGLE_VERIFICATION,
    NODE_ENV: process.env.NODE_ENV,
  };

  try {
    const validatedEnv = envSchema.parse(rawEnv);

    // Log successful validation in development
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.log('✅ Environment variables validated successfully:', {
        NEXT_PUBLIC_API_URL: validatedEnv.NEXT_PUBLIC_API_URL,
        NEXT_PUBLIC_BASE_URL: validatedEnv.NEXT_PUBLIC_BASE_URL,
        NEXT_PUBLIC_GOOGLE_VERIFICATION: validatedEnv.NEXT_PUBLIC_GOOGLE_VERIFICATION ? '***' : 'not set',
        NODE_ENV: validatedEnv.NODE_ENV,
      });
    }

    return validatedEnv;
  } catch (error) {
    // Format validation errors for better readability
    if (error instanceof z.ZodError) {
      const errorMessages = error.issues.map((err) => {
        const path = err.path.join('.');
        return `  - ${path}: ${err.message}`;
      }).join('\n');

      console.error('❌ Invalid environment variables:\n' + errorMessages);
      console.error('\n💡 Make sure you have created a .env.local file with the required variables.');
      console.error('   See .env.local.example for reference.\n');
    } else {
      console.error('❌ Environment validation error:', error);
    }

    throw new Error('Invalid environment variables. Please check your .env.local configuration.');
  }
}

/**
 * Validated environment variables
 *
 * Import this object to access type-safe environment variables throughout the app.
 * @example
 * import { env } from '@/lib/env';
 *
 * const apiUrl = env.NEXT_PUBLIC_API_URL;
 */
export const env = validateEnv();
