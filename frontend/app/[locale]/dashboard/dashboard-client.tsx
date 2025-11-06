'use client';

import { useTranslations } from 'next-intl';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { ProtectedRoute } from '@/components/protected-route';
import { useAuthStore } from '@/stores/auth-store';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface Transaction {
  id: number;
  date: string;
  amount: number;
  category: string;
  merchant_name: string;
}

interface CategoryBreakdown {
  category: string;
  total: number;
  percentage: number;
}

interface Stats {
  total_transactions: number;
  total_spent: number;
  average_transaction: number;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16', '#a855f7', '#6366f1'];

export function DashboardClient() {
  const t = useTranslations();
  const { user } = useAuthStore();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [breakdown, setBreakdown] = useState<CategoryBreakdown[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [txRes, breakdownRes, statsRes] = await Promise.all([
        api.get('transactions', { searchParams: { page: 1, page_size: 10 } }).json<any>(),
        api.get('transactions/breakdown').json<any>(),
        api.get('transactions/stats').json<any>()
      ]);
      setTransactions(txRes.transactions || []);
      setBreakdown(breakdownRes.categories || []);
      setStats(statsRes);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadError('');
      setUploadSuccess('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadError('');
    setUploadSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      await api.post('files/upload', { body: formData }).json();
      
      setUploadSuccess(t('dashboard.upload_success'));
      setFile(null);
      
      // Refresh data after upload
      setTimeout(() => fetchData(), 2000);
    } catch (error: any) {
      const message = error?.response?.data?.detail || t('dashboard.upload_error');
      setUploadError(typeof message === 'string' ? message : JSON.stringify(message));
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <p className="text-gray-600 dark:text-gray-400">{t('auth.loading')}</p>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {t('dashboard.title')}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Welcome back, {user?.email || 'User'}!
        </p>

        {/* Upload Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">{t('dashboard.upload')}</h2>
          <div className="flex items-center space-x-4">
            <input
              type="file"
              accept=".pdf,.csv,.png,.jpg,.jpeg"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-900 dark:text-gray-100 
                       file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0
                       file:text-sm file:font-medium file:bg-blue-50 dark:file:bg-blue-900/20
                       file:text-blue-700 dark:file:text-blue-400 hover:file:bg-blue-100 dark:hover:file:bg-blue-900/40"
            />
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 
                       text-white rounded-md font-medium whitespace-nowrap"
            >
              {uploading ? t('auth.loading') : t('dashboard.upload')}
            </button>
          </div>
          {uploadError && (
            <p className="mt-2 text-sm text-red-600 dark:text-red-400">{uploadError}</p>
          )}
          {uploadSuccess && (
            <p className="mt-2 text-sm text-green-600 dark:text-green-400">{uploadSuccess}</p>
          )}
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">{t('dashboard.total_transactions')}</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {stats.total_transactions}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">{t('dashboard.total_spent')}</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                ${stats.total_spent.toFixed(2)}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">{t('dashboard.average_transaction')}</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                ${stats.average_transaction.toFixed(2)}
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Spending Breakdown Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">{t('dashboard.spending_breakdown')}</h2>
            {breakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={breakdown as any}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry: any) => `${t(`categories.${entry.category}`)}: ${entry.percentage.toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total"
                  >
                    {breakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                {t('transactions.no_transactions')}
              </p>
            )}
          </div>

          {/* Recent Transactions */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">{t('dashboard.recent_transactions')}</h2>
            {transactions.length > 0 ? (
              <div className="space-y-3">
                {transactions.map((tx) => (
                  <div key={tx.id} className="flex justify-between items-center border-b border-gray-200 dark:border-gray-700 pb-2">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{tx.merchant_name || 'Unknown'}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(tx.date).toLocaleDateString()} • {t(`categories.${tx.category}`)}
                      </p>
                    </div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      ${Math.abs(tx.amount).toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                {t('transactions.no_transactions')}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
    </ProtectedRoute>
  );
}
