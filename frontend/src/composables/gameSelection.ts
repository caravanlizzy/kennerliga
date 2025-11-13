import { ref, reactive, computed, Ref } from 'vue';
import {
  GameDto,
  GameOptionDto,
  SelectedGameDtoPayload,
  SelectedGameOptionDto,
  TPlatform,
} from 'src/models/gameModels';
import { api } from 'boot/axios';
import {
  createSelectedGame,
  fetchGameOptionChoices,
  fetchGameOptions,
} from 'src/services/gameService';

type TGameSelection = {
  game: GameDto;
  selectedOptions: SelectedGameOptionDto[];
  profileId: number;
  leagueId: number;
};

export function useGameSelection(leagueId: number, profileId: number) {
  const gameInformation = reactive<{
    game: GameDto | undefined;
    options: GameOptionDto[];
  }>({
    game: undefined,
    options: [],
  });

  const isLoading = ref(false);
  const platform: Ref<TPlatform | null> = ref(null);
  const filter = ref('');
  const platforms: Ref<TPlatform[]> = ref([]);
  const gameData = ref<GameDto[]>([]);
  const EMPTY_GAME: GameDto = {
    id: -1,
    name: '',
    platform: -1,
  };

  const gameSelection = reactive<TGameSelection>({
    game: EMPTY_GAME,
    selectedOptions: [],
    profileId: 0,
    leagueId: 0,
  });

  const isValid = computed(() => {
    if (!gameInformation.game || gameSelection.game.id === -1) {
      return false;
    }

    const optionsWithChoices = gameInformation.options.filter(
      (o) => o.has_choices
    );

    return optionsWithChoices.every((option) => {
      const selected = gameSelection.selectedOptions.find(
        (so) => so.id === option.id
      );
      return !!selected?.choice;
    });
  });

  const filteredGames = computed(() => {
    return gameData.value.filter((game) => {
      return (
        (!platform.value || game.platform === platform.value.id) &&
        (!filter.value ||
          game.name.toLowerCase().includes(filter.value.toLowerCase()))
      );
    });
  });

  const loadPlatformsAndGames = async () => {
    platforms.value = await fetchPlatforms();
    gameData.value = await fetchGames();
  };

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

  function setSelectedOptions(options: GameOptionDto[]) {
    gameSelection.selectedOptions = options.map((option) => ({
      id: option.id,
      selected_game: gameSelection.game?.id,
      value: option.has_choices ? undefined : false,
      choice: undefined,
    }));
  }

  function findSelectedOption(optionId: number) {
    return gameSelection.selectedOptions.find((o) => o.id === optionId);
  }

  async function loadOptions(gameId: number) {
    try {
      const { data: options } = await fetchGameOptions(gameId);
      gameInformation.options = options;
      setSelectedOptions(options); // cleaner
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
    const { data: gameData } = await api(`game/games/?league=${leagueId}`);
    return gameData;
  }

  function toSelectedGamePayload(
    selection: TGameSelection
  ): SelectedGameDtoPayload {
    return {
      game: selection.game.id,
      selected_options: selection.selectedOptions.map((option) => ({
        selected_game: selection.game.id,
        game_option_id: option.id,
        ...(option.choice
          ? { choice_id: option.choice.id }
          : { value: option.value }),
      })),
      profile_id: profileId,
      league_id: leagueId,
    };
  }

  function submitGame(manageOnly = false) {
    if (gameSelection) {
      const data = toSelectedGamePayload(gameSelection);
      return createSelectedGame(data, manageOnly);
    } else {
      console.warn('No game selected');
    }
  }

  return {
    gameInformation,
    gameSelection,
    isLoading,
    isValid,
    setGameInformation,
    findChoicesByOption,
    findSelectedOption,
    submitGame,
    platform,
    filter,
    platforms,
    gameData,
    filteredGames,
    loadPlatformsAndGames,
  };
}
