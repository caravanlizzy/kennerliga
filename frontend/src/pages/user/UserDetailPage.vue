<!-- UserSeasons.vue -->
<template>
  <section class="q-pa-sm">
    <!-- User header -->
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold row items-center">
        <q-icon name="person" class="q-mr-sm" color="primary" />
        {{ user?.username || route.params.username }}
      </div>
      <KennerButton
        dense
        flat
        round
        icon="refresh"
        @click="reload"
        :loading="loading"
        :disable="loading"
      >
        <KennerTooltip>Refresh data</KennerTooltip>
      </KennerButton>
    </div>

    <!-- Stats Overview -->
    <div v-if="!loading && user" class="q-mb-lg">
      <div class="row q-col-gutter-sm">
        <div class="col-12 col-sm-4">
          <q-card flat bordered class="text-center q-pa-sm bg-blue-1 text-blue-9">
            <div class="text-caption text-weight-medium">Seasons</div>
            <div class="text-h6 text-weight-bold">{{ stats.totalSeasons }}</div>
          </q-card>
        </div>
        <div class="col-12 col-sm-4">
          <q-card flat bordered class="text-center q-pa-sm bg-green-1 text-green-9">
            <div class="text-caption text-weight-medium">Avg Rank</div>
            <div class="text-h6 text-weight-bold">
              {{ stats.avgSeasonRank ? stats.avgSeasonRank.toFixed(1) : '-' }}
            </div>
          </q-card>
        </div>
        <div class="col-12 col-sm-4">
          <q-card flat bordered class="text-center q-pa-sm bg-orange-1 text-orange-9">
            <div class="text-caption text-weight-medium">Win Rate</div>
            <div class="text-h6 text-weight-bold">{{ stats.winRate.toFixed(0) }}%</div>
          </q-card>
        </div>
      </div>

      <div class="row q-col-gutter-sm q-mt-sm">
        <!-- Position Distribution -->
        <div class="col-12">
          <q-card flat bordered>
            <q-card-section class="q-py-xs bg-grey-1">
              <div class="text-subtitle2">Game Positions</div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-py-md">
              <div class="row q-col-gutter-md items-center">
                <div class="col-12 col-sm-4 text-center">
                  <div class="text-h3 text-weight-bolder text-primary">
                    {{ stats.avgGamePosition ? stats.avgGamePosition.toFixed(1) : '-' }}
                  </div>
                  <div class="text-caption text-grey-7">Average Position</div>
                </div>
                <div class="col-12 col-sm-8">
                  <div class="row items-center q-gutter-x-sm no-wrap q-mb-xs">
                    <div style="width: 30px" class="text-weight-bold text-caption">1st</div>
                    <div class="col">
                      <q-linear-progress :value="stats.positionDistribution[1] / (stats.totalGames || 1)" color="positive" size="12px" rounded />
                    </div>
                    <div style="width: 25px" class="text-right text-caption">{{ stats.positionDistribution[1] }}</div>
                  </div>
                  <div class="row items-center q-gutter-x-sm no-wrap q-mb-xs">
                    <div style="width: 30px" class="text-weight-bold text-caption">2nd</div>
                    <div class="col">
                      <q-linear-progress :value="stats.positionDistribution[2] / (stats.totalGames || 1)" color="green-4" size="12px" rounded />
                    </div>
                    <div style="width: 25px" class="text-right text-caption">{{ stats.positionDistribution[2] }}</div>
                  </div>
                  <div class="row items-center q-gutter-x-sm no-wrap q-mb-xs">
                    <div style="width: 30px" class="text-weight-bold text-caption">3rd</div>
                    <div class="col">
                      <q-linear-progress :value="stats.positionDistribution[3] / (stats.totalGames || 1)" color="orange-4" size="12px" rounded />
                    </div>
                    <div style="width: 25px" class="text-right text-caption">{{ stats.positionDistribution[3] }}</div>
                  </div>
                  <div class="row items-center q-gutter-x-sm no-wrap q-mb-xs">
                    <div style="width: 30px" class="text-weight-bold text-caption">4th</div>
                    <div class="col">
                      <q-linear-progress :value="stats.positionDistribution[4] / (stats.totalGames || 1)" color="deep-orange-4" size="12px" rounded />
                    </div>
                    <div style="width: 25px" class="text-right text-caption">{{ stats.positionDistribution[4] }}</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card flat bordered class="full-height">
            <q-card-section class="q-py-xs bg-grey-1">
              <div class="text-subtitle2">Most Played Games</div>
            </q-card-section>
            <q-separator />
            <q-list dense>
              <q-item v-for="game in stats.mostPlayedGames" :key="game.name">
                <q-item-section avatar>
                  <q-icon name="videogame_asset" color="grey-6" size="xs" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ game.name }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-badge color="primary" rounded>{{ game.count }}</q-badge>
                </q-item-section>
              </q-item>
              <q-item v-if="!stats.mostPlayedGames.length">
                <q-item-section class="text-grey-6 italic">No games played yet</q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card flat bordered class="full-height">
            <q-card-section class="q-py-xs bg-grey-1">
              <div class="text-subtitle2">Best Games (Avg. Pos)</div>
            </q-card-section>
            <q-separator />
            <q-list dense>
              <q-item v-for="game in stats.bestGames" :key="game.name">
                <q-item-section avatar>
                  <q-icon name="star" color="orange" size="xs" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ game.name }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-badge color="secondary" rounded>#{{ game.avgPos.toFixed(1) }}</q-badge>
                </q-item-section>
              </q-item>
              <q-item v-if="!stats.bestGames.length">
                <q-item-section class="text-grey-6 italic">Play more games to see your best!</q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>

        <div class="col-12">
           <q-card flat bordered>
            <q-card-section class="q-py-xs bg-grey-1">
              <div class="text-subtitle2">Lifetime Achievements</div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-py-sm">
              <div class="row q-col-gutter-md">
                <div class="col-6 col-sm-3 text-center">
                  <div class="text-h6 text-weight-bold">{{ stats.totalGames }}</div>
                  <div class="text-caption text-grey-7">Total Games</div>
                </div>
                <div class="col-6 col-sm-3 text-center">
                  <div class="text-h6 text-weight-bold">{{ leagueMemberships.length }}</div>
                  <div class="text-caption text-grey-7">Leagues Joined</div>
                </div>
                <div class="col-6 col-sm-3 text-center">
                  <div class="text-h6 text-weight-bold text-secondary">
                    {{ stats.highestRank ? `#${stats.highestRank}` : '-' }}
                  </div>
                  <div class="text-caption text-grey-7">Highest Season Rank</div>
                </div>
                <div class="col-6 col-sm-3 text-center">
                   <div class="text-h6 text-weight-bold text-accent">
                    {{ stats.avgLeagueLevel ? stats.avgLeagueLevel.toFixed(1) : '-' }}
                  </div>
                  <div class="text-caption text-grey-7">Avg League Level</div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Seasons box -->
    <q-card flat bordered class="rounded-borders">
      <q-card-section class="bg-grey-1 q-py-xs q-px-sm">
        <div class="text-subtitle2 text-weight-medium">
          Seasons Participated
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <!-- Loading -->
        <LoadingSpinner v-if="loading" text="Loading…" />

        <!-- Empty -->
        <q-banner
          v-else-if="!userSeasonList.length"
          class="bg-grey-2 text-grey-8 q-ma-none q-pa-sm"
        >
          No seasons found.
        </q-banner>

        <!-- Season cards -->
        <div v-else class="row q-col-gutter-md">
          <div
            v-for="sp in userSeasonList"
            :key="sp.id"
            class="col-12 col-sm-6 col-md-4"
          >
            <q-card
              flat
              bordered
              clickable
              class="rounded-borders hover-shadow"
              @click="$emit('open:season', sp.season)"
            >
              <q-card-section class="row items-center no-wrap">
                <q-avatar
                  icon="event"
                  color="primary"
                  text-color="white"
                  class="q-mr-md"
                />
                <div class="col">
                  <div class="text-subtitle1 text-weight-bold">
                    {{ sp.season_details?.name }}
                  </div>
                  <div class="text-caption text-grey-7">
                    <span v-if="sp.season_details?.year">Year: {{ sp.season_details.year }}</span>
                    <span v-if="sp.season_details?.status"> · Status: {{ sp.season_details.status }}</span>
                  </div>
                </div>
              </q-card-section>
              <q-separator v-if="sp.rank !== null" />
              <q-card-section v-if="sp.rank !== null" class="q-py-xs">
                <div class="row items-center justify-between">
                  <span class="text-caption text-grey-7">Season Rank:</span>
                  <q-badge color="secondary" class="text-weight-bold">
                    #{{ sp.rank }}
                  </q-badge>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </section>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';
