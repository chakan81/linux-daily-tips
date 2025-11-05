'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useCategories } from '@/lib/hooks/useTips';

interface TipsFiltersProps {
  difficulty?: string;
  category?: string;
  sortBy: string;
  order: 'asc' | 'desc';
  onDifficultyChange: (val?: string) => void;
  onCategoryChange: (val?: string) => void;
  onSortChange: (sortBy: string, order: 'asc' | 'desc') => void;
}

const DIFFICULTIES = ['beginner', 'intermediate', 'advanced'] as const;

const SORT_OPTIONS = [
  { label: 'Latest', value: 'publish_date:desc' },
  { label: 'Oldest', value: 'publish_date:asc' },
  { label: 'Title A-Z', value: 'title:asc' },
  { label: 'Title Z-A', value: 'title:desc' },
] as const;

/**
 * Tips filters component
 *
 * Provides filtering controls for tips list:
 * - Difficulty level (All/Beginner/Intermediate/Advanced)
 * - Category selection
 * - Sort order (Latest/Oldest/Title)
 *
 * @example
 * ```tsx
 * <TipsFilters
 *   difficulty={difficulty}
 *   category={category}
 *   sortBy="publish_date"
 *   order="desc"
 *   onDifficultyChange={setDifficulty}
 *   onCategoryChange={setCategory}
 *   onSortChange={(sortBy, order) => { setSortBy(sortBy); setOrder(order); }}
 * />
 * ```
 */
export function TipsFilters({
  difficulty,
  category,
  sortBy,
  order,
  onDifficultyChange,
  onCategoryChange,
  onSortChange,
}: TipsFiltersProps) {
  const currentSort = `${sortBy}:${order}`;

  // Fetch categories from API
  const { data: categoriesData, isLoading: categoriesLoading } = useCategories();
  const categories = categoriesData?.categories || [];

  const handleSortChange = (value: string) => {
    const [newSortBy, newOrder] = value.split(':') as [string, 'asc' | 'desc'];
    onSortChange(newSortBy, newOrder);
  };

  return (
    <div className="flex flex-wrap gap-4 items-center" role="region" aria-label="Filter tips">
      {/* Difficulty Filter */}
      <div className="flex flex-col gap-2">
        <label htmlFor="difficulty-filter" className="text-sm font-medium text-foreground sr-only">
          Difficulty Level
        </label>
        <Select
          value={difficulty || 'all'}
          onValueChange={(val) => onDifficultyChange(val === 'all' ? undefined : val)}
        >
          <SelectTrigger id="difficulty-filter" className="w-[180px]" aria-label="Filter by difficulty level">
            <SelectValue placeholder="Difficulty" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Difficulties</SelectItem>
            {DIFFICULTIES.map((diff) => (
              <SelectItem key={diff} value={diff}>
                {diff.charAt(0).toUpperCase() + diff.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Category Filter */}
      <div className="flex flex-col gap-2">
        <label htmlFor="category-filter" className="text-sm font-medium text-foreground sr-only">
          Category
        </label>
        <Select
          value={category || 'all'}
          onValueChange={(val) => onCategoryChange(val === 'all' ? undefined : val)}
          disabled={categoriesLoading}
        >
          <SelectTrigger id="category-filter" className="w-[200px]" aria-label="Filter by category">
            <SelectValue placeholder={categoriesLoading ? "Loading..." : "Category"} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat
                  .split('-')
                  .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ')}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Sort Filter */}
      <div className="flex flex-col gap-2">
        <label htmlFor="sort-filter" className="text-sm font-medium text-foreground sr-only">
          Sort Order
        </label>
        <Select value={currentSort} onValueChange={handleSortChange}>
          <SelectTrigger id="sort-filter" className="w-[160px]" aria-label="Sort tips">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            {SORT_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
