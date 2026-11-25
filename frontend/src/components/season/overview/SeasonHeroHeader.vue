<template>
  <div
    class="row items-center justify-between"
    :class="isMobile ? 'q-px-md q-py-sm border-bottom-subtle' : 'q-mb-md q-mb-sm-lg'"
  >
    <div class="row items-center q-gutter-x-sm no-wrap col ellipsis">
      <KennerButton
        flat
        round
        dense
        icon="arrow_back"
        color="grey-7"
        :to="{ name: 'seasons' }"
      >
        <KennerTooltip>Back to Seasons</KennerTooltip>
      </KennerButton>
      <div class="column col ellipsis">
        <div class="row items-center q-gutter-x-sm no-wrap">
          <h1
            class="text-h6 text-sm-h5 text-weight-bolder text-dark tracking-tight q-my-none ellipsis"
          >
            {{ seasonTitle }}
          </h1>
          <div
            v-if="seasonStatusLabel === 'RUNNING'"
            class="season-live-badge row items-center no-wrap q-gutter-x-xs q-px-sm q-py-xs rounded-borders shrink-0"
          >
            <span class="pulse-dot" />
            <span class="text-weight-bolder text-uppercase live-text"
              >Running</span
            >
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
import KennerTooltip from 'components/base/KennerTooltip.vue';

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
  background: rgba(33, 186, 69, 0.12);
  color: var(--q-positive, #21ba45);
  font-size: 11px;
  letter-spacing: 0.5px;
  border: 1px solid rgba(33, 186, 69, 0.3);
}
.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--q-positive, #21ba45);
  box-shadow: 0 0 0 0 rgba(33, 186, 69, 0.7);
  animation: pulse-ring 1.8s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
  display: inline-block;
}
@keyframes pulse-ring {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(33, 186, 69, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(33, 186, 69, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(33, 186, 69, 0);
  }
}
</style>
