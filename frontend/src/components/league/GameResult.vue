<template>
  <div class="q-pa-sm">
    <q-card class="result-card q-pa-md">
      <!-- Header with toggler -->
      <div class="row items-center justify-between q-mb-sm">
        <div class="text-h6">Ergebnis eintragen</div>
        <q-btn
          flat
          round
          dense
          size="sm"
          icon="expand_more"
          class="toggle-btn"
          :class="{ rotated: showForm }"
          @click="showForm = !showForm"
        />
      </div>

      <!-- Tabs on top -->
      <div class="tab-wrapper q-mb-sm">
        <q-tabs
          v-model="selectedGameId"
          :vertical="!isDesktop"
          active-color="primary"
          indicator-color="primary"
          align="left"
          narrow-indicator
          class="text-primary"
          swipeable
        >
          <q-tab
            v-for="game in uniqueSelectedGames"
            :key="game.id"
            :name="game.id"
            :label="game.game_name"
          />
        </q-tabs>
      </div>

      <!-- Form always below tabs -->
      <div v-show="showForm">
        <q-separator class="q-mb-sm" />
        <keep-alive>
          <component
            :is="ResultMatchForm"
            v-if="selectedGameId"
            :key="selectedGameId"
            :selected-game-id="selectedGameId"
            :players="getPlayersForGame(selectedGameId)"
          />
        </keep-alive>
      </div>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect } from 'vue';
import { useQuasar } from 'quasar';
import ResultMatchForm from './ResultMatchForm.vue';

const props = defineProps<{
  league: any;
}>();

const $q = useQuasar();
const showForm = ref(true);
const selectedGameId = ref<number | null>(null);

const isDesktop = computed(() => $q.screen.gt.sm);

const allMembers = computed(() => props.league?.members || []);

const uniqueSelectedGames = computed(() => {
  const seen = new Set();
  return allMembers.value
    .map((member) => member.selected_game)
    .filter((game) => game && !seen.has(game.id) && seen.add(game.id));
});

watchEffect(() => {
  if (selectedGameId.value === null && uniqueSelectedGames.value.length > 0) {
    selectedGameId.value = uniqueSelectedGames.value[0].id;
  }
});

function getPlayersForGame(gameId: number) {
  return allMembers.value
    .map((member) => ({
      id: member.id,
      username: member.username,
    }));
}
</script>

<style scoped>
.result-card {
  background: #f3f3f3;
  border-radius: 8px;
  margin: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.toggle-btn {
  transition: transform 0.2s ease;
}

.toggle-btn.rotated {
  transform: rotate(180deg);
}
</style>
