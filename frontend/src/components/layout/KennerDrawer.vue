<template>
  <div class="column full-height kenner-drawer-container glass-effect">
    <!-- Drawer Header -->
    <div
      class="q-pa-lg q-mb-sm row items-center border-bottom-subtle bg-drawer-header"
    >
      <q-icon name="img:icons/favicon.svg" size="36px" class="q-mr-sm" />
      <q-space />
      <KennerButton
        flat
        round
        dense
        icon="close"
        color="grey-7"
        @click="drawerState = false"
      />
    </div>

    <!-- Drawer Content -->
    <div class="col scroll q-px-sm">
      <q-list class="q-py-sm">
        <DrawerSubGroup>Browse</DrawerSubGroup>
        <DrawerItem
          icon="event"
          icon-color="primary"
          label="Seasons"
          forward-name="seasons"
        />
        <DrawerItem
          icon="people_alt"
          icon-color="primary"
          label="Players"
          forward-name="players"
        />
        <DrawerItem
          icon="query_stats"
          icon-color="primary"
          label="Statistics"
          forward-name="statistics"
        />

        <q-separator class="q-my-sm drawer-separator" />
        <DrawerSubGroup>Info</DrawerSubGroup>
        <DrawerItem
          icon="menu_book"
          icon-color="primary"
          label="Rules"
          forward-name="rules"
        />
        <DrawerItem
          icon="info"
          icon-color="primary"
          label="About"
          forward-name="about"
        />

        <q-separator class="q-my-sm drawer-separator" />
        <DrawerSubGroup>Preferences</DrawerSubGroup>
        <div
          class="drawer-preference-item q-mx-sm row items-center justify-between squircle-shape"
        >
          <div class="row items-center no-wrap">
            <div
              class="drawer-preference-item__icon-section row items-center justify-center"
            >
              <q-icon :name="themeModeIcon" size="20px" color="primary" />
            </div>
            <span
              class="drawer-preference-item__label text-weight-medium q-pl-xs"
            >
              Dark Mode
            </span>
          </div>
          <q-btn-toggle
            :model-value="themeStore.mode"
            dense
            rounded
            unelevated
            toggle-color="primary"
            :color="themeStore.isDark ? 'dark' : 'grey-3'"
            :text-color="themeStore.isDark ? 'grey-4' : 'grey-8'"
            :options="[
              { value: 'light', slot: 'light' },
              { value: 'dark', slot: 'dark' },
              { value: 'auto', slot: 'auto' },
            ]"
            class="theme-toggle-group"
            @update:model-value="onThemeModeChange"
          >
            <template #light>
              <q-icon name="light_mode" size="16px" />
              <KennerTooltip>Light</KennerTooltip>
            </template>
            <template #dark>
              <q-icon name="dark_mode" size="16px" />
              <KennerTooltip>Dark</KennerTooltip>
            </template>
            <template #auto>
              <q-icon name="brightness_auto" size="16px" />
              <KennerTooltip>Auto</KennerTooltip>
            </template>
          </q-btn-toggle>
        </div>

        <q-item
          tag="label"
          dense
          class="drawer-item drawer-item--action q-mx-sm squircle-shape cursor-pointer"
        >
          <q-item-section avatar class="drawer-item__icon-section">
            <q-icon
              :name="
                notificationsSubscribed
                  ? 'notifications_active'
                  : 'notifications_off'
              "
              size="20px"
              color="primary"
            />
          </q-item-section>
          <q-item-section class="drawer-item__text-section">
            <q-item-label class="drawer-item__label text-weight-medium">
              Notifications
            </q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-toggle
              :model-value="notificationsSubscribed"
              :loading="notificationsLoading"
              dense
              color="primary"
              @update:model-value="toggleNotifications"
            >
              <KennerTooltip>
                {{
                  notificationsSubscribed
                    ? 'Disable notifications'
                    : 'Enable notifications'
                }}
              </KennerTooltip>
            </q-toggle>
          </q-item-section>
        </q-item>

        <template v-if="isAdmin">
          <q-separator class="q-my-sm drawer-separator" />
          <DrawerSubGroup>Management</DrawerSubGroup>
          <DrawerItem
            icon="admin_panel_settings"
            icon-color="primary"
            label="Admin"
            forward-name="admin"
          />
          <DrawerItem
            v-if="currentSeasonId"
            icon="settings_applications"
            icon-color="primary"
            label="Current Season"
            :forward-params="{ id: currentSeasonId }"
            forward-name="season-manage"
          />
          <DrawerItem
            icon="sports_esports"
            icon-color="primary"
            label="Games"
            forward-name="games"
          />
          <DrawerItem
            icon="mark_email_unread"
            icon-color="primary"
            label="Invitations & Passwords"
            forward-name="invitations"
          />
          <DrawerItem
            icon="settings"
            icon-color="primary"
            label="Configuration"
            forward-name="configuration"
          />
        </template>
      </q-list>
    </div>

    <div class="q-pa-md q-pb-xl">
      <q-separator class="q-mb-md drawer-separator" />
      <DrawerItem
        icon="exit_to_app"
        icon-color="red-7"
        label="Logout"
        class="logout-item"
        @click="doLogout"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Notify } from 'quasar';
