<template>
  <div class="col-12 col-md-6">
    <KennerInput
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
    </KennerInput>
  </div>
</template>

<script setup lang="ts">
import KennerInput from 'components/base/KennerInput.vue';
const filter = defineModel<string>();
</script>

