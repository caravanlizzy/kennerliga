<template>
  <div class="selected-game-card">
    <div v-if="member.selected_game">
      <div class="card-header row items-start justify-between">
        <div class="column">
          <div class="row items-center no-wrap">
            <q-avatar size="24px" class="q-mr-sm bg-dark text-white">
              <q-icon name="sports_esports" />
            </q-avatar>

            <div class="text-subtitle1 text-weight-medium ellipsis" >
              {{ truncateString(member.selected_game.game_name) }}
              <q-tooltip v-if="(member.selected_game.game_name || '').length > 28">
                {{ member.selected_game.game_name }}
              </q-tooltip>
            </div>
          </div>

          <!-- Banners -->
          <q-banner class="q-mt-md bg-grey-1 rounded-borders q-pa-none" dense>
            <template #avatar>
              <q-icon name="block" class="text-grey-6" />
            </template>

            <div class="row items-center no-wrap">
              <q-separator vertical inset class="q-mx-sm" />

              <!-- Subtle, neutral chip -->
              <q-chip
                v-if="bannedGameName"
                dense
                outline
                color="grey-6"
                text-color="grey-7"
                icon="do_not_disturb_on"
                class="q-ml-none text-caption q-px-sm q-py-none"
              >
                <!-- You can keep line-through, or just dim it; here we just dim -->
                <span class="text-grey-7">{{ bannedGameName }}</span>
                <q-tooltip>Not active anymore (banned by others)</q-tooltip>
              </q-chip>

              <div v-else-if="banners.length" class="row items-center q-gutter-xs">
                <UserAvatar
                  v-for="(name, idx) in banners"
                  :key="idx"
                  :display-username="name"
                  :color-class="'bg-grey-1'"
                />
              </div>

              <div v-else class="text-grey-6 text-caption">No bans yet</div>
            </div>
          </q-banner>


        </div>

        <q-btn
          flat
          round
          size="sm"
          icon="expand_more"
          class="transition-all"
          :class="{ 'rotate-180': isExpanded }"
          @click="isExpanded = !isExpanded"
          color="dark"
        />
      </div>

      <q-card-section v-if="isExpanded" class="card-body">
        <GameSettingsDisplay :selectedOptions="member.selected_game.selected_options" />
      </q-card-section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import { truncateString } from 'src/helpers';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';

// --- types trimmed to what we actually render ---
type Choice = { id: number; name: string; option: number };
type GameOption = { id: number; name: string; /* other fields omitted */ };

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

type Member = {
  id: number;
  username: string;
  profile_name: string;
  selected_game: SelectedGame | null;
  banned_selected_game: SelectedGame | null;
  banned_by: string[];           // array of display names (e.g., profile_name or username)
  selected_game_id?: number | null; // optional convenience
  is_active_player: boolean;
  rank: number;
  position: number;
  colorClass?: string;
};

const props = defineProps<{
  member: Member;
}>();

const isExpanded = ref(false);

// Directly use backend-provided banned_by
const banners = computed(() => props.member.banned_by ?? []);


const bannedGameName = computed(() => {
  const bsg = props.member?.banned_selected_game;
  // try nested first, then flat
  return bsg?.game?.game_name ?? bsg?.game_name ?? null;
});
</script>

<style scoped lang="scss">
.selected-game-card {
  border-radius: 8px;
  overflow: hidden;
}
.rotate-180 {
  transform: rotate(180deg);
}
</style>
