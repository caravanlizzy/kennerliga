<template>
  <div class="column full-width glass-effect">
    <q-toolbar
      class="navbar text-dark q-py-sm relative-position"
      :class="isMobile ? 'q-px-sm' : 'q-px-md'"
      style="border-bottom: none;"
    >
      <!-- Left: Brand -->
      <div class="row no-wrap items-center">
        <NavHome />
      </div>

      <q-space />

      <!-- Center: Section Navigation Icons -->
      <div
        v-if="!isMobile && navSections.length"
        class="row no-wrap items-center absolute-center"
      >
        <q-btn
          v-for="section in navSections"
          :key="section.id"
          flat
          dense
          :icon="section.icon"
          :color="unref(section.isActive) ? (section.color || 'primary') : 'grey-7'"
          :size="isMobile ? 'sm' : 'md'"
          @click="handleSectionClick(section)"
          class="nav-section-btn squircle-shape"
          :class="[
            { 'is-active': unref(section.isActive) },
            section.color ? `nav-section-btn--${section.color}` : ''
          ]"
        >
          <q-tooltip>Scroll to {{ section.title }}</q-tooltip>
        </q-btn>
      </div>

      <q-space />

      <!-- Right: Controls -->
      <div class="row no-wrap items-center" :class="isMobile ? 'q-gutter-x-xs' : 'q-gutter-x-sm'">

        <NavMyLeague v-if="user && user.myCurrentLeagueId" />

        <NavProfileMenu :onToggle="onToggle" class="q-ml-xs" />
      </div>
    </q-toolbar>

    <!-- Center: Mobile Tabs (Second Row) -->
    <div v-if="isMobile" class="row justify-center q-pb-sm q-px-sm">
      <div class="row no-wrap items-center full-width justify-center" style="height: 40px; border-bottom: 1px solid rgba(0, 0, 0, 0.05);">
        <q-tabs
          :model-value="activeTab"
          class="text-dark compact-tabs full-width"
          active-color="primary"
          indicator-color="primary"
          align="justify"
          dense
          no-caps
          @update:model-value="handleTabChange"
        >
          <q-tab icon="home" name="welcome" class="tab-welcome" label="Home" />
          <q-tab icon="military_tech" name="seasons" class="tab-seasons" label="Seasons" />
          <q-tab icon="bolt" name="live" class="tab-live" label="Live" />
          <q-tab icon="chat" name="chat" class="tab-chat" label="Chat" />
          <q-tab icon="stars" name="leaderboard" class="tab-leaderboard" label="Stats" />
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
import { computed, unref } from 'vue';
import { useResponsive } from 'src/composables/responsive';
import { scroll } from 'quasar';
import { useRouter } from 'vue-router';

const { getScrollTarget, setVerticalScrollPosition } = scroll;

defineProps<{ onToggle: () => void }>();
const { user } = storeToRefs(useUserStore());
const uiStore = useUiStore();
const { navSections } = storeToRefs(uiStore);
const route = useRoute();
const router = useRouter();
const { isMobile } = useResponsive();

const isIndexPage = computed(() => route.name === 'home');

const activeTab = computed(() => {
  const name = route.name as string;
  if (name === 'home') return 'welcome';
  if (name === 'mobile-seasons') return 'seasons';
  if (name === 'mobile-live') return 'live';
  if (name === 'mobile-chat') return 'chat';
  if (name === 'mobile-leaderboard') return 'leaderboard';
  return null;
});

function handleTabChange(value: string) {
  if (isMobile.value) {
    switch (value) {
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
      case 'welcome':
        router.push({ name: 'home' });
        break;
    }
  } else if (!isIndexPage.value) {
    router.push({ name: 'home' });
  }
}

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
  display: flex;
  align-items: center;
}

.compact-tabs {
  .q-tab {
    min-height: 40px !important;
    padding: 0 4px !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  }
  .q-tab__content {
    padding: 4px 0 !important;
    min-width: 44px !important;
    position: relative;
  }
  .q-tab__label {
    font-size: 10px;
    font-weight: 700;
  }
  .q-icon {
    font-size: 20px !important;
  }
  .tab-welcome .q-icon, .tab-welcome .q-tab__label { color: #616161; }
  .tab-live .q-icon, .tab-live .q-tab__label { color: #616161; }
  .tab-seasons .q-icon, .tab-seasons .q-tab__label { color: #616161; }
  .tab-chat .q-icon, .tab-chat .q-tab__label { color: #616161; } // grey-7
  .tab-leaderboard .q-icon, .tab-leaderboard .q-tab__label { color: #616161; }

  @each $name, $color in (
    "welcome": #1976D2,
    "seasons": #1976D2,
    "live": #9C27B0,
    "chat": #26A69A,
    "leaderboard": #F2C037
  ) {
    .tab-#{$name} {
      &:hover {
        background: rgba($color, 0.05);
        .q-icon, .q-tab__label {
          color: $color !important;
        }
      }
      &.q-tab--active {
        color: $color !important;
        background: rgba($color, 0.08);
      }
    }
  }

  .q-tab--active {
    .q-tab__indicator {
      height: 3px;
      border-radius: 3px 3px 0 0;
      background: currentColor !important;
    }
  }
}

.glass-effect {
  background: rgba(255, 255, 255, 0.82) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 2px solid #eeeeee;
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
  height: 40px;
  min-width: 40px;

  &.squircle-shape {
    border-radius: 12px !important;
  }

  &:hover {
    opacity: 1;
    background: rgba(0, 0, 0, 0.05);
  }

  &.is-active {
    opacity: 1;
    background: rgba(0, 0, 0, 0.03);
    // color: var(--q-primary) !important; // Handled by dynamic :color prop
  }

  @each $name, $color in (
    "primary": #1976D2,
    "secondary": #26A69A,
    "accent": #9C27B0,
    "warning": #F2C037,
    "negative": #C10015,
    "info": #31CCEC
  ) {
    &.nav-section-btn--#{$name} {
      &:hover {
        background: rgba($color, 0.08) !important;
        color: $color !important;
      }
      &.is-active {
        background: rgba($color, 0.1) !important;
      }
    }
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
