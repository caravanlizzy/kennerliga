<template>
  <div class="col-12 col-md-6">
    <div class="text-caption text-grey-7 q-mb-xs">Platform</div>
    <div class="row items-center q-gutter-xs">
      <q-chip
        v-for="p in platforms || []"
        :key="p.id"
        clickable
        :outline="!isPlatformSelected(p.id)"
        :color="getPlatformColor(p.name).color"
        :text-color="
          isPlatformSelected(p.id)?'white':getPlatformColor(p.name).color
        "
        :style="!isPlatformSelected(p.id) ? 'background-color: white' : ''"
        @click="togglePlatform(p.id)"
      >
        <q-icon name="sports_esports" size="16px" class="q-mr-xs" />
        {{ shortPlatformLabel(p.name) }}
      </q-chip>
    </div>
  </div>
</template>

<script setup lang="ts">

import { getPlatformColor } from 'src/composables/gameSelection';

defineProps<{
  platforms: any[];
  isPlatformSelected: (id: number) => boolean;
  togglePlatform: (id: number) => void;
}>();

function shortPlatformLabel(name: string): string {
  return name.length > 14 ? name.slice(0, 13) + '…' : name;
}
</script>
