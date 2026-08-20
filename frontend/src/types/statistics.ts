export type TStatBetter = 'higher' | 'lower';

export type TStatEntry = {
  rank: number | null;
  value: number | null;
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

export type TStatisticsOverview = {
  min_games: number;
  window: number;
  categories: TStatCategory[];
};

export type TGameStatSummary = {
  game_id: number;
  name: string;
  platform: string;
  games_played: number;
  distinct_players: number;
};

export type TGameLeaderboardEntry = {
  rank: number | null;
  profile_id: number;
  profile_name: string;
  username: string | null;
  games_played: number;
  wins: number;
  podiums: number;
  avg_position: number | null;
  win_rate: number | null;
  is_me: boolean;
  eligible: boolean;
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
