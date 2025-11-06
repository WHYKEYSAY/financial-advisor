'use client';

import { useTranslations } from 'next-intl';

export default function PricingPage() {
  const t = useTranslations();

  const tiers = [
    {
      key: 'analyst',
      color: 'blue',
      features: t.raw('pricing.analyst.features') as string[]
    },
    {
      key: 'optimizer',
      color: 'green',
      features: t.raw('pricing.optimizer.features') as string[]
    },
    {
      key: 'autopilot',
      color: 'purple',
      features: t.raw('pricing.autopilot.features') as string[]
    }
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, { border: string; text: string; button: string }> = {
      blue: {
        border: 'border-blue-200 dark:border-blue-800',
        text: 'text-blue-600 dark:text-blue-400',
        button: 'bg-blue-600 hover:bg-blue-700'
      },
      green: {
        border: 'border-green-200 dark:border-green-800',
        text: 'text-green-600 dark:text-green-400',
        button: 'bg-green-600 hover:bg-green-700'
      },
      purple: {
        border: 'border-purple-200 dark:border-purple-800',
        text: 'text-purple-600 dark:text-purple-400',
        button: 'bg-purple-600 hover:bg-purple-700'
      }
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {t('pricing.title')}
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            {t('hero.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {tiers.map((tier) => {
            const colors = getColorClasses(tier.color);
            const isOptimizer = tier.key === 'optimizer';
            const showMonthlyYearly = tier.key !== 'analyst';

            return (
              <div
                key={tier.key}
                className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 border-2 ${colors.border} ${
                  isOptimizer ? 'transform scale-105 ring-2 ring-green-500' : ''
                }`}
              >
                {isOptimizer && (
                  <div className="bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300 text-sm font-semibold px-3 py-1 rounded-full inline-block mb-4">
                    Popular
                  </div>
                )}
                
                <h2 className={`text-2xl font-bold ${colors.text} mb-2`}>
                  {t(`pricing.${tier.key}.name`)}
                </h2>
                
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {t(`pricing.${tier.key}.description`)}
                </p>

                <div className="mb-6">
                  {showMonthlyYearly ? (
                    <>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white">
                        {t(`pricing.${tier.key}.price_monthly`)}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {t(`pricing.${tier.key}.price_yearly`)} (save 17%)
                      </p>
                    </>
                  ) : (
                    <p className="text-4xl font-bold text-gray-900 dark:text-white">
                      {t(`pricing.${tier.key}.price`)}
                    </p>
                  )}
                </div>

                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className={`${colors.text} mr-2 mt-1`}>✓</span>
                      <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  className={`w-full py-3 px-6 ${colors.button} text-white rounded-md font-medium transition-colors`}
                  onClick={() => {
                    if (tier.key === 'analyst') {
                      window.location.href = '/register';
                    } else {
                      alert('Stripe checkout integration coming soon!');
                    }
                  }}
                >
                  {t('pricing.cta')}
                </button>
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Questions?
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Contact us at support@creditsphere.com
          </p>
        </div>
      </div>
    </div>
  );
}
