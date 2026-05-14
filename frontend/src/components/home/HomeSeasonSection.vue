<template>
  <ContentSection
    id="seasons"
    icon="military_tech"
    title="Seasons"
    class="col-12"
    color="primary"
  >
    <template #header-extra>
      <div
        v-if="!loading"
        class="row no-wrap q-gutter-x-sm q-ml-md"
      >
        <div style="width: 110px">
          <KennerSelect
            :model-value="selectedSeasonYear"
            :options="seasonYearOptions"
            label="Year"
            emit-value
            map-options
            @update:model-value="$emit('update:selectedSeasonYear', $event)"
          />
        </div>
        <div style="width: 110px">
          <KennerSelect
            :model-value="selectedSeasonMonth"
            :options="seasonMonthOptions"
            label="Month"
            emit-value
            map-options
            @update:model-value="$emit('update:selectedSeasonMonth', $event)"
          />
        </div>
      </div>
    </template>
    <SeasonStandings
      v-if="!loading"
      :seasonId="selectedSeasonId"
      class="col-12"
    />
    <div v-else class="flex flex-center q-pa-xl">
      <LoadingSpinner text="Loading seasons..." />
    </div>
  </ContentSection>
</template>

<script setup lang="ts">
defineOptions({ name: 'HomeSeasonSection' });
import ContentSection from 'components/base/ContentSection.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

type SelectOption = { label: string | number; value: number };

defineProps<{
  selectedSeasonYear: number | null;
  selectedSeasonMonth: number | null;
  selectedSeasonId: number | null;
  seasonYearOptions: SelectOption[];
  seasonMonthOptions: SelectOption[];
  loading: boolean;
}>();

defineEmits<{
  (e: 'update:selectedSeasonYear', value: number | null): void;
  (e: 'update:selectedSeasonMonth', value: number | null): void;
}>();
</script>
