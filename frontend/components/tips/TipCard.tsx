import { ArrowRight } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { getDifficultyColor, formatRelativeTime } from '@/lib/utils';
import type { TipData } from '@/lib/types';

interface TipCardProps {
  tip: TipData;
  onClick: () => void;
}

/**
 * Individual tip card component
 *
 * Reuses design from RecentTipsSection for consistency
 *
 * @param tip - Tip data to display
 * @param onClick - Click handler for card interaction
 *
 * @example
 * ```tsx
 * <TipCard
 *   tip={tipData}
 *   onClick={() => router.push(`/tips/${tipData.id}`)}
 * />
 * ```
 */
export function TipCard({ tip, onClick }: TipCardProps) {
  const publishDate = new Date(tip.publishDate);
  const dateText = formatRelativeTime(publishDate);

  // Ensure category is always an array
  const categories: string[] = Array.isArray(tip.category) ? tip.category : [tip.category];

  return (
    <Card
      className="group hover:scale-105 transition-transform duration-300 cursor-pointer h-full flex flex-col"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      aria-label={`${tip.title} - ${tip.difficulty} difficulty, ${categories.join(', ')} category, published ${dateText}`}
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <CardTitle className="text-xl font-bold line-clamp-2 group-hover:text-accent-600 transition-colors">
            {tip.title}
          </CardTitle>
          <Badge className={getDifficultyColor(tip.difficulty)}>
            {tip.difficulty}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 flex-grow">
        <p className="text-muted-foreground line-clamp-2">
          {tip.description}
        </p>

        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex gap-2 flex-wrap">
            {categories.slice(0, 2).map((cat: string) => (
              <Badge key={cat} variant="outline">
                {cat}
              </Badge>
            ))}
            {categories.length > 2 && (
              <Badge variant="secondary">
                +{categories.length - 2} more
              </Badge>
            )}
          </div>
          <time className="text-sm text-muted-foreground" dateTime={publishDate.toISOString()}>
            {dateText}
          </time>
        </div>
      </CardContent>

      <CardFooter>
        <Button
          variant="ghost"
          className="w-full group-hover:bg-primary/10 justify-between"
          asChild
        >
          <span>
            Read More
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" aria-hidden="true" />
          </span>
        </Button>
      </CardFooter>
    </Card>
  );
}
