import { ArrowRight, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { DifficultyLevel, TipCategory } from '@/lib/types'

interface RecentTipPreview {
  id: number
  title: string
  difficulty: DifficultyLevel
  category: TipCategory
  date: string
}

const recentTips: RecentTipPreview[] = [
  {
    id: 2,
    title: "Find Files with locate Command",
    difficulty: "Beginner" as DifficultyLevel,
    category: "Search" as TipCategory,
    date: "Yesterday"
  },
  {
    id: 3,
    title: "Process Management with htop",
    difficulty: "Advanced" as DifficultyLevel,
    category: "System Monitoring" as TipCategory,
    date: "2 days ago"
  },
  {
    id: 4,
    title: "Network Configuration with ip command",
    difficulty: "Intermediate" as DifficultyLevel,
    category: "Networking" as TipCategory,
    date: "3 days ago"
  },
]

export function RecentTipsSection() {
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
          {recentTips.map((tip, index) => (
            <Link
              key={tip.id}
              href={`/tips/${tip.id}`}
              className="card-awwwards interactive group card-enter"
              style={{ animationDelay: `${index * 100}ms` }}
              aria-label={`${tip.title} - ${tip.difficulty} 난이도, ${tip.category} 카테고리, ${tip.date}에 게시됨`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  tip.difficulty === 'Beginner' ? 'bg-green-200 dark:bg-green-900/30 text-green-800 dark:text-green-400' :
                  tip.difficulty === 'Intermediate' ? 'bg-yellow-200 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400' :
                  'bg-red-200 dark:bg-red-900/30 text-red-800 dark:text-red-400'
                }`}>
                  {tip.difficulty}
                </div>
                <span className="text-sm text-muted-foreground">{tip.date}</span>
              </div>

              <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-accent-600 transition-colors">
                {tip.title}
              </h3>

              <p className="text-sm text-muted-foreground mb-4">{tip.category}</p>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-accent-600">Read more</span>
                <ArrowRight className="w-4 h-4 text-accent-600 group-hover:translate-x-1 transition-transform" aria-hidden="true" />
              </div>
            </Link>
          ))}
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