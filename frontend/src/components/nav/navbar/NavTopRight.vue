<template>
  <div class="row no-wrap">
    <kenner-button v-if="loggedIn" stretch flat icon="settings"/>
    <kenner-button v-if="loggedIn" stretch flat icon="logout" color="accent" forward-name="home" />
    <kenner-button v-else stretch flat icon="login" color="positive" forward-name="login" />
  </div>
</template>
<script setup lang="ts">

import KennerButton from 'components/buttons/KennerButton.vue';
defineProps<{ loggedIn: boolean }>();
</script>
