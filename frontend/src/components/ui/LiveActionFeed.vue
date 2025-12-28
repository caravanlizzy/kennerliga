<template>
  <div class="live-action-feed">
    <div v-if="loading" class="flex flex-center q-pa-md">
      <q-spinner color="primary" size="2em" />
    </div>
    <div v-else-if="events.length === 0" class="text-center q-pa-md text-grey-6 italic">
      No live actions yet.
    </div>
    <div v-else class="events-list q-pa-sm">
      <div v-for="event in sortedEvents" :key="event.id" class="event-item q-mb-sm">
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
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { TLiveEvent, TLiveEventType } from 'src/types';
import { fetchCurrentSeasonId, fetchLeaguesBySeason } from 'src/services/seasonService';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { api } from 'boot/axios';

const events = ref<TLiveEvent[]>([]);
const loading = ref(true);
let pollInterval: any = null;

const sortedEvents = computed(() => {
  return [...events.value].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
});

async function fetchEvents() {
  try {
    const seasonId = await fetchCurrentSeasonId();
    if (!seasonId) return;

    const leagues = await fetchLeaguesBySeason(seasonId);
    const newEvents: TLiveEvent[] = [];

    for (const leagueSummary of leagues) {
      const league = await fetchLeagueDetails(leagueSummary.id);

      // Game Picks & Bans
      for (const member of league.members) {
        if (member.selected_games) {
          for (const game of member.selected_games) {
            newEvents.push({
              id: `pick-${game.id}`,
              type: 'PICK',
              timestamp: game.created_at || new Date().toISOString(), // Assuming created_at exists, fallback to now
              leagueLevel: league.level,
              leagueId: league.id,
              data: {
                playerName: member.username || member.profile_name,
                gameName: game.game_name
              }
            });
          }
        }

        if (member.banned_selected_game) {
          newEvents.push({
            id: `ban-${member.id}`,
            type: 'BAN',
            timestamp: new Date().toISOString(), // We might not have ban timestamp easily
            leagueLevel: league.level,
            leagueId: league.id,
            data: {
              playerName: member.username || member.profile_name,
              gameName: member.banned_selected_game.game_name
            }
          });
        }
      }

      // Game Finished (check results)
      for (const member of league.members) {
        if (member.selected_games) {
          for (const game of member.selected_games) {
            try {
              const { data: results } = await api.get<any[]>(`/result/results/?selected_game=${game.id}`);
              // Check if game is finished: results length equals league members length
              if (results.length > 0 && results.length === league.members.length) {
                // Sort results to find winner
                const sortedResults = [...results].sort((a, b) => (b.points || 0) - (a.points || 0));
                const winner = sortedResults[0];
                newEvents.push({
                  id: `finish-${game.id}`,
                  type: 'GAME_FINISHED',
                  timestamp: sortedResults[0].created_at || new Date().toISOString(),
                  leagueLevel: league.level,
                  leagueId: league.id,
                  data: {
                    gameName: game.game_name,
                    summary: `Winner: ${winner.player_profile_name} (${winner.points} pts)`
                  }
                });
              }
            } catch (e) {
              console.error(`Error fetching results for game ${game.id}`, e);
            }
          }
        }
      }

      if (league.status === 'DONE') {
        newEvents.push({
          id: `league-done-${league.id}`,
          type: 'LEAGUE_FINISHED',
          timestamp: new Date().toISOString(),
          leagueLevel: league.level,
          leagueId: league.id,
          data: {
            winners: league.members.slice(0, 3).map(m => m.username || m.profile_name) // Mock winners
          }
        });
      }
    }

    // Check for Season Finished
    if (leagues.length > 0 && leagues.every(l => l.status === 'DONE')) {
      const l1 = leagues.find(l => l.level === 1 || l.level === '1');
      if (l1) {
        const l1Details = await fetchLeagueDetails(l1.id);
        const winner = l1Details.members.sort((a, b) => (b.position || 0) - (a.position || 0))[0]; // This logic might need refinement based on how season winners are calculated
        if (winner) {
          newEvents.push({
            id: `season-done-${seasonId}`,
            type: 'SEASON_FINISHED',
            timestamp: new Date().toISOString(),
            leagueId: l1.id,
            data: {
              seasonWinner: winner.username || winner.profile_name
            }
          });
        }
      }
    }

    // Deduplicate and update
    const existingIds = new Set(events.value.map(e => e.id));
    const filteredNew = newEvents.filter(e => !existingIds.has(e.id));
    if (filteredNew.length > 0) {
      events.value = [...events.value, ...filteredNew];
    }

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
