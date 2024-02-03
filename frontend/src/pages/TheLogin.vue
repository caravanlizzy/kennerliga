<template>
  <div class="row items-center justify-center bg-blue-3">
    <q-card square style="width: 400px; height: 370px;" class="shadow-20 bg-primary q-px-xl q-pt-md">
      <q-card-section class="">
        <span class="text-h4 text-secondary">
          Login
        </span>
      </q-card-section>
      <q-card-section>
        <kenner-input rules="" label="Email" />
        <kenner-input rules="" label="Passwort" type="password" class="q-pt-lg"/>
      </q-card-section>
      <q-card-section>
        <kenner-button size="lg" class="full-width" label="Anmelden" color="positive" />
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">

import KennerInput from 'components/inputs/KennerInput.vue';
import KennerButton from 'components/KennerButton.vue';
</script>

<style scoped>

</style>
