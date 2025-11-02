import { AuthForm } from '@/components/auth-form';

export default async function RegisterPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <AuthForm mode="register" locale={locale} />
    </div>
  );
}
