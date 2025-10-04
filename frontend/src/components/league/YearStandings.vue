<template>
  <SideAccentBox>
    <q-table flat bordered>{{columns}}</q-table>
  </SideAccentBox>
</template>

<script setup lang="ts">
import SideAccentBox from 'components/base/SideAccentBox.vue';

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
