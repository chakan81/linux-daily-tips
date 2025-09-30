import { Terminal, ArrowRight, Code, Zap } from 'lucide-react'
import Link from 'next/link'

export function CTASection() {
  return (
    <section className="container-awwwards py-16">
      <div className="max-w-4xl mx-auto text-center card-awwwards">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-accent-100 rounded-3xl mb-8" aria-hidden="true">
          <Zap className="w-10 h-10 text-accent-600" aria-hidden="true" />
        </div>

        <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
          Ready to Master Linux?
        </h2>

        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Join thousands of developers and system administrators who are improving their
          Linux skills one command at a time.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/terminal"
            className="inline-flex items-center justify-center gap-2 bg-black text-white px-8 py-4 rounded-2xl font-semibold hover:bg-gray-800 transition-all duration-200 interactive group"
            aria-label="지금 바로 터미널에서 리눅스 학습 시작하기"
          >
            <Terminal className="w-5 h-5" aria-hidden="true" />
            Start Learning Now
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" aria-hidden="true" />
          </Link>

          <Link
            href="/about"
            className="inline-flex items-center justify-center gap-2 bg-secondary text-secondary-foreground px-8 py-4 rounded-2xl font-semibold hover:bg-secondary/80 transition-all duration-200 interactive"
            aria-label="Linux Daily Tips 서비스에 대해 더 자세히 알아보기"
          >
            <Code className="w-5 h-5" aria-hidden="true" />
            Learn More
          </Link>
        </div>
      </div>
    </section>
  )
}