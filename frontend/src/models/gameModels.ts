export type TPlatform = {
  id: number,
  name: string
}

export type GameDto = {
  id: number;
  name: string;
  platform: string;
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
  id?: number;
  player?: number;
  game: number;
  league?: number;
  selected_options: SelectedGameOptionDto[];
}

export type SelectedGameOptionDto = {
  id: number;
  selected_game: number;
  choice?: number;
  value?: boolean;
}

// Define the type
export type SelectedOptionsMap = {
  [optionId: number]: SelectedGameOptionDto | boolean | null;
};
