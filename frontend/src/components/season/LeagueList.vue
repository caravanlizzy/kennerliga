<template>
  <q-card
    flat
    bordered
    class="q-hoverable full-height column"
    :class="{ 'cursor-pointer': isAdmin, 'bg-grey-1': league.is_completed }"
    @click="isAdmin ? goToLeague(league) : undefined"
  >
    <div v-if="isAdmin" class="q-focus-helper"></div>
    <div class="q-pa-md row items-center q-gutter-x-md no-wrap">
      <LeagueLevel :level="league.level" size="40px" fontSize="16px" />

      <div class="col column q-gutter-y-xs overflow-hidden">
        <div class="column">
          <span class="text-caption text-grey-6 text-weight-bold q-mb-xs">Players:</span>
          <div v-if="league.members?.length" class="column q-gutter-y-xs q-pl-xs">
            <div
              v-for="m in league.members"
              :key="m.id"
              class="row items-center q-gutter-x-sm"
              @click.stop
            >
              <div class="player-dot" />
              <span class="text-caption text-grey-8">{{ m.profile_name }}</span>
            </div>
          </div>
          <div v-else class="text-caption text-grey-5 italic">None</div>
        </div>
      </div>

      <div class="col-auto row items-center q-gutter-x-xs">
        <q-badge v-if="league.is_completed" color="positive" class="q-pa-xs">
          <q-icon name="check_circle" size="12px" />
        </q-badge>
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
    </div>
  </q-card>
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
.player-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--q-primary);
  opacity: 0.6;
}
</style>
