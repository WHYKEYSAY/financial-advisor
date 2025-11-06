import { AuthForm } from '@/components/auth-form';
import { setRequestLocale } from 'next-intl/server';
import { Suspense } from 'react';

export default async function LoginPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <Suspense fallback={<div className="animate-pulse bg-white dark:bg-gray-800 rounded-lg shadow-lg w-full max-w-md h-96" />}>
        <AuthForm mode="login" locale={locale} />
      </Suspense>
    </div>
  );
}
