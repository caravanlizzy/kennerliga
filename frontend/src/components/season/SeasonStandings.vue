<template>
  <div class="q-pa-md column season-standings">
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
            <div
              v-if="mode === 'results'"
              class="row items-center q-gutter-x-sm q-mb-md q-px-sm q-pt-sm"
            >
              <LeagueLevel :level="league.level" />
              <span class="text-subtitle1 text-weight-bold">{{ league.name }}</span>
            </div>
            <LeagueMatchResults
              v-if="mode === 'results'"
              :leagueId="league.id"
              :show-standings="isOverviewPage"
            />
            <LeagueStandings v-else-if="mode === 'standings-simple'" :leagueId="league.id" />
            <div v-else-if="mode === 'picks'" class="q-pa-sm">
              <div class="row items-center q-gutter-x-sm q-mb-md q-px-sm q-pt-sm">
                <LeagueLevel :level="league.level" />
                <span class="text-subtitle1 text-weight-bold">{{ league.name }} Picks &amp; Bans</span>
              </div>
              <PlayerCard
                v-if="getMembersForLeague(league.id).length > 0"
                :all-members="getMembersForLeague(league.id)"
              />
              <div v-else class="q-pa-md text-grey-6 italic text-center">
                No participant picks recorded for this league.
              </div>
            </div>
            <LeagueStandingsMatrix v-else :leagueId="league.id" :prefetchedData="allStandingsData[league.id]" :level="league.level" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import LeagueMatchResults from 'components/league/LeagueMatchResults.vue';
import LeagueStandings from 'components/league/LeagueStandings.vue';
import LeagueStandingsMatrix from 'components/league/LeagueStandingsMatrix.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import PlayerCard from 'components/league/PlayerCard.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { api } from 'boot/axios';
import KennerButton from 'components/base/KennerButton.vue';
import { useCachedResource } from 'src/composables/cachedResource';
import { fetchSeasonParticipants } from 'src/services/seasonService';
import type { TSeasonParticipantDto } from 'src/types';

import { useLeagueStore } from 'stores/leagueStore';
import { useUpdateStore } from 'stores/updateStore';

const route = useRoute();
const updateStore = useUpdateStore();
let unsubSeason: (() => void) | null = null;
let unsubLeague: (() => void) | null = null;

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
  mode?: 'standings' | 'results' | 'standings-simple' | 'picks';
  participants?: TSeasonParticipantDto[];
}>(), {
  mode: 'standings'
});

const isOverviewPage = computed(() => route.name === 'season-overview');

const participantsList = ref<TSeasonParticipantDto[]>(props.participants || []);

watch(() => props.participants, (newVal) => {
  if (newVal && newVal.length > 0) {
    participantsList.value = newVal;
  }
}, { immediate: true });

async function ensureParticipantsLoaded() {
  if (props.mode === 'picks' && participantsList.value.length === 0 && props.seasonId) {
    try {
      participantsList.value = await fetchSeasonParticipants(props.seasonId);
    } catch (e) {
      console.error('Failed to load season participants for picks:', e);
    }
  }
}

watch(() => [props.seasonId, props.mode], () => {
  ensureParticipantsLoaded();
}, { immediate: true });

function getMembersForLeague(leagueId: number) {
  return participantsList.value.filter((p) => {
    if (typeof p.league === 'object' && p.league !== null) {
      return (p.league as any).id === leagueId;
    }
    return p.league === leagueId;
  });
}

// Stale-while-revalidate loader: cached data for the current season stays on
// screen while a fresh request is in flight, so the UI never flashes the
// blocking spinner on subsequent visits.
const {
  data: payload,
  loading: loadingLeagues,
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

async function refreshData() {
  if (props.seasonId) {
    if (props.mode === 'picks') {
      try {
        participantsList.value = await fetchSeasonParticipants(props.seasonId);
      } catch (e) {
        console.error('Failed to reload season participants for picks:', e);
      }
    }
    await loadLeaguesForSeason(props.seasonId);
  }
}

onMounted(() => {
  unsubSeason = updateStore.subscribe('/season/', refreshData);
  unsubLeague = updateStore.subscribe('/league/', refreshData);
});

onUnmounted(() => {
  if (unsubSeason) unsubSeason();
  if (unsubLeague) unsubLeague();
});

// Silence unused-var warning; kept in the destructure for API symmetry.
void resetLeagues;
</script>

<style scoped lang="scss">
.league-card {
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  background: #fafafa;
  padding: 8px;
}
</style>

