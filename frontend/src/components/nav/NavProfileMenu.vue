<template>
  <div
    class="row items-center q-pa-xs no-wrap q-gutter-x-xs bg-grey-1 nav-item-radius border-subtle"
    style="z-index: 1"
  >
    <UserAvatar
      v-if="isAuthenticated"
      :display-username="user?.username || ''"
      class="q-ml-xs q-mr-xs"
      shape="circle"
    />

    <q-btn
      v-if="isAuthenticated"
      flat
      dense
      round
      color="dark"
      icon="menu"
      @click="onToggle"
    />

    <q-btn
      v-else
      flat
      dense
      round
      color="positive"
      icon="login"
      :to="{ name: 'login' }"
    />
  </div>
</template>
<script setup lang="ts">
import UserAvatar from 'components/ui/UserAvatar.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

defineProps<{ onToggle: () => void }>();
const { user, isAuthenticated } = storeToRefs(useUserStore());
</script>
