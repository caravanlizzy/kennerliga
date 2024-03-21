<template>
  <div v-if="!isLoading" class="flex flex-center">
    <q-spinner-puff color="secondary" />
  </div>
  <div v-else>
    <div class="text-h6">
      {{ game.name }}
    </div>
    <div class="text-h8"> {{ game.platform }}</div>
    <div class="row">
      <game-option-card v-for="option in options" :key="option.id" class="col-3">
        <template #cardHeader>
          <span class="text-secondary">
          {{ option.name }}
          </span>
        </template>
        <template #cardBody>
          <div v-if="option.has_choices">
            <div class="text-bold">Auswahl</div>
            <q-separator />
            <ul v-for="choice of option.choices" :key="JSON.stringify(choice)">
              <li>{{ choice.name }}</li>
            </ul>
          </div>
          <div v-else class="flex-center flex"> An/Aus Option</div>
        </template>
      </game-option-card>
    </div>
  </div>


</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';
import GameOptionCard from 'components/cards/gameOptionCard.vue';
import { ref } from 'vue';

const route = useRoute();
const isLoading = ref(true);
const { data: game } = await api(`games/${route.params.id}`);
const { data: options } = await api(`game-options/?game=${game.id}`);
for (const [index, option] of options.entries()) {
  const { data: choices } = await api(`game-option-choices/?option=${option.id}`);
  options[index]['choices'] = choices;
}
isLoading.value = true;
console.log(options);


</script>

<style scoped>
</style>
