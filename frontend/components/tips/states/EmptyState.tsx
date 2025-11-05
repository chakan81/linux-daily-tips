import { FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EmptyStateProps {
  onReset?: () => void;
}

/**
 * Empty state component when no tips are found
 *
 * Displays when the tips list is empty (no filters applied)
 *
 * @param onReset - Optional callback to reset all filters
 *
 * @example
 * ```tsx
 * {tips.length === 0 && !hasFilters && (
 *   <EmptyState onReset={handleResetFilters} />
 * )}
 * ```
 */
export function EmptyState({ onReset }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="rounded-full bg-muted p-6 mb-6">
        <FileText className="w-12 h-12 text-muted-foreground" aria-hidden="true" />
      </div>

      <h3 className="text-2xl font-bold text-foreground mb-2">
        No tips found
      </h3>

      <p className="text-muted-foreground mb-6 max-w-md">
        It looks like there are no tips available yet. Check back later for new content!
      </p>

      {onReset && (
        <Button onClick={onReset} variant="outline" size="lg">
          Clear All Filters
        </Button>
      )}
    </div>
  );
}
