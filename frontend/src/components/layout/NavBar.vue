<template>
  <q-toolbar
    class="navbar bg-grey-1 text-dark q-px-md q-py-none shadow-1 relative-position"
  >
    <!-- Left: Brand -->
    <div class="row items-center no-wrap">
      <q-btn
        v-if="isMobile"
        :to="{ name: 'home' }"
        flat
        round
        dense
        color="primary"
        icon="psychology"
        aria-label="Home"
      />
      <q-chip
        v-else
        clickable
        outline
        color="primary"
        text-color="primary"
        @click="goHome"
        class="q-px-sm q-py-xs bg-grey-1 text-dark"
      >
        <q-icon name="psychology" size="16px" class="q-mr-xs" />
        <span class="text-weight-medium">Kennerliga</span>
      </q-chip>
    </div>

    <q-space />

    <!-- Center: Main CTA -->
    <div class="row items-center no-wrap absolute-center">
      <q-btn
        v-if="isAuthenticated"
        :to="{ name: 'my-league' }"
        unelevated
        color="primary"
        class="q-px-md q-py-xs rounded-borders text-weight-medium"
        no-caps
      >
        <q-icon name="emoji_events" />
        <span v-show="!isMobile" class="q-ml-xs">My League</span>
        <q-badge v-if="isMeActivePlayer" floating rounded color="positive" />
      </q-btn>
    </div>

    <q-space />

    <!-- Right: Controls -->
    <div class="row items-center no-wrap q-gutter-x-sm bg-grey-1" style="z-index: 1">
      <q-btn
        flat
        dense
        round
        color="accent"
        icon="build"
        :to="{ name: 'dev' }"
      />

      <UserName
        v-if="isAuthenticated"
        :display-username="user?.username || ''"
        class="q-ml-xs q-mr-xs"
      />

      <q-btn
        v-if="isAuthenticated"
        flat
        dense
        round
        color="primary"
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
  </q-toolbar>
</template>

<script setup lang="ts">
import { useUserStore } from 'stores/userStore'
import { storeToRefs } from 'pinia'
import UserName from 'components/ui/UserName.vue'
import { useRouter } from 'vue-router'
import { useUiStore } from 'stores/uiStore'
import { useResponsive } from 'src/composables/reponsive'
import { useLeagueStore } from 'stores/leagueStore'
import { onMounted } from 'vue'

defineProps<{ onToggle: () => void }>()

const router = useRouter()
const { isAuthenticated, user } = storeToRefs(useUserStore())
const { isMeActivePlayer } = storeToRefs(useLeagueStore())
const { updateLeagueData } = useLeagueStore()
const { isMobile } = useResponsive()

onMounted(() => updateLeagueData())

function goHome() {
  router.push({ name: 'home' })
}
</script>

<style scoped>
.navbar {
  position: relative;
  overflow: hidden;
}

.navbar::before {
  content: "";
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 1200 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,50 C100,90 200,10 300,70 C400,130 500,0 600,50 C700,100 800,20 900,60 C1000,100 1100,30 1200,50' stroke='%23e53935' stroke-width='3' fill='none'/%3E%3C/svg%3E")
    center / cover no-repeat;
  opacity: 0.7;
  z-index: 0;
}
</style>
