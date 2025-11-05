import { test, expect } from '@playwright/test';

test.describe('Tips Page', () => {
  test('Tips 페이지가 정상적으로 로드된다', async ({ page }) => {
    await page.goto('/tips');
    
    // 페이지 헤딩 확인
    const heading = page.locator('h1').filter({ hasText: 'Linux Tips' });
    await expect(heading).toBeVisible();
    
    // 팁 카드가 표시되는지 확인
    const tipCards = page.locator('[data-testid="tip-card"]');
    await expect(tipCards.first()).toBeVisible({ timeout: 10000 });
  });

  test('검색 기능이 작동한다', async ({ page }) => {
    await page.goto('/tips');

    // 검색창 찾기
    const searchInput = page.locator('input[aria-label="Search tips"]');
    await expect(searchInput).toBeVisible();

    // 검색어 입력 (300ms debounce + 추가 대기)
    await searchInput.fill('find');

    // URL 변경을 대기 (debounce 300ms + 네트워크 + 렌더링)
    await expect(page).toHaveURL(/q=find/, { timeout: 10000 });

    // 검색 결과 헤더 확인
    const searchResultText = page.locator('text=Search results for').first();
    await expect(searchResultText).toBeVisible();
  });

  test('난이도 필터가 작동한다', async ({ page }) => {
    await page.goto('/tips');

    // 필터 드롭다운 찾기 (ID로 정확히 찾기)
    const difficultyFilter = page.locator('#difficulty-filter');
    await expect(difficultyFilter).toBeVisible();

    // 필터 열기
    await difficultyFilter.click();

    // "Beginner" 옵션 선택
    const beginnerOption = page.locator('[role="option"]').filter({ hasText: 'Beginner' });
    await expect(beginnerOption).toBeVisible();
    await beginnerOption.click();

    // URL에 difficulty=beginner 파라미터 확인
    await expect(page).toHaveURL(/difficulty=beginner/, { timeout: 5000 });

    // 활성 필터 칩 확인
    const activeFilterChip = page.locator('[data-testid="active-filter-chip"]').filter({ hasText: /Beginner/i }).first();
    await expect(activeFilterChip).toBeVisible();
  });

  test('카테고리 필터가 작동한다', async ({ page }) => {
    await page.goto('/tips');
    
    // 카테고리 필터 드롭다운 찾기
    const categoryFilter = page.locator('button').filter({ hasText: /Category|All Categories/i }).first();
    await expect(categoryFilter).toBeVisible();
    
    // 필터 열기
    await categoryFilter.click();
    
    // 첫 번째 카테고리 옵션 선택 (예: "File Management")
    const categoryOption = page.locator('[role="menuitem"]').filter({ hasText: /file|system|network/i }).first();
    if (await categoryOption.count() > 0) {
      await categoryOption.click();
      
      // URL에 category 파라미터 확인
      await page.waitForURL(/category=/);
    }
  });

  test('정렬 기능이 작동한다', async ({ page }) => {
    await page.goto('/tips');
    
    // 정렬 드롭다운 찾기
    const sortDropdown = page.locator('button').filter({ hasText: /Sort|Latest/i }).first();
    await expect(sortDropdown).toBeVisible();
    
    // 드롭다운 열기
    await sortDropdown.click();
    
    // "Title A-Z" 옵션 선택
    const titleSortOption = page.locator('text=/Title.*A.*Z/i').first();
    if (await titleSortOption.count() > 0) {
      await titleSortOption.click();
      
      // URL에 sort_by=title 파라미터 확인
      await page.waitForURL(/sort_by=title/);
    }
  });

  test('팁 카드를 클릭하면 상세 페이지로 이동한다', async ({ page }) => {
    await page.goto('/tips');
    
    // 첫 번째 팁 카드 클릭
    const firstTipCard = page.locator('[data-testid="tip-card"]').first();
    await expect(firstTipCard).toBeVisible({ timeout: 10000 });
    await firstTipCard.click();
    
    // URL이 /tips/[id] 형식인지 확인
    await expect(page).toHaveURL(/\/tips\/tip_[A-Z0-9]+/);
    
    // 상세 페이지가 로드되었는지 확인
    const tipContent = page.locator('text=/명령어|Linux|리눅스/').first();
    await expect(tipContent).toBeVisible();
  });

  test('페이지네이션이 작동한다', async ({ page }) => {
    await page.goto('/tips');
    
    // 페이지네이션 버튼 확인 (page=2가 있는지)
    const page2Button = page.locator('button').filter({ hasText: '2' }).first();
    
    if (await page2Button.count() > 0) {
      await page2Button.click();
      
      // URL에 page=2 파라미터 확인
      await expect(page).toHaveURL(/page=2/);
      
      // 페이지 상단으로 스크롤되었는지 확인 (선택적)
      const scrollY = await page.evaluate(() => window.scrollY);
      expect(scrollY).toBeLessThan(100);
    }
  });

  test('활성 필터를 제거할 수 있다', async ({ page }) => {
    // 필터가 적용된 URL로 직접 이동
    await page.goto('/tips?difficulty=beginner&category=file-system');
    
    // 활성 필터 칩 확인
    const filterChips = page.locator('[data-testid="active-filter-chip"]');
    const chipCount = await filterChips.count();
    
    if (chipCount > 0) {
      // 첫 번째 필터 칩의 X 버튼 클릭
      const removeButton = filterChips.first().locator('button');
      await removeButton.click();
      
      // URL에서 해당 필터가 제거되었는지 확인
      await page.waitForTimeout(500);
      const currentUrl = page.url();
      
      // 남은 필터 칩 수가 줄었는지 확인
      const newChipCount = await filterChips.count();
      expect(newChipCount).toBeLessThan(chipCount);
    }
  });

  test('"Clear All" 버튼이 모든 필터를 제거한다', async ({ page }) => {
    // 여러 필터가 적용된 URL로 이동
    await page.goto('/tips?difficulty=beginner&category=file-system');
    
    // "Clear All" 버튼 찾기
    const clearAllButton = page.locator('button').filter({ hasText: /Clear All/i }).first();
    
    if (await clearAllButton.count() > 0) {
      await clearAllButton.click();
      
      // URL에서 모든 필터 파라미터가 제거되었는지 확인
      await page.waitForTimeout(500);
      const url = page.url();
      expect(url).not.toContain('difficulty=');
      expect(url).not.toContain('category=');
    }
  });
});
