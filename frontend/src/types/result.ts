/**
 * Match-result payloads and DTOs (backend app: `result`).
 */
export type TMatchResultPayload = {
  player_profile: number;
  selected_game: number;
  points: number | null;
  position: number | null;
  notes: string | null;
  starting_position: number | null;
  starting_points: number | null;
  faction_ids: number[];
  tie_breaker_value: number | null;
  win_condition_option?: number | null;
};

export type TMatchResultSubmitPayload = {
  selected_game: number;
  results: TMatchResultPayload[];
  win_condition: number;
  tiebreaker?: { id: number };
};

export type TMatchResultDto = {
  id: number;
  player_profile: number;
  player_profile_name: string;
  selected_game: number;
  game_name?: string;
  points: number | null;
  position: number | null;
  notes: string | null;
  starting_position: number | null;
  starting_points: number | null;
  tie_breaker_value: number | null;
  decisive_tie_breaker: { id: number; name: string } | null;
  win_condition: { id: number; name: string } | null;
  win_condition_option: { id: number; name: string; order: number } | null;
  factions: { id: number; name: string; level: number }[];
};

export type TMatchResult = TMatchResultDto;
