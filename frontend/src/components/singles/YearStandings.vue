<template>
  <div class="q-pa-md">
    <q-table flat bordered>{{columns}}</q-table>
  </div>
</template>

<script setup lang="ts">
const columns = [
  {
    name: 'player',
    label: 'SpielerIn',
  },
  {
    name: 'win',
    label: 'wins'
  }
]
</script>
