<template>
  <q-page class="bg-white">
    <div class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle">
      <div class="text-h5 text-weight-bold text-dark">
        Live Action
      </div>
      <q-icon name="bolt" size="sm" color="accent" />
    </div>
    <div class="q-pa-md">
      <LiveActionFeed />
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'LiveActionMobilePage' });
import LiveActionFeed from 'components/ui/LiveActionFeed.vue';
import { useUiStore } from 'stores/uiStore';

</script>

<style scoped>
.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
</style>
