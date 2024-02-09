<template>
  <div class="row no-wrap">
    <kenner-button v-if="loggedIn" stretch flat icon="settings" />
    <kenner-button v-if="loggedIn" stretch flat icon="logout" color="accent" forward-name="home" @click="logout"/>
    <kenner-button v-else stretch flat icon="login" color="positive" forward-name="login" />
  </div>
</template>
<script setup lang="ts">
import KennerButton from 'components/buttons/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

const store = useUserStore()
const { loggedIn } = storeToRefs(store)
const { logout } = store;
</script>
