import { Clock, Terminal, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { TipData, DifficultyLevel, TipCategory } from '@/lib/types'

// Mock data for demonstration - 백엔드 타입과 동기화
const todaysTip: TipData = {
  id: 1,
  title: "Master File Permissions with chmod",
  description: "Learn how to properly set file permissions using chmod command with octal and symbolic notation.",
  content: "# Understanding chmod\n\nThe `chmod` command is essential for managing file permissions in Linux...",
  command: "chmod 755 script.sh",
  difficulty: "Intermediate" as DifficultyLevel,
  category: "File Management" as TipCategory,
  estimatedTime: "5 min",
  tags: ["permissions", "security", "files"],
  slug: "master-file-permissions-chmod",
  publishDate: new Date().toISOString(),
  lastUpdated: new Date().toISOString(),
  viewCount: 1250,
  likeCount: 89,
  isPublished: true,
}

export function TodayTipSection() {
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
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  todaysTip.difficulty === 'Beginner' ? 'bg-green-200 dark:bg-green-900/30 text-green-800 dark:text-green-400' :
                  todaysTip.difficulty === 'Intermediate' ? 'bg-yellow-200 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400' :
                  'bg-red-200 dark:bg-red-900/30 text-red-800 dark:text-red-400'
                }`}>
                  {todaysTip.difficulty}
                </div>
                <span className="text-sm text-muted-foreground">{todaysTip.category}</span>
              </div>
              <h3 className="text-2xl font-bold text-foreground mb-2">
                {todaysTip.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {todaysTip.description}
              </p>
            </div>

            <div className="flex items-center gap-2 text-sm text-muted-foreground ml-6">
              <Clock className="w-4 h-4" aria-hidden="true" />
              <span aria-label={`예상 소요시간 ${todaysTip.estimatedTime}`}>{todaysTip.estimatedTime}</span>
            </div>
          </div>

          <div className="bg-gray-900 rounded-xl p-6 mb-6 terminal-container" role="region" aria-label="터미널 예제">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 bg-red-500 rounded-full" aria-hidden="true"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full" aria-hidden="true"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full" aria-hidden="true"></div>
              <span className="text-gray-400 text-sm ml-4">Terminal</span>
            </div>
            <div className="font-mono" role="code" aria-label={`명령어: ${todaysTip.command}`}>
              <div className="text-terminal-green">$ {todaysTip.command}</div>
              <div className="text-terminal-text mt-2 opacity-75">
                # Sets read, write, execute permissions for owner
                <br />
                # and read, execute permissions for group and others
              </div>
            </div>
          </div>

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