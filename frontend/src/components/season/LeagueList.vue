<template>
  <q-card
    bordered
    flat
    class="league-card cursor-pointer transition-all"
    @click="goToLeague(league)"
  >
    <!-- Header with gradient background -->
    <q-card-section
      class="bg-primary from-primary to-secondary text-white"
    >
      <div class="row items-center justify-between q-gutter-sm">
        <q-avatar
          color="white"
          text-color="primary"
          size="56px"
          class="shadow-2"
        >
          <div class="text-h6 text-weight-bold">L{{ league.level }}</div>
        </q-avatar>
        <q-chip
          square
          color="white"
          text-color="primary"
          icon="group"
          class="shadow-1"
        >
          <span class="text-weight-bold">{{
            league.members?.length || 0
          }}</span>
        </q-chip>
      </div>
    </q-card-section>

    <!-- Members section with better spacing -->
    <q-card-section class="q-pt-md">
      <div class="row items-center q-mb-sm">
        <q-icon name="people" color="grey-7" size="18px" class="q-mr-xs" />
        <span
          class="text-caption text-grey-7 text-weight-medium text-uppercase"
        >
          Members ({{ league.members?.length || 0 }})
        </span>
      </div>

      <!-- Empty state for no members -->
      <div
        v-if="!league.members?.length"
        class="text-center q-pa-md text-grey-5"
      >
        <q-icon name="person_off" size="32px" class="q-mb-xs" />
        <div class="text-caption">No members yet</div>
      </div>

      <!-- Member chips with avatar style -->
      <div v-else class="row q-col-gutter-xs">
        <q-chip
          v-for="m in league.members"
          :key="m.id"
          clickable
          @click.stop
          color="grey-2"
          text-color="grey-9"
          class="q-mb-xs"
        >
          <q-avatar color="primary" text-color="white" size="24px">
            <q-icon name="person" size="16px" />
          </q-avatar>
          <span class="q-ml-xs">{{ m.profile_name }}</span>
        </q-chip>
      </div>
    </q-card-section>

    <q-separator />

  </q-card>
</template>

<script setup lang="ts">
import { TLeague } from 'src/types';
import { useRouter } from 'vue-router';

defineProps<{ league: TLeague }>();

const router = useRouter();

function goToLeague(league: TLeague) {
  try {
    router.push({ name: 'ManageLeague', params: { id: league.id } });
  } catch (e) {
    router.push(`/leagues/${league.id}`);
  }
}
</script>

<style scoped lang="scss">

.opacity-80 {
  opacity: 0.8;
}
</style>
