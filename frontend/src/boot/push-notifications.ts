import { boot } from 'quasar/wrappers';
import { watch } from 'vue';
import { Capacitor } from '@capacitor/core';
import {
  PushNotifications,
  type Token,
  type PermissionStatus,
} from '@capacitor/push-notifications';
import { useUserStore } from 'stores/userStore';
import {
  registerPushDevice,
  deactivatePushDevice,
} from 'src/services/pushNotificationService';

let activeToken: string | null = null;

async function registerForPush(userStore: ReturnType<typeof useUserStore>) {
  const permissions: PermissionStatus = await PushNotifications.requestPermissions();
  if (permissions.receive !== 'granted') {
    return;
  }

  PushNotifications.removeAllListeners();

  PushNotifications.addListener('registration', async (token: Token) => {
    activeToken = token.value;
    if (!userStore.isAuthenticated) {
      return;
    }
    await registerPushDevice({
      token: token.value,
      platform: Capacitor.getPlatform() as 'android' | 'ios' | 'web' | 'unknown',
      notify_registration_open: true,
      notify_league_started: true,
      notify_active_player: true,
    });
  });

  PushNotifications.addListener('registrationError', (error) => {
    console.error('Push registration error:', error);
  });

  await PushNotifications.register();
}

export default boot(async () => {
  if (!Capacitor.isNativePlatform()) {
    return;
  }

  const userStore = useUserStore();

  watch(
    () => userStore.isAuthenticated,
    async (isAuthenticated, wasAuthenticated) => {
      if (isAuthenticated) {
        await registerForPush(userStore);
        return;
      }

      if (wasAuthenticated && activeToken) {
        await deactivatePushDevice(activeToken);
        activeToken = null;
      }
    },
    { immediate: true }
  );
});
