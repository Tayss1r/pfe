'use client';

/**
 * Equipment Search Page
 *
 * Features:
 * - Single search input with live/autocomplete search
 * - Debounced input (300ms) for smooth UX
 * - Modern card-based UI with dark mode support
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import {
  equipmentService,
  EquipmentSearchParams,
  EquipmentSummary,
} from '@/lib/equipment-service';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default function EquipmentSearchPage() {
  const { isLoading: authLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 12;

  // Debounced search query (300ms delay)
  const debouncedQuery = useDebounce(searchQuery, 300);

  // Results
  const [results, setResults] = useState<EquipmentSummary[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState('');
  const [hasInteracted, setHasInteracted] = useState(false);

  // Input ref for focus management
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Auto-focus search input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Perform search when debounced query or page changes
  const performSearch = useCallback(async (query: string, currentPage: number) => {
    setIsSearching(true);
    setError('');

    try {
      const searchParams: EquipmentSearchParams = {
        page: currentPage,
        page_size: pageSize,
      };

      if (query.trim()) {
        searchParams.q = query.trim();
      }

      const response = await equipmentService.search(searchParams);
      setResults(response.items);
      setTotalPages(response.total_pages);
      setTotal(response.total);
    } catch (err: any) {
      console.error('Search failed:', err);
      setError(err.response?.data?.detail || 'Search failed. Please try again.');
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [pageSize]);

  // Effect: search on debounced query change
  useEffect(() => {
    if (hasInteracted || debouncedQuery) {
      setHasInteracted(true);
      setPage(1);
      performSearch(debouncedQuery, 1);
    }
  }, [debouncedQuery, performSearch, hasInteracted]);

  // Effect: search on page change (only if already interacted)
  useEffect(() => {
    if (hasInteracted && page > 1) {
      performSearch(debouncedQuery, page);
    }
  }, [page, debouncedQuery, performSearch, hasInteracted]);

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    if (!hasInteracted) {
      setHasInteracted(true);
    }
  };

  const handleClear = () => {
    setSearchQuery('');
    setPage(1);
    inputRef.current?.focus();
  };

  const handleViewEquipment = (equipmentId: string) => {
    router.push(`/equipment/${equipmentId}`);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleLoadAll = () => {
    setHasInteracted(true);
    performSearch('', 1);
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="flex flex-col items-center gap-4">
          <svg className="animate-spin h-10 w-10 text-blue-600" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Equipment Search</h1>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <Link
                href="/dashboard"
                className="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                ← Dashboard
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Search Section */}
      <section className="max-w-4xl mx-auto px-4 py-8">
        <div className="relative">
          <div className="relative flex items-center">
            <svg className="absolute left-4 w-5 h-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <input
              ref={inputRef}
              type="text"
              value={searchQuery}
              onChange={handleQueryChange}
              placeholder="Search by serial number, client, brand, model, or type..."
              className="w-full pl-12 pr-20 py-4 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg shadow-sm transition-all"
              autoComplete="off"
            />
            {searchQuery && (
              <button
                onClick={handleClear}
                className="absolute right-14 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                title="Clear search"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
            {isSearching && (
              <div className="absolute right-4">
                <svg className="animate-spin h-5 w-5 text-blue-600" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
            )}
          </div>
          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-3">
            Start typing to search • Results update automatically
          </p>
        </div>
      </section>

      {/* Error Message */}
      {error && (
        <div className="max-w-4xl mx-auto px-4 mb-6">
          <div className="flex items-center gap-3 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Results Section */}
      <section className="max-w-7xl mx-auto px-4 pb-12">
        {!hasInteracted ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-6">🔧</div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">Find Equipment</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
              Search across all equipment by serial number, client name, brand, model, or type.
            </p>
            <button
              onClick={handleLoadAll}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              Browse All Equipment
            </button>
          </div>
        ) : results.length === 0 && !isSearching ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-6">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No equipment found</h3>
            <p className="text-gray-600 dark:text-gray-400">Try adjusting your search terms or browse all equipment.</p>
          </div>
        ) : (
          <>
            {/* Results Header */}
            <div className="mb-6">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                {total} equipment{total !== 1 ? 's' : ''} found
              </span>
            </div>

            {/* Equipment Cards Grid */}
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {results.map((equipment) => (
                <div
                  key={equipment.id}
                  onClick={() => handleViewEquipment(equipment.id)}
                  className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-600 cursor-pointer transition-all"
                >
                  <div className="aspect-[4/3] bg-gray-100 dark:bg-gray-700 relative overflow-hidden">
                    {equipment.image ? (
                      <img
                        src={equipment.image}
                        alt={equipment.serial_number}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-4xl text-gray-400">
                        🖥️
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2 truncate">
                      {equipment.serial_number}
                    </h3>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {equipment.brand && (
                        <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                          {equipment.brand}
                        </span>
                      )}
                      {equipment.model && (
                        <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
                          {equipment.model}
                        </span>
                      )}
                    </div>
                    {equipment.type && (
                      <span className="inline-block px-2 py-0.5 text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded mb-2">
                        {equipment.type}
                      </span>
                    )}
                    <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <span className="truncate">{equipment.client_name}</span>
                    </div>
                  </div>
                  <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-sm">
                    <span className="text-blue-600 dark:text-blue-400 font-medium group-hover:underline">View Details</span>
                    <svg className="w-4 h-4 text-blue-600 dark:text-blue-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-4 mt-8">
                <button
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page === 1}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  ← Previous
                </button>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page === totalPages}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}
