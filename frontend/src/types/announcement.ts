export enum TAnnouncementType {
  INFO = 'INFO',
  WINNER = 'WINNER',
  REGISTER = 'REGISTER',
  WARNING = 'WARNING',
  NEUTRAL = 'NEUTRAL',
}

export type TAnnouncement = {
  id: number;
  type: TAnnouncementType;
  title: string;
  content: string | null;
  visible_until: string;
  visible_from: string;
};

export type TAnnouncementCreate = {
  type: TAnnouncementType;
  title: string;
  content?: string | null;
  visible_until: string;
  visible_from: string;
};
