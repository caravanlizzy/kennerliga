<template>
  <q-toolbar
    class="navbar text-dark q-py-sm relative-position glass-effect shadow-1"
    :class="isMobile ? 'q-px-sm' : 'q-px-md'"
  >
    <!-- Left: Brand -->
    <NavHome />

    <q-space />

    <!-- Center: Mobile Tabs -->
    <div v-if="isMobile && isIndexPage" class="row no-wrap items-center bg-blue-grey-1 rounded-borders q-pa-none q-mr-sm" style="height: 40px; border: 1px solid rgba(54, 64, 88, 0.08); box-shadow: inset 0 1px 2px rgba(0,0,0,0.03)">
      <q-tabs
        v-model="activeTab"
        class="text-dark compact-tabs"
        active-color="primary"
        indicator-color="transparent"
        align="center"
        dense
        no-caps
      >
        <q-tab icon="auto_awesome" name="welcome" class="tab-welcome" />
        <q-tab icon="history" name="seasons" class="tab-seasons" />
        <q-tab icon="sensors" name="live" class="tab-live" />
        <q-tab icon="chat" name="chat" class="tab-chat" />
        <q-tab icon="leaderboard" name="leaderboard" class="tab-leaderboard" />
      </q-tabs>
    </div>

    <!-- Right: Controls -->
    <div class="row no-wrap items-center" :class="isMobile ? 'q-gutter-x-xs' : 'q-gutter-x-sm'">

      <!-- Minimized Items (Mobile - show only those NOT in tabs if any, but usually they are the same) -->
      <!-- Actually, the request says minimize functionality does not make sense on mobile since it duplicates nav elements -->
      <!-- So we just don't show minimizedItems on mobile at all in the navbar -->

      <!-- Minimized Items (Desktop) -->
      <div
        v-if="!isMobile && minimizedItems.length"
        class="row no-wrap items-center q-gutter-x-sm"
      >
        <q-btn
          v-for="item in minimizedItems"
          :key="item.id"
          flat
          round
          dense
          :icon="item.icon"
          :color="item.color"
          @click="restore(item.id)"
        >
          <q-tooltip>Restore {{ item.title }}</q-tooltip>
        </q-btn>
        <q-separator vertical inset class="q-mx-sm" />
      </div>

      <!-- Main CTA -->
      <NavMyLeague v-if="user && user.myCurrentLeagueId" />

      <NavProfileMenu :onToggle="onToggle" />
    </div>
  </q-toolbar>
</template>

<script setup lang="ts">
import NavHome from 'components/nav/NavHome.vue';
import NavMyLeague from 'components/nav/NavMyLeague.vue';
import NavProfileMenu from 'components/nav/NavProfileMenu.vue';
import { useUserStore } from 'stores/userStore';
import { useUiStore } from 'src/stores/uiStore';
import { storeToRefs } from 'pinia';
import { useRoute } from 'vue-router';
import { computed } from 'vue';
import { useResponsive } from 'src/composables/responsive';

defineProps<{ onToggle: () => void }>();
const { user } = storeToRefs(useUserStore());
const { minimizedItems, activeTab } = storeToRefs(useUiStore());
const { restore } = useUiStore();
const route = useRoute();
const { isMobile } = useResponsive();

const isIndexPage = computed(() => route.name === 'home');

</script>

<style lang="scss">
.navbar {
  position: relative;
  min-height: 64px;
}

.compact-tabs {
  .q-tab {
    min-height: 40px !important;
    padding: 0 !important;
    border-radius: 4px !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  }
  .q-tab__content {
    padding: 0 !important;
    min-width: 44px !important;
    position: relative;
  }
  .tab-welcome .q-icon { color: var(--q-primary); }
  .tab-live .q-icon { color: var(--q-accent); }
  .tab-seasons .q-icon { color: var(--q-primary); }
  .tab-chat .q-icon { color: var(--q-primary); }
  .tab-leaderboard .q-icon { color: var(--q-primary); }

  .q-tab--active {
    background: white !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;

    &::after {
      content: '';
      position: absolute;
      bottom: 3px;
      left: 50%;
      transform: translateX(-50%);
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: currentColor;
    }
  }
}

.glass-effect {
  background: rgba(255, 255, 255, 0.82) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(54, 64, 88, 0.1);
}

/* Compact version for mobile */
.nav-item-radius {
  padding: 4px 12px;
  border-radius: 12px;
}

.border-subtle {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.right-controls--mobile .q-btn {
  transform: scale(0.9);
}

.full-rounded {
  border-radius: 100%;
}
</style>
