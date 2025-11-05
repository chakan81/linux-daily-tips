'use client';

import { Calendar } from 'lucide-react';
import { getDifficultyColor, formatDate } from '@/lib/utils';
import type { TipData } from '@/lib/types/tip';

/**
 * MetadataBadges Props
 */
interface MetadataBadgesProps {
  difficulty: TipData['difficulty'];
  categories: string[];
  publishDate: string;
  maxCategories?: number;
  className?: string;
}

/**
 * MetadataBadges Component
 * Displays difficulty, categories, and publish date badges
 */
export function MetadataBadges({
  difficulty,
  categories,
  publishDate,
  maxCategories = 3,
  className = '',
}: MetadataBadgesProps) {
  const visibleCategories = categories.slice(0, maxCategories);
  const remainingCount = categories.length - maxCategories;

  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      {/* Difficulty Badge */}
      <span
        className={`px-3 py-1 rounded-full text-xs font-semibold ${getDifficultyColor(difficulty)}`}
        aria-label={`Difficulty: ${difficulty}`}
      >
        {difficulty}
      </span>

      {/* Category Badges */}
      {visibleCategories.map((category, index) => (
        <span
          key={`${category}-${index}`}
          className="px-3 py-1 rounded-full text-xs font-medium bg-blue-900/30 text-blue-400 border border-blue-700/50"
          aria-label={`Category: ${category}`}
        >
          {category}
        </span>
      ))}

      {/* Remaining Categories Indicator */}
      {remainingCount > 0 && (
        <span
          className="px-3 py-1 rounded-full text-xs font-medium bg-gray-800/50 text-gray-400"
          aria-label={`${remainingCount} more categories`}
        >
          +{remainingCount} more
        </span>
      )}

      {/* Publish Date */}
      <time
        dateTime={publishDate}
        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-gray-800/50 text-gray-400"
        aria-label={`Published on ${formatDate(publishDate)}`}
      >
        <Calendar className="w-3.5 h-3.5" aria-hidden="true" />
        <span>{formatDate(publishDate)}</span>
      </time>
    </div>
  );
}
