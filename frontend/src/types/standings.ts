/**
 * The `full-standings` contract.
 *
 * Mirrors `league.services.build_full_standings_payload` on the backend and
 * is served by both
 *   GET /league/leagues/{id}/full-standings/      (one league)
 *   GET /season/seasons/{id}/full-standings/      (every league of a season)
 *
 * These shapes used to be re-declared inside each consuming component, which
 * let them drift apart; keep them here so the components share one contract.
 */

/** One player's result in one selected game, pre-formatted for display. */
export type TGameStandingCell = {
  points: string | null;
  league_points: string | null;
  rank: number | null;
  display_rank?: string | null;
  display_value?: string | null;
  decisive_tie_breaker_name?: string | null;
  tie_breaker_value?: string | null;
};

/** One row of the standings matrix: a player and their per-game cells. */
export type TFullStandingsRow = {
  player_profile_id: number;
  profile_name: string;
  user_id?: number | null;
  username?: string | null;
  total_league_points: string;
  total_wins: string;
  unresolved_tie_group?: string | null;
  /** Keyed by selected-game id, stringified. */
  games: Record<string, TGameStandingCell>;
  /** Derived client-side from the matching tie group. */
  resolved_tie_reason?: string;
};

export type TTieGroupMember = {
  player_profile_id: number;
  profile_name: string;
  user_id?: number | null;
  username?: string | null;
  order_index?: number;
};

export type TTieResolution = {
  reason: string;
  reason_display: string;
  note?: string | null;
  is_resolved: boolean;
};

export type TTieGroup = {
  group_key: string;
  unresolved: boolean;
  members: TTieGroupMember[];
  league_points?: string;
  wins?: string;
  resolution?: TTieResolution | null;
};

export type TSelectedGameSetting = {
  name: string;
  value: string;
};

/** A selected game as it appears in the standings header row. */
export type TStandingsSelectedGame = {
  id: number;
  game_name: string;
  game_short_name: string;
  platform_name?: string;
  has_points: boolean;
  selected_by_id?: number | null;
  selected_by_name?: string | null;
  settings?: TSelectedGameSetting[];
};

export type TFullStandings = {
  selected_games: TStandingsSelectedGame[];
  standings: TFullStandingsRow[];
  season_id?: number;
  tie_groups?: TTieGroup[];
  all_games_finished?: boolean;
  is_season_completed?: boolean;
};

/** One league's payload inside the batched season endpoint. */
export type TSeasonLeagueStandings = TFullStandings & {
  id: number;
  level: number;
  name: string;
};

export type TSeasonFullStandings = {
  season: { id: number; name: string; status: string };
  leagues: TSeasonLeagueStandings[];
};

/** Flattened row used by the compact league standings table. */
export type TLeagueStandingRow = {
  player_profile: number;
  profile_name: string;
  wins: number;
  league_points: number;
  unresolved_tie_group?: string | null;
  resolved_tie_reason?: string;
};
