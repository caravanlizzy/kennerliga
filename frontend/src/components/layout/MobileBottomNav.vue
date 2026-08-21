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
      <q-tab name="seasons" icon="military_tech" label="Seasons" class="tab-seasons" />
      <q-tab name="live" icon="bolt" label="Live" class="tab-live" />
      <!-- Chat feature temporarily disabled -->
      <!-- <q-tab name="chat" icon="chat" label="Chat" /> -->
      <q-tab name="leaderboard" icon="stars" label="Rank" class="tab-leaderboard" />
      <q-tab name="stats" icon="query_stats" label="Stats" class="tab-stats" />
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
  border-top: none !important;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.03);

  :deep(.q-tab) {
    min-height: 50px;
    padding: 0;
    transition: all 0.2s ease;

    .q-tab__icon {
      font-size: 22px;
      margin-bottom: 2px;
      transition: transform 0.2s ease;
    }

    .q-tab__label {
      font-size: 10px;
      font-weight: 600;
      margin-top: 1px;
      opacity: 0.8;
    }

    &.q-tab--active {
      .q-tab__icon {
        transform: translateY(-2px);
      }
      .q-tab__label {
        opacity: 1;
      }
    }

    &.tab-seasons {
      .q-tab__icon {
        color: #f59e0b; // Amber
      }
      &.q-tab--active {
        background: rgba(245, 158, 11, 0.05);
        color: #b45309;
      }
    }

    &.tab-live {
      .q-tab__icon {
        color: #ef4444; // Red
      }
      &.q-tab--active {
        background: rgba(239, 68, 68, 0.05);
        color: #b91c1c;
      }
    }

    &.tab-leaderboard {
      .q-tab__icon {
        color: #3b82f6; // Blue
      }
      &.q-tab--active {
        background: rgba(59, 130, 246, 0.05);
        color: #1d4ed8;
      }
    }

    &.tab-stats {
      .q-tab__icon {
        color: #6366f1; // Indigo
      }
      &.q-tab--active {
        background: rgba(99, 102, 241, 0.05);
        color: #4338ca;
      }
    }
  }
}
</style>
