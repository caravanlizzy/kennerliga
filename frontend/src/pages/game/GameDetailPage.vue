<template>
  <div v-if="isLoading" class="flex flex-center">
    <q-spinner-puff color="accent" />
  </div>
  <div v-else>
    <div class="text-h4 text-primary">
      {{ game.name }}
    </div>
    <div class="text-h8"> {{ platform.name }}</div>

    <!-- KennerGrid rendering all items, including ResultConfiguration -->
    <KennerGrid :items="completeOptions" class="q-mt-md">
      <template v-slot:default="{ item }">
        <div  >
          <!-- Check if it's the ResultConfiguration component -->
          <div v-if="item.isResultConfig">
            <ResultConfiguration
              :isHighlighed="true"
              :hasPoints="resultConfig.has_points"
              :startingPointSystem="startingPointSystem"
              :hasStartingPlayerOrder="resultConfig.has_starting_player_order"
              :isAsymmetric="resultConfig.is_asymmetric"
              :factions="factions"
              :tieBreakers="tieBreakers"
            />
          </div>
          <!-- Otherwise, render regular option -->
          <div v-else>
            <div class="text-h6 text-secondary">
              {{ item.name }}
            </div>
            <ul v-for="choice of item.choices" :key="JSON.stringify(choice)">
              <li>{{ choice.name }}</li>
            </ul>
          </div>
        </div>
      </template>
    </KennerGrid>
  </div>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';
import ResultConfiguration from 'components/game/ResultConfiguration.vue';
import KennerGrid from 'components/grid/KennerGrid.vue';
import { computed, ref } from 'vue';

const route = useRoute();
const isLoading = ref(true);

const { data: game } = await api(`game/games-full/${route.params.id}`);

const { data: [resultConfig] } = await api(`game/result-configs/?game=${route.params.id}`);
const { data: tieBreakers } = await api(`game/tie-breakers/?result_config=${resultConfig.id}`);
const { data: factions } = await api(`game/factions/?game=${route.params.id}`);
const { data: platform } = await api(`game/platforms/${game.platform}`);
const { data: startingPointSystem } = await api(`game/starting-point-systems/${resultConfig.starting_points_system}`);
isLoading.value = false;

// Filter yesNoOptions (those without choices)
// const yesNoOptions = computed(() => options.filter(option => !option.has_choices));
const yesNoOptions = computed(() => game.options.filter(option => !option.has_choices));

// Create "An-/Aus Option" with all yesNoOption names as choices
const anAusOption = computed(() => ({
  name: 'An-/Aus Optionen', // Name for the new option
  has_choices: true,        // Set to true since we are adding choices
  choices: yesNoOptions.value.map(option => ({ name: option.name })) // Map option names to choices
}));

// Filter the choiceOptions (those with existing choices)
const choiceOptions = computed(() => game.options.filter(option => option.has_choices));

// Add the ResultConfiguration as an item in the grid
const resultConfigItem = computed(() => ({
  isResultConfig: true,
  isHighlighted: true
}));

// Combine "An-/Aus Option" with choiceOptions and ResultConfiguration
const completeOptions = computed(() => [
  anAusOption.value,
  ...choiceOptions.value,
  resultConfigItem.value // Add ResultConfiguration as the last grid item
]);

</script>
