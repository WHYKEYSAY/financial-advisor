'use client';

import { useTranslations } from 'next-intl';

interface CreditOverview {
  total_credit_limit: number;
  total_used: number;
  overall_utilization: number;
  health_status: string;
  cards_summary: any[];
}

interface VirtualCreditCardProps {
  overview: CreditOverview;
}

export function VirtualCreditCard({ overview }: VirtualCreditCardProps) {
  const t = useTranslations('vcm');

  const availableCredit = overview.total_credit_limit - overview.total_used;
  const utilizationPercentage = overview.overall_utilization;

  // Health status colors
  const getHealthColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'optimal':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20';
      case 'underutilized':
        return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20';
      case 'elevated':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20';
      case 'high':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20';
    }
  };

  const getProgressBarColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'optimal':
        return 'bg-green-600';
      case 'underutilized':
        return 'bg-blue-600';
      case 'elevated':
        return 'bg-yellow-600';
      case 'high':
        return 'bg-red-600';
      default:
        return 'bg-gray-600';
    }
  };

  return (
    <div className="bg-gradient-to-br from-blue-600 to-purple-700 rounded-2xl shadow-xl p-8 text-white">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-blue-100 text-sm uppercase tracking-wide">
            {t('virtualCard.title')}
          </p>
          <h2 className="text-3xl font-bold mt-1">
            ${overview.total_credit_limit.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </h2>
          <p className="text-blue-100 text-sm mt-1">
            {t('virtualCard.totalLimit')}
          </p>
        </div>
        
        {/* Health Status Badge */}
        <div className={`px-4 py-2 rounded-full text-sm font-semibold ${getHealthColor(overview.health_status)}`}>
          {t(`health.${overview.health_status}`)}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white/10 backdrop-blur rounded-lg p-4">
          <p className="text-blue-100 text-sm">
            {t('virtualCard.available')}
          </p>
          <p className="text-2xl font-bold mt-1">
            ${availableCredit.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </p>
        </div>

        <div className="bg-white/10 backdrop-blur rounded-lg p-4">
          <p className="text-blue-100 text-sm">
            {t('virtualCard.used')}
          </p>
          <p className="text-2xl font-bold mt-1">
            ${overview.total_used.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </p>
        </div>

        <div className="bg-white/10 backdrop-blur rounded-lg p-4">
          <p className="text-blue-100 text-sm">
            {t('virtualCard.utilization')}
          </p>
          <p className="text-2xl font-bold mt-1">
            {utilizationPercentage.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Utilization Progress Bar */}
      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-blue-100">{t('virtualCard.utilizationBar')}</span>
          <span className="font-semibold">{utilizationPercentage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full ${getProgressBarColor(overview.health_status)} transition-all duration-500`}
            style={{ width: `${Math.min(utilizationPercentage, 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-blue-100 mt-2">
          <span>0%</span>
          <span className="text-green-300">10%</span>
          <span className="text-green-300">30%</span>
          <span className="text-yellow-300">50%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Card Count */}
      <div className="mt-6 pt-6 border-t border-white/20">
        <p className="text-blue-100 text-sm">
          {t('virtualCard.cardsEnrolled', { count: overview.cards_summary.length })}
        </p>
      </div>
    </div>
  );
}
