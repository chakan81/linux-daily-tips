'use client';

import { BookOpen, Users, TrendingUp } from 'lucide-react'
import { useStats } from '@/lib/hooks/useStats'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'

export function StatsSection() {
  const { data: stats, isLoading, error } = useStats();

  if (isLoading) {
    return (
      <section className="container-awwwards py-16" aria-label="서비스 통계" role="region">
        <h2 className="sr-only">Linux Daily Tips 서비스 통계</h2>
        <LoadingSpinner size="lg" text="Loading statistics..." />
      </section>
    );
  }

  if (error) {
    return (
      <section className="container-awwwards py-16" aria-label="서비스 통계" role="region">
        <h2 className="sr-only">Linux Daily Tips 서비스 통계</h2>
        <ErrorMessage
          type="error"
          message="Failed to load statistics. Please try again later."
        />
      </section>
    );
  }

  if (!stats) {
    return null;
  }
  return (
    <section className="container-awwwards py-16" aria-label="서비스 통계" role="region">
      {/* Screen reader only heading */}
      <h2 className="sr-only">Linux Daily Tips 서비스 통계</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-100 rounded-2xl mb-4" aria-hidden="true">
            <BookOpen className="w-8 h-8 text-accent-600" aria-hidden="true" />
          </div>
          <div className="text-3xl font-bold text-foreground mb-2">
            {stats.totalTips.toLocaleString()}+
          </div>
          <p className="text-muted-foreground">Linux Tips & Commands</p>
        </div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-100 rounded-2xl mb-4" aria-hidden="true">
            <Users className="w-8 h-8 text-accent-600" aria-hidden="true" />
          </div>
          <div className="text-3xl font-bold text-foreground mb-2">
            {stats.activeUsers.toLocaleString()}+
          </div>
          <p className="text-muted-foreground">Active Learners</p>
        </div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-100 rounded-2xl mb-4" aria-hidden="true">
            <TrendingUp className="w-8 h-8 text-accent-600" aria-hidden="true" />
          </div>
          <div className="text-3xl font-bold text-foreground mb-2">
            {stats.completionRate}%
          </div>
          <p className="text-muted-foreground">Success Rate</p>
        </div>
      </div>
    </section>
  )
}