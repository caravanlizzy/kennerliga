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
       <div class="text-caption q-mb-lg">This season hasn't been set up with any leagues yet.</div>
       <KennerButton
         v-if="!isOverviewPage"
         outline
         color="primary"
         icon="visibility"
         label="Season Overview"
         :to="{ name: 'season-overview', params: { id: seasonId } }"
       />
    </div>

    <div v-else class="column q-gutter-y-md">
      <div v-if="seasonId && !isOverviewPage" class="row justify-end q-px-sm">
        <KennerButton
          outline
          color="primary"
          icon="visibility"
          label="Season Overview"
          :to="{ name: 'season-overview', params: { id: seasonId } }"
        />
      </div>

      <div class="column q-gutter-y-xl">
        <div v-for="league in leagues" :key="league.id" class="league-wrapper">
          <div class="row items-center q-mb-md q-px-sm">
            <div class="league-badge q-mr-md">
              {{ league.level }}
            </div>
            <div class="column">
              <div class="text-h6 text-weight-bold text-grey-9 line-height-1">
                League {{ league.level }}
              </div>
              <div class="text-caption text-grey-6 uppercase letter-spacing-1">
                {{ mode === 'results' ? 'Match Results' : 'Division Standings' }}
              </div>
            </div>
            <q-space />
            <KennerButton flat round icon="info" color="grey-4" size="sm">
              <KennerTooltip>
                {{ mode === 'results' ? 'Detailed match results' : 'Current standings' }} for League {{ league.level }}
              </KennerTooltip>
            </KennerButton>
          </div>
          <div class="results-container">
            <LeagueMatchResults v-if="mode === 'results'" :leagueId="league.id" />
            <LeagueStandingsMatrix v-else :leagueId="league.id" :prefetchedData="allStandingsData[league.id]" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import LeagueMatchResults from 'components/league/LeagueMatchResults.vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { api } from 'boot/axios';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useResponsive } from 'src/composables/responsive';

import { useLeagueStore } from 'stores/leagueStore';

const { isMobile } = useResponsive();
const route = useRoute();

interface League {
  id: number;
  name: string;
  level: number;
}

const props = withDefaults(defineProps<{
  seasonId?: number | null;
  mode?: 'standings' | 'results';
}>(), {
  mode: 'standings'
});

const leagues = ref<League[]>([]);
const allStandingsData = ref<Record<number, any>>({});
const loadingLeagues = ref(false);

const isOverviewPage = computed(() => route.name === 'season-overview');

async function loadLeaguesForSeason(seasonId: number) {
  loadingLeagues.value = true;
  try {
    const { data: leaguesData } = await api.get<League[]>('league/leagues', {
      params: { season: seasonId },
    });
    leagues.value = leaguesData;

    if (leaguesData.length > 0) {
      if (props.mode === 'standings') {
        // Fetch all full-standings in parallel
        const standingsPromises = leaguesData.map(l =>
          api.get(`league/leagues/${l.id}/full-standings/`).then(res => ({ id: l.id, data: res.data }))
        );
        const results = await Promise.all(standingsPromises);
        const standingsMap: Record<number, any> = {};
        results.forEach(r => {
          standingsMap[r.id] = r.data;
        });
        allStandingsData.value = standingsMap;
      } else {
        // In results mode, initialize all league stores in parallel
        const storePromises = leaguesData.map(l => {
          const store = useLeagueStore(l.id)();
          return store.init();
        });
        await Promise.all(storePromises);
      }
    }
  } catch (e) {
    console.error('Error loading season standings:', e);
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

.results-container {
  /* removed white background and border to let cards breathe */
}
</style>
