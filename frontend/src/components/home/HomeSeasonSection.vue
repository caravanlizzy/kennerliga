<template>
  <ContentSection
    id="seasons"
    icon="military_tech"
    title="Seasons"
    class="col-12"
    color="primary"
  >
    <template #title>
      <div class="row items-center no-wrap q-gutter-x-sm season-title-block">
        <span class="text-h5 text-weight-bold tracking-tight text-primary">Seasons</span>
        <div v-if="isLiveSeason" class="live-pill">
          <span class="live-dot" />
          Running
        </div>
      </div>
    </template>

    <template #header-extra>
      <div
        v-if="!loading"
        class="row items-center justify-end no-wrap q-gutter-x-sm q-ml-md col season-header-extra"
      >
        <div style="min-width: 110px">
          <KennerSelect
            :model-value="selectedSeasonYear"
            :options="seasonYearOptions"
            label="Year"
            emit-value
            map-options
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
            @update:model-value="$emit('update:selectedSeasonMonth', $event)"
          />
        </div>
        <KennerButton
          v-if="selectedSeasonId"
          outline
          color="primary"
          icon="visibility"
          :label="isMobile ? '' : 'Overview'"
          :round="isMobile"
          :to="{ name: 'season-overview', params: { id: selectedSeasonId } }"
          class="overview-btn q-ml-md"
        >
          <KennerTooltip v-if="isMobile">Season Overview</KennerTooltip>
        </KennerButton>
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

<style scoped lang="scss">
.season-title-block {
  min-height: 40px;
}

.season-header-extra {
  min-height: 40px;
  gap: 8px;

  :deep(.q-field) {
    align-self: center;
  }

  .overview-btn {
    align-self: center;
    height: 40px;
  }
}


.live-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: #047857;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6);
  animation: live-pulse 1.6s ease-out infinite;
}

@keyframes live-pulse {
  0%   { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.55); }
  70%  { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

:global(.body--dark) .live-pill {
  color: #6ee7b7;
  background: rgba(16, 185, 129, 0.18);
  border-color: rgba(16, 185, 129, 0.4);
}
</style>
