<template>
  <q-page class="q-pa-none user-detail-page">
    <!-- User Profile Hero Section -->
    <UserHero
      v-if="user"
      :user="user"
      :league-stats="leagueStats"
      :game-stats-count="gameStats.length"
    />
    <div v-else-if="loading" class="profile-hero-skeleton bg-primary q-pa-md">
      <div class="max-width-container q-mx-auto row items-center q-col-gutter-md">
        <div class="col-12 col-md-auto flex justify-center">
          <q-skeleton type="QAvatar" size="100px" />
        </div>
        <div class="col-12 col-md column items-center items-md-start">
          <q-skeleton type="text" width="200px" height="40px" />
          <q-skeleton type="text" width="150px" height="24px" class="q-mt-sm" />
        </div>
      </div>
    </div>

    <div v-if="loading" class="q-px-md q-py-lg max-width-container q-mx-auto">
      <div class="row q-col-gutter-lg">
        <div class="col-12 col-md-4">
          <q-skeleton type="rect" height="200px" class="q-mb-lg rounded-borders" />
          <q-skeleton type="rect" height="300px" class="rounded-borders" />
        </div>
        <div class="col-12 col-md-8">
          <q-skeleton type="rect" height="48px" class="q-mb-lg rounded-borders" />
          <div class="row q-col-gutter-md">
            <div v-for="i in 6" :key="i" class="col-12 col-sm-6 col-md-4">
              <q-skeleton type="rect" height="100px" class="rounded-borders" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="user" class="q-px-md q-py-lg max-width-container q-mx-auto">
      <div class="row q-col-gutter-lg">
        <!-- Left Column: User Summary & Actions -->
        <div class="col-12 col-md-4">
          <div class="sticky-top">
            <!-- Pick Limit Status -->
            <UserPicks
              v-model:selected-year="selectedYear"
              :picked-games="pickedGames"
              :max-game-limit="maxGameLimit"
              :available-years="availableYears"
              @update:selected-year="refreshPicks"
            />

            <!-- Overall Performance Summary -->
            <UserPerformance :overall-stats="overallStats" />
          </div>
        </div>

        <!-- Right Column: Tabs for detailed view -->
        <div class="col-12 col-md-8">
          <q-tabs
            v-model="tab"
            dense
            class="text-grey-7 surface-card q-mb-lg"
            active-color="primary"
            indicator-color="primary"
            align="justify"
            narrow-indicator
          >
            <q-tab name="games" icon="videogame_asset" label="Games" />
            <q-tab name="seasons" icon="event" label="Seasons" />
          </q-tabs>

          <q-tab-panels v-model="tab" animated class="bg-transparent">
            <!-- Games Tab -->
            <q-tab-panel name="games" class="q-pa-none">
              <UserGamesTab
                v-model:game-search="gameSearch"
                :top-games="topGames"
                :filtered-game-stats="filteredGameStats"
              />
            </q-tab-panel>

            <!-- Seasons Tab -->
            <q-tab-panel name="seasons" class="q-pa-none">
              <UserSeasonsTab :user-season-list="userSeasonList" />
            </q-tab-panel>
          </q-tab-panels>
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
import UserHero from 'components/user/UserHero.vue';
import UserPicks from 'components/user/UserPicks.vue';
import UserPerformance from 'components/user/UserPerformance.vue';
import UserGamesTab from 'components/user/UserGamesTab.vue';
import UserSeasonsTab from 'components/user/UserSeasonsTab.vue';
import KennerButton from 'components/base/KennerButton.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { TUserDto, TSeasonParticipantDto, TSeasonDto } from 'src/types';

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const user = ref<TUserDto | null>(null);
const userSeasonList = ref<(TSeasonParticipantDto & { season_details?: TSeasonDto })[]>([]);
const gameSearch = ref('');
const tab = ref('games');

const leagueStats = ref({
  totalLeagues: 0,
});
const overallStats = ref({
  total_games: 0,
  wins: 0,
  podiums: 0,
  avg_pos: 0,
  positions: {} as Record<number, number>
});
const gameStats = ref<any[]>([]);
const topGames = ref<any[]>([]);
const pickedGames = ref<any[]>([]);
const maxGameLimit = ref(2);
const selectedYear = ref(new Date().getFullYear());
const availableYears = ref<number[]>([new Date().getFullYear()]);

