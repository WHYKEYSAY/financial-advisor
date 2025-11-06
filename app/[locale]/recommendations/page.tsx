'use client';

import { useTranslations } from 'next-intl';
import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { CardRecommendation } from '@/types/api';

interface RecommendationCardProps {
  rec: CardRecommendation;
  rank: number;
  locale: string;
}

// Utility to extract top 3 reward categories
function extractTopRewards(rewards: unknown): Array<{ label: string; rate: string }> {
  try {
    if (!rewards || typeof rewards !== 'object') return [];

    const rewardsObj = rewards as Record<string, any>;
    const entries: Array<{ label: string; rate: number }> = [];

    // Try to extract rewards from various structures
    for (const [key, value] of Object.entries(rewardsObj)) {
      if (key === 'default') continue; // Skip default category for top 3

      let rate: number | null = null;
      
      if (typeof value === 'number') {
        rate = value;
      } else if (value && typeof value === 'object' && 'rate' in value) {
        rate = typeof value.rate === 'number' ? value.rate : null;
      }

      if (rate !== null) {
        // Capitalize label
        const label = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
        entries.push({ label, rate });
      }
    }

    // Sort by rate descending and take top 3
    const sorted = entries.sort((a, b) => b.rate - a.rate).slice(0, 3);

    // Format rate as percentage
    return sorted.map(({ label, rate }) => ({
      label,
      rate: rate <= 1 ? `${(rate * 100).toFixed(1)}%` : `${rate.toFixed(1)}%`
    }));
  } catch (error) {
    console.error('Failed to extract rewards:', error);
    return [];
  }
}

