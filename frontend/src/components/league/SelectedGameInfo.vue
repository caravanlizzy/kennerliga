<template>
  <div class="q-mt-xl">
    <!-- Selected Game -->
    <div v-if="member.selected_game" class="q-mb-sm">
      <q-card
        :flat="status !== 'BANNING'"
        bordered
        class="q-mb-md q-pa-sm shadow-1 hover-card"
        :class="{ 'cursor-pointer ': isBannable }"
      >
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">
            {{ member.selected_game.game_name }}
            <q-badge
              v-if="isBannable"
              color="accent"
              text-color="white"
              class="bannable-badge q-ml-md"
              @click.stop="openBanDialog"
            >
              Bannen
            </q-badge>
          </div>
          {{myBansBannedBy}}
          <q-btn
            flat
            dense
            round
            icon="expand_more"
            class="material-symbols-outlined"
            :class="{ 'rotate-180': isExpanded }"
            @click="isExpanded = !isExpanded"
            color="primary"
          />
        </q-card-section>

        <q-slide-transition>
          <div v-show="isExpanded">
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
                    name="check_circle"
                    color="positive"
                  />
                  <q-icon
                    v-else-if="option.value === false"
                    name="cancel"
                    color="negative"
                  />
                  <q-icon v-else name="help" color="grey" />
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </q-slide-transition>
      </q-card>
    </div>

    <!-- Banned Game -->
    <div v-if="member.banned_game">
      <div class="text-caption text-weight-medium">Gebanntes Spiel:</div>
      <div class="text-body2 text-weight-bold text-negative">
        {{ member.banned_game.game_name }}
      </div>
    </div>

    <!-- Nothing Selected -->
    <div
      v-if="!member.selected_game && !member.banned_game"
      class="text-caption text-grey-6"
    >
      Noch keine Auswahl oder Bann.
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

const props = defineProps<{
  member: any;
  status: string;
  isActive: boolean;
  isBannable: boolean;
}>();

const league = inject('league');
const { user } = useUserStore();

const isExpanded = ref(false);
const confirmDialog = ref(false);

function openBanDialog() {
  confirmDialog.value = true;
}

function findMyGame(){
  const member =  league.value.members.find((member) => member.username = props.member.username);
  console.log(member.username);
  return member.selected_game;
}

function findBanners(game: { id: number }): string[] {
  if (!league.value?.members) {
    return [];
  }
  const members = league.value.members.filter(member => member.banned_game.id === game.id);
  return members.map(member => member.username);
}


const myBansBannedBy = computed(() => {
  const myGame = findMyGame();
  if(!myGame) return [];
  return findBanners(myGame);
})

async function confirmBan() {
  confirmDialog.value = false;
  if (!user?.username || !league.value.id) {
    throw new Error('Missing required parameters');
  }
  banGame({
    leagueId: league.value.id,
    username: user.username,
    gameId: props.member.selected_game.id, // Should come from a parameter or state
  });
}
</script>

<style scoped lang="scss">
.rotate-180 {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba($accent, 0.6);
  }
  70% {
    transform: scale(1.15);
    box-shadow: 0 0 0 12px rgba($accent, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba($accent, 0);
  }
}

.bannable-badge {
  cursor: pointer;
  font-weight: bold;
  border-radius: 12px;
  font-size: 1.1rem;
  padding: 4px 10px;
  animation: pulse 1.6s infinite;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.bannable-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.3);
}
</style>
