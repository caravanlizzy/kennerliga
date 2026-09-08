import { Notify } from 'quasar';
import { boot } from 'quasar/wrappers';
import { watch } from 'vue';

import {
  isPushNotificationSupported,
  PushNotConfiguredError,
  subscribeToPushNotifications,
} from 'src/services/notificationService';
import { useUserStore } from 'stores/userStore';

export default boot(() => {
  const userStore = useUserStore();

  async function enableNotifications(): Promise<void> {
    try {
      await subscribeToPushNotifications();
    } catch (error) {
      console.error('Unable to enable push notifications:', error);
      const message =
        error instanceof PushNotConfiguredError
          ? 'Notifications are not configured on the server yet.'
          : 'Notifications could not be enabled.';
      Notify.create({ type: 'negative', message });
    }
  }

  function offerNotifications(): void {
    if (!userStore.isAuthenticated || !isPushNotificationSupported()) {
      return;
    }

    if (Notification.permission === 'granted') {
      void enableNotifications();
    }
  }

  watch(() => userStore.isAuthenticated, offerNotifications, { immediate: true });
});
