'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useAuthStore } from '@/stores/auth-store';

interface AuthFormProps {
  mode: 'login' | 'register';
  locale: string;
}

export function AuthForm({ mode, locale }: AuthFormProps) {
  const t = useTranslations();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, register, loading, error, clearError } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      errors.email = t('auth.error_invalid_email') || 'Invalid email';
    }
    
    if (!password || password.length < 8) {
      errors.password = t('auth.error_min_length') || 'Password must be at least 8 characters';
    }
    
    if (mode === 'register' && password !== confirmPassword) {
      errors.confirmPassword = t('auth.password_mismatch');
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setFieldErrors({});
    
    if (!validate()) return;

    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register({ email, password });
      }
      
      // Redirect after successful auth
      const next = searchParams.get('next') || '/dashboard';
      // Use window.location for hard navigation to ensure state is fresh
      window.location.href = `/${locale}${next}`;
    } catch (err) {
      // Error is handled by store
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-900 dark:text-white">
        {mode === 'login' ? t('auth.login_title') : t('auth.register_title')}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
            {t('auth.email')}
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {fieldErrors.email && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{fieldErrors.email}</p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
            {t('auth.password')}
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {fieldErrors.password && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{fieldErrors.password}</p>
          )}
        </div>

        {mode === 'register' && (
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
              {t('auth.confirm_password')}
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {fieldErrors.confirmPassword && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{fieldErrors.confirmPassword}</p>
            )}
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 
                   text-white font-medium rounded-md transition-colors flex items-center justify-center"
        >
          {loading ? (
            <>
              <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {t('auth.loading')}
            </>
          ) : (
            mode === 'login' ? t('auth.login_button') : t('auth.register_button')
          )}
        </button>
      </form>

      <div className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
        {mode === 'login' ? (
          <p>
            {t('auth.no_account')}{' '}
            <a href={`/${locale}/register`} className="text-blue-600 dark:text-blue-400 hover:underline">
              {t('auth.register_link')}
            </a>
          </p>
        ) : (
          <p>
            {t('auth.have_account')}{' '}
            <a href={`/${locale}/login`} className="text-blue-600 dark:text-blue-400 hover:underline">
              {t('auth.login_link')}
            </a>
          </p>
        )}
      </div>
    </div>
  );
}
