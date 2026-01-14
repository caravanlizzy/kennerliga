<template>
  <q-page class="column col bg-white">
    <div class="q-pa-md row items-center justify-between no-wrap border-bottom-subtle bg-white">
      <div class="text-h5 text-weight-bold"><span class="text-primary">Kenner</span><span class="text-accent">Chat</span></div>
      <q-icon name="chat" color="primary" size="sm" />
    </div>
    <KennerChat class="col bg-white" />
  </q-page>
</template>

<script setup lang="ts">
import KennerChat from 'components/chat/KennerChat.vue';
</script>

<style scoped>
.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
</style>
