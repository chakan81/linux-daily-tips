'use client';

/**
 * TipDetailSkeleton Component
 * Loading skeleton for tip detail page
 */
export function TipDetailSkeleton() {
  return (
    <div className="container-awwwards max-w-4xl mx-auto px-4 sm:px-8 lg:px-12 py-12">
      {/* Back Button Skeleton */}
      <div className="mb-8">
        <div className="h-10 w-32 bg-gray-800/50 rounded-lg animate-pulse" />
      </div>

      {/* Gradient Border Card */}
      <div className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl opacity-75" />
        <div className="relative bg-gradient-to-br from-gray-900/50 to-black/50 backdrop-blur-xl rounded-2xl p-8">

          {/* Header Section */}
          <header className="mb-8">
            {/* Metadata Badges Skeleton */}
            <div className="flex flex-wrap gap-2 mb-4">
              <div className="h-7 w-24 bg-gray-800/50 rounded-full animate-pulse" />
              <div className="h-7 w-32 bg-gray-800/50 rounded-full animate-pulse" />
              <div className="h-7 w-28 bg-gray-800/50 rounded-full animate-pulse" />
            </div>

            {/* Title Skeleton */}
            <div className="space-y-3">
              <div className="h-10 bg-gray-800/50 rounded-lg animate-pulse" />
              <div className="h-10 w-2/3 bg-gray-800/50 rounded-lg animate-pulse" />
            </div>
          </header>

          {/* Description Skeleton */}
          <section className="mb-8">
            <div className="space-y-2">
              <div className="h-6 bg-gray-800/50 rounded animate-pulse" />
              <div className="h-6 bg-gray-800/50 rounded animate-pulse" />
              <div className="h-6 w-3/4 bg-gray-800/50 rounded animate-pulse" />
            </div>
          </section>

          {/* Code Block Skeleton */}
          <section className="mb-8">
            <div className="h-8 w-24 bg-gray-800/50 rounded mb-3 animate-pulse" />
            <div className="bg-gray-900/80 rounded-xl p-6 space-y-2">
              <div className="h-5 bg-gray-800/50 rounded animate-pulse" />
              <div className="h-5 w-5/6 bg-gray-800/50 rounded animate-pulse" />
              <div className="h-5 w-4/5 bg-gray-800/50 rounded animate-pulse" />
            </div>
          </section>

          {/* Content Skeleton */}
          <section className="mb-8">
            <div className="h-8 w-32 bg-gray-800/50 rounded mb-3 animate-pulse" />
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="h-5 bg-gray-800/50 rounded animate-pulse" />
                <div className="h-5 bg-gray-800/50 rounded animate-pulse" />
                <div className="h-5 bg-gray-800/50 rounded animate-pulse" />
                <div className="h-5 w-2/3 bg-gray-800/50 rounded animate-pulse" />
              </div>
              <div className="space-y-2">
                <div className="h-5 bg-gray-800/50 rounded animate-pulse" />
                <div className="h-5 bg-gray-800/50 rounded animate-pulse" />
                <div className="h-5 w-3/4 bg-gray-800/50 rounded animate-pulse" />
              </div>
            </div>
          </section>

          {/* CTA Button Skeleton */}
          <footer>
            <div className="h-14 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl animate-pulse" />
          </footer>
        </div>
      </div>
    </div>
  );
}
