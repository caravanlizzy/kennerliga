<template>
  <div class="selected-game-card">
    <div v-if="member.selected_game" class="game-container">
      <div class="card-header row items-start justify-between">
        <div class="column">
          <div class="row items-center no-wrap">
            <div class="text-subtitle1 text-weight-medium">
              {{ member.selected_game.game_name }}
            </div>
          </div>

          <!-- Banners -->
          <q-card flat class="q-mt-sm row q-pa-sm bg-grey-2">
            <div class="row items-center q-gutter-xs q-mb-xs q-mr-xs">
              <div>
                <q-icon name="block" size="18px" class="text-negative" />
              </div>
              <KennerTooltip>Banned by</KennerTooltip>
            </div>
            <q-separator vertical />

            <div v-if="banners.length" class="row q-ml-xs">
              <UserName
                v-for="(name, idx) in banners"
                :key="idx"
                :display-username="name"
                :color-class="'bg-grey-2'"
              />
            </div>
            <div v-else class="q-ml-sm text-grey-7">
              No bans yet
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import UserName from 'components/ui/UserName.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';

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
  // NEW from backend:
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
