<template>
  <q-card
    flat
    bordered
    class="cursor-pointer rounded-borders overflow-hidden"
    @click="goToLeague(league)"
  >
    <!-- Header -->
    <q-card-section class="bg-grey-2 q-py-md">
      <div class="row items-center justify-between">
        <div class="row items-center q-gutter-md">
          <q-avatar
            size="52px"
            color="dark"
            text-color="white"
            class="text-weight-bold text-h6"
          >
            L{{ league?.level }}
          </q-avatar>
          <div>
            <div class="text-subtitle1 text-weight-bold text-grey-9">
              League {{ league?.level }}
            </div>
            <div class="text-caption text-grey-6">
              {{ league?.members?.length || 0 }} participants
            </div>
          </div>
        </div>
        <q-badge
          color="dark"
          text-color="white"
          class="q-pa-sm"
        >
          <q-icon name="group" size="16px" class="q-mr-xs" />
          <span class="text-weight-bold">{{ league.members?.length || 0 }}</span>
        </q-badge>
      </div>
    </q-card-section>

    <q-separator />

    <!-- Members section -->
    <q-card-section class="bg-white">
      <div class="row items-center q-mb-md">
        <q-icon name="people" color="grey-7" size="18px" class="q-mr-xs" />
        <span class="text-caption text-grey-7 text-weight-bold text-uppercase">
          Members
        </span>
      </div>

      <!-- Empty state -->
      <div
        v-if="!league.members?.length"
        class="text-center q-pa-lg rounded-borders bg-grey-1"
      >
        <q-icon name="person_off" size="36px" color="grey-5" class="q-mb-sm" />
        <div class="text-body2 text-grey-6">No members yet</div>
      </div>

      <!-- Member chips -->
      <div v-else class="row q-gutter-sm">
        <q-chip
          v-for="m in league.members"
          :key="m.id"
          clickable
          outline
          color="dark"
          text-color="grey-9"
          @click.stop
        >
          <q-avatar
            size="24px"
            color="dark"
            text-color="white"
          >
            <q-icon name="person" size="14px" />
          </q-avatar>
          <span class="q-ml-sm text-weight-medium">{{ m.profile_name }}</span>
        </q-chip>
      </div>
    </q-card-section>

    <!-- Footer -->
    <q-separator />
    <q-card-section class="bg-grey-1 q-py-sm">
      <div class="row items-center justify-end text-grey-6">
        <span class="text-caption text-weight-medium">View details</span>
        <q-icon name="chevron_right" size="20px" />
      </div>
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
