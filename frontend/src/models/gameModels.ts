export type TGameOptionChoice = {
  itemId: number;
  name: string;
}

export type TFaction = {
  itemId: number;
  name: string;
}

export type TTieBreaker = {
  itemId: number;
  name: string;
}

export type TGameOption = {
  itemId: number;
  title: string;
  hasChoices: boolean;
  choices: TGameOptionChoice[];
  onlyIfOption?: number;
  onlyIfChoice?: number;
  onlyIfValue?: boolean;
}

export type TResultConfig = {
  isAsymmetric: boolean;
  hasPoints: boolean;
  startingPointSystem: string;
  hasStartingPlayerOrder: boolean; // Assuming it's a number for order/index
  factions?: TFaction[]; // Assuming it's an array of faction names or identifiers
  hasTieBreaker: boolean;
  tieBreakers?: TTieBreaker[]; // Assuming array of tie breaker rules or identifiers
}

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

export type GameOptionChoiceDtp = {
  id:number;
  name: string;
  option: number;
}
