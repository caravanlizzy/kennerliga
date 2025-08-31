// stores/leagueStore.ts
import { defineStore } from 'pinia';
import { ref, computed, shallowRef } from 'vue';
import { getMyLeagueId } from 'src/services/game/leagueService';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { useUserStore } from 'stores/userStore';
import { banGame } from 'src/services/game/banGameService';
import { api } from 'boot/axios';
import { TLeagueStatus } from 'src/types';

// Shared leaf types
/**
 * Represents a choice with a unique identifier, name, and a reference to a game option.
 *
 * @typedef {Object} Choice
 * @property {number} id - The unique identifier for the choice.
 * @property {string} name - The name of the choice.
 * @property {number} option - The ID of the associated game option, corresponding to GameOption.id.
 */
type Choice = {
  id: number;
  name: string;
  option: number; // GameOption.id
};

/**
 * Represents a game option within a game configuration.
 *
 * @typedef {Object} GameOption
 * @property {number} id - The unique identifier for the game option.
 * @property {string} name - The name of the game option.
 * @property {boolean} has_choices - Indicates if the game option has selectable choices.
 * @property {number} game - The identifier of the game that the option belongs to.
 * @property {boolean|null} only_if_value - Specifies if the option is conditionally displayed based on a specific value. Can be null.
 * @property {number|null} only_if_option - Specifies the dependent option by its identifier for conditional display. Can be null.
 * @property {number|null} only_if_choice - Specifies the dependent choice by its identifier for conditional display. Can be null.
 */
export type GameOption = {
  id: number;
  name: string;
  has_choices: boolean;
  game: number;
  only_if_value: boolean | null;
  only_if_option: number | null;
  only_if_choice: number | null;
};

/**
 * Represents a selected option within a game where choices and values may vary.
 *
 * @typedef {Object} SelectedOption
 * @property {number} id - Unique identifier for the selected option.
 * @property {GameOption} game_option - The game option associated with this selection.
 * @property {Choice | null} choice - The specific choice made, used when choices are available (has_choices === true).
 * @property {boolean | null} value - The selected boolean value, used when choices are not available (has_choices === false).
 */
type SelectedOption = {
  id: number;
  game_option: GameOption;
  choice: Choice | null;       // used when has_choices === true
  value: boolean | null;       // used when has_choices === false
};

// Selected/banned game shapes
/**
 * Represents the selected game with its associated details and selected options.
 *
 * @typedef {Object} SelectedGame
 * @property {number} id - The unique identifier for the selected game.
 * @property {number} game - The unique identifier for the base game associated with the selected game.
 * @property {string} game_name - The name of the base game.
 * @property {SelectedOption[]} selected_options - A list of selected options related to the game.
 */
type SelectedGame = {
  id: number;                  // selected_game id
  game: number;                // base game id
  game_name: string;
  selected_options: SelectedOption[];
};

/**
 * Represents detailed information about a banned game.
 *
 * This type holds the data associated with a game that has been banned,
 * including its unique identifier, name, and any selected options related to it.
 *
 * Properties:
 *  @property {number} id - The unique identifier for the banned game.
 *  @property {number} game - The unique identifier for the corresponding game.
 *  @property {string} game_name - The name of the banned game.
 *  @property {SelectedOption[]} selected_options - An array of selected options associated with the game.
 */
type BannedGameFull = {
  id: number;                  // banned selected_game id
  game: number;
  game_name: string;
  selected_options: SelectedOption[];
};

/**
 * Represents an object containing details about a banned or unavailable game
 * with no associated game or options selected.
 *
 * This type is used to signify a game that is no longer active or chosen within a specific context,
 * returning null or empty values for its properties.
 *
 * Properties:
 * - game: Represents the game object, which, in this case, is null, indicating no game is available.
 * - selected_options: An empty array denoting no options have been selected for this game.
 * - leagueId: Represents the league identifier, which is null since no game or league is associated.
 * - playerProfileId: Represents a player's profile identifier, which is null as no specific player context is given.
 */
type BannedGameEmpty = {
  game: null;
  selected_options: [];
  leagueId: null;
  playerProfileId: null;
};

