export type TKennerButton = {
  label?: string;
  icon?: string;
  color?: string;
  forwardName?: string;
  shape?: 'rounded' | 'squircle' | 'circle';
};

export type TItem = {
  itemId: number;
  name: string;
  isEditable: boolean;
};

export type TMessageDto = {
  id: number;
  text: string;
  datetime: string;
  user: number;
  sender: string;
  label?: string;
};

export type TFeedbackDto = {
  id: number;
  message: string;
  created_at: string;
  user?: number;
  username?: string;
};
