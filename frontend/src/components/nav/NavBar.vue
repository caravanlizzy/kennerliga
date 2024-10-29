<template>
<!--  <q-btn  style="height: 44px; width: 44px;">-->
<!--    <img src="public/icons/kennericon.jpg" style="height: 44px; width: 44px;">-->
<!--  </q-btn>-->
  <KennerButton :to="{ name: 'home' }" flat color="primary" icon="pets"/>
  <q-toolbar-title class="text-primary">
    Kennerliga
  </q-toolbar-title>
  <KennerButton :to="{name: 'game-selection'}" v-if="isAuthenticated" flat color="primary" icon="sports_esports">
    <q-tooltip class="bg-primary text-white" :delay="50" :hide-delay="170" anchor="top left"> Spielauswahl
    </q-tooltip>
  </KennerButton>
  <KennerButton v-if="isAuthenticated" flat color="secondary" icon="add_circle">
    <q-tooltip class="bg-primary text-white" :delay="50" :hide-delay="170" anchor="top left"> Ergebnis
      eintragen
    </q-tooltip>
  </KennerButton>
  <TheUsername v-if="isAuthenticated" />
  <KennerButton v-if="isAuthenticated" flat icon="menu" @click="onToggle" />
  <KennerButton v-else flat icon="login"  :to="{name:'login'}"/>
</template>

<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import {  } from 'src/composables/reponsive';
import TheUsername from 'components/singles/TheUsername.vue';

defineProps<{
  onToggle: () => void,
}>()

const store = useUserStore();
const { isAuthenticated } = storeToRefs(store);
</script>
