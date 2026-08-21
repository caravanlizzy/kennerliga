<template>
  <q-card flat bordered class="award-card full-height">
    <q-card-section class="q-pb-none">
      <div class="row items-center no-wrap">
        <div class="stat-icon-box q-mr-sm">
          <q-icon :name="icon" color="primary" size="22px" />
        </div>
        <div class="column">
          <div class="text-subtitle1 text-weight-bolder text-dark line-height-1">
            {{ award.label }}
          </div>
          <div class="text-caption text-grey-6">{{ award.description }}</div>
        </div>
      </div>
    </q-card-section>

    <q-card-section class="q-pt-sm">
      <div v-if="award.top3.length === 0" class="text-caption text-grey-6 q-pa-sm">
        Not enough data to rank players yet.
      </div>

      <div v-else class="row q-col-gutter-sm">
        <div v-for="(entry, idx) in award.top3" :key="entry.profile_id" class="col">
          <div class="podium-player" :class="{ 'podium-player--me': entry.is_me }">
            <span class="rank-badge" :class="medalClass(idx + 1)">{{ idx + 1 }}</span>
            <div
              class="podium-player__name ellipsis"
              :class="{ 'text-weight-bolder text-primary': entry.is_me }"
            >
              {{ entry.profile_name }}
            </div>
            <div class="podium-player__score text-weight-bolder text-dark">
              {{ entry.value }}<span class="podium-player__unit"> {{ award.unit }}</span>
            </div>
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { TAward } from 'src/types';

const props = defineProps<{ award: TAward }>();

const ICONS: Record<string, string> = {
  hater: 'thumb_down',
  inspirer: 'auto_awesome',
};

const icon = computed(() => ICONS[props.award.key] ?? 'emoji_events');

function medalClass(rank: number): string {
  if (rank === 1) return 'rank-badge--gold';
  if (rank === 2) return 'rank-badge--silver';
  if (rank === 3) return 'rank-badge--bronze';
  return '';
}
</script>

<style scoped lang="scss">
.stat-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.podium-player {
  height: 100%;
  text-align: center;
  padding: 10px 6px 8px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.06);

  &--me {
    background: rgba(99, 102, 241, 0.08);
    border-color: rgba(99, 102, 241, 0.2);
  }

  &__name {
    font-size: 12px;
    line-height: 1.2;
    margin-top: 6px;
  }

  &__score {
    font-size: 15px;
    margin-top: 2px;
  }

  &__unit {
    font-size: 11px;
    font-weight: 500;
    color: #64748b;
  }
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
}

.rank-badge--gold {
  background: #f5c344;
  color: #4a3300;
}

.rank-badge--silver {
  background: #c9ccd1;
  color: #33363b;
}

.rank-badge--bronze {
  background: #d99a63;
  color: #3d2306;
}
</style>
