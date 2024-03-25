<template>
  <kenner-button :to="{ name: 'home' }" flat color="primary" icon="pets" />
  <q-toolbar-title class="text-primary">
    Kennerliga
  </q-toolbar-title>
  <kenner-button v-if="isAuthenticated" flat color="secondary" icon="add_circle">
    <q-tooltip class="bg-primary text-white" :delay="50" :hide-delay="450" anchor="center left"> Ergebnis
      eintragen
    </q-tooltip>
  </kenner-button>
  <kenner-button v-if="isAuthenticated" flat icon="menu" @click="onToggle" />
  <kenner-button v-else flat icon="login"  :to="{name:'login'}"/>
</template>

<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import {  } from 'src/composables/reponsive';

defineProps<{
  onToggle: () => void,
}>()

const store = useUserStore();
const { isAuthenticated } = storeToRefs(store);
</script>
