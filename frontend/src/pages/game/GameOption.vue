<template>
    <q-card class=" q-mt-lg column">
      <kenner-button class="self-end q-mr-xs q-mt-xs" flat  icon="close" @click="deleteOption"></kenner-button>
    <div class="col q-mx-md q-my-xs">
      <q-checkbox :model-value="isBoolean" @update:model-value="emitIsBoolean" color="primary" label="Ja/Nein Option" />
      <kenner-input :model-value="title" @update:modelValue="emitTitle" label="Spieloption Titel" class="q-mb-md q-mx-xs" />
    </div>
  </q-card>
</template>

<script setup lang="ts">
import KennerInput from 'components/inputs/KennerInput.vue';
import { TGameOption } from 'pages/game/models';
import KennerButton from 'components/buttons/KennerButton.vue';

defineProps<TGameOption>();
const emits = defineEmits<{
  changeTitle: [title: string]
  updateBoolean: [isBoolean: boolean]
  deleteOption: [id: number]
}>()

function emitTitle(title: string){
  emits('changeTitle', title);
}

function emitIsBoolean(isBoolean: boolean){
  emits('updateBoolean', isBoolean);
}
 function deleteOption(id: number){
  emits('deleteOption', id);
 }

</script>

<style scoped lang="scss">
.bordered {
  border: 1px solid $primary;
}
</style>
