export interface Todo {
  id: number;
  content: string;
}

export type CreateButton = {
  label: string;
  icon: string;
  color: string;
  forwardTo?: string;
}
export interface Meta {
  totalCount: number;
}
