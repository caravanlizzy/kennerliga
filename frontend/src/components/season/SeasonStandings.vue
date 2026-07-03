<template>
  <div :class="isMobile ? 'q-pa-sm' : 'q-pa-md'" class="column season-standings">
    <!-- State primary -->
    <LoadingSpinner v-if="loadingLeagues" text="Loading standings..." />

    <!-- Leagues + matrices -->
    <div v-else-if="!seasonId && !loadingLeagues" class="empty-state column items-center q-pa-xl">
      <div class="empty-state__icon-wrap q-mb-md">
        <q-icon name="info_outline" size="32px" />
      </div>
      <div class="text-h6 text-weight-bold">No season selected</div>
      <div class="text-caption text-grey-6">Please select year and month that contain a league.</div>
    </div>

    <div v-else-if="leagues.length === 0 && seasonId" class="empty-state column items-center q-pa-xl">
      <div class="empty-state__icon-wrap q-mb-md">
        <q-icon name="upcoming" size="32px" />
      </div>
      <div class="text-h6 text-weight-bold">No leagues found</div>
      <div class="text-caption text-grey-6 q-mb-lg">This season hasn't been set up with any leagues yet.</div>
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
      <div class="column q-gutter-y-lg">
        <div
          v-for="league in leagues"
          :key="league.id"
          class="league-card"
          :class="`league-card--l${league.level}`"
        >
          <div class="league-card__header row items-center">
            <div class="league-badge" :class="`league-badge--l${league.level}`">
              L{{ league.level }}
            </div>
            <div class="column q-ml-md">
              <div class="league-card__title">
                League {{ league.level }}
              </div>
              <div class="league-card__subtitle">
                {{ mode === 'results' ? 'Division Overview' : 'Division Standings' }}
              </div>
            </div>
            <q-space />
            <KennerButton flat round dense icon="info" :color="getLeagueColor(league.level)" size="sm">
              <KennerTooltip>
                {{ mode === 'results' ? 'Detailed match results' : 'Current standings' }} for League {{ league.level }}
              </KennerTooltip>
            </KennerButton>
          </div>
          <div class="league-card__body">
            <LeagueMatchResults
              v-if="mode === 'results'"
              :leagueId="league.id"
              :show-standings="isOverviewPage"
            />
            <LeagueStandings v-else-if="mode === 'standings-simple'" :leagueId="league.id" />
            <LeagueStandingsMatrix v-else :leagueId="league.id" :prefetchedData="allStandingsData[league.id]" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import LeagueMatchResults from 'components/league/LeagueMatchResults.vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { api } from 'boot/axios';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useResponsive } from 'src/composables/responsive';
import { leagueColors } from 'src/composables/leagueColors';
import { useCachedResource } from 'src/composables/cachedResource';

import { useLeagueStore } from 'stores/leagueStore';

const { isMobile } = useResponsive();
const { getLeagueColor } = leagueColors();
const route = useRoute();

interface League {
  id: number;
  name: string;
  level: number;
}

interface SeasonPayload {
  leagues: League[];
  standingsMap: Record<number, any>;
}

const props = withDefaults(defineProps<{
  seasonId?: number | null;
  mode?: 'standings' | 'results' | 'standings-simple';
}>(), {
  mode: 'standings'
});

const isOverviewPage = computed(() => route.name === 'season-overview');

// Stale-while-revalidate loader: cached data for the current season stays on
// screen while a fresh request is in flight, so the UI never flashes the
// blocking spinner on subsequent visits.
const {
  data: payload,
  loading: loadingLeagues,
  refreshing: refreshingLeagues,
  load: loadLeaguesForSeason,
  reset: resetLeagues,
} = useCachedResource<number, SeasonPayload>(async (seasonId) => {
  if (props.mode === 'standings') {
    // Batched: single request returns all leagues + their full standings.
    const { data } = await api.get(`season/seasons/${seasonId}/full-standings/`);
    const leaguesPayload: any[] = data?.leagues ?? [];
    const leaguesOut: League[] = leaguesPayload.map(l => ({
      id: l.id,
      name: l.name,
      level: l.level,
    }));
    const standingsMap: Record<number, any> = {};
    leaguesPayload.forEach(l => {
      standingsMap[l.id] = l;
    });
    return { leagues: leaguesOut, standingsMap };
  }

  const { data: leaguesData } = await api.get<League[]>('league/leagues', {
    params: { season: seasonId },
  });

  if (leaguesData.length > 0 && props.mode === 'results') {
    // In results mode, initialize all league stores in parallel
    const storePromises = leaguesData.map(l => {
      const store = useLeagueStore(l.id)();
      return store.init();
    });
    await Promise.all(storePromises);
  }
  return { leagues: leaguesData, standingsMap: {} };
});

const leagues = computed<League[]>(() => payload.value?.leagues ?? []);
const allStandingsData = computed<Record<number, any>>(
  () => payload.value?.standingsMap ?? {}
);

watch(() => props.seasonId, (id) => {
  if (!id) {
    resetLeagues();
    return;
  }
  loadLeaguesForSeason(id);
}, { immediate: true });
</script>

<style scoped lang="scss">
.season-standings {
  max-width: 1200px;
  margin: 0 auto;
}

/* ---------- Empty states ---------- */
.empty-state {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(54, 64, 88, 0.04);
  color: #5b6478;
  text-align: center;
}

.empty-state__icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background: linear-gradient(135deg, var(--q-primary), var(--q-accent));
}

:global(.body--dark) .empty-state {
  background: rgba(30, 30, 30, 0.72);
  border-color: rgba(255, 255, 255, 0.08);
  color: #c8cdd6;
}

/* ---------- League card ---------- */
.league-card {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(54, 64, 88, 0.05);
  overflow: hidden;
  transition: box-shadow 0.25s ease, transform 0.25s ease;
}

.league-card:hover {
  box-shadow: 0 8px 24px rgba(54, 64, 88, 0.08);
}

.league-card__header {
  padding: 14px 18px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(236, 72, 153, 0.04));
  border-bottom: 1px solid rgba(54, 64, 88, 0.06);
}

.league-card__title {
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.1;
  color: #1f2533;
  letter-spacing: -0.01em;
}

.league-card__subtitle {
  margin-top: 2px;
  font-size: 0.72rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #8a94a6;
  font-weight: 600;
}

.league-card__body {
  padding: 4px 6px 8px;
}

:global(.body--dark) .league-card {
  background: rgba(30, 30, 30, 0.72);
  border-color: rgba(255, 255, 255, 0.08);
}

:global(.body--dark) .league-card__header {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(236, 72, 153, 0.08));
  border-bottom-color: rgba(255, 255, 255, 0.06);
}

:global(.body--dark) .league-card__title { color: #eef0f4; }
:global(.body--dark) .league-card__subtitle { color: #9aa3b2; }

/* ---------- League badge (medal tones) ---------- */
.league-badge {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.05rem;
  letter-spacing: -0.02em;
  color: white;
  background: linear-gradient(135deg, #94a3b8, #64748b);
  flex-shrink: 0;
}

.league-badge--l1 {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}
.league-badge--l2 {
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
}
.league-badge--l3 {
  background: linear-gradient(135deg, #fdba74, #c2825a);
}
</style>
