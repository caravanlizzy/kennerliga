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
  id: number ;
  name: string;
  isEditable: boolean;
}
export type ObjPool<T> = {
  [key: string]: T;
}
