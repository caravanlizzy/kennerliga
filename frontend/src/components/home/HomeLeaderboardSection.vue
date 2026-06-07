<template>
  <ContentSection
    id="leaderboard"
    icon="stars"
    title="Hall of Fame"
    class="col-12"
    color="secondary"
  >
    <template #header-extra>
      <div style="min-width: 120px" class="q-ml-md">
        <KennerSelect
          :model-value="year"
          :options="years"
          emit-value
          map-options
          @update:model-value="$emit('update:year', $event)"
        />
      </div>
    </template>
    <LeaderBoard :year="year" />
  </ContentSection>
</template>

<script setup lang="ts">
defineOptions({ name: 'HomeLeaderboardSection' });
import ContentSection from 'components/base/ContentSection.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import LeaderBoard from 'components/season/LeaderBoard.vue';

defineProps<{
  year: number;
  years: number[];
}>();

defineEmits<{
  (e: 'update:year', value: number): void;
}>();
</script>
