export type TGameOptionChoice = {
  itemId: number;
  value: string;
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
  factions?: string[]; // Assuming it's an array of faction names or identifiers
  hasTieBreaker: boolean;
  tieBreakers?: string[]; // Assuming array of tie breaker rules or identifiers
}


export type GameDto = {
  name: string;
  platform: string;
}

export type GameOptionDto = {
  name: string;
  game: number;
  has_choices?: boolean;
  only_if_option?: number;
  only_if_choice?: number;
  only_if_value?: boolean;
}

export type GameOptionChoiceDtp = {
  name: string;
  option: number;
}
