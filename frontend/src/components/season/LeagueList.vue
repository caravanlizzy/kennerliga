<template>
  <q-card
    flat
    bordered
    class="q-hoverable full-height column"
    :class="{ 'cursor-pointer': isAdmin, 'bg-grey-1': league.is_completed }"
    @click="isAdmin ? goToLeague(league) : undefined"
  >
    <div v-if="isAdmin" class="q-focus-helper"></div>
    <!-- Header -->
    <div class="q-px-md q-py-md row items-center justify-between no-wrap q-gutter-x-md">
      <LeagueLevel :level="league.level" />
      <div class="col-auto column items-end q-gutter-y-xs">
        <q-badge outline color="grey-8" class="q-pa-xs">
          <q-icon name="group" size="14px" class="q-mr-xs" />
          <span>{{ league.members?.length || 0 }}</span>
        </q-badge>
        <q-badge v-if="league.is_completed" color="positive" class="q-pa-xs">
          <q-icon name="check_circle" size="12px" class="q-mr-xs" />
          <span>COMPLETE</span>
        </q-badge>
        <KennerButton
          v-if="isAdmin"
          flat
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

    <q-separator />

    <!-- Members -->
    <div class="q-px-md q-pt-sm q-pb-md">
      <div class="text-caption text-grey-6 q-mb-xs text-weight-medium">Users</div>
      <div v-if="league.members?.length" class="row q-col-gutter-xs">
        <q-chip
          v-for="m in league.members"
          :key="m.id"
          dense
          clickable
          icon="person"
          outline
          color="grey-7"
          class="q-mr-xs q-mb-xs"
          @click.stop
        >
          {{ m.profile_name }}
        </q-chip>
      </div>
      <div v-else class="text-caption text-grey-5 italic">No users assigned</div>
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
