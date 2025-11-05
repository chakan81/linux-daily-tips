import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('홈페이지가 정상적으로 로드된다', async ({ page }) => {
    await page.goto('/');
    
    // 페이지 타이틀 확인
    await expect(page).toHaveTitle(/Linux Daily Tips/);

    // 메인 헤딩 확인 (첫 번째 h1)
    await expect(page.locator('h1').first()).toContainText('Linux Daily Tips');
  });

  test('오늘의 팁이 표시된다', async ({ page }) => {
    await page.goto('/');
    
    // "Today's Tip" 섹션이 있는지 확인
    const todayTipSection = page.locator('text=Today\'s Tip').first();
    await expect(todayTipSection).toBeVisible();
    
    // 팁 제목이 표시되는지 확인
    const tipTitle = page.locator('h2').filter({ hasText: /명령어|리눅스|Linux/ }).first();
    await expect(tipTitle).toBeVisible();
    
    // 난이도 배지가 표시되는지 확인 (대소문자 무시)
    const difficultyBadge = page.locator('text=/beginner|intermediate|advanced/i').first();
    await expect(difficultyBadge).toBeVisible();
  });

  test('최근 팁 섹션이 표시된다', async ({ page }) => {
    await page.goto('/');

    // "Recent Tips" 헤딩 확인
    const recentTipsHeading = page.locator('h2').filter({ hasText: 'Recent Tips' });
    await expect(recentTipsHeading).toBeVisible();

    // 팁 링크가 최소 1개 이상 있는지 확인 (홈페이지는 커스텀 카드 스타일 사용)
    const tipLinks = page.locator('a[href^="/tips/"]');
    await expect(tipLinks.first()).toBeVisible();
  });

  test('"View All Tips" 링크가 작동한다', async ({ page }) => {
    await page.goto('/');

    // "View All Tips" 버튼 찾기
    const viewAllButton = page.locator('text=View All Tips').first();
    await expect(viewAllButton).toBeVisible();

    // 클릭 후 /tips 페이지로 이동하는지 확인 (페이지 로딩 대기)
    await Promise.all([
      page.waitForURL('/tips', { timeout: 10000 }),
      viewAllButton.click(),
    ]);
    await expect(page).toHaveURL('/tips');
  });

  test('통계 섹션이 표시된다', async ({ page }) => {
    await page.goto('/');
    
    // 통계 섹션 확인 (Total Tips, Daily Streak 등)
    const statsSection = page.locator('text=/Total Tips|Daily/i').first();
    await expect(statsSection).toBeVisible();
  });

  test('CTA 버튼이 작동한다', async ({ page }) => {
    await page.goto('/');
    
    // "Try Terminal" 또는 "Start Learning" 버튼 찾기
    const ctaButton = page.locator('text=/Try.*Terminal|Start Learning|Get Started/i').first();
    
    // 버튼이 있으면 클릭 가능한지 확인
    if (await ctaButton.count() > 0) {
      await expect(ctaButton).toBeVisible();
      await expect(ctaButton).toBeEnabled();
    }
  });
});
