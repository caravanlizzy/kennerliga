<template>
  <q-table
    :title="isMobile ? '' : 'League Standings'"
    flat
    :rows="rows"
    :columns="columns"
    row-key="player_profile"
    hide-bottom
    class="bg-transparent"
    :loading="loading"
  />
</template>

<script setup lang="ts">
import { QTableProps } from 'quasar';
import { storeToRefs } from 'pinia';
import { computed, ref, onMounted } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';
import { useUserStore } from 'stores/userStore';
import { api } from 'boot/axios';
import { formatNumbers } from 'src/helpers';
import { useResponsive } from 'src/composables/responsive';

const { user } = storeToRefs(useUserStore());
const myLeagueStore = useLeagueStore(user.value.myCurrentLeagueId)();
const { leagueId } = storeToRefs(myLeagueStore);
const { isMobile } = useResponsive();

interface LeagueStanding {
  player_profile: number;
  profile_name: string;
  wins: number;
  league_points: number;
}

const standings = ref<LeagueStanding[]>([]);
const loading = ref(false);

const fetchStandings = async () => {
  if (!leagueId.value) return;
  loading.value = true;
  try {
    const { data } = await api.get<LeagueStanding[]>(
      `league/leagues/${leagueId.value}/standings/`
    );
    standings.value = data;
  } catch (e) {
    console.error('Error fetching standings:', e);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchStandings);

formatNumbers()
const rows = computed(() => {
  return [...standings.value].sort((a, b) => {
    if (b.league_points !== a.league_points)
      return b.league_points - a.league_points;
    if (b.wins !== a.wins) return b.wins - a.wins;
    return a.profile_name.localeCompare(b.profile_name);
  });
});

const columns: QTableProps['columns'] = [
  {
    name: 'profile_name',
    label: 'Player',
    field: 'profile_name',
    align: 'left',
  },
  {
    name: 'league_points',
    label: 'League Points',
    field: 'league_points',
    align: 'center',
    format: (val: number) => formatNumbers(val),
  },
  {
    name: 'wins',
    label: 'Wins',
    field: 'wins',
    align: 'center',
    format: (val: number) => formatNumbers(val),
  },
];
</script>
