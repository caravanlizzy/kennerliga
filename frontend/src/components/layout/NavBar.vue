<template>
  <div class="column full-width glass-effect shadow-1">
    <q-toolbar
      class="navbar text-dark q-py-sm relative-position"
      :class="isMobile ? 'q-px-sm' : 'q-px-md'"
      style="border-bottom: none;"
    >
      <!-- Left: Brand -->
      <NavHome />

      <q-space />

      <!-- Right: Controls -->
      <div class="row no-wrap items-center" :class="isMobile ? 'q-gutter-x-xs' : 'q-gutter-x-sm'">

        <!-- Section Navigation Icons -->
        <div
          v-if="!isMobile && (navSections.length || minimizedItems.length)"
          class="row no-wrap items-center q-gutter-x-xs"
        >
          <q-btn
            v-for="section in navSections"
            :key="section.id"
            flat
            round
            dense
            :icon="section.icon"
            :color="section.color"
            :size="isMobile ? 'sm' : 'md'"
            @click="handleSectionClick(section)"
            class="nav-section-btn"
            :class="{ 'is-active': unref(section.isActive) }"
          >
            <q-tooltip>Scroll to {{ section.title }}</q-tooltip>
          </q-btn>

          <q-separator v-if="navSections.length && minimizedItems.length" vertical inset class="q-mx-xs opacity-10" />

          <q-btn
            v-for="item in minimizedItems"
            :key="item.id"
            flat
            round
            dense
            :icon="item.icon"
            :color="item.color"
            size="sm"
            @click="restore(item.id)"
            class="nav-section-btn minimized-btn"
          >
            <q-tooltip>Restore {{ item.title }}</q-tooltip>
          </q-btn>

          <q-separator vertical inset class="q-mx-sm opacity-10" />
        </div>

        <!-- Main CTA -->
        <NavMyLeague v-if="user && user.myCurrentLeagueId" />

        <NavProfileMenu :onToggle="onToggle" />
      </div>
    </q-toolbar>

    <!-- Center: Mobile Tabs (Second Row) -->
    <div v-if="isMobile && isIndexPage" class="row justify-center q-pb-sm q-px-sm">
      <div class="row no-wrap items-center bg-blue-grey-1 rounded-borders q-pa-none full-width justify-center" style="height: 40px; border: 1px solid rgba(54, 64, 88, 0.08); box-shadow: inset 0 1px 2px rgba(0,0,0,0.03)">
        <q-tabs
          v-model="activeTab"
          class="text-dark compact-tabs full-width"
          active-color="primary"
          indicator-color="transparent"
          align="justify"
          dense
          no-caps
        >
          <q-tab icon="military_tech" name="seasons" class="tab-seasons" />
          <q-tab icon="bolt" name="live" class="tab-live" />
          <q-tab icon="leaderboard" name="leaderboard" class="tab-leaderboard" />
        </q-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import NavHome from 'components/nav/NavHome.vue';
import NavMyLeague from 'components/nav/NavMyLeague.vue';
import NavProfileMenu from 'components/nav/NavProfileMenu.vue';
import { useUserStore } from 'stores/userStore';
import { useUiStore, type NavSection } from 'src/stores/uiStore';
import { storeToRefs } from 'pinia';
import { useRoute } from 'vue-router';
import { ref, computed, onMounted, onUnmounted, watch, unref } from 'vue';
import { useResponsive } from 'src/composables/responsive';
import { scroll } from 'quasar';

const { getScrollTarget, setVerticalScrollPosition } = scroll;

defineProps<{ onToggle: () => void }>();
const { user } = storeToRefs(useUserStore());
const { navSections, minimizedItems, activeTab } = storeToRefs(useUiStore());
const { restore } = useUiStore();
const route = useRoute();
const { isMobile } = useResponsive();

const isIndexPage = computed(() => route.name === 'home');

function handleSectionClick(section: NavSection) {
  if (section.onClick) {
    section.onClick();
  } else {
    scrollToSection(section.id);
  }
}

function scrollToSection(id: string) {
  const el = document.getElementById(id);
  if (el) {
    const target = getScrollTarget(el);
    const offset = el.offsetTop - 80; // Adjust for sticky navbar
    setVerticalScrollPosition(target, offset, 300);
  }
}
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

.nav-section-btn {
  opacity: 0.7;
  transition: all 0.3s ease;

  &:hover {
    opacity: 1;
    transform: translateY(-2px);
    background: rgba(0, 0, 0, 0.05);
  }

  &.is-active {
    opacity: 1;
    transform: translateY(-2px);
    background: rgba(0, 0, 0, 0.05);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

  &.minimized-btn {
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}
</style>
