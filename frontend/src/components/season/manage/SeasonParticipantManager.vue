<template>
  <div class="season-summary q-mb-lg">
    <div
      class="season-summary__header row items-center q-gutter-x-sm q-px-md q-py-sm"
    >
      <div class="stat-pill">{{ leagues.length }} leagues</div>
      <div class="stat-pill">{{ participants.length }} players</div>
      <div
        v-if="seasonStatusLabel"
        class="status-pill"
        :class="`status-pill--${statusColor}`"
      >
        {{ seasonStatusLabel }}
      </div>
    </div>

    <div class="season-summary__divider" />

    <q-expansion-item
      label="Show participants"
      header-class="text-grey-7"
      dense
      expand-icon-class="text-grey-7"
    >
      <div class="q-px-md q-pt-sm q-pb-md">
        <div
          class="row items-center justify-between q-mb-sm q-col-gutter-sm"
        >
          <div v-if="participants.length > 4" class="col-12 col-sm-6">
            <KennerInput
              v-model="search"
              placeholder="Search participants..."
              dense
              class="full-width"
            >
              <template #prepend>
                <q-icon name="search" size="18px" color="grey-6" />
              </template>
              <template #append v-if="search">
                <q-icon
                  name="clear"
                  size="18px"
                  class="cursor-pointer"
                  @click="search = ''"
                />
              </template>
            </KennerInput>
          </div>
          <div
            v-if="isAdmin"
            :class="[
              'row justify-end',
              participants.length > 4 ? 'col-12 col-sm-6' : 'col-12',
            ]"
          >
            <KennerButton
              outline
              no-caps
              size="sm"
              color="primary"
              icon="person_add"
              label="Add Participant"
              @click="$emit('open-add-participant')"
            />
          </div>
        </div>

        <div v-if="participants.length > 0">
          <div
            v-if="filteredParticipantsByLeague.length === 0 && search"
            class="text-caption text-grey-6 italic q-py-sm"
          >
            No participants matching "{{ search }}"
          </div>
          <div
            v-for="group in filteredParticipantsByLeague"
            :key="group.league?.id || 'unassigned'"
            class="q-mb-md"
          >
            <div class="row items-center q-gutter-x-sm q-mb-xs">
              <template v-if="group.league">
                <LeagueLevel
                  :level="group.league.level"
                  size="20px"
                  font-size="10px"
                />
                <span class="text-caption text-weight-bold"
                  >League {{ group.league.level }}</span
                >
              </template>
              <template v-else>
                <q-icon name="help_outline" size="16px" color="grey-6" />
                <span class="text-caption text-weight-bold text-grey-6"
                  >Unassigned</span
                >
              </template>
              <div class="text-caption text-grey-6">
                ({{ group.members.length }})
              </div>
            </div>
            <div
              v-if="group.members.length > 0"
              class="column q-gutter-y-xs q-pl-md q-mt-xs"
            >
              <div
                v-for="p in group.members"
                :key="p.id"
                class="row items-center justify-between q-py-xs participant-row"
              >
                <div class="row items-center q-gutter-x-sm">
                  <div class="player-dot" />
                  <span class="text-caption text-grey-8">{{
                    p.profile_name
                  }}</span>
                </div>
                <KennerButton
                  v-if="isAdmin"
                  flat
                  round
                  dense
                  size="xs"
                  color="negative"
                  icon="delete"
                  aria-label="Remove participant"
                  :disable="p.has_results"
                  :loading="removingParticipantId === p.id"
                  @click="$emit('remove-participant', p)"
                >
                  <KennerTooltip>
                    {{
                      p.has_results
                        ? 'Cannot remove: player has match results in this season'
                        : 'Remove participant'
                    }}
                  </KennerTooltip>
                </KennerButton>
              </div>
            </div>
            <div v-else class="text-caption text-grey-5 italic q-ml-md">
              No players
            </div>
          </div>
        </div>
        <div v-else class="text-caption text-grey-6 italic">
          No registered players for this season.
        </div>
      </div>
    </q-expansion-item>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import type { TLeagueDto, TSeasonParticipantDto } from 'src/types';

