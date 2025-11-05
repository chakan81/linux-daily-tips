'use client';

import { Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { useTipsList, useSearchTips } from '@/lib/hooks/useTips';
import { useDebouncedValue } from '@/lib/hooks/useDebouncedValue';
import {
  TipsGrid,
  TipsGridSkeleton,
  TipsFilters,
  SearchBar,
  ActiveFiltersChips,
  TipsPagination,
  EmptyState,
  NoResultsState,
} from '@/components/tips';
import { TipErrorState } from '@/components/tips';

/**
 * Tips List Content Component
 *
 * Provides a complete tips browsing experience with:
 * - Search functionality (debounced 300ms)
 * - Filtering by difficulty and category
 * - Sorting by date and title
 * - Pagination
 * - URL state management (query parameters)
 *
 * URL Structure:
 * /tips?page=2&difficulty=beginner&category=file-system&q=find&sort_by=publish_date&order=desc
 */
function TipsListContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // State (initialized from URL)
  const [page, setPage] = useState(1);
  const [difficulty, setDifficulty] = useState<string | undefined>(undefined);
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('publish_date');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');

  // Debounced search query
  const debouncedQuery = useDebouncedValue(searchQuery, 300);

  // URL → State synchronization (on mount and when URL changes)
  useEffect(() => {
    setPage(parseInt(searchParams.get('page') || '1'));
    setDifficulty(searchParams.get('difficulty') || undefined);
    setCategory(searchParams.get('category') || undefined);
    setSearchQuery(searchParams.get('q') || '');
    setSortBy(searchParams.get('sort_by') || 'publish_date');
    setOrder((searchParams.get('order') as 'asc' | 'desc') || 'desc');
  }, [searchParams]);

  // State → URL synchronization
  const updateURL = (updates: Partial<{
    page: number;
    difficulty?: string;
    category?: string;
    q?: string;
    sort_by?: string;
    order?: 'asc' | 'desc';
  }>) => {
    const params = new URLSearchParams();

    const newState = {
      page,
      difficulty,
      category,
      q: debouncedQuery,
      sort_by: sortBy,
      order,
      ...updates,
    };

    // Only add non-default values to URL
    if (newState.page > 1) params.set('page', newState.page.toString());
    if (newState.difficulty) params.set('difficulty', newState.difficulty);
    if (newState.category) params.set('category', newState.category);
    if (newState.q) params.set('q', newState.q);
    if (newState.sort_by !== 'publish_date') params.set('sort_by', newState.sort_by);
    if (newState.order !== 'desc') params.set('order', newState.order);

    const queryString = params.toString();
    router.push(`/tips${queryString ? `?${queryString}` : ''}`, { scroll: false });
  };

  // Trigger URL update when debounced query changes
  useEffect(() => {
    const currentQuery = searchParams.get('q') || '';

    if (debouncedQuery !== currentQuery) {
      updateURL({ q: debouncedQuery || undefined, page: 1 }); // Reset to page 1 on new search
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery]);

  // API calls - conditional based on search mode
  const isSearchMode = !!debouncedQuery;

  const listQuery = useTipsList({
    page,
    page_size: 12,
    difficulty,
    category,
    sort_by: sortBy,
    order,
  });

  const searchQuery_API = useSearchTips({
    q: debouncedQuery,
    page,
    page_size: 12,
    difficulty,
    category,
  });

  // Select appropriate query based on mode
  const { data, isLoading, isError, error, refetch } = isSearchMode
    ? searchQuery_API
    : listQuery;

  // Scroll to top on page change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [page]);

  // Event handlers
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    updateURL({ page: newPage });
  };

  const handleDifficultyChange = (val?: string) => {
    setDifficulty(val);
    updateURL({ difficulty: val, page: 1 });
  };

  const handleCategoryChange = (val?: string) => {
    setCategory(val);
    updateURL({ category: val, page: 1 });
  };

  const handleSortChange = (newSortBy: string, newOrder: 'asc' | 'desc') => {
    setSortBy(newSortBy);
    setOrder(newOrder);
    updateURL({ sort_by: newSortBy, order: newOrder, page: 1 });
  };

  const handleSearchChange = (val: string) => {
    setSearchQuery(val);
    // URL update happens via useEffect on debouncedQuery change
  };

  const handleRemoveFilter = (key: 'difficulty' | 'category') => {
    if (key === 'difficulty') {
      setDifficulty(undefined);
      updateURL({ difficulty: undefined, page: 1 });
    } else if (key === 'category') {
      setCategory(undefined);
      updateURL({ category: undefined, page: 1 });
    }
  };

  const handleClearAllFilters = () => {
    setDifficulty(undefined);
    setCategory(undefined);
    updateURL({ difficulty: undefined, category: undefined, page: 1 });
  };

  const handleResetAll = () => {
    setSearchQuery('');
    setDifficulty(undefined);
    setCategory(undefined);
    setSortBy('publish_date');
    setOrder('desc');
    setPage(1);
    router.push('/tips');
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    updateURL({ q: undefined, page: 1 });
  };

  const handleCardClick = (id: string) => {
    router.push(`/tips/${id}`);
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Linux Tips
          </h1>
          <p className="text-xl text-muted-foreground">
            Browse our collection of Linux tips and tricks
          </p>
        </div>

        <div className="space-y-8">
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            <SearchBar
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search tips..."
              disabled={false}
            />
            <TipsFilters
              difficulty={difficulty}
              category={category}
              sortBy={sortBy}
              order={order}
              onDifficultyChange={handleDifficultyChange}
              onCategoryChange={handleCategoryChange}
              onSortChange={handleSortChange}
            />
          </div>

          <TipsGridSkeleton count={12} />
        </div>
      </div>
    );
  }

  // Render error state
  if (isError) {
    return (
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Linux Tips
          </h1>
        </div>
        <TipErrorState
          error={error || new Error('Failed to load tips. Please try again.')}
          onRetry={refetch}
        />
      </div>
    );
  }

  const tips = data?.items || [];
  const totalItems = data?.total || 0;
  const totalPages = Math.ceil(totalItems / 12);
  const hasActiveFilters = !!(difficulty || category);
  const isEmpty = tips.length === 0;

  return (
    <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
          Linux Tips
        </h1>
        <p className="text-xl text-muted-foreground">
          {isSearchMode
            ? `Search results for "${debouncedQuery}"`
            : 'Browse our collection of Linux tips and tricks'}
        </p>
      </div>

      {/* Search and Filters */}
      <div className="space-y-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          <SearchBar
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search tips..."
            disabled={false}
          />
          <TipsFilters
            difficulty={difficulty}
            category={category}
            sortBy={sortBy}
            order={order}
            onDifficultyChange={handleDifficultyChange}
            onCategoryChange={handleCategoryChange}
            onSortChange={handleSortChange}
          />
        </div>

        {/* Active Filters Chips */}
        {hasActiveFilters && (
          <ActiveFiltersChips
            filters={{ difficulty, category }}
            onRemove={handleRemoveFilter}
            onClearAll={handleClearAllFilters}
          />
        )}
      </div>

      {/* Tips Grid or Empty States */}
      {isEmpty ? (
        isSearchMode ? (
          <NoResultsState
            query={debouncedQuery}
            onClearSearch={handleClearSearch}
            onReset={handleResetAll}
          />
        ) : (
          <EmptyState onReset={hasActiveFilters ? handleClearAllFilters : undefined} />
        )
      ) : (
        <>
          <TipsGrid tips={tips} onCardClick={handleCardClick} />

          {/* Pagination */}
          <TipsPagination
            currentPage={page}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={12}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  );
}

/**
 * Tips List Page (with Suspense boundary for useSearchParams)
 *
 * Wraps TipsListContent in a Suspense boundary to satisfy Next.js 16 requirements
 * for using useSearchParams() in a page component.
 */
export default function TipsListPage() {
  return (
    <Suspense fallback={
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Linux Tips
          </h1>
          <p className="text-xl text-muted-foreground">
            Browse our collection of Linux tips and tricks
          </p>
        </div>
        <TipsGridSkeleton count={12} />
      </div>
    }>
      <TipsListContent />
    </Suspense>
  );
}
