<template>
  <q-toolbar
    class="navbar bg-grey-4 text-dark q-px-md q-py-none shadow-1 relative-position"
  >
    <!-- Left: Brand -->
    <NavHome />

    <q-space />

    <!-- Center: Main CTA -->
    <NavMyLeague v-if="user && user.myCurrentLeagueId" />

    <q-space />

    <!-- Right: Controls -->
    <NavProfileMenu :onToggle="onToggle" />
  </q-toolbar>
</template>

<script setup lang="ts">
import NavHome from 'components/nav/NavHome.vue';
import NavMyLeague from 'components/nav/NavMyLeague.vue';
import NavProfileMenu from 'components/nav/NavProfileMenu.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

defineProps<{ onToggle: () => void }>();
const { user } = storeToRefs(useUserStore());

</script>

<style lang="scss">
.navbar {
  position: relative;
  overflow: hidden;
}

.navbar::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 1200 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,50 C100,90 200,10 300,70 C400,130 500,0 600,50 C700,100 800,20 900,60 C1000,100 1100,30 1200,50' stroke='%23e53935' stroke-width='3' fill='none'/%3E%3C/svg%3E")
    center / cover no-repeat;
  opacity: 0.7;
  z-index: 0;
}

/* Compact version for mobile */
.nav-item-radius {
  padding: 2px 7px;
  border-radius: 13px;
}

.right-controls--mobile .q-btn {
  transform: scale(0.9);
}

.full-rounded {
  border-radius: 100%;
}
</style>
