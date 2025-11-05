'use client';

import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';

interface TipsPaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

/**
 * Generate page numbers with ellipsis
 *
 * Examples:
 * - Total 5 pages: [1, 2, 3, 4, 5]
 * - Current page 1 of 10: [1, 2, 3, 4, 5, '...', 10]
 * - Current page 5 of 10: [1, '...', 4, 5, 6, '...', 10]
 * - Current page 10 of 10: [1, '...', 6, 7, 8, 9, 10]
 */
function getPageNumbers(current: number, total: number): (number | string)[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  if (current <= 3) {
    return [1, 2, 3, 4, 5, '...', total];
  }

  if (current >= total - 2) {
    return [1, '...', total - 4, total - 3, total - 2, total - 1, total];
  }

  return [1, '...', current - 1, current, current + 1, '...', total];
}

/**
 * Tips pagination component
 *
 * Provides pagination controls with page numbers, previous/next buttons,
 * and a summary of displayed items
 *
 * @param currentPage - Current page number (1-indexed)
 * @param totalPages - Total number of pages
 * @param totalItems - Total number of items across all pages
 * @param pageSize - Number of items per page
 * @param onPageChange - Handler for page changes
 *
 * @example
 * ```tsx
 * <TipsPagination
 *   currentPage={page}
 *   totalPages={10}
 *   totalItems={156}
 *   pageSize={12}
 *   onPageChange={setPage}
 * />
 * ```
 */
export function TipsPagination({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
}: TipsPaginationProps) {
  // Don't render if only one page or no items
  if (totalPages <= 1 || totalItems === 0) {
    return null;
  }

  const pageNumbers = getPageNumbers(currentPage, totalPages);
  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  const handlePageClick = (page: number | string) => {
    if (typeof page === 'number' && page !== currentPage) {
      onPageChange(page);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 py-8">
      {/* Items Summary */}
      <p className="text-sm text-muted-foreground">
        Showing <span className="font-medium text-foreground">{startItem}</span> to{' '}
        <span className="font-medium text-foreground">{endItem}</span> of{' '}
        <span className="font-medium text-foreground">{totalItems}</span> tips
      </p>

      {/* Pagination Controls */}
      <Pagination>
        <PaginationContent>
          {/* Previous Button */}
          <PaginationItem>
            <PaginationPrevious
              onClick={(e) => {
                e.preventDefault();
                if (currentPage > 1) {
                  onPageChange(currentPage - 1);
                }
              }}
              aria-disabled={currentPage === 1}
              className={
                currentPage === 1
                  ? 'pointer-events-none opacity-50'
                  : 'cursor-pointer'
              }
            />
          </PaginationItem>

          {/* Page Numbers */}
          {pageNumbers.map((pageNum, index) => (
            <PaginationItem key={`${pageNum}-${index}`}>
              {pageNum === '...' ? (
                <PaginationEllipsis />
              ) : (
                <PaginationLink
                  onClick={(e) => {
                    e.preventDefault();
                    handlePageClick(pageNum);
                  }}
                  isActive={pageNum === currentPage}
                  className="cursor-pointer"
                  aria-label={`Go to page ${pageNum}`}
                >
                  {pageNum}
                </PaginationLink>
              )}
            </PaginationItem>
          ))}

          {/* Next Button */}
          <PaginationItem>
            <PaginationNext
              onClick={(e) => {
                e.preventDefault();
                if (currentPage < totalPages) {
                  onPageChange(currentPage + 1);
                }
              }}
              aria-disabled={currentPage === totalPages}
              className={
                currentPage === totalPages
                  ? 'pointer-events-none opacity-50'
                  : 'cursor-pointer'
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
}
