import { expect, type Page } from '@playwright/test';
import { TIMEOUTS, SCROLL_THRESHOLD } from '../constants';

/**
 * Tips Page E2E Test Helper Class
 *
 * Tips 페이지 테스트에서 반복되는 패턴을 추상화한 헬퍼 클래스
 * - 페이지 네비게이션
 * - 검색/필터/정렬
 * - URL 상태 관리
 * - 활성 필터 관리
 */
export class TipsTestHelpers {
  constructor(private page: Page) {}

  /**
   * Tips 페이지로 이동 (쿼리 파라미터 지원)
   *
   * @param params URL 쿼리 파라미터 (예: { difficulty: 'beginner', category: 'file-system' })
   */
  async navigateToTips(params?: Record<string, string>) {
    const queryString = params
      ? '?' + new URLSearchParams(params).toString()
      : '';
    await this.page.goto(`/tips${queryString}`);
  }

  /**
   * Tips 페이지 헤딩이 표시되는지 확인
   */
  async verifyPageLoaded() {
    const heading = this.page.locator('h1').filter({ hasText: 'Linux Tips' });
    await expect(heading).toBeVisible();
  }

  /**
   * 팁 카드가 로드될 때까지 대기
   *
   * @param timeout 대기 시간 (기본: TIP_CARD_LOAD)
   */
  async waitForTipCards(timeout: number = TIMEOUTS.TIP_CARD_LOAD) {
    const tipCards = this.page.locator('[data-testid="tip-card"]');
    await expect(tipCards.first()).toBeVisible({ timeout });
  }

  /**
   * 검색 수행
   *
   * @param query 검색어
   * @param timeout URL 변경 대기 시간 (기본: SEARCH_DEBOUNCE)
   */
  async searchTips(query: string, timeout: number = TIMEOUTS.SEARCH_DEBOUNCE) {
    const searchInput = this.page.locator('input[aria-label="Search tips"]');
    await expect(searchInput).toBeVisible();
    await searchInput.fill(query);

    // URL 변경 대기 (debounce 300ms + 네트워크 + 렌더링)
    await expect(this.page).toHaveURL(new RegExp(`q=${query}`), { timeout });
  }

  /**
   * 난이도 필터 선택
   *
   * @param level 난이도 ('Beginner' | 'Intermediate' | 'Advanced')
   * @param timeout URL 변경 대기 시간 (기본: FILTER_UPDATE)
   */
  async selectDifficulty(
    level: 'Beginner' | 'Intermediate' | 'Advanced',
    timeout: number = TIMEOUTS.FILTER_UPDATE
  ) {
    const difficultyFilter = this.page.locator('#difficulty-filter');
    await expect(difficultyFilter).toBeVisible();
    await difficultyFilter.click();

    const option = this.page.locator('[role="option"]').filter({ hasText: level });
    await expect(option).toBeVisible();
    await option.click();

    // URL에 difficulty 파라미터 확인
    await expect(this.page).toHaveURL(
      new RegExp(`difficulty=${level.toLowerCase()}`),
      { timeout }
    );
  }

  /**
   * 카테고리 필터 선택
   *
   * @param categoryPattern 카테고리 패턴 (예: /file|system|network/i)
   * @returns 카테고리 옵션이 존재했는지 여부
   */
  async selectCategory(categoryPattern: RegExp): Promise<boolean> {
    const categoryFilter = this.page
      .locator('button')
      .filter({ hasText: /Category|All Categories/i })
      .first();
    await expect(categoryFilter).toBeVisible();
    await categoryFilter.click();

    const categoryOption = this.page
      .locator('[role="menuitem"]')
      .filter({ hasText: categoryPattern })
      .first();

    if (await categoryOption.count() > 0) {
      await categoryOption.click();
      await this.page.waitForURL(/category=/);
      return true;
    }

    return false;
  }

  /**
   * 정렬 옵션 선택
   *
   * @param sortPattern 정렬 옵션 패턴 (예: /Title.*A.*Z/i)
   * @param expectedParam 기대되는 URL 파라미터 (예: 'sort_by=title')
   * @returns 정렬 옵션이 존재했는지 여부
   */
  async selectSort(sortPattern: RegExp, expectedParam: string): Promise<boolean> {
    const sortDropdown = this.page
      .locator('button')
      .filter({ hasText: /Sort|Latest/i })
      .first();
    await expect(sortDropdown).toBeVisible();
    await sortDropdown.click();

    const sortOption = this.page.locator(`text=${sortPattern}`).first();

    if (await sortOption.count() > 0) {
      await sortOption.click();
      await this.page.waitForURL(new RegExp(expectedParam));
      return true;
    }

    return false;
  }

