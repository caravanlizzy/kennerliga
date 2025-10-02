<template>
  <div>
    <template v-if="yes">Yes</template>
    <template v-else>No</template>
  </div>
</template>

<script setup lang="ts">
defineProps<{ yes: boolean }>();
</script>
