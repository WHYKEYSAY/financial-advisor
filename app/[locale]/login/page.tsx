import { AuthForm } from '@/components/auth-form';
import { setRequestLocale } from 'next-intl/server';

export default async function LoginPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <AuthForm mode="login" locale={locale} />
    </div>
  );
}
