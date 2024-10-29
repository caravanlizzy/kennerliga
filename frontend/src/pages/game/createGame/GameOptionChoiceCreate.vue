<template>
  <div class="column q-pa-xs q-mt-lg">
    <div class="q-mx-xs q-mb-xs text-bold">Auswahloptionen</div>
    <ListCreator button-label="Neue Option" @update-list="update"/>
  </div>
</template>

<script setup lang="ts">
import { inject } from 'vue';
import ListCreator from 'components/lists/ListCreator.vue';
import { TGameOption } from 'src/types';

const { updateItem } = inject('useGameOptions');
const props = defineProps<{ gameOption: TGameOption, addChoice: () => void }>();

function update(updatedItemList: string[]) {
  updateItem(props.gameOption, 'choices', updatedItemList);
}
</script>
