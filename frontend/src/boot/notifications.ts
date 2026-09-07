import { Notify } from 'quasar';
import { boot } from 'quasar/wrappers';
import { watch } from 'vue';

import { isPushNotificationSupported, subscribeToPushNotifications } from 'src/services/notificationService';
import { useUserStore } from 'stores/userStore';

export default boot(() => {
  const userStore = useUserStore();

  async function enableNotifications(): Promise<void> {
    try {
      await subscribeToPushNotifications();
    } catch (error) {
      console.error('Unable to enable push notifications:', error);
      Notify.create({ type: 'negative', message: 'Notifications could not be enabled.' });
    }
  }

  function offerNotifications(): void {
    if (!userStore.isAuthenticated || !isPushNotificationSupported()) {
      return;
    }

    if (Notification.permission === 'granted') {
      void enableNotifications();
      return;
    }

    if (Notification.permission === 'default') {
      Notify.create({
        message: 'Enable notifications for registration, season starts, and your turn.',
        timeout: 0,
        actions: [{ label: 'Enable', color: 'white', handler: enableNotifications }],
      });
    }
  }

  watch(() => userStore.isAuthenticated, offerNotifications, { immediate: true });
});
