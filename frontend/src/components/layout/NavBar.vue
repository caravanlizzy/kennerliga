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

      <!-- Center: Current Champion -->
      <div
        class="row no-wrap items-center absolute-center"
      >
        <CurrentChampion />
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
import CurrentChampion from 'components/season/CurrentChampion.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import { useResponsive } from 'src/composables/responsive';

defineProps<{ onToggle: () => void }>();
const { user } = storeToRefs(useUserStore());
const { isMobile } = useResponsive();
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


</style>
