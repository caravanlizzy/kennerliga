import { TSelectedGameDto, TSelectedGameOptionDto } from './game';

export type TSeasonDto = {
  id: number;
  year: number;
  month: number;
  name?: string;
  status?: string;
  is_completed?: boolean;
};

export type TLeagueStatus =
  | 'PICKING'
  | 'REPICKING'
  | 'BANNING'
  | 'PLAYING'
  | 'DONE';

export type TSeasonParticipantDto = {
  id: number;
  season: number;
  rank: number;
  username: string;
  profile_name: string;
  profile: number; // player_profile id
  selected_games: TSelectedGameDto[] | null;
  my_banned_game: TBannedGame;
  has_banned: boolean;
  is_active_player: boolean;
  position: number;
  banned_by: string[];
};

export type TLeagueDto = {
  id: number;
  level: number | string;
  season: number;
  members?: TSeasonParticipantDto[];
  status?: TLeagueStatus;
  is_completed?: boolean;
};

export type TBannedGameFull = {
  id: number;
  game: number;
  game_name: string;
  profile: number;
  selected_options: TSelectedGameOptionDto[];
};

export type TBannedGameEmpty = {
  game: null;
  selected_options: [];
  leagueId: null;
  playerProfileId: null;
};

export type TBannedGame = TBannedGameFull | TBannedGameEmpty;
