<template>
  <LoadingSpinner v-if="isLoading" />
  <GameSelectionForm
    v-else
    :gameInformation="gameInformation"
    :gameSelection="gameSelection"
    :visibleOptions="visibleOptions"
    :isLoading="isLoading"
    :isValid="isValid"
    :onSubmit="onSubmit"
  />
</template>

<script setup lang="ts">
import { useGameSelection } from 'src/composables/gameSelection';
import { onMounted, provide, ref } from 'vue';
import { api } from 'boot/axios';
import GameSelectionForm from 'components/game/selectedGame/GameSelectionForm.vue';
import { editSelectedGame } from 'src/services/gameService';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';

const props = defineProps<{
  leagueId: number;
  profileId: number;
  gameId: number;
  selectedGameId: number;
}>();

const isLoading = ref(true);

const {
  gameInformation,
  gameSelection,
  platforms,
  isValid,
  visibleOptions,
  initGameInformation,
  fetchPlatforms,
  toSelectedGamePayload,
} = useGameSelection(props.leagueId, props.profileId);

onMounted(async () => {
  isLoading.value = true;
  await fetchPlatforms();
  const { data: game } = await api(`game/games/${props.gameId}`);
  const { data: selection } = await api(
    `game/selected-games/${props.selectedGameId}`
  );
  gameSelection.leagueId = props.leagueId;
  gameSelection.profileId = props.profileId;
  await initGameInformation(game);
  gameSelection.selectedOptions = apiToGameSelectionOptions(
    selection.selected_options
  );
  isLoading.value = false;
});

const emit = defineEmits<{
  (e: 'on-success'): void;
}>();

provide('platforms', platforms);

async function onSubmit() {
  try {
    const payload = toSelectedGamePayload(gameSelection);
    await editSelectedGame({ id: props.selectedGameId, ...payload });
    emit('on-success');
  } catch (e) {
    console.error(e);
  }
}

function apiToGameSelectionOptions(options) {
  return options.map((option) => {
    const result =
      option.choice !== null
        ? {
            id: option.game_option.id,
            value: null,
            choice: option.choice,
            selected_game: props.selectedGameId,
          }
        : {
            id: option.game_option.id,
            value: option.value,
            choice: null,
            selected_game: props.selectedGameId,
          };
    return result;
  });
}
</script>
