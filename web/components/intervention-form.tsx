'use client';

/**
 * Intervention Form Component
 *
 * Main form for creating and managing interventions
 */

import React, { useState } from 'react';
import { InterventionDetail, interventionService } from '@/lib/intervention-service';
import { AttachmentUploader } from './attachment-uploader';
import { SignaturePad } from './signature-pad';

interface InterventionFormProps {
  intervention: InterventionDetail;
  onUpdate: () => void;
  onComplete: () => void;
}

export function InterventionForm({ intervention, onUpdate, onComplete }: InterventionFormProps) {
  const [diagnostic, setDiagnostic] = useState(intervention.diagnostic || '');
  const [actionsTaken, setActionsTaken] = useState(intervention.actions_taken || '');
  const [result, setResult] = useState(intervention.result || '');
  const [failureReason, setFailureReason] = useState(intervention.failure_reason || '');
  const [status, setStatus] = useState<'COMPLETED' | 'NOT_REPAIRED'>('COMPLETED');

  const [isSaving, setIsSaving] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showSignature, setShowSignature] = useState(false);

  const isCompleted = intervention.status === 'COMPLETED' || intervention.status === 'NOT_REPAIRED';

  const handleSaveDraft = async () => {
    setIsSaving(true);
    setError('');
    setSuccess('');

    try {
      await interventionService.updateIntervention(intervention.id, {
        diagnostic,
        actions_taken: actionsTaken,
        result,
      });
      setSuccess('Intervention saved successfully');
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save intervention');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCompleteClick = () => {
    if (status === 'NOT_REPAIRED' && !failureReason.trim()) {
      setError('Failure reason is required when marking as NOT REPAIRED');
      return;
    }
    setShowSignature(true);
  };

  const handleSignatureSave = async (blob: Blob) => {
    setIsCompleting(true);
    setError('');
    setSuccess('');

    try {
      // Upload signature
      await interventionService.uploadSignature(intervention.id, blob);

      // Complete intervention
      await interventionService.completeIntervention(intervention.id, {
        status,
        result,
        failure_reason: status === 'NOT_REPAIRED' ? failureReason : undefined,
      });

      setSuccess('Intervention completed successfully');
      setShowSignature(false);
      onComplete();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to complete intervention');
    } finally {
      setIsCompleting(false);
    }
  };

  const handlePhotoUpload = async (file: File) => {
    await interventionService.uploadPhoto(intervention.id, file);
    onUpdate(); // Refresh to show new attachment
  };

  return (
    <div className="space-y-6">
      {/* Error/Success Messages */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <p className="text-sm text-green-600 dark:text-green-400">{success}</p>
        </div>
      )}

      {/* Intervention Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Intervention Status
          </h3>
          <span
            className={`px-3 py-1 text-sm font-medium rounded-full ${
              intervention.status === 'COMPLETED'
                ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                : intervention.status === 'NOT_REPAIRED'
                ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400'
                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
            }`}
          >
            {intervention.status.replace('_', ' ')}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500 dark:text-gray-400">Started:</span>
            <span className="ml-2 text-gray-900 dark:text-gray-100">
              {intervention.started_at
                ? new Date(intervention.started_at).toLocaleString()
                : 'N/A'}
            </span>
          </div>
          {intervention.completed_at && (
            <div>
              <span className="text-gray-500 dark:text-gray-400">Completed:</span>
              <span className="ml-2 text-gray-900 dark:text-gray-100">
                {new Date(intervention.completed_at).toLocaleString()}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Form Fields */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-4">
        {/* Diagnostic */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Diagnostic
          </label>
          <textarea
            value={diagnostic}
            onChange={(e) => setDiagnostic(e.target.value)}
            disabled={isCompleted}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            placeholder="Describe the problem..."
          />
        </div>

        {/* Actions Taken */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Actions Taken
          </label>
          <textarea
            value={actionsTaken}
            onChange={(e) => setActionsTaken(e.target.value)}
            disabled={isCompleted}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            placeholder="Describe repair steps performed..."
          />
        </div>

        {/* Result */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Result
          </label>
          <textarea
            value={result}
            onChange={(e) => setResult(e.target.value)}
            disabled={isCompleted}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            placeholder="Describe the final outcome..."
          />
        </div>

        {/* Status Selector (only when completing) */}
        {!isCompleted && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Final Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as 'COMPLETED' | 'NOT_REPAIRED')}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="COMPLETED">Completed</option>
              <option value="NOT_REPAIRED">Not Repaired</option>
            </select>
          </div>
        )}

        {/* Failure Reason (only if NOT_REPAIRED) */}
        {status === 'NOT_REPAIRED' && !isCompleted && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Failure Reason <span className="text-red-500">*</span>
            </label>
            <textarea
              value={failureReason}
              onChange={(e) => setFailureReason(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Explain why the equipment could not be repaired..."
            />
          </div>
        )}

        {intervention.failure_reason && isCompleted && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Failure Reason
            </label>
            <p className="text-gray-900 dark:text-gray-100">{intervention.failure_reason}</p>
          </div>
        )}
      </div>

      {/* Photo Attachments */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <AttachmentUploader
          attachments={intervention.attachments}
          onUpload={handlePhotoUpload}
          disabled={isCompleted}
        />
      </div>

      {/* Signature Section (shown when completing) */}
      {showSignature && !isCompleted && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <SignaturePad onSave={handleSignatureSave} disabled={isCompleting} />
        </div>
      )}

      {/* Signature Display (if completed) */}
      {intervention.signature_image_path && isCompleted && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Technician Signature
          </label>
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-900">
            <img
              src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/${intervention.signature_image_path}`}
              alt="Technician signature"
              className="max-w-md"
            />
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {!isCompleted && (
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={handleSaveDraft}
            disabled={isSaving || isCompleting}
            className="flex-1 px-6 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSaving ? 'Saving...' : 'Save Draft'}
          </button>
          <button
            onClick={handleCompleteClick}
            disabled={isSaving || isCompleting || showSignature}
            className="flex-1 px-6 py-3 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isCompleting ? 'Completing...' : 'Complete Intervention'}
          </button>
        </div>
      )}
    </div>
  );
}

