import type { AvatarShape } from './avatar';

export type TStatBetter = 'higher' | 'lower';

export type TStatEntry = {
  rank: number | null;
  value: number | null;
  // Optional pre-formatted label shown verbatim instead of `value`
  // (e.g. "L1 · 24 pts" for the career metric).
  display?: string | null;
  // Highest league reached (career metric), used to render a league badge.
  best_level?: number | null;
  profile_id: number;
  profile_name: string;
  username: string | null;
  is_me: boolean;
  eligible: boolean;
};

export type TStatCategory = {
  key: string;
  label: string;
  description: string;
  unit: string;
  better: TStatBetter;
  min_games: number | null;
  total_ranked: number;
  me: TStatEntry;
  top: TStatEntry[];
  around_me: TStatEntry[];
};

// The "fun" awards (Hater, Inspirer) are ranked and shaped identically to
// the categories above, so both render through the same StatCategoryCard.
export type TAward = TStatCategory;

export type TStatisticsOverview = {
  min_games: number;
  window: number;
  categories: TStatCategory[];
  awards: TAward[];
};

export type TGameBestPlayer = {
  profile_id: number;
  profile_name: string;
  win_rate: number | null;
  avg_position: number | null;
};

export type TGameStatSummary = {
  game_id: number;
  name: string;
  platform: string;
  games_played: number;
  distinct_players: number;
  best_player: TGameBestPlayer | null;
};

export type TGameLeaderboardEntry = {
  rank: number | null;
  profile_id: number;
  profile_name: string;
  username: string | null;
  games_played: number;
  wins: number;
  avg_position: number | null;
  win_rate: number | null;
  is_me: boolean;
  eligible: boolean;
};

// A single entry in the "most picked"/"most banned" games podiums shown atop
// the games statistics section.
export type TPopularGame = {
  game_id: number;
  name: string;
  platform: string;
  count: number;
};

export type TPopularGames = {
  most_picked: TPopularGame[];
  most_banned: TPopularGame[];
};

export type TGameLeaderboard = {
  game_id: number;
  name: string;
  platform: string;
  min_games: number;
  excluded_low_sample_count: number;
  leaderboard: TGameLeaderboardEntry[];
  me: TGameLeaderboardEntry;
};

/** Per-league-level placement tallies for one player in one year. */
export type TPerLevelCounts = {
  first: number;
  second: number;
  third: number;
  fourth: number;
};

export type TPlayerYearStanding = {
  player_profile_id: number;
  profile_name: string;
  username: string;
  avatar_shape?: AvatarShape;
  avatar_color?: string;
  /** Keyed by league level, stringified. */
  per_level: Record<string, TPerLevelCounts>;
};

/** Mirrors the `/leaderboard/` endpoint (`api.views.LeaderboardViewSet`). */
export type TYearLeaderboard = {
  year: number | 'all';
  levels: number[];
  standings: TPlayerYearStanding[];
};

export type TWinSuggestionOpponent = {
  profile_id: number;
  profile_name: string | null;
  chance: number;
  shared_matches: number;
  opponent_games: number;
};

export type TWinSuggestion = {
  game_id: number;
  name: string;
  short_name: string;
  platform: string;
  win_chance: number;
  games_played: number;
  wins: number;
  shared_matches: number;
  opponents: TWinSuggestionOpponent[];
};

export type TGameHighScore = {
  points: number;
  profile_id: number;
  profile_name: string;
  username: string | null;
  match_id: number;
  season_id: number | null;
  season_name: string | null;
  league_id: number | null;
  league_level: number | null;
  league_name: string | null;
  date: string;
};

export type TGameRecords = {
  high_score: TGameHighScore | null;
  low_score: number | null;
  avg_score: number | null;
  avg_winning_score: number | null;
};

export type TGameOverviewStats = {
  total_matches: number;
  distinct_players: number;
  distinct_seasons: number;
  total_picks: number;
  total_bans: number;
};

export type TGameSuperlativePlayer = {
  profile_id: number;
  profile_name: string;
  username: string | null;
  count: number;
};

export type TGameSuperlatives = {
  most_picked_by: TGameSuperlativePlayer[];
  most_banned_by: TGameSuperlativePlayer[];
  most_wins_by: TGameSuperlativePlayer[];
  most_played_by: TGameSuperlativePlayer[];
};

export type TGameLeaderboardPlayer = {
  rank: number | null;
  profile_id: number;
  profile_name: string;
  username: string | null;
  games_played: number;
  wins: number;
  win_rate: number;
  avg_position: number | null;
  best_score: number | null;
  avg_score: number | null;
  is_me: boolean;
  eligible: boolean;
};

export type TGameFactionStat = {
  id: number;
  name: string;
  icon?: string | null;
  games_played: number;
  wins: number;
  win_rate: number;
  avg_position: number | null;
  avg_points: number | null;
  best_score: number | null;
};

export type TGameStartingPositionStat = {
  starting_position: number;
  games_played: number;
  wins: number;
  win_rate: number;
  avg_position: number | null;
  avg_points: number | null;
  best_score: number | null;
};

export type TGameRuleVariantStat = {
  option_id: number;
  option_name: string;
  choice_id: number | null;
  choice_name: string;
  matches_count: number;
  avg_winning_score: number | null;
  avg_score: number | null;
  high_score: number | null;
};

export type TGameMatchParticipant = {
  profile_id: number;
  profile_name: string;
  username: string | null;
  position: number | null;
  points: number | null;
  starting_position?: number | null;
  starting_points?: number | null;
  faction_name: string | null;
  win_condition_name: string | null;
  is_winner: boolean;
};

export type TGameMatchOption = {
  option_name: string;
  choice_name: string;
};

export type TGameRecentMatch = {
  id: number;
  season_id: number | null;
  season_name: string | null;
  season_year: number | null;
  league_id: number | null;
  league_level: number | null;
  league_name: string | null;
  date: string;
  participants: TGameMatchParticipant[];
  selected_options: TGameMatchOption[];
};

export type TGameMatch = TGameRecentMatch;

export type TGameDetailInfo = {
  id: number;
  name: string;
  short_name: string;
  platform: {
    id: number;
    name: string;
  };
  min_players: number;
  max_players: number;
  selectable: boolean;
  has_points: boolean;
  is_asymmetric: boolean;
  has_starting_player_order: boolean;
  starting_points_system: string | null;
  win_conditions: string[];
  tie_breakers: string[];
  options: {
    id: number;
    name: string;
    choices: string[];
  }[];
  factions: {
    id: number;
    name: string;
  }[];
};

export type TGameDetailedStatistics = {
  game: TGameDetailInfo;
  overview: TGameOverviewStats;
  records: TGameRecords;
  superlatives: TGameSuperlatives;
  leaderboard: TGameLeaderboardPlayer[];
  factions: TGameFactionStat[];
  starting_positions?: TGameStartingPositionStat[];
  rule_variants?: TGameRuleVariantStat[];
  recent_matches: TGameRecentMatch[];
};
