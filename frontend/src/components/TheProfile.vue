<template>
 <kenner-button flat icon="person" class="text-accent">
   {{ user?.username }}
 </kenner-button>
</template>

<script setup lang="ts">

import { useUserStore } from 'stores/userStore';
import KennerButton from 'components/buttons/KennerButton.vue';
const { user } = useUserStore();
</script>
