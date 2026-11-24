import { ref } from 'vue';
import { Notify } from 'quasar';
import type { Router } from 'vue-router';

export const appVersion = process.env.APP_VERSION || '1.0.0';

export const updateAvailable = ref(false);
export const isCheckingForUpdates = ref(false);

let swRegistration: ServiceWorkerRegistration | null = null;
let updateNotificationDismissFn: (() => void) | null = null;
let lastCheckTimestamp = 0;
let isRefreshing = false;

/**
 * Attaches listeners to a service worker registration to track when
 * a new service worker finishes installing and is waiting to activate.
 */
function attachRegistrationListeners(registration: ServiceWorkerRegistration) {
  if (registration.waiting) {
    updateAvailable.value = true;
    showUpdatePrompt(registration);
    return;
  }

  registration.addEventListener('updatefound', () => {
    const installingWorker = registration.installing;
    if (!installingWorker) return;

    installingWorker.addEventListener('statechange', () => {
      if (
        installingWorker.state === 'installed' &&
        navigator.serviceWorker.controller
      ) {
        updateAvailable.value = true;
        showUpdatePrompt(registration);
      }
    });
  });
}

/**
 * Register the ServiceWorkerRegistration instance from register-service-worker.js.
 */
export function setServiceWorkerRegistration(
  registration: ServiceWorkerRegistration
) {
  swRegistration = registration;
  attachRegistrationListeners(registration);
}

/**
 * Handler called when register-service-worker fires its `updated` event.
 */
export function onServiceWorkerUpdated(
  registration: ServiceWorkerRegistration
) {
  swRegistration = registration;
  updateAvailable.value = true;
  showUpdatePrompt(registration);
}

/**
 * Applies the waiting service worker update and reloads the application.
 */
export async function applyUpdate(
  registration?: ServiceWorkerRegistration | null
) {
  const reg = registration || swRegistration;

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (isRefreshing) return;
      isRefreshing = true;
      window.location.reload();
    });
  }

  if (reg?.waiting) {
    reg.waiting.postMessage({ type: 'SKIP_WAITING' });
  }

  // Fallback reload if controllerchange doesn't fire within 800ms
  setTimeout(() => {
    if (!isRefreshing) {
      isRefreshing = true;
      window.location.reload();
    }
  }, 800);
}

/**
 * Displays a non-intrusive, persistent notification informing the user
 * that an update is available with an immediate action to update.
 */
export function showUpdatePrompt(
  registration?: ServiceWorkerRegistration | null,
  isManual = false
) {
  // If a notification is already open, dismiss previous one to prevent stacking
  if (updateNotificationDismissFn) {
    updateNotificationDismissFn();
    updateNotificationDismissFn = null;
  }

  const reg = registration || swRegistration;

  updateNotificationDismissFn = Notify.create({
    message: 'New version available!',
    caption: 'Click update to apply the latest Kennerliga version.',
    icon: 'system_update',
    color: 'primary',
    textColor: 'white',
    position: 'bottom-right',
    timeout: 0,
    multiLine: true,
    classes: 'kenner-update-notification',
    actions: [
      {
        label: 'Update now',
        icon: 'refresh',
        color: 'white',
        handler: () => {
          void applyUpdate(reg);
        },
      },
      {
        label: 'Later',
        color: 'grey-4',
        handler: () => {
          updateNotificationDismissFn = null;
        },
      },
    ],
    onDismiss: () => {
      updateNotificationDismissFn = null;
    },
  });

  if (isManual) {
    updateAvailable.value = true;
  }
}

/**
 * Manually or automatically checks for service worker updates.
 * @param manual If true, provides user feedback if already on the latest version.
 */
export async function checkForUpdates(manual = false): Promise<boolean> {
  if (isCheckingForUpdates.value) return false;
  isCheckingForUpdates.value = true;
  lastCheckTimestamp = Date.now();

  try {
    if (!('serviceWorker' in navigator)) {
      if (manual) {
        Notify.create({
          type: 'info',
          message: 'Updates are managed automatically by your browser.',
        });
      }
      return false;
    }

    const reg =
      swRegistration || (await navigator.serviceWorker.getRegistration());
    if (!reg) {
      if (manual) {
        Notify.create({
          type: 'positive',
          message: 'You are using the latest version of Kennerliga.',
          icon: 'check_circle',
        });
      }
      return false;
    }

    swRegistration = reg;

    if (reg.waiting) {
      updateAvailable.value = true;
      showUpdatePrompt(reg, manual);
      return true;
    }

    await reg.update();

    if (
      reg.waiting ||
      (reg.installing && reg.installing.state === 'installed')
    ) {
      updateAvailable.value = true;
      showUpdatePrompt(reg, manual);
      return true;
    }

    if (manual) {
      Notify.create({
        type: 'positive',
        message: 'You are using the latest version of Kennerliga.',
        icon: 'check_circle',
      });
    }
    return false;
  } catch (error) {
    console.error('Failed to check for app updates:', error);
    if (manual) {
      Notify.create({
        type: 'warning',
        message:
          'Could not check for updates right now. Please try again later.',
      });
    }
    return false;
  } finally {
    isCheckingForUpdates.value = false;
  }
}

/**
 * Initializes automatic background update checks and chunk loading failure recovery.
 */
export function initAppUpdateListeners(router?: Router) {
  if (typeof window === 'undefined') return;

  // Handle Vite dynamic import chunk loading errors (e.g. after a new deployment)
  window.addEventListener('vite:preloadError', (event) => {
    console.warn(
      'Vite preload error detected (possible new deployment), reloading page...',
      event
    );
    window.location.reload();
  });

  // Check for updates when user returns to tab / PWA
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      const fiveMinutes = 5 * 60 * 1000;
      if (Date.now() - lastCheckTimestamp > fiveMinutes) {
        void checkForUpdates(false);
      }
    }
  });

  // Periodic update check every 15 minutes
  setInterval(() => {
    void checkForUpdates(false);
  }, 15 * 60 * 1000);

  // Throttled update check on route navigation (at most once every 5 minutes)
  if (router) {
    router.afterEach(() => {
      const fiveMinutes = 5 * 60 * 1000;
      if (Date.now() - lastCheckTimestamp > fiveMinutes) {
        void checkForUpdates(false);
      }
    });
  }
}
