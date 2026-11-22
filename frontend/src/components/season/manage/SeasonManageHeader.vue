<template>
  <div
    v-if="route.name !== 'league-manager'"
    class="row items-center justify-between q-mb-md"
  >
    <div class="text-h5 text-weight-bold text-dark tracking-tight">
      {{ season?.name || '…' }}
    </div>
    <div class="row items-center q-gutter-x-sm">
      <KennerButton
        outline
        no-caps
        icon="visibility"
        round
        color="secondary"
        size="sm"
        aria-label="View Public Overview"
        :to="{ name: 'season-overview', params: { id: seasonId } }"
      >
        <KennerTooltip>View Public Overview</KennerTooltip>
      </KennerButton>

      <KennerButton
        v-if="isAdmin && season?.status === 'NEXT'"
        outline
        no-caps
        icon="campaign"
        round
        color="positive"
        size="sm"
        aria-label="Open Season for Registration"
        :loading="opening"
        @click="$emit('open-season')"
      >
        <KennerTooltip>Open Season for Registration</KennerTooltip>
      </KennerButton>

      <KennerButton
        v-if="isAdmin && season?.status === 'OPEN'"
        outline
        no-caps
        icon="groups"
        round
        color="secondary"
        size="sm"
        aria-label="Fill Leagues from current participants"
        :loading="filling"
        :disable="seasonHasResults"
        @click="$emit('fill-leagues')"
      >
        <KennerTooltip>
          {{
            seasonHasResults
              ? 'Cannot refill leagues: match results already exist in this season'
              : 'Fill Leagues from current participants'
          }}
        </KennerTooltip>
      </KennerButton>

      <KennerButton
        v-if="isAdmin && season?.status === 'OPEN'"
        outline
        no-caps
        icon="play_arrow"
        round
        color="positive"
        size="sm"
        aria-label="Start Season Manually"
        :loading="starting"
        @click="$emit('start-season')"
      >
        <KennerTooltip>Start Season Manually</KennerTooltip>
      </KennerButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import type { TSeasonDto } from 'src/types';

defineProps<{
  season: TSeasonDto | null;
  seasonId: number;
  isAdmin: boolean;
  seasonHasResults: boolean;
  opening: boolean;
  filling: boolean;
  starting: boolean;
}>();

defineEmits<{
  (e: 'open-season'): void;
  (e: 'fill-leagues'): void;
  (e: 'start-season'): void;
}>();

const route = useRoute();
</script>
