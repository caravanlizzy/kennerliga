<template>
  <div class="q-px-md q-pb-sm">
    <q-input filled square bottom-slots hide-bottom-space :label="buttonLabel" v-model="inputItem.name">
      <template v-slot:append>
        <kenner-button round dense flat icon="add" @click="addItem" />
      </template>
    </q-input>
    <div v-for="(item, index) of listItems" :key="item.id">
      <div v-if="item.isEditable">
        <q-input square bottom-slots hide-bottom-space label="editieren" color="info" class="text-white"
                 v-model="item.name">
          <template v-slot:prepend>
            <kenner-counter v-if="ranked" :content="index" />
          </template>
          <template v-slot:append>
            <kenner-button color="info" dense flat icon="check" @click="item.isEditable=false"
                           @blur="item.isEditable=false" />
          </template>
        </q-input>
      </div>
      <div v-else @click="() => item.isEditable = true" class="flex justify-between q-pa-sm rounded item-border"
           :class="{'border-bottom': index === listItems.length - 1}">
        <div v-if="ranked" class="row">
          <div class="column">
            <q-btn
              flat
              v-if="index > 0"
              icon="arrow_drop_up"
              size="sm"
              @click.stop="moveItemUp(index)"
            />
            <q-btn
              flat
              v-if="index<listItems.length -1"
              icon="arrow_drop_down"
              size="sm"
              @click.stop="moveItemDown(index)"
            />
          </div>
          <!--          <kenner-counter :content="index" />-->
        </div>
        <div class="column justify-center item-start">{{ item.name }}</div>
        <kenner-button icon="close" @click="removeItem(item)" color="accent" flat dense />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">

import KennerButton from 'components/buttons/KennerButton.vue';
import { Ref, ref } from 'vue';
import { TItem } from 'components/models';
import KennerCounter from 'components/items/KennerCounter.vue';

defineProps<{ buttonLabel: string, ranked?: boolean }>();
const emit = defineEmits<{
  (event: 'updateList', list: Omit<TItem, 'isEditable'>[]): void;
}>();

let nextId = 0;
const listItems: Ref<TItem[]> = ref([]);
const inputItem: Ref<TItem> = ref({ id: nextId, name: '', isEditable: false });


function addItem() {
  inputItem.value.id = nextId;
  nextId++;
  listItems.value.push(inputItem.value);
  listItems.value.sort((a: TItem, b: TItem) => {
    return a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' });
  });
  inputItem.value = { ...inputItem.value, isEditable: false, name: '' };
  updateList();
}

function moveItemUp(index: number): void {
  if (index > 0 && index < listItems.value.length) {
    // Swap the elements at index and index - 1
    [listItems.value[index], listItems.value[index - 1]] = [listItems.value[index - 1], listItems.value[index]];
  }
  updateList();
}

function moveItemDown(index: number): void {
  if (index >= 0 && index < listItems.value.length + 1) {
    // Swap the elements at index and index - 1
    [listItems.value[index], listItems.value[index + 1]] = [listItems.value[index + 1], listItems.value[index]];
  }
  updateList();
}

function removeItem(item: TItem): void {
  listItems.value = listItems.value.filter(i => i !== item);
  updateList();
}

function updateList() {
  emit('updateList', listItems.value.map(({ isEditable, ...rest }) => rest));
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
