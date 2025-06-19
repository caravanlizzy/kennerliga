<template>
  <div class="selected-game-card">
    <!-- Selected Game -->
    <div v-if="member.selected_game" class="game-container">
      <div
        class="card-header row items-start justify-between"
        :class="{ 'cursor-pointer': isBannable }"
      >
        <div class="column">
          <div class="row items-center no-wrap">
            <div class="text-subtitle1 text-weight-medium">
              {{ member.selected_game.game_name }}
            </div>
            <q-badge
              v-if="isBannable"
              color="white"
              text-color="accent"
              class="bannable-badge q-ml-sm"
              @click.stop="openBanDialog"
            >
              Bannen
            </q-badge>
          </div>

          <!-- Banner Container -->
          <div class="banners-wrapper">
            <div class="banner-label">Gebannt von:</div>
            <div class="row q-gutter-xs banner-list">
              <UserName
                v-for="username of bannerUsernamesForMyGame"
                :key="username"
                :username="username"
              />
            </div>
          </div>
        </div>

        <q-btn
          flat
          dense
          round
          icon="expand_more"
          class="material-symbols-outlined expand-btn"
          :class="{ 'rotate-180': isExpanded }"
          @click="isExpanded = !isExpanded"
          color="grey-8"
        />
      </div>

      <q-card-section v-if="isExpanded" class="card-body">
        <q-separator spaced />
        <q-list dense>
          <q-item
            v-for="option in member.selected_game.selected_options"
            :key="option.id"
          >
            <q-item-section>{{ option.game_option.name }}</q-item-section>
            <q-item-section side class="text-right">
        <span v-if="option.choice" class="text-secondary">
          {{ option.choice.name }}
        </span>
              <q-icon
                v-else-if="option.value === true"
                name="check"
                color="grey-7"
              />
              <q-icon
                v-else-if="option.value === false"
                name="close"
                color="grey-5"
              />
              <q-icon v-else name="help" color="grey" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>

    </div>

    <!-- Banned Game -->
    <div v-if="member.banned_game" class="q-mt-sm">
      <div class="text-caption text-weight-medium">Gebanntes Spiel:</div>
      <div class="text-body2 text-weight-bold text-secondary">
        {{ member.banned_game.game_name || 'Nichts' }}
      </div>
    </div>

    <!-- Confirm Ban Dialog -->
    <q-dialog v-model="confirmDialog">
      <q-card>
        <q-card-section class="text-h6">
          {{ member.selected_game?.game_name }} bannen?
        </q-card-section>

        <q-card-section>
          Sicher dass du
          <span class="text-weight-bold">{{
              member.selected_game?.game_name
            }}</span>
          von <span class="text-weight-bold">{{ member.username }}</span> bannen
          willst?
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Abbrechen" color="primary" v-close-popup />
          <q-btn unelevated label="Bannen" color="accent" @click="confirmBan" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, ref } from 'vue';
import { useUserStore } from 'stores/userStore';
import { banGame } from 'src/services/game/banGameService';
import UserName from 'components/ui/UserName.vue';

const props = defineProps<{
  member: any;
  status: string;
  isActive: boolean;
  isBannable: boolean;
}>();

const league = inject('league');
const fetchLeagueDetails = inject('fetchLeagueDetails');
const { user } = useUserStore();

const isExpanded = ref(false);
const confirmDialog = ref(false);

function openBanDialog() {
  confirmDialog.value = true;
}

function getSelectedGameForMember() {
  const member = league.value.members.find(
    (m) => m.username === props.member.username
  );
  return member.selected_game;
}

function getBannersOfGame(game: { id: number }): string[] {
  if (!league.value?.members) return [];
  return league.value.members
    .filter((m) => m.banned_game?.id === game.id)
    .map((m) => m.username);
}

const bannerUsernamesForMyGame = computed(() => {
  const myGame = getSelectedGameForMember();
  if (!myGame) return [];
  return getBannersOfGame(myGame);
});

async function confirmBan() {
  confirmDialog.value = false;
  if (!user?.username || !league.value?.id) {
    throw new Error('Missing required parameters');
  }
  try {
    banGame({
      leagueId: league.value.id,
      username: user.username,
      gameId: props.member.selected_game.id,
    });
    fetchLeagueDetails();
  } catch (error) {
    console.error(error);
  }
}
</script>

<style scoped lang="scss">
.selected-game-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  background-color: #e9eff6; // cooler light blue, more elegant than #f0f4fa
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-body {
  padding: 12px 16px;
}

.column {
  display: flex;
  flex-direction: column;
}

.banner-list {
  flex-wrap: wrap;
}

.bannable-badge {
  cursor: pointer;
  font-size: 0.7rem;
  font-weight: bold;
  padding: 3px 8px;
  border-radius: 10px;
  border: 1px solid #f76c9f;
  background-color: rgba(247, 108, 159, 0.1);
  transition: transform 0.2s ease;
}

.banners-wrapper {
  margin-top: 4px;
  min-height: 35px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.banner-label {
  font-size: 0.75rem;
  color: #888;
  white-space: nowrap;
}

.bannable-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.expand-btn {
  transition: transform 0.3s ease;
  margin-top: 2px;
}

.rotate-180 {
  transform: rotate(180deg);
}
</style>
