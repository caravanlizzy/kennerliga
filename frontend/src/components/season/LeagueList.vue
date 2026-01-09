<template>
  <q-card
    bordered
    flat
    class="league-card"
    :class="{ 'cursor-pointer': isAdmin }"
    @click="isAdmin ? goToLeague(league) : undefined"
  >
    <q-card-section class="row items-center q-gutter-sm">
      <q-avatar color="primary" text-color="white" size="40px">
        L{{ league.level }}
      </q-avatar>
      <div class="col">
        <div class="text-subtitle1 text-weight-medium">League {{ league.level }}</div>
        <div class="text-caption text-grey-7">ID: {{ league.id }}</div>
      </div>
      <div class="col-auto column items-end q-gutter-y-xs">
        <q-chip square outline icon="group" class="q-ma-none">{{ league.members?.length || 0 }}</q-chip>
        <q-badge
          v-if="league.is_completed"
          color="positive"
          text-color="white"
          class="q-pa-xs"
        >
          <q-icon name="check_circle" size="14px" class="q-mr-xs" />
          <span class="text-weight-bold" style="font-size: 10px">COMPLETE</span>
        </q-badge>
        <KennerButton
          v-if="isAdmin"
          flat
          dense
          color="primary"
          icon="settings"
          size="sm"
          label="Manage"
          @click.stop="goToLeague(league)"
        />
      </div>
    </q-card-section>
    <q-separator />
    <q-card-section>
      <div class="text-caption text-grey-7 q-mb-xs">Members</div>
      <div v-if="league.members?.length" class="row q-col-gutter-xs">
        <q-chip
          v-for="m in league.members"
          :key="m.id"
          dense
          clickable
          @click.stop
          icon="person"
          class="q-mr-xs q-mb-xs"
        >
          {{ m.profile_name }}
        </q-chip>
      </div>
      <div v-else class="text-caption text-grey-5 italic">No members assigned</div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { TLeagueDto } from 'src/types';
import { useRouter } from 'vue-router';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import KennerButton from 'components/base/KennerButton.vue';

defineProps<{ league: TLeagueDto }>();

const router = useRouter();
const { isAdmin } = storeToRefs(useUserStore());

function goToLeague(league: TLeagueDto) {
  router.push({ name: 'league-manager', params: { id: league.id } });
}
</script>

<style scoped>
.league-card:hover.cursor-pointer {
  background: #fafafa;
}
</style>
