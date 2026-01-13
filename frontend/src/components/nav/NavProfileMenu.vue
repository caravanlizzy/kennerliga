<template>
  <div class="row items-center no-wrap q-gutter-x-sm">
    <UserAvatar
      v-if="isAuthenticated"
      :display-username="user?.username || ''"
      shape="squircle"
      size="36px"
    />

    <KennerButton
      v-if="isAuthenticated"
      flat
      dense
      shape="squircle"
      color="grey-7"
      icon="menu"
      class="nav-section-btn"
      style="height: 40px; min-width: 40px;"
      @click="onToggle"
    />

    <KennerButton
      v-else
      flat
      dense
      shape="squircle"
      color="primary"
      icon="login"
      class="nav-section-btn"
      style="height: 40px; min-width: 40px;"
      :to="{ name: 'login' }"
    />
  </div>
</template>
<script setup lang="ts">
import UserAvatar from 'components/ui/UserAvatar.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import KennerButton from 'components/base/KennerButton.vue';

defineProps<{ onToggle: () => void }>();
const { user, isAuthenticated } = storeToRefs(useUserStore());
</script>
