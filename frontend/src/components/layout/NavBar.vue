<template>
  <q-toolbar
    class="navbar text-dark q-px-md q-py-sm relative-position glass-effect shadow-1"
  >
    <!-- Left: Brand -->
    <NavHome />

    <q-space />

    <!-- Right: Controls -->
    <div class="row no-wrap items-center q-gutter-x-md">
      <!-- Minimized Items -->
      <div
        v-if="minimizedItems.length && isIndexPage"
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

defineProps<{ onToggle: () => void }>();
const { user } = storeToRefs(useUserStore());
const { minimizedItems } = storeToRefs(useUiStore());
const { restore } = useUiStore();
const route = useRoute();

const isIndexPage = computed(() => route.name === 'home');

</script>

<style lang="scss">
.navbar {
  position: relative;
  min-height: 64px;
}

.glass-effect {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
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
