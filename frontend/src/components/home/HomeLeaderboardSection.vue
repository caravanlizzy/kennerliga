<template>
  <ContentSection
    id="leaderboard"
    icon="stars"
    title="Hall of Fame"
    class="col-12"
    color="secondary"
  >
    <template #header-extra>
      <div class="row items-center justify-end no-wrap q-gutter-x-sm q-ml-md col">
        <SmoothSwitch
          v-model="showAllLeagues"
          :options="[
            { label: 'Highest', value: false },
            { label: 'All', value: true }
          ]"
        />
        <div style="min-width: 120px">
          <KennerSelect
            :model-value="year"
            :options="years"
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
import { ref } from 'vue';
import ContentSection from 'components/base/ContentSection.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import SmoothSwitch from 'components/base/SmoothSwitch.vue';
import LeaderBoard from 'components/season/LeaderBoard.vue';

defineProps<{
  year: number;
  years: number[];
}>();

const showAllLeagues = ref(false);

defineEmits<{
  (e: 'update:year', value: number): void;
}>();
</script>
