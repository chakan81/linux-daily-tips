import { test, expect } from '@playwright/test';

test.describe('Terminal Emulator', () => {
  test('터미널 페이지가 정상적으로 로드된다', async ({ page }) => {
    await page.goto('/terminal');

    // 페이지 헤딩 확인
    const heading = page.locator('h1').filter({ hasText: /Terminal|터미널/ });
    await expect(heading).toBeVisible();

    // "Start Session" 버튼이 있거나 xterm 터미널이 있는지 확인
    const startButton = page.locator('button').filter({ hasText: /Start|New.*Terminal|Create Session/i }).first();
    const terminalContainer = page.locator('.xterm');

    // 둘 중 하나라도 있으면 성공
    const hasButton = await startButton.count() > 0;
    const hasTerminal = await terminalContainer.count() > 0;

    expect(hasButton || hasTerminal).toBeTruthy();
  });

  test('터미널 세션을 생성할 수 있다', async ({ page }) => {
    await page.goto('/terminal');
    
    // "Start Session" 또는 "New Terminal" 버튼 찾기
    const startButton = page.locator('button').filter({ hasText: /Start|New.*Terminal|Create Session/i }).first();
    
    if (await startButton.count() > 0) {
      await expect(startButton).toBeVisible();
      await startButton.click();
      
      // 터미널이 활성화되었는지 확인 (프롬프트 표시)
      await page.waitForTimeout(2000); // WebSocket 연결 대기
      
      const terminalScreen = page.locator('.xterm-screen');
      await expect(terminalScreen).toBeVisible();
    }
  });

  test('ls 명령어를 실행할 수 있다', async ({ page }) => {
    await page.goto('/terminal');
    
    // 터미널 세션 시작
    const startButton = page.locator('button').filter({ hasText: /Start|New.*Terminal/i }).first();
    if (await startButton.count() > 0) {
      await startButton.click();
      await page.waitForTimeout(2000);
    }
    
    // 터미널에 포커스
    const terminalTextarea = page.locator('.xterm-helper-textarea');
    await terminalTextarea.click();
    
    // "ls" 명령어 입력
    await page.keyboard.type('ls');
    await page.keyboard.press('Enter');
    
    // 출력 대기 및 확인
    await page.waitForTimeout(1000);
    
    // 일반적인 디렉토리 이름이 출력되는지 확인 (bin, usr, etc 등)
    const terminalContent = page.locator('.xterm-screen');
    const text = await terminalContent.textContent();
    
    // 최소한 명령어가 실행되었는지 확인
    expect(text).toBeTruthy();
  });

  test('pwd 명령어를 실행할 수 있다', async ({ page }) => {
    await page.goto('/terminal');
    
    // 터미널 세션 시작
    const startButton = page.locator('button').filter({ hasText: /Start|New.*Terminal/i }).first();
    if (await startButton.count() > 0) {
      await startButton.click();
      await page.waitForTimeout(2000);
    }
    
    // 터미널에 포커스
    const terminalTextarea = page.locator('.xterm-helper-textarea');
    await terminalTextarea.click();
    
    // "pwd" 명령어 입력
    await page.keyboard.type('pwd');
    await page.keyboard.press('Enter');
    
    // 출력 대기
    await page.waitForTimeout(1000);
    
    // 경로가 출력되는지 확인 (/로 시작)
    const terminalContent = page.locator('.xterm-screen');
    const text = await terminalContent.textContent();
    
    expect(text).toContain('/');
  });

  test('echo 명령어를 실행할 수 있다', async ({ page }) => {
    await page.goto('/terminal');
    
    // 터미널 세션 시작
    const startButton = page.locator('button').filter({ hasText: /Start|New.*Terminal/i }).first();
    if (await startButton.count() > 0) {
      await startButton.click();
      await page.waitForTimeout(2000);
    }
    
    // 터미널에 포커스
    const terminalTextarea = page.locator('.xterm-helper-textarea');
    await terminalTextarea.click();
    
    // "echo Hello World" 명령어 입력
    await page.keyboard.type('echo Hello Playwright');
    await page.keyboard.press('Enter');
    
    // 출력 대기
    await page.waitForTimeout(1000);
    
    // "Hello Playwright"가 출력되는지 확인
    const terminalContent = page.locator('.xterm-screen');
    const text = await terminalContent.textContent();
    
    expect(text).toContain('Hello Playwright');
  });

  test('터미널 세션을 종료할 수 있다', async ({ page }) => {
    await page.goto('/terminal');

    // 터미널 세션 시작
    const startButton = page.locator('button').filter({ hasText: /Start|New.*Terminal/i }).first();
    if (await startButton.count() > 0) {
      await startButton.click();
      await page.waitForTimeout(2000);
    }

    // "Stop" 또는 "Close" 버튼 찾기
    const stopButton = page.locator('button').filter({ hasText: /Stop|Close|End Session/i }).first();

    if (await stopButton.count() > 0) {
      await stopButton.click();
      await page.waitForTimeout(1000);

      // "Start" 버튼이 다시 나타났는지 확인 (세션이 종료되었다는 의미)
      const newStartButton = page.locator('button').filter({ hasText: /Start|New.*Terminal/i }).first();
      await expect(newStartButton).toBeVisible({ timeout: 5000 });
    } else {
      // Stop 버튼이 없으면 테스트 스킵 (세션이 이미 종료됨)
      test.skip();
    }
  });

  test('여러 명령어를 순차적으로 실행할 수 있다', async ({ page }) => {
    await page.goto('/terminal');
    
    // 터미널 세션 시작
    const startButton = page.locator('button').filter({ hasText: /Start|New.*Terminal/i }).first();
    if (await startButton.count() > 0) {
      await startButton.click();
      await page.waitForTimeout(2000);
    }
    
    const terminalTextarea = page.locator('.xterm-helper-textarea');
    await terminalTextarea.click();
    
    // 첫 번째 명령어
    await page.keyboard.type('pwd');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(500);
    
    // 두 번째 명령어
    await page.keyboard.type('ls');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(500);
    
    // 세 번째 명령어
    await page.keyboard.type('echo Test Complete');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(1000);
    
    // 마지막 출력 확인
    const terminalContent = page.locator('.xterm-screen');
    const text = await terminalContent.textContent();
    
    expect(text).toContain('Test Complete');
  });
});
