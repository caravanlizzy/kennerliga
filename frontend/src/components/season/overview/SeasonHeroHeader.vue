<template>
  <div
    class="row items-center justify-between"
    :class="isMobile ? 'q-px-md q-py-sm border-bottom-subtle' : 'q-mb-md q-mb-sm-lg'"
  >
    <div class="row items-center q-gutter-x-sm no-wrap col ellipsis">
      <div class="column col ellipsis">
        <div class="row items-center q-gutter-x-sm no-wrap">
          <h1
            class="text-h6 text-sm-h5 text-weight-bolder text-dark tracking-tight q-my-none ellipsis"
          >
            {{ seasonTitle }}
          </h1>
          <div
            v-if="seasonStatusLabel === 'RUNNING'"
            class="season-live-badge row items-center no-wrap q-gutter-x-xs shrink-0"
          >
            <span class="status-dot" />
            <span class="live-text">Running</span>
          </div>
          <q-badge
            v-else-if="seasonStatusLabel"
            :color="statusColor"
            class="q-px-sm q-py-xs text-weight-bold text-caption text-uppercase shrink-0"
            rounded
          >
            {{ seasonStatusLabel }}
          </q-badge>
        </div>
        <div
          class="row items-center q-gutter-x-xs text-caption text-grey-6 ellipsis wrap q-mt-xs"
        >
          <span v-if="seasonSubtitle">{{ seasonSubtitle }}</span>
          <span v-if="seasonSubtitle && leaguesCount > 0">·</span>
          <span v-if="leaguesCount > 0">
            {{ leaguesCount }}
            {{ leaguesCount === 1 ? 'League' : 'Leagues' }}
          </span>
          <span v-if="leaguesCount > 0 && participantsCount > 0">·</span>
          <span v-if="participantsCount > 0">
            {{ participantsCount }}
            {{ participantsCount === 1 ? 'Participant' : 'Participants' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Action buttons -->
    <div class="row items-center q-gutter-x-sm shrink-0">
      <KennerButton
        v-if="isAdmin"
        outline
        color="secondary"
        icon="settings"
        :label="isMobile ? undefined : 'Manage Season'"
        :round="isMobile"
        :dense="isMobile"
        :to="{ name: 'season-manage', params: { id: seasonId } }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import KennerButton from 'components/base/KennerButton.vue';

defineProps<{
  seasonId: number;
  seasonTitle: string;
  seasonStatusLabel?: string;
  statusColor: string;
  seasonSubtitle?: string | null;
  leaguesCount: number;
  participantsCount: number;
  isAdmin: boolean;
  isMobile: boolean;
}>();
</script>

<style scoped>
.tracking-tight {
  letter-spacing: -0.02em;
}
.shrink-0 {
  flex-shrink: 0;
}
.season-live-badge {
  background: color-mix(in srgb, #15803d 14%, transparent);
  color: #15803d;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border-radius: 4px;
  padding: 2px 6px;
  border: none;
  line-height: 1.3;
}
.status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: currentColor;
  opacity: 0.9;
  display: inline-block;
}
body.body--dark .season-live-badge,
.body--dark .season-live-badge {
  background: color-mix(in srgb, #4ade80 22%, transparent);
  color: #4ade80;
  border: none;
}
</style>
