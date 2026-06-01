<template>
  <div />
</template>

<script setup lang="ts">
import { h, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { QCard, QCardSection, QIcon, QSeparator } from 'quasar';
import { useMyLeagueStore } from 'src/composables/myLeague';
import { useActionBar } from 'src/composables/actionBar';
import { banGame } from 'src/services/gameService';
import type { TSeasonParticipantDto, TSelectedGameDto } from 'src/types';

// Statuses whose action-bar contents are owned by this section.
const OWNED_STATUSES = ['BANNING'] as const;
type TOwnedStatus = (typeof OWNED_STATUSES)[number];

const isOwnedStatus = (status: unknown): status is TOwnedStatus =>
  OWNED_STATUSES.includes(status as TOwnedStatus);

interface TBanCandidate extends TSelectedGameDto {
  owner_name: string;
}

const myLeagueStore = useMyLeagueStore();
const {
  isMeBanningGame,
  leagueStatus,
  members,
  myProfileId,
  leagueId,
} = storeToRefs(myLeagueStore);
const { updateLeagueData } = myLeagueStore;

const { setActions, setLeadText, setSubject, reset } = useActionBar();

function buildCandidates(): TBanCandidate[] {
  const out: TBanCandidate[] = [];
  members.value.forEach((m: TSeasonParticipantDto) => {
    // Players can't ban their own picks
    if (m.profile === myProfileId.value) return;
    (m.selected_games || []).forEach((sg: TSelectedGameDto) => {
      out.push({ ...sg, owner_name: m.profile_name });
    });
  });
  return out;
}

async function performBan(selectedGameId?: number, skip = false) {
  if (myProfileId.value == null || leagueId.value == null) return;
  try {
    await banGame({
      profileId: myProfileId.value,
      leagueId: leagueId.value,
      selectedGameId: skip ? undefined : selectedGameId,
      skip,
    });
    await updateLeagueData();
  } catch (e) {
    console.error('Error banning game:', e);
  }
}

function renderCandidateList(candidates: TBanCandidate[]) {
  if (!candidates.length) {
    return () =>
      h(
        'div',
        { class: 'row items-center q-gutter-sm text-grey-7 q-py-sm' },
        [
          h(QIcon, { name: 'info', size: 'sm', color: 'grey-5' }),
          h('span', 'No games available to ban.'),
        ]
      );
  }

  return () =>
    h(
      'div',
      { class: 'ban-candidate-grid q-mt-sm' },
      candidates.map((c, idx) =>
        h(
          QCard,
          {
            key: c.id,
            flat: true,
            bordered: true,
            class: 'ban-candidate-card cursor-pointer',
            onClick: () => performBan(c.id, false),
          },
          {
            default: () => [
              h(
                QCardSection,
                { class: 'row items-center no-wrap q-pa-sm' },
                {
                  default: () => [
                    h(
                      'div',
                      {
                        class:
                          'ban-candidate-index text-caption text-weight-bold text-grey-6 q-mr-sm',
                      },
                      String(idx + 1).padStart(2, '0')
                    ),
                    h('div', { class: 'col' }, [
                      h(
                        'div',
                        { class: 'text-weight-bold text-dark ellipsis' },
                        c.game_name
                      ),
                      h(
                        'div',
                        { class: 'text-caption text-grey-7 ellipsis' },
                        [
                          h(QIcon, {
                            name: 'person',
                            size: '14px',
                            class: 'q-mr-xs',
                          }),
                          `Picked by ${c.owner_name}`,
                        ]
                      ),
                    ]),
                    h(QIcon, {
                      name: 'block',
                      size: 'sm',
                      color: 'negative',
                      class: 'q-ml-sm ban-candidate-icon',
                    }),
                  ],
                }
              ),
            ],
          }
        )
      )
    );
}

function manageActionBar() {
  if (!isOwnedStatus(leagueStatus.value)) return;
  if (!isMeBanningGame.value) return;

  const candidates = buildCandidates();

  setLeadText('Ban a game picked by another player');
  setSubject(() =>
    h('div', [
      h(
        'div',
        { class: 'text-body2 text-grey-7 q-mb-xs' },
        candidates.length
          ? 'Click a game to ban it, or skip your ban.'
          : ''
      ),
      h(QSeparator, { class: 'q-my-xs' }),
      renderCandidateList(candidates)(),
    ])
  );

  setActions([
    {
      name: 'Skip Ban',
      buttonVariant: 'grey-7',
      callback: () => performBan(undefined, true),
    },
  ]);
}

// Re-render the action bar when ban-relevant inputs change.
watch(
  [leagueStatus, isMeBanningGame, members],
  manageActionBar,
  { immediate: true, deep: true }
);

// When leaving the BANNING status, clear the action bar so a later remount
// doesn't start from stale values.
watch(
  leagueStatus,
  (status, prev) => {
    if (isOwnedStatus(prev) && !isOwnedStatus(status)) {
      reset();
    }
  },
  { immediate: true }
);
</script>

<style lang="scss">
/* Global styles: this component renders into ActionBar via a render fn,
   so scoped styles wouldn't reach the nodes. */
.ban-candidate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 8px;
}

.ban-candidate-card {
  border-radius: 10px;
  transition: all 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.08);

  &:hover {
    border-color: var(--q-negative);
    background: rgba(193, 0, 21, 0.04);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    .ban-candidate-icon {
      transform: scale(1.1);
    }
  }
}

.ban-candidate-icon {
  transition: transform 0.2s ease;
}

.ban-candidate-index {
  min-width: 22px;
  text-align: center;
  letter-spacing: 0.05em;
}
</style>
