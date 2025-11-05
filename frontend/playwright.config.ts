import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E 테스트 설정
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // 테스트 파일 경로
  testDir: './e2e',

  // 전체 테스트 타임아웃
  timeout: 30 * 1000,

  // 각 테스트 재시도 횟수 (CI에서만)
  retries: process.env.CI ? 2 : 0,

  // 병렬 워커 수
  workers: process.env.CI ? 1 : undefined,

  // Reporter 설정
  reporter: [
    ['html'],
    ['list'],
    ['json', { outputFile: 'e2e-results.json' }]
  ],

  // 공통 설정
  use: {
    // 기본 URL (Docker 환경 감지)
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',

    // 스크린샷 (실패 시에만)
    screenshot: 'only-on-failure',

    // 비디오 녹화 (Docker 환경에서는 비활성화, ffmpeg 필요)
    video: process.env.DOCKER_ENV ? 'off' : 'retain-on-failure',

    // 트레이스 (실패 시에만)
    trace: 'on-first-retry',
  },

  // 프로젝트 설정 (브라우저별)
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Docker 환경에서 시스템 Chromium 사용
        ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH && {
          launchOptions: {
            executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
          },
        }),
      },
    },
  ],

  // 개발 서버 설정 (테스트 전 자동 시작)
  // Docker 환경에서는 이미 실행 중이므로 webServer 설정 비활성화
  webServer: process.env.DOCKER_ENV ? undefined : {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
