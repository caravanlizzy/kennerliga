<template>
  <div>List of Leagues with their members, games and results</div>
  {{ leagues }}
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { onMounted, Ref, ref } from 'vue';
import { getLeaguesBySeason } from 'src/services/seasonService';

const route = useRoute();
const seasonId = parseInt(route.params.id as string);

const leagues: Ref<any> = ref();
onMounted(async () => {
  leagues.value = await getLeaguesBySeason(seasonId);
});
</script>
