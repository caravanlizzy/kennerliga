<template>
  <OverviewCard>
    <template #title>
      An/Aus Optionen
    </template>
    <template #content>
      <ul v-for="option of options" :key="option.id">
        <li v-if="option.has_choices">
          {{ option.name }}
        </li>
      </ul>
    </template>
  </OverviewCard>
</template>

<script setup lang="ts">
import OverviewCard from 'components/cards/OverviewCard.vue';
import { GameOptionDto } from 'src/models/gameModels';
defineProps<{
  options: GameOptionDto[];
}>()
</script>

<style scoped>

</style>
