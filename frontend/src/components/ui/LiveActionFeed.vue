<template>
  <div>
    <div v-if="loading" class="flex flex-center q-pa-md">
      <q-spinner color="primary" size="2em" />
    </div>
    <div
      v-else-if="events.length === 0"
      class="text-center q-pa-md text-grey-6 italic"
    >
      No live actions yet.
    </div>
    <div v-else class="events-list q-pa-sm">
      <!-- League Filters -->
      <div
        v-if="availableLeagues.length > 1"
        class="row q-gutter-xs q-mb-md q-px-xs league-filter-row"
      >
        <q-chip
          clickable
          dense
          :outline="!isAllSelected"
          :color="isAllSelected ? 'primary' : 'grey-7'"
          text-color="white"
          size="sm"
          class="text-weight-bold league-filter-chip"
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
          class="text-weight-bold league-filter-chip"
          @click="toggleLeagueFilter(lvl)"
        >
          L{{ lvl }}
        </q-chip>
      </div>

      <div
        v-for="event in filteredEvents"
        :key="event.id"
        class="event-item q-mb-sm"
      >
        <q-card
          flat
          :class="['event-card', `event-card--${event.type.toLowerCase()}`]"
          :style="{ '--event-color': getColorHex(event.type) }"
        >
          <q-card-section class="q-pa-sm q-pl-md">
            <div class="row items-center no-wrap">
              <div class="col">
                <div
                  class="text-caption flex justify-between items-center event-meta"
                >
                  <span class="row items-center q-gutter-x-xs">
                    <q-badge
                      :color="getLeagueColor(Number(event.leagueLevel))"
                      class="text-weight-bold league-badge"
                    >
                      L{{ event.leagueLevel }}
                    </q-badge>

                    <span class="event-type-pill">
                      <q-icon :name="getEventIcon(event.type)" size="12px" class="q-mr-xs" />
                      {{ getEventDisplayType(event.type) }}
                    </span>
                  </span>
                  <span class="event-time">{{
                    formatTime(event.timestamp)
                  }}</span>
                </div>
                <div class="event-content q-mt-xs">
                  <span v-if="event.type === 'PICK'">
                    <strong>{{ event.data.playerName }}</strong> picks
                    <strong>{{ event.data.gameName }}</strong>
                  </span>
                  <span v-else-if="event.type === 'BAN'">
                    <template v-if="!event.data.skippedBan && event.data.gameName">
                      <strong>{{ event.data.playerName }}</strong> bans
                      <strong>{{ event.data.gameName }}</strong>
                    </template>
                    <template v-else>
                      <strong>{{ event.data.playerName }}</strong> skips their
                      ban
                    </template>
                  </span>
                  <span v-else-if="event.type === 'GAME_FINISHED'">
                    <strong>{{ event.data.winner }}</strong> wins
                    <strong>{{ event.data.gameName }}</strong>
                    <div v-if="event.data.results" class="q-mt-sm results-container">
                      <table class="results-table full-width">
                        <tbody>
                          <tr v-for="(res, idx) in event.data.results" :key="idx">
                            <td class="results-table__pos q-pr-sm" style="width: 20px;">
                              {{ res.position || idx + 1 }}.
                            </td>
                            <td class="playerName results-table__name">
                              {{ res.playerName }}
                            </td>
                            <td class="text-right results-table__points text-caption" v-if="res.points">
                              {{ res.points }} VP
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </span>
                  <span v-else-if="event.type === 'LEAGUE_RUNNING'">
                    League {{ event.data.leagueLevel || event.leagueLevel }} is on! Games being played:
                    <div v-if="event.data.games && event.data.games.length" class="q-mt-sm results-container">
                      <table class="results-table full-width">
                        <tbody>
                          <tr v-for="(g, idx) in event.data.games" :key="idx">
                            <td class="results-table__pos q-pr-sm" style="width: 20px;">
                              {{ idx + 1 }}.
                            </td>
                            <td class="playerName results-table__name">
                              <strong>{{ g.gameName }}</strong>
                              <span class="text-grey-6"> &mdash; {{ g.playerName }}</span>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </span>
                  <span v-else-if="event.type === 'LEAGUE_FINISHED'">
                    League {{ event.data.leagueLevel || event.leagueLevel }} finishes! Winner:
                    <strong>{{ event.data.winners?.join(', ') }}</strong>
                  </span>
                  <span v-else-if="event.type === 'SEASON_FINISHED'">
                    Season {{ event.data.seasonName }} finishes! Shout out to
                    <strong>{{ event.data.seasonWinner }}</strong
                    >!
                  </span>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { leagueColors } from '../../composables/leagueColors';
