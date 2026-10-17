export type TKennerButton = {
  label?: string;
  icon?: string;
  color?: string;
  forwardName?: string;
  forwardParams?: Record<string, unknown>;
  to?: unknown;
  shape?: 'rounded' | 'squircle' | 'circle' | 'square';
  size?: string;
  dense?: boolean;
  round?: boolean;
  rounded?: boolean;
};

export type TItem = {
  itemId: number;
  name: string;
  isEditable: boolean;
};
