<template>
  <div class="text-h6 q-my-md">
    List of Leagues with their members, games and results
  </div>
  <div
    v-for="league of leagues"
    :key="league.id"
    class="q-pa-md q-mb-md bg-grey-2 rounded-borders"
  >
    <div class="text-h5 q-mb-md">L{{ league.level }}</div>
    <div class="text-subtitle1 q-mb-sm">Members</div>
    <div class="q-gutter-y-sm">
      <div
        v-for="member of league.members"
        :key="member.id"
        class="q-pa-sm bg-white rounded-borders"
      >
        <div class="text-weight-medium">{{ member.username }}</div>
        <div class="text-grey-8">
          Game: {{ member.selected_game.game_name }}
        </div>
        <div v-if="member.banned_selected_game" class="text-grey-8">
          Banned Game: {{ member.banned_selected_game.game_name }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { onMounted, Ref, ref } from 'vue';
import { getLeageDetailsBySeason } from 'src/services/seasonService';

const route = useRoute();
const seasonId = parseInt(route.params.id as string);

const leagues: Ref<any> = ref();
onMounted(async () => {
  leagues.value = await getLeageDetailsBySeason(seasonId);
});
</script>
