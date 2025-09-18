<template>
  <q-btn flat @click="goHome({ name: 'home' })">
    <q-chip size="md" color="secondary" text-color="white">
      <q-icon
        name="psychology"
        class="q-mr-md"
        size="xs"
        color="white"
      ></q-icon>
      Kennerliga
    </q-chip>
  </q-btn>
  <q-toolbar-title class="text-primary justify-center row no-wrap">
    <KennerButton
      :to="{ name: 'my-league' }"
      v-if="isAuthenticated"
      class="my-league-btn q-px-sm"
      color="info"
    >
      <q-avatar size="24px" class="q-mr-sm q-mx-auto">
        <q-icon name="emoji_events" color="amber-4" />
      </q-avatar>
      <div v-if="!isMobile" class="text-weight-bold text-primary">
        My League
      </div>
    </KennerButton>
  </q-toolbar-title>
  <KennerButton
    @click="toggleDev"
    color="grey-8"
    unelevated
    flat
  >
    <q-avatar size="24px" class="q-mx-auto">
      <q-icon name="build" color="grey-8" />
    </q-avatar>
  </KennerButton>

  <UserName v-if="isAuthenticated" :display-username="user.username" />
  <KennerButton
    color="primary"
    v-if="isAuthenticated"
    flat
    icon="menu"
    @click="onToggle"
  />
  <KennerButton
    color="primary"
    v-else
    flat
    icon="login"
    :to="{ name: 'login' }"
  />
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import UserName from 'components/ui/UserName.vue';
import { useRouter } from 'vue-router';
import { useUiStore } from 'stores/uiStore';
import { useResponsive } from 'src/composables/reponsive';

defineProps<{
  onToggle: () => void;
}>();

const router = useRouter();
const { toggleDev } = useUiStore();
const { isAuthenticated, user } = storeToRefs(useUserStore());
const { isMobile } = useResponsive();

function goHome() {
  router.push({ name: 'home' });
}
</script>

<style lang="scss" scoped>
.my-league-btn {
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
}
</style>
