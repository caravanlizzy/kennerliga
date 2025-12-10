import { ref, reactive, computed, Ref } from 'vue';
import {
  GameDto,
  GameOptionDto,
  SelectedGameDtoPayload,
  TPlatform,
} from 'src/models/gameModels';
import { api } from 'boot/axios';
import {
  createSelectedGame,
  fetchGameOptionChoices,
  fetchGameOptions,
} from 'src/services/gameService';
import { TGameSelection } from 'src/types';

const EMPTY_GAME: GameDto = {
  id: -1,
  name: '',
  platform: -1,
};

export function useGameSelection(leagueId: number, profileId: number) {
  // --- state ---

  const gameInformation = reactive<{
    game: GameDto | undefined;
    options: GameOptionDto[];
  }>({
    game: undefined, // currently selected game
    options: [], // options for the selected game
  });

  const isLoading = ref(false); // loading state for options/choices
  const platform: Ref<TPlatform | null> = ref(null); // single platform filter (legacy)
  const filter = ref(''); // text filter for game name
  const platforms: Ref<TPlatform[]> = ref([]); // all platforms
  const gameData = ref<GameDto[]>([]); // all games
  const selectedPlatforms = ref<Set<number>>(new Set()); // multi-platform filter

  const gameSelection = reactive<TGameSelection>({
    game: EMPTY_GAME, // selected game
    selectedOptions: [], // selected options for that game
    profileId: 0,
    leagueId: 0,
  });

  // --- computed ---

  const isValid = computed(() => {
    // game must be chosen
    if (!gameInformation.game || gameSelection.game.id === -1) {
      return false;
    }

    // all options with choices must have a choice selected
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
    // filter by single platform + name
    return gameData.value.filter((game) => {
      return (
        (!platform.value || game.platform === platform.value.id) &&
        (!filter.value ||
          game.name.toLowerCase().includes(filter.value.toLowerCase()))
      );
    });
  });

  const availableGames = computed(() => {
    // final list: text filter + multi-platform filter
    const base = filteredGames.value || [];
    if (selectedPlatforms.value.size === 0) return base;
    return base.filter((g: GameDto) => selectedPlatforms.value.has(g.platform));
  });

  // --- platform / game loading ---

  const loadPlatformsAndGames = async () => {
    await fetchPlatforms();
    await fetchGames();
  };

  async function fetchPlatforms() {
    const { data } = await api('game/platforms/');
    platforms.value = data;
  }

  async function fetchGames() {
    const { data } = await api('game/games/');
    gameData.value = data;
  }

  // --- game selection / primary ---

  async function initGameInformation(game: GameDto) {
    // avoid reloading if same game
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

  function initGameSelection(options: GameOptionDto[]) {
    // initialize selectedOptions from options
    gameSelection.selectedOptions = options.map((option) => ({
      id: option.id,
      selected_game: gameSelection.game?.id,
      value: option.has_choices ? undefined : false,
      choice: undefined,
    }));
  }

  // --- option / choice loading ---

  async function loadOptions(gameId: number) {
    try {
      const { data: options } = await fetchGameOptions(gameId);
      gameInformation.options = options;
      initGameSelection(options);
    } catch (error) {
      console.error(`Failed to fetch options for game ${gameId}:`, error);
      gameInformation.options = [];
    }
  }

  async function loadChoices() {
    // fetch choices for options that have choices
    for (const option of gameInformation.options) {
      if (!option.has_choices) continue;
      const { data: newChoices } = await fetchGameOptionChoices(option.id);
      option.choices = [...(option.choices || []), ...newChoices];
    }
  }

  // --- platform selection helpers ---

  const togglePlatform = (id: number) => {
    // toggle platform in multi-select set
    const s = new Set(selectedPlatforms.value);
    if (s.has(id)) s.delete(id);
    else s.add(id);
    selectedPlatforms.value = s;
  };

  const isPlatformSelected = (id: number) => selectedPlatforms.value.has(id);

  // --- payload + submit ---

  function toSelectedGamePayload(
    selection: TGameSelection
  ): SelectedGameDtoPayload {
    // build payload for API
    return {
      game: selection.game.id,
      selected_options: selection.selectedOptions.map((option) => ({
        selected_game: selection.game.id,
        game_option_id: option.id,
        ...(option.choice
          ? { choice_id: option.choice.id }
          : { value: option.value }),
      })),
      profile: profileId,
      league: leagueId,
    };
  }

  function submitGame(manageOnly = false) {
    // submit selected game to backend
    if (gameSelection) {
      const data = toSelectedGamePayload(gameSelection);
      return createSelectedGame(data, manageOnly);
    } else {
      console.warn('No game selected');
    }
  }

  return {
    // state
    gameInformation,
    gameSelection,
    isLoading,
    platform,
    filter,
    platforms,
    gameData,
    selectedPlatforms,

    // computed
    isValid,
    filteredGames,
    availableGames,

    // functions
    loadPlatformsAndGames,
    fetchPlatforms,
    initGameInformation,
    togglePlatform,
    isPlatformSelected,
    submitGame,
    toSelectedGamePayload
  };
}

// ---- helpers ----
export function getPlatformName(
  platforms: TPlatform[],
  platformId: number | string
): string {
  const platformObj = platforms.find((p: any) => p.id === platformId);
  return platformObj?.name ?? `No platform found for: ${platformId}`;
}

export function getPlatformColor(name: TPlatform['name']): {
  color: string;
  text: string;
} {
  switch ((name || '').toLowerCase()) {
    case 'boardgamers.space':
      return { color: 'deep-purple-3', text: 'white' };
    case 'yucata':
      return { color: 'blue-5', text: 'white' };
    case 'bga':
      return { color: 'green-5', text: 'white' };
    default:
      return { color: 'grey-3', text: 'white' };
  }
}
