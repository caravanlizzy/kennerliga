export enum AnnouncementType {
  INFO = 'INFO',
  WINNER = 'WINNER',
  REGISTER = 'REGISTER',
  WARNING = 'WARNING',
  NEUTRAL = 'NEUTRAL',
}

export type TAnnouncementDto = {
  id: number;
  type: AnnouncementType;
  title: string;
  content: string | null;
  visible_until: string;
  visible_from: string;
  season_id?: number;
};

export type AnnouncementCreate = {
  type: AnnouncementType;
  title: string;
  content?: string | null;
  visible_until: string;
  visible_from: string;
};
