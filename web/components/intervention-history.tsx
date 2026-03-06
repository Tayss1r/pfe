'use client';

/**
 * Intervention History Component
 *
 * Displays past interventions for an equipment
 */

import React from 'react';
import { InterventionHistory } from '@/lib/intervention-service';

interface InterventionHistoryListProps {
  history: InterventionHistory[];
  onSelect?: (interventionId: string) => void;
}

export function InterventionHistoryList({ history, onSelect }: InterventionHistoryListProps) {
  const getStatusBadge = (status: string) => {
    const styles = {
      COMPLETED: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400',
      NOT_REPAIRED: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400',
      IN_PROGRESS: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status as keyof typeof styles] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-400'}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (history.length === 0) {
    return (
      <div className="text-center py-12 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          No intervention history
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
        {/* Desktop Table View */}
        <div className="hidden md:block overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Technician
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Diagnostic
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              {history.map((intervention) => (
                <tr
                  key={intervention.id}
                  className={onSelect ? 'hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors' : ''}
                  onClick={() => onSelect?.(intervention.id)}
                >
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {formatDate(intervention.completed_at || intervention.started_at)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {intervention.technician_name}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm">
                    {getStatusBadge(intervention.status)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 max-w-xs truncate">
                    {intervention.diagnostic || 'N/A'}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm">
                    {onSelect && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelect(intervention.id);
                        }}
                        className="text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        View Details
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile Card View */}
        <div className="md:hidden divide-y divide-gray-200 dark:divide-gray-700">
          {history.map((intervention) => (
            <div
              key={intervention.id}
              className={`p-4 space-y-2 ${onSelect ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800' : ''}`}
              onClick={() => onSelect?.(intervention.id)}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {intervention.technician_name}
                </span>
                {getStatusBadge(intervention.status)}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {formatDate(intervention.completed_at || intervention.started_at)}
              </div>
              {intervention.diagnostic && (
                <div className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                  {intervention.diagnostic}
                </div>
              )}
              {onSelect && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelect(intervention.id);
                  }}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                >
                  View Details →
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

