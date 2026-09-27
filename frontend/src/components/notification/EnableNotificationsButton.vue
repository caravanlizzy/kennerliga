<template>
  <q-btn
    :color="color"
    :flat="flat"
    :outline="outline"
    :dense="dense"
    :unelevated="unelevated"
    :rounded="rounded"
    :class="customClass"
    icon="notifications"
    :label="label"
    :loading="loading"
    @click="enableNotifications"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Notify } from 'quasar';
import {
  isPushNotificationSupported,
  PushNotConfiguredError,
  subscribeToPushNotifications,
} from 'src/services/notificationService';

interface Props {
  color?: string;
  flat?: boolean;
  outline?: boolean;
  dense?: boolean;
  unelevated?: boolean;
  rounded?: boolean;
  customClass?: string;
  label?: string;
}

withDefaults(defineProps<Props>(), {
  color: 'primary',
  flat: false,
  outline: false,
  dense: false,
  unelevated: true,
  rounded: false,
  customClass: '',
  label: 'Enable notifications',
});

const loading = ref(false);

async function enableNotifications(): Promise<void> {
  if (!isPushNotificationSupported()) {
    Notify.create({
      type: 'negative',
      message: 'Push notifications are not supported on this device/browser.',
    });
    return;
  }

  loading.value = true;
  try {
    await subscribeToPushNotifications();
    Notify.create({
      type: 'positive',
      message: 'Notifications enabled.',
    });
  } catch (error) {
    console.error('Unable to enable push notifications:', error);

    Notify.create({
      type: 'negative',
      message:
        error instanceof PushNotConfiguredError
          ? 'Notifications are not configured on the server yet.'
          : 'Notifications could not be enabled.',
    });
  } finally {
    loading.value = false;
  }
}
</script>
