<template>
    <q-table
      title="Yearly Standings"
      flat
      hide-bottom
      :rows="rows"
    />
</template>

<script setup lang="ts">
const rows = [
  { player: 'Player 1', win: 2 },
  { player: 'Player 2', win: 1 },
  { player: 'Player 3', win: 0 },
  { player: 'Player 4', win: 0 },
];
</script>
