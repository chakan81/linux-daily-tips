'use client';

import { useState } from 'react';
import { Check, Copy } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { copyToClipboard } from '@/lib/utils';

/**
 * CodeBlock Props
 */
interface CodeBlockProps {
  code: string;
  language?: string;
  showCopy?: boolean;
  maxHeight?: string;
  className?: string;
}

/**
 * CodeBlock Component
 * Syntax-highlighted code block with copy functionality
 */
export function CodeBlock({
  code,
  language = 'bash',
  showCopy = true,
  maxHeight = '400px',
  className = '',
}: CodeBlockProps) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(code);
    if (success) {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  return (
    <div className={`relative group ${className}`}>
      {/* Copy Button */}
      {showCopy && (
        <button
          onClick={handleCopy}
          className="absolute top-3 right-3 z-10 p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-all duration-200 opacity-0 group-hover:opacity-100"
          aria-label={isCopied ? 'Copied!' : 'Copy code'}
          type="button"
        >
          {isCopied ? (
            <Check className="w-4 h-4 text-green-400" aria-hidden="true" />
          ) : (
            <Copy className="w-4 h-4" aria-hidden="true" />
          )}
        </button>
      )}

      {/* Syntax Highlighter */}
      <div
        className="rounded-xl overflow-hidden border border-gray-800"
        style={{ maxHeight }}
      >
        <SyntaxHighlighter
          language={language}
          style={oneDark}
          showLineNumbers
          customStyle={{
            margin: 0,
            padding: '1.5rem',
            fontSize: '0.875rem',
            lineHeight: '1.5',
            background: 'rgba(17, 24, 39, 0.8)',
            maxHeight,
            overflowX: 'auto',
            overflowY: 'auto',
          }}
          codeTagProps={{
            style: {
              fontFamily: 'JetBrains Mono, Monaco, Consolas, monospace',
            },
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>

      {/* Copy Feedback */}
      {isCopied && (
        <div
          className="absolute top-16 right-3 px-3 py-1.5 rounded-lg bg-green-500 text-white text-sm font-medium animate-in fade-in slide-in-from-top-2 duration-200"
          role="status"
          aria-live="polite"
        >
          Copied!
        </div>
      )}
    </div>
  );
}