async function load() {
  loading.value = true;
  user.value = null;
  userSeasonList.value = [];
  const username = String(route.params.username || '');
  try {
    const { data: usersResponse } = await api.get('user/users/', {
      params: { username }
    });

    let foundUser: TUserDto | null;
    const users = Array.isArray(usersResponse) ? usersResponse : usersResponse.results || [];
    foundUser = users.find((u: TUserDto) => u.username.toLowerCase() === username.toLowerCase()) || null;

    if (foundUser) {
      user.value = foundUser;
      const profileId = foundUser.profile?.id || foundUser.profile_id;

      if (profileId) {
        const [seasonsRes, statsRes] = await Promise.all([
          api.get('season/season-participants/', { params: { profile: profileId } }),
          api.get(`user/users/${foundUser.id}/statistics/`, { params: { year: selectedYear.value } })
        ]);

        const participants: TSeasonParticipantDto[] = Array.isArray(seasonsRes.data) ? seasonsRes.data : seasonsRes.data.results || [];
        leagueStats.value = statsRes.data.league_stats;
        overallStats.value = statsRes.data.overall_stats;
        gameStats.value = statsRes.data.game_stats;
        topGames.value = statsRes.data.top_games || [];
        pickedGames.value = statsRes.data.picked_games || [];
        maxGameLimit.value = statsRes.data.max_game_limit || 2;
        availableYears.value = statsRes.data.available_years || [new Date().getFullYear()];

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

async function refreshPicks() {
  if (!user.value) return;
  try {
    const { data } = await api.get(`user/users/${user.value.id}/statistics/`, {
      params: { year: selectedYear.value }
    });
    pickedGames.value = data.picked_games || [];
  } catch (err) {
    console.error('Failed to refresh picks:', err);
  }
}


const filteredGameStats = computed(() => {
  if (!gameSearch.value) return gameStats.value;
  const search = gameSearch.value.toLowerCase();
  return gameStats.value.filter(g => g.name.toLowerCase().includes(search));
});

onMounted(load);
</script>

<style scoped lang="scss">
/* ---- Theme tokens (light defaults) ---- */
.user-detail-page {
  --page-bg: #f1f5f9;
  --surface-bg: #ffffff;
  --surface-header-bg: #f8fafc;
  --surface-header-text: rgba(15, 23, 42, 0.7);
  --surface-border: rgba(15, 23, 42, 0.12);
  --surface-border-strong: rgba(15, 23, 42, 0.2);
  --surface-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
  --stat-tile-bg: #f8fafc;
  --text-heading: #1e293b;
  --divider: rgba(15, 23, 42, 0.08);

  background: var(--page-bg);
  min-height: 100vh;
}

.profile-hero-skeleton {
  min-height: 160px;
  background: linear-gradient(135deg, var(--q-primary) 0%, #1e293b 100%);
}


/* ---- Shared surface utilities ---- */
.sticky-top {
  @media (min-width: 1024px) {
    position: sticky;
    top: 24px;
    z-index: 10;
  }
}

.surface-card {
  background: var(--surface-bg) !important;
  border: 1px solid var(--surface-border) !important;
  border-radius: 16px;
  box-shadow: var(--surface-shadow);
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--surface-border-strong) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  }
}

.surface-card-header {
  background: var(--surface-header-bg);
  color: var(--surface-header-text);
  border-bottom: 1px solid var(--divider);
}

.stat-tile {
  background: var(--stat-tile-bg);
  border: 1px solid var(--surface-border) !important;
  border-radius: 12px;
  transition: all 0.2s ease;

  &:hover {
    background: #ffffff;
    border-color: var(--q-primary) !important;
  }
}

@media (max-width: 599px) {
  .profile-hero-skeleton { padding: 16px 16px !important; min-height: 140px; }
}

.max-width-container {
  max-width: var(--kenner-max-width);
}

.empty-state {
  border: 1px dashed var(--surface-border-strong);
}

.z-index-1 { z-index: 1; }
.z-index-2 { z-index: 2; }
</style>
