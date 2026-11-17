<template>
  <ContentSection
    id="leaderboard"
    icon="stars"
    title="Hall of Fame"
    class="col-12"
    color="secondary"
  >
    <template #header-extra>
      <div
        class="row items-center justify-end no-wrap q-gutter-x-sm q-ml-md col"
      >
        <SmoothSwitch
          v-model="showAllLeagues"
          :options="[
            { label: 'Highest', value: false },
            { label: 'All', value: true },
          ]"
        />
        <div style="min-width: 120px">
          <KennerSelect
            :model-value="year"
            :options="yearOptions"
            emit-value
            map-options
            @update:model-value="$emit('update:year', $event)"
          />
        </div>
      </div>
    </template>
    <LeaderBoard v-model:show-all-leagues="showAllLeagues" :year="year" />
  </ContentSection>
</template>

<script setup lang="ts">
defineOptions({ name: 'HomeLeaderboardSection' });
import { computed, ref } from 'vue';
import ContentSection from 'components/base/ContentSection.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import SmoothSwitch from 'components/base/SmoothSwitch.vue';
import LeaderBoard from 'components/season/LeaderBoard.vue';

const props = defineProps<{
  year: number | 'all';
  years: number[];
}>();

const showAllLeagues = ref(false);

const yearOptions = computed(() => [
  { label: 'All-time', value: 'all' as const },
  ...[...props.years]
    .sort((a, b) => b - a)
    .map((y) => ({ label: String(y), value: y })),
]);

defineEmits<{
  (e: 'update:year', value: number | 'all'): void;
}>();
</script>
