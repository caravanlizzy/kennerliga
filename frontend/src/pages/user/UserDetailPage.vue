<template>
  <q-page class="q-pa-none bg-grey-1">
    <!-- User Profile Hero Section -->
    <div v-if="user" class="profile-hero bg-primary text-white q-pa-lg relative-position overflow-hidden">
      <div class="hero-content row items-center q-col-gutter-lg relative-position z-index-1">
        <div class="col-12 col-md-auto flex justify-center">
          <div class="avatar-container shadow-10 rounded-borders bg-white q-pa-xs">
            <UserAvatar
              :display-username="user.username"
              size="96px"
              shape="rounded"
            />
          </div>
        </div>
        <div class="col-12 col-md column items-start text-center-mobile">
          <div class="row items-center q-gutter-x-md full-width-mobile justify-center-mobile">
            <h1 class="text-h3 text-weight-bolder q-ma-none tracking-tighter">{{ user.username }}</h1>
            <q-badge v-if="user.admin" color="amber-8" class="text-dark text-weight-bold q-px-sm" label="ADMIN" />
          </div>
          <div v-if="user.profile?.name" class="text-h6 text-white-80 text-weight-light q-mt-xs">
            {{ user.profile.name }}
          </div>
          <div class="row q-gutter-x-lg q-mt-md full-width-mobile justify-center-mobile">
            <div class="column items-center">
              <div class="text-h4 text-weight-bolder">{{ leagueStats.totalLeagues }}</div>
              <div class="text-caption text-uppercase letter-spacing-1 text-white-60">Leagues</div>
            </div>
            <div class="separator-vertical" />
            <div class="column items-center">
              <div class="text-h4 text-weight-bolder">{{ gameStats.length }}</div>
              <div class="text-caption text-uppercase letter-spacing-1 text-white-60">Games</div>
            </div>
          </div>
        </div>
        <div class="absolute-top-right q-pa-md z-index-2">
          <KennerButton
            flat
            round
            icon="refresh"
            color="white"
            @click="reload"
            :loading="loading"
          />
        </div>
      </div>
      <!-- Decorative background elements -->
      <div class="hero-bg-overlay absolute-full" />
      <q-icon name="person" class="hero-watermark absolute-bottom-right text-white" size="200px" />
    </div>

    <div v-if="loading" class="flex justify-center q-my-xl">
      <LoadingSpinner />
    </div>

    <div v-else-if="user" class="q-px-md q-py-lg max-width-container mx-auto">
      <div class="row q-col-gutter-lg">
        <!-- Sidebar: Standings Distribution -->
        <div class="col-12 col-md-4">
          <q-card flat bordered class="rounded-borders sticky-top overflow-hidden">
            <q-card-section class="bg-grey-2 text-weight-bold text-uppercase letter-spacing-1 text-grey-8">
              Standings Distribution
            </q-card-section>
            <q-card-section class="q-pa-md">
              <div class="column q-gutter-y-md">
                <div v-for="pos in [1, 2, 3, 4]" :key="pos" class="distribution-row row items-center q-col-gutter-sm">
                  <div class="col-2 text-weight-bold text-grey-7">{{ pos }}{{ getOrdinal(pos) }}</div>
                  <div class="col">
                    <q-linear-progress
                      :value="(leagueStats.distribution[pos]?.percentage || 0) / 100"
                      size="12px"
                      :color="getPosColor(pos)"
                      track-color="grey-3"
                      class="rounded-borders"
                    />
                  </div>
                  <div class="col-3 text-right">
                    <div class="text-weight-bolder" :class="getPosColorClass(pos)">
                      {{ (leagueStats.distribution[pos]?.percentage || 0).toFixed(0) }}%
                    </div>
                    <div class="text-caption text-grey-5">{{ leagueStats.distribution[pos]?.count || 0 }}x</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Recent Seasons in Sidebar -->
          <q-card flat bordered class="rounded-borders q-mt-lg overflow-hidden">
            <q-card-section class="bg-grey-2 text-weight-bold text-uppercase letter-spacing-1 text-grey-8">
              Recent Seasons
            </q-card-section>
            <q-list separator>
              <q-item
                v-for="sp in userSeasonList.slice(0, 5)"
                :key="sp.id"
                clickable
                v-ripple
                @click="router.push({ name: 'season-overview', params: { id: sp.season } })"
              >
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ sp.season_details?.name || `Season ${sp.season}` }}</q-item-label>
                  <q-item-label caption v-if="sp.rank">League {{ sp.rank }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-badge
                    :color="getPosBadgeColor(sp.position || 0)"
                    class="text-weight-bold"
                  >
                    #{{ sp.position || '-' }}
                  </q-badge>
                </q-item-section>
              </q-item>
              <q-item v-if="userSeasonList.length === 0">
                <q-item-section class="text-grey-6 italic text-center">No seasons joined yet</q-item-section>
              </q-item>
            </q-list>
          </q-card>
        </div>

        <!-- Main Content -->
        <div class="col-12 col-md-8">
          <!-- Top Games Highlight -->
          <div v-if="topGames.length > 0" class="q-mb-xl">
            <div class="row items-center q-mb-md">
              <q-icon name="emoji_events" color="amber-8" size="24px" class="q-mr-sm" />
              <div class="text-h5 text-weight-bolder text-dark tracking-tighter">Top 3 Performing Games</div>
            </div>
            <div class="row q-col-gutter-md">
              <div v-for="(game, idx) in topGames" :key="'top-'+game.name" class="col-12 col-sm-4">
                <q-card flat class="top-game-card relative-position transition-all overflow-hidden" :class="`rank-${idx+1}`">
                  <div class="rank-badge absolute-top-left q-pa-sm text-white text-weight-bolder">
                    #{{ idx + 1 }}
                  </div>
                  <q-card-section class="q-pt-xl q-pb-md text-center">
                    <div class="text-subtitle1 text-weight-bolder text-dark ellipsis q-mb-sm">{{ game.name }}</div>
                    <div class="row justify-center q-gutter-x-md">
                      <div class="column">
                        <div class="text-h5 text-weight-bolder text-positive">{{ game.winRate.toFixed(0) }}%</div>
                        <div class="text-caption text-grey-7 uppercase" style="font-size: 0.6rem">Winrate</div>
                      </div>
                      <div class="separator-vertical-dark" />
                      <div class="column">
                        <div class="text-h5 text-weight-bolder text-primary">#{{ game.avgPos.toFixed(1) }}</div>
                        <div class="text-caption text-grey-7 uppercase" style="font-size: 0.6rem">Avg Pos</div>
                      </div>
                    </div>
                  </q-card-section>
                  <div class="card-footer-accent" :class="`bg-rank-${idx+1}`" />
                </q-card>
              </div>
            </div>
          </div>

          <!-- All Games Statistics -->
          <div>
            <div class="row items-center justify-between q-mb-md">
              <div class="row items-center">
                <q-icon name="videogame_asset" color="indigo-7" size="24px" class="q-mr-sm" />
                <div class="text-h5 text-weight-bolder text-dark tracking-tighter">Game Statistics</div>
              </div>
              <div style="min-width: 200px">
                <q-input
                  v-model="gameSearch"
                  outlined
                  dense
                  rounded
                  placeholder="Search games..."
                  class="bg-white"
                >
                  <template #append>
                    <q-icon name="search" size="xs" />
                  </template>
                </q-input>
              </div>
            </div>

            <div v-if="filteredGameStats.length === 0" class="text-center q-pa-xl text-grey-5 bg-white rounded-borders border-dashed border-grey-4">
              <q-icon name="sports_esports" size="48px" class="q-mb-sm opacity-20" />
              <div class="text-h6 text-weight-light">No games found</div>
              <div class="text-caption">Try a different search term</div>
            </div>

            <div v-else class="row q-col-gutter-md">
              <div v-for="game in filteredGameStats" :key="game.name" class="col-12 col-sm-6">
                <q-card flat bordered class="game-stat-card hover-lift transition-all">
                  <q-card-section>
                    <div class="text-subtitle1 text-weight-bold text-dark ellipsis q-mb-sm">{{ game.name }}</div>
                    <div class="row items-center justify-between">
                      <div class="column">
                        <div class="text-h6 text-weight-bolder text-positive">{{ game.winRate.toFixed(0) }}%</div>
                        <div class="text-caption text-grey-6 uppercase letter-spacing-1" style="font-size: 0.6rem">Win Rate</div>
                      </div>
                      <div class="column items-end">
                        <div class="text-h6 text-weight-bolder text-primary">#{{ game.avgPos.toFixed(1) }}</div>
                        <div class="text-caption text-grey-6 uppercase letter-spacing-1" style="font-size: 0.6rem">Avg Pos</div>
                      </div>
                    </div>
                    <div class="q-mt-md">
                      <div class="text-caption text-grey-6 q-mb-xs text-weight-bold uppercase" style="font-size: 0.6rem">Recent Results</div>
                      <div class="row q-gutter-xs">
                        <q-badge
                          v-for="(p, idx) in game.positions.slice(-5).reverse()"
                          :key="idx"
                          :color="getPosBadgeColor(p)"
                          class="text-weight-bold result-badge"
                        >
                          {{ p }}
                        </q-badge>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>
        </div>
      </div>
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
const topGames = ref<any[]>([]);

async function load() {
  loading.value = true;
  user.value = null;
  userSeasonList.value = [];
  const username = String(route.params.username || '');
  try {
    const { data: usersResponse } = await api.get('user/users/', {
      params: { username }
    });

    let foundUser: TUserDto | null = null;
    const users = Array.isArray(usersResponse) ? usersResponse : usersResponse.results || [];
    foundUser = users.find((u: TUserDto) => u.username.toLowerCase() === username.toLowerCase()) || null;

    if (foundUser) {
      user.value = foundUser;
      const profileId = foundUser.profile?.id || foundUser.profile_id;

      if (profileId) {
        const [seasonsRes, statsRes] = await Promise.all([
          api.get('season/season-participants/', { params: { profile: profileId } }),
          api.get(`user/users/${foundUser.id}/statistics/`)
        ]);

        const participants: TSeasonParticipantDto[] = Array.isArray(seasonsRes.data) ? seasonsRes.data : seasonsRes.data.results || [];
        leagueStats.value = statsRes.data.league_stats;
        gameStats.value = statsRes.data.game_stats;
        topGames.value = statsRes.data.top_games || [];

        const seasonIds = [...new Set(participants.map(p => p.season))];
        const seasonsData = await Promise.all(seasonIds.map(id => api.get(`season/seasons/${id}/`)));
        const seasonsMap: Record<number, TSeasonDto> = {};
        seasonsData.forEach(res => {
          if (res.data) seasonsMap[res.data.id] = res.data;
        });

        userSeasonList.value = participants.map(p => ({
          ...p,
          season_details: seasonsMap[p.season]
        })).sort((a, b) => (b.season_details?.id || 0) - (a.season_details?.id || 0));
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

function getPosColor(pos: number) {
  switch (pos) {
    case 1: return 'amber-8';
    case 2: return 'blue-grey-4';
    case 3: return 'orange-9';
    case 4: return 'brown-5';
    default: return 'grey-6';
  }
}

function getPosColorClass(pos: number) {
  return `text-${getPosColor(pos)}`;
}

function getPosBadgeColor(pos: number) {
  return getPosColor(pos);
}

onMounted(load);
</script>

<style scoped lang="scss">
.profile-hero {
  min-height: 250px;
  background: linear-gradient(135deg, var(--q-primary) 0%, darken(#2d3436, 10%) 100%);
}

.hero-bg-overlay {
  background-image: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%);
  pointer-events: none;
}

.hero-watermark {
  opacity: 0.05;
  right: -50px;
  bottom: -50px;
  pointer-events: none;
}

.avatar-container {
  border-radius: 20px;
  transform: rotate(-3deg);
  transition: transform 0.3s ease;
  &:hover {
    transform: rotate(0deg) scale(1.05);
  }
}

.text-white-80 { color: rgba(255,255,255,0.8); }
.text-white-60 { color: rgba(255,255,255,0.6); }

.separator-vertical {
  width: 1px;
  height: 40px;
  background: rgba(255,255,255,0.2);
}

.separator-vertical-dark {
  width: 1px;
  height: 30px;
  background: rgba(0,0,0,0.05);
}

.max-width-container {
  max-width: 1200px;
}

.mx-auto {
  margin-left: auto;
  margin-right: auto;
}

.sticky-top {
  position: sticky;
  top: 20px;
  z-index: 10;
}

.tracking-tighter { letter-spacing: -1px; }
.letter-spacing-1 { letter-spacing: 1px; }

.distribution-row {
  &:hover {
    background: rgba(0,0,0,0.02);
  }
}

.top-game-card {
  border-radius: 16px;
  background: white;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid rgba(0,0,0,0.03);

  &.rank-1 { border-top: 4px solid #ffc107; }
  &.rank-2 { border-top: 4px solid #b0bec5; }
  &.rank-3 { border-top: 4px solid #ff9800; }

  .rank-badge {
    border-bottom-right-radius: 12px;
    font-size: 0.9rem;
  }
  &.rank-1 .rank-badge { background: #ffc107; color: #000; }
  &.rank-2 .rank-badge { background: #b0bec5; }
  &.rank-3 .rank-badge { background: #ff9800; }
}

.bg-rank-1 { background: #ffc107; }
.bg-rank-2 { background: #b0bec5; }
.bg-rank-3 { background: #ff9800; }

.card-footer-accent {
  height: 4px;
  width: 100%;
}

.game-stat-card {
  border-radius: 12px;
  &:hover {
    border-color: var(--q-primary);
  }
}

.result-badge {
  border-radius: 4px;
  padding: 2px 6px;
}

.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  }
}

@media (max-width: 599px) {
  .text-center-mobile { text-align: center; }
  .full-width-mobile { width: 100%; }
  .justify-center-mobile { justify-content: center; }
  .profile-hero { padding: 32px 16px !important; min-height: 200px; }
}

.z-index-1 { z-index: 1; }
.z-index-2 { z-index: 2; }
</style>
