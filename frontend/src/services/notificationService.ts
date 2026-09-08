import { api } from 'boot/axios';

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

export async function subscribeToPushNotifications(): Promise<void> {
  if (!isPushNotificationSupported()) {
    throw new Error('Push notifications are not supported by this browser.');
  }

  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    return;
  }

  const registration = await navigator.serviceWorker.ready;
  const subscription = await getOrCreateSubscription(registration);
  await postSubscription(subscription);
  registerSubscriptionChangeHandler(registration);
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
        const subscription = await getOrCreateSubscription(registration);
        await postSubscription(subscription);
      } catch (error) {
        console.error('Unable to recover rotated push subscription:', error);
      }
    })();
  });
}
