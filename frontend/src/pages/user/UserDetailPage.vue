<template>
    <div v-if="isFinished">
   {{ data.username }}
    </div>
</template>

<script setup lang="ts">
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';

const route = useRoute();

const { data , isFinished } = useAxios(`user/users/${route.params.id}`, api);
</script>