function RecommendationCard({ rec, rank, locale }: RecommendationCardProps) {
  const t = useTranslations();
  const isTopCard = rank === 1;
  const showTrophy = rank <= 3;

  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: 'CAD'
    }).format(value);
  };

  // Extract top rewards
  const topRewards = extractTopRewards(rec.rewards);

  // Get initials for placeholder
  const getInitials = () => {
    const parts = rec.product_name.split(' ');
    return parts.slice(0, 2).map(p => p[0]).join('').toUpperCase();
  };

  return (
    <div
      className={`rounded-xl border shadow-sm p-6 transition-all hover:shadow-lg hover:-translate-y-0.5 
                  ${isTopCard 
                    ? 'bg-gradient-to-r from-amber-50 to-white dark:from-amber-900/20 dark:to-zinc-900 border-amber-300/60 dark:border-amber-700/40' 
                    : 'bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800'
                  }`}
    >
      {/* Ranking Badge */}
      {showTrophy && (
        <div className="flex items-center mb-3">
          <span className="text-lg font-bold text-amber-600 dark:text-amber-400">
            🏆 #{rank}
          </span>
          <span className="sr-only">Rank {rank} recommendation</span>
        </div>
      )}

      {/* Card Logo/Image Placeholder */}
      <div className="flex justify-center mb-4">
        {rec.image_url ? (
          <img 
            src={rec.image_url} 
            alt={`${rec.issuer} ${rec.product_name}`}
            className="h-16 w-auto object-contain"
          />
        ) : (
          <div className="h-16 w-24 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
            {getInitials()}
          </div>
        )}
      </div>

      {/* Card Header */}
      <div className="mb-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
          {rec.product_name}
        </h3>
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <span>{rec.issuer}</span>
          {rec.card_network && (
            <>
              <span>•</span>
              <span className="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-xs font-medium">
                {rec.card_network}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Annual Fee */}
      <div className="mb-4 text-sm">
        <span className="text-gray-600 dark:text-gray-400">{t('recommendations.annualFee')}: </span>
        <span className="font-semibold text-gray-900 dark:text-white">
          {formatCurrency(Number(rec.annual_fee))}
        </span>
      </div>

      {/* NAV Breakdown */}
      <div className="mb-5 p-4 rounded-lg bg-gray-50 dark:bg-zinc-800/50 space-y-2">
        <div className="flex justify-between items-center pb-2 border-b border-gray-200 dark:border-gray-700">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {t('recommendations.estimatedValue')}
          </span>
          <span className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
            +{formatCurrency(rec.nav)}
          </span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">{t('recommendations.annualRewards')}</span>
          <span className="font-medium text-emerald-600 dark:text-emerald-400">
            +{formatCurrency(rec.annual_rewards)}
          </span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">{t('recommendations.welcomeBonus')}</span>
          <span className="font-medium text-emerald-600 dark:text-emerald-400">
            +{formatCurrency(rec.welcome_bonus_amortized)}/yr
          </span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">{t('recommendations.annualFee')}</span>
          <span className="font-medium text-gray-500 dark:text-gray-400">
            -{formatCurrency(Number(rec.annual_fee))}
          </span>
        </div>
      </div>

      {/* Top Reward Categories */}
      {topRewards.length > 0 && (
        <div className="mb-5">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            {t('recommendations.topCategories')}
          </h4>
          <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
            {topRewards.map((reward, idx) => (
              <li key={idx} className="flex items-center gap-2">
                <span className="text-blue-500">•</span>
                <span>{reward.label}</span>
                <span className="font-semibold text-gray-900 dark:text-white">{reward.rate}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        {/* TODO: Phase 2 - Add detailed view route */}
        <button
          className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium 
                     text-gray-700 dark:text-gray-300 bg-white dark:bg-zinc-800 
                     hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          disabled
        >
          {t('recommendations.viewDetails')}
        </button>
        
        {rec.apply_url ? (
          <a
            href={rec.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium 
                       text-center focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500"
          >
            {t('recommendations.applyNow')} →
          </a>
        ) : (
          <button
            className="flex-1 px-4 py-2 bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-500 
                       rounded-md text-sm font-medium cursor-not-allowed"
            disabled
          >
            {t('recommendations.applyNow')}
          </button>
        )}
      </div>
    </div>
  );
}

// Loading skeleton component
function SkeletonCard() {
  return (
    <div className="rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm p-6">
      <div className="animate-pulse space-y-4">
        <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="flex gap-3">
          <div className="flex-1 h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
          <div className="flex-1 h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    </div>
  );
}

export default function RecommendationsPage({
  params: { locale }
}: {
  params: { locale: string }
}) {
  const t = useTranslations();
  const [selectedMonths, setSelectedMonths] = useState(12);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [data, setData] = useState<CardRecommendation[]>([]);
  const [emptyReason, setEmptyReason] = useState<'no-transactions' | 'no-results' | null>(null);

  const fetchRecommendations = async (months: number) => {
    try {
      setLoading(true);
      setErrorMessage(null);
      setEmptyReason(null);

      const response = await api.get('recommendations/cards', {
        searchParams: { months }
      }).json<CardRecommendation[]>();

      if (response.length === 0) {
        setEmptyReason('no-results');
      } else {
        // Sort by NAV descending as a safety net
        const sorted = [...response].sort((a, b) => b.nav - a.nav);
        setData(sorted);
      }
    } catch (error: any) {
      console.error('Failed to fetch recommendations:', error);
      
      // Check for specific error codes
      if (error?.response?.status === 412 || error?.response?.status === 428) {
        setEmptyReason('no-transactions');
      } else {
        setErrorMessage(error?.message || 'Failed to load recommendations');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations(selectedMonths);
  }, [selectedMonths]);

  // Sorted recommendations (already sorted, but using useMemo for consistency)
  const sortedRecommendations = useMemo(() => {
    return [...data].sort((a, b) => b.nav - a.nav);
  }, [data]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
            {t('recommendations.title')}
          </h1>

          {/* Filter Bar */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-4">
              <label 
                htmlFor="months-filter" 
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {t('recommendations.filterByMonths')}:
              </label>
              <select
                id="months-filter"
                value={selectedMonths}
                onChange={(e) => setSelectedMonths(Number(e.target.value))}
                aria-label={t('recommendations.filterByMonths')}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                         focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={3}>{t('recommendations.months_3')}</option>
                <option value={6}>{t('recommendations.months_6')}</option>
                <option value={12}>{t('recommendations.months_12')}</option>
              </select>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main>
          {loading ? (
            // Loading State
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : errorMessage ? (
            // Error State
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
              <p className="text-red-800 dark:text-red-200 mb-4">{errorMessage}</p>
              <button
                onClick={() => fetchRecommendations(selectedMonths)}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-medium"
              >
                {t('common.retry') || 'Retry'}
              </button>
            </div>
          ) : emptyReason === 'no-transactions' ? (
            // No Transactions Empty State
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-8 text-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t('recommendations.emptyState.noTransactions')}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {t('recommendations.emptyState.uploadCTA')}
              </p>
              <Link
                href={`/${locale}/dashboard`}
                className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium"
              >
                {t('recommendations.emptyState.uploadButton')}
              </Link>
            </div>
          ) : emptyReason === 'no-results' ? (
            // No Results Empty State
            <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 text-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t('recommendations.emptyState.noResults')}
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                {t('recommendations.emptyState.contactSupport')}
              </p>
            </div>
          ) : (
            // Cards Grid
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              {sortedRecommendations.map((rec, index) => (
                <RecommendationCard
                  key={rec.card_id}
                  rec={rec}
                  rank={index + 1}
                  locale={locale}
                />
              ))}
            </div>
          )}
        </main>

        {/* Footer Explanation */}
        {!loading && !errorMessage && !emptyReason && sortedRecommendations.length > 0 && (
          <footer className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
              {t('recommendations.navExplanation')}
            </p>
          </footer>
        )}
      </div>
    </div>
  );
}
