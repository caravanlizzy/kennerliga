<template>
  <div class="selected-game-card">
    <!-- Selected Game -->
    <div v-if="member.selected_game" class="game-container">
      <div
        class="card-header row items-start justify-between"
        :class="{ 'cursor-pointer': isBannable(member) }"
      >
        <div class="column">
          <div class="row items-center no-wrap">
            <div class="text-subtitle1 text-weight-medium">
              {{ member.selected_game.game_name }}
            </div>

            <q-badge
              v-if="isBannable(member)"
              color="accent"
              class="q-ml-sm"
              @click.stop="openBanDialog"
            >
              <q-icon name="block" class="q-mr-xs"></q-icon>
              BAN
            </q-badge>
          </div>

          <!-- Banners -->
          <q-card flat class="q-mt-sm row q-pa-sm bg-grey-1">
            <div class="row items-center q-gutter-xs q-mb-xs q-mr-xs">
              <q-icon name="block" size="18px" class="text-negative" />
              <div class="text-caption text-weight-medium">Banned by</div>
            </div>

            <div v-if="banners.length" class="row">
              <UserName
                v-for="b in banners"
                :key="b.id"
                :username="b.username"
                :color-class="b.colorClass"
              ></UserName>
            </div>
          </q-card>
        </div>

        <q-btn
          flat
          round
          size="sm"
          icon="expand_more"
          class="transition-all"
          :class="{ 'rotate-180': isExpanded }"
          @click="isExpanded = !isExpanded"
          color="primary"
        />

      </div>

      <q-card-section v-if="isExpanded" class="card-body">
        <q-separator spaced />
        <q-markup-table flat bordered dense class="rounded-borders">
          <tbody>
          <tr
            v-for="opt in member.selected_game.selected_options"
            :key="opt.id"
          >
            <td class="text-left text-weight-medium">
              {{ opt.game_option.name }}
            </td>
            <td class="text-right">
          <span v-if="opt.choice" class="text-primary">
            {{ opt.choice.name }}
          </span>
              <q-icon v-else-if="opt.value === true" name="check_circle" color="positive" />
              <q-icon v-else-if="opt.value === false" name="cancel" color="negative" />
              <q-icon v-else name="help_outline" color="grey" />
            </td>
          </tr>
          </tbody>
        </q-markup-table>
      </q-card-section>



    </div>

    <!-- Confirm Ban Dialog -->
    <q-dialog v-model="confirmDialog">
      <q-card>
        <q-card-section class="text-h6">
          {{ member.selected_game?.game_name }} ban?
        </q-card-section>

        <q-card-section>
          Are you sure you want to ban
          <span class="text-weight-bold">{{
            member.selected_game?.game_name
          }}</span>
          by <span class="text-weight-bold">{{ member.username }}</span>
          ?
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="No, cancel" color="primary" v-close-popup />
          <q-btn unelevated label="Yes, ban" color="accent" @click="confirmBan" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { storeToRefs } from 'pinia';
import UserName from 'components/ui/UserName.vue';
import { useUserStore } from 'stores/userStore';
import { GameOption, useLeagueStore } from 'stores/leagueStore';
import { banGame } from 'src/services/game/banGameService';
import { TLeagueMember } from 'src/types';

// Reuse the types you already defined in your store file
type Choice = { id: number; name: string; option: number };

type SelectedOption = {
  id: number;
  game_option: GameOption;
  choice: Choice | null;
  value: boolean | null;
};
type SelectedGame = {
  id: number;
  game: number;
  game_name: string;
  selected_options: SelectedOption[];
};
type BannedGameFull = {
  id: number;
  game: number;
  game_name: string;
  selected_options: SelectedOption[];
};
type BannedGameEmpty = {
  game: null;
  selected_options: [];
  leagueId: null;
  playerProfileId: null;
};
type BannedGame = BannedGameFull | BannedGameEmpty;
type Member = {
  id: number;
  username: string;
  profile_name: string;
  selected_game: SelectedGame | null;
  banned_game: BannedGame;
  is_active_player: boolean;
  rank: number;
  position: number;
  colorClass?: string;
};

const props = defineProps<{
  member: Member;
  isBannable?: (m: TLeagueMember) => boolean;
}>();

const league = useLeagueStore();
const { members, leagueId, membersById } = storeToRefs(league);
const { updateLeagueData } = league;
const { user } = useUserStore();

const isExpanded = ref(false);
const confirmDialog = ref(false);

function openBanDialog() {
  confirmDialog.value = true;
}

function closeBanDialog() {
  confirmDialog.value = false;
}

function isBannedGameFull(bg: BannedGame): bg is BannedGameFull {
  return (bg as BannedGameFull).id != null;
}

const myGameId = computed(() => props.member.selected_game?.id ?? null);

const banners = computed(() => {
  const id = myGameId.value;
  if (!id) return [];
  // Members whose banned_game matches my selected_game
  return members.value
    .filter(
      (m) =>
        m.banned_game &&
        isBannedGameFull(m.banned_game) &&
        m.banned_game.id === id
    )
    .map((m) => ({
      username: m.username,
      colorClass: m.colorClass ?? 'bg-grey-2',
    }));
});

async function confirmBan() {
  closeBanDialog();
  if (!user?.username || !leagueId.value || !myGameId.value) return;
  try {
    await banGame({
      leagueId: leagueId.value, // your store has number|null, not an object
      username: user.username,
      gameId: myGameId.value,
    });
    await updateLeagueData(); // optional: expose a lighter refresh if you add one
  } catch (e) {
    console.error(e);
  }
}
</script>

<style scoped lang="scss">
.selected-game-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.rotate-180 {
  transform: rotate(180deg);
}
</style>
