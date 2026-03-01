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
        class="row q-gutter-xs q-mb-md q-px-xs"
      >
        <q-chip
          clickable
          :outline="!isAllSelected"
          :color="isAllSelected ? 'primary' : 'grey-7'"
          text-color="white"
          size="sm"
          class="text-weight-bold"
          @click="toggleAllLeagues"
        >
          All
        </q-chip>
        <q-chip
          v-for="lvl in availableLeagues"
          :key="lvl"
          clickable
          :outline="!selectedLeagues.has(lvl)"
          :color="selectedLeagues.has(lvl) ? 'primary' : 'grey-7'"
          text-color="white"
          size="sm"
          class="text-weight-bold"
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
        <q-card flat class="event-card">
          <q-card-section class="q-pa-sm">
            <div class="row items-center no-wrap">
              <div class="col-auto q-mr-sm">
                <div
                  class="icon-wrapper flex flex-center"
                  :style="{
                    backgroundColor: getColorHex(event.type) + '15',
                    border: `1px solid ${getColorHex(event.type)}30`,
                  }"
                >
                  <q-icon
                    :name="getIcon(event.type)"
                    :color="getColor(event.type)"
                    size="xs"
                  />
                </div>
              </div>
              <div class="col">
                <div
                  class="text-caption text-grey-7 flex justify-between items-center"
                >
                  <span class="row items-center">
                    <q-badge
                      :color="getLeagueColor(Number(event.leagueLevel))"
                      class="q-mr-xs text-weight-bold"
                      style="font-size: 0.65rem"
                    >
                      L{{ event.leagueLevel }}
                    </q-badge>
                  </span>
                  <span style="font-size: 0.7rem; opacity: 0.8">{{
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
                    <span v-if="event.data.points"> ({{event.data.points}} VP)</span>
                    <div v-if="event.data.results" class="q-mt-xs">
                      <div class="row q-gutter-x-xs text-caption text-grey-8" style="font-size: 0.75rem;">
                        <span v-for="(res, idx) in event.data.results" :key="idx" class="position-item">
                          <span v-if="idx > 0" class="q-mr-xs">•</span>
                          <span class="text-weight-bold">{{ res.position || idx + 1 }}.</span>
                          {{ res.playerName }}
                        </span>
                      </div>
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
import { useLeagueColors } from 'src/composables/useLeagueColors';
import { TLiveEvent, TLiveEventType } from 'src/types';
import { fetchLiveActionEvents } from 'src/services/seasonService';
import { useUpdateStore } from 'stores/updateStore';

const updateStore = useUpdateStore();
const { getLeagueColor } = useLeagueColors();
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

function getIcon(type: TLiveEventType) {
  switch (type) {
    case 'PICK':
      return 'add_circle';
    case 'BAN':
      return 'block';
    case 'GAME_FINISHED':
      return 'check_circle';
    case 'LEAGUE_FINISHED':
      return 'emoji_events';
    case 'SEASON_FINISHED':
      return 'celebration';
    default:
      return 'info';
  }
}

function getColor(type: TLiveEventType) {
  switch (type) {
    case 'PICK':
      return 'primary';
    case 'BAN':
      return 'negative';
    case 'GAME_FINISHED':
      return 'positive';
    case 'LEAGUE_FINISHED':
      return 'warning';
    case 'SEASON_FINISHED':
      return 'accent';
    default:
      return 'grey';
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
</script>

<style scoped>
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
}

.event-card {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  border-radius: 8px;
}

.icon-wrapper {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}
.event-content {
  font-size: 0.9rem;
  line-height: 1.4;
  color: #2c3e50;
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
