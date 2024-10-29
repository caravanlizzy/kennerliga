export type TKennerButton = {
  label?: string;
  icon?: string;
  color?: string;
  forwardName?: string;
}
export interface Meta {
  totalCount: number;
}
export type BreadCrumb = {
  label: string;
  icon: string;
  forwardRouteName: string;
}
export type TItem = {
  itemId: number;
  name: string;
  isEditable: boolean;
}
export type ObjPool<T> = {
  [key: string]: T;
}
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
