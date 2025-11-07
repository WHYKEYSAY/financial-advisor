'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { api } from '@/lib/api';

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

interface AllocationStep {
  card_id: number;
  issuer: string;
  product: string;
  last4: string | null;
  amount_to_charge: number;
  current_utilization: number;
  new_utilization: number;
  available_credit: number;
  reason: string;
}

interface AllocationResponse {
  total_amount: number;
  allocation_feasible: boolean;
  allocation_steps: AllocationStep[];
  optimization_summary: string;
  total_available_credit: number;
  warnings: string[];
}

interface AllocationCalculatorProps {
  cards: CardSummary[];
  totalAvailableCredit: number;
}

export function AllocationCalculator({ cards, totalAvailableCredit }: AllocationCalculatorProps) {
  const t = useTranslations('vcm');
  const [amount, setAmount] = useState('');
  const [allocation, setAllocation] = useState<AllocationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async () => {
    const amountNum = parseFloat(amount);
    
    if (isNaN(amountNum) || amountNum <= 0) {
      setError(t('allocator.invalidAmount'));
      return;
    }

    if (amountNum > totalAvailableCredit) {
      setError(t('allocator.exceedsCredit'));
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await api.post('vcm/allocate', { amount: amountNum });
      setAllocation(response.data);
    } catch (err: any) {
      console.error('Error calculating allocation:', err);
      setError(err.response?.data?.detail || t('allocator.calculationFailed'));
    } finally {
      setLoading(false);
    }
  };

  const getUtilizationColor = (utilization: number) => {
    if (utilization <= 30) return 'text-green-600 dark:text-green-400';
    if (utilization <= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {t('allocator.title')}
        </h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {t('allocator.subtitle')}
        </p>
      </div>

      <div className="p-6">
        {/* Input Section */}
        <div className="mb-6">
          <label htmlFor="amount" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {t('allocator.inputLabel')}
          </label>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span className="text-gray-500 dark:text-gray-400 sm:text-sm">$</span>
              </div>
              <input
                type="number"
                id="amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleCalculate();
                  }
                }}
                placeholder="0.00"
                min="0"
                step="0.01"
                className="block w-full pl-7 pr-12 py-3 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              onClick={handleCalculate}
              disabled={loading || !amount || cards.length === 0}
              className="px-6 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? t('allocator.calculating') : t('allocator.calculate')}
            </button>
          </div>
          
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            {t('allocator.availableCredit')}: ${totalAvailableCredit.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
            <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Allocation Results */}
        {allocation && (
          <div className="space-y-4">
            {/* Summary */}
            <div className={`p-4 rounded-lg ${allocation.allocation_feasible ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' : 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800'}`}>
              <h4 className={`text-sm font-semibold ${allocation.allocation_feasible ? 'text-green-800 dark:text-green-200' : 'text-yellow-800 dark:text-yellow-200'}`}>
                {t('allocator.results')}
              </h4>
              <p className={`mt-1 text-sm ${allocation.allocation_feasible ? 'text-green-700 dark:text-green-300' : 'text-yellow-700 dark:text-yellow-300'}`}>
                {allocation.optimization_summary}
              </p>
            </div>

            {/* Warnings */}
            {allocation.warnings && allocation.warnings.length > 0 && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-4">
                <h5 className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                  {t('allocator.warnings')}
                </h5>
                <ul className="list-disc list-inside space-y-1">
                  {allocation.warnings.map((warning, index) => (
                    <li key={index} className="text-sm text-yellow-700 dark:text-yellow-300">
                      {warning}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Allocation Steps */}
            {allocation.allocation_steps.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                  {t('allocator.breakdown')}
                </h4>
                <div className="space-y-3">
                  {allocation.allocation_steps.map((step, index) => (
                    <div key={step.card_id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h5 className="font-medium text-gray-900 dark:text-white">
                            {index + 1}. {step.issuer} {step.product}
                            {step.last4 && <span className="text-gray-500 dark:text-gray-400 ml-2">•••• {step.last4}</span>}
                          </h5>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            {step.reason}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-semibold text-gray-900 dark:text-white">
                            ${step.amount_to_charge.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">{t('allocator.currentUtil')}:</span>
                          <span className={`ml-2 font-medium ${getUtilizationColor(step.current_utilization)}`}>
                            {step.current_utilization.toFixed(1)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">{t('allocator.newUtil')}:</span>
                          <span className={`ml-2 font-medium ${getUtilizationColor(step.new_utilization)}`}>
                            {step.new_utilization.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* No Cards Message */}
        {cards.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <p>{t('allocator.noCardsMessage')}</p>
          </div>
        )}
      </div>
    </div>
  );
}
