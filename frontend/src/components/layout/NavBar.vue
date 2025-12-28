<template>
  <q-toolbar
    class="navbar bg-white text-dark q-px-md q-py-sm relative-position"
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
  min-height: 64px;
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
