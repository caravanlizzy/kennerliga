<template>
    <div>
   {{ data }} 
    </div>
</template>

<script setup lang="ts">
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';

const route = useRoute();

const { data , isFinished } = useAxios(`users/${route.params.id}`, api);
</script>