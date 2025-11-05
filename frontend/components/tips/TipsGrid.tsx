import { TipCard } from './TipCard';
import type { TipData } from '@/lib/types';

interface TipsGridProps {
  tips: TipData[];
  onCardClick: (id: string) => void;
}

/**
 * Tips grid layout component
 *
 * Displays tips in a responsive 3-column grid
 * - Mobile: 1 column
 * - Tablet: 2 columns
 * - Desktop: 3 columns
 *
 * @param tips - Array of tips to display
 * @param onCardClick - Handler for tip card clicks
 *
 * @example
 * ```tsx
 * <TipsGrid
 *   tips={tipsData}
 *   onCardClick={(id) => router.push(`/tips/${id}`)}
 * />
 * ```
 */
export function TipsGrid({ tips, onCardClick }: TipsGridProps) {
  return (
    <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      {tips.map((tip) => (
        <TipCard
          key={tip.id}
          tip={tip}
          onClick={() => onCardClick(String(tip.id))}
        />
      ))}
    </div>
  );
}
