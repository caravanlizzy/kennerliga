import type { AvatarShape } from './avatar';

export type TProfileDto = {
  id: number;
  name: string;
};

export type TUserDto = {
  id: number;
  username: string;
  email: string;
  is_superuser: boolean;
  is_staff: boolean;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  avatar_shape?: AvatarShape;
  avatar_color?: string;
  profile?: TProfileDto;
  profile_id?: number;
  token?: string;
  admin?: boolean;
  myCurrentLeagueId?: number | null;
  isMyTurn?: boolean;
  total_games?: number | null;
  win_rate?: number | null;
  avg_position?: number | null;
  most_participated_league_level?: number | null;
};

export type TPlayerProfileDto = {
  id: number;
  profile_name: string;
  user?: number | null;
};

/** Mirrors `UserInviteLinkSerializer`. */
export type TUserInviteDto = {
  id: number;
  key: string;
  type?: 'invitation' | 'password';
  label: string;
  user?: number | null;
  username?: string;
  player_profile?: number | null;
  player_profile_details?: TPlayerProfileDto | null;
  created_by?: number | null;
  created_at: string;
  expires_at?: string | null;
  invite_url: string;
};

/** One game's aggregate row in the player statistics payload. */
export type TPlayerGameStat = {
  name: string;
  winRate: number;
  avgPos: number;
  count: number;
  positions: number[];
};

/** A game the player picked this year, with the per-year limit applied. */
export type TPlayerPickedGame = {
  game_id: number;
  name: string;
  platform: string;
  count: number;
  limit_exceeded: boolean;
};

/** Mirrors the payload of `UserViewSet.user_statistics`. */
export type TUserStatistics = {
  overall_stats: {
    total_games: number;
    wins: number;
    podiums: number;
    avg_pos: number;
    /** Keyed by finishing position. */
    positions: Record<number, number>;
  };
  league_stats: {
    totalLeagues: number;
  };
  game_stats: TPlayerGameStat[];
  top_games: TPlayerGameStat[];
  picked_games: TPlayerPickedGame[];
  /** Comes from the App Configuration (`max_same_game_per_year`). */
  max_game_limit: number;
  available_years: number[];
};
