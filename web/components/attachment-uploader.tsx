'use client';

/**
 * Attachment Uploader Component
 *
 * Upload and preview photos for interventions
 */

import React, { useState } from 'react';
import { InterventionAttachment } from '@/lib/intervention-service';

interface AttachmentUploaderProps {
  attachments: InterventionAttachment[];
  onUpload: (file: File) => Promise<void>;
  disabled?: boolean;
}

export function AttachmentUploader({ attachments, onUpload, disabled = false }: AttachmentUploaderProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/heic'];
    if (!allowedTypes.includes(file.type)) {
      setUploadError('Only JPG, PNG, and HEIC images are allowed');
      return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setUploadError('File size must be less than 10MB');
      return;
    }

    setIsUploading(true);
    setUploadError('');

    try {
      await onUpload(file);
    } catch (error: any) {
      setUploadError(error.message || 'Failed to upload photo');
    } finally {
      setIsUploading(false);
      // Reset input
      e.target.value = '';
    }
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Photo Attachments
      </label>

      {/* Upload Button */}
      <div>
        <label
          className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
            disabled || isUploading
              ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          {isUploading ? 'Uploading...' : 'Upload Photo'}
          <input
            type="file"
            accept="image/jpeg,image/png,image/heic"
            onChange={handleFileSelect}
            disabled={disabled || isUploading}
            className="hidden"
          />
        </label>
      </div>

      {/* Upload Error */}
      {uploadError && (
        <div className="text-sm text-red-600 dark:text-red-400">
          {uploadError}
        </div>
      )}

      {/* Uploaded Images Preview */}
      {attachments.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="relative aspect-square rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800"
            >
              <img
                src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/${attachment.file_path}`}
                alt="Intervention photo"
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                <p className="text-xs text-white truncate">
                  {new Date(attachment.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {attachments.length === 0 && (
        <div className="text-center py-8 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
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
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            No photos uploaded yet
          </p>
        </div>
      )}
    </div>
  );
}

