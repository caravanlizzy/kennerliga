<template>
  <div>
    <div class="flex">
      <div>
        <q-toggle label="Assymmentrisch" :model-value="isAssymmetric"
                  @update:model-value="isAssymmetric = !isAssymmetric"/>
        <div v-if="isAssymmetric" class="q-pa-md">
          <q-input bottom-slots label="Neue Faction" v-model="inputItem">
            <template v-slot:append>
              <kenner-button round dense flat icon="add" @click="addItem" />
            </template>
          </q-input>
          <div v-for="item of listItems" :key="item">
            <div class="flex justify-between q-mb-sm">
              <div class="column justify-center">{{ item }}</div>
              <kenner-button icon="close" @click="removeItem(item)" color="accent" flat dense round/>
            </div>
          </div>
        </div>
      </div>
      <div>
        <q-toggle label="Startspielerreihenfolge" :model-value="startingPlayerOrder"
                  @update:model-value="startingPlayerOrder = !startingPlayerOrder"/>
      </div>
      <div>
        <q-toggle label="Punkte" :model-value="hasPoints" @update:model-value="hasPoints = !hasPoints"/>
      </div>
    </div>
  </div>

</template>

<script setup lang="ts">

import { ref } from 'vue';
import KennerButton from "components/buttons/KennerButton.vue";

const isAssymmetric = ref(false);
const startingPlayerOrder = ref(true);
const hasPoints = ref(true);

const listItems = ref([
  'darklings',
  'mermaids',
  'auren',
  'fakirs',
  'cultists',
  'chaos',
  'swarmlings',
]);

const inputItem = ref('');
function addItem(){
  listItems.value.unshift(inputItem.value);
  inputItem.value = '';
}

function removeItem(item: string): void{
  listItems.value = listItems.value.filter(i => i!==item);
}
</script>
