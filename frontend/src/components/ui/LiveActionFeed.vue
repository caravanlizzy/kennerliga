<template>
  <div>
    <div v-if="loading" class="flex flex-center q-pa-md">
      <q-spinner-puff color="primary" size="2em" />
    </div>
    <div
      v-else-if="events.length === 0"
      class="text-center q-pa-md text-grey-6 italic"
    >
      No live actions yet.
    </div>
    <div v-else class="q-pa-sm">
      <!-- League Filters -->
      <div
        v-if="availableLeagues.length > 1"
        class="row q-gutter-xs q-mb-md q-px-xs"
      >
        <q-chip
          clickable
          dense
          :outline="!isAllSelected"
          :color="isAllSelected ? 'primary' : 'grey-7'"
          text-color="white"
          size="sm"
          class="text-weight-bold"
          style="border-radius: 8px"
          @click="toggleAllLeagues"
        >
          All
        </q-chip>
        <q-chip
          v-for="lvl in availableLeagues"
          :key="lvl"
          clickable
          dense
          :outline="!selectedLeagues.has(lvl)"
          :color="selectedLeagues.has(lvl) ? 'primary' : 'grey-7'"
          text-color="white"
          size="sm"
          class="text-weight-bold"
          style="border-radius: 8px"
          @click="toggleLeagueFilter(lvl)"
        >
          L{{ lvl }}
        </q-chip>
      </div>

      <div class="column">
        <template v-for="(event, index) in filteredEvents" :key="event.id">
          <div
            class="q-py-md q-px-sm column justify-center"
          >
            <div
              class="flex justify-between items-center q-mb-xs"
              :class="$q.dark.isActive ? 'text-grey-5' : 'text-grey-7'"
              style="font-size: 0.65rem;"
            >
              <span class="row items-center q-gutter-x-xs">
                <q-badge
                  :color="getLeagueColor(Number(event.leagueLevel))"
                  class="text-weight-bold"
                  style="font-size: 0.65rem; border-radius: 6px; padding: 2px 6px;"
                >
                  L{{ event.leagueLevel }}
                </q-badge>

                <q-badge
                  rounded
                  :style="{
                    color: getColorHex(event.type),
                    backgroundColor: `color-mix(in srgb, ${getColorHex(event.type)} 12%, transparent)`,
                    fontSize: '0.65rem',
                    letterSpacing: '0.08em'
                  }"
                  class="text-bold q-px-sm q-py-xs text-uppercase"
                >
                  <q-icon :name="getEventIcon(event.type)" size="12px" class="q-mr-xs" />
                  {{ getEventDisplayType(event.type) }}
                </q-badge>
              </span>
              <span style="opacity: 0.85;">{{
                formatTime(event.timestamp)
              }}</span>
            </div>
            <div
              class="q-mt-xs"
              style="font-size: 0.9rem; line-height: 1.45;"
              :class="$q.dark.isActive ? 'text-grey-3' : 'text-grey-9'"
            >
              <span v-if="event.type === 'PICK'">
                <strong class="text-primary">{{ event.data.playerName }}</strong> picks
                <strong class="text-primary">{{ event.data.gameName }}</strong>
              </span>
              <span v-else-if="event.type === 'BAN'">
                <template v-if="!event.data.skippedBan && event.data.gameName">
                  <strong class="text-primary">{{ event.data.playerName }}</strong> bans
                  <strong class="text-primary">{{ event.data.gameName }}</strong>
                </template>
                <template v-else>
                  <strong class="text-primary">{{ event.data.playerName }}</strong> skips their
                  ban
                </template>
              </span>
              <span v-else-if="event.type === 'GAME_FINISHED'">
                <strong class="text-primary">{{ event.data.winner }}</strong> wins
                <strong class="text-primary">{{ event.data.gameName }}</strong>
                <div v-if="event.data.results" class="q-mt-sm q-pa-xs" :style="{ borderLeft: `1px solid ${$q.dark.isActive ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)'}` }">
                  <table class="full-width" style="border-collapse: collapse; font-size: 0.75rem;">
                    <tbody>
                      <tr v-for="(res, idx) in event.data.results" :key="idx" :style="{ borderBottom: idx === event.data.results.length - 1 ? 'none' : `1px dashed ${$q.dark.isActive ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'}` }">
                        <td class="q-pr-sm text-grey-6" style="width: 20px; font-weight: 500;">
                          {{ res.position || idx + 1 }}.
                        </td>
                        <td class="ellipsis" style="max-width: 120px;">
                          {{ res.playerName }}
                        </td>
                        <td class="text-right text-grey-6 q-pl-xs" v-if="res.points">
                          {{ res.points }} VP
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </span>
              <span v-else-if="event.type === 'LEAGUE_RUNNING'">
                League {{ event.data.leagueLevel || event.leagueLevel }} is on! Games:
                <div v-if="event.data.games && event.data.games.length" class="q-mt-sm q-pa-xs" :style="{ borderLeft: `1px solid ${$q.dark.isActive ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)'}` }">
                  <table class="full-width" style="border-collapse: collapse; font-size: 0.75rem;">
                    <tbody>
                      <tr v-for="(g, idx) in event.data.games" :key="idx" :style="{ borderBottom: idx === event.data.games.length - 1 ? 'none' : `1px dashed ${$q.dark.isActive ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'}` }">
                        <td class="q-pr-sm text-grey-6" style="width: 20px;">
                          {{ idx + 1 }}.
                        </td>
                        <td class="ellipsis" style="max-width: 120px;">
                          <strong class="text-primary">{{ g.gameName }}</strong>
                          <span class="text-grey-6"> &mdash; {{ g.playerName }}</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </span>
              <span v-else-if="event.type === 'LEAGUE_FINISHED'">
                League {{ event.data.leagueLevel || event.leagueLevel }} finishes! Winner:
                <strong class="text-primary">{{ event.data.winners?.join(', ') }}</strong>
              </span>
              <span v-else-if="event.type === 'SEASON_FINISHED'">
                Season {{ event.data.seasonName }} finishes! Shout out to
                <strong class="text-primary">{{ event.data.seasonWinner }}</strong>!
              </span>
            </div>
          </div>
          <q-separator v-if="index < filteredEvents.length - 1" />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { leagueColors } from 'src/composables/leagueColors';
