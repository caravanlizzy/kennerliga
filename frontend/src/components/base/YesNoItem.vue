<template>
  <div>
    <template v-if="yes">Ja</template>
    <template v-else>Nein</template>
  </div>
</template>

<script setup lang="ts">
defineProps<{ yes: boolean }>();
</script>
