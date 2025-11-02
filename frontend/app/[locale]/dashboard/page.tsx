import { getTranslations } from 'next-intl/server';
import { DashboardClient } from './dashboard-client';

export const dynamic = 'force-dynamic';

export default async function DashboardPage() {
  return <DashboardClient />;
}
