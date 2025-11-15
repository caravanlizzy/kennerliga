export type TPlatform = {
  id: number,
  name: string
}

export type GameDto = {
  id: number;
  name: string;
  platform: number;
}

export type GameOptionDto = {
  id: number;
  name: string;
  game: number;
  has_choices?: boolean;
  only_if_option?: number;
  only_if_choice?: number;
  only_if_value?: boolean;
  choices?: GameOptionChoiceDto[];
}

export type GameOptionChoiceDto = {
  id:number;
  name: string;
  option: number;
}

export type SelectedGameDto = {
  id: number;
  profile: number;
  game: number;
  league: number;
  selected_options: SelectedGameOptionDto[];
}


export type SelectedGameDtoPayload = {
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

export type SelectedGameOptionDto = {
  id: number;
  selected_game: number;
  choice?: GameOptionChoiceDto;
  value?: boolean;
}

// API submission shape
export type SelectedGameOptionPayload = {
  game_option: number;
  selected_game: number;
  value?: boolean;
  choice?: number;
};



export type BanDecisionDtoPayload = {
  username: string;
  selectedGameId?: number;
  leagueId: number;
  decline?: boolean;
};

