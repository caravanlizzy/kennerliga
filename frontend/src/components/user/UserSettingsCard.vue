<template>
  <q-card flat bordered class="q-mb-lg surface-card">
    <q-card-section class="surface-card-header text-weight-bold text-uppercase letter-spacing-1 row items-center justify-between q-py-sm">
      <div class="row items-center q-gutter-x-sm">
        <q-icon name="settings" size="xs" />
        <div class="text-caption text-weight-bolder">Settings</div>
      </div>
    </q-card-section>

    <q-list separator>
      <q-item class="q-py-md">
        <q-item-section avatar min-width="40px" class="q-pr-none">
          <q-avatar
            size="36px"
            :color="notificationsEnabled ? 'primary' : 'grey-4'"
            :text-color="notificationsEnabled ? 'white' : 'grey-8'"
            :icon="notificationsEnabled ? 'notifications_active' : 'notifications_off'"
            class="shadow-1 transition-all"
          />
        </q-item-section>

        <q-item-section>
          <div class="row items-center q-gutter-x-xs">
            <span class="text-weight-bold text-body2">Push Notifications</span>
            <q-badge
              v-if="!supported"
              color="grey-6"
              label="Unsupported"
              class="q-ml-xs text-caption"
            />
            <q-badge
              v-else-if="permissionDenied"
              color="negative"
              label="Blocked"
              class="q-ml-xs text-caption"
            />
          </div>
          <div class="text-caption text-grey-6 q-mt-xs">
            <template v-if="!supported">
              Push notifications are not supported by this browser.
            </template>
            <template v-else-if="permissionDenied">
              Permission was blocked in your browser settings.
            </template>
            <template v-else-if="notificationsEnabled">
              Receive updates for matches, picks, and league announcements.
            </template>
            <template v-else>
              Enable notifications to stay up to date with matches and picks.
            </template>
          </div>
        </q-item-section>

        <q-item-section side>
          <q-toggle
            v-model="notificationsEnabled"
            :disable="!supported || permissionDenied || loading"
            color="primary"
            @update:model-value="onToggleNotifications"
          />
        </q-item-section>
      </q-item>
    </q-list>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Notify } from 'quasar';
import {
  isPushNotificationSupported,
  isPushNotificationSubscribed,
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications,
  PushNotConfiguredError,
} from 'src/services/notificationService';

const supported = ref(isPushNotificationSupported());
const permissionDenied = ref(typeof Notification !== 'undefined' && Notification.permission === 'denied');
const notificationsEnabled = ref(false);
const loading = ref(false);

async function checkStatus() {
  if (!supported.value) {
    notificationsEnabled.value = false;
    return;
  }
  permissionDenied.value = Notification.permission === 'denied';
  try {
    notificationsEnabled.value = await isPushNotificationSubscribed();
  } catch (err) {
    console.error('Error checking notification subscription:', err);
    notificationsEnabled.value = false;
  }
}

async function onToggleNotifications(enable: boolean) {
  if (!supported.value) {
    Notify.create({
      type: 'negative',
      message: 'Push notifications are not supported on this device/browser.',
    });
    notificationsEnabled.value = false;
    return;
  }

  loading.value = true;
  if (enable) {
    try {
      const granted = await subscribeToPushNotifications();
      permissionDenied.value = Notification.permission === 'denied';
      if (granted) {
        notificationsEnabled.value = true;
        Notify.create({
          type: 'positive',
          message: 'Push notifications enabled.',
        });
      } else {
        notificationsEnabled.value = false;
        if (permissionDenied.value) {
          Notify.create({
            type: 'warning',
            message: 'Notification permission was denied in your browser settings.',
          });
        }
      }
    } catch (error) {
      console.error('Failed to enable notifications:', error);
      notificationsEnabled.value = false;
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
  } else {
    try {
      await unsubscribeFromPushNotifications();
      notificationsEnabled.value = false;
      Notify.create({
        type: 'info',
        message: 'Push notifications disabled.',
      });
    } catch (error) {
      console.error('Failed to disable notifications:', error);
      Notify.create({
        type: 'negative',
        message: 'Could not disable notifications. Please try again.',
      });
      // Re-sync state
      await checkStatus();
    } finally {
      loading.value = false;
    }
  }
}

onMounted(() => {
  void checkStatus();
});
</script>

<style scoped lang="scss">
.surface-card {
  background: var(--surface-bg) !important;
  border-color: var(--surface-border) !important;
  border-radius: 12px;
}

.surface-card-header {
  background: var(--surface-header-bg);
  color: var(--surface-header-text);
  border-bottom: 1px solid var(--divider);
}

.letter-spacing-1 {
  letter-spacing: 1px;
}

.transition-all {
  transition: all 0.3s ease;
}
</style>
