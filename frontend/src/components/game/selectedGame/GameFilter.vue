<template>
  <div class="col-12 col-md-6">
    <q-input
      v-model="filter"
      label="Game"
      outlined
      dense
      clearable
      class="rounded-borders"
    >
      <template #append>
        <q-icon name="search" />
      </template>
    </q-input>
  </div>
</template>

<script setup lang="ts">
const filter = defineModel<string>();
</script>

