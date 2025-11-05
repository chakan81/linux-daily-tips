import { X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ActiveFiltersChipsProps {
  filters: {
    difficulty?: string;
    category?: string;
  };
  onRemove: (key: 'difficulty' | 'category') => void;
  onClearAll: () => void;
}

/**
 * Active filters chips component
 *
 * Displays active filters as removable badges with a clear all button
 *
 * @param filters - Object containing active filters
 * @param onRemove - Handler to remove individual filter
 * @param onClearAll - Handler to clear all filters
 *
 * @example
 * ```tsx
 * <ActiveFiltersChips
 *   filters={{ difficulty: 'beginner', category: 'networking' }}
 *   onRemove={(key) => setFilter(key, undefined)}
 *   onClearAll={() => resetAllFilters()}
 * />
 * ```
 */
export function ActiveFiltersChips({
  filters,
  onRemove,
  onClearAll,
}: ActiveFiltersChipsProps) {
  const activeFilters = Object.entries(filters).filter(
    ([_, value]) => value !== undefined && value !== null
  );

  // Don't render if no active filters
  if (activeFilters.length === 0) {
    return null;
  }

  const formatFilterLabel = (key: string, value: string) => {
    const formattedKey = key.charAt(0).toUpperCase() + key.slice(1);
    const formattedValue = value
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    return `${formattedKey}: ${formattedValue}`;
  };

  return (
    <div className="flex flex-wrap items-center gap-2" role="region" aria-label="Active filters">
      <span className="text-sm text-muted-foreground font-medium">Active filters:</span>

      {activeFilters.map(([key, value]) => (
        <Badge
          key={key}
          variant="secondary"
          className="gap-1 pr-1 cursor-pointer hover:bg-secondary/80 transition-colors"
          role="button"
          tabIndex={0}
          onClick={() => onRemove(key as 'difficulty' | 'category')}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onRemove(key as 'difficulty' | 'category');
            }
          }}
          aria-label={`Remove ${key} filter: ${value}`}
        >
          {formatFilterLabel(key, value as string)}
          <X className="w-3 h-3" aria-hidden="true" />
        </Badge>
      ))}

      {activeFilters.length >= 2 && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearAll}
          className="h-6 px-2 text-xs"
          aria-label="Clear all filters"
        >
          Clear All
        </Button>
      )}
    </div>
  );
}
