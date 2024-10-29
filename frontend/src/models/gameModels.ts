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
}

export type GameOptionChoiceDto = {
  id:number;
  name: string;
  option: number;
}
