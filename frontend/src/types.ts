import {
  GameDto,
  SelectedGameDto,
  SelectedGameOptionDto,
} from 'src/models/gameModels';

export type TKennerButton = {
  label?: string;
  icon?: string;
  color?: string;
  forwardName?: string;
};
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
export type TGameOptionChoice = {
  id: number;
  name: string;
};
export type TFaction = {
  name: string;
  level: number;
};
export type TTieBreaker = {
  name: string;
  higher_wins: boolean;
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
  factions?: TFaction[];
  hasTieBreaker: boolean;
  tieBreakers?: TTieBreaker[];
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
};

export type TGameSelection = {
  game: GameDto;
  selectedOptions: SelectedGameOptionDto[];
  profileId: number;
  leagueId: number;
};

export type TMember = {
  id: number; // player_profile id, also referenced in results
  username: string;
  profile_name: string;
  profile: number;
  selected_games: SelectedGame[] | null;
  banned_game: BannedGame;
  is_active_player: boolean;
  rank: number;
  position: number;
};

export type MatchResult = {
  id: number;
  player_profile: number; // Member.id
  selected_game: number; // SelectedGame.id
  points: number | null;
  starting_position: number | null;
  tie_breaker_value: string; // may be empty ""
  decisive_tie_breaker: string | null;
  faction_name: string | null;
}; // Selected/banned game shapes
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
export type GameOption = {
  id: number;
  name: string;
  has_choices: boolean;
  game: number;
  only_if_value: boolean | null;
  only_if_option: number | null;
  only_if_choice: number | null;
};

type SelectedOption = {
  id: number;
  game_option: GameOption;
  choice: Choice | null; // used when has_choices === true
  value: boolean | null; // used when has_choices === false
};

type SelectedGame = {
  id: number; // selected_game id
  game: number; // base game id
  game_name: string;
  selected_options: SelectedOption[];
};

type BannedGameFull = {
  id: number; // banned selected_game id
  game: number;
  game_name: string;
  selected_options: SelectedOption[];
};

type BannedGameEmpty = {
  game: null;
  selected_options: [];
  leagueId: null;
  playerProfileId: null;
};

type BannedGame = BannedGameFull | BannedGameEmpty;
