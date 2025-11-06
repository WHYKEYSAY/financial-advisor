'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, initializing, initialize } = useAuthStore();

  useEffect(() => {
    // Initialize auth store on mount
    initialize();
  }, [initialize]);

  useEffect(() => {
    // Redirect to login if not authenticated after initialization
    if (!initializing && !user) {
      // Extract locale from path
      const localeMatch = pathname.match(/^\/(en|zh)/);
      const locale = localeMatch ? localeMatch[1] : 'en';
      
      // Build next parameter
      const nextPath = pathname.replace(/^\/(en|zh)/, '');
      const next = nextPath ? `?next=${encodeURIComponent(nextPath)}` : '';
      
      router.push(`/${locale}/login${next}`);
    }
  }, [initializing, user, pathname, router]);

  // Show loading state while initializing
  if (initializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render children if not authenticated
  if (!user) {
    return null;
  }

  return <>{children}</>;
}
