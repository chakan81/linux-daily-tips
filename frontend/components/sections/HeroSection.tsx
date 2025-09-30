import { Terminal, Play, Star, ArrowRight } from 'lucide-react'
import Link from 'next/link'

export function HeroSection() {
  return (
    <section className="container-awwwards py-16 md:py-24" aria-labelledby="hero-heading">
      <div className="max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 bg-secondary/60 backdrop-blur-sm px-4 py-2 rounded-full border border-border mb-8">
          <Star className="w-4 h-4 text-yellow-500 fill-current" aria-hidden="true" />
          <span className="text-sm font-medium text-foreground">Daily Linux Learning</span>
          <Star className="w-4 h-4 text-yellow-500 fill-current" aria-hidden="true" />
        </div>

        <h1 id="hero-heading" className="text-4xl md:text-6xl font-bold tracking-tight gradient-text mb-6">
          Master Linux
          <br />
          <span className="text-accent-600">One Command at a Time</span>
        </h1>

        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
          Learn essential Linux commands through daily tips, interactive terminal practice,
          and hands-on tutorials. Perfect for developers, sysadmins, and Linux enthusiasts.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/terminal"
            className="inline-flex items-center justify-center gap-2 bg-black text-white px-8 py-4 rounded-2xl font-semibold hover:bg-gray-800 transition-all duration-200 interactive group"
            aria-label="터미널 에뮬레이터에서 실습하기"
          >
            <Terminal className="w-5 h-5" aria-hidden="true" />
            Try Interactive Terminal
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" aria-hidden="true" />
          </Link>

          <Link
            href="#today-tip"
            className="inline-flex items-center justify-center gap-2 bg-secondary text-secondary-foreground px-8 py-4 rounded-2xl font-semibold hover:bg-secondary/80 transition-all duration-200 interactive"
            aria-label="오늘의 리눅스 팁 보기"
          >
            <Play className="w-5 h-5" aria-hidden="true" />
            View Today&apos;s Tip
          </Link>
        </div>
      </div>
    </section>
  )
}