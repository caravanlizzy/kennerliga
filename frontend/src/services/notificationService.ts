import { api } from 'boot/axios';

const PUSH_DISABLED_KEY = 'kenner_push_notifications_disabled';

export function isPushUserDisabled(): boolean {
  try {
    return localStorage.getItem(PUSH_DISABLED_KEY) === 'true';
  } catch {
    return false;
  }
}

export function setPushUserDisabled(disabled: boolean): void {
  try {
    if (disabled) {
      localStorage.setItem(PUSH_DISABLED_KEY, 'true');
    } else {
      localStorage.removeItem(PUSH_DISABLED_KEY);
    }
  } catch {
    // Ignore storage errors in restricted contexts
  }
}

function decodeVapidPublicKey(value: string): Uint8Array {
  const padding = '='.repeat((4 - (value.length % 4)) % 4);
  const base64 = (value + padding).replace(/-/g, '+').replace(/_/g, '/');
  const data = atob(base64);
  return Uint8Array.from(data, (character) => character.charCodeAt(0));
}

// Thrown when the backend reports that VAPID keys are not configured (503),
// so the caller can show an accurate message instead of a generic failure.
export class PushNotConfiguredError extends Error {
  constructor() {
    super('Push notifications are not configured on the server.');
    this.name = 'PushNotConfiguredError';
  }
}

export function isPushNotificationSupported(): boolean {
  return 'Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window;
}

export async function getExistingPushSubscription(): Promise<PushSubscription | null> {
  if (!isPushNotificationSupported()) {
    return null;
  }
  try {
    const registration = await navigator.serviceWorker.ready;
    return await registration.pushManager.getSubscription();
  } catch (error) {
    console.error('Failed to get push subscription:', error);
    return null;
  }
}

export async function isPushNotificationSubscribed(): Promise<boolean> {
  if (!isPushNotificationSupported()) {
    return false;
  }
  if (isPushUserDisabled()) {
    return false;
  }
  if (Notification.permission !== 'granted') {
    return false;
  }
  const subscription = await getExistingPushSubscription();
  return subscription !== null;
}

async function fetchVapidPublicKey(): Promise<string> {
  try {
    const { data } = await api.get<{ public_key: string }>('/notifications/vapid-public-key/');
    return data.public_key;
  } catch (error) {
    if (
      typeof error === 'object' &&
      error !== null &&
      'response' in error &&
      (error as { response?: { status?: number } }).response?.status === 503
    ) {
      throw new PushNotConfiguredError();
    }
    throw error;
  }
}

// Registers the given subscription with the backend. Extracted so both the
// initial subscribe flow and the pushsubscriptionchange recovery can reuse it.
async function postSubscription(subscription: PushSubscription): Promise<void> {
  await api.post('/notifications/subscriptions/', subscription.toJSON());
}

async function deleteSubscription(endpoint: string): Promise<void> {
  await api.delete('/notifications/subscriptions/', { data: { endpoint } });
}

async function getOrCreateSubscription(
  registration: ServiceWorkerRegistration,
): Promise<PushSubscription> {
  const existing = await registration.pushManager.getSubscription();
  if (existing) {
    return existing;
  }
  const publicKey = await fetchVapidPublicKey();
  return registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: decodeVapidPublicKey(publicKey),
  });
}

export async function subscribeToPushNotifications(): Promise<boolean> {
  if (!isPushNotificationSupported()) {
    throw new Error('Push notifications are not supported by this browser.');
  }

  setPushUserDisabled(false);

  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    return false;
  }

  const registration = await navigator.serviceWorker.ready;
  const subscription = await getOrCreateSubscription(registration);
  await postSubscription(subscription);
  registerSubscriptionChangeHandler(registration);
  return true;
}

export async function unsubscribeFromPushNotifications(): Promise<void> {
  if (!isPushNotificationSupported()) {
    return;
  }

  setPushUserDisabled(true);

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      const endpoint = subscription.endpoint;
      try {
        await subscription.unsubscribe();
      } catch (err) {
        console.error('Failed to unsubscribe from browser push service:', err);
      }
      try {
        await deleteSubscription(endpoint);
      } catch (err) {
        console.error('Failed to delete subscription on backend:', err);
      }
    }
  } catch (error) {
    console.error('Error during push unsubscription:', error);
    throw error;
  }
}

// The browser can rotate a push subscription at any time; when it does, the
// old endpoint stops working. Re-subscribe and re-POST so delivery self-heals.
let subscriptionChangeHandlerRegistered = false;

function registerSubscriptionChangeHandler(registration: ServiceWorkerRegistration): void {
  if (subscriptionChangeHandlerRegistered) {
    return;
  }
  const target = registration.pushManager as unknown as EventTarget & {
    addEventListener?: EventTarget['addEventListener'];
  };
  if (typeof target.addEventListener !== 'function') {
    return;
  }
  subscriptionChangeHandlerRegistered = true;
  target.addEventListener('pushsubscriptionchange', () => {
    void (async () => {
      try {
        if (isPushUserDisabled()) {
          return;
        }
        const subscription = await getOrCreateSubscription(registration);
        await postSubscription(subscription);
      } catch (error) {
        console.error('Unable to recover rotated push subscription:', error);
      }
    })();
  });
}
