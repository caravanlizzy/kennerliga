<template>
    <q-table flat>{{columns}}</q-table>
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