import { TLiveEvent, TLiveEventType } from 'src/types';
import { fetchLiveActionEvents } from 'src/services/seasonService';
import { useUpdateStore } from 'stores/updateStore';
import { useCachedResource } from 'src/composables/cachedResource';

const updateStore = useUpdateStore();
const { getLeagueColor } = leagueColors();

// Stale-while-revalidate cache with a module-level `cacheKey`, so events
// survive component unmount/remount (e.g. navigating away and back). Without
// this, the local refs would be recreated on each mount and the feed would
// flash the blocking spinner every time.
const {
  data: eventsData,
  loading,
  load: loadEvents,
} = useCachedResource<'live', TLiveEvent[]>(
  () => fetchLiveActionEvents(),
  { cacheKey: 'live-action-feed' }
);
const events = computed<TLiveEvent[]>(() => eventsData.value ?? []);

const selectedLeagues = ref<Set<number | string>>(new Set());
let unsubscribe: (() => void) | null = null;

const availableLeagues = computed(() => {
  const lvls = events.value
    .map((e) => e.leagueLevel)
    .filter((lvl): lvl is number | string => lvl !== undefined);
  return Array.from(new Set(lvls)).sort((a, b) => Number(a) - Number(b));
});

const isAllSelected = computed(() => selectedLeagues.value.size === 0);

const filteredEvents = computed(() => {
  if (isAllSelected.value) return events.value;
  return events.value.filter(
    (e) =>
      e.leagueLevel !== undefined && selectedLeagues.value.has(e.leagueLevel)
  );
});

function toggleLeagueFilter(lvl: number | string) {
  if (selectedLeagues.value.has(lvl)) {
    selectedLeagues.value.delete(lvl);
  } else {
    selectedLeagues.value.add(lvl);
  }

  // If all individual leagues are selected, automatically switch to "All" (empty set)
  if (selectedLeagues.value.size === availableLeagues.value.length) {
    selectedLeagues.value.clear();
  }
}

function toggleAllLeagues() {
  selectedLeagues.value.clear();
}

function fetchEvents() {
  // SWR is handled by `useCachedResource`: the blocking `loading` flag is
  // only true until the first payload; subsequent calls run in the
  // background so cached events stay on screen.
  void loadEvents('live');
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

  return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

function getEventDisplayType(type: TLiveEventType) {
  switch (type) {
    case 'PICK':
      return 'PICK';
    case 'BAN':
      return 'BAN';
    case 'LEAGUE_RUNNING':
      return 'RUNNING';
    case 'GAME_FINISHED':
      return 'WIN';
    case 'LEAGUE_FINISHED':
      return 'COMPLETE';
    case 'SEASON_FINISHED':
      return 'SEASON';
    default:
      return type.replace('_', ' ');
  }
}

onMounted(() => {
  fetchEvents();
  unsubscribe = updateStore.subscribe('/season/', fetchEvents);
});

onUnmounted(() => {
  if (unsubscribe) unsubscribe();
});

function getColorHex(type: TLiveEventType) {
  switch (type) {
    case 'PICK':
      return '#37474f'; // primary (from quasar.variables.scss)
    case 'BAN':
      return '#d63a38'; // negative
    case 'LEAGUE_RUNNING':
      return '#1976d2'; // info / blue
    case 'GAME_FINISHED':
      return '#4bb26a'; // positive
    case 'LEAGUE_FINISHED':
      return '#e67e22'; // warning
    case 'SEASON_FINISHED':
      return '#26c6da'; // secondary
    default:
      return '#9e9e9e';
  }
}

function getEventIcon(type: TLiveEventType) {
  switch (type) {
    case 'PICK':
      return 'check_circle';
    case 'BAN':
      return 'block';
    case 'LEAGUE_RUNNING':
      return 'sports_esports';
    case 'GAME_FINISHED':
      return 'emoji_events';
    case 'LEAGUE_FINISHED':
      return 'workspace_premium';
    case 'SEASON_FINISHED':
      return 'military_tech';
    default:
      return 'bolt';
  }
}
</script>

