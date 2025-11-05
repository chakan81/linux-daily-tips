'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';

/**
 * MarkdownRenderer Props
 */
interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * MarkdownRenderer Component
 * Renders markdown content with GFM support and XSS protection
 */
export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-invert max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
        components={{
          // Custom styling for different elements
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold text-foreground mb-4 mt-8 first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-2xl font-bold text-foreground mb-3 mt-6">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-xl font-semibold text-foreground mb-2 mt-4">
              {children}
            </h3>
          ),
          p: ({ children }) => (
            <p className="text-gray-300 leading-relaxed mb-4">
              {children}
            </p>
          ),
          ul: ({ children }) => (
            <ul className="list-disc list-inside space-y-2 mb-4 text-gray-300">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-300">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-gray-300 ml-4">
              {children}
            </li>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-900/10 rounded-r-lg">
              {children}
            </blockquote>
          ),
          code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            const isInline = !match;

            if (isInline) {
              return (
                <code
                  className="px-1.5 py-0.5 rounded bg-gray-800 text-blue-400 font-mono text-sm"
                  {...props}
                >
                  {children}
                </code>
              );
            }

            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre className="bg-gray-900 rounded-lg p-4 overflow-x-auto mb-4 border border-gray-800">
              {children}
            </pre>
          ),
          a: ({ children, href }) => (
            <a
              href={href}
              className="text-blue-400 hover:text-blue-300 underline transition-colors duration-200"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto mb-4">
              <table className="w-full border-collapse border border-gray-700">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-800">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-gray-700">
              {children}
            </tbody>
          ),
          th: ({ children }) => (
            <th className="px-4 py-2 text-left text-gray-300 font-semibold border border-gray-700">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-2 text-gray-300 border border-gray-700">
              {children}
            </td>
          ),
          hr: () => (
            <hr className="my-8 border-gray-700" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
