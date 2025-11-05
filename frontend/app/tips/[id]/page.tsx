'use client';

import { use } from 'react';
import { Clock } from 'lucide-react';
import { useTip } from '@/lib/hooks/useTips';
import { BackButton } from '@/components/common/BackButton';
import { MetadataBadges } from '@/components/tips/MetadataBadges';
import { CodeBlock } from '@/components/tips/CodeBlock';
import { MarkdownRenderer } from '@/components/tips/MarkdownRenderer';
import { TerminalCTAButton } from '@/components/tips/TerminalCTAButton';
import { TipDetailSkeleton } from '@/components/tips/TipDetailSkeleton';
import { TipErrorState } from '@/components/tips/TipErrorState';

/**
 * TipDetailPage Props
 */
interface TipDetailPageProps {
  params: Promise<{ id: string }>;
}

/**
 * TipDetailPage Component
 * Displays complete tip details with command, description, and full content
 */
export default function TipDetailPage({ params }: TipDetailPageProps) {
  // Unwrap params using React.use() for Next.js 15 async params
  const { id } = use(params);
  const { data: tip, isLoading, error, refetch } = useTip(id);

  // Loading state
  if (isLoading) {
    return <TipDetailSkeleton />;
  }

  // Error state
  if (error) {
    return <TipErrorState error={error as Error} onRetry={() => refetch()} />;
  }

  // No data state (shouldn't happen but defensive)
  if (!tip) {
    return (
      <TipErrorState
        error={new Error('Tip not found')}
        onRetry={() => refetch()}
      />
    );
  }

  const publishDate = new Date(tip.publishDate);
  const categories = Array.isArray(tip.category) ? tip.category : [tip.category];

  return (
    <div className="container-awwwards max-w-4xl mx-auto px-4 sm:px-8 lg:px-12 py-12">
      {/* Back Navigation */}
      <div className="mb-8">
        <BackButton href="/tips" label="Back to Tips" />
      </div>

      {/* Main Content Card with Gradient Border */}
      <article className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl opacity-75 group-hover:opacity-100 transition duration-300" />
        <div className="relative bg-gradient-to-br from-gray-900/50 to-black/50 backdrop-blur-xl rounded-2xl p-8 sm:p-12">

          {/* Header Section */}
          <header className="mb-8">
            <MetadataBadges
              difficulty={tip.difficulty}
              categories={categories}
              publishDate={publishDate.toISOString()}
              className="mb-6"
            />

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-4">
              {tip.title}
            </h1>

            {/* Estimated Time */}
            {tip.estimatedTime && (
              <div className="flex items-center gap-2 text-gray-400">
                <Clock className="w-4 h-4" aria-hidden="true" />
                <span className="text-sm">{tip.estimatedTime}</span>
              </div>
            )}
          </header>

          {/* Description */}
          {tip.description && (
            <section className="mb-8">
              <h2 className="sr-only">Description</h2>
              <p className="text-lg text-gray-300 leading-relaxed">
                {tip.description}
              </p>
            </section>
          )}

          {/* Command Section */}
          {tip.command && (
            <section className="mb-8">
              <h2 className="text-xl font-semibold text-foreground mb-3">
                Command
              </h2>
              <CodeBlock
                code={tip.command}
                language="bash"
                maxHeight="200px"
              />
            </section>
          )}

          {/* Full Content */}
          {tip.content && (
            <section className="mb-8">
              <h2 className="text-xl font-semibold text-foreground mb-4">
                Detailed Guide
              </h2>
              <MarkdownRenderer content={tip.content} />
            </section>
          )}

          {/* Tags */}
          {tip.tags && tip.tags.length > 0 && (
            <section className="mb-8">
              <h2 className="text-sm font-semibold text-gray-400 mb-3">
                Tags
              </h2>
              <div className="flex flex-wrap gap-2">
                {tip.tags.map((tag, index) => (
                  <span
                    key={`${tag}-${index}`}
                    className="px-3 py-1 rounded-full text-xs font-medium bg-gray-800/50 text-gray-300 border border-gray-700"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </section>
          )}

          {/* Call to Action */}
          <footer>
            <TerminalCTAButton tipId={id} />
          </footer>
        </div>
      </article>

      {/* Metadata for Screen Readers */}
      <div className="sr-only" aria-live="polite">
        Viewing tip: {tip.title}, difficulty: {tip.difficulty}
      </div>
    </div>
  );
}
