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
        <template v-for="option in options" :key="option.id">
          <overview-card v-if="option.has_choices" >
            <template #cardHeader>
              {{ option.name }}
            </template>
            <template #cardBody>
              <div class="text-bold">Auswahl</div>
              <q-separator />
              <ul v-for="choice of option.choices" :key="JSON.stringify(choice)">
                <li>{{ choice.name }}</li>
              </ul>
            </template>
          </overview-card>
        </template>
      </div>
      <overview-card style="max-width: 500px">
        <template #cardHeader>
          Ergebniskonfiguration
        </template>
        <template #cardBody>
          <div class="q-gutter-sm">
            <div class="row justify-between">
              <div>Spiel mit Punkten:</div>
              <YesNoItem :yes="resultConfig.has_points" />
            </div>

            <div class="row justify-between">
              <div>Startpunkte:</div>
              <div> {{ startingPointSystem.code }} <span
                class="text-italic">{{ startingPointSystem.description }} </span></div>
            </div>
            <div class="row justify-between">
              <div>StartspielerInreihenfolge</div>
              <YesNoItem :yes="resultConfig.has_starting_player_order" />
            </div>
            <div class="col">
              <div class="row justify-between">
                <div>Asymmetrisch</div>
                <YesNoItem :yes="resultConfig.is_asymmetric" />
              </div>
              <div class="row justify-between q-ml-lg">
                <div flat v-if="resultConfig.is_asymmetric">
                  Factions
                </div>
                <div v-if="resultConfig.is_asymmetric">
                  <div v-for="faction of factions" :key="faction.id" class="inline-block q-mx-xs">
                    {{ faction.name }}
                  </div>
                </div>
              </div>
            </div>
            <div class="row justify-between">
              <div> Tie Breaker</div>
              <div>
                <template v-if="tieBreakers.length > 0">
                  <div v-for="(tieBreaker, index) in tieBreakers" :key="tieBreaker.order">
                    {{ index + 1 }}. {{ tieBreaker.name }}
                  </div>
                </template>
                <template v-else>
                  Keine
                </template>
              </div>
            </div>
          </div>
        </template>
      </overview-card>
  </div>


</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';
import OverviewCard from 'components/cards/OverviewCard.vue';
import { ref } from 'vue';
import YesNoItem from 'components/items/YesNoItem.vue';

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


</script>
