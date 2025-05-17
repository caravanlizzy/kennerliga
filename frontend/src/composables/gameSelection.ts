import { ref, reactive, computed } from 'vue';
import {
  GameDto,
  GameOptionDto,
  SelectedGameDtoPayload,
  SelectedGameOptionDto
} from 'src/models/gameModels';
import {
  createSelectedGame,
  fetchGameOptionChoices,
  fetchGameOptions,
} from 'src/services/game/selectGameService';
import { api } from 'boot/axios';

type TGameSelection = {
  game: GameDto;
  selectedOptions: SelectedGameOptionDto[];
};

export function useGameSelection() {
  const gameInformation = reactive<{
    game: GameDto | undefined;
    options: GameOptionDto[];
  }>({
    game: undefined,
    options: [],
  });

  const isLoading = ref(false);
  const platform = ref();
  const filter = ref('');
  const platforms = ref([]);
  const gameData = ref<GameDto[]>([]);

  const filteredGames = computed(() => {
    return gameData.value.filter((game) => {
      return (
        (!platform.value || game.platform === platform.value.id) &&
        (!filter.value || game.name.toLowerCase().includes(filter.value.toLowerCase()))
      );
    });
  });

  const loadPlatformsAndGames = async () => {
    platforms.value = await fetchPlatforms();
    gameData.value = await fetchGames();
  };


  const EMPTY_GAME: GameDto = {
    id: -1,
    name: '',
    platform: '',
  };

  const gameSelection = reactive<TGameSelection>({
    game: EMPTY_GAME,
    selectedOptions: [],
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
      choice: undefined,
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


  function transformSubmitData(selection: TGameSelection): SelectedGameDtoPayload {
    const selected_options = selection.selectedOptions.map((option) => {
      const base = {
        selected_game: selection.game.id,
        game_option: option.id, // transformed from 'id'
      };

      if (option.choice) {
        return {
          ...base,
          choice: option.choice.id,
        };
      }

      return {
        ...base,
        value: option.value,
      };
    });

    return {
      game: selection.game.id,
      selected_options,
    };
  }


  function submitGame() {
    console.log('game selection: ', gameSelection);
    if (gameSelection) {
      const data = transformSubmitData(gameSelection);
      return createSelectedGame(data);
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
    submitGame,
    platform,
    filter,
    platforms,
    gameData,
    filteredGames,
    loadPlatformsAndGames
  };
}
