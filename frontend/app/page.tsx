import { Suspense } from 'react'
import { Metadata } from 'next'
import { HeroSection, TodayTipSection, RecentTipsSection, StatsSection, CTASection } from '@/components/sections'

export const metadata: Metadata = {
  title: 'Home',
}

function LoadingSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-8 bg-gray-200 rounded-lg w-3/4"></div>
      <div className="h-64 bg-gray-200 rounded-2xl"></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
        ))}
      </div>
    </div>
  )
}

export default function HomePage() {
  return (
    <div className="page-enter">
      {/* Skip to main content link for keyboard navigation */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-black focus:text-white focus:rounded-lg focus:text-sm font-medium"
      >
        메인 콘텐츠로 바로가기
      </a>

      {/* Screen reader only - page description */}
      <div className="sr-only">
        <h1>Linux Daily Tips - 매일 새로운 리눅스 명령어를 배우는 웹서비스</h1>
        <p>터미널 실습과 함께 리눅스 명령어를 단계별로 학습할 수 있습니다. 초보자부터 고급 사용자까지 모든 수준의 팁을 제공합니다.</p>
      </div>

      <main id="main-content">
        <Suspense fallback={<LoadingSkeleton />}>
          <HeroSection />
          <TodayTipSection />
          <RecentTipsSection />
          <StatsSection />
          <CTASection />
        </Suspense>
      </main>
    </div>
  )
}