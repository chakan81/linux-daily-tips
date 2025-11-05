'use client';

import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

/**
 * BackButton Props
 */
interface BackButtonProps {
  href?: string;
  label?: string;
  className?: string;
}

/**
 * BackButton Component
 * Navigation button to go back to previous page or specific URL
 */
export function BackButton({
  href,
  label = 'Back to Tips',
  className = ''
}: BackButtonProps) {
  const router = useRouter();

  const handleClick = (e: React.MouseEvent) => {
    if (!href) {
      e.preventDefault();
      router.back();
    }
  };

  const baseClasses = "inline-flex items-center gap-2 text-gray-400 hover:text-white transition-all duration-200 group";
  const combinedClasses = `${baseClasses} ${className}`;

  if (href) {
    return (
      <Link
        href={href}
        className={combinedClasses}
        aria-label={label}
      >
        <ArrowLeft
          className="w-5 h-5 transition-transform duration-200 group-hover:-translate-x-1"
          aria-hidden="true"
        />
        <span className="font-medium">{label}</span>
      </Link>
    );
  }

  return (
    <button
      onClick={handleClick}
      className={combinedClasses}
      aria-label={label}
      type="button"
    >
      <ArrowLeft
        className="w-5 h-5 transition-transform duration-200 group-hover:-translate-x-1"
        aria-hidden="true"
      />
      <span className="font-medium">{label}</span>
    </button>
  );
}