/**
 * Represents a game that has been banned. The game can be represented in two forms:
 * either as a full definition or as an empty placeholder.
 *
 * A `BannedGame` can either be:
 * - `BannedGameFull`: A complete representation of the banned game with detailed information.
 * - `BannedGameEmpty`: A placeholder for situations where no detailed information about the banned game is available.
 */
type BannedGame = BannedGameFull | BannedGameEmpty;

// Member
/**
 * Represents a member in the system with associated properties, status, and metadata.
 *
 * @typedef {Object} Member
 * @property {number} id - The unique identifier for the player profile; used in results reference.
 * @property {string} username - The username of the member.
 * @property {string} profile_name - The display name of the member.
 * @property {SelectedGame | null} selected_game - The currently selected game for the member, if any.
 * @property {BannedGame} banned_game - The game that the member is banned from.
 * @property {boolean} is_active_player - Indicates whether the member is currently an active player.
 * @property {number} rank - The rank of the member within the system.
 * @property {number} position - The position of the member, typically related to ranking.
 * @property {string} [colorClass] - A client-side UI property that determines the color class for display purposes.
 */
type Member = {
  id: number;                  // player_profile id, also referenced in results
  username: string;
  profile_name: string;
  selected_game: SelectedGame | null;
  banned_game: BannedGame;
  is_active_player: boolean;
  rank: number;
  position: number;
  colorClass?: string;         // UI-only, added client-side
};

/**
 * Represents the result of a player's match in a game with various related attributes.
 *
 * @typedef {Object} MatchResult
 * @property {number} id - The unique identifier for the match result.
 * @property {number} player_profile - The ID of the player profile associated with this match result. Corresponds to Member.id.
 * @property {number} selected_game - The ID of the game selected for this match result. Corresponds to SelectedGame.id.
 * @property {number|null} points - The points scored by the player in the match. Can be null if not applicable.
 * @property {number|null} starting_position - The starting position of the player in the match. Can be null if not applicable.
 * @property {string} tie_breaker_value - The value or criteria used for tie-breaking. May be an empty string if not applicable.
 * @property {string|null} decisive_tie_breaker - The decisive tie-breaking value or condition, if applicable. Can be null.
 * @property {string|null} faction_name - The name of the faction used by the player in the match, if applicable. Can be null.
 */
export type MatchResult = {
  id: number;
  player_profile: number;      // Member.id
  selected_game: number;       // SelectedGame.id
  points: number | null;
  starting_position: number | null;
  tie_breaker_value: string;    // may be empty ""
  decisive_tie_breaker: string | null;
  faction_name: string | null;
};


/**
 * Represents a Vue Store for managing league-related data and state.
 *
 * This store is responsible for fetching, maintaining, and providing access to
 * information about leagues, their members, games, statuses, and match results.
 *
 * A range of state properties, computed values, and actions are provided to
 * manage or derive data associated with leagues.
 *
 * The store provides comprehensive utilities including:
 * - State variables for holding league info, members, and match results.
 * - Computed properties for efficient access to specific structured data.
 * - Actions for initialization, data fetching, and updates.
 *
 * Key Features:
 * - Reactive state management for leagues and members.
 * - Efficient mapping and lookup utilities for member and game data.
 * - Result management for games using immutable updates for reactivity.
 */
