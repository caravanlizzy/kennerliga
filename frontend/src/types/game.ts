export type TPlatform = {
  id: number;
  name: string;
};

export type TGameDto = {
  id: number;
  name: string;
  platform: number;
};

export type TGameOptionChoiceDto = {
  id: number;
  name: string;
  option: number;
};

export type TFullGameConditionDto = {
  negate?: boolean;
  depends_on_option?: number | { id: number };
  expected_value?: unknown;
  expected_choice?: number | { id: number };
};

export type TFullGameAvailabilityGroupDto = {
  conditions?: TFullGameConditionDto[];
};

export type TFullGameOptionDto = {
  id: number;
  name: string;
  has_choices: boolean;
  choices?: TGameOptionChoiceDto[];
  availability_groups?: TFullGameAvailabilityGroupDto[];
};

export type TFullGameDto = {
  id: number;
  name: string;
  platform: number;
  options: TFullGameOptionDto[];
};

export type TGameOptionDto = {
  id: number;
  name: string;
  game: number;
  has_choices?: boolean;
  only_if_option?: number;
  only_if_choice?: number;
  only_if_value?: boolean;
  choices?: TGameOptionChoiceDto[];
};

export type TSelectedGameOptionDto = {
  id: number;
  selected_game: number;
  game_option?: TGameOptionDto;
  choice?: TGameOptionChoiceDto;
  value?: boolean;
};

export type TSelectedGameDto = {
  id: number;
  profile: number;
  game: number;
  game_name?: string;
  league: number;
  selected_options: TSelectedGameOptionDto[];
};

export type TSelectedGameDtoPayload = {
  game: number;
  selected_options: {
    selected_game: number;
    game_option_id: number;
    choice_id?: number;
    value?: boolean | null;
  }[];
  profile: number;
  league: number;
};

export type TSelectedGameOptionPayload = {
  game_option: number;
  selected_game: number;
  value?: boolean;
  choice?: number;
};

export type TBanDecisionDtoPayload = {
  profileId: string | number;
  selectedGameId?: number;
  leagueId: number;
  skip?: boolean;
};

export type TFaction = {
  name: string;
  level: number;
};

export type TTieBreaker = {
  name: string;
  higher_wins: boolean;
};

export type TResultConfig = {
  isAsymmetric: boolean;
  hasPoints: boolean;
  startingPointSystem: string;
  hasStartingPlayerOrder: boolean;
  factions?: TFaction[];
  hasTieBreaker: boolean;
  tieBreakers?: TTieBreaker[];
};

export type TMatchResult = {
  id: number;
  player_profile: number;
  selected_game: number;
  points: number | null;
  starting_position: number | null;
  tie_breaker_value: string;
  decisive_tie_breaker: string | null;
  faction_name: string | null;
};
