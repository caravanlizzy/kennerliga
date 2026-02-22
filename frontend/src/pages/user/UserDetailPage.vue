<template>
  <q-page class="q-pa-md bg-grey-1">
    <!-- User Header -->
    <div v-if="user" class="row items-center justify-between q-mb-lg bg-white q-pa-md rounded-borders shadow-sm">
      <div class="row items-center q-gutter-x-md">
        <UserAvatar
          :display-username="user.username"
          size="64px"
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
                  <div class="text-subtitle1 text-weight-bold">{{ sp.season_details?.name || `Season ${sp.season}` }}</div>
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

    <div v-else class="flex flex-center q-my-xl text-grey-6">
      <div class="column items-center">
        <q-icon name="person_off" size="64px" class="q-mb-md opacity-20" />
        <div class="text-h6">User not found</div>
        <KennerButton
          flat
          color="primary"
          label="Go back"
          icon="arrow_back"
          class="q-mt-md"
          @click="router.back()"
        />
      </div>
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
import { TUserDto, TSeasonParticipantDto, TSeasonDto } from 'src/types';

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const user = ref<TUserDto | null>(null);
const userSeasonList = ref<(TSeasonParticipantDto & { season_details?: TSeasonDto })[]>([]);
const gameSearch = ref('');

const leagueStats = ref({
  totalLeagues: 0,
  distribution: {} as Record<number, { count: number; percentage: number }>
});
const gameStats = ref<any[]>([]);

async function load() {
  loading.value = true;
  user.value = null;
  userSeasonList.value = [];
  const username = String(route.params.username || '');
  try {
    // 1. Fetch the User object by username
    const { data: usersResponse } = await api.get('user/users/', {
      params: { username }
    });

    let foundUser: TUserDto | null = null;
    const users = Array.isArray(usersResponse) ? usersResponse : usersResponse.results || [];
    foundUser = users.find((u: TUserDto) => u.username.toLowerCase() === username.toLowerCase()) || null;

    if (foundUser) {
      user.value = foundUser;

      // 2. Extract profile ID from user object
      const profileId = foundUser.profile?.id || foundUser.profile_id;

      if (profileId) {
        // Fetch seasons and statistics in parallel
        const [seasonsRes, statsRes] = await Promise.all([
          api.get('season/season-participants/', { params: { profile: profileId } }),
          api.get(`user/users/${foundUser.id}/statistics/`)
        ]);

        const participants: TSeasonParticipantDto[] = Array.isArray(seasonsRes.data) ? seasonsRes.data : seasonsRes.data.results || [];

        // Map backend statistics
        leagueStats.value = statsRes.data.league_stats;
        gameStats.value = statsRes.data.game_stats;

        // 3. Fetch season details for each participant entry to get the season name
        const seasonIds = [...new Set(participants.map(p => p.season))];
        const seasonsData = await Promise.all(seasonIds.map(id => api.get(`season/seasons/${id}/`)));
        const seasonsMap: Record<number, TSeasonDto> = {};
        seasonsData.forEach(res => {
          if (res.data) seasonsMap[res.data.id] = res.data;
        });

        userSeasonList.value = participants.map(p => ({
          ...p,
          season_details: seasonsMap[p.season]
        }));
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
    background-color: #f8f9fa !important;
    border-color: var(--q-primary) !important;
  }
}
.border-subtle {
  border: 1px solid rgba(0,0,0,0.05);
}
.opacity-20 {
  opacity: 0.2;
}
</style>
