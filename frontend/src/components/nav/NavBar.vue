<template>
  <q-toolbar-title class="row no-wrap items-center justify-between q-py-xs">
    <kenner-button :to="{ name: 'home' }" flat color="accent" :size="iconSize" icon="pets" />
    <div>
      <kenner-button v-if="loggedIn" flat color="secondary" icon="add_circle">
        <q-tooltip class="bg-primary text-white" :delay="50" :hide-delay="450" anchor="center left"> Ergebnis
          eintragen
        </q-tooltip>
      </kenner-button>
      <kenner-button flat icon="menu" @click="onToggle" />
    </div>
  </q-toolbar-title>
</template>

<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import { useResponsive } from 'src/composables/reponsive';

defineProps<{
  onToggle: () => void,
}>()

const store = useUserStore();
const { loggedIn } = storeToRefs(store);
const { iconSize } = useResponsive();
</script>
