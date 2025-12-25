import { ref, reactive, computed, watch, Ref } from 'vue';
import type {
  GameDto,
  GameOptionDto,
  SelectedGameDtoPayload,
  TPlatform,
  FullGameDto,
  GameOptionChoiceDto,
} from 'src/models/gameModels';
import { api } from 'boot/axios';
import { createSelectedGame, fetchFullGame } from 'src/services/gameService';
import type { TGameSelection } from 'src/types';

// --- helpers (local types for availability evaluation) ---
type AvailabilityConditionLike = {
  negate?: boolean;

  // write-style refs (may or may not be present in read payload)
  depends_on_option_ref?: string;
  expected_choice_ref?: string;
  expected_value?: unknown;

  // read-style ids/objects (depends on your DRF serializer)
  depends_on_option?: number | { id: number };
  expected_choice?: number | { id: number };

  // read-style *_id fields (matches your logged payload)
  depends_on_option_id?: number | null;
  expected_choice_id?: number | null;
};

type AvailabilityGroupLike = {
  conditions?: AvailabilityConditionLike[];
};

type OptionWithAvailability = GameOptionDto & {
  availability_groups?: AvailabilityGroupLike[];
  // some serializers may include these on read; keep optional
  ref?: string;
};

const EMPTY_GAME: GameDto = { id: -1, name: '', platform: -1 };

function asId(v: unknown): number | undefined {
  if (typeof v === 'number') return v;
  if (v && typeof v === 'object' && 'id' in (v as any) && typeof (v as any).id === 'number') {
    return (v as any).id;
  }
  return undefined;
}