import { onMounted, ref, computed } from 'vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { TSeasonDto, TSeasonParticipantDto, TUserDto, TMatchResultDto, TLeagueDto, TSelectedGameDto } from 'src/types';

defineEmits<{ (e: 'open:season', seasonId: number | string): void }>();

const user = ref<TUserDto>();
const userSeasonList = ref<(TSeasonParticipantDto & { season_details?: TSeasonDto })[]>([]);
const matchResults = ref<TMatchResultDto[]>([]);
const leagueMemberships = ref<TLeagueDto[]>([]);
const loading = ref(true);
const route = useRoute();

onMounted(async () => {
  await loadData();
});

async function loadData() {
  loading.value = true;
  try {
    await fetchUser();
    const profileId = user.value?.profile_id;
    if (profileId) {
      await Promise.all([
        fetchUserSeasons(),
        fetchMatchResults(),
        fetchLeagueMemberships(),
      ]);
    }
  } finally {
    loading.value = false;
  }
}

function reload() {
  loadData();
}

async function fetchUser(): Promise<void> {
  try {
    const { data } = await api(
      `user/users/${encodeURIComponent(String(route.params.username))}/`
    );
    user.value = data;
  } catch (err) {
    console.error('Failed to fetch user:', err);
  }
}

async function fetchUserSeasons(): Promise<void> {
  const profileId = user.value?.profile_id;
  if (!profileId) return;
  try {
    const { data } = await api.get('season/season-participants/', {
      params: { profile: profileId },
    });
    userSeasonList.value = Array.isArray(data) ? data : data.results || [];
  } catch (err: any) {
    console.error('Failed to fetch user seasons:', err);
    userSeasonList.value = [];
  }
}

