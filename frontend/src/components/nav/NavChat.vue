<template>
  <div v-if="!isMobile" class="row items-center no-wrap">
    <KennerButton
      unelevated
      color="teal"
      flat
      shape="squircle"
      class="chat-btn"
      :class="{ 'is-active': chatDrawerOpen }"
      style="height: 36px; min-width: 36px;"
      @click="toggleChat"
    >
      <div class="row items-center no-wrap">
        <q-icon name="chat" class="q-mr-xs" />
        <span class="text-weight-bold">CHAT</span>
      </div>
      <q-badge v-if="unreadCount > 0" floating rounded color="red" class="unread-badge">
        {{ unreadCount }}
      </q-badge>
    </KennerButton>
  </div>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import { storeToRefs } from 'pinia';
import { useUiStore } from 'stores/uiStore';
import KennerButton from 'components/base/KennerButton.vue';
import { computed } from 'vue';

const { isMobile } = useResponsive();
const uiStore = useUiStore();
const { chatDrawerOpen } = storeToRefs(uiStore);
const { toggleChat } = uiStore;

// Placeholder for unread count - assuming it might be added later to uiStore or chatStore
const unreadCount = computed(() => 0);
</script>

<style scoped lang="scss">
.chat-btn {
  transition: all 0.3s ease;

  &.is-active {
    background: rgba($teal, 0.1) !important;
  }

  &:hover {
    background: rgba($teal, 0.05) !important;
  }
}

.unread-badge {
  top: -2px !important;
  right: -2px !important;
  padding: 2px 4px;
  font-size: 10px;
  border: 2px solid white;
}
</style>
