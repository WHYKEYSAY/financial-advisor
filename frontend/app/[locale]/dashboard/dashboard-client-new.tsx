'use client';

import { useTranslations } from 'next-intl';
import { useState, useEffect } from 'react';
import { api, getCreditOverview, getAccountSummary } from '@/lib/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { CreditOverview, AccountSummary, HealthStatus, CardSummary } from '@/types/api';

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

// Helper functions
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency: 'CAD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function formatPercent(value: number): string {
  const clamped = Math.max(0, Math.min(100, value));
  return `${clamped.toFixed(0)}%`;
}

function getHealthBadgeClasses(status: HealthStatus): string {
  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
  const statusClasses = {
    optimal: 'text-green-700 bg-green-100 dark:text-green-300 dark:bg-green-900/30',
    underutilized: 'text-blue-700 bg-blue-100 dark:text-blue-300 dark:bg-blue-900/30',
    elevated: 'text-yellow-800 bg-yellow-100 dark:text-yellow-300 dark:bg-yellow-900/30',
    high: 'text-red-700 bg-red-100 dark:text-red-300 dark:bg-red-900/30',
  };
  return `${baseClasses} ${statusClasses[status]}`;
}

function getBarColor(status: HealthStatus): string {
  const colors = {
    optimal: 'bg-green-500',
    underutilized: 'bg-blue-500',
    elevated: 'bg-yellow-500',
    high: 'bg-red-500',
  };
  return colors[status];
}

