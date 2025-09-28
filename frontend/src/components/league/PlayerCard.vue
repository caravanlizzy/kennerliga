<template>
  <q-card flat bordered class="q-ma-sm rounded-borders">
    <!-- Header (neutral bg, subtle color dot) -->
    <q-card-section class="row justify-between items-center q-py-sm">

      <!-- Username + active indicator -->
      <div class="row items-center no-wrap">
        <!-- small color dot from member.colorClass -->
        <q-icon name="circle" :class="memberColor" size="10px" class="q-mr-sm" />
        <span class="text-subtitle2 text-weight-medium">
          {{ member.username }}
        </span>

        <!-- 'Active' is outline, positive -->
        <q-badge
          v-if="member.is_active_player"
          outline
          rounded
          color="positive"
          text-color="positive"
          class="q-ml-sm"
        >
          <q-icon name="verified" size="14px" class="q-mr-xs" />
          Active
        </q-badge>
      </div>

      <!-- Badges (outline, semantic, not filled) -->
      <div class="row items-center q-gutter-xs no-wrap">
        <q-badge v-if="member.selected_game" outline color="primary" text-color="primary">
          <q-icon name="sports_esports" size="14px" class="q-mr-xs" />
          Game
        </q-badge>

        <q-badge v-if="member.banned_game" outline color="negative" text-color="negative">
          <q-icon name="block" size="14px" class="q-mr-xs" />
          Ban
        </q-badge>
      </div>
    </q-card-section>

    <!-- Body (keep light) -->
    <q-card-section class="q-pa-sm bg-grey-1">
      <SelectedGameInfo
        :member="member"
      />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import SelectedGameInfo from 'components/league/SelectedGameInfo.vue';
import { computed } from 'vue';

const props = defineProps<{ member: any }>();

/**
 * Derive a Quasar color name from member.colorClass (e.g. 'bg-red-6' -> 'red-6').
 * Falls back to 'primary' if not present.
 */
const memberColor = computed(() => {
  const cls = props.member?.color || '';
  const first = (Array.isArray(cls) ? cls[0] : String(cls)).split(/\s+/)[0];
  const derived = first.replace(/^bg-/, '');
  return derived || 'primary';
});
</script>
