import Cookies from 'js-cookie';

const TOKEN_KEYS = {
  ACCESS: 'access_token',
  REFRESH: 'refresh_token',
} as const;

const COOKIE_OPTIONS = {
  path: '/',
  sameSite: 'lax' as const,
  secure: process.env.NODE_ENV === 'production',
};

/**
 * Save authentication tokens to cookies
 */
export function saveTokens(accessToken: string, refreshToken: string): void {
  Cookies.set(TOKEN_KEYS.ACCESS, accessToken, {
    ...COOKIE_OPTIONS,
    expires: 7, // 7 days
  });
  
  Cookies.set(TOKEN_KEYS.REFRESH, refreshToken, {
    ...COOKIE_OPTIONS,
    expires: 14, // 14 days
  });
}

/**
 * Get access token from cookies
 */
export function getAccessToken(): string | undefined {
  return Cookies.get(TOKEN_KEYS.ACCESS);
}

/**
 * Get refresh token from cookies
 */
export function getRefreshToken(): string | undefined {
  return Cookies.get(TOKEN_KEYS.REFRESH);
}

/**
 * Clear all authentication tokens from cookies
 */
export function clearTokens(): void {
  Cookies.remove(TOKEN_KEYS.ACCESS, { path: '/' });
  Cookies.remove(TOKEN_KEYS.REFRESH, { path: '/' });
}

/**
 * Check if user is authenticated (has access token)
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken();
}
