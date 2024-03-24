export type TGameOptionChoice = {
  internalId: number;
  value: string;
}

export type TGameOption = {
  internalId: number;
  title: string;
  hasChoices: boolean;
  choices: TGameOptionChoice[];
  onlyIfOption?: number;
  onlyIfChoice?: number;
  onlyIfValue?: boolean;
}

export type GameDto = {
  name: string;
  platform: string;
}

export type GameOptionDto = {
  name: string;
  game: number;
  is_activated?: boolean;
  has_choices?: boolean;
  only_if_option?: number;
  only_if_choice?: number;
  only_if_value?: boolean;
}

export type GameOptionChoiceDtp = {
  name: string;
  is_selected: boolean;
  option: number;
}
