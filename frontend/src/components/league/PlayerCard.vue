<template>
  <q-card flat bordered class="rounded-borders" :style="`border-left: 4px solid ${color}`">
    <!-- Header -->
    <q-card-section class="header q-py-sm q-px-md ">
      <div class="row items-center no-wrap full-width">
        <!-- Avatar with tiny active dot -->
        <q-avatar size="24px" class="q-mr-sm">
          <q-icon name="person" size="16px" />
          <q-badge
            v-if="member.is_active_player"
            floating
            rounded
            color="positive"
            class="dot-badge"
          />
        </q-avatar>

        <!-- Name + optional rank -->
        <div class="col text-truncate">
          <div class="row items-center no-wrap">
            <span class="text-subtitle2 text-weight-medium ellipsis">
              {{ member.username }}
            </span>
            <q-tooltip v-if="(member.username || '').length > 18">
              {{ member.username }}
            </q-tooltip>

            <span
              v-if="member.rank !== undefined"
              class="text-caption text-grey-7 q-ml-sm"
            >
              #{{ member.rank }}
            </span>
          </div>
        </div>

        <!-- Small meta icons (lighter than badges) -->
        <div class="row items-center no-wrap q-ml-auto meta-icons">
          <q-icon
            v-if="member.selected_game"
            name="sports_esports"
            size="16px"
            class="text-positive"
          >
            <q-tooltip>Has a selected game</q-tooltip>
          </q-icon>

          <q-icon
            v-if="member.has_banned"
            name="block"
            size="16px"
            class="text-negative q-ml-xs"
          >
            <q-tooltip>Submitted a ban</q-tooltip>
          </q-icon>
        </div>
      </div>
    </q-card-section>

    <!-- Hairline -->
    <q-separator class="hairline" color="info" />

    <!-- Body -->
    <q-card-section class="q-pt-sm q-pb-md q-pl-md q-pr-md">
      <SelectedGameInfo :member="member" />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import SelectedGameInfo from 'components/league/SelectedGameInfo.vue';

withDefaults(
  defineProps<{ member: any, color: string }>(),
  { color: 'var(--q-primary)' }
)
</script>
