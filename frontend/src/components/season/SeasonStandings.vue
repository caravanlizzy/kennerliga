<template>
  <div :class="isMobile ? 'q-pa-sm' : 'q-pa-md'" class="column season-standings">
    <!-- State primary -->
    <LoadingSpinner v-if="loadingLeagues" />

    <!-- Leagues + matrices -->
    <div v-else-if="!seasonId && !loadingLeagues" class="column items-center q-pa-xl text-grey-6">
      <q-icon name="info_outline" size="48px" class="q-mb-md" />
      <div class="text-h6">No season selected</div>
      <div>Please select year and month that contain a league.</div>
    </div>

    <div v-else-if="leagues.length === 0 && seasonId" class="column items-center q-pa-xl text-grey-6 bg-white rounded-borders border-subtle">
       <q-icon name="upcoming" size="48px" class="q-mb-md opacity-20" />
       <div class="text-h6 text-weight-bold">No leagues found</div>
       <div class="text-caption">This season hasn't been set up with any leagues yet.</div>
    </div>

    <div v-else class="column q-gutter-y-xl">
      <div v-for="league in leagues" :key="league.id" class="league-wrapper">
        <div class="row items-center q-mb-md q-px-sm">
          <div class="league-badge q-mr-md">
            {{ league.level }}
          </div>
          <div class="column">
            <div class="text-h6 text-weight-bold text-grey-9 line-height-1">
              League {{ league.level }}
            </div>
            <div class="text-caption text-grey-6 uppercase letter-spacing-1">Division Standings</div>
          </div>
          <q-space />
          <KennerButton flat round icon="info" color="grey-4" size="sm">
            <KennerTooltip>Current standings for League {{ league.level }}</KennerTooltip>
          </KennerButton>
        </div>
        <div class="matrix-container rounded-borders overflow-hidden">
          <LeagueStandingsMatrix :leagueId="league.id" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { api } from 'boot/axios';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useResponsive } from 'src/composables/responsive';

const { isMobile } = useResponsive();

interface League {
  id: number;
  name: string;
  level: number;
}

const props = defineProps<{
  seasonId?: number | null;
}>();

const leagues = ref<League[]>([]);
const loadingLeagues = ref(false);

async function loadLeaguesForSeason(seasonId: number) {
  loadingLeagues.value = true;
  try {
    const { data } = await api.get<League[]>('league/leagues', {
      params: { season: seasonId },
    });
    leagues.value = data;
  } finally {
    loadingLeagues.value = false;
  }
}

watch(() => props.seasonId, (id) => {
  if (!id) {
    leagues.value = [];
    return;
  }
  loadLeaguesForSeason(id);
}, { immediate: true });

</script>

<style scoped lang="scss">
.border-subtle {
  border: 1px solid rgba(54, 64, 88, 0.08);
}

.opacity-20 {
  opacity: 0.2;
}

.season-standings {
  max-width: 1200px;
  margin: 0 auto;
}

.league-badge {
  background: var(--q-primary);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
  box-shadow: 0 2px 4px rgba(var(--q-primary), 0.3);
}

.line-height-1 {
  line-height: 1;
}

.letter-spacing-1 {
  letter-spacing: 1px;
}

.uppercase {
  text-transform: uppercase;
}

.matrix-container {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>