  /**
   * 첫 번째 팁 카드 클릭
   *
   * @param timeout 카드 표시 대기 시간 (기본: TIP_CARD_LOAD)
   */
  async clickFirstTipCard(timeout: number = TIMEOUTS.TIP_CARD_LOAD) {
    const firstCard = this.page.locator('[data-testid="tip-card"]').first();
    await expect(firstCard).toBeVisible({ timeout });
    await firstCard.click();
  }

  /**
   * 팁 상세 페이지로 이동했는지 확인
   */
  async verifyTipDetailPage() {
    // URL이 /tips/[id] 형식인지 확인
    await expect(this.page).toHaveURL(/\/tips\/tip_[A-Z0-9]+/);

    // 상세 페이지 콘텐츠가 로드되었는지 확인
    const tipContent = this.page.locator('text=/명령어|Linux|리눅스/').first();
    await expect(tipContent).toBeVisible();
  }

  /**
   * 페이지네이션 버튼 클릭
   *
   * @param pageNumber 이동할 페이지 번호
   * @returns 페이지 버튼이 존재했는지 여부
   */
  async goToPage(pageNumber: number): Promise<boolean> {
    const pageButton = this.page
      .locator('button')
      .filter({ hasText: pageNumber.toString() })
      .first();

    if (await pageButton.count() > 0) {
      await pageButton.click();
      await expect(this.page).toHaveURL(new RegExp(`page=${pageNumber}`));
      return true;
    }

    return false;
  }

  /**
   * 페이지 상단으로 스크롤되었는지 확인
   *
   * @param threshold 스크롤 임계값 (기본: SCROLL_THRESHOLD.TOP)
   */
  async verifyScrolledToTop(threshold: number = SCROLL_THRESHOLD.TOP) {
    const scrollY = await this.page.evaluate(() => window.scrollY);
    expect(scrollY).toBeLessThan(threshold);
  }

  /**
   * 활성 필터 칩 확인
   *
   * @param timeout 표시 대기 시간 (기본: FILTER_UPDATE)
   * @returns 활성 필터 칩 개수
   */
  async getActiveFilterCount(timeout: number = TIMEOUTS.FILTER_UPDATE): Promise<number> {
    const filterChips = this.page.locator('[data-testid="active-filter-chip"]');
    await expect(filterChips.first()).toBeVisible({ timeout });
    return await filterChips.count();
  }

  /**
   * 특정 활성 필터 칩 제거
   *
   * @param index 제거할 칩 인덱스 (기본 0, 첫 번째)
   * @param waitTime DOM 업데이트 대기 시간 (기본: DOM_UPDATE)
   * @returns 제거 전 칩 개수
   */
  async removeActiveFilter(index: number = 0, waitTime: number = TIMEOUTS.DOM_UPDATE): Promise<number> {
    const filterChips = this.page.locator('[data-testid="active-filter-chip"]');
    const chipCount = await filterChips.count();
    expect(chipCount).toBeGreaterThan(0);

    // Badge 자체가 클릭 가능
    await filterChips.nth(index).click();

    // DOM 업데이트 대기
    await this.page.waitForTimeout(waitTime);

    return chipCount;
  }

  /**
   * 모든 필터 제거 ("Clear All" 버튼)
   *
   * @param waitTime DOM 업데이트 대기 시간 (기본: DOM_UPDATE)
   * @returns "Clear All" 버튼이 존재했는지 여부
   */
  async clearAllFilters(waitTime: number = TIMEOUTS.DOM_UPDATE): Promise<boolean> {
    const clearAllButton = this.page
      .locator('button')
      .filter({ hasText: /Clear All/i })
      .first();

    if (await clearAllButton.count() > 0) {
      await clearAllButton.click();
      await this.page.waitForTimeout(waitTime);
      return true;
    }

    return false;
  }

  /**
   * URL에 특정 파라미터가 없는지 확인
   *
   * @param params 확인할 파라미터 목록 (예: ['difficulty', 'category'])
   */
  async verifyURLWithoutParams(params: string[]) {
    const url = this.page.url();
    for (const param of params) {
      expect(url).not.toContain(`${param}=`);
    }
  }

  /**
   * 검색 결과 헤더가 표시되는지 확인
   */
  async verifySearchResultHeader() {
    const searchResultText = this.page.locator('text=Search results for').first();
    await expect(searchResultText).toBeVisible();
  }

  /**
   * 특정 난이도 활성 필터 칩이 표시되는지 확인
   *
   * @param level 난이도
   */
  async verifyDifficultyChipVisible(level: 'Beginner' | 'Intermediate' | 'Advanced') {
    const activeFilterChip = this.page
      .locator('[data-testid="active-filter-chip"]')
      .filter({ hasText: new RegExp(level, 'i') })
      .first();
    await expect(activeFilterChip).toBeVisible();
  }
}
