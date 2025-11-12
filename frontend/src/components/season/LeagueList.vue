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
      <div class="row q-col-gutter-xs">
        <q-chip
          v-for="m in (league.members || [])"
          :key="m.id"
          dense
          clickable
          @click.stop
          icon="person"
          class="q-mr-xs q-mb-xs"
        >
          {{ m.username || m.name }}
        </q-chip>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-actions align="right">
      <q-btn flat icon="open_in_new" label="Open" @click.stop="goToLeague(league)" />
    </q-card-actions>
  </q-card>
</template>
<script setup lang="ts">
import { TLeague } from 'src/types';
import { useRouter } from 'vue-router';

defineProps<{ league: TLeague }>();

const router = useRouter();

function goToLeague(league: TLeague) {
  // Adjust the route target to your app's routes
  // Option A: named route
  try {
    router.push({ name: 'ManageLeague', params: { id: league.id } });
  } catch (e) {
    // Option B: fallback path-based navigation
    router.push(`/leagues/${league.id}`);
  }
}
</script>
