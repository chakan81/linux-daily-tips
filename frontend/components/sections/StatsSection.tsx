import { BookOpen, Users, TrendingUp } from 'lucide-react'
import { StatsData, DifficultyLevel, TipCategory } from '@/lib/types'

const stats: StatsData = {
  totalTips: 365,
  activeUsers: 12500,
  completionRate: 87,
  dailyActiveUsers: 850,
  weeklyActiveUsers: 4200,
  monthlyActiveUsers: 12500,
  popularCategories: [
    { category: "File Management" as TipCategory, count: 45, percentage: 12.3 },
    { category: "System Monitoring" as TipCategory, count: 38, percentage: 10.4 },
    { category: "Networking" as TipCategory, count: 32, percentage: 8.8 },
  ],
  difficultyDistribution: [
    { difficulty: "Beginner" as DifficultyLevel, count: 120, percentage: 32.9 },
    { difficulty: "Intermediate" as DifficultyLevel, count: 150, percentage: 41.1 },
    { difficulty: "Advanced" as DifficultyLevel, count: 95, percentage: 26.0 },
  ],
}

export function StatsSection() {
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