<template>
<!--  <q-btn  style="height: 44px; width: 44px;">-->
<!--    <img src="public/icons/kennericon.jpg" style="height: 44px; width: 44px;">-->
<!--  </q-btn>-->
  <kenner-button :to="{ name: 'home' }" flat color="primary" icon="pets"/>
  <q-toolbar-title class="text-primary">
    Kennerliga
  </q-toolbar-title>
  <kenner-button :to="{name: 'game-select'}" v-if="isAuthenticated" flat color="primary" icon="sports_esports">
    <q-tooltip class="bg-primary text-white" :delay="50" :hide-delay="170" anchor="top left"> Spielauswahl
    </q-tooltip>
  </kenner-button>
  <kenner-button @click="registerForCurrentSeason()"> Register </kenner-button>
  <kenner-button v-if="isAuthenticated" flat color="secondary" icon="add_circle">
    <q-tooltip class="bg-primary text-white" :delay="50" :hide-delay="170" anchor="top left"> Ergebnis
      eintragen
    </q-tooltip>
  </kenner-button>
  <TheUsername v-if="isAuthenticated" />
  <kenner-button v-if="isAuthenticated" flat icon="menu" @click="onToggle" />
  <kenner-button v-else flat icon="login"  :to="{name:'login'}"/>
</template>

<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import {  } from 'src/composables/reponsive';
import TheUsername from 'components/TheUsername.vue';
import {registerForCurrentSeason} from "src/services/season/seasonService";

defineProps<{
  onToggle: () => void,
}>()

const store = useUserStore();
const { isAuthenticated } = storeToRefs(store);
</script>