export const useLeagueStore = defineStore('league', () => {
  // leagueData
  const leagueId = ref<number | null>(null);
  const leagueData = shallowRef<any>(null);
  const members = ref<Member[]>([]);
  const leagueStatus = ref<TLeagueStatus>('PICKING'); // states: PICKING, BANNING, REPICKING, PLAYING, DONE

  // --- Derived maps for O(1) lookups ---
  const membersById = computed<{ [key: number]: Member }>(() =>
    members.value.reduce((acc: { [key: number]: Member }, m) => {
      acc[m.id] = m;
      return acc;
    }, {})
  );

  const selectedGames = computed(() => {
    if (!members.value.length) return [];
    return members.value
      .map((member) =>
        member.selected_game &&
        ({ ...member.selected_game, selected_by: member.username })
      )
      .filter(Boolean) as Array<Member['selected_game'] & { selected_by: string }>;
  });

  const selectedGamesById = computed<
    Record<number, { id: number; game_name: string; selected_by: string }>
  >(() =>
    selectedGames.value.reduce(
      (acc, g) => {
        acc[g.id] = g;
        return acc;
      },
      {} as Record<number, { id: number; game_name: string; selected_by: string }>
    )
  );

  // --- Results keyed by selected_game for fast access ---
  // Using a Record so reactivity stays simple.
  const matchResultsByGame = ref<Record<number, MatchResult[]>>({});

  const matchResults = computed<MatchResult[]>(() =>
    Object.values(matchResultsByGame.value).flat()
  );

  const selectedGamesWithResults = computed(() =>
    selectedGames.value.filter(g => (matchResultsByGame.value[g.id]?.length ?? 0) > 0)
  );

  const selectedGamesFetchedEmpty = computed(() =>
    selectedGames.value.filter(g => (matchResultsByGame.value[g.id]?.length ?? 0) === 0)
  );


  const initialized = ref(false);
  let initPromise: Promise<void> | null = null;

  async function updateLeagueData() {
    if (leagueId.value == null) return;
    const { data } = await fetchLeagueDetails(leagueId.value);
    leagueData.value = data;
    members.value = data.members;
    members.value = members.value.map((member, index) => ({
      ...member,
      colorClass: `bg-player-${index + 1}`,
    }));
    leagueStatus.value = data.status;
  }

  // Helper to set results atomically & dedup on id
  function setResultsForGame(selectedGameId: number, results: MatchResult[]) {
    const uniq = new Map<number, MatchResult>();
    results.forEach(r => uniq.set(r.id, r));
    matchResultsByGame.value = {
      ...matchResultsByGame.value,
      [selectedGameId]: Array.from(uniq.values()).sort((a, b) => (b.points ?? 0) - (a.points ?? 0)),
    };
  }

  async function getMatchResults() {
    if (leagueId.value == null) return;
    const ids = selectedGames.value.map((s) => s.id);
    if (!ids.length) return;

    // fetch all in parallel (replace with a single multi-id endpoint when available)
    const promises = ids.map((id) =>
      api.get<MatchResult[]>(`/result/results/?selected_game=${id}`)
        .then(({ data }) => setResultsForGame(id, data))
        .catch(() => setResultsForGame(id, [])) // keep UI predictable
    );
    await Promise.all(promises);
  }

  async function refreshResultsForGame(selectedGameId: number) {
    const { data } = await api.get<MatchResult[]>(`/result/results/?selected_game=${selectedGameId}`);
    setResultsForGame(selectedGameId, data);
  }

  async function init() {
    if (initialized.value) return;
    if (initPromise) return initPromise;
    initPromise = (async () => {
      leagueId.value = await getMyLeagueId();
      await updateLeagueData();
      await getMatchResults();
      initialized.value = true;
      initPromise = null;
    })();
    return initPromise;
  }

  const activePlayer = computed(() =>
    members.value.find((m) => m.is_active_player)
  );

  const { isMe, user } = useUserStore();
  const isMeActivePlayer = computed(() =>
    activePlayer.value ? isMe(activePlayer.value.username) : false
  );

  const isMePickingGame = computed(
    () => leagueStatus.value === 'PICKING' && isMeActivePlayer.value
  );
  const isMeBanningGame = computed(
    () => leagueStatus.value === 'BANNING' && isMeActivePlayer.value
  );

  async function banNothing() {
    if (!user || !leagueId.value) return;
    try {
      await banGame({ username: user.username, leagueId: leagueId.value, decline: true });
      await updateLeagueData();
    } catch (e) {
      console.error(e);
    }
  }

  return {
    // state
    leagueId,
    leagueData,
    members,
    leagueStatus,
    initialized,
    selectedGames,
    matchResults,
    matchResultsByGame,

    // getters
    activePlayer,
    isMeActivePlayer,
    isMePickingGame,
    isMeBanningGame,
    selectedGamesWithResults,
    selectedGamesFetchedEmpty,
    membersById,
    selectedGamesById,

    // actions
    init,
    updateLeagueData,
    banNothing,
    getMatchResults,
    refreshResultsForGame,
  };
});
