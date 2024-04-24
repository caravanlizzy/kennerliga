<template>
  <q-input filled bottom-slots hide-bottom-space :label="buttonLabel" v-model="inputItem.name">
    <template v-slot:append>
      <kenner-button round dense flat icon="add" @click="addItem"/>
    </template>
  </q-input>
  <div v-for="(item, index) of listItems" :key="item.id">
    <div v-if="item.isEditable">
      <q-input filled bottom-slots hide-bottom-space label="editieren" color="info" class="text-white" v-model="item.name">
        <template v-slot:append>
          <kenner-button color="info" dense flat icon="check" @click="item.isEditable=false" @blur="item.isEditable=false"/>
        </template>
      </q-input>
    </div>
    <div v-else @click="() => item.isEditable = true" class="flex justify-between q-pa-sm rounded item-border" :class="{'border-bottom': index === listItems.length - 1}">
      <div class="column justify-center">{{ item.name }}</div>
      <kenner-button icon="close" @click="removeItem(item)" color="accent" flat dense />
    </div>
  </div>
</template>
<script setup lang="ts">

import KennerButton from 'components/buttons/KennerButton.vue';
import { Ref, ref } from 'vue';

type TItem = {
  id: number ;
  name: string;
  isEditable: boolean;
}

defineProps<{ buttonLabel: string }>();
const emit = defineEmits<{
  (event: 'updateList', list: TItem[]): void;
}>();

let nextId = 0;
const listItems: Ref<TItem[]> = ref([])
const inputItem: Ref<TItem> = ref({ id: nextId, name: '', isEditable: false });

function addItem() {
  inputItem.value.id = nextId;
  nextId++;
  listItems.value.push(inputItem.value);
  listItems.value.sort((a:TItem, b:TItem) => {
    return a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' });
  });
  emit('updateList', listItems.value);
  inputItem.value = { ...inputItem.value, isEditable: false, name: ''};
}

function removeItem(item: TItem): void {
  listItems.value = listItems.value.filter(i => i !== item);
  emit('updateList', listItems.value);
}
</script>

<style scoped>
.item-border {
  border-left: 1px solid #e8e8e8;
  border-right: 1px solid #e8e8e8;
}
.border-bottom {
  border-bottom: 1px solid #e8e8e8;
  border-bottom-right-radius: 5px;
  border-bottom-left-radius: 5px;
}
</style>
