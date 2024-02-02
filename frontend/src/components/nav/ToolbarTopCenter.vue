<template>
  <div class="row">
    <q-btn size="lg" stretch flat color="secondary" icon="add_circle">
      <q-tooltip class="bg-secondary text-primary" delay="50" hide-delay="50" > Ergebnis eintragen</q-tooltip>
    </q-btn>
    <q-btn size="lg" :to="{ name:'games' }" stretch flat icon="casino"></q-btn>
    <q-btn size="lg" :to="{ name: 'users' }" stretch flat icon="person"></q-btn>
  </div>
</template>
<script setup lang="ts">
</script>


<style scoped>
.q-btn {
  margin: 0 10px;
}
</style>
