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
export type TLeagueMember = {
  id: string | number;
  username: string;
  is_active_player: boolean;
  selected_game?: string;
  banned_game?: string;
}

