/**
 * Bharat 11 — Push Notification Helper
 * Handles subscription, permission, and push management
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import { useAuthStore } from '../stores/authStore';

const VAPID_PUBLIC_KEY = process.env.REACT_APP_VAPID_PUBLIC_KEY;

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function usePushNotifications() {
  const { isAuthenticated } = useAuthStore();
  const [permission, setPermission] = useState(
    typeof Notification !== 'undefined' ? Notification.permission : 'denied'
  );
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    const supported = 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
    setIsSupported(supported);

    if (supported) {
      setPermission(Notification.permission);
      // Check if already subscribed
      navigator.serviceWorker.ready.then((reg) => {
        reg.pushManager.getSubscription().then((sub) => {
          setIsSubscribed(!!sub);
        });
      });
    }
  }, []);

  const subscribe = useCallback(async () => {
    if (!isSupported || !isAuthenticated || !VAPID_PUBLIC_KEY) return false;

    try {
      const perm = await Notification.requestPermission();
      setPermission(perm);
      if (perm !== 'granted') return false;

      const reg = await navigator.serviceWorker.ready;
      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });

      // Send subscription to backend
      const subJson = subscription.toJSON();
      await apiClient.post('/notifications/subscribe', {
        subscription: subJson,
      });

      setIsSubscribed(true);
      return true;
    } catch (err) {
      console.error('[Push] Subscription failed:', err);
      return false;
    }
  }, [isSupported, isAuthenticated]);

  const unsubscribe = useCallback(async () => {
    if (!isSupported) return;

    try {
      const reg = await navigator.serviceWorker.ready;
      const subscription = await reg.pushManager.getSubscription();
      if (subscription) {
        const subJson = subscription.toJSON();
        await subscription.unsubscribe();
        await apiClient.post('/notifications/unsubscribe', {
          subscription: subJson,
        });
      }
      setIsSubscribed(false);
    } catch (err) {
      console.error('[Push] Unsubscribe failed:', err);
    }
  }, [isSupported]);

  return {
    isSupported,
    permission,
    isSubscribed,
    subscribe,
    unsubscribe,
  };
}
