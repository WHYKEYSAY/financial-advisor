import ky, { type KyInstance, type Options } from 'ky';
import { getAccessToken, getRefreshToken, saveTokens, clearTokens } from './auth';
import type { ErrorResponse, CreditOverview, AccountsListResponse, AccountSummary } from '@/types/api';

// Shared promise to prevent concurrent refresh attempts
let refreshPromise: Promise<boolean> | null = null;

/**
 * Attempt to refresh the access token
 * Returns true if successful, false otherwise
 */
async function attemptTokenRefresh(): Promise<boolean> {
  // If refresh is already in progress, wait for it
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        return false;
      }

      // Call refresh endpoint without auth headers to avoid infinite loop
      const response = await ky.post('auth/refresh', {
        prefixUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
        json: { refresh_token: refreshToken },
      }).json<{ access_token: string; refresh_token: string }>();

      // Save new tokens
      saveTokens(response.access_token, response.refresh_token);
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * Redirect to login page with next parameter
 */
function redirectToLogin(): void {
  if (typeof window === 'undefined') return;

  clearTokens();
  
  // Try to preserve locale from current path
  const currentPath = window.location.pathname;
  const localeMatch = currentPath.match(/^\/(en|zh)/);
  const locale = localeMatch ? localeMatch[1] : 'en';
  
  // Build next parameter
  const nextPath = currentPath.replace(/^\/(en|zh)/, '');
  const next = nextPath && nextPath !== '/login' ? `?next=${encodeURIComponent(nextPath)}` : '';
  
  window.location.assign(`/${locale}/login${next}`);
}

/**
 * Normalize error responses for consistent UI consumption
 */
export function normalizeError(error: any): string {
  try {
    // If it's already an ErrorResponse
    if (error?.detail) {
      if (typeof error.detail === 'string') {
        return error.detail;
      }
      return JSON.stringify(error.detail);
    }

    // If it's a ky HTTPError
    if (error?.response) {
      return 'Request failed. Please try again.';
    }

    // Network error
    if (error?.message) {
      return error.message;
    }

    return 'An unexpected error occurred.';
  } catch {
    return 'An unexpected error occurred.';
  }
}

/**
 * Pre-configured ky instance with auth and refresh logic
 */
const api = ky.create({
  prefixUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  credentials: 'include',
  hooks: {
    beforeRequest: [
      (request) => {
        // Inject Authorization header if token exists
        const token = getAccessToken();
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
      },
    ],
    afterResponse: [
      async (request, options, response) => {
        // Handle 401 Unauthorized
        if (response.status === 401) {
          // Don't attempt refresh on auth endpoints
          if (request.url.includes('/auth/')) {
            return response;
          }

          // Attempt token refresh
          const refreshed = await attemptTokenRefresh();
          
          if (refreshed) {
            // Retry the original request with new token
            const token = getAccessToken();
            if (token) {
              request.headers.set('Authorization', `Bearer ${token}`);
              return ky(request);
            }
          }

          // Refresh failed, redirect to login
          redirectToLogin();
        }

        return response;
      },
    ],
  },
});

/**
 * Get credit overview from VCM
 */
export async function getCreditOverview(): Promise<CreditOverview> {
  const response = await api.get('vcm/overview').json();
  return response as CreditOverview;
}

/**
 * Get account summary
 * Fetches from /accounts/list and computes totals
 */
export async function getAccountSummary(): Promise<AccountSummary> {
  const response = await api.get('accounts/list').json() as AccountsListResponse;
  
  const totalAccounts = response.total || 0;
  const activeCards = response.accounts.filter(
    (acc) => acc.account_type === 'credit_card'
  ).length;
  
  return {
    total_accounts: totalAccounts,
    active_cards: activeCards,
  };
}

export { api };
export default api;
