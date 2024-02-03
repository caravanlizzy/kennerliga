<template>
  <q-toolbar-title shrink class="row no-wrap">
    <kenner-button stretch flat color="secondary" icon="add_circle">
      <q-tooltip class="bg-secondary text-primary" delay="50" hide-delay="250"> Ergebnis eintragen</q-tooltip>
    </kenner-button>
    <kenner-button forward-name="games" stretch flat icon="casino" />
    <kenner-button forward-name="users" stretch flat icon="person" />
  </q-toolbar-title>
</template>
<script setup lang="ts">
import KennerButton from 'components/KennerButton.vue';

</script>


<style scoped>
.q-btn {
  margin: 0 10px;
}
</style>