export function useGameSelection(leagueId: number, profileId: number) {
  // --- state ---
  const gameInformation = reactive<{
    game: GameDto | undefined;
    options: OptionWithAvailability[];
  }>({
    game: undefined,
    options: [],
  });

  const isLoading = ref(false);
  const platform: Ref<TPlatform | null> = ref(null);
  const filter = ref('');
  const platforms: Ref<TPlatform[]> = ref([]);
  const gameData = ref<GameDto[]>([]);
  const selectedPlatforms = ref<Set<number>>(new Set());

  const gameSelection = reactive<TGameSelection>({
    game: EMPTY_GAME,
    selectedOptions: [],
    profileId: 0,
    leagueId: 0,
  });

  // --- computed (filters) ---
  const filteredGames = computed(() => {
    return gameData.value.filter((game) => {
      return (
        (!platform.value || game.platform === platform.value.id) &&
        (!filter.value || game.name.toLowerCase().includes(filter.value.toLowerCase()))
      );
    });
  });

  const availableGames = computed(() => {
    const base = filteredGames.value || [];
    if (selectedPlatforms.value.size === 0) return base;
    return base.filter((g: GameDto) => selectedPlatforms.value.has(g.platform));
  });

  // --- selection helpers ---
  function initGameSelection(options: OptionWithAvailability[]) {
    gameSelection.selectedOptions = options.map((option) => ({
      id: option.id,
      selected_game: gameSelection.game?.id,
      value: option.has_choices ? undefined : false,
      choice: undefined,
    }));
  }

  function getSelectedOption(optionId: number) {
    return gameSelection.selectedOptions.find((so) => so.id === optionId);
  }

  function getSelectedChoiceId(optionId: number): number | undefined {
    const so = getSelectedOption(optionId);
    return so?.choice?.id;
  }

  function getSelectedValue(optionId: number): unknown {
    const so = getSelectedOption(optionId);
    return so?.value;
  }

  // --- availability evaluation ---
  /**
   * Rule:
   * - If option has no availability_groups (or empty), it's available.
   * - Otherwise: option is available if ANY group is satisfied (OR across groups).
   * - A group is satisfied if ALL its conditions are satisfied (AND within group).
   */
  function isOptionAvailable(option: OptionWithAvailability): boolean {
    const groups = option.availability_groups ?? [];
    if (groups.length === 0) return true;

    const optionById = new Map<number, OptionWithAvailability>();
    for (const o of gameInformation.options) optionById.set(o.id, o);

    // Build ref->id map if refs happen to be present on read
    const optionIdByRef = new Map<string, number>();
    for (const o of gameInformation.options) {
      if (typeof o.ref === 'string' && o.ref.trim()) {
        optionIdByRef.set(o.ref, o.id);
      }
    }

    const isCondTrue = (cond: AvailabilityConditionLike): boolean => {
      const negate = Boolean(cond.negate);

      // resolve depends_on option id (support object/id, *_id, then ref)
      const dependsOnId =
        asId(cond.depends_on_option) ??
        (typeof cond.depends_on_option_id === 'number' ? cond.depends_on_option_id : undefined) ??
        (cond.depends_on_option_ref ? optionIdByRef.get(cond.depends_on_option_ref) : undefined);

      // If we can't resolve, default to "not satisfied" (safer than showing restricted options)
      if (!dependsOnId) return false;

      // Resolve expected choice id if present (support object/id and *_id)
      const expectedChoiceId =
        asId(cond.expected_choice) ??
        (typeof cond.expected_choice_id === 'number' ? cond.expected_choice_id : undefined);

      // Determine whether condition is "choice match" or "value match"
      let satisfied = false;

      if (expectedChoiceId != null) {
        satisfied = getSelectedChoiceId(dependsOnId) === expectedChoiceId;
      } else if (cond.expected_value !== undefined) {
        satisfied = getSelectedValue(dependsOnId) === cond.expected_value;
      } else {
        // If neither is provided in read payload, we cannot evaluate -> treat as not satisfied
        satisfied = false;
      }

      return negate ? !satisfied : satisfied;
    };

    const isGroupSatisfied = (group: AvailabilityGroupLike): boolean => {
      const conditions = group.conditions ?? [];
      // no conditions => group trivially satisfied
      if (conditions.length === 0) return true;
      return conditions.every(isCondTrue);
    };

    return groups.some(isGroupSatisfied);
  }

  const visibleOptions = computed(() => {
    return gameInformation.options.filter(isOptionAvailable);
  });

  // When options become hidden, clear their selection so payload doesn't include stale/invalid data
  watch(
    () => visibleOptions.value.map((o) => o.id),
    (visibleIds, prevVisibleIds) => {
      const visible = new Set(visibleIds);
      const prevVisible = new Set(prevVisibleIds ?? []);

      const optionById = new Map(gameInformation.options.map((o) => [o.id, o] as const));

      for (const so of gameSelection.selectedOptions) {
        if (!visible.has(so.id)) {
          so.choice = undefined;
          so.value = undefined;
          continue;
        }

        // Newly visible: restore defaults
        if (!prevVisible.has(so.id)) {
          const opt = optionById.get(so.id);
          if (opt?.has_choices) {
            // leave choice undefined (user must pick)
            so.choice = so.choice ?? undefined;
          } else {
            // toggles should always have a boolean
            if (so.value === undefined) so.value = false;
          }
        }
      }
    }
  );

  // --- computed (validity) ---
  const isValid = computed(() => {
    if (!gameInformation.game || gameSelection.game.id === -1) return false;

    // Only require selections for currently visible options
    const opts = visibleOptions.value;

    // For options with choices: must have a choice selected
    const optionsWithChoices = opts.filter((o) => o.has_choices);
    const choicesOk = optionsWithChoices.every((option) => {
      const selected = getSelectedOption(option.id);
      return !!selected?.choice;
    });

    // For boolean/value options: you may want to require a value (optional, keep as-is)
    return choicesOk;
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
    const { data } = await api(`game/games/?league=${leagueId}`);
    gameData.value = data;
  }

  // --- game selection / primary ---
  async function initGameInformation(game: GameDto) {
    if (gameInformation.game && gameInformation.game.id === game.id) return;

    isLoading.value = true;

    // reset
    gameInformation.game = game;
    gameInformation.options = [];
    gameSelection.game = game;
    gameSelection.selectedOptions = [];

    try {
      const full: FullGameDto = await fetchFullGame(game.id);

      gameInformation.game = { id: full.id, name: full.name, platform: full.platform };
      // ensure arrays exist
      gameInformation.options = (full.options ?? []).map((o: any) => ({
        ...o,
        choices: (o.choices ?? []) as GameOptionChoiceDto[],
        availability_groups: (o.availability_groups ?? []) as AvailabilityGroupLike[],
      }));

      initGameSelection(gameInformation.options);
    } catch (e) {
      console.error(`Failed to fetch full game ${game.id}:`, e);
      gameInformation.options = [];
      gameSelection.selectedOptions = [];
    } finally {
      isLoading.value = false;
    }
  }

  // --- platform selection helpers ---
  const togglePlatform = (id: number) => {
    const s = new Set(selectedPlatforms.value);
    if (s.has(id)) s.delete(id);
    else s.add(id);
    selectedPlatforms.value = s;
  };

  const isPlatformSelected = (id: number) => selectedPlatforms.value.has(id);

  // --- payload + submit ---
  function toSelectedGamePayload(selection: TGameSelection): SelectedGameDtoPayload {
    // Only submit selections for currently visible options
    const visible = new Set(visibleOptions.value.map((o) => o.id));

    return {
      game: selection.game.id,
      selected_options: selection.selectedOptions
        .filter((so) => visible.has(so.id))
        .map((option) => ({
          selected_game: selection.game.id,
          game_option_id: option.id,
          ...(option.choice ? { choice_id: option.choice.id } : { value: option.value }),
        })),
      profile: profileId,
      league: leagueId,
    };
  }

  function submitGame(manageOnly = false) {
    const data = toSelectedGamePayload(gameSelection);
    return createSelectedGame(data, manageOnly);
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
    visibleOptions,

    // functions
    loadPlatformsAndGames,
    fetchPlatforms,
    initGameInformation,
    togglePlatform,
    isPlatformSelected,
    submitGame,
    toSelectedGamePayload,
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
