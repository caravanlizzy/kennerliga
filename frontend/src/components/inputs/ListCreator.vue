<template>
  <q-input bottom-slots :label="buttonLabel" v-model="inputItem">
    <template v-slot:append>
      <kenner-button round dense flat icon="add" @click="addItem"/>
    </template>
  </q-input>
  <div v-for="item of listItems" :key="item">
    <div class="flex justify-between q-mb-sm bg-grey-3 q-py-md q-pl-md q-pr-xs rounded">
      <div class="column justify-center">{{ item }}</div>
        <kenner-button size="sm" icon="close" @click="removeItem(item)" color="accent" flat dense round/>
    </div>
  </div>
</template>
<script setup lang="ts">

import KennerButton from 'components/buttons/KennerButton.vue';
import { Ref, ref } from 'vue';

const props = defineProps<{ initialItems: string[], buttonLabel: string }>();
const emit = defineEmits<{
  (event: 'updateList', list: string[]): void;
}>();

const listItems: Ref<string[]> = ref([ ...props.initialItems ])
const inputItem = ref('');

function addItem() {
  listItems.value.push(inputItem.value);
  listItems.value.sort((a, b) => {
    return a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
  });
  emit('updateList', listItems.value);
  inputItem.value = '';
}

function removeItem(item: string): void {
  listItems.value = listItems.value.filter(i => i !== item);
  emit('updateList', listItems.value);
}
</script>
