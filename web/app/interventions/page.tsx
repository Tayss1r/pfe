'use client';

/**
 * Intervention Page for Equipment
 *
 * Displays active intervention or intervention history for an equipment
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import {
  interventionService,
  InterventionDetail,
  InterventionHistory,
} from '@/lib/intervention-service';
import { InterventionForm } from '@/components/intervention-form';
import { InterventionHistoryList } from '@/components/intervention-history';
import { ThemeToggle } from '@/components/theme-toggle';
import Link from 'next/link';

export default function InterventionPage() {
  const { isLoading: authLoading, isAuthenticated } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const equipmentId = searchParams.get('equipment');
  const interventionId = searchParams.get('id');

  const [intervention, setIntervention] = useState<InterventionDetail | null>(null);
  const [history, setHistory] = useState<InterventionHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState<'current' | 'history'>('current');

  const loadIntervention = useCallback(async () => {
    if (!equipmentId) return;

    try {
      setIsLoading(true);
      setError('');

      if (interventionId) {
        // Load specific intervention
        const data = await interventionService.getIntervention(interventionId);
        setIntervention(data);
      } else {
        // Load active intervention
        const activeIntervention = await interventionService.getActiveIntervention(equipmentId);
        setIntervention(activeIntervention);
      }

      // Load history
      const historyData = await interventionService.getEquipmentHistory(equipmentId);
      setHistory(historyData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load intervention');
    } finally {
      setIsLoading(false);
    }
  }, [equipmentId, interventionId]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    if (isAuthenticated && equipmentId) {
      loadIntervention();
    }
  }, [authLoading, isAuthenticated, equipmentId, loadIntervention, router]);

  const handleStartIntervention = async () => {
    if (!equipmentId) return;

    try {
      setIsLoading(true);
      const newIntervention = await interventionService.createIntervention({
        equipment_id: equipmentId,
      });
      setIntervention(newIntervention);
      setActiveView('current');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create intervention');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = () => {
    loadIntervention();
  };

  const handleComplete = () => {
    loadIntervention();
    setActiveView('history');
  };

  const handleViewIntervention = (id: string) => {
    router.push(`/interventions?equipment=${equipmentId}&id=${id}`);
  };

  if (authLoading || isLoading) {
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

  if (!equipmentId) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6">
            <p className="text-red-600 dark:text-red-400">Equipment ID is required</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">Interventions</h1>
              {intervention && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {intervention.equipment_brand} {intervention.equipment_model} - {intervention.equipment_serial}
                </p>
              )}
            </div>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <Link
                href={`/equipment/${equipmentId}`}
                className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white border border-gray-300 dark:border-gray-600 rounded-lg transition-colors"
              >
                ← Back to Equipment
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* View Toggle */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setActiveView('current')}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeView === 'current'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
            }`}
          >
            Current Intervention
          </button>
          <button
            onClick={() => setActiveView('history')}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeView === 'history'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
            }`}
          >
            History ({history.length})
          </button>
        </div>

        {/* Content */}
        {activeView === 'current' ? (
          intervention ? (
            <InterventionForm
              intervention={intervention}
              onUpdate={handleUpdate}
              onComplete={handleComplete}
            />
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-12 text-center">
              <div className="text-6xl mb-4">🔧</div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                No Active Intervention
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Start a new intervention to begin working on this equipment
              </p>
              <button
                onClick={handleStartIntervention}
                className="px-6 py-3 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                Start New Intervention
              </button>
            </div>
          )
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
              Intervention History
            </h2>
            <InterventionHistoryList history={history} onSelect={handleViewIntervention} />
          </div>
        )}
      </main>
    </div>
  );
}

