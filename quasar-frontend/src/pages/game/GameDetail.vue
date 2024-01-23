<template>
<!--    <div>-->
<!--      <q-card class="game-card"  flat>-->
<!--        <q-card-section>-->
<!--          <div class="text-h6" v-if="isFinished"> {{ data.name }}</div>-->
<!--        </q-card-section>-->
<!--        <q-separator inset/>-->
<!--        <q-card-section>-->
<!--          <div class="text-subtitle2" v-if="isFinished"> {{ data.platform }}</div>-->
<!--        </q-card-section>-->
<!--      </q-card>-->
<!--    </div>-->
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
