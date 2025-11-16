<template>
  <q-card flat bordered class="rounded-borders" :style="`border-left: 4px solid ${color}`">
    <!-- Header -->
    <q-card-section class="header q-py-sm q-px-md">
      <div class="row items-center no-wrap full-width">

        <!-- Name + optional rank -->
        <div class="col">
          <div class="row items-center no-wrap">
            <div class="name-wrap">
              <span class="name-text text-subtitle2 text-weight-medium ellipsis">
                {{ member.username }}
              </span>

              <!-- Tiny active dot -->
              <span
                v-if="member.is_active_player"
                class="active-dot"
              />
            </div>

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

        <!-- Small meta icons -->
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
  defineProps<{ member: any; color?: string }>(),
  { color: 'var(--q-primary)' }
);
</script>

<style scoped>
/* Keep the name container tight and relative so the dot can float on it */
.name-wrap {
  position: relative;
  display: inline-block;
  max-width: 100%;
  line-height: 1.2;
}

/* Ellipsis already exists on the span; ensure it doesn’t get pushed by the dot */
.name-text {
  display: inline-block;
  max-width: 100%;
  vertical-align: middle;
  padding-right: 12px; /* breathing room so the dot doesn’t overlap letters */
}

/* The dot itself */
.active-dot {
  position: absolute;
  top: -2px;        /* tweak to taste */
  right: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--q-positive);
  /* ring for contrast against any background */
  box-shadow: 0 0 0 2px var(--q-card-bg, #fff);
}

/* Optional: if you use dark mode, give the ring a darker fallback */
:root[class*="body--dark"] .active-dot {
  box-shadow: 0 0 0 2px rgba(0,0,0,.6);
}
</style>
