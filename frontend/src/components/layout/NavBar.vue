<template>
  <q-toolbar class="q-px-none row justify-between items-center">
    <!-- Left: Brand -->
    <div class="row items-center">
      <template v-if="isMobile">
        <q-btn
          :to="{ name: 'home' }"
          round
          size="md"
          color="white"
          text-color="secondary"
          icon="psychology"
          aria-label="Home"
          type="button"
        />
      </template>
      <template v-else>
        <q-chip
          clickable
          :to="{ name: 'home' }"
          color="secondary"
          text-color="white"
          :ripple="{ color: 'white' }"
          class="kenner-brand q-px-sm q-py-xs"
        >
          <q-avatar size="18px" class="bg-white text-secondary">
            <q-icon name="psychology" size="16px" />
          </q-avatar>
          <span class="q-ml-sm text-weight-medium">Kennerliga</span>
        </q-chip>
      </template>
    </div>

    <!-- Center: CTA -->
    <q-toolbar-title class="absolute-center">
      <q-btn
        v-if="isAuthenticated"
        :to="{ name: 'my-league' }"
        color="primary"
        text-color="white"
        class="my-league-btn q-px-md q-py-xs rounded-full shadow-2"
        :style="isMeActivePlayer ? 'border: 2px solid #FFC107;' : ''"
        no-caps
        unelevated
        type="button"
      >
        <q-icon name="emoji_events" color="amber-4" />
        <span v-show="!isMobile" class="text-weight-medium">My League</span>
      </q-btn>
    </q-toolbar-title>

    <!-- Right: controls -->
    <div class="row justify-center items-center">
      <KennerButton @click="toggleDev" color="white" icon="build" flat />

      <UserName
        v-if="isAuthenticated"
        :display-username="user?.username || ''"
      />

      <KennerButton
        v-if="isAuthenticated"
        flat
        color="white"
        icon="menu"
        @click="onToggle"
      />

      <KennerButton
        v-else
        flat
        color="white"
        icon="login"
        :to="{ name: 'login' }"
      />
    </div>
  </q-toolbar>
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import UserName from 'components/ui/UserName.vue';
import { useRouter } from 'vue-router';
import { useUiStore } from 'stores/uiStore';
import { useResponsive } from 'src/composables/reponsive';
import { useLeagueStore } from 'stores/leagueStore';

defineProps<{
  onToggle: () => void;
}>();

const router = useRouter();
const { toggleDev } = useUiStore();
const { isAuthenticated, user, isAdmin } = storeToRefs(useUserStore());
const { isMeActivePlayer } = storeToRefs(useLeagueStore());
const { isMobile } = useResponsive();

function goHome() {
  router.push({ name: 'home' });
}
</script>
