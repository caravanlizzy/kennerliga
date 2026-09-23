<template>
  <q-item
    :clickable="isAdmin"
    :v-ripple="isAdmin"
    class="q-py-md league-item"
    :class="{ 'cursor-pointer': isAdmin, 'bg-grey-1': league.is_completed }"
    @click="isAdmin ? goToLeague(league) : undefined"
  >
    <q-item-section avatar>
      <LeagueLevel :level="league.level" size="40px" fontSize="16px" />
    </q-item-section>

    <q-item-section>
      <div class="row items-center q-gutter-x-sm q-mb-xs">
        <span class="text-subtitle1 text-weight-bold text-dark">League {{ league.level }}</span>
        <q-badge v-if="league.is_completed" color="positive" class="q-pa-xs">
          <q-icon name="check_circle" size="12px" class="q-mr-xs" />
          <span>Complete</span>
        </q-badge>
      </div>

      <div class="row items-center q-gutter-x-sm wrap">
        <span class="text-caption text-grey-6 text-weight-bold">Players:</span>
        <template v-if="league.members?.length">
          <div
            v-for="m in league.members"
            :key="m.id"
            class="row items-center q-gutter-x-xs q-mr-sm"
            @click.stop
          >
            <div class="player-dot" />
            <span class="text-caption text-grey-8">{{ m.profile_name }}</span>
          </div>
        </template>
        <span v-else class="text-caption text-grey-5 italic">None</span>
      </div>
    </q-item-section>

    <q-item-section side>
      <div class="row items-center q-gutter-x-sm">
        <q-badge outline color="grey-8" class="q-pa-xs">
          <q-icon name="group" size="14px" class="q-mr-xs" />
          <span>{{ league.members?.length || 0 }}</span>
        </q-badge>
        <KennerButton
          v-if="isAdmin"
          dense
          no-caps
          color="primary"
          icon="settings"
          size="sm"
          label="Manage"
          @click.stop="goToLeague(league)"
        />
      </div>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import { TLeagueDto } from 'src/types';
import { useRouter } from 'vue-router';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import KennerButton from 'components/base/KennerButton.vue';
import LeagueLevel from './LeagueLevel.vue';

defineProps<{ league: TLeagueDto }>();

const router = useRouter();
const { isAdmin } = storeToRefs(useUserStore());

function goToLeague(league: TLeagueDto) {
  router.push({
    name: 'league-manager',
    params: { id: league.season, leagueId: league.id },
  });
}
</script>

<style scoped lang="scss">
.league-item {
  transition: background-color 0.2s ease;

  &:hover {
    background: #f8fafc;
  }
}

.player-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--q-primary);
  opacity: 0.6;
}
</style>
