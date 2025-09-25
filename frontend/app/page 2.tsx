import { Suspense } from 'react'
import { Metadata } from 'next'
import Link from 'next/link'
import {
  Terminal,
  BookOpen,
  Clock,
  TrendingUp,
  Users,
  Star,
  ArrowRight,
  Play,
  Code,
  Zap
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Home',
}

// Mock data for demonstration
const todaysTip = {
  id: 1,
  title: "Master File Permissions with chmod",
  description: "Learn how to properly set file permissions using chmod command with octal and symbolic notation.",
  command: "chmod 755 script.sh",
  difficulty: "Intermediate",
  category: "File Management",
  estimatedTime: "5 min",
}

const stats = {
  totalTips: 365,
  activeUsers: 12500,
  completionRate: 87,
}

const recentTips = [
  {
    id: 2,
    title: "Find Files with locate Command",
    difficulty: "Beginner",
    category: "Search",
    date: "Yesterday"
  },
  {
    id: 3,
    title: "Process Management with htop",
    difficulty: "Advanced",
    category: "System Monitoring",
    date: "2 days ago"
  },
  {
    id: 4,
    title: "Network Configuration with ip command",
    difficulty: "Intermediate",
    category: "Networking",
    date: "3 days ago"
  },
]

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

function HeroSection() {
  return (
    <section className="container-awwwards py-16 md:py-24">
      <div className="max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 bg-white/60 backdrop-blur-sm px-4 py-2 rounded-full border border-gray-200 mb-8">
          <Star className="w-4 h-4 text-yellow-500 fill-current" />
          <span className="text-sm font-medium text-gray-700">Daily Linux Learning</span>
          <Star className="w-4 h-4 text-yellow-500 fill-current" />
        </div>

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight gradient-text mb-6">
          Master Linux
          <br />
          <span className="text-accent-600">One Command at a Time</span>
        </h1>

        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed">
          Learn essential Linux commands through daily tips, interactive terminal practice,
          and hands-on tutorials. Perfect for developers, sysadmins, and Linux enthusiasts.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/terminal"
            className="inline-flex items-center justify-center gap-2 bg-black text-white px-8 py-4 rounded-2xl font-semibold hover:bg-gray-800 transition-all duration-200 interactive group"
          >
            <Terminal className="w-5 h-5" />
            Try Interactive Terminal
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            href="#today-tip"
            className="inline-flex items-center justify-center gap-2 bg-white/70 backdrop-blur-sm text-gray-900 px-8 py-4 rounded-2xl font-semibold border border-gray-200 hover:bg-white hover:shadow-card-hover transition-all duration-200 interactive"
          >
            <Play className="w-5 h-5" />
            View Today's Tip
          </Link>
        </div>
      </div>
    </section>
  )
}

function StatsSection() {
  return (
    <section className="container-awwwards py-16">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-100 rounded-2xl mb-4">
            <BookOpen className="w-8 h-8 text-accent-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">
            {stats.totalTips.toLocaleString()}+
          </div>
          <p className="text-gray-600">Linux Tips & Commands</p>
        </div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-100 rounded-2xl mb-4">
            <Users className="w-8 h-8 text-accent-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">
            {stats.activeUsers.toLocaleString()}+
          </div>
          <p className="text-gray-600">Active Learners</p>
        </div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent-100 rounded-2xl mb-4">
            <TrendingUp className="w-8 h-8 text-accent-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">
            {stats.completionRate}%
          </div>
          <p className="text-gray-600">Success Rate</p>
        </div>
      </div>
    </section>
  )
}

function TodaysTipSection() {
  return (
    <section id="today-tip" className="container-awwwards py-16">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Today's Linux Tip
          </h2>
          <p className="text-xl text-gray-600">
            Master a new command every day with practical examples
          </p>
        </div>

        <div className="card-awwwards card-enter">
          <div className="flex items-start justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  todaysTip.difficulty === 'Beginner' ? 'bg-green-100 text-green-700' :
                  todaysTip.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {todaysTip.difficulty}
                </div>
                <span className="text-sm text-gray-500">{todaysTip.category}</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                {todaysTip.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {todaysTip.description}
              </p>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-500 ml-6">
              <Clock className="w-4 h-4" />
              {todaysTip.estimatedTime}
            </div>
          </div>

          <div className="bg-gray-900 rounded-xl p-6 mb-6 terminal-container">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-400 text-sm ml-4">Terminal</span>
            </div>
            <div className="font-mono">
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
            >
              <Terminal className="w-5 h-5" />
              Practice in Terminal
            </Link>

            <Link
              href={`/tips/${todaysTip.id}`}
              className="flex-1 inline-flex items-center justify-center gap-2 bg-gray-100 text-gray-900 px-6 py-3 rounded-xl font-semibold hover:bg-gray-200 transition-all duration-200 interactive"
            >
              <BookOpen className="w-5 h-5" />
              Read Full Guide
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}

function RecentTipsSection() {
  return (
    <section className="container-awwwards py-16">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Recent Tips
          </h2>
          <p className="text-xl text-gray-600">
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
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  tip.difficulty === 'Beginner' ? 'bg-green-100 text-green-700' :
                  tip.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {tip.difficulty}
                </div>
                <span className="text-sm text-gray-500">{tip.date}</span>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-accent-600 transition-colors">
                {tip.title}
              </h3>

              <p className="text-sm text-gray-500 mb-4">{tip.category}</p>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-accent-600">Read more</span>
                <ArrowRight className="w-4 h-4 text-accent-600 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link
            href="/tips"
            className="inline-flex items-center justify-center gap-2 bg-white/70 backdrop-blur-sm text-gray-900 px-8 py-4 rounded-2xl font-semibold border border-gray-200 hover:bg-white hover:shadow-card-hover transition-all duration-200 interactive"
          >
            <BookOpen className="w-5 h-5" />
            View All Tips
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  )
}

function CTASection() {
  return (
    <section className="container-awwwards py-16">
      <div className="max-w-4xl mx-auto text-center card-awwwards">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-accent-100 rounded-3xl mb-8">
          <Zap className="w-10 h-10 text-accent-600" />
        </div>

        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
          Ready to Master Linux?
        </h2>

        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Join thousands of developers and system administrators who are improving their
          Linux skills one command at a time.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/terminal"
            className="inline-flex items-center justify-center gap-2 bg-black text-white px-8 py-4 rounded-2xl font-semibold hover:bg-gray-800 transition-all duration-200 interactive group"
          >
            <Terminal className="w-5 h-5" />
            Start Learning Now
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            href="/about"
            className="inline-flex items-center justify-center gap-2 bg-white/70 backdrop-blur-sm text-gray-900 px-8 py-4 rounded-2xl font-semibold border border-gray-200 hover:bg-white hover:shadow-card-hover transition-all duration-200 interactive"
          >
            <Code className="w-5 h-5" />
            Learn More
          </Link>
        </div>
      </div>
    </section>
  )
}

export default function HomePage() {
  return (
    <div className="page-enter">
      <Suspense fallback={<LoadingSkeleton />}>
        <HeroSection />
        <StatsSection />
        <TodaysTipSection />
        <RecentTipsSection />
        <CTASection />
      </Suspense>
    </div>
  )
}