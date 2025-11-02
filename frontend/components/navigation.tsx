'use client';

import { useTranslations } from 'next-intl';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import Link from 'next/link';

interface NavigationProps {
  locale: string;
}

export function Navigation({ locale }: NavigationProps) {
  const t = useTranslations();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const toggleLocale = () => {
    const newLocale = locale === 'en' ? 'zh' : 'en';
    window.location.href = `/${newLocale}${window.location.pathname.replace(`/${locale}`, '')}`;
  };

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href={`/${locale}`} className="flex items-center">
            <span className="text-xl font-bold text-blue-600 dark:text-blue-400">
              {t('brand.name')}
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex space-x-6">
            <Link href={`/${locale}`} className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
              {t('nav.home')}
            </Link>
            <Link href={`/${locale}/dashboard`} className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
              {t('nav.dashboard')}
            </Link>
            <Link href={`/${locale}/transactions`} className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
              {t('nav.transactions')}
            </Link>
            <Link href={`/${locale}/pricing`} className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
              {t('nav.pricing')}
            </Link>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4">
            {/* Theme Toggle */}
            {mounted && (
              <button
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="p-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? '☀️' : '🌙'}
              </button>
            )}

            {/* Locale Toggle */}
            <button
              onClick={toggleLocale}
              className="px-3 py-1 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 
                       hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600"
            >
              {locale === 'en' ? '中文' : 'EN'}
            </button>

            {/* Auth Links */}
            <Link
              href={`/${locale}/login`}
              className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
            >
              {t('nav.login')}
            </Link>
            <Link
              href={`/${locale}/register`}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium"
            >
              {t('nav.register')}
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
