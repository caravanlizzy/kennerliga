<template>
  <div v-if="isLoading" class="flex flex-center">
    <q-spinner-puff color="accent" />
  </div>
  <div v-else>
    <div class="text-h6">
      {{ game.name }}
    </div>
    <div class="text-h8"> {{ platform.name }}</div>
    <div class="row">
      <YesNoOptions v-if="hasYesNoOptions" :options="options" />
      <ChoiceOptions :options="options" style="min-width:200px" />
    </div>
    <ResultConfiguration
      :hasPoints="resultConfig.has_points"
      :startingPointSystem="startingPointSystem"
      :hasStartingPlayerOrder="resultConfig.has_starting_player_order"
      :isAsymmetric="resultConfig.is_asymmetric"
      :factions="factions"
      :tieBreakers="tieBreakers"
    />
  </div>


</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';
import OverviewCard from 'components/cards/OverviewCard.vue';
import { computed, ref } from 'vue';
import YesNoItem from 'components/items/YesNoItem.vue';
import ResultConfiguration from 'pages/game/gameDetail/ResultConfiguration.vue';
import YesNoOptions from 'pages/game/gameDetail/YesNoOptions.vue';
import ChoiceOptions from 'pages/game/gameDetail/ChoiceOptions.vue';

const route = useRoute();
const isLoading = ref(true);
const { data: game } = await api(`game/games/${route.params.id}`);
const { data: options } = await api(`game/options/?game=${game.id}`);
for (const [index, option] of options.entries()) {
  const { data: choices } = await api(`game/option-choices/?option=${option.id}`);
  options[index]['choices'] = choices;
}
const { data: [resultConfig] } = await api(`game/result-configs/?game=${route.params.id}`);
const { data: tieBreakers } = await api(`game/tie-breakers/?game=${route.params.id}`);
const { data: factions } = await api(`game/factions/?game=${route.params.id}`);
const { data: platform } = await api(`game/platforms/${game.platform}`);
const { data: startingPointSystem } = await api(`game/starting-point-systems/${resultConfig.starting_points_system}`);
isLoading.value = false;

const hasYesNoOptions = computed(() => {
  let count = 0;
  for (const option of options) {
    if (!option.has_choices) return true;
  }
  return false;
});


</script>
