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
