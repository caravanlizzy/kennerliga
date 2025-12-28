<template>
  <q-card bordered flat class="league-card cursor-pointer" @click="goToLeague(league)">
    <q-card-section class="row items-center q-gutter-sm">
      <q-avatar color="primary" text-color="white" size="40px">
        L{{ league.level }}
      </q-avatar>
      <div class="col">
        <div class="text-subtitle1 text-weight-medium">League {{ league.level }}</div>
        <div class="text-caption text-grey-7">ID: {{ league.id }}</div>
      </div>
      <q-chip square outline icon="group" class="q-ml-auto">{{ league.members?.length || 0 }}</q-chip>
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

defineProps<{ league: TLeagueDto }>();

const router = useRouter();

function goToLeague(league: TLeagueDto) {
  try {
    router.push({ name: 'ManageLeague', params: { id: league.id } });
  } catch (e) {
    router.push(`/leagues/${league.id}`);
  }
}
</script>

<style scoped>
.league-card:hover {
  background: #fafafa;
}
</style>