async function fetchMatchResults(): Promise<void> {
  const profileId = user.value?.profile_id;
  if (!profileId) return;
  try {
    const { data } = await api.get('result/results/', {
      params: { player_profile: profileId },
    });
    matchResults.value = Array.isArray(data) ? data : data.results || [];
  } catch (err: any) {
    console.error('Failed to fetch match results:', err);
    matchResults.value = [];
  }
}

const stats = computed(() => {
  const totalSeasons = userSeasonList.value.length;
  const ranks = userSeasonList.value
    .map((sp) => sp.rank)
    .filter((r): r is number => r !== null);
  const avgSeasonRank = ranks.length
    ? ranks.reduce((a, b) => a + b, 0) / ranks.length
    : 0;

  const gamePositions = matchResults.value
    .map((r) => r.position)
    .filter((p): p is number => p !== null);
  const avgGamePosition = gamePositions.length
    ? gamePositions.reduce((a, b) => a + b, 0) / gamePositions.length
    : 0;

  const levels = leagueMemberships.value
    .map((l) => Number(l.level))
    .filter((l) => !isNaN(l));
  const avgLeagueLevel = levels.length
    ? levels.reduce((a, b) => a + b, 0) / levels.length
    : 0;

  // Most played games
  const gameCounts: Record<string, { count: number; name: string; positions: number[] }> = {};
  matchResults.value.forEach((r) => {
    const gameName = r.game_name || `Game ${r.selected_game}`;
    if (!gameCounts[gameName]) {
      gameCounts[gameName] = {
        count: 0,
        name: gameName,
        positions: [],
      };
    }
    gameCounts[gameName].count++;
    if (r.position !== null) {
      gameCounts[gameName].positions.push(r.position);
    }
  });

  const mostPlayedGames = Object.values(gameCounts)
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  const bestGames = Object.values(gameCounts)
    .filter((g) => g.positions.length >= 2) // Need at least 2 games to be "best" consistently
    .map((g) => ({
      ...g,
      avgPos: g.positions.reduce((a, b) => a + b, 0) / g.positions.length,
    }))
    .sort((a, b) => a.avgPos - b.avgPos || b.count - a.count)
    .slice(0, 5);

  const positionDistribution = {
    1: gamePositions.filter((p) => p === 1).length,
    2: gamePositions.filter((p) => p === 2).length,
    3: gamePositions.filter((p) => p === 3).length,
    4: gamePositions.filter((p) => p === 4).length,
  };

  const winRate = gamePositions.length
    ? (positionDistribution[1] / gamePositions.length) * 100
    : 0;

  const highestRank = ranks.length ? Math.min(...ranks) : null;

  return {
    totalSeasons,
    avgSeasonRank,
    avgGamePosition,
    avgLeagueLevel,
    mostPlayedGames,
    bestGames,
    positionDistribution,
    winRate,
    highestRank,
    totalGames: matchResults.value.length,
  };
});

async function fetchLeagueMemberships(): Promise<void> {
  const profileId = user.value?.profile_id;
  if (!profileId) return;
  try {
    // We try to fetch leagues where this profile is a member
    const { data } = await api.get('league/leagues/', {
      params: { members__profile: profileId },
    });
    leagueMemberships.value = Array.isArray(data) ? data : data.results || [];
  } catch (err: any) {
    console.error('Failed to fetch league memberships:', err);
    leagueMemberships.value = [];
  }
}
</script>
