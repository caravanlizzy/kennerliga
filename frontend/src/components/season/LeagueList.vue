<template>
  <q-item
    :clickable="isAdmin"
    :v-ripple="isAdmin"
    class="q-py-md league-item"
    :class="{ 'cursor-pointer': isAdmin, 'bg-grey-1': league.is_completed }"
    @click="isAdmin ? goToLeague(league) : undefined"
  >
    <q-item-section avatar>
      <LeagueLevel :level="league.level" size="40px" fontSize="16px" />
    </q-item-section>

    <q-item-section>
      <div class="row items-center q-gutter-x-sm q-mb-xs">
        <span class="text-subtitle1 text-weight-bold text-dark"
          >League {{ league.level }}</span
        >
        <q-badge v-if="league.is_completed" color="positive" class="q-pa-xs">
          <q-icon name="check_circle" size="12px" class="q-mr-xs" />
          <span>Complete</span>
        </q-badge>
      </div>

      <div class="row items-center q-gutter-x-sm wrap">
        <span class="text-caption text-grey-6 text-weight-bold">Players:</span>
        <template v-if="league.members?.length">
          <div
            v-for="m in league.members"
            :key="m.id"
            class="row items-center q-gutter-x-xs q-mr-sm"
            @click.stop
          >
            <div class="player-dot" />
            <span class="text-caption text-grey-8">{{ m.profile_name }}</span>
          </div>
        </template>
        <span v-else class="text-caption text-grey-5 italic">None</span>
      </div>

      <div
        v-if="league.progress"
        class="row items-center q-gutter-xs q-mt-xs wrap league-progress-row"
      >
        <div
          class="progress-pill"
          :class="{
            'progress-pill--done': league.progress.picks.missing === 0,
          }"
        >
          <q-icon name="touch_app" size="13px" class="q-mr-xs" />
          <span class="text-weight-medium">Picks:</span>
          <span class="q-ml-xs text-weight-bold"
            >{{ league.progress.picks.current }}/{{
              league.progress.picks.total
            }}</span
          >
          <span
            v-if="league.progress.picks.missing > 0"
            class="missing-count q-ml-xs"
            >({{ league.progress.picks.missing }} missing)</span
          >
          <q-icon
            v-else
            name="check"
            size="13px"
            class="q-ml-xs text-positive"
          />
        </div>

        <div
          class="progress-pill"
          :class="{ 'progress-pill--done': league.progress.bans.missing === 0 }"
        >
          <q-icon name="block" size="13px" class="q-mr-xs" />
          <span class="text-weight-medium">Bans:</span>
          <span class="q-ml-xs text-weight-bold"
            >{{ league.progress.bans.current }}/{{
              league.progress.bans.total
            }}</span
          >
          <span
            v-if="league.progress.bans.missing > 0"
            class="missing-count q-ml-xs"
            >({{ league.progress.bans.missing }} missing)</span
          >
          <q-icon
            v-else
            name="check"
            size="13px"
            class="q-ml-xs text-positive"
          />
        </div>

        <div
          class="progress-pill"
          :class="{
            'progress-pill--done': league.progress.reports.missing === 0,
          }"
        >
          <q-icon name="emoji_events" size="13px" class="q-mr-xs" />
          <span class="text-weight-medium">Reports:</span>
          <span class="q-ml-xs text-weight-bold"
            >{{ league.progress.reports.current }}/{{
              league.progress.reports.total
            }}</span
          >
          <span
            v-if="league.progress.reports.missing > 0"
            class="missing-count q-ml-xs"
            >({{ league.progress.reports.missing }} missing)</span
          >
          <q-icon
            v-else
            name="check"
            size="13px"
            class="q-ml-xs text-positive"
          />
        </div>
      </div>
    </q-item-section>

    <q-item-section side>
      <div class="row items-center q-gutter-x-sm">
        <q-badge outline color="grey-8" class="q-pa-xs">
          <q-icon name="group" size="14px" class="q-mr-xs" />
          <span>{{ league.members?.length || 0 }}</span>
        </q-badge>
        <KennerButton
          v-if="isAdmin"
          dense
          no-caps
          color="primary"
          icon="settings"
          size="sm"
          label="Manage"
          @click.stop="goToLeague(league)"
        />
        <KennerButton
          v-if="isAdmin"
          dense
          round
          flat
          size="sm"
          color="negative"
          icon="delete"
          :disable="league.has_results"
          @click.stop="onDelete"
        >
          <KennerTooltip>
            {{
              league.has_results
                ? 'Cannot remove: match results exist in this league'
                : 'Remove league'
            }}
          </KennerTooltip>
        </KennerButton>
      </div>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
import { TLeagueDto } from 'src/types';
import { useRouter } from 'vue-router';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import LeagueLevel from './LeagueLevel.vue';

const props = defineProps<{ league: TLeagueDto }>();
const emit = defineEmits<{
  (e: 'delete', league: TLeagueDto): void;
}>();

const router = useRouter();
const { isAdmin } = storeToRefs(useUserStore());

function goToLeague(league: TLeagueDto) {
  router.push({
    name: 'league-manager',
    params: { id: league.season, leagueId: league.id },
  });
}

function onDelete() {
  if (props.league.has_results) return;
  emit('delete', props.league);
}
</script>

<style scoped lang="scss">
.league-item {
  transition: background-color 0.2s ease;

  &:hover {
    background: var(--kenner-surface-subtle);
  }
}

.player-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--q-primary);
  opacity: 0.6;
}

.league-progress-row {
  margin-top: 6px;
  gap: 6px;
}

.progress-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 12px;
  background: var(--kenner-surface-subtle, #f5f5f5);
  border: 1px solid var(--kenner-border-subtle, #e0e0e0);
  color: var(--kenner-text-secondary, #616161);

  .missing-count {
    color: var(--q-warning, #f57c00);
    font-weight: 500;
  }

  &--done {
    border-color: rgba(46, 125, 50, 0.25);
    background: rgba(46, 125, 50, 0.08);
    color: var(--q-positive, #2e7d32);
  }
}
</style>
