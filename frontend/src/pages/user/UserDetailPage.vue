<template>
  <q-page class="q-pa-md bg-grey-1">
    <!-- User Header -->
    <div v-if="user" class="row items-center justify-between q-mb-lg bg-white q-pa-md rounded-borders shadow-sm">
      <div class="row items-center q-gutter-x-md">
        <UserAvatar
          :display-username="user.username"
          size="64px"
          shape="circle"
        />
        <div class="column">
          <div class="text-h4 text-weight-bolder text-dark tracking-tighter line-height-1">
            {{ user.username }}
          </div>
          <div v-if="user.profile?.name" class="text-subtitle2 text-grey-6">
            {{ user.profile.name }}
          </div>
        </div>
      </div>
      <KennerButton
        flat
        round
        icon="refresh"
        color="primary"
        @click="reload"
        :loading="loading"
      />
    </div>

    <div v-if="loading" class="flex justify-center q-my-xl">
      <LoadingSpinner />
    </div>

    <div v-else-if="user" class="column q-gutter-y-lg">
      <!-- League Statistics Section -->
      <ContentSection title="League Statistics" icon="stars" color="amber-9">
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4 text-center column justify-center">
            <div class="text-h2 text-weight-bolder text-primary">
              {{ leagueStats.totalLeagues }}
            </div>
            <div class="text-subtitle2 text-grey-7 text-uppercase letter-spacing-1">Leagues Joined</div>
          </div>
          <div class="col-12 col-md-8">
            <div class="text-subtitle2 q-mb-sm text-grey-8">Standings Distribution</div>
            <div class="row q-col-gutter-sm">
              <div v-for="pos in [1, 2, 3, 4]" :key="pos" class="col-6 col-sm-3">
                <q-card flat bordered class="text-center q-pa-sm">
                  <div class="text-caption text-weight-bold text-grey-7">{{ pos }}{{ getOrdinal(pos) }} Place</div>
                  <div class="text-h5 text-weight-bolder" :class="getPosColorClass(pos)">
                    {{ leagueStats.distribution[pos]?.percentage.toFixed(0) }}%
                  </div>
                  <div class="text-caption text-grey-5">{{ leagueStats.distribution[pos]?.count }} times</div>
                </q-card>
              </div>
            </div>
          </div>
        </div>
      </ContentSection>

      <!-- Game Search & Stats Section -->
      <ContentSection title="Game Statistics" icon="videogame_asset" color="indigo-7">
        <div class="q-mb-md">
          <q-input
            v-model="gameSearch"
            outlined
            dense
            placeholder="Search games..."
            class="bg-white"
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
        </div>

        <div v-if="filteredGameStats.length === 0" class="text-center q-pa-xl text-grey-6 bg-white rounded-borders border-subtle">
          <q-icon name="sports_esports" size="48px" class="q-mb-sm opacity-20" />
          <div>No games found matching your search.</div>
        </div>

        <div v-else class="row q-col-gutter-md">
          <div v-for="game in filteredGameStats" :key="game.name" class="col-12 col-sm-6 col-md-4">
            <q-card flat bordered class="hover-shadow transition-all">
              <q-card-section>
                <div class="text-subtitle1 text-weight-bold text-dark ellipsis">{{ game.name }}</div>
                <div class="row items-center justify-between q-mt-sm">
                  <div class="column">
                    <div class="text-caption text-grey-6 uppercase">Win Rate</div>
                    <div class="text-h6 text-weight-bolder text-positive">{{ game.winRate.toFixed(0) }}%</div>
                  </div>
                  <div class="column items-end">
                    <div class="text-caption text-grey-6 uppercase">Avg Pos</div>
                    <div class="text-h6 text-weight-bolder text-primary">#{{ game.avgPos.toFixed(1) }}</div>
                  </div>
                </div>
                <div class="q-mt-sm">
                  <div class="text-caption text-grey-6 q-mb-xs">Recent Positions</div>
                  <div class="row q-gutter-xs">
                    <q-badge
                      v-for="(p, idx) in game.positions.slice(-5).reverse()"
                      :key="idx"
                      :color="getPosBadgeColor(p)"
                      class="text-weight-bold"
                    >
                      {{ p }}
                    </q-badge>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </ContentSection>

      <!-- Seasons Participated Section -->
      <ContentSection title="Seasons Participated" icon="calendar_month" color="deep-purple-7">
        <div v-if="userSeasonList.length === 0" class="text-center q-pa-xl text-grey-6">
          No seasons found.
        </div>
        <div v-else class="row q-col-gutter-md">
          <div v-for="sp in userSeasonList" :key="sp.id" class="col-12 col-sm-6 col-md-4">
            <q-card
              flat
              bordered
              clickable
              class="hover-shadow rounded-borders"
              @click="router.push({ name: 'season-overview', params: { id: sp.season } })"
            >
              <q-card-section class="row items-center no-wrap">
                <div class="column col">
                  <div class="text-subtitle1 text-weight-bold">{{ sp.season_details?.name }}</div>
                  <div class="row items-center q-gutter-x-sm">
                    <q-badge color="grey-2" text-color="grey-9" class="text-weight-bold">
                      Pos: {{ sp.position || '-' }}
                    </q-badge>
                    <q-badge v-if="sp.rank" color="primary" class="text-weight-bold">
                      League {{ sp.rank }}
                    </q-badge>
                  </div>
                </div>
                <q-icon name="chevron_right" color="grey-4" />
              </q-card-section>
            </q-card>
          </div>
        </div>
      </ContentSection>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from 'boot/axios';
