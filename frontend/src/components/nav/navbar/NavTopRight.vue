<template>
  <div class="row no-wrap">
    <kenner-button v-if="loggedIn" color="secondary" :dark="false" stretch flat icon="settings" />
<!--    <kenner-button v-if="loggedIn" stretch flat icon="logout" color="accent" forward-name="home" @click="logout"/>-->
    <kenner-button v-else stretch flat icon="login" color="info" forward-name="login" label="Login" />
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
