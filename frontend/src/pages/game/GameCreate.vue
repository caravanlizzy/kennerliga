<template>
  <div class="q-pa-md bg-primary text-white">
    <p class="text-h5">Neues Spiel</p>
    <div class="q-py-md" style="max-width: 400px">
      <q-form @submit="onSubmit" class="q-gutter-md">
        <q-input dark color="white" label-color="info" filled v-model="form.name" label="Spielname" lazy-rules :rules="[
          val => val.length > 0 && val !== null || 'Spielname ist Pflicht'
        ]" />
        <q-input dark color="white" label-color="info" filled v-model="form.platform" label="Platform" lazy-rules
                 :rules="[
          val => ['BGA', 'yucata'].includes(val) || 'Spielname ist Pflicht'
        ]" />
        <q-btn type="submit" push color="positive" label="Speichern" />
      </q-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { useAxios } from '@vueuse/integrations/useAxios';

const $q = useQuasar();
const form = ref({
  name: '',
  platform: ''
});

const onSubmit = async () => {
  const { response, error, isFinished } = await useAxios('games/', {
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
