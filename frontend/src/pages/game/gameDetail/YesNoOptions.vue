<template>
  <overview-card>
    <template #cardHeader>
      An/Aus Optionen
    </template>
    <template #cardBody>
      <ul v-for="option of options" :key="option.id">
        <li v-if="option.has_choices">
          {{ option.name }}
        </li>
      </ul>
    </template>
  </overview-card>
</template>

<script setup lang="ts">
import OverviewCard from 'components/cards/OverviewCard.vue';
import { GameOptionDto, TGameOption } from 'pages/game/models';
defineProps<{
  options: GameOptionDto[];
}>()
</script>

<style scoped>

</style>
