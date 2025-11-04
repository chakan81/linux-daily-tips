'use client';

import { ArrowRight, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { useRecentTips } from '@/lib/hooks/useTips'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { getDifficultyColor } from '@/lib/utils'

export function RecentTipsSection() {
  const { data: recentTips, isLoading, error } = useRecentTips(3);

  if (isLoading) {
    return (
      <section className="container-awwwards py-16">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Recent Tips
            </h2>
            <p className="text-xl text-muted-foreground">
              Catch up on what you might have missed
            </p>
          </div>
          <LoadingSpinner size="lg" text="Loading recent tips..." />
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="container-awwwards py-16">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Recent Tips
            </h2>
            <p className="text-xl text-muted-foreground">
              Catch up on what you might have missed
            </p>
          </div>
          <ErrorMessage
            type="error"
            message="Failed to load recent tips. Please try again later."
          />
        </div>
      </section>
    );
  }

  if (!recentTips || !recentTips.items || recentTips.items.length === 0) {
    return null;
  }
  return (
    <section className="container-awwwards py-16">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Recent Tips
          </h2>
          <p className="text-xl text-muted-foreground">
            Catch up on what you might have missed
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {recentTips.items.map((tip, index) => {
            // Format the date as relative time
            // 백엔드가 publish_date (snake_case)로 반환
            const publishDate = new Date((tip as any).publish_date || tip.publishDate);
            const now = new Date();
            const diffInDays = Math.floor((now.getTime() - publishDate.getTime()) / (1000 * 60 * 60 * 24));
            const dateText = diffInDays === 0 ? 'Today' : diffInDays === 1 ? 'Yesterday' : `${diffInDays} days ago`;

            return (
              <Link
                key={tip.id}
                href={`/tips/${tip.id}`}
                className="card-awwwards interactive group card-enter"
                style={{ animationDelay: `${index * 100}ms` }}
                aria-label={`${tip.title} - ${tip.difficulty} 난이도, ${tip.category} 카테고리, ${dateText}에 게시됨`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(tip.difficulty)}`}>
                    {tip.difficulty}
                  </div>
                  <span className="text-sm text-muted-foreground">{dateText}</span>
                </div>

                <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-accent-600 transition-colors">
                  {tip.title}
                </h3>

                <p className="text-sm text-muted-foreground mb-4">{Array.isArray(tip.category) ? tip.category.join(', ') : tip.category}</p>

                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-accent-600">Read more</span>
                  <ArrowRight className="w-4 h-4 text-accent-600 group-hover:translate-x-1 transition-transform" aria-hidden="true" />
                </div>
              </Link>
            );
          })}
        </div>

        <div className="text-center mt-12">
          <Link
            href="/tips"
            className="inline-flex items-center justify-center gap-2 bg-secondary text-secondary-foreground px-8 py-4 rounded-2xl font-semibold hover:bg-secondary/80 transition-all duration-200 interactive"
            aria-label="모든 리눅스 팁 목록 보기"
          >
            <BookOpen className="w-5 h-5" aria-hidden="true" />
            View All Tips
            <ArrowRight className="w-5 h-5" aria-hidden="true" />
          </Link>
        </div>
      </div>
    </section>
  )
}