<template>
  <q-card flat unelevated class="player-card">

    <q-card-section class="card-body">

      <div class="game-primary-section">
        <div v-if="member.selected_game" class="selected-game-card">

          <!-- Game Header -->
          <div class="game-title-row">

            <!-- Inline Avatar -->
            <UserAvatar
              class="player-avatar-inline"
              :display-username="member.username"
              size="32px"
              shape="circle"
            />

            <!-- Game Title Highlight -->
            <div class="game-title-highlight">
              <div class="game-title">
                <span class="game-name-text">
                  {{ member.selected_game.game_name }}
                  <q-tooltip v-if="(member.selected_game.game_name || '').length > 28">
                    {{ member.selected_game.game_name }}
                  </q-tooltip>
                </span>
              </div>
            </div>

            <q-btn
              flat
              round
              size="sm"
              icon="expand_more"
              class="expand-btn"
              :class="{ expanded: isExpanded }"
              @click="isExpanded = !isExpanded"
            />
          </div>

          <!-- Bans Section -->
          <div class="bans-section">
            <div class="ban-row">
              <div class="bans-label">
                <q-icon name="gavel" size="16px" />
                <span>My Ban</span>
              </div>
              <div class="bans-content">
                <q-chip
                  v-if="myBannedGameName"
                  dense
                  class="my-ban-chip"
                >
                  {{ myBannedGameName }}
                </q-chip>
                <span v-else class="no-bans"></span>
              </div>
            </div>

            <div class="ban-row">
              <div class="bans-label">
                <q-icon name="group" size="16px" />
                <span>{{ firstGameSelection ? 'First Game Pick' : 'Banned By' }}</span>
              </div>
              <div class="bans-content">
                <template v-if="firstGameSelection">
                  <q-chip dense class="first-selection-chip" icon="looks_one">
                    {{ firstGameSelection }}
                  </q-chip>
                </template>

                <template v-else-if="banners.length">
                  <div class="banners-avatars">
                    <UserAvatar
                      v-for="(name, idx) in banners"
                      :key="idx"
                      :display-username="name"
                      size="28px"
              	      shape="circle"
                    />
                  </div>
                </template>

                <span v-else class="no-bans"></span>
              </div>
            </div>
          </div>

          <!-- Expandable Settings -->
          <transition name="expand">
            <div v-if="isExpanded" class="game-settings-wrapper">
              <div class="settings-divider"></div>
              <GameSettingsDisplay
                :selectedOptions="member.selected_game.selected_options"
              />
            </div>
          </transition>
        </div>

        <!-- Empty State -->
        <div v-else class="no-game-selected">
          <q-icon name="videogame_asset_off" size="32px" />
          <span>No game selected</span>
        </div>
      </div>

    </q-card-section>
  </q-card>
</template>


<script setup lang="ts">
import { ref, computed } from 'vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import { truncateString } from 'src/helpers';
import GameSettingsDisplay from 'components/game/selectedGame/GameSettingsDisplay.vue';

const props = withDefaults(defineProps<{ member: any; color?: string }>(), {
  color: 'var(--q-dark)',
});

const isExpanded = ref(false);
const banners = computed(() => props.member.banned_by ?? []);

const myBannedGameName = computed(() => {
  const mbg = props.member?.my_banned_game;
  return mbg?.game_name ?? null;
});

const firstGameSelection = computed(() => {
  const fgs = props.member?.first_game_selection;
  return fgs?.game_name ?? fgs?.game?.game_name ?? null;
});
</script>

<style scoped lang="scss">

.player-card {
  border-radius: 14px;
  padding: 16px;
}

/* GAME TITLE ROW */
.game-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.player-avatar-inline {
  flex-shrink: 0;
}

.game-title-highlight {
  flex: 1;
  padding: 6px 0;
  position: relative;
  /* No border, no background = clean */
}

.game-title-highlight::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: #3dadea; /* primary color */
  border-radius: 3px;
}

.game-name-text {
  font-size: 18px;
  font-weight: 700;
  color: #222;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* CHIPS – clean white with soft gray border */
.q-chip {
  background: #fff !important;
  border: 1px solid #e5e7eb !important;
  font-size: 13px;
  padding: 4px 10px !important;
  border-radius: 8px !important;
}

/* RED CHIP */
.my-ban-chip {
  color: #dc2626 !important;
  border-color: #fecaca !important;
}

/* BLUE CHIP */
.first-selection-chip {
  color: #1e3a8a !important;
  border-color: #bfdbfe !important;
}

/* BANS SECTION – no background, no border */
.bans-section {
  margin-top: 6px;
}

.ban-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.bans-label {
  width: 110px;
  font-size: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
}

.no-bans {
  color: #9ca3af;
  font-style: italic;
}


</style>

