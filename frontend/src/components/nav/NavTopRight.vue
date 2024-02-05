<template>
  <q-toolbar-title shrink class="row align-end">
    <kenner-button v-if="loggedIn" stretch flat icon="settings"/>

    <kenner-button v-if="loggedIn" stretch flat icon="logout" color="accent" forward-name="home" />
    <kenner-button v-else stretch flat icon="login" color="positive" forward-name="login" />
  </q-toolbar-title>
</template>
<script setup lang="ts">

import KennerButton from 'components/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
const { loggedIn } = useUserStore()
</script>
