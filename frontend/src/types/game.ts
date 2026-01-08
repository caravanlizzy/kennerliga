export type TPlatform = {
  id: number;
  name: string;
};

export type TGameDto = {
  id: number;
  name: string;
  short_name: string;
  platform: number;
};

export type TGameOptionChoice = {
  id: number | string;
  name: string;
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
  game: number;
  has_choices: boolean;
  choices?: TGameOptionChoiceDto[];
  availability_groups?: TFullGameAvailabilityGroupDto[];
};

export type TFullGameDto = {
  id: number;
  name: string;
  short_name: string;
  platform: number;
  options: TFullGameOptionDto[];
};

export type TGameOption = {
  id: number | string;
  title: string;
  hasChoices: boolean;
  choices: TGameOptionChoice[];
  onlyIfOption?: number | string;
  onlyIfChoice?: number | string;
  onlyIfValue?: boolean;
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

export type TGameInformation = {
  game: TFullGameDto;
  options: TFullGameOptionDto[];
};

export type TGameSelection = {
  game: TGameDto;
  selectedOptions: TSelectedGameOptionPayload[];
  profileId: number;
  leagueId: number;
};

export type TSelectedGameDto = {
  id: number;
  profile: number;
  game: number;
  game_name?: string;
  league: number;
  selected_options: TSelectedGameOptionDto[];
  created_at?: string;
  successfully_banned?: boolean;
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
  choice?: TGameOptionChoiceDto;
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
  id?: number;
  game?: number;
  hasPoints: boolean;
  isAsymmetric: boolean;
  startingPointSystem: number | null;
  hasStartingPlayerOrder: boolean;
  factions?: TFaction[];
  tieBreakers?: TTieBreaker[];
  hasTieBreaker?: boolean;
};

export type TTieBreakerDto = {
  id: number;
  name: string;
  order: number;
};

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
};

export type TMatchResultSubmitPayload = {
  selected_game: number;
  results: TMatchResultPayload[];
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
  factions: { id: number; name: string; level: number }[];
};

export type TMatchResult = TMatchResultDto;
