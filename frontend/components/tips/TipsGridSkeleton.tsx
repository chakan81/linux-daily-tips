import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';

interface TipsGridSkeletonProps {
  count?: number;
}

/**
 * Skeleton loading component for tips grid
 *
 * @param count - Number of skeleton cards to display (default: 12)
 *
 * @example
 * ```tsx
 * {isLoading && <TipsGridSkeleton count={9} />}
 * ```
 */
export function TipsGridSkeleton({ count = 12 }: TipsGridSkeletonProps) {
  return (
    <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, index) => (
        <Card key={index} className="overflow-hidden">
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-6 w-20 rounded-full" />
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>

            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex gap-2">
                <Skeleton className="h-6 w-20 rounded-full" />
                <Skeleton className="h-6 w-24 rounded-full" />
              </div>
              <Skeleton className="h-4 w-24" />
            </div>
          </CardContent>

          <CardFooter>
            <Skeleton className="h-10 w-full" />
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
