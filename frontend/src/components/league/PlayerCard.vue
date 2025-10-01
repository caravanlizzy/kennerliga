<template>
  <q-card flat bordered class="q-ma-sm rounded-borders">
    <!-- Header -->
    <q-card-section class="row justify-between items-center q-py-xs">

      <!-- Username + active indicator -->
      <div class="row items-center no-wrap">
        <!-- subtle avatar dot -->
        <q-avatar size="18px" class="q-mr-sm header-avatar">
          <q-icon name="person" size="14px" />
        </q-avatar>

        <span class="text-subtitle2 text-weight-medium ellipsis maxw-username">
        {{ member.username }}
      </span>
        <q-tooltip v-if="(member.username || '').length > 18">
          {{ member.username }}
        </q-tooltip>

        <q-badge
          v-if="member.is_active_player"
          outline rounded color="positive" text-color="positive" class="q-ml-sm"
        >
          <q-icon name="verified" size="14px" class="q-mr-xs" />
          Active
        </q-badge>

        <!-- optional: rank adds nice structure if available -->
        <q-badge v-if="member.rank !== undefined" outline class="q-ml-sm text-caption" color="grey-6" text-color="grey-8">
          #{{ member.rank }}
        </q-badge>
      </div>

      <!-- Badges (outline, semantic) -->
      <div class="row items-center q-gutter-xs no-wrap">
        <q-badge v-if="member.selected_game" color="positive">
          <q-icon name="sports_esports" size="14px" />
          <q-tooltip>Has a selected game</q-tooltip>
        </q-badge>

        <q-badge v-if="member.has_banned" color="negative">
          <q-icon name="block" size="14px" />
          <q-tooltip>Submitted a ban</q-tooltip>
        </q-badge>
      </div>
    </q-card-section>

    <!-- a hairline to separate header/body more clearly -->
    <q-separator />

    <!-- Body -->
    <q-card-section class="q-pa-md bg-grey-1">
      <SelectedGameInfo :member="member" />
    </q-card-section>
  </q-card>

</template>

<script setup lang="ts">
import SelectedGameInfo from 'components/league/SelectedGameInfo.vue';

defineProps<{ member: any }>();
</script>
