<template>
  <div class="q-pb-sm">
    <KennerInput bottom-slots hide-bottom-space :label="buttonLabel" v-model="inputItem.name"
             @keyup.enter="addItem">
      <template v-slot:append>
        <KennerButton round dense flat icon="add" @click="addItem"/>
      </template>
    </KennerInput>
    <div v-for="(item, index) of listItems" :key="item.id">
      <div v-if="item.isEditable">
        <KennerInput bottom-slots hide-bottom-space label="editieren" color="primary" class="text-white"
                 v-model="item.name">
          <template v-slot:prepend>
            <kenner-counter v-if="ranked" :content="index"/>
          </template>
          <template v-slot:append>
            <KennerButton color="primary" dense flat icon="check" @click="item.isEditable=false"
                           @blur="item.isEditable=false"/>
          </template>
        </KennerInput>
      </div>
      <div v-else @click="() => item.isEditable = true" class="flex justify-between q-pa-sm rounded item-border"
           :class="{'border-bottom': index === listItems.length - 1}">
        <div v-if="ranked" class="row">
          <div class="column">
            <KennerButton
              flat
              v-if="index > 0"
              icon="arrow_drop_up"
              size="sm"
              @click.stop="moveItemUp(index)"
            />
            <KennerButton
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
        <KennerButton icon="delete" @click="removeItem(item)" color="accent" flat dense/>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">

import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import { Ref, ref } from 'vue';
import { TItem } from 'src/types';
import KennerCounter from 'components/base/KennerCounter.vue';
import { createRandomId } from 'src/helpers';

const props = defineProps<{ buttonLabel: string, ranked?: boolean, initialList?: string[] }>();
const emit = defineEmits<{
  (event: 'updateList', list: string[]): void;
}>();

const listItems: Ref<TItem[]> = ref([]);
const inputItem: Ref<TItem> = ref({ itemId: -1, name: '', isEditable: false });

if (props.initialList) {
  listItems.value = props.initialList.map(name => ({
    itemId: createRandomId(),
    name,
    isEditable: false
  }));
}


function addItem() {
  if(!inputItem.value.name) return;
  inputItem.value.itemId = createRandomId();
  listItems.value.push({ ...inputItem.value });
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
  emit('updateList', listItems.value.map((item) => item.name));
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