import { TLiveEvent, TLiveEventType } from 'src/types';
import { fetchLiveActionEvents } from 'src/services/seasonService';
import { useUpdateStore } from 'stores/updateStore';

const updateStore = useUpdateStore();
const { getLeagueColor } = leagueColors();
const events = ref<TLiveEvent[]>([]);
const loading = ref(true);
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

async function fetchEvents() {
  try {
    events.value = await fetchLiveActionEvents();
  } catch (error) {
    console.error('Error fetching live events:', error);
  } finally {
    loading.value = false;
  }
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

<style scoped lang="scss">
.live-action-feed {
  max-height: 500px;
  overflow-y: auto;
}

@media (min-width: 1024px) {
  .live-action-feed {
    max-height: none;
    height: calc(100vh - 250px);
    min-height: 400px;
  }
}

.custom-scrollbar {
  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 10px;
  }

  :global(.body--dark) &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
  }
}

.league-badge {
  font-size: 0.65rem;
  letter-spacing: 0.04em;
  padding: 2px 6px;
  border-radius: 6px;
}

.event-type-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 2px 8px;
  border-radius: 999px;
  color: var(--event-color);
  background: color-mix(in srgb, var(--event-color) 12%, transparent);
  text-transform: uppercase;
}

.event-meta {
  color: #64748b;
}

:global(.body--dark) .event-meta {
  color: #94a3b8;
}

.event-time {
  font-size: 0.7rem;
  font-variant-numeric: tabular-nums;
  opacity: 0.85;
}

.event-card {
  position: relative;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(54, 64, 88, 0.08);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

:global(.body--dark) .event-card {
  background: rgba(30, 34, 45, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: none;
}

.event-content {
  font-size: 0.9rem;
  line-height: 1.45;
  color: #1f2937;
}

:global(.body--dark) .event-content {
  color: #e5e7eb;
}

.results-container {
  padding: 4px 8px;
  margin-top: 6px;
  background: transparent;
  border-left: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 0;
}

:global(.body--dark) .results-container {
  border-left-color: rgba(255, 255, 255, 0.08);
}

.league-filter-chip {
  border-radius: 8px;
}

.results-table {
  border-collapse: collapse;
  font-size: 0.75rem;
  margin-top: 2px;
}

.results-table tr {
  border-bottom: 1px dashed rgba(0, 0, 0, 0.04);
}

:global(.body--dark) .results-table tr {
  border-bottom: 1px dashed rgba(255, 255, 255, 0.04);
}
.results-table tr:last-child {
  border-bottom: none;
}
.results-table td {
  padding: 3px 0;
  vertical-align: middle;
}
.results-table__pos {
  color: #94a3b8;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
.results-table__name {
  color: #475569;
  font-weight: 400;
}
.results-table__points {
  color: #94a3b8;
  font-variant-numeric: tabular-nums;
}
:global(.body--dark) .results-table__pos,
:global(.body--dark) .results-table__points {
  color: #64748b;
}
:global(.body--dark) .results-table__name {
  color: #cbd5e1;
}
.results-table .playerName {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.position-item {
  display: flex;
  align-items: center;
  white-space: nowrap;
}
strong {
  color: var(--q-primary);
}
</style>
