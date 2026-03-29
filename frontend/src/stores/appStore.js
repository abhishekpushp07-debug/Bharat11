/**
 * App Store - Zustand
 * Global app state (theme, navigation, UI state)
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export const useAppStore = create(
  persist(
    (set, get) => ({
      // Theme
      theme: 'dark', // Always dark for CrickPredict
      
      // Navigation
      activeTab: 'home',
      setActiveTab: (tab) => set({ activeTab: tab }),
      
      // UI State
      isLoading: false,
      setLoading: (isLoading) => set({ isLoading }),
      
      // Bottom Sheet
      bottomSheet: {
        isOpen: false,
        content: null,
        title: '',
      },
      openBottomSheet: (content, title = '') => 
        set({ bottomSheet: { isOpen: true, content, title } }),
      closeBottomSheet: () => 
        set({ bottomSheet: { isOpen: false, content: null, title: '' } }),
      
      // Toast/Notifications
      toast: null,
      showToast: (message, type = 'info', duration = 3000) => {
        const id = Date.now();
        set({ toast: { id, message, type, duration } });
        setTimeout(() => {
          if (get().toast?.id === id) {
            set({ toast: null });
          }
        }, duration);
      },
      hideToast: () => set({ toast: null }),
      
      // Language preference
      language: 'hi', // Default Hindi, can be 'en'
      setLanguage: (lang) => set({ language: lang }),
      
      // PWA Install prompt
      installPrompt: null,
      setInstallPrompt: (prompt) => set({ installPrompt: prompt }),
      clearInstallPrompt: () => set({ installPrompt: null }),
      
      // Network status
      isOnline: navigator.onLine,
      setOnline: (status) => set({ isOnline: status }),
    }),
    {
      name: 'crickpredict-app',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        language: state.language,
        activeTab: state.activeTab,
      }),
    }
  )
);

// Listen for online/offline events
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    useAppStore.getState().setOnline(true);
    useAppStore.getState().showToast('Back online!', 'success');
  });
  
  window.addEventListener('offline', () => {
    useAppStore.getState().setOnline(false);
    useAppStore.getState().showToast('You are offline', 'warning');
  });
  
  // Listen for PWA install prompt
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    useAppStore.getState().setInstallPrompt(e);
  });
}
