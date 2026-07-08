<template>
  <ContentSection
    id="seasons"
    icon="military_tech"
    title="Seasons"
    class="col-12"
    color="primary"
  >
    <template #title>
      <div class="row items-center no-wrap q-gutter-x-sm">
        <span class="text-h5 text-weight-bold text-primary">Seasons</span>
        <q-badge
          v-if="isLiveSeason"
          rounded
          color="positive"
          class="q-px-sm q-py-xs text-weight-bolder text-uppercase"
        >
          Running
        </q-badge>
      </div>
    </template>

    <template #header-extra>
      <div
        class="row items-center justify-end no-wrap q-gutter-x-sm q-ml-md col"
      >
        <div style="min-width: 110px">
          <KennerSelect
            :model-value="selectedSeasonYear"
            :options="seasonYearOptions"
            label="Year"
            emit-value
            map-options
            :disable="loading"
            @update:model-value="$emit('update:selectedSeasonYear', $event)"
          />
        </div>
        <div style="min-width: 110px">
          <KennerSelect
            :model-value="selectedSeasonMonth"
            :options="seasonMonthOptions"
            label="Month"
            emit-value
            map-options
            :disable="loading"
            @update:model-value="$emit('update:selectedSeasonMonth', $event)"
          />
        </div>
        <KennerButton
          v-if="selectedSeasonId && !loading"
          outline
          color="primary"
          icon="visibility"
          :label="isMobile ? '' : 'Overview'"
          :round="isMobile"
          :to="{ name: 'season-overview', params: { id: selectedSeasonId } }"
          class="q-ml-md"
        >
          <KennerTooltip v-if="isMobile">Season Overview</KennerTooltip>
        </KennerButton>
      </div>
    </template>
    <!--
      Stale-while-revalidate: as soon as we have a `selectedSeasonId`, keep
      rendering SeasonStandings — even if the store is currently `refreshing`
      in the background — so cached data stays visible during navigation.
      Only when we truly have nothing to show yet (first load, no cache) do we
      fall back to the loading spinner.
    -->
    <SeasonStandings
      v-if="selectedSeasonId"
      :seasonId="selectedSeasonId"
      class="col-12"
    />
    <div v-else-if="loading" class="flex flex-center q-pa-xl">
      <LoadingSpinner text="Loading seasons..." />
    </div>
  </ContentSection>
</template>

<script setup lang="ts">
defineOptions({ name: 'HomeSeasonSection' });
import { computed } from 'vue';
import ContentSection from 'components/base/ContentSection.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { useResponsive } from 'src/composables/responsive';

type SelectOption = { label: string | number; value: number };

const props = defineProps<{
  selectedSeasonYear: number | null;
  selectedSeasonMonth: number | null;
  selectedSeasonId: number | null;
  currentSeasonId?: number | null;
  seasonYearOptions: SelectOption[];
  seasonMonthOptions: SelectOption[];
  loading: boolean;
  // Non-blocking background refresh indicator. The section keeps rendering
  // cached data while this is true; consumers may optionally surface a subtle
  // hint in the header if they wish.
  refreshing?: boolean;
}>();

defineEmits<{
  (e: 'update:selectedSeasonYear', value: number | null): void;
  (e: 'update:selectedSeasonMonth', value: number | null): void;
}>();

const { isMobile } = useResponsive();

const isLiveSeason = computed(
  () =>
    props.currentSeasonId != null &&
    props.selectedSeasonId != null &&
    props.currentSeasonId === props.selectedSeasonId
);
</script>
