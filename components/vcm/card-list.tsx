'use client';

import { useTranslations } from 'next-intl';

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

interface CardListProps {
  cards: CardSummary[];
  onUpdate: () => void;
}

export function CardList({ cards, onUpdate }: CardListProps) {
  const t = useTranslations('vcm');

  const getHealthColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'optimal':
        return 'bg-green-500';
      case 'underutilized':
        return 'bg-blue-500';
      case 'elevated':
        return 'bg-yellow-500';
      case 'high':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getHealthBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'optimal':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'underutilized':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'elevated':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {t('cards.enrolled')}
        </h3>
      </div>

      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {cards.map((card) => {
          const availableCredit = card.credit_limit - card.current_balance;
          
          return (
            <div key={card.card_id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                      {card.issuer} {card.product}
                    </h4>
                    {card.last4 && (
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        •••• {card.last4}
                      </span>
                    )}
                  </div>
                  
                  <div className="mt-2 flex items-center gap-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getHealthBadgeColor(card.health_status)}`}>
                      {t(`health.${card.health_status}`)}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {card.utilization_rate.toFixed(1)}% {t('cards.utilization')}
                    </span>
                  </div>
                </div>

                {/* Optional: Add enrollment toggle button here */}
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {t('cards.limit')}
                  </p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    ${card.credit_limit.toLocaleString('en-US', { minimumFractionDigits: 0 })}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {t('cards.balance')}
                  </p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    ${card.current_balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {t('cards.available')}
                  </p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    ${availableCredit.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>

              {/* Utilization Bar */}
              <div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full ${getHealthColor(card.health_status)} transition-all duration-300`}
                    style={{ width: `${Math.min(card.utilization_rate, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>0%</span>
                  <span className="text-green-600 dark:text-green-400">30%</span>
                  <span>100%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {cards.length === 0 && (
        <div className="p-12 text-center text-gray-500 dark:text-gray-400">
          <p>{t('cards.noCards')}</p>
        </div>
      )}
    </div>
  );
}
