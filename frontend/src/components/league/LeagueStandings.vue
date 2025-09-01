<template>
  <div>
    <q-table
      flat
      :rows="rows"
      :columns="columns"
      row-key="id"
      hide-bottom
    />
  </div>
</template>

<script setup lang="ts">
import { QTableProps } from 'quasar'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useLeagueStore } from 'stores/leagueStore'

const { matchResultsByGame, membersById } = storeToRefs(useLeagueStore())

// compute league standings
const rows = computed(() => {
  const standings: Record<number, { id: number; league_player: string; league_points: number; wins: number }> = {}

  // iterate each game
  for (const gameId in matchResultsByGame.value) {
    const results = [...(matchResultsByGame.value[gameId] ?? [])]

    if (results.length === 0) continue

    // sort by raw points (descending)
    results.sort((a, b) => (b.points ?? -9999) - (a.points ?? -9999))

    // assign league points by placement
    const placementPoints = [6, 3, 1, 0]
    results.forEach((res, idx) => {
      const member = membersById.value[res.player_profile]
      const username = member?.username ?? `#${res.player_profile}`

      if (!standings[res.player_profile]) {
        standings[res.player_profile] = {
          id: res.player_profile,
          league_player: username,
          league_points: 0,
          wins: 0
        }
      }

      standings[res.player_profile].league_points += placementPoints[idx] ?? 0
      if (idx === 0) standings[res.player_profile].wins += 1
    })
  }

  return Object.values(standings).sort((a, b) => {
    if (b.league_points !== a.league_points) {
      return b.league_points - a.league_points
    }
    return b.wins - a.wins
  })
})

const columns: QTableProps['columns'] = [
  {
    name: 'league_player',
    label: 'Player',
    field: 'league_player',
    align: 'center'
  },
  {
    name: 'league_points',
    label: 'League Points',
    field: 'league_points',
    align: 'center'
  },
  {
    name: 'wins',
    label: 'Wins',
    field: 'wins',
    align: 'center'
  }
]
</script>
