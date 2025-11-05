'use client';

import { Terminal } from 'lucide-react';
import Link from 'next/link';

/**
 * TerminalCTAButton Props
 */
interface TerminalCTAButtonProps {
  tipId: string;
  className?: string;
}

/**
 * TerminalCTAButton Component
 * Call-to-action button to open tip in terminal
 */
export function TerminalCTAButton({ tipId, className = '' }: TerminalCTAButtonProps) {
  return (
    <Link
      href={`/terminal?tip=${tipId}`}
      className={`
        inline-flex items-center justify-center gap-3 w-full
        bg-gradient-to-r from-blue-500 to-purple-500
        text-white px-8 py-4 rounded-xl
        font-semibold text-lg
        hover:shadow-2xl hover:shadow-blue-500/50 hover:scale-[1.02]
        transition-all duration-300
        ${className}
      `}
      aria-label={`Practice this tip in interactive terminal`}
    >
      <Terminal className="w-6 h-6" aria-hidden="true" />
      <span>Try it in Terminal</span>
    </Link>
  );
}
