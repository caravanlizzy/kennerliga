<template>
  <KennerInput
    v-model="filter"
    label="Game"
    clearable
    class="full-width"
  >
    <template #append>
      <q-icon name="search" color="primary" />
    </template>
  </KennerInput>
</template>

<script setup lang="ts">
import KennerInput from 'components/base/KennerInput.vue';
const filter = defineModel<string>();
</script>

