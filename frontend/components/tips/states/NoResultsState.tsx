import { Search } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface NoResultsStateProps {
  query: string;
  onClearSearch: () => void;
  onReset: () => void;
}

/**
 * No results state component for search queries
 *
 * Displays when search returns no results
 *
 * @param query - The search query that returned no results
 * @param onClearSearch - Callback to clear only the search query
 * @param onReset - Callback to reset all filters and search
 *
 * @example
 * ```tsx
 * {tips.length === 0 && searchQuery && (
 *   <NoResultsState
 *     query={searchQuery}
 *     onClearSearch={() => setSearchQuery('')}
 *     onReset={handleResetAll}
 *   />
 * )}
 * ```
 */
export function NoResultsState({
  query,
  onClearSearch,
  onReset,
}: NoResultsStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="rounded-full bg-muted p-6 mb-6">
        <Search className="w-12 h-12 text-muted-foreground" aria-hidden="true" />
      </div>

      <h3 className="text-2xl font-bold text-foreground mb-2">
        No results for &quot;{query}&quot;
      </h3>

      <p className="text-muted-foreground mb-6 max-w-md">
        We couldn&apos;t find any tips matching your search. Try different keywords or clear your filters.
      </p>

      <div className="flex flex-wrap gap-3 justify-center">
        <Button onClick={onClearSearch} variant="outline" size="lg">
          Clear Search
        </Button>
        <Button onClick={onReset} variant="default" size="lg">
          Reset All Filters
        </Button>
      </div>
    </div>
  );
}
