<template>
  <div class="q-pa-md bg-primary text-white">
    <p class="text-h5">Neues Spiel</p>
    <div class="q-py-md" style="max-width: 400px">
      <q-form @submit="onSubmit" class="q-gutter-md">
        <q-input dark color="white" label-color="info" filled v-model="name" label="Spielname" lazy-rules :rules="[
          val => val.length > 0 && val !== null || 'Spielname ist Pflicht'
        ]" />
        <q-btn type="submit" color="positive" label="Speichern" />
      </q-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

const onSubmit = () => {
  console.log('test');

  $q.notify({
    color: 'positive',
    textColor: 'white',
    icon: 'save',
    message: 'Gespeichert'
  })
};
const name = ref('');

</script>