'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { api } from '@/lib/api';
import { ProtectedRoute } from '@/components/protected-route';
import { VirtualCreditCard } from '@/components/vcm/virtual-credit-card';
import { CardList } from '@/components/vcm/card-list';
import { AllocationCalculator } from '@/components/vcm/allocation-calculator';

interface CardSummary {
  card_id: number;
  issuer: string;
  product: string;
  credit_limit: number;
  current_balance: number;
  utilization_rate: number;
  health_status: string;
  last4: string | null;
}

interface CreditOverview {
  total_credit_limit: number;
  total_used: number;
  overall_utilization: number;
  health_status: string;
  cards_summary: CardSummary[];
}

export default function VCMPage() {
  const t = useTranslations('vcm');
  const [overview, setOverview] = useState<CreditOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOverview();
  }, []);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('vcm/overview');
      setOverview(response.data);
    } catch (err: any) {
      console.error('Error fetching VCM overview:', err);
      setError(err.response?.data?.detail || 'Failed to load credit overview');
    } finally {
      setLoading(false);
    }
  };

  const handleCardUpdate = () => {
    // Refresh overview when cards are added/updated
    fetchOverview();
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {t('title')}
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              {t('subtitle')}
            </p>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
              <p className="text-red-800 dark:text-red-200">{error}</p>
              <button
                onClick={fetchOverview}
                className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
              >
                {t('tryAgain')}
              </button>
            </div>
          )}

          {/* Content */}
          {!loading && overview && (
            <div className="space-y-8">
              {/* Section 1: Virtual Credit Card Overview */}
              <VirtualCreditCard overview={overview} />

              {/* Section 2: Enrolled Cards List */}
              <CardList
                cards={overview.cards_summary}
                onUpdate={handleCardUpdate}
              />

              {/* Section 3: Spending Allocation Calculator */}
              <AllocationCalculator
                cards={overview.cards_summary}
                totalAvailableCredit={
                  overview.total_credit_limit - overview.total_used
                }
              />
            </div>
          )}

          {/* Empty State */}
          {!loading && overview && overview.cards_summary.length === 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                {t('noCards.title')}
              </h3>
              <p className="mt-2 text-gray-500 dark:text-gray-400">
                {t('noCards.description')}
              </p>
              <button
                onClick={() => {
                  // TODO: Open add card modal
                  alert('Add card functionality coming soon');
                }}
                className="mt-6 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {t('noCards.addCard')}
              </button>
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
