'use client';

import { Search, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface SearchBarProps {
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

/**
 * Search bar component for tips
 *
 * Provides a search input with clear button
 *
 * @param value - Current search query value
 * @param onChange - Handler for search query changes
 * @param placeholder - Optional placeholder text
 *
 * @example
 * ```tsx
 * <SearchBar
 *   value={searchQuery}
 *   onChange={setSearchQuery}
 *   placeholder="Search tips..."
 * />
 * ```
 */
export function SearchBar({
  value,
  onChange,
  placeholder = 'Search tips...',
  disabled = false,
}: SearchBarProps) {
  return (
    <div className="relative w-full max-w-md">
      <Search
        className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none"
        aria-hidden="true"
      />

      <Input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="pl-9 pr-9"
        aria-label="Search tips"
        disabled={disabled}
      />

      {value && !disabled && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onChange('')}
          className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
          aria-label="Clear search"
        >
          <X className="w-4 h-4" aria-hidden="true" />
        </Button>
      )}
    </div>
  );
}
