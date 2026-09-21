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
              {{ truncateString(member.selected_game.game_name || '') }}
              <KennerTooltip v-if="(member.selected_game.game_name || '').length > 28">
                {{ member.selected_game.game_name }}
              </KennerTooltip>
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
                <KennerTooltip>Not active anymore (banned by others)</KennerTooltip>
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

        <KennerButton
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
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import type { TSelectedGameDto } from 'src/types';

/**
 * The member shape this card renders. The game/option pieces reuse the
 * shared DTOs rather than re-declaring trimmed copies, which is how they
 * previously drifted away from `types/game.ts`.
 */
type SelectedGameRef = Pick<
  TSelectedGameDto,
  'id' | 'game' | 'game_name' | 'selected_options'
>;

type Member = {
  id: number;
  username: string;
  profile_name: string;
  selected_game: SelectedGameRef | null;
  banned_selected_game: SelectedGameRef | null;
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
  // `game` is the game's id on this payload, so the game's display name only
  // ever comes from `game_name` (the old nested `game.game_name` lookup could
  // never resolve).
  return props.member?.banned_selected_game?.game_name ?? null;
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
