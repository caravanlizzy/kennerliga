<template>
  <div class="q-pa-md bg-primary text-white">
    <p class="text-h5">Neues Spiel</p>
    <div class="q-py-md" style="max-width: 400px">
      <q-form @submit="onSubmit" class="q-gutter-md">
        <kenner-input rules="" label="Spielname" v-model="form.name"/>
        <kenner-select label="Plattform" :options="options" v-model="form.platform"/>
        <kenner-button class="q-my-xl" type="submit" push color="positive" label="Speichern" />
      </q-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { useAxios } from '@vueuse/integrations/useAxios';
import KennerInput from 'components/inputs/KennerInput.vue';
import KennerSelect from 'components/inputs/KennerSelect.vue';
import KennerButton from 'components/buttons/KennerButton.vue';

const $q = useQuasar();
const form = ref({
  name: '',
  platform: null
});

const options = ref(['BGA', 'Yucata']);

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
  } else if (error.value){
    $q.notify({
      color: 'negative',
      textColor: 'white',
      icon: 'warning',
      message: 'Fehler'
    });
  }
};

</script>
