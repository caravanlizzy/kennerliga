<template>
  <q-toolbar class="kenner-toolbar q-px-none row justify-between items-center">
    <!-- Left: Brand -->
    <div class="row items-center">
      <template v-if="isMobile">
        <q-btn
          :to="{ name: 'home' }"
          round
          size="md"
          flat
          :ripple="{ color: 'positive' }"
          color="positive"
          icon="psychology"
          aria-label="Home"
          type="button"
        />
      </template>
      <template v-else>
        <q-chip
          clickable
          @click="goHome()"
          outline
          color="positive"
          text-color="positive"
          :ripple="{ color: 'positive' }"
          class="q-px-sm q-py-xs"
        >
          <q-icon name="psychology" size="16px" color="positive" />
          <span class="q-ml-sm text-weight-medium">Kennerliga</span>
        </q-chip>
      </template>
    </div>

    <!-- Center: CTA -->
    <q-toolbar-title class="absolute-center">
      <q-btn
        v-if="isAuthenticated"
        :to="{ name: 'my-league' }"
        outline
        color="primary"
        class="q-px-md q-py-xs rounded-borders"
        :ripple="{ color: 'accent' }"
        no-caps
        type="button"
      >
        <q-icon name="emoji_events" />
        <span v-show="!isMobile" class="text-weight-medium q-ml-xs">My League</span>

        <!-- tiny positive indicator when user is active player -->
        <q-badge
          v-if="isMeActivePlayer"
          floating
          rounded
          color="positive"
        />
      </q-btn>
    </q-toolbar-title>

    <!-- Right: controls -->
    <div class="row justify-center items-center">
      <KennerButton
        @click="toggleDev"
        flat
        color="accent"
        icon="build"
        :ripple="{ color: 'accent' }"
      />

      <UserName
        v-if="isAuthenticated"
        :display-username="user?.username || ''"
      />

      <KennerButton
        v-if="isAuthenticated"
        flat
        color="primary"
        icon="menu"
        @click="onToggle"
        :ripple="{ color: 'accent' }"
      />

      <KennerButton
        v-else
        flat
        color="positive"
        icon="login"
        :to="{ name: 'login' }"
        :ripple="{ color: 'accent' }"
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
const { isAuthenticated, user } = storeToRefs(useUserStore());
const { isMeActivePlayer } = storeToRefs(useLeagueStore());
const { isMobile } = useResponsive();

function goHome() {
  router.push({ name: 'home' });
}
</script>