import KennerButton from 'components/base/KennerButton.vue';
import DrawerItem from 'components/base/DrawerItem.vue';
import DrawerSubGroup from 'components/base/DrawerSubGroup.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import {
  isPushNotificationSupported,
  isPushNotificationSubscribed,
  PushNotConfiguredError,
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications,
} from 'src/services/notificationService';
import { useUserStore } from 'stores/userStore';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';
import { useThemeStore, ThemeMode } from 'stores/themeStore';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { provide, watch, ref, computed } from 'vue';

const drawerState = defineModel();

const themeStore = useThemeStore();
const { logout } = useUserStore();
const userStore = useUserStore();
const { isAdmin } = storeToRefs(userStore);

const homeSeasonStore = useHomeSeasonStore();
const { currentSeasonId } = storeToRefs(homeSeasonStore);

const router = useRouter();
const notificationsSubscribed = ref(false);
const notificationsLoading = ref(false);

const themeModeIcon = computed(() => {
  if (themeStore.mode === 'auto') return 'brightness_auto';
  return themeStore.isDark ? 'dark_mode' : 'light_mode';
});

function onThemeModeChange(newMode: ThemeMode) {
  if (newMode) {
    themeStore.setMode(newMode);
  }
}

provide('closeDrawer', () => (drawerState.value = false));

watch(
  isAdmin,
  (val) => {
    if (val) {
      void homeSeasonStore.init();
    }
  },
  { immediate: true }
);

async function checkNotificationStatus() {
  if (!isPushNotificationSupported()) {
    notificationsSubscribed.value = false;
    return;
  }
  try {
    notificationsSubscribed.value = await isPushNotificationSubscribed();
  } catch {
    notificationsSubscribed.value = false;
  }
}

watch(
  drawerState,
  (open) => {
    if (open) {
      void checkNotificationStatus();
    }
  },
  { immediate: true }
);

async function toggleNotifications(): Promise<void> {
  if (notificationsLoading.value) return;
  if (!isPushNotificationSupported()) {
    Notify.create({
      type: 'negative',
      message: 'Push notifications are not supported on this device/browser.',
    });
    return;
  }

  notificationsLoading.value = true;
  try {
    if (notificationsSubscribed.value) {
      await unsubscribeFromPushNotifications();
      notificationsSubscribed.value = false;
      Notify.create({
        type: 'info',
        message: 'Notifications disabled.',
      });
    } else {
      const granted = await subscribeToPushNotifications();
      if (granted) {
        notificationsSubscribed.value = true;
        Notify.create({
          type: 'positive',
          message: 'Notifications enabled.',
        });
      } else {
        notificationsSubscribed.value = false;
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
    notificationsLoading.value = false;
  }
}

async function doLogout(): Promise<void> {
  await logout();
  drawerState.value = false;
  await router.push({ name: 'home' });
}
</script>

<style lang="scss">
.kenner-drawer-container {
}

.bg-drawer-header {
}

.glass-effect {
  border-left: 1px solid var(--kenner-border-subtle);
  border-bottom: none !important;
}

.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);

  .body--dark & {
    border-bottom-color: var(--kenner-border-subtle);
  }
}

.drawer-separator {
  opacity: 0.15;
  margin: 16px 24px;
}

.drawer-preference-item {
  min-height: 38px;
  padding: 4px 12px;
  margin: 1px 0;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  color: #555;

  .body--dark & {
    color: var(--kenner-text-secondary);
  }

  &.squircle-shape {
    border-radius: var(--kenner-card-radius, 0px) !important;
  }
}

.drawer-preference-item__icon-section {
  min-width: 36px !important;
  padding-right: 0 !important;
}

.drawer-preference-item__label {
  font-size: 0.9375rem;
  line-height: 1.2;
}

.theme-toggle-group {
  padding: 2px;
  background: rgba(0, 0, 0, 0.05);

  .body--dark & {
    background: rgba(255, 255, 255, 0.08);
  }

  .q-btn {
    padding: 2px 8px;
    min-height: 24px;
  }
}

.drawer-item {
  min-height: 32px;
  padding: 2px 12px;
  margin: 1px 0;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  color: #555;

  .body--dark & {
    color: var(--kenner-text-secondary);
  }

  &.squircle-shape {
    border-radius: var(--kenner-card-radius, 0px) !important;
  }

  &--action:hover {
    background: rgba(var(--q-primary), 0.05);
    color: var(--kenner-primary-text);

    .q-icon {
      color: var(--kenner-primary-text);
    }
  }
}

.drawer-item__icon-section {
  min-width: 36px !important;
  padding-right: 0 !important;
  transition: transform 0.2s ease;
}

.drawer-item__text-section {
  padding-left: 8px;
}

.drawer-item__label {
  font-size: 0.9375rem;
  line-height: 1.2;
}

.logout-item {
  border: 1px solid rgba(255, 0, 0, 0.05);
  background: rgba(255, 0, 0, 0.02);
  &:hover {
    background: rgba(255, 0, 0, 0.06);
    color: #d32f2f !important;

    .body--dark & {
      color: var(--kenner-danger-text) !important;
    }
  }
}

.kenner-drawer {
}
</style>
