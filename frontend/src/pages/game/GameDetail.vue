<template>
  <div v-if="isLoading" class="flex flex-center">
    <q-spinner-puff color="accent"/>
  </div>
  <div v-else>
    <div class="text-h6">
      {{ game.name }}
    </div>
    <div class="text-h8"> {{platform.name}}</div>
    <div class="column">
      <div class="row">
        <overview-card v-for="option in options" :key="option.id" class="col-3">
          <template #cardHeader>
            {{ option.name }}
          </template>
          <template #cardBody>
            <div v-if="option.has_choices">
              <div class="text-bold">Auswahl</div>
              <q-separator/>
              <ul v-for="choice of option.choices" :key="JSON.stringify(choice)">
                <li>{{ choice.name }}</li>
              </ul>
            </div>
            <div v-else class="flex-center flex"> An/Aus Option</div>
          </template>
        </overview-card>
      </div>
      <overview-card>
        <template #cardHeader>
         Ergebniskonfiguration
        </template>
        <template #cardBody>

          <div class="row">
            <div class="col-7 q-gutter-sm">
              <div>Spiel mit Punkten:</div>
              <div>Startpunkte:</div>
              <div>StartspielerInreihenfolge</div>
              <div>Asymmetrisch</div>
              <div flat v-if="resultConfig.is_asymmetric">
                Factions
              </div>
              <div> Tie Breaker </div>
            </div>
            <div class="col-5 q-gutter-sm">
              <YesNoItem :yes="resultConfig.has_points" />
              <div> {{ startingPointSystem.code }} <span
                class="text-italic">{{ startingPointSystem.description }} </span></div>
              <YesNoItem :yes="resultConfig.has_starting_player_order" />
              <YesNoItem :yes="resultConfig.is_asymmetric" />
              <div  v-if="resultConfig.is_asymmetric">
                <div v-for="faction of factions" :key="faction.id" class="inline-block q-mx-xs">
                  {{ faction.name }}
                </div>
              </div>
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
for (const [ index, option ] of options.entries()) {
  const { data: choices } = await api(`game/option-choices/?option=${option.id}`);
  options[index]['choices'] = choices;
}
const { data: [ resultConfig ] } = await api(`game/result-configs/?game=${route.params.id}`);
const { data:  tieBreakers  } = await api(`game/tie-breakers/?game=${route.params.id}`);
const { data:  factions  } = await api(`game/factions/?game=${route.params.id}`);
const { data: platform } = await api(`game/platforms/${game.platform}`);
const { data: startingPointSystem } = await api(`game/starting-point-systems/${resultConfig.starting_points_system}`);
isLoading.value = false;


</script>
