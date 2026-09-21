export type TKennerButton = {
  label?: string;
  icon?: string;
  color?: string;
  forwardName?: string;
  shape?: 'rounded' | 'squircle' | 'circle' | 'square';
};

export type TItem = {
  itemId: number;
  name: string;
  isEditable: boolean;
};
