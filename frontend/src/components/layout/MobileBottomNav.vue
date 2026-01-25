<template>
  <q-footer v-if="isMobile && isAuthenticated" bordered class="bg-white text-dark mobile-bottom-nav">
    <q-tabs
      :model-value="activeTab"
      class="full-width"
      active-color="primary"
      indicator-color="transparent"
      align="justify"
      dense
      no-caps
      @update:model-value="handleTabChange"
    >
      <q-tab name="welcome" icon="home" label="Home" />
      <q-tab name="seasons" icon="military_tech" label="Seasons" />
      <q-tab name="live" icon="bolt" label="Live" />
      <q-tab name="chat" icon="chat" label="Chat" />
      <q-tab name="leaderboard" icon="stars" label="Stats" />
    </q-tabs>
  </q-footer>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useResponsive } from 'src/composables/responsive';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

const route = useRoute();
const router = useRouter();
const { isMobile } = useResponsive();
const { isAuthenticated } = storeToRefs(useUserStore());

const activeTab = computed(() => {
  const name = route.name as string;
  if (name === 'home') return 'welcome';
  if (name === 'mobile-seasons' || name === 'seasons') return 'seasons';
  if (name === 'mobile-live' || name === 'live') return 'live';
  if (name === 'mobile-chat' || name === 'chat') return 'chat';
  if (name === 'mobile-leaderboard' || name === 'leaderboard') return 'leaderboard';
  return null;
});

function handleTabChange(value: string) {
  switch (value) {
    case 'welcome':
      router.push({ name: 'home' });
      break;
    case 'seasons':
      router.push({ name: 'mobile-seasons' });
      break;
    case 'live':
      router.push({ name: 'mobile-live' });
      break;
    case 'chat':
      router.push({ name: 'mobile-chat' });
      break;
    case 'leaderboard':
      router.push({ name: 'mobile-leaderboard' });
      break;
  }
}
</script>

<style lang="scss" scoped>
.mobile-bottom-nav {
  height: 60px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  border-top: 1px solid rgba(0, 0, 0, 0.05) !important;

  :deep(.q-tab) {
    min-height: 60px;
    padding: 0;

    .q-tab__icon {
      font-size: 22px;
    }

    .q-tab__label {
      font-size: 10px;
      font-weight: 600;
      margin-top: 2px;
    }

    &.q-tab--active {
      .q-tab__icon, .q-tab__label {
        color: var(--q-primary);
      }
    }
  }
}
</style>
