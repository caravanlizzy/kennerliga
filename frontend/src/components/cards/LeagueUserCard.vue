<template>
  <div
    class="q-pa-xl rounded-borders relative full-height"
    :style="{
      minHeight: '240px',
    }"
  >
    <!-- Header -->
    <div class="row items-center justify-between">
      <div class="text-subtitle1 text-weight-bold">
        {{ member.username }}
        <!-- Aktiv Badge -->
        <q-badge
          v-if="isActive"
          color="accent"
          text-color="white"
          class="q-mr-xs q-ml-md"
        >
          <q-icon name="play_arrow" size="16px" class="q-mr-xs" />
        </q-badge>
      </div>

      <div class="row q-gutter-xs items-center">

        <q-badge
          v-if="member.selected_game"
          color="secondary"
          text-color="white"
        >
          GAME
        </q-badge>
        <q-badge
          v-if="member.banned_game"
          color="negative"
          text-color="white"
        >
          BAN
        </q-badge>
      </div>
    </div>

    <!-- Game Info -->
    <div class="q-mt-xl">
      <div v-if="member.selected_game" class="q-mb-sm">
        <div class="text-body2 text-weight-bold">
          {{ member.selected_game }}
        </div>
      </div>

      <div v-if="member.banned_game">
        <div class="text-caption text-weight-medium">Gebanntes Spiel:</div>
        <div class="text-body2 text-weight-bold text-negative">
          {{ member.banned_game }}
        </div>
      </div>

      <div
        v-if="!member.selected_game && !member.banned_game"
        class="text-caption text-grey-6"
      >
        Noch keine Auswahl oder Bann.
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
defineProps<{
  member: any;
  isActive: boolean;
}>();
</script>
