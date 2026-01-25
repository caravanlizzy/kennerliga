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
