/**
 * Auth Store - Zustand
 * Manages authentication state with persistence
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { api } from '@/api/client';

const initialState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

export const useAuthStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // Actions
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),

      // Register
      register: async (phone, pin, username, referralCode) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.auth.register({
            phone,
            pin,
            username,
            referral_code: referralCode || undefined,
          });
          
          const { token, user } = response.data;
          
          // Store tokens
          localStorage.setItem('crickpredict_token', token.access_token);
          localStorage.setItem('crickpredict_refresh_token', token.refresh_token);
          
          set({
            user,
            token: token.access_token,
            refreshToken: token.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
          return { success: true };
        } catch (error) {
          const errorMsg = error?.message || error?.response?.data?.message || 'Registration failed';
          set({ isLoading: false, error: errorMsg });
          return { success: false, error: errorMsg };
        }
      },

      // Login
      login: async (phone, pin) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.auth.login({ phone, pin });
          
          const { token, user } = response.data;
          
          // Store tokens
          localStorage.setItem('crickpredict_token', token.access_token);
          localStorage.setItem('crickpredict_refresh_token', token.refresh_token);
          
          set({
            user,
            token: token.access_token,
            refreshToken: token.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
          return { success: true };
        } catch (error) {
          const errorMsg = error?.message || error?.response?.data?.message || 'Login failed';
          set({ isLoading: false, error: errorMsg });
          return { success: false, error: errorMsg };
        }
      },

      // Logout
      logout: () => {
        localStorage.removeItem('crickpredict_token');
        localStorage.removeItem('crickpredict_refresh_token');
        set(initialState);
      },

      // Fetch current user
      fetchUser: async () => {
        const token = localStorage.getItem('crickpredict_token');
        if (!token) {
          set({ isAuthenticated: false, isLoading: false });
          return;
        }

        set({ isLoading: true });
        try {
          const response = await api.auth.me();
          set({
            user: response.data,
            token: token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // Token invalid - logout
          console.log('Token invalid, logging out');
          get().logout();
          set({ isLoading: false });
        }
      },

      // Update user locally (after actions)
      updateUser: (updates) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        }));
      },

      // Refresh user data from server
      refreshUser: async () => {
        try {
          const response = await api.auth.me();
          set({ user: response.data });
        } catch (e) { /* silent */ }
      },

      // Refresh tokens
      refreshTokens: async () => {
        const refreshToken = localStorage.getItem('crickpredict_refresh_token');
        if (!refreshToken) return false;

        try {
          const response = await api.auth.refresh(refreshToken);
          const { access_token } = response.data;
          
          localStorage.setItem('crickpredict_token', access_token);
          set({ token: access_token });
          
          return true;
        } catch (error) {
          get().logout();
          return false;
        }
      },
    }),
    {
      name: 'crickpredict-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
