'use client';

import { useTranslations, useLocale } from 'next-intl';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type {
  Account,
  AccountListResponse,
  AccountSummaryResponse,
  CategoryBreakdown,
  BreakdownResponse,
} from '@/types/api';

const COLORS = [
  '#3b82f6',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#14b8a6',
  '#f97316',
];

export default function AccountsPage() {
  const t = useTranslations();
  const locale = useLocale();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [summary, setSummary] = useState<AccountSummaryResponse | null>(null);
  const [breakdown, setBreakdown] = useState<CategoryBreakdown[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [accountsRes, summaryRes, breakdownRes] = await Promise.all([
        api.get('accounts/list').json<AccountListResponse>(),
        api.get('accounts/summary').json<AccountSummaryResponse>().catch(() => null),
        api.get('transactions/breakdown').json<BreakdownResponse>().catch(() => null),
      ]);

      setAccounts(accountsRes.accounts);
      setSummary(summaryRes);
      setBreakdown(breakdownRes?.categories || []);
    } catch (err: any) {
      setError(err?.message || t('accounts.errors.loadFailed'));
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="mt-2 h-4 w-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-24 bg-white dark:bg-gray-800 rounded-lg shadow animate-pulse"
              />
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-96 bg-white dark:bg-gray-800 rounded-lg shadow animate-pulse" />
            <div className="h-96 bg-white dark:bg-gray-800 rounded-lg shadow animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <p className="text-red-800 dark:text-red-200">{error}</p>
              <button
                onClick={fetchData}
                className="text-sm font-medium text-red-600 dark:text-red-400 hover:underline"
              >
                {t('accounts.reload')}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const totalAccounts = accounts.length;
  const totalSpent = summary?.credit_cards.total_spent || 0;
  const netBalance = summary?.credit_cards.net_balance || 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('accounts.title')}
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {t('accounts.subtitle')}
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {t('accounts.accountCount')}
            </p>
            <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
              {totalAccounts}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {t('accounts.totalSpent')}
            </p>
            <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
              ${totalSpent.toFixed(2)}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {t('accounts.totalBalance')}
            </p>
            <p
              className={`mt-2 text-3xl font-bold ${
                netBalance >= 0
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-red-600 dark:text-red-400'
              }`}
            >
              ${Math.abs(netBalance).toFixed(2)}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Spending Breakdown Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              {t('accounts.spendingBreakdown')}
            </h2>
            {breakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={breakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.percentage.toFixed(1)}%`}
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
              <div className="h-[300px] flex items-center justify-center text-gray-500 dark:text-gray-400">
                {t('transactions.no_transactions')}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Quick Actions
            </h2>
            <div className="space-y-3">
              <Link
                href={`/${locale}/upload`}
                className="block w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-center font-medium transition-colors"
              >
                📄 {t('accounts.uploadNew')}
              </Link>
              <Link
                href={`/${locale}/transactions`}
                className="block w-full px-4 py-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg text-center font-medium transition-colors"
              >
                📊 {t('accounts.viewTransactions')}
              </Link>
            </div>
          </div>
        </div>

        {/* Account List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              {t('accounts.accountList')}
            </h2>
          </div>

          {accounts.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <p className="text-gray-500 dark:text-gray-400">{t('accounts.empty')}</p>
              <Link
                href={`/${locale}/upload`}
                className="mt-4 inline-block px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
              >
                {t('accounts.uploadNew')}
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {accounts.map((account) => (
                <div
                  key={`${account.institution}-${account.account_type}`}
                  className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {account.institution}
                        </h3>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                          {t(`accounts.accountType.${account.account_type}`)}
                        </span>
                      </div>

                      <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500 dark:text-gray-400">
                            {t('accounts.list.statementCount')}
                          </p>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {account.statement_count}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400">
                            {t('accounts.list.transactionCount')}
                          </p>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {account.transaction_count}
                          </p>
                        </div>
                        <div className="col-span-2">
                          <p className="text-gray-500 dark:text-gray-400">
                            {t('accounts.list.dateRange')}
                          </p>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {formatDate(account.first_statement)} →{' '}
                            {formatDate(account.last_statement)}
                          </p>
                        </div>
                      </div>
                    </div>

                    <Link
                      href={`/${locale}/transactions?institution=${encodeURIComponent(
                        account.institution
                      )}`}
                      className="ml-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors"
                    >
                      {t('accounts.viewTransactions')}
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
