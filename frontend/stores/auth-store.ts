import { create } from 'zustand';
import { api, normalizeError } from '@/lib/api';
import { saveTokens, getAccessToken, clearTokens } from '@/lib/auth';
import type { User, AuthResponse, MeResponse } from '@/types/api';

interface AuthState {
  user: User | null;
  initializing: boolean;
  loading: boolean;
  error: string | null;
}

interface AuthActions {
  initialize: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; name?: string }) => Promise<void>;
  fetchMe: () => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>((set, get) => ({
  // Initial state
  user: null,
  initializing: true,
  loading: false,
  error: null,

  // Initialize: check for existing token and fetch user
  initialize: async () => {
    try {
      const token = getAccessToken();
      
      if (token) {
        // Token exists, try to fetch user
        await get().fetchMe();
      }
    } catch (error) {
      console.error('Initialization error:', error);
      // Silent fail - user is just not logged in
    } finally {
      set({ initializing: false });
    }
  },

  // Login: authenticate and fetch user
  login: async (email: string, password: string) => {
    set({ loading: true, error: null });
    
    try {
      const response = await api.post('auth/login', {
        json: { email, password },
      }).json<AuthResponse>();

      // Save tokens to cookies
      saveTokens(response.access_token, response.refresh_token);

      // Set user from response
      set({ user: response.user, loading: false, error: null });
    } catch (error: any) {
      const errorMessage = normalizeError(error);
      set({ loading: false, error: errorMessage });
      throw error;
    }
  },

  // Register: create account and fetch user
  register: async (data: { email: string; password: string; name?: string }) => {
    set({ loading: true, error: null });
    
    try {
      const response = await api.post('auth/register', {
        json: data,
      }).json<AuthResponse>();

      // Save tokens to cookies
      saveTokens(response.access_token, response.refresh_token);

      // Set user from response
      set({ user: response.user, loading: false, error: null });
    } catch (error: any) {
      const errorMessage = normalizeError(error);
      set({ loading: false, error: errorMessage });
      throw error;
    }
  },

  // Fetch current user
  fetchMe: async () => {
    try {
      const user = await api.get('auth/me').json<MeResponse>();
      set({ user, error: null });
    } catch (error: any) {
      const errorMessage = normalizeError(error);
      set({ user: null, error: errorMessage });
      throw error;
    }
  },

  // Logout: clear tokens and user
  logout: async () => {
    set({ loading: true });
    
    try {
      // Best-effort logout call to backend
      await api.post('auth/logout').json();
    } catch (error) {
      // Ignore errors - we'll clear tokens anyway
      console.warn('Logout request failed:', error);
    } finally {
      // Clear tokens and user state
      clearTokens();
      set({ user: null, loading: false, error: null });
    }
  },

  // Clear error message
  clearError: () => {
    set({ error: null });
  },
}));
