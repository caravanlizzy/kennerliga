<template>
  <div class="">
    <q-btn size="md" dense icon="add_circle" label="Ergebnis" color="secondary" />
    <q-btn size="xl" :to="{ name:'games' }" stretch flat icon="sports_esports"></q-btn>
    <q-btn size="xl" :to="{ name: 'users' }" stretch flat icon="person"></q-btn>
  </div>
</template>
<script setup lang="ts">
</script>


<style scoped>
.q-btn {
  margin: 0 10px;
}
</style>
