<template>
  <q-page class="column col bg-white">
    <div class="q-pa-md row items-center border-bottom-subtle bg-white">
      <q-icon name="chat" color="blue-grey-8" size="sm" class="q-mr-sm" />
      <div class="text-h5 text-weight-bold">KennerChat</div>
    </div>
    <KennerChat class="col bg-white" />
  </q-page>
</template>

<script setup lang="ts">
import KennerChat from 'components/chat/KennerChat.vue';
import { onMounted } from 'vue';
import { useUiStore } from 'stores/uiStore';

const uiStore = useUiStore();
</script>

<style scoped>
.border-bottom-subtle {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
</style>
