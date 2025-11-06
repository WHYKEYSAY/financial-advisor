'use client';

import { useTranslations } from 'next-intl';
import { useState, useCallback, useRef } from 'react';
import { api } from '@/lib/api';
import { ProtectedRoute } from '@/components/protected-route';
import type { UploadItem, FileUploadResponse } from '@/types/api';

const ACCEPTED_EXT = ['pdf', 'csv', 'png', 'jpg', 'jpeg'];
const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB

function isAcceptedType(file: File): boolean {
  const ext = file.name.split('.').pop()?.toLowerCase() || '';
  return ACCEPTED_EXT.includes(ext);
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export default function UploadPage() {
  const t = useTranslations();
  const [isDragging, setIsDragging] = useState(false);
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    addFilesToQueue(files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      addFilesToQueue(files);
      e.target.value = ''; // Reset input
    }
  };

  const addFilesToQueue = (files: File[]) => {
    const newItems: UploadItem[] = files.map((file) => {
      if (!isAcceptedType(file)) {
        return {
          id: generateId(),
          file,
          progress: 0,
          status: 'error' as const,
          error: t('upload.messages.unsupportedType'),
        };
      }

      if (file.size > MAX_FILE_SIZE) {
        return {
          id: generateId(),
          file,
          progress: 0,
          status: 'error' as const,
          error: `File too large (max 25MB)`,
        };
      }

      return {
        id: generateId(),
        file,
        progress: 0,
        status: 'idle' as const,
      };
    });

    setUploads((prev) => [...newItems, ...prev]);

    // Start uploading valid files
    newItems.forEach((item) => {
      if (item.status === 'idle') {
        uploadFile(item);
      }
    });
  };

  const uploadFile = async (item: UploadItem) => {
    // Update status to uploading
    setUploads((prev) =>
      prev.map((u) => (u.id === item.id ? { ...u, status: 'uploading', progress: 10 } : u))
    );

    try {
      const formData = new FormData();
      formData.append('file', item.file);

      // Simulate progress (ky doesn't support upload progress natively)
      const progressInterval = setInterval(() => {
        setUploads((prev) =>
          prev.map((u) =>
            u.id === item.id && u.progress < 90
              ? { ...u, progress: u.progress + 10 }
              : u
          )
        );
      }, 200);

      const response = await api.post('files/upload', { body: formData }).json<FileUploadResponse>();

      clearInterval(progressInterval);

      setUploads((prev) =>
        prev.map((u) =>
          u.id === item.id
            ? { ...u, status: 'success', progress: 100, response }
            : u
        )
      );
    } catch (error: any) {
      const message =
        error?.response?.data?.detail || error?.message || t('upload.messages.uploadFailed');

      setUploads((prev) =>
        prev.map((u) =>
          u.id === item.id
            ? { ...u, status: 'error', progress: 0, error: typeof message === 'string' ? message : JSON.stringify(message) }
            : u
        )
      );
    }
  };

  const retryUpload = (item: UploadItem) => {
    setUploads((prev) =>
      prev.map((u) =>
        u.id === item.id ? { ...u, status: 'idle', progress: 0, error: undefined } : u
      )
    );
    uploadFile({ ...item, status: 'idle', progress: 0, error: undefined });
  };

  const removeItem = (id: string) => {
    setUploads((prev) => prev.filter((u) => u.id !== id));
  };

  const clearAll = () => {
    setUploads([]);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('upload.title')}
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {t('upload.subtitle')}
          </p>
        </div>

        {/* Dropzone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            rounded-lg border-2 border-dashed transition-all duration-200
            ${
              isDragging
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800'
            }
          `}
        >
          <div className="p-12 flex flex-col items-center justify-center text-center">
            <div className="mb-4 text-6xl">📎</div>
            <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {t('upload.dragTitle')}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              {t('upload.supportedFormats')}
            </p>
            <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              {t('upload.or')}
            </div>
            <label className="inline-flex cursor-pointer items-center rounded-md bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 transition-colors">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.csv,.png,.jpg,.jpeg"
                className="hidden"
                onChange={handleFileSelect}
              />
              {t('upload.clickToSelect')}
            </label>
            <p className="mt-3 text-xs text-gray-400 dark:text-gray-500">
              {t('upload.multipleHint')}
            </p>
          </div>
        </div>

        {/* Upload List */}
        {uploads.length > 0 && (
          <div className="mt-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                {t('upload.selectedFiles')} ({uploads.length})
              </h2>
              <button
                onClick={clearAll}
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:underline"
              >
                {t('upload.actions.clearAll')}
              </button>
            </div>

            <div className="space-y-3">
              {uploads.map((item) => (
                <div
                  key={item.id}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {item.file.name}
                        </p>
                        <span
                          className={`
                            inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
                            ${
                              item.status === 'success'
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                : item.status === 'error'
                                ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                                : item.status === 'uploading'
                                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                                : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                            }
                          `}
                        >
                          {t(`upload.status.${item.status}`)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {(item.file.size / 1024 / 1024).toFixed(2)} MB
                        {item.response?.message && ` • ${item.response.message}`}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      {item.status === 'error' && (
                        <button
                          onClick={() => retryUpload(item)}
                          className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          {t('upload.actions.retry')}
                        </button>
                      )}
                      <button
                        onClick={() => removeItem(item.id)}
                        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      >
                        ✕
                      </button>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {item.status === 'uploading' && (
                    <div className="mt-2">
                      <div className="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                        <div
                          className="h-2 rounded-full bg-blue-600 transition-all duration-300"
                          style={{ width: `${item.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Error Message */}
                  {item.error && (
                    <div className="mt-2 text-xs text-red-600 dark:text-red-400">
                      {item.error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
    </ProtectedRoute>
  );
}
