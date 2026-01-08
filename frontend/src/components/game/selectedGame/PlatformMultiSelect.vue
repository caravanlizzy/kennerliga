<template>
  <div class="col-12">
    <div class="row items-center q-gutter-xs">
      <q-chip
        v-for="p in platforms || []"
        :key="p.id"
        clickable
        dense
        :outline="!isPlatformSelected(p.id)"
        :color="getPlatformColor(p.name).color"
        :text-color="
          isPlatformSelected(p.id)?'white':getPlatformColor(p.name).color
        "
        :style="!isPlatformSelected(p.id) ? 'background-color: white' : ''"
        @click="togglePlatform(p.id)"
        class="platform-chip"
      >
        <q-icon name="sports_esports" size="14px" class="q-mr-xs" />
        {{ shortPlatformLabel(p.name) }}
      </q-chip>
    </div>
  </div>
</template>

<script setup lang="ts">

import { getPlatformColor } from 'src/composables/gameSelection';
import { inject } from 'vue';
import { TPlatform } from 'src/types';

const platforms = inject<TPlatform[]>('platforms', []);

defineProps<{
  isPlatformSelected: (id: number) => boolean;
  togglePlatform: (id: number) => void;
}>();

function shortPlatformLabel(name: string): string {
  const short = name.split('.')[0];
  return short.length > 14 ? short.slice(0, 13) + '…' : short;
}
</script>

<style scoped lang="scss">
.platform-chip {
  font-size: 11px;
  height: 24px;
  margin: 2px;
}
</style>
