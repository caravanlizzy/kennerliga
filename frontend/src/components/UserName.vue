<template>
 <q-avatar color="accent" size="30px">
   {{ user?.username[0] }}
   <KennerTooltip>{{ user?.username}}</KennerTooltip>
 </q-avatar>
</template>

<script setup lang="ts">

import { useUserStore } from 'stores/userStore';
import KennerTooltip from 'components/KennerTooltip.vue';
const { user } = useUserStore();
</script>
