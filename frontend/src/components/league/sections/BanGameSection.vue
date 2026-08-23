<template>
  <ContentSection
    v-if="showBanSection"
    title="Ban a Game"
    color="negative"
    icon="block"
    v-bind="$attrs"
  >
    <div class="text-body2 text-grey-7 q-mb-md">
      <template v-if="candidates.length">
        Click a game picked by another player to ban it, or skip your ban.
      </template>
      <template v-else>No games available to ban.</template>
    </div>

    <div v-if="candidates.length" class="ban-candidate-grid q-mb-md">
      <q-card
        v-for="(c, idx) in candidates"
        :key="c.id"
        flat
        bordered
        class="ban-candidate-card cursor-pointer"
        @click="performBan(c.id, false)"
      >
        <q-card-section class="row items-center no-wrap q-pa-sm">
          <div class="ban-candidate-index text-caption text-weight-bold text-grey-6 q-mr-sm">
            {{ String(idx + 1).padStart(2, '0') }}
          </div>
          <div class="col">
            <div class="text-weight-bold text-dark ellipsis">{{ c.game_name }}</div>
            <div class="text-caption text-grey-7 ellipsis">
              <q-icon name="person" size="14px" class="q-mr-xs" />
              Picked by {{ c.owner_name }}
            </div>
          </div>
          <q-icon name="block" size="sm" color="negative" class="q-ml-sm ban-candidate-icon" />
        </q-card-section>
      </q-card>
    </div>

    <div class="row justify-end">
      <KennerButton
        flat
        label="Skip Ban"
        color="grey-7"
        :loading="banning"
        @click="performBan(undefined, true)"
      />
    </div>
  </ContentSection>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { storeToRefs } from 'pinia';
import ContentSection from 'components/base/ContentSection.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useMyLeagueStore } from 'src/composables/myLeague';
import { banGame } from 'src/services/gameService';
import type { TSeasonParticipantDto, TSelectedGameDto } from 'src/types';

const myLeagueStore = useMyLeagueStore();
const { isMeBanningGame, leagueStatus, members, myProfileId, leagueId } =
  storeToRefs(myLeagueStore);
const { updateLeagueData } = myLeagueStore;

const banning = ref(false);

const showBanSection = computed(
  () => leagueStatus.value === 'BANNING' && isMeBanningGame.value
);

interface TBanCandidate extends TSelectedGameDto {
  owner_name: string;
}

const candidates = computed<TBanCandidate[]>(() => {
  const out: TBanCandidate[] = [];
  members.value.forEach((m: TSeasonParticipantDto) => {
    // Players can't ban their own picks
    if (m.profile === myProfileId.value) return;
    (m.selected_games || []).forEach((sg: TSelectedGameDto) => {
      out.push({ ...sg, owner_name: m.profile_name });
    });
  });
  return out;
});

async function performBan(selectedGameId?: number, skip = false) {
  if (myProfileId.value == null || leagueId.value == null) return;
  banning.value = true;
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
  } finally {
    banning.value = false;
  }
}
</script>

<style scoped lang="scss">
.ban-candidate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 8px;
}

.ban-candidate-card {
  border-radius: var(--kenner-card-radius, 16px);
  border: 1px solid var(--kenner-border-color);
  background: white;
}

.ban-candidate-index {
  min-width: 22px;
  text-align: center;
  letter-spacing: 0.05em;
}
</style>
