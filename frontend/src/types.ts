import { SelectedGameDto } from 'src/models/gameModels';

export type TKennerButton = {
  label?: string;
  icon?: string;
  color?: string;
  forwardName?: string;
};
export interface Meta {
  totalCount: number;
}
export type BreadCrumb = {
  label: string;
  icon: string;
  forwardRouteName: string;
};
export type TItem = {
  itemId: number;
  name: string;
  isEditable: boolean;
};
export type ObjPool<T> = {
  [key: string]: T;
};
export type TGameOptionChoice = {
  id: number;
  name: string;
};
export type TFaction = {
  id: number;
  name: string;
};
export type TTieBreaker = {
  id: number;
  name: string;
};
export type TGameOption = {
  id: number;
  title: string;
  hasChoices: boolean;
  choices: TGameOptionChoice[];
  onlyIfOption?: number;
  onlyIfChoice?: number;
  onlyIfValue?: boolean;
};
export type TResultConfig = {
  isAsymmetric: boolean;
  hasPoints: boolean;
  startingPointSystem: string;
  hasStartingPlayerOrder: boolean; // Assuming it's a number for order/index
  factions?: TFaction[]; // Assuming it's an array of faction names or identifiers
  hasTieBreaker: boolean;
  tieBreakers?: TTieBreaker[]; // Assuming array of tie breaker rules or identifiers
};
export type TUser = {
  id: number;
  password: string; // Encrypted password format
  last_login: string; // ISO 8601 date string
  is_superuser: boolean;
  email: string;
  is_staff: boolean;
  is_active: boolean;
  date_joined: string; // ISO 8601 date string
  username: string;
  groups: any[]; // Can be defined in detail if group structure is known
  user_permissions: any[]; // Can be defined in detail if permission structure is known
};

export type TMember = {
  id: number;
  username: string;
  selected_game?: {
    id: number;
    game_name: string;
  } | null;
};

export type TLeagueStatus =
  | 'PICKING'
  | 'REPICKING'
  | 'BANNING'
  | 'PLAYING'
  | 'DONE';

export type TLeague = {
  id: number;
  level: number | string;
  season: number;
  members: TMember[];
};

export type TSeason = {
  id: number;
  name: string;
};
export type TMessage = {
  text: string;
  datetime: string;
  user: number;
  sender: string;
};

export type TSeasonParticipantRead = {
  id: number;

  // write fields echoed back as values
  season: number;
  profile_id: number;
  rank: number | null;

  // read-only fields
  username: string;
  profile_name: string;
  selected_game: SelectedGameDto | null;
  banned_selected_game: SelectedGameDto | null;
  has_banned: boolean;
  is_active_player: boolean;
};

export type TLeagueMember = {
  id: number;
  season: number;
  profile_id: number;
  rank: number;
  username: string;
  profile_name: string;
  selected_game: SelectedGameDto | null;
  banned_selected_game: SelectedGameDto | null;
  has_banned: boolean;
  is_active_player: boolean;
  position: number;
  selected_game_id: number | null;
  banned_by: string[];
}

