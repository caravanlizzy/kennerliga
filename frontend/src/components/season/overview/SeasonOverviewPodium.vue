<template>
  <div
    class="champions-card"
    :class="isMobile ? 'q-mx-md q-pa-md' : 'q-pa-md q-pa-sm-lg'"
  >
    <div class="row items-center q-gutter-x-sm q-mb-md">
      <div class="champions-icon-wrap">
        <q-icon name="emoji_events" color="amber-8" size="24px" />
      </div>
      <div>
        <div class="text-subtitle1 text-weight-bold text-dark">
          Season Champions
        </div>
        <div class="text-caption text-grey-6">
          Podium winners and league champions
        </div>
      </div>
    </div>
    <SeasonWinners :season-id="seasonId" />
  </div>
</template>

<script setup lang="ts">
import SeasonWinners from 'components/season/SeasonWinners.vue';

defineProps<{
  seasonId: number;
  isMobile: boolean;
}>();
</script>

<style scoped>
.champions-card {
  background: linear-gradient(
    135deg,
    rgba(255, 248, 225, 0.6) 0%,
    rgba(255, 255, 255, 0.9) 100%
  );
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 14px;
}
.body--dark .champions-card {
  background: linear-gradient(
    135deg,
    rgba(255, 193, 7, 0.08) 0%,
    rgba(30, 30, 30, 0.9) 100%
  );
  border-color: rgba(255, 193, 7, 0.2);
}
.champions-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 193, 7, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
