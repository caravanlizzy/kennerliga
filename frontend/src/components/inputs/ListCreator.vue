<template>
  <q-input bottom-slots label="Neue Faction" v-model="inputItem">
    <template v-slot:append>
      <kenner-button round dense flat icon="add" @click="addItem" />
    </template>
  </q-input>
  <div v-for="item of sortedItems" :key="item">
    <div class="flex justify-between q-mb-sm">
      <div class="column justify-center">{{ item }}</div>
      <kenner-button icon="close" @click="removeItem(item)" color="accent" flat dense round/>
    </div>
  </div>
</template>
<script setup lang="ts">

import KennerButton from 'components/buttons/KennerButton.vue';
import { computed, Ref, ref } from 'vue';

const props = defineProps<{initialItems:string[]}>();

const listItems: Ref<string[]> = ref([...props.initialItems])
const inputItem = ref('');
const sortedItems = computed(() => [...listItems.value].sort((a, b) => {
  return a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
}));

function addItem(){
  listItems.value.push(inputItem.value);
  inputItem.value = '';
}

function removeItem(item: string): void{
  listItems.value = listItems.value.filter(i => i!==item);
}
</script>
