<template>
  <q-footer v-if="isMobile && isAuthenticated" class="text-dark mobile-bottom-nav">
    <q-tabs
      :model-value="activeTab"
      class="full-width"
      indicator-color="transparent"
      align="justify"
      dense
      no-caps
      @update:model-value="handleTabChange"
    >
      <q-tab name="seasons" icon="military_tech" label="Seasons" />
      <q-tab name="live" icon="bolt" label="Live" />
      <!-- Chat feature temporarily disabled -->
      <!-- <q-tab name="chat" icon="chat" label="Chat" /> -->
      <q-tab name="leaderboard" icon="stars" label="Rank" />
      <q-tab name="stats" icon="query_stats" label="Stats" />
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
    case 'season-standings': return 'seasons';
    case 'live': return 'live';
    case 'chat': return 'chat';
    case 'leaderboard': return 'leaderboard';
    case 'statistics': return 'stats';
    default: return null;
  }
});

const tabToRoute = {
  seasons: 'season-standings',
  live: 'live',
  chat: 'chat',
  leaderboard: 'leaderboard',
  stats: 'statistics',
} as const;

function handleTabChange(value: string) {
  const name = tabToRoute[value as keyof typeof tabToRoute];
  if (name) router.push({ name });
}
</script>

<style lang="scss" scoped>
.mobile-bottom-nav {
  height: calc(50px + env(safe-area-inset-bottom));
  padding-bottom: env(safe-area-inset-bottom);
  background: var(--kenner-bg-glass, rgba(255, 255, 255, 0.98)) !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-top: 1px solid var(--kenner-border-color) !important;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.04);

  // Pin the tab layout deterministically instead of trusting q-tabs' own
  // width measurement. q-tabs measures its content width internally to decide
  // whether to enter "scrollable" mode; on a bfcache restore (reopening the
  // site from cache) that stale/misfired measurement survives and the content
  // wrapper stays in flex-start/scrollable state, squishing every tab into the
  // left half of the bar. Forcing the wrapper full width + space-between and
  // giving each tab equal flex makes the bar always span full width regardless
  // of what q-tabs thinks its size is (a hard refresh re-measures, which is why
  // it never persisted there).
  :deep(.q-tabs__content) {
    width: 100%;
    justify-content: space-between;
  }

  :deep(.q-tabs--scrollable) {
    .q-tabs__arrow {
      display: none;
    }
  }

  :deep(.q-tab) {
    flex: 1 1 0;
    min-height: 50px;
    padding: 0;
    color: #64748b;
    transition: all 0.2s ease;

    .q-tab__icon {
      font-size: 22px;
      margin-bottom: 2px;
      color: #64748b;
      transition: transform 0.2s ease, color 0.2s ease;
    }

    .q-tab__label {
      font-size: 10px;
      font-weight: 500;
      margin-top: 1px;
      color: #64748b;
      transition: color 0.2s ease, font-weight 0.2s ease;
    }

    &.q-tab--active {
      color: $dark;

      .q-tab__icon {
        transform: translateY(-2px);
        color: $dark;
      }

      .q-tab__label {
        font-weight: 600;
        color: $dark;
      }
    }
  }
}
</style>
