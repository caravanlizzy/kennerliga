export type TKennerButton = {
  label?: string;
  icon?: string;
  color?: string;
  forwardName?: string;
};

export type TItem = {
  itemId: number;
  name: string;
  isEditable: boolean;
};

export type TMessageDto = {
  text: string;
  datetime: string;
  user: number;
  sender: string;
};
