<template>
  <ContentSection
    id="seasons"
    icon="military_tech"
    title="Seasons"
    class="col-12 full-height"
    color="primary"
    no-margin
  >
    <template #title>
      <div class="row items-center no-wrap q-gutter-x-sm">
        <span class="text-h5 text-weight-bold text-primary">Seasons</span>
        <div
          v-if="isLiveSeason || isRunningSeason"
          class="season-live-badge row items-center no-wrap q-gutter-x-xs q-px-sm q-py-xs rounded-borders"
        >
          <span class="pulse-dot" />
          <span class="text-weight-bolder text-uppercase live-text">Running</span>
        </div>
      </div>
    </template>

    <template #header-extra>
      <div
        class="row items-center justify-end q-gutter-x-sm q-gutter-y-xs q-ml-sm col flex-wrap"
      >
        <div :style="{ minWidth: isMobile ? '80px' : '110px' }">
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
        <div :style="{ minWidth: isMobile ? '80px' : '110px' }">
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
          v-if="currentSeasonId && !isLiveSeason && !loading"
          outline
          color="positive"
          icon="today"
          :label="isMobile ? '' : 'Current'"
          :round="isMobile"
          :class="isMobile ? 'q-ml-xs' : 'q-ml-md'"
          aria-label="Jump to current season"
          @click="$emit('selectCurrentSeason')"
        >
          <KennerTooltip>Jump to current season</KennerTooltip>
        </KennerButton>
        <KennerButton
          v-if="selectedSeasonId && !loading"
          outline
          color="primary"
          icon="visibility"
          :label="isMobile ? '' : 'Overview'"
          :round="isMobile"
          :to="{ name: 'season-overview', params: { id: selectedSeasonId } }"
          :class="isMobile ? 'q-ml-xs' : 'q-ml-md'"
          aria-label="Season Overview"
        >
          <KennerTooltip v-if="isMobile">Season Overview</KennerTooltip>
        </KennerButton>
      </div>
    </template>

    <!-- Season Progress Bar (Current Season only) -->
    <div
      v-if="(isLiveSeason || isRunningSeason) && selectedSeasonProgress && selectedSeasonId && !loading"
      class="col-12 q-mb-sm"
    >
      <SeasonProgressBar
        :progress="selectedSeasonProgress"
        :status="selectedSeason?.status"
      />
    </div>

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
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import SeasonStandings from 'components/season/SeasonStandings.vue';
import SeasonProgressBar from 'components/season/SeasonProgressBar.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { useResponsive } from 'src/composables/responsive';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';

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
  (e: 'selectCurrentSeason'): void;
}>();

const { isMobile } = useResponsive();
const homeSeasonStore = useHomeSeasonStore();
const { selectedSeason, selectedSeasonProgress } = storeToRefs(homeSeasonStore);

const isRunningSeason = computed(
  () => selectedSeason.value?.status === 'RUNNING'
);

const isLiveSeason = computed(
  () =>
    props.currentSeasonId != null &&
    props.selectedSeasonId != null &&
    props.currentSeasonId === props.selectedSeasonId
);
</script>

<style scoped>
.season-live-badge {
  background: rgba(33, 186, 69, 0.12);
  color: var(--q-positive, #21ba45);
  font-size: 11px;
  letter-spacing: 0.5px;
  border: 1px solid rgba(33, 186, 69, 0.3);
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--q-positive, #21ba45);
  box-shadow: 0 0 0 0 rgba(33, 186, 69, 0.7);
  animation: pulse-ring 1.8s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
  display: inline-block;
}

@keyframes pulse-ring {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(33, 186, 69, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(33, 186, 69, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(33, 186, 69, 0);
  }
}
</style>
