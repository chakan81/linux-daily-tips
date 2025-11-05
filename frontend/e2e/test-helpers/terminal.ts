import { expect, type Page } from '@playwright/test';
import { TIMEOUTS } from '../constants';

/**
 * Terminal E2E Test Helper Class
 *
 * 터미널 테스트에서 반복되는 패턴을 추상화한 헬퍼 클래스
 * - 세션 시작/종료
 * - 명령어 실행
 * - 출력 검증
 */
export class TerminalTestHelpers {
  constructor(private page: Page) {}

  /**
   * 터미널 페이지로 이동
   */
  async navigateToTerminal() {
    await this.page.goto('/terminal');
  }

  /**
   * 터미널 세션 시작
   * "Start Terminal" 버튼 클릭 및 WebSocket 연결 대기
   */
  async startSession() {
    const startButton = this.page
      .locator('button')
      .filter({ hasText: /Start|New.*Terminal|Create Session/i })
      .first();

    if (await startButton.count() > 0) {
      await startButton.click();
      await this.page.waitForTimeout(TIMEOUTS.WEBSOCKET_CONNECTION);
    }
  }

  /**
   * 터미널에 포커스 설정
   */
  async focusTerminal() {
    const terminalTextarea = this.page.locator('.xterm-helper-textarea');
    await terminalTextarea.click();
  }

  /**
   * 명령어 실행 (포커스 + 타이핑 + Enter + 대기)
   *
   * @param command 실행할 명령어 (예: 'ls', 'pwd', 'echo Hello')
   * @param waitTime 명령어 실행 후 대기 시간 (기본: COMMAND_EXECUTION)
   */
  async executeCommand(command: string, waitTime: number = TIMEOUTS.COMMAND_EXECUTION) {
    await this.focusTerminal();
    await this.page.keyboard.type(command);
    await this.page.keyboard.press('Enter');
    await this.page.waitForTimeout(waitTime);
  }

  /**
   * 터미널 출력 내용 가져오기
   *
   * @returns 터미널 화면의 텍스트 내용
   */
  async getTerminalContent(): Promise<string | null> {
    const terminalContent = this.page.locator('.xterm-screen');
    return await terminalContent.textContent();
  }

  /**
   * 터미널 페이지가 정상적으로 로드되었는지 확인
   */
  async verifyTerminalVisible() {
    const heading = this.page.locator('h1').filter({ hasText: /Terminal|터미널/ });
    await expect(heading).toBeVisible();
  }

  /**
   * "Start Terminal" 버튼 또는 xterm 터미널이 표시되는지 확인
   */
  async verifyTerminalOrButtonVisible() {
    const startButton = this.page
      .locator('button')
      .filter({ hasText: /Start|New.*Terminal|Create Session/i })
      .first();
    const terminalContainer = this.page.locator('.xterm');

    const hasButton = await startButton.count() > 0;
    const hasTerminal = await terminalContainer.count() > 0;

    expect(hasButton || hasTerminal).toBeTruthy();
  }

  /**
   * 터미널 세션 종료
   * "Stop" 또는 "Close" 버튼 클릭
   *
   * @returns 종료 버튼이 존재했는지 여부
   */
  async stopSession(): Promise<boolean> {
    const stopButton = this.page
      .locator('button')
      .filter({ hasText: /Stop|Close|End Session/i })
      .first();

    if (await stopButton.count() > 0) {
      await stopButton.click();
      await this.page.waitForTimeout(TIMEOUTS.SESSION_TERMINATION);
      return true;
    }

    return false;
  }

  /**
   * 세션 종료 후 "Start" 버튼이 다시 나타나는지 확인
   */
  async verifySessionEnded() {
    const newStartButton = this.page
      .locator('button')
      .filter({ hasText: /Start|New.*Terminal/i })
      .first();
    await expect(newStartButton).toBeVisible({ timeout: 5000 });
  }

  /**
   * 터미널 화면(.xterm-screen)이 표시되는지 확인
   */
  async verifyTerminalScreenVisible() {
    const terminalScreen = this.page.locator('.xterm-screen');
    await expect(terminalScreen).toBeVisible();
  }
}
