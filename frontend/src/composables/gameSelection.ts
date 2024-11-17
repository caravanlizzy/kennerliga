import { ref, reactive, computed } from 'vue';
import {
  GameDto,
  GameOptionDto,
  SelectedGameDto,
  SelectedGameOptionDto,
} from 'src/models/gameModels';
import {
  createSelectedGame,
  getGameOptionChoices,
  getGameOptions,
} from 'src/services/game/selectGameService';
import { api } from 'boot/axios';

export function useGameSelection() {
  const gameInformation = reactive<{
    game: GameDto | undefined;
    options: GameOptionDto[];
  }>({
    game: undefined,
    options: [],
  });

  const isLoading = ref(false);

  const gameSelection = reactive<SelectedGameDto>({
    game: 0,
    selected_options: [],
  });

  async function setGameInformation(game: GameDto) {
    if (gameInformation.game && gameInformation.game.id === game.id) return;
    isLoading.value = true;
    loadGame(game);
    await loadOptions(game.id);
    await loadChoices();
    isLoading.value = false;
  }

  function loadGame(game: GameDto) {
    gameInformation.game = game;
    gameSelection.game = game.id;
    gameInformation.options = [];
    gameSelection.selected_options = [];
  }

  function setSelectedOption(option: GameOptionDto) {
    const selectedOption: SelectedGameOptionDto = {
      id: option.id,
      selected_game: gameSelection.game,
      value: option.has_choices ? undefined : false,
      choice: undefined,
    };
    gameSelection.selected_options.push(selectedOption);
  }

  async function loadOptions(gameId: number) {
    try {
      const { data: options } = await getGameOptions(gameId);
      gameInformation.options = options;
      options.forEach(setSelectedOption);
    } catch (error) {
      console.error(`Failed to fetch options for game ${gameId}:`, error);
      gameInformation.options = [];
    }
  }

  async function loadChoices() {
    for (const option of gameInformation.options) {
      if (!option.has_choices) continue;
      const { data: newChoices } = await getGameOptionChoices(option.id);
      option.choices = [...(option.choices || []), ...newChoices];
    }
  }

  function findChoicesByOption(optionId: number) {
    return (
      gameInformation.options.find((option) => option.id === optionId)
        ?.choices || null
    );
  }

  async function fetchPlatforms() {
    const { data: platforms } = await api('game/platforms/');
    return platforms;
  }

  async function fetchGames() {
    const { data: gameData } = await api('game/games/');
    return gameData;
  }

  function submitGame() {
    if (gameSelection) {
      createSelectedGame(gameSelection);
    } else {
      console.warn('No game selected');
    }
  }

  return {
    gameInformation,
    gameSelection,
    isLoading,
    setGameInformation,
    findChoicesByOption,
    fetchPlatforms,
    fetchGames,
    submitGame,
  };
}
