import { TSelectedGameDto, TSelectedGameOptionDto } from './game';

export type TSeasonDto = {
  id: number;
  year: number;
  month: number;
  name?: string;
  status?: string;
};

export type TSeasonParticipantDto = {
  id: number;
  season: number;
  profile_id: number;
  rank: number | null;
  username: string;
  profile_name: string;
  selected_game: TSelectedGameDto | null;
  banned_selected_game: TSelectedGameDto | null;
  has_banned: boolean;
  is_active_player: boolean;
};

export type TLeagueStatus =
  | 'PICKING'
  | 'REPICKING'
  | 'BANNING'
  | 'PLAYING'
  | 'DONE';

export type TLeagueMemberDto = {
  id: number;
  season: number;
  profile_id: number;
  rank: number;
  username: string;
  profile_name: string;
  profile: number; // player_profile id
  selected_game: TSelectedGameDto | null;
  selected_games: TSelectedGameDto[] | null;
  banned_selected_game: TSelectedGameDto | null;
  banned_game: TBannedGame;
  has_banned: boolean;
  is_active_player: boolean;
  position: number;
  selected_game_id: number | null;
  banned_by: string[];
};

export type TLeagueDto = {
  id: number;
  level: number | string;
  season: number;
  members: TLeagueMemberDto[];
  status?: TLeagueStatus;
};

export type TBannedGameFull = {
  id: number;
  game: number;
  game_name: string;
  selected_options: TSelectedGameOptionDto[];
};

export type TBannedGameEmpty = {
  game: null;
  selected_options: [];
  leagueId: null;
  playerProfileId: null;
};

export type TBannedGame = TBannedGameFull | TBannedGameEmpty;
