<template>
  <div>Results</div>
  <MatchResult
    v-for="selectedGameId of selectedGameIds"
    :key="selectedGameId"
    :selectedGameId="selectedGameId"
  />
</template>

<script setup lang="ts">
import MatchResult from 'components/league/MatchResult.vue';

defineProps<{ selectedGameIds: number[] }>();
</script>
