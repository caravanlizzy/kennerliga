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
          <div class="q-pa-xs">
            <LeagueMatchResults
              v-if="mode === 'results'"
              :leagueId="league.id"
              :show-standings="isOverviewPage"
            />
            <LeagueStandings v-else-if="mode === 'standings-simple'" :leagueId="league.id" />
            <LeagueStandingsMatrix v-else :leagueId="league.id" :prefetchedData="allStandingsData[league.id]" :level="league.level" />
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
import LeagueLevel from 'components/season/LeagueLevel.vue';

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
  // Note: `cacheKey` below persists the SWR state across component
  // unmount/remount so navigating back to a season keeps the standings
  // cached instead of showing the blocking spinner.
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
}, { cacheKey: `season-standings:${props.mode}` });

const leagues = computed<League[]>(() => payload.value?.leagues ?? []);
const allStandingsData = computed<Record<number, any>>(
  () => payload.value?.standingsMap ?? {}
);

// The cache is module-level (see `cacheKey` above), so we deliberately do
// NOT call `resetLeagues()` when `seasonId` is falsy — that would wipe the
// cache for every other mount of this component. When a valid id becomes
// available we just load it; the previous key's data stays around until it
// is naturally overwritten.
watch(() => props.seasonId, (id) => {
  if (!id) return;
  loadLeaguesForSeason(id);
}, { immediate: true });

// Silence unused-var warning; kept in the destructure for API symmetry.
void resetLeagues;
</script>

