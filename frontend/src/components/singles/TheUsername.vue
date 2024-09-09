<template>
 <div class="text-accent q-mx-md" style="text-transform: none;">
   {{ user?.username }}
 </div>
</template>

<script setup lang="ts">

import { useUserStore } from 'stores/userStore';
const { user } = useUserStore();
</script>
