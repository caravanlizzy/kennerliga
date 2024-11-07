<template>
  <!--  <q-btn :to="{ name: 'home' }" round color="secondary" class="glossy" icon="psychology"/>-->
  <q-btn flat @click="goHome({name: 'home'})">
    <q-chip size="md" color="info" text-color="white">
      <q-icon name="psychology" class="q-mr-md" size="xs" color="white"></q-icon>
      Kennerliga
    </q-chip>
  </q-btn>
  <q-toolbar-title class="text-primary">
    <!--      <h6 class="text-italic" > Kennerliga </h6>-->
  </q-toolbar-title>
  <KennerButton :to="{name: 'game-selection'}" v-if="isAuthenticated" flat color="primary" icon="sports_esports">
    <q-tooltip class="bg-primary text-white" :delay="50" :hide-delay="170" anchor="top left"> Aktive Liga
    </q-tooltip>
  </KennerButton>
  <!--  <KennerButton v-if="isAuthenticated" flat color="secondary" icon="add_circle">-->
  <!--    <q-tooltip class="bg-primary text-white" :delay="50" :hide-delay="170" anchor="top left"> Ergebnis-->
  <!--      eintragen-->
  <!--    </q-tooltip>-->
  <!--  </KennerButton>-->
  <TheUsername v-if="isAuthenticated"/>
  <KennerButton v-if="isAuthenticated" flat icon="menu" @click="onToggle"/>
  <KennerButton v-else flat icon="login" :to="{name:'login'}"/>
</template>

<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import TheUsername from 'components/singles/TheUsername.vue';
import { useRouter } from 'vue-router';

defineProps<{
  onToggle: () => void,
}>()

const store = useUserStore();
const router = useRouter();
const { isAuthenticated } = storeToRefs(store);

function goHome() {
  router.push({ name: 'home' });
}

</script>