const props = defineProps<{
  leagues: TLeagueDto[];
  participants: TSeasonParticipantDto[];
  isAdmin: boolean;
  removingParticipantId: number | null;
  seasonStatusLabel: string;
  statusColor: string;
}>();

defineEmits<{
  (e: 'open-add-participant'): void;
  (e: 'remove-participant', participant: TSeasonParticipantDto): void;
}>();

const search = ref('');

const participantsByLeague = computed(() => {
  const groups: {
    league: TLeagueDto | null;
    members: TSeasonParticipantDto[];
  }[] = [];

  const sortedLeagues = [...props.leagues].sort((a, b) => {
    const levelA = typeof a.level === 'string' ? parseInt(a.level) : a.level;
    const levelB = typeof b.level === 'string' ? parseInt(b.level) : b.level;
    return levelA - levelB;
  });

  const assignedParticipantIds = new Set<number>();

  sortedLeagues.forEach((l) => {
    const members = l.members || [];
    members.forEach((m) => assignedParticipantIds.add(m.id));
    groups.push({ league: l, members });
  });

  const unassigned = props.participants.filter(
    (p) => !assignedParticipantIds.has(p.id)
  );
  if (unassigned.length > 0) {
    groups.push({ league: null, members: unassigned });
  }

  return groups;
});

const filteredParticipantsByLeague = computed(() => {
  const term = search.value.trim().toLowerCase();
  if (!term) return participantsByLeague.value;

  return participantsByLeague.value
    .map((group) => ({
      ...group,
      members: group.members.filter((m) =>
        m.profile_name.toLowerCase().includes(term)
      ),
    }))
    .filter((group) => group.members.length > 0);
});
</script>

<style scoped lang="scss">
.season-summary {
  background: var(--kenner-bg-glass-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--kenner-border-color);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(54, 64, 88, 0.04);
  overflow: hidden;
}

.season-summary__header {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.6) 0%,
    rgba(255, 255, 255, 0.2) 100%
  );

  .body--dark & {
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.04) 0%,
      rgba(255, 255, 255, 0.01) 100%
    );
  }
}

.season-summary__divider {
  height: 1px;
  background: linear-gradient(
    to right,
    transparent 0%,
    rgba(54, 64, 88, 0.1) 50%,
    transparent 100%
  );

  .body--dark & {
    background: linear-gradient(
      to right,
      transparent 0%,
      rgba(255, 255, 255, 0.12) 50%,
      transparent 100%
    );
  }
}

.stat-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(54, 64, 88, 0.06);
  color: var(--kenner-text-secondary);
  font-size: 12px;
  font-weight: 600;

  .body--dark & {
    background: var(--kenner-hover-bg);
  }
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  border: 1px solid transparent;
  text-transform: uppercase;
}

.status-pill--primary {
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.15) 0%,
    rgba(99, 102, 241, 0.05) 100%
  );
  color: var(--q-primary);
  border-color: rgba(99, 102, 241, 0.25);
}

.status-pill--teal-6 {
  background: linear-gradient(
    135deg,
    rgba(0, 150, 136, 0.15) 0%,
    rgba(0, 150, 136, 0.05) 100%
  );
  color: #00897b;
  border-color: rgba(0, 150, 136, 0.25);

  .body--dark & {
    color: #4db6ac;
  }
}

.status-pill--grey-7,
.status-pill--grey-6 {
  background: rgba(54, 64, 88, 0.06);
  color: var(--kenner-text-secondary);
  border-color: rgba(54, 64, 88, 0.12);

  .body--dark & {
    background: var(--kenner-hover-bg);
    border-color: var(--kenner-border-color);
  }
}

.player-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--q-primary);
  opacity: 0.6;
}

.participant-row {
  border-radius: 8px;
  padding-left: 8px;
  padding-right: 8px;
  transition: background-color 0.2s ease;

  &:hover {
    background: rgba(54, 64, 88, 0.04);

    .body--dark & {
      background: var(--kenner-hover-bg);
    }
  }
}
</style>
