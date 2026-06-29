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
      <q-tab name="leaderboard" icon="stars" label="Rank" />
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
  switch (route.name) {
    case 'home': return 'welcome';
    case 'season-standings': return 'seasons';
    case 'live': return 'live';
    case 'chat': return 'chat';
    case 'leaderboard': return 'leaderboard';
    default: return null;
  }
});

const tabToRoute = {
  welcome: 'home',
  seasons: 'season-standings',
  live: 'live',
  chat: 'chat',
  leaderboard: 'leaderboard',
} as const;

function handleTabChange(value: string) {
  const name = tabToRoute[value as keyof typeof tabToRoute];
  if (name) router.push({ name });
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
