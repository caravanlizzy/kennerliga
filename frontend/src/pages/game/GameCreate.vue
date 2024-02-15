<template>
  <div class="q-pa-md">
    <p class="text-h5">Neues Spiel</p>
    <div class="q-py-md" >
      <q-form @submit="onSubmit" class="q-gutter-md">
        <kenner-input class="max-w-500" label="Spielname" v-model="form.name" />
        <kenner-select class="max-w-500" label="Plattform" :options="platforms" v-model="form.platform" />
        <div class="q-mt-xl">
          <div>
            <span class="text-h6">Spieloptionen</span>
            <kenner-button class="q-ml-lg" color="primary" label="Spieloption" icon="add" @click="addEmptyOption" />
          </div>
          <div class="flex row ">
            <GameOption
              v-for="{ id, title, isBoolean } of gameOptions"
              :key="id"
              :is-boolean="isBoolean"
              @changeTitle="updateTitle($event, id)"
              @deleteOption="deleteOption(id)"
              @updateBoolean="updateBoolean($event, id)"
              :title="title"
              :id="id"
            />
          </div>
        </div>
        <kenner-button class="q-my-xl" type="submit" push color="positive" label="Speichern" />
      </q-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, Ref, ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { useAxios } from '@vueuse/integrations/useAxios';
import KennerInput from 'components/inputs/KennerInput.vue';
import KennerSelect from 'components/inputs/KennerSelect.vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { TGameOption } from 'pages/game/models';
import GameOption from 'pages/game/GameOption.vue';

const $q = useQuasar();
const form = ref({
  name: '',
  platform: null
});

const platforms = ref(['BGA', 'Yucata']);
const gameOptions: Ref<TGameOption[]> = ref([]);
let optionCounter = 0;

const canAdd = computed(() => {
  const lastAdded = findOption(optionCounter-1);
  return lastAdded?.title !== '';
})

function addEmptyOption(): void {
  if(!canAdd.value) return;
  gameOptions.value.push({ title: '', isBoolean: true, id: optionCounter });
  optionCounter++;
}

function findOption(id: number): TGameOption | undefined {
  return gameOptions.value.find((item) => item.id === id);
}

function updateTitle(newTitle: string, id: number) {
  const option = findOption(id);
  if (option) {
    option.title = newTitle;
  }
}

function updateBoolean(isBoolean: boolean, id: number) {
  const option = findOption(id);
  if (option) {
    option.isBoolean = isBoolean;
  }
}

function deleteOption(id: number): void {
  gameOptions.value = gameOptions.value.filter((o) => o.id !== id);
}

const onSubmit = async () => {
  const { error, isFinished } = await useAxios('games/', {
    method: 'POST',
    data: { name: form.value.name, platform: form.value.platform }
  }, api);
  if (isFinished.value) {
    $q.notify({
      color: 'positive',
      textColor: 'white',
      icon: 'save',
      message: 'Gespeichert'
    });
  } else if (error.value) {
    $q.notify({
      color: 'negative',
      textColor: 'white',
      icon: 'warning',
      message: 'Fehler'
    });
  }
};
</script>

<style scoped>
.max-w-500{
  max-width: 500px;
}
</style>
