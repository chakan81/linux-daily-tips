'use client';

import { Clock, Terminal, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { useTodayTip } from '@/lib/hooks/useTips'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { getDifficultyColor } from '@/lib/utils'

export function TodayTipSection() {
  const { data: todaysTip, isLoading, error } = useTodayTip();

  if (isLoading) {
    return (
      <section id="today-tip" className="container-awwwards py-16" aria-labelledby="todays-tip-heading">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 id="todays-tip-heading" className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Today&apos;s Linux Tip
            </h2>
            <p className="text-xl text-muted-foreground">
              Master a new command every day with practical examples
            </p>
          </div>
          <LoadingSpinner size="lg" text="Loading today's tip..." />
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section id="today-tip" className="container-awwwards py-16" aria-labelledby="todays-tip-heading">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 id="todays-tip-heading" className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Today&apos;s Linux Tip
            </h2>
            <p className="text-xl text-muted-foreground">
              Master a new command every day with practical examples
            </p>
          </div>
          <ErrorMessage
            type="error"
            title="Failed to load tip"
            message="Could not load today's tip. Please try again later."
          />
        </div>
      </section>
    );
  }

  if (!todaysTip) {
    return null;
  }
  return (
    <section id="today-tip" className="container-awwwards py-16" aria-labelledby="todays-tip-heading">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 id="todays-tip-heading" className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Today&apos;s Linux Tip
          </h2>
          <p className="text-xl text-muted-foreground">
            Master a new command every day with practical examples
          </p>
        </div>

        <div className="card-awwwards card-enter">
          <div className="flex items-start justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(todaysTip.difficulty)}`}>
                  {todaysTip.difficulty}
                </div>
                <span className="text-sm text-muted-foreground">{Array.isArray(todaysTip.category) ? todaysTip.category.join(', ') : todaysTip.category}</span>
              </div>
              <h3 className="text-2xl font-bold text-foreground mb-2">
                {todaysTip.title}
              </h3>
            </div>
          </div>

          {todaysTip.content && (
            <div className="prose prose-invert max-w-none mb-6 p-6 bg-gray-900/50 rounded-xl" role="region" aria-label="팁 미리보기">
              <p className="text-gray-300 leading-relaxed line-clamp-3">
                {todaysTip.content.split('\n').slice(0, 3).join(' ').substring(0, 200)}...
              </p>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/terminal"
              className="flex-1 inline-flex items-center justify-center gap-2 bg-black text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-800 transition-all duration-200 interactive"
              aria-label={`${todaysTip.title} 명령어를 터미널에서 직접 실습하기`}
            >
              <Terminal className="w-5 h-5" aria-hidden="true" />
              Practice in Terminal
            </Link>

            <Link
              href={`/tips/${todaysTip.id}`}
              className="flex-1 inline-flex items-center justify-center gap-2 bg-secondary text-secondary-foreground px-6 py-3 rounded-xl font-semibold hover:bg-secondary/80 transition-all duration-200 interactive"
              aria-label={`${todaysTip.title} 전체 가이드 읽기`}
            >
              <BookOpen className="w-5 h-5" aria-hidden="true" />
              Read Full Guide
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}