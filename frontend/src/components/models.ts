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

export type ObjPool<T> = {
  [key: string]: T;
}
