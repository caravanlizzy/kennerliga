<template>
<div class="q-pa-lg">
  <div class="text-h6"> Wähle dein Spiel</div>
  Plattform <kenner-select :options="platforms" label="Platform"/>
</div>
</template>

<script setup lang="ts">
import KennerSelect from 'components/inputs/KennerSelect.vue';
import { api } from 'boot/axios';
const {data: platforms} = await api('game/platforms/');
</script>

<style scoped>

</style>
