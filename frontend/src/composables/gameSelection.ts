import { ref, reactive } from 'vue';
import {
  GameDto,
  GameOptionDto,
  SelectedGameDto,
  SelectedGameOptionDto
} from 'src/models/gameModels';
import {
  createSelectedGame,
  fetchGameOptionChoices,
  fetchGameOptions
} from 'src/services/game/selectGameService';
import { api } from 'boot/axios';

type TGameSelection = {
  game: GameDto|null;
  selectedOptions: SelectedGameOptionDto[];
}

export function useGameSelection() {
  const gameInformation = reactive<{
    game: GameDto | undefined;
    options: GameOptionDto[];
  }>({
    game: undefined,
    options: []
  });

  const isLoading = ref(false);

  const gameSelection = reactive<TGameSelection>({
    game: null,
    selectedOptions: []
  });

  async function setGameInformation(game: GameDto) {
    if (gameInformation.game && gameInformation.game.id === game.id) return;
    isLoading.value = true;
    resetGame(game);
    await loadOptions(game.id);
    await loadChoices();
    isLoading.value = false;
  }

  function resetGame(game: GameDto) {
    resetGameInformation(game);
    resetGameSelection(game);
  }

  function resetGameInformation(game: GameDto) {
    gameInformation.game = game;
    gameInformation.options = [];
  }

  function resetGameSelection(game: GameDto) {
    gameSelection.game = game;
    gameSelection.selectedOptions = [];
  }

  function setSelectedOption(option: GameOptionDto) {
    const selectedOption: SelectedGameOptionDto = {
      id: option.id,
      selected_game: gameSelection.game!.id,
      value: option.has_choices ? undefined : false,
      choice: undefined
    };
    gameSelection.selectedOptions.push(selectedOption);
  }

  async function loadOptions(gameId: number) {
    try {
      const { data: options } = await fetchGameOptions(gameId);
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
      const { data: newChoices } = await fetchGameOptionChoices(option.id);
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

  function transformSubmitData(selection: TGameSelection): SelectedGameDto {
    const selectedOptions = selection.selectedOptions.map((option) => {
      if (option.choice) {
        return ({
          game_option: option.id,
          choice: option.choice.id
        });
      }
      return ({
        game_option: option.id,
        value: option.value
      });
    });
    return ({
      game: selection.game!.id,
      selected_options: selectedOptions
    });
  }

  function submitGame() {
    if (gameSelection) {
      const data = transformSubmitData(gameSelection);
      createSelectedGame(data);
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
    submitGame
  };
}
