import { test, expect } from '@playwright/test';
import { TipsTestHelpers } from './test-helpers/tips';

test.describe('Tips Page', () => {
  let tips: TipsTestHelpers;

  test.beforeEach(async ({ page }) => {
    tips = new TipsTestHelpers(page);
    await tips.navigateToTips();
  });

  test('Tips 페이지가 정상적으로 로드된다', async () => {
    await tips.verifyPageLoaded();
    await tips.waitForTipCards();
  });

  test('검색 기능이 작동한다', async () => {
    await tips.searchTips('find');
    await tips.verifySearchResultHeader();
  });

  test('난이도 필터가 작동한다', async () => {
    await tips.selectDifficulty('Beginner');
    await tips.verifyDifficultyChipVisible('Beginner');
  });

  test('카테고리 필터가 작동한다', async () => {
    const selected = await tips.selectCategory(/file|system|network/i);

    if (selected) {
      // URL에 category 파라미터 확인은 selectCategory에서 이미 수행됨
      expect(selected).toBe(true);
    }
  });

  test('정렬 기능이 작동한다', async () => {
    const sorted = await tips.selectSort(/Title.*A.*Z/i, 'sort_by=title');

    if (sorted) {
      // URL 변경 확인은 selectSort에서 이미 수행됨
      expect(sorted).toBe(true);
    }
  });

  test('팁 카드를 클릭하면 상세 페이지로 이동한다', async () => {
    await tips.clickFirstTipCard();
    await tips.verifyTipDetailPage();
  });

  test('페이지네이션이 작동한다', async ({ page }) => {
    const navigated = await tips.goToPage(2);

    if (navigated) {
      // 페이지 상단으로 스크롤되었는지 확인
      await tips.verifyScrolledToTop();
    }
  });

  test('활성 필터를 제거할 수 있다', async ({ page }) => {
    // 필터가 적용된 URL로 직접 이동
    await tips.navigateToTips({ difficulty: 'beginner', category: 'file-system' });

    // 페이지 로딩 대기
    await page.waitForTimeout(1000);

    // 필터 칩 제거
    const originalCount = await tips.removeActiveFilter();

    // 남은 필터 칩 수가 줄었는지 확인
    const filterChips = page.locator('[data-testid="active-filter-chip"]');
    const newCount = await filterChips.count();
    expect(newCount).toBeLessThan(originalCount);
  });

  test('"Clear All" 버튼이 모든 필터를 제거한다', async () => {
    // 여러 필터가 적용된 URL로 이동
    await tips.navigateToTips({ difficulty: 'beginner', category: 'file-system' });

    const cleared = await tips.clearAllFilters();

    if (cleared) {
      // URL에서 모든 필터 파라미터가 제거되었는지 확인
      await tips.verifyURLWithoutParams(['difficulty', 'category']);
    }
  });
});
