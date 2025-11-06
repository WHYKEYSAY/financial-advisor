import { getTranslations } from 'next-intl/server';
import { DashboardClient } from './dashboard-client';

export default async function DashboardPage() {
  return <DashboardClient />;
}