import UserAvatar from 'components/ui/UserAvatar.vue';
import KennerButton from 'components/base/KennerButton.vue';
import ContentSection from 'components/base/ContentSection.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { TUserDto, TSeasonParticipantDto, TMatchResultDto, TSeasonDto } from 'src/types';

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const user = ref<TUserDto | null>(null);
const userSeasonList = ref<(TSeasonParticipantDto & { season_details?: TSeasonDto })[]>([]);
const matchResults = ref<TMatchResultDto[]>([]);
const gameSearch = ref('');

async function load() {
  loading.value = true;
  const username = route.params.username;
  try {
    // 1. Fetch the User object by username
    const { data: usersResponse } = await api.get('user/users/', {
      params: { username }
    });

    let foundUser: TUserDto | null = null;
    if (Array.isArray(usersResponse) && usersResponse.length > 0) {
      foundUser = usersResponse[0];
    } else if (usersResponse.results && usersResponse.results.length > 0) {
      foundUser = usersResponse.results[0];
    }

    if (foundUser) {
      user.value = foundUser;

      // 2. Extract profile ID from user object
      const profileId = foundUser.profile_id || foundUser.profile?.id;

      if (profileId) {
        const [seasonsRes, resultsRes] = await Promise.all([
          api.get('season/season-participants/', { params: { profile: profileId } }),
          api.get('result/results/', { params: { player_profile: profileId } })
        ]);
        userSeasonList.value = Array.isArray(seasonsRes.data) ? seasonsRes.data : seasonsRes.data.results || [];
        matchResults.value = Array.isArray(resultsRes.data) ? resultsRes.data : resultsRes.data.results || [];
      }
    }
  } catch (err) {
    console.error('Failed to load user details:', err);
  } finally {
    loading.value = false;
  }
}

function reload() {
  load();
}

const leagueStats = computed(() => {
  const totalLeagues = userSeasonList.value.length;
  const distribution: Record<number, { count: number; percentage: number }> = {};

  [1, 2, 3, 4].forEach(pos => {
    const count = userSeasonList.value.filter(sp => sp.position === pos).length;
    distribution[pos] = {
      count,
      percentage: totalLeagues ? (count / totalLeagues) * 100 : 0
    };
  });

  return {
    totalLeagues,
    distribution
  };
});

const gameStats = computed(() => {
  const statsMap: Record<string, { name: string; positions: number[]; wins: number }> = {};

  matchResults.value.forEach(r => {
    const gameName = r.game_name || `Game ${r.selected_game}`;
    if (!statsMap[gameName]) {
      statsMap[gameName] = { name: gameName, positions: [], wins: 0 };
    }
    if (r.position !== null) {
      statsMap[gameName].positions.push(r.position);
      if (r.position === 1) statsMap[gameName].wins++;
    }
  });

  return Object.values(statsMap).map(g => ({
    ...g,
    winRate: g.positions.length ? (g.wins / g.positions.length) * 100 : 0,
    avgPos: g.positions.length ? g.positions.reduce((a, b) => a + b, 0) / g.positions.length : 0,
    count: g.positions.length
  })).sort((a, b) => b.count - a.count);
});

const filteredGameStats = computed(() => {
  if (!gameSearch.value) return gameStats.value;
  const search = gameSearch.value.toLowerCase();
  return gameStats.value.filter(g => g.name.toLowerCase().includes(search));
});

function getOrdinal(n: number) {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return s[(v - 20) % 10] || s[v] || s[0];
}

function getPosColorClass(pos: number) {
  switch (pos) {
    case 1: return 'text-amber-8';
    case 2: return 'text-blue-grey-4';
    case 3: return 'text-orange-9';
    case 4: return 'text-brown-5';
    default: return 'text-grey-7';
  }
}

function getPosBadgeColor(pos: number) {
  switch (pos) {
    case 1: return 'amber-8';
    case 2: return 'blue-grey-4';
    case 3: return 'orange-8';
    case 4: return 'brown-5';
    default: return 'grey-5';
  }
}

onMounted(load);
</script>

<style scoped lang="scss">
.line-height-1 {
  line-height: 1;
}
.letter-spacing-1 {
  letter-spacing: 1px;
}
.hover-shadow {
  transition: all 0.3s ease;
  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    transform: translateY(-2px);
  }
}
.border-subtle {
  border: 1px solid rgba(0,0,0,0.05);
}
.opacity-20 {
  opacity: 0.2;
}
</style>
