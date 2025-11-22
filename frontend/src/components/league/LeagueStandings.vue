<template>
    <q-table
      title="League Standings"
      flat
      :rows="rows"
      :columns="columns"
      row-key="id"
      hide-bottom
      class="bg-transparent"
    />
</template>

<script setup lang="ts">
import { QTableProps } from 'quasar';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';
import { useLeagueStore } from 'stores/leagueStore';

const { matchResultsBySelectedGame, membersById } = storeToRefs(useLeagueStore());

// compute league standings
const rows = computed(() => {
  // 1) Seed every member with zeros so they always show up
  const standings: Record<
    number,
    { id: number; league_player: string; league_points: number; wins: number }
  > = {};

  for (const idStr in membersById.value) {
    const id = Number(idStr);
    const m = membersById.value[id];
    standings[id] = {
      id,
      league_player: m?.username ?? `#${id}`,
      league_points: 0,
      wins: 0,
    };
  }

  // 2) Aggregate league points & wins from finished games
  const placementPoints = [6, 3, 1, 0]; // extend/adjust if needed
  for (const gameId in matchResultsBySelectedGame.value) {
    const results = [...(matchResultsBySelectedGame.value[gameId] ?? [])];
    if (results.length === 0) continue;

    // Sort by raw points desc; null/undefined sink to bottom
    results.sort((a, b) => (b.points ?? -Infinity) - (a.points ?? -Infinity));

    results.forEach((res, idx) => {
      const pid = res.player_profile;
      if (!(pid in standings)) {
        // fallback in case a result references a non-member (shouldn't happen)
        standings[pid] = {
          id: pid,
          league_player: membersById.value[pid]?.username ?? `#${pid}`,
          league_points: 0,
          wins: 0,
        };
      }
      standings[pid].league_points += placementPoints[idx] ?? 0;
      if (idx === 0) standings[pid].wins += 1;
    });
  }

  // 3) Sort: league points desc, then wins desc, then name asc
  return Object.values(standings).sort((a, b) => {
    if (b.league_points !== a.league_points)
      return b.league_points - a.league_points;
    if (b.wins !== a.wins) return b.wins - a.wins;
    return a.league_player.localeCompare(b.league_player);
  });
});

const columns: QTableProps['columns'] = [
  {
    name: 'league_player',
    label: 'Player',
    field: 'league_player',
    align: 'left',
  },
  {
    name: 'league_points',
    label: 'League Points',
    field: 'league_points',
    align: 'center',
  },
  {
    name: 'wins',
    label: 'Wins',
    field: 'wins',
    align: 'center',
  },
];
</script>