export function DashboardClient() {
  const t = useTranslations();
  
  // Existing states
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [breakdown, setBreakdown] = useState<CategoryBreakdown[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  // New states for VCM and Accounts
  const [creditOverview, setCreditOverview] = useState<CreditOverview | null>(null);
  const [vcmLoading, setVcmLoading] = useState(true);
  const [vcmError, setVcmError] = useState<string | null>(null);

  const [accountSummary, setAccountSummary] = useState<AccountSummary | null>(null);
  const [accountsLoading, setAccountsLoading] = useState(true);
  const [accountsError, setAccountsError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setVcmLoading(true);
      setAccountsLoading(true);

      // Fetch all data in parallel
      const [txRes, breakdownRes, statsRes, vcmRes, accountsRes] = await Promise.allSettled([
        api.get('transactions', { searchParams: { page: 1, page_size: 10 } }).json<any>(),
        api.get('transactions/breakdown').json<any>(),
        api.get('transactions/stats').json<any>(),
        getCreditOverview(),
        getAccountSummary(),
      ]);

      // Handle transactions data
      if (txRes.status === 'fulfilled') {
        setTransactions(txRes.value.transactions || []);
      }
      if (breakdownRes.status === 'fulfilled') {
        setBreakdown(breakdownRes.value.categories || breakdownRes.value || []);
      }
      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value);
      }

      // Handle VCM data
      if (vcmRes.status === 'fulfilled') {
        setCreditOverview(vcmRes.value);
        setVcmError(null);
      } else {
        console.error('Failed to fetch VCM data:', vcmRes.reason);
        setVcmError(t('errors.load_vcm'));
      }
      setVcmLoading(false);

      // Handle accounts data
      if (accountsRes.status === 'fulfilled') {
        setAccountSummary(accountsRes.value);
        setAccountsError(null);
      } else {
        console.error('Failed to fetch accounts data:', accountsRes.reason);
        setAccountsError(t('errors.load_accounts'));
      }
      setAccountsLoading(false);

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const retryVcm = async () => {
    setVcmLoading(true);
    setVcmError(null);
    try {
      const vcmData = await getCreditOverview();
      setCreditOverview(vcmData);
    } catch (error) {
      console.error('Retry VCM failed:', error);
      setVcmError(t('errors.load_vcm'));
    } finally {
      setVcmLoading(false);
    }
  };

  const retryAccounts = async () => {
    setAccountsLoading(true);
    setAccountsError(null);
    try {
      const accountsData = await getAccountSummary();
      setAccountSummary(accountsData);
    } catch (error) {
      console.error('Retry accounts failed:', error);
      setAccountsError(t('errors.load_accounts'));
    } finally {
      setAccountsLoading(false);
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          {t('dashboard.title')}
        </h1>

        {/* Upload Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">{t('dashboard.upload')}</h2>
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

        {/* Account Overview & VCM Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Account Overview Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              {t('accounts.title')}
            </h2>
            
            {accountsLoading ? (
              <div className="animate-pulse space-y-4">
                <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </div>
            ) : accountsError ? (
              <div className="rounded-md border border-red-200 bg-red-50 dark:bg-red-950 dark:border-red-800 p-4">
                <p className="text-sm text-red-700 dark:text-red-300 mb-2">{accountsError}</p>
                <button
                  onClick={retryAccounts}
                  className="text-sm font-medium text-red-600 dark:text-red-400 hover:underline"
                >
                  {t('common.retry')}
                </button>
              </div>
            ) : accountSummary && (accountSummary.total_accounts > 0 || accountSummary.active_cards > 0) ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">{t('accounts.total_accounts')}</span>
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {accountSummary.total_accounts}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">{t('accounts.active_cards')}</span>
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {accountSummary.active_cards}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                {t('accounts.no_accounts')}
              </p>
            )}
          </div>

          {/* Credit Health Card (VCM) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              {t('vcm.title')}
            </h2>
            
            {vcmLoading ? (
              <div className="animate-pulse space-y-4">
                <div className="flex justify-between">
                  <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                  <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
                </div>
                <div className="flex justify-between">
                  <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                  <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-full mt-4"></div>
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
              </div>
            ) : vcmError ? (
              <div className="rounded-md border border-red-200 bg-red-50 dark:bg-red-950 dark:border-red-800 p-4">
                <p className="text-sm text-red-700 dark:text-red-300 mb-2">{vcmError}</p>
                <button
                  onClick={retryVcm}
                  className="text-sm font-medium text-red-600 dark:text-red-400 hover:underline"
                >
                  {t('common.retry')}
                </button>
              </div>
            ) : creditOverview ? (
              <div className="space-y-4">
                {/* Top Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{t('vcm.credit_limit')}</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                      {formatCurrency(creditOverview.total_credit_limit)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{t('vcm.used_credit')}</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">
                      {formatCurrency(creditOverview.total_used)}
                    </p>
                  </div>
                </div>

                {/* Utilization Progress Bar */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">{t('vcm.utilization')}</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {formatPercent(creditOverview.overall_utilization)}
                    </span>
                  </div>
                  <div 
                    className="h-2 bg-gray-200 dark:bg-gray-700 rounded overflow-hidden"
                    role="progressbar"
                    aria-valuenow={Math.max(0, Math.min(100, creditOverview.overall_utilization))}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className={`h-full ${getBarColor(creditOverview.health_status)} transition-all duration-300`}
                      style={{ width: formatPercent(creditOverview.overall_utilization) }}
                    ></div>
                  </div>
                </div>

                {/* Health Status Badge */}
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400 mr-2">
                    {t('vcm.health_status')}:
                  </span>
                  <span className={getHealthBadgeClasses(creditOverview.health_status)}>
                    {t(`vcm.${creditOverview.health_status}`)}
                  </span>
                </div>

                {/* Per-card List (Optional P1 feature) */}
                {creditOverview.cards_summary && creditOverview.cards_summary.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      {t('vcm.card_details')}
                    </h3>
                    <div className="space-y-3">
                      {creditOverview.cards_summary.map((card: CardSummary) => (
                        <div key={card.card_id} className="text-sm">
                          <div className="flex justify-between items-center mb-1">
                            <span className="font-medium text-gray-900 dark:text-white truncate">
                              {card.issuer} {card.product}
                              {card.last4 && <span className="text-gray-500 ml-1">••{card.last4}</span>}
                            </span>
                            <span className="text-xs text-gray-600 dark:text-gray-400 ml-2">
                              {formatPercent(card.utilization_rate)}
                            </span>
                          </div>
                          <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded overflow-hidden">
                            <div
                              className={`h-full ${getBarColor(card.health_status)}`}
                              style={{ width: formatPercent(card.utilization_rate) }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                {t('vcm.no_cards')}
              </p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Spending Breakdown Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              {t('dashboard.spending_breakdown')}
            </h2>
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
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              {t('dashboard.recent_transactions')}
            </h2>
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
  );
}
