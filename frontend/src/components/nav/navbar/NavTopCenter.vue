<template>
  <div class="row no-wrap">
    <kenner-button v-if="loggedIn" flat color="secondary" icon="add_circle">
      <q-tooltip class="bg-secondary text-primary" :delay="50" :hide-delay="250"> Ergebnis eintragen</q-tooltip>
    </kenner-button>
    <kenner-button v-if="loggedIn" :dark="false" forward-name="games" stretch flat icon="casino" />
    <kenner-button v-if="loggedIn" :dark="false" forward-name="users" stretch flat icon="person" />
  </div>
</template>
<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';

import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

const store = useUserStore();
const { loggedIn } = storeToRefs(store);
</script>
