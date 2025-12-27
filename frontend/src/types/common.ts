export type TKennerButton = {
  label?: string;
  icon?: string;
  color?: string;
  forwardName?: string;
};

export type TBreadCrumb = {
  label: string;
  icon: string;
  forwardRouteName: string;
};

export type TItem = {
  itemId: number;
  name: string;
  isEditable: boolean;
};

export type TMessage = {
  text: string;
  datetime: string;
  user: number;
  sender: string;
};
