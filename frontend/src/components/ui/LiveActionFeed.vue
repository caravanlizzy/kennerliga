<template>
  <div class="live-action-feed">
    <div v-if="loading" class="flex flex-center q-pa-md">
      <q-spinner color="primary" size="2em" />
    </div>
    <div v-else-if="events.length === 0" class="text-center q-pa-md text-grey-6 italic">
      No live actions yet.
    </div>
    <div v-else class="events-list q-pa-sm">
      <div v-for="event in events" :key="event.id" class="event-item q-mb-sm">
        <q-card flat bordered class="event-card" :style="{ borderLeftColor: getColorHex(event.type) }">
          <q-card-section class="q-pa-sm">
            <div class="row items-center no-wrap">
              <div class="col-auto q-mr-sm">
                <q-icon :name="getIcon(event.type)" :color="getColor(event.type)" size="sm" />
              </div>
              <div class="col">
                <div class="text-caption text-grey-7 flex justify-between">
                  <span>League {{ event.leagueLevel }}</span>
                  <span>{{ formatTime(event.timestamp) }}</span>
                </div>
                <div class="event-content">
                  <span v-if="event.type === 'PICK'">
                    <strong>{{ event.data.playerName }}</strong> picked <strong>{{ event.data.gameName }}</strong>
                  </span>
                  <span v-else-if="event.type === 'BAN'">
                    <strong>{{ event.data.playerName }}</strong> banned <strong>{{ event.data.gameName }}</strong>
                  </span>
                  <span v-else-if="event.type === 'GAME_FINISHED'">
                    Game <strong>{{ event.data.gameName }}</strong> finished! {{ event.data.summary }}
                  </span>
                  <span v-else-if="event.type === 'LEAGUE_FINISHED'">
                    League {{ event.leagueLevel }} finished! Winners: {{ event.data.winners?.join(', ') }}
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
import { ref, onMounted, onUnmounted } from 'vue';
import { TLiveEvent, TLiveEventType } from 'src/types';
import { fetchLiveActionEvents } from 'src/services/seasonService';

const events = ref<TLiveEvent[]>([]);
const loading = ref(true);
let pollInterval: any = null;

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
.event-card {
  transition: transform 0.2s;
  border-left: 4px solid currentColor;
}
.event-card:hover {
  transform: translateX(4px);
}
.event-content {
  font-size: 0.9rem;
  line-height: 1.4;
}

</style>
