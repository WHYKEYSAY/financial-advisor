import { setRequestLocale } from 'next-intl/server';

export default async function DebugPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  return (
    <div>
      <h1>✅ Locale Route Works!</h1>
      <p>If you see this at /en/debug or /zh/debug, the [locale] routing is working.</p>
    </div>
  );
}
