<template>
  <q-btn
    :color="color"
    :flat="flat"
    :outline="outline"
    :dense="dense"
    :unelevated="unelevated"
    :rounded="rounded"
    :class="customClass"
    :icon="subscribed ? 'notifications_active' : 'notifications_none'"
    :label="effectiveLabel"
    :loading="loading"
    @click="toggleNotifications"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Notify } from 'quasar';
import {
  isPushNotificationSupported,
  isPushNotificationSubscribed,
  PushNotConfiguredError,
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications,
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

const props = withDefaults(defineProps<Props>(), {
  color: 'primary',
  flat: false,
  outline: false,
  dense: false,
  unelevated: true,
  rounded: false,
  customClass: '',
  label: '',
});

const loading = ref(false);
const subscribed = ref(false);

const effectiveLabel = computed(() => {
  if (props.label) return props.label;
  return subscribed.value ? 'Disable notifications' : 'Enable notifications';
});

async function checkStatus() {
  if (!isPushNotificationSupported()) {
    subscribed.value = false;
    return;
  }
  try {
    subscribed.value = await isPushNotificationSubscribed();
  } catch {
    subscribed.value = false;
  }
}

async function toggleNotifications(): Promise<void> {
  if (!isPushNotificationSupported()) {
    Notify.create({
      type: 'negative',
      message: 'Push notifications are not supported on this device/browser.',
    });
    return;
  }

  loading.value = true;
  try {
    if (subscribed.value) {
      await unsubscribeFromPushNotifications();
      subscribed.value = false;
      Notify.create({
        type: 'info',
        message: 'Notifications disabled.',
      });
    } else {
      const granted = await subscribeToPushNotifications();
      if (granted) {
        subscribed.value = true;
        Notify.create({
          type: 'positive',
          message: 'Notifications enabled.',
        });
      } else {
        subscribed.value = false;
        Notify.create({
          type: 'warning',
          message: 'Notification permission was denied or dismissed.',
        });
      }
    }
  } catch (error) {
    console.error('Unable to update push notifications:', error);

    Notify.create({
      type: 'negative',
      message:
        error instanceof PushNotConfiguredError
          ? 'Notifications are not configured on the server yet.'
          : 'Notifications could not be updated.',
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void checkStatus();
});
</script>
