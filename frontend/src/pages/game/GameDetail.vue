<template>
  <div>
    <div v-if="isFinished" class="text-h6">
      {{ data.name }}
    </div>
    <div v-if="isFinished" class="text-h8"> {{ data.platform }}</div>
  </div>

</template>

<script setup lang="ts">
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';

const route = useRoute();

const { data , isFinished } = useAxios(`games/${route.params.id}`, api);
</script>

<style scoped>
</style>
