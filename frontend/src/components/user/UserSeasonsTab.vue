<template>
  <div class="user-seasons-tab">
    <div class="row items-center justify-between q-mb-md">
      <div class="row items-center">
        <q-icon name="history" color="teal-7" size="24px" class="q-mr-sm" />
        <div class="text-h5 text-weight-bolder text-heading tracking-tighter">Season Participation</div>
      </div>
      <div class="text-caption text-grey-6 text-uppercase text-weight-bold letter-spacing-1">{{ userSeasonList.length }} Seasons Joined</div>
    </div>
    <q-card flat bordered class="surface-card overflow-hidden">
      <q-list separator>
        <q-item
          v-for="sp in userSeasonList"
          :key="sp.id"
          clickable
          v-ripple
          @click="router.push({ name: 'season-overview', params: { id: sp.season } })"
          class="q-py-lg transition-all season-item"
        >
          <q-item-section avatar>
            <q-avatar class="season-avatar shadow-1" text-color="primary" icon="emoji_events" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-h6 text-weight-bold text-heading">{{ sp.season_details?.name || `Season ${sp.season}` }}</q-item-label>
            <div v-if="sp.league" class="q-mt-xs">
              <LeagueLevel badge :level="sp.league.level" />
            </div>
          </q-item-section>
          <q-item-section side>
            <div class="row items-center q-gutter-x-lg">
              <div class="column items-end">
                <div class="text-caption text-grey-5 text-uppercase text-weight-bolder letter-spacing-1" style="font-size: 0.6rem">
                  {{ sp.league_position_display || 'Final Rank' }}
                </div>
                <div class="row items-center">
                  <span class="text-h4 text-weight-bolder q-mr-xs" :class="getPosColorClass(sp.league_position || 0)">
                    #{{ sp.league_position || '-' }}
                  </span>
                  <q-icon v-if="sp.league_position && sp.league_position <= 3" name="workspace_premium" :color="getPosBadgeColor(sp.league_position)" size="sm" />
                </div>
              </div>
              <q-icon name="chevron_right" color="grey-3" size="md" class="gt-xs" />
            </div>
          </q-item-section>
        </q-item>
        <q-item v-if="userSeasonList.length === 0">
          <q-item-section class="text-grey-5 text-italic text-center q-pa-xl">
            <q-icon name="event_busy" size="64px" class="q-mb-md opacity-20" />
            <div class="text-h6">No seasons joined yet</div>
            <div class="text-caption">Join a league to see your history here</div>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import { TSeasonParticipantDto, TSeasonDto } from 'src/types';

defineProps<{
  userSeasonList: (TSeasonParticipantDto & { season_details?: TSeasonDto })[];
}>();

const router = useRouter();

function getPosColor(pos: number) {
  switch (pos) {
    case 1: return 'amber-8';
    case 2: return 'blue-grey-4';
    case 3: return 'orange-9';
    case 4: return 'brown-5';
    default: return 'grey-6';
  }
}

function getPosBadgeColor(pos: number) {
  return getPosColor(pos);
}

function getPosColorClass(pos: number) {
  return `text-${getPosColor(pos)}`;
}
</script>

<style scoped lang="scss">
.tracking-tighter { letter-spacing: -1px; }
.letter-spacing-1 { letter-spacing: 1px; }

.surface-card {
  background: var(--surface-bg) !important;
  border-color: var(--surface-border) !important;
  border-radius: 12px;
  box-shadow: var(--surface-shadow);
}

.season-avatar {
  background: #f1f5f9;
}

.season-item {
  &:hover {
    background: #f8fafc;
  }
}

.text-heading { color: var(--text-heading) !important; }

.transition-all {
  transition: all 0.2s ease;
}
</style>
