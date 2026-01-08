<template>
  <div class="live-action-feed custom-scrollbar">
    <div v-if="loading" class="flex flex-center q-pa-md">
      <q-spinner color="primary" size="2em" />
    </div>
    <div v-else-if="events.length === 0" class="text-center q-pa-md text-grey-6 italic">
      No live actions yet.
    </div>
    <div v-else class="events-list q-pa-sm">
      <!-- League Filters -->
      <div v-if="availableLeagues.length > 1" class="row q-gutter-xs q-mb-md q-px-xs">
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

      <div v-for="event in filteredEvents" :key="event.id" class="event-item q-mb-sm">
        <q-card flat class="event-card" :style="{ borderLeftColor: getColorHex(event.type) }">
          <q-card-section class="q-pa-sm">
            <div class="row items-center no-wrap">
              <div class="col-auto q-mr-sm">
                <q-icon :name="getIcon(event.type)" :color="getColor(event.type)" size="sm" />
              </div>
              <div class="col">
                <div class="text-caption text-grey-7 flex justify-between items-center">
                  <span class="row items-center">
                    <q-badge color="grey-3" text-color="grey-9" class="q-mr-xs text-weight-bold" style="font-size: 0.65rem">
                      L{{ event.leagueLevel }}
                    </q-badge>
                  </span>
                  <span style="font-size: 0.7rem; opacity: 0.8">{{ formatTime(event.timestamp) }}</span>
                </div>
                <div class="event-content q-mt-xs">
                  <span v-if="event.type === 'PICK'">
                    <strong>{{ event.data.playerName }}</strong> picked <strong>{{ event.data.gameName }}</strong>
                  </span>
                  <span v-else-if="event.type === 'BAN'">
                    <template v-if="event.data.gameName">
                      <strong>{{ event.data.playerName }}</strong> banned <strong>{{ event.data.gameName }}</strong>
                    </template>
                    <template v-else>
                      <strong>{{ event.data.playerName }}</strong> skipped their ban
                    </template>
                  </span>
                  <span v-else-if="event.type === 'GAME_FINISHED'">
                    Game <strong>{{ event.data.gameName }}</strong> finished! {{ event.data.summary }}
                  </span>
                  <span v-else-if="event.type === 'LEAGUE_FINISHED'">
                    League {{ event.leagueLevel }} finished! Winner: <strong>{{ event.data.winners?.join(', ') }}</strong>
                  </span>
                  <span v-else-if="event.type === 'SEASON_FINISHED'">
                    Season finished! Shout out to <strong>{{ event.data.seasonWinner }}</strong>!
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
import { TLiveEvent, TLiveEventType } from 'src/types';
import { fetchLiveActionEvents } from 'src/services/seasonService';

const events = ref<TLiveEvent[]>([]);
const loading = ref(true);
const selectedLeagues = ref<Set<number | string>>(new Set());
let pollInterval: any = null;

const availableLeagues = computed(() => {
  const lvls = events.value
    .map((e) => e.leagueLevel)
    .filter((lvl): lvl is number | string => lvl !== undefined);
  return Array.from(new Set(lvls)).sort((a, b) => Number(a) - Number(b));
});

const isAllSelected = computed(() => selectedLeagues.value.size === 0);

const filteredEvents = computed(() => {
  if (isAllSelected.value) return events.value;
  return events.value.filter((e) => e.leagueLevel !== undefined && selectedLeagues.value.has(e.leagueLevel));
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
    case 'PICK': return 'add_circle';
    case 'BAN': return 'block';
    case 'GAME_FINISHED': return 'check_circle';
    case 'LEAGUE_FINISHED': return 'emoji_events';
    case 'SEASON_FINISHED': return 'celebration';
    default: return 'info';
  }
}

function getColor(type: TLiveEventType) {
  switch (type) {
    case 'PICK': return 'primary';
    case 'BAN': return 'negative';
    case 'GAME_FINISHED': return 'positive';
    case 'LEAGUE_FINISHED': return 'warning';
    case 'SEASON_FINISHED': return 'accent';
    default: return 'grey';
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
  pollInterval = setInterval(fetchEvents, 30000); // Poll every 30s
});

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval);
});

function getColorHex(type: TLiveEventType) {
  switch (type) {
    case 'PICK': return '#364058'; // primary
    case 'BAN': return '#d63a38'; // negative
    case 'GAME_FINISHED': return '#4bb26a'; // positive
    case 'LEAGUE_FINISHED': return '#facb48'; // warning
    case 'SEASON_FINISHED': return '#5e35b1'; // accent
    default: return '#9e9e9e';
  }
}
</script>

<style scoped>
.live-action-feed {
  max-height: 500px;
  overflow-y: auto;
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
  border-left: 3px solid currentColor;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  border-radius: 8px;
  margin-left: 1px;
}
.event-card:hover {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.event-content {
  font-size: 0.9rem;
  line-height: 1.4;
  color: #2c3e50;
}
strong {
  color: var(--q-primary);
}

</style>
