<template>
  <div
    class="row items-center q-mb-lg q-pa-lg bg-white rounded-borders"
  >
    <div class="col-grow">
      <div class="row items-center q-gutter-md">
        <div class="text-h4 text-weight-bolder text-primary">
          League Manager
        </div>
        <div class="row q-gutter-sm">
          <q-chip
            square
            color="grey-2"
            text-color="grey-9"
            class="text-weight-bold"
            icon="event"
          >
            {{ season?.name }}
          </q-chip>
          <q-chip
            square
            :color="season?.status === 'RUNNING' ? 'positive' : 'grey-7'"
            text-color="white"
            class="text-weight-bold"
          >
            {{ season?.status }}
          </q-chip>
          <q-chip
            square
            color="secondary"
            text-color="white"
            class="text-weight-bold"
            icon="military_tech"
          >
            Level {{ league?.level }}
          </q-chip>
        </div>
      </div>
    </div>
    <div class="col-auto">
      <KennerButton
        flat
        icon="refresh"
        round
        color="secondary"
        size="md"
        @click="$emit('refresh')"
      >
        <KennerTooltip>Refresh</KennerTooltip>
      </KennerButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TSeasonDto } from 'src/types';
import KennerButton from 'src/components/base/KennerButton.vue';
import KennerTooltip from 'src/components/base/KennerTooltip.vue';

defineProps<{
  league: any;
  season: TSeasonDto | null;
}>();

defineEmits(['refresh']);
</script>
