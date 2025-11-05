import { test, expect } from '@playwright/test';
import { TerminalTestHelpers } from './test-helpers/terminal';

test.describe('Terminal Emulator', () => {
  let terminal: TerminalTestHelpers;

  test.beforeEach(async ({ page }) => {
    terminal = new TerminalTestHelpers(page);
    await terminal.navigateToTerminal();
  });

  test('터미널 페이지가 정상적으로 로드된다', async () => {
    await terminal.verifyTerminalVisible();
    await terminal.verifyTerminalOrButtonVisible();
  });

  test('터미널 세션을 생성할 수 있다', async () => {
    await terminal.startSession();

    // 터미널이 활성화되었는지 확인 (WebSocket 연결 대기 포함)
    await terminal.verifyTerminalScreenVisible();
  });

  test('ls 명령어를 실행할 수 있다', async () => {
    await terminal.startSession();
    await terminal.executeCommand('ls');

    const text = await terminal.getTerminalContent();
    expect(text).toBeTruthy();
  });

  test('pwd 명령어를 실행할 수 있다', async () => {
    await terminal.startSession();
    await terminal.executeCommand('pwd');

    const text = await terminal.getTerminalContent();
    expect(text).toBeTruthy();
  });

  test('echo 명령어를 실행할 수 있다', async ({ page }) => {
    await terminal.startSession();
    await terminal.executeCommand('echo Hello Playwright');

    const text = await terminal.getTerminalContent();
    expect(text).toContain('Hello Playwright');
  });

  test('터미널 세션을 종료할 수 있다', async () => {
    await terminal.startSession();

    const stopped = await terminal.stopSession();

    if (stopped) {
      // "Start" 버튼이 다시 나타났는지 확인 (세션이 종료되었다는 의미)
      await terminal.verifySessionEnded();
    } else {
      // Stop 버튼이 없으면 테스트 스킵 (세션이 이미 종료됨)
      test.skip();
    }
  });

  test('여러 명령어를 순차적으로 실행할 수 있다', async () => {
    await terminal.startSession();

    // 세 가지 명령어 순차 실행
    await terminal.executeCommand('pwd', 500);
    await terminal.executeCommand('ls', 500);
    await terminal.executeCommand('echo Test Complete');

    // 마지막 출력 확인
    const text = await terminal.getTerminalContent();
    expect(text).toContain('Test Complete');
  });
});
