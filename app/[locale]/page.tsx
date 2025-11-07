'use client';

import { useTranslations, useLocale } from 'next-intl';
import Link from 'next/link';

export default function HomePage() {
  const t = useTranslations();
  const locale = useLocale();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {t('brand.name')}
          </div>
          <div className="flex items-center gap-4">
            <Link
              href={`/${locale}/login`}
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              {t('nav.login')}
            </Link>
            <Link
              href={`/${locale}/register`}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              {t('nav.register')}
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            {t('hero.title')}
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            {t('hero.subtitle')}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href={`/${locale}/register`}
              className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition shadow-lg hover:shadow-xl"
            >
              {t('hero.cta_primary')}
            </Link>
            <Link
              href={`/${locale}/pricing`}
              className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition shadow-lg border border-gray-200 dark:border-gray-700"
            >
              {t('hero.cta_secondary')}
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-32 grid md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-2">Smart Categorization</h3>
            <p className="text-gray-600 dark:text-gray-300">
              AI categorization with fuzzy matching
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">💳</div>
            <h3 className="text-xl font-bold mb-2">Rewards Optimization</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Maximize credit card rewards
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-2">AI Insights</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Intelligent spending analysis
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 mt-32 border-t border-gray-200 dark:border-gray-700">
        <div className="flex justify-center gap-8 text-sm text-gray-600 dark:text-gray-400">
          <span className="text-gray-500">{t('footer.coming_soon')}</span>
        </div>
      </footer>
    </div>
  );
}
